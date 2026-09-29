"""
Unit tests for Part 3: Taxonomy, Common National Material Code (CNMC), and Mapping Registry.
"""

import pytest
from src.data.sample_cpse_catalogs import SAMPLE_CPSE_DATASETS
from src.engine.ingestion import ingest_and_normalize_records
from src.engine.clusterer import cluster_materials_by_similarity
from src.taxonomy.unspcs_rules import lookup_taxonomy_for_item_type
from src.engine.code_generator import generate_cnmc_code
from src.engine.mapping_registry import MappingRegistry
from src.models.material import TechnicalAttributes


def test_taxonomy_lookup():
    code, path = lookup_taxonomy_for_item_type("VALVE")
    assert code == "40141801"
    assert "Piping Valves" in path

    bolt_code, _ = lookup_taxonomy_for_item_type("BOLT")
    assert bolt_code == "31161504"

    unknown_code, _ = lookup_taxonomy_for_item_type("UNKNOWN_DEVICE")
    assert unknown_code == "99000000"


def test_cnmc_code_determinism():
    attr1 = TechnicalAttributes(
        item_type="VALVE",
        item_subtype="BALL",
        size_dimension="2 INCH",
        pressure_rating="150#",
        material_grade="SS316",
        standard_norm="ASME B16.34"
    )
    attr2 = TechnicalAttributes(
        item_type="VALVE",
        item_subtype="BALL",
        size_dimension="2 INCH",
        pressure_rating="150#",
        material_grade="SS316",
        standard_norm="ASME B16.34"
    )

    code1 = generate_cnmc_code(attr1)
    code2 = generate_cnmc_code(attr2)

    assert code1 == code2
    assert code1.startswith("CNMC-4014-VLV-")


def test_cnmc_differentiation():
    attr_2inch = TechnicalAttributes(
        item_type="VALVE",
        item_subtype="BALL",
        size_dimension="2 INCH",
        pressure_rating="150#",
        material_grade="SS316"
    )
    attr_6inch = TechnicalAttributes(
        item_type="VALVE",
        item_subtype="BALL",
        size_dimension="6 INCH",
        pressure_rating="150#",
        material_grade="SS316"
    )

    code1 = generate_cnmc_code(attr_2inch)
    code2 = generate_cnmc_code(attr_6inch)
    assert code1 != code2


def test_cluster_harmonization_and_registry_lookups():
    normalized = ingest_and_normalize_records(SAMPLE_CPSE_DATASETS)
    clusters = cluster_materials_by_similarity(normalized)

    # Harmonize the Valve cluster (contains IOCL, NTPC, and SAIL)
    valve_cluster = next(c for c in clusters if "VALVE" in c.canonical_description)
    registry = MappingRegistry()

    issued_cnmc = registry.harmonize_cluster(valve_cluster, approved_by="DIRECTOR_PROCUREMENT_COMMITTEE")

    assert valve_cluster.status == "APPROVED"
    assert issued_cnmc.startswith("CNMC-4014-VLV-")

    # 1. Forward lookup by CPSE code
    rec_iocl = registry.get_by_cpse_code("IOCL", "IOC-MTR-402911")
    assert rec_iocl is not None
    assert rec_iocl.assigned_cnmc == issued_cnmc
    assert rec_iocl.approved_by == "DIRECTOR_PROCUREMENT_COMMITTEE"

    rec_ntpc = registry.get_by_cpse_code("NTPC", "NTPC-MECH-88210")
    assert rec_ntpc is not None
    assert rec_ntpc.assigned_cnmc == issued_cnmc

    rec_sail = registry.get_by_cpse_code("SAIL", "SAIL-BSP-VAL-00431")
    assert rec_sail is not None
    assert rec_sail.assigned_cnmc == issued_cnmc

    # 2. Reverse lookup by CNMC (Cross-CPSE mapping)
    mapped_cpse_list = registry.get_by_cnmc(issued_cnmc)
    assert len(mapped_cpse_list) == 3
    found_cpse_ids = {r.cpse_id for r in mapped_cpse_list}
    assert found_cpse_ids == {"IOCL", "NTPC", "SAIL"}

    # 3. CSV export rows
    csv_rows = registry.export_as_csv_rows()
    assert len(csv_rows) == 3
    assert csv_rows[0]["Common_National_Material_Code"] == issued_cnmc
