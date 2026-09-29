"""
Integration tests for Part 6: SAP Connector, Tamper-Evident Audit Ledger, and Governance.
"""

import pytest
from src.models.material import CPSEIdentifier
from src.data.sample_cpse_catalogs import SAMPLE_CPSE_DATASETS
from src.engine.ingestion import ingest_and_normalize_records
from src.engine.clusterer import cluster_materials_by_similarity
from src.engine.mapping_registry import MappingRegistry
from src.connectors.sap_mock_connector import MockSAPConnector
from src.governance.audit_ledger import TamperEvidentAuditLedger


def test_sap_bapi_sync_and_duplicate_warning():
    # 1. Setup registry with harmonized valve cluster
    normalized = ingest_and_normalize_records(SAMPLE_CPSE_DATASETS)
    clusters = cluster_materials_by_similarity(normalized)
    valve_cluster = next(c for c in clusters if "VALVE" in c.canonical_description)

    registry = MappingRegistry()
    issued_cnmc = registry.harmonize_cluster(valve_cluster, approved_by="COMMITTEE_HEAD")

    # 2. Test SAP connector for IOCL
    iocl_sap = MockSAPConnector(CPSEIdentifier.IOCL, registry)
    detail_res = iocl_sap.bapi_material_get_detail("IOC-MTR-402911")
    assert detail_res.return_code == "S"
    assert detail_res.data["CNMC"] == issued_cnmc
    assert "VALVE" in detail_res.data["MAKTX"]

    # 3. Save CNMC to local SAP MARA table
    save_res = iocl_sap.bapi_material_savedata("IOC-MTR-402911", issued_cnmc)
    assert save_res.return_code == "S"
    assert iocl_sap.sap_mara_table["IOC-MTR-402911"]["ZZ_CNMC"] == issued_cnmc

    # 4. Simulate an ONGC or GAIL engineer attempting to create a duplicate material
    # requisition for the same 2" 150# SS316 Ball Valve
    gail_sap = MockSAPConnector(CPSEIdentifier.GAIL, registry)
    warning_res = gail_sap.pre_procurement_duplicate_check(
        requisition_desc="BALL VALVE 2 INCH 150# FLANGED RF SS316 BODY TRIM TO ASME B16.34",
        uom="NOS"
    )
    assert warning_res.return_code == "W"
    assert "already standardized" in warning_res.message
    assert warning_res.data["assigned_cnmc"] == issued_cnmc
    assert "IOCL" in warning_res.data["available_in_other_cpses"]


def test_tamper_evident_audit_ledger():
    ledger = TamperEvidentAuditLedger()
    assert len(ledger.chain) == 1  # Genesis block
    assert ledger.verify_integrity() is True

    # Append events
    tx1 = ledger.append_event(
        actor="CPSE_DIRECTOR_IOCL",
        action="APPROVE_HARMONIZATION",
        cluster_id="CLUST-VALVE-0001",
        assigned_cnmc="CNMC-4014-VLV-2BC3",
        participating_records=["IOC-MTR-402911", "NTPC-MECH-88210"]
    )
    assert tx1.tx_id == "TX-000001"
    assert ledger.verify_integrity() is True

    tx2 = ledger.append_event(
        actor="COMMITTEE_SECRETARY",
        action="SYNC_ERP_MARA",
        cluster_id=None,
        assigned_cnmc="CNMC-4014-VLV-2BC3",
        participating_records=["IOC-MTR-402911"]
    )
    assert tx2.tx_id == "TX-000002"
    assert ledger.verify_integrity() is True

    # Tamper test: Alter actor in tx1
    ledger.chain[1].actor = "MALICIOUS_ACTOR"
    assert ledger.verify_integrity() is False
