"""
Integration tests for Part 5: FastAPI Web API Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.web.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"


def test_analytics_kpis(client):
    res = client.get("/api/analytics/kpis")
    assert res.status_code == 200
    data = res.json()
    assert data["total_material_records"] > 0
    assert data["total_duplicate_clusters"] > 0
    assert "cpse_distribution" in data
    assert "IOCL" in data["cpse_distribution"]


def test_list_clusters_and_approval_flow(client):
    # 1. Fetch clusters
    res = client.get("/api/clusters")
    assert res.status_code == 200
    clusters = res.json()
    assert len(clusters) > 0

    # Pick a pending cluster (e.g. Bolts or Pipes)
    pending = next((c for c in clusters if c["status"] == "PENDING_REVIEW"), None)
    if pending:
        cluster_id = pending["cluster_id"]
        # 2. Approve cluster
        approve_res = client.post(
            f"/api/clusters/{cluster_id}/approve",
            json={"approved_by": "TEST_OFFICER"}
        )
        assert approve_res.status_code == 200
        approve_data = approve_res.json()
        assert approve_data["status"] == "SUCCESS"
        assert approve_data["assigned_cnmc"].startswith("CNMC-")

        # 3. Verify status updated
        get_res = client.get(f"/api/clusters/{cluster_id}")
        assert get_res.json()["status"] == "APPROVED"


def test_catalog_search(client):
    # Search by keyword "VALVE"
    res = client.get("/api/catalog?query=VALVE")
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0
    for item in items:
        assert "VALVE" in item["standard_description"] or "VALVE" in item["raw_description"]


def test_csv_export(client):
    res = client.get("/api/mappings/export")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    content = res.text
    assert "COMMON_NATIONAL_CODE_CNMC" in content
    assert "LOCAL_MATERIAL_CODE" in content


def test_governance_ledger_endpoint(client):
    res = client.get("/api/governance/ledger")
    assert res.status_code == 200
    data = res.json()
    assert data["integrity_verified"] is True
    assert data["total_blocks"] >= 2  # Genesis + initial valve approval
    assert len(data["chain"]) >= 2
    # Verify latest block structure
    latest = data["chain"][0]
    assert "current_hash" in latest
    assert "previous_hash" in latest
    assert "actor" in latest

