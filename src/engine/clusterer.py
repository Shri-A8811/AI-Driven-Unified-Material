"""
Clusterer and deduplication grouper for multi-CPSE material records.
Groups candidate duplicates into actionable review clusters with savings calculations.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from src.models.material import NormalizedMaterial, MatchStatus
from src.engine.matcher import compute_match_confidence


class DuplicateCluster(BaseModel):
    """Cluster of candidate duplicate or equivalent materials across CPSEs."""
    cluster_id: str
    canonical_description: str
    match_type: str
    confidence_score: float
    records: List[NormalizedMaterial]
    participating_cpses: List[str]
    rationale: List[str]
    potential_savings_inr: float = 0.0
    status: str = "PENDING_REVIEW"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def cluster_materials_by_similarity(
    materials: List[NormalizedMaterial],
    confidence_threshold: float = 75.0
) -> List[DuplicateCluster]:
    """
    Scans a set of normalized material records and clusters duplicates across different CPSEs.
    """
    clusters: List[DuplicateCluster] = []
    assigned_records = set()
    cluster_counter = 1

    for i in range(len(materials)):
        item_a = materials[i]
        if item_a.record_id in assigned_records:
            continue

        current_group = [item_a]
        cluster_confidences = []
        cluster_rationales = set()
        highest_match_type = "FUNCTIONALLY_EQUIVALENT"

        for j in range(i + 1, len(materials)):
            item_b = materials[j]
            if item_b.record_id in assigned_records:
                continue

            conf, rationale, match_type = compute_match_confidence(item_a, item_b)
            if conf >= confidence_threshold:
                current_group.append(item_b)
                cluster_confidences.append(conf)
                for r in rationale:
                    cluster_rationales.add(r)
                if match_type == "NEAR_DUPLICATE":
                    highest_match_type = "NEAR_DUPLICATE"

        # If a cluster has items from 2 or more distinct records
        if len(current_group) > 1:
            for item in current_group:
                assigned_records.add(item.record_id)

            cpses = sorted(list(set(it.cpse_id.value for it in current_group)))
            avg_conf = sum(cluster_confidences) / len(cluster_confidences) if cluster_confidences else 100.0

            # Estimate collaborative procurement savings (e.g. 10-15% of collective spend)
            estimated_spend = sum(
                (item.attributes.additional_attributes.get("unit_price_inr", 1000.0))
                for item in current_group
            )
            potential_savings = round(estimated_spend * 0.12, 2)

            cluster_id = f"CLUST-{item_a.attributes.item_type or 'MAT'}-{cluster_counter:04d}"
            cluster_counter += 1

            for item in current_group:
                item.cluster_id = cluster_id
                item.match_status = MatchStatus.CANDIDATE_MATCH
                item.confidence_score = round(avg_conf, 1)

            cluster = DuplicateCluster(
                cluster_id=cluster_id,
                canonical_description=item_a.standard_description,
                match_type=highest_match_type,
                confidence_score=round(avg_conf, 1),
                records=current_group,
                participating_cpses=cpses,
                rationale=list(cluster_rationales),
                potential_savings_inr=potential_savings,
                status="PENDING_REVIEW"
            )
            clusters.append(cluster)

    return clusters
