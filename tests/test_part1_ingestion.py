"""
Unit tests for Part 1: Ingestion, Normalization, and Attribute Extraction.
"""

import pytest
from src.data.sample_cpse_catalogs import SAMPLE_CPSE_DATASETS
from src.engine.ingestion import ingest_and_normalize_records
from src.engine.preprocessor import preprocess_material_description, normalize_uom
from src.models.material import CPSEIdentifier


def test_uom_normalization():
    assert normalize_uom("PCS") == "NOS"
    assert normalize_uom("EA") == "NOS"
    assert normalize_uom("MTR") == "MTR"
    assert normalize_uom("METRE") == "MTR"
    assert normalize_uom("KGS") == "KG"


def test_abbreviation_expansion():
    raw = "VLV BALL 2\" 150 LBS RF FLG BODY STAINLESS STEEL 316 ASME-B16.34"
    cleaned, uom = preprocess_material_description(raw, "EA")
    assert "VALVE" in cleaned
    assert "150#" in cleaned
    assert "SS" in cleaned
    assert "ASME B16.34" in cleaned
    assert uom == "NOS"


def test_ingest_all_sample_records():
    normalized = ingest_and_normalize_records(SAMPLE_CPSE_DATASETS)
    assert len(normalized) == len(SAMPLE_CPSE_DATASETS)
    
    # Check that every record has extracted attributes and clean descriptions
    for item in normalized:
        assert item.record_id.startswith("NORM-")
        assert len(item.cleaned_description) > 0
        assert len(item.standard_description) > 0
        assert item.standard_uom in ["NOS", "MTR", "BAG", "SET", "KG"]


def test_valve_attribute_extraction_across_cpses():
    # Grab the 3 records from the valve duplicate cluster (IOCL, NTPC, SAIL)
    valves = [r for r in SAMPLE_CPSE_DATASETS if "402911" in r.local_material_code or "88210" in r.local_material_code or "00431" in r.local_material_code]
    assert len(valves) == 3

    normalized = ingest_and_normalize_records(valves)
    for v in normalized:
        assert v.attributes.item_type == "VALVE"
        assert v.attributes.item_subtype == "BALL"
        assert "2 INCH" in v.attributes.size_dimension
        assert v.attributes.pressure_rating == "150#"
        assert v.attributes.material_grade == "SS316"
        assert v.attributes.standard_norm == "ASME B16.34"


def test_fastener_attribute_extraction_across_cpses():
    # Cluster B: M16x65 Hex Bolt Grade 8.8 (IOCL, NTPC, BHEL)
    fasteners = [r for r in SAMPLE_CPSE_DATASETS if "10928" in r.local_material_code or "44910" in r.local_material_code or "992" in r.local_material_code]
    assert len(fasteners) == 3

    normalized = ingest_and_normalize_records(fasteners)
    for f in normalized:
        assert f.attributes.item_type == "BOLT"
        assert f.attributes.size_dimension == "M16"
        assert f.attributes.length_thickness == "65 MM"
        assert f.attributes.material_grade == "GRADE 8.8"
        assert "IS 1363" in f.attributes.standard_norm


def test_pipe_attribute_extraction_across_cpses():
    # Cluster C: 4" Sch 40 CS Seamless Pipe ASTM A106 Gr.B (IOCL, SAIL)
    pipes = [r for r in SAMPLE_CPSE_DATASETS if "77312" in r.local_material_code or "PIPE-102" in r.local_material_code]
    assert len(pipes) == 2

    normalized = ingest_and_normalize_records(pipes)
    for p in normalized:
        assert p.attributes.item_type == "PIPE"
        assert p.attributes.item_subtype == "SEAMLESS"
        assert "4 INCH" in p.attributes.size_dimension
        assert p.attributes.length_thickness == "SCH 40"
        assert p.attributes.material_grade == "ASTM A106 GR.B"
