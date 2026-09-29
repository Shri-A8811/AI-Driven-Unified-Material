"""
Unit tests for Part 2: AI Matching, Semantic Deduplication, and Duplicate Clustering.
"""

import pytest
from src.data.sample_cpse_catalogs import SAMPLE_CPSE_DATASETS
from src.engine.ingestion import ingest_and_normalize_records
from src.engine.matcher import compute_match_confidence, check_attribute_compatibility
from src.engine.clusterer import cluster_materials_by_similarity


@pytest.fixture
def normalized_materials():
    return ingest_and_normalize_records(SAMPLE_CPSE_DATASETS)


def test_valve_duplicate_pair_confidence(normalized_materials):
    iocl_valve = next(m for m in normalized_materials if m.local_material_code == "IOC-MTR-402911")
    ntpc_valve = next(m for m in normalized_materials if m.local_material_code == "NTPC-MECH-88210")
    sail_valve = next(m for m in normalized_materials if m.local_material_code == "SAIL-BSP-VAL-00431")

    # Verify IOCL vs NTPC Ball Valve
    conf1, rationale1, match_type1 = compute_match_confidence(iocl_valve, ntpc_valve)
    assert conf1 >= 80.0
    assert match_type1 in ["NEAR_DUPLICATE", "FUNCTIONALLY_EQUIVALENT"]
    assert any("SS316" in r or "2 INCH" in r for r in rationale1)

    # Verify IOCL vs SAIL Ball Valve
    conf2, rationale2, match_type2 = compute_match_confidence(iocl_valve, sail_valve)
    assert conf2 >= 80.0


def test_incompatible_items_rejection(normalized_materials):
    # Compare 2" 150# Ball Valve (IOC-MTR-402911) against 6" 600# Gate Valve (IOC-VLV-9901)
    ball_valve = next(m for m in normalized_materials if m.local_material_code == "IOC-MTR-402911")
    gate_valve = next(m for m in normalized_materials if m.local_material_code == "IOC-VLV-9901")

    conf, rationale, match_type = compute_match_confidence(ball_valve, gate_valve)
    assert conf == 0.0
    assert match_type == "CONFLICT"
    assert any("conflict" in r.lower() or "mismatch" in r.lower() for r in rationale)


def test_cluster_materials_detects_all_clusters(normalized_materials):
    clusters = cluster_materials_by_similarity(normalized_materials, confidence_threshold=75.0)

    # We expect 5 clusters: Valves, Bolts, Pipes, Bearings, Gaskets
    assert len(clusters) == 5

    cluster_descriptions = [c.canonical_description for c in clusters]
    assert any("VALVE" in d for d in cluster_descriptions)
    assert any("BOLT" in d for d in cluster_descriptions)
    assert any("PIPE" in d for d in cluster_descriptions)
    assert any("BEARING" in d for d in cluster_descriptions)
    assert any("GASKET" in d for d in cluster_descriptions)

    # Verify that multi-CPSE participation is represented in clusters
    valve_cluster = next(c for c in clusters if "VALVE" in c.canonical_description)
    assert len(valve_cluster.records) == 3
    assert "IOCL" in valve_cluster.participating_cpses
    assert "NTPC" in valve_cluster.participating_cpses
    assert "SAIL" in valve_cluster.participating_cpses
    assert valve_cluster.potential_savings_inr > 0
