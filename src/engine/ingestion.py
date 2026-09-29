"""
Ingestion coordinator: takes raw CPSE records and returns fully normalized material items.
"""

import uuid
from typing import List
from src.models.material import RawMaterialRecord, NormalizedMaterial, MatchStatus
from src.engine.preprocessor import preprocess_material_description
from src.engine.attribute_extractor import extract_technical_attributes, build_standard_description


def ingest_and_normalize_records(raw_records: List[RawMaterialRecord]) -> List[NormalizedMaterial]:
    """
    Transforms raw incoming CPSE material records into normalized entities.
    """
    normalized_list = []
    for raw in raw_records:
        cleaned_desc, std_uom = preprocess_material_description(raw.raw_description, raw.raw_uom)
        attrs = extract_technical_attributes(cleaned_desc)
        std_desc = build_standard_description(attrs, cleaned_desc)

        record_id = f"NORM-{raw.cpse_id.value}-{raw.local_material_code}"
        normalized = NormalizedMaterial(
            record_id=record_id,
            cpse_id=raw.cpse_id,
            local_material_code=raw.local_material_code,
            raw_description=raw.raw_description,
            cleaned_description=cleaned_desc,
            standard_description=std_desc,
            standard_uom=std_uom,
            attributes=attrs,
            match_status=MatchStatus.UNPROCESSED,
            confidence_score=0.0
        )
        normalized_list.append(normalized)

    return normalized_list
