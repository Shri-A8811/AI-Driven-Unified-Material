"""
Tests for Core System Requirements Matrix:
- Requirement 11: Most Important AI Output (Canonical 8-tuple)
- Requirement 5: Manual Mapping Capability & Role-based Review
- Requirement 7: Mapping Reversal and Version History
"""

import pytest
from fastapi.testclient import TestClient
from src.web.app import app, REGISTRY, NORMALIZED_STORE, CLUSTER_STORE


@pytest.fixture
def client():
    return TestClient(app)


def test_requirement_11_canonical_8_tuple_output(client):
    """
    Validates Requirement 11:
    Every material must produce:
    CPSE Code -> Standardized Description -> Standard Specifications -> Classification ->
    Similar/Equivalent Materials -> Confidence Score -> Common National Material Code -> Approval Status
    """
    res = client.get("/api/pipeline/outputs")
    assert res.status_code == 200
    tuples = res.json()
    assert len(tuples) > 0

    first = tuples[0]
    # Check all 8 canonical fields exist
    assert "cpse_code" in first
    assert "standardized_description" in first
    assert "standard_specifications" in first
    assert "classification" in first
    assert "similar_equivalent_materials" in first
    assert "confidence_score" in first
    assert "common_national_material_code" in first
    assert "approval_status" in first

    # Check specification subfields
    specs = first["standard_specifications"]
    assert "item_type" in specs

    # Check classification taxonomy
    clf = first["classification"]
    assert "taxonomy_code" in clf
    assert "taxonomy_path" in clf


def test_requirement_5_manual_mapping_by_data_steward(client):
    """
    Validates Requirement 5:
    Data Steward can manually link a material to a target CNMC with role and justification.
    """
    res = client.post(
        "/api/materials/manual-map",
        json={
            "cpse_id": "SAIL",
            "local_material_code": "SAIL-CIV-0091",
            "target_cnmc": "CNMC-3011-CMT-9999",
            "mapped_by": "CHIEF_DATA_STEWARD",
            "role": "DATA_STEWARD",
            "justification": "Standardized under Pozzolana Portland Cement group as per Plant Tender."
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["record"]["assigned_cnmc"] == "CNMC-3011-CMT-9999"
    assert data["record"]["status"] == "MANUAL_APPROVED"


def test_requirement_7_mapping_reversal_and_versioning(client):
    """
    Validates Requirement 7:
    Ability to reverse/correct mappings and track version history.
    """
    # Revert the mapping created above
    res = client.post(
        "/api/mappings/revert",
        json={
            "cpse_id": "SAIL",
            "local_material_code": "SAIL-CIV-0091",
            "reverted_by": "QUALITY_CONTROLLER",
            "reason": "Specification revised to Grade 53 OPC instead of PPC."
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["reverted_record"]["status"] == "REVERTED"

    # Verify history was recorded
    key = "SAIL::SAIL-CIV-0091"
    assert key in REGISTRY.history
    assert len(REGISTRY.history[key]) >= 1
