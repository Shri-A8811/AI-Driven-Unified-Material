"""
Canonical AI Output Pipeline Formatter.
Implements Requirement 11:
Produces for every existing material:
CPSE Code -> Standardized Description -> Standard Specifications -> Classification ->
Similar/Equivalent Materials -> Confidence Score -> Common National Material Code -> Approval Status
"""

from typing import List, Dict, Any, Optional
from src.models.material import NormalizedMaterial, CoreAIOutputTuple
from src.engine.clusterer import DuplicateCluster
from src.taxonomy.unspcs_rules import lookup_taxonomy_for_item_type
from src.engine.mapping_registry import MappingRegistry


def build_core_ai_output_for_item(
    item: NormalizedMaterial,
    clusters_by_id: Dict[str, DuplicateCluster],
    registry: MappingRegistry
) -> CoreAIOutputTuple:
    """
    Constructs the canonical 8-tuple for a single normalized material.
    """
    # 1. Classification
    tax_code, tax_path = lookup_taxonomy_for_item_type(item.attributes.item_type)
    classification = {
        "taxonomy_code": tax_code,
        "taxonomy_path": tax_path,
        "item_group": item.attributes.item_type or "MISC"
    }

    # 2. Standard Specifications
    specs = {
        "item_type": item.attributes.item_type,
        "item_subtype": item.attributes.item_subtype,
        "size_dimension": item.attributes.size_dimension,
        "pressure_rating": item.attributes.pressure_rating,
        "material_grade": item.attributes.material_grade,
        "length_thickness": item.attributes.length_thickness,
        "standard_norm": item.attributes.standard_norm,
        "end_connection": item.attributes.end_connection
    }

    # 3. Similar / Equivalent Materials (from cluster or registry)
    similar_materials: List[Dict[str, Any]] = []
    if item.cluster_id and item.cluster_id in clusters_by_id:
        cluster = clusters_by_id[item.cluster_id]
        for peer in cluster.records:
            if peer.record_id != item.record_id:
                similar_materials.append({
                    "cpse_id": peer.cpse_id.value,
                    "local_material_code": peer.local_material_code,
                    "raw_description": peer.raw_description,
                    "standard_description": peer.standard_description,
                    "match_type": cluster.match_type,
                    "confidence_score": cluster.confidence_score
                })

    # Check active mapping registry for approval status and CNMC
    mapping = registry.get_by_cpse_code(item.cpse_id.value, item.local_material_code)
    cnmc = item.assigned_cnmc or (mapping.assigned_cnmc if mapping else None)
    status_str = "HARMONIZED" if cnmc else item.match_status.value
    approved_by = mapping.approved_by if mapping else item.approved_by
    justification = mapping.justification_comment if mapping else item.justification
    approved_at = mapping.approved_at.isoformat() if mapping else None
    version = mapping.version if mapping else 1

    return CoreAIOutputTuple(
        cpse_code=item.local_material_code,
        cpse_id=item.cpse_id.value,
        raw_description=item.raw_description,
        standardized_description=item.standard_description,
        standard_specifications=specs,
        classification=classification,
        similar_equivalent_materials=similar_materials,
        confidence_score=item.confidence_score or (cluster.confidence_score if item.cluster_id and item.cluster_id in clusters_by_id else 0.0),
        common_national_material_code=cnmc,
        approval_status=status_str,
        approved_by=approved_by,
        approval_justification=justification,
        approval_timestamp=approved_at,
        version=version
    )


def generate_all_core_ai_outputs(
    materials: List[NormalizedMaterial],
    clusters: List[DuplicateCluster],
    registry: MappingRegistry
) -> List[CoreAIOutputTuple]:
    """Generates the 8-tuple records for all materials in the system."""
    clusters_by_id = {c.cluster_id: c for c in clusters}
    return [build_core_ai_output_for_item(m, clusters_by_id, registry) for m in materials]
