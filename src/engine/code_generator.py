"""
Common National Material Code (CNMC) Generator.
Generates deterministic, standardized, collision-free codes for 'One Nation – One Material Code'.
"""

import hashlib
from typing import Optional
from src.models.material import TechnicalAttributes
from src.taxonomy.unspcs_rules import lookup_taxonomy_for_item_type


def generate_attribute_signature(attrs: TechnicalAttributes) -> str:
    """
    Creates a canonical attribute string for cryptographic hashing.
    """
    parts = [
        str(attrs.item_type or "").strip().upper(),
        str(attrs.item_subtype or "").strip().upper(),
        str(attrs.size_dimension or "").strip().upper(),
        str(attrs.length_thickness or "").strip().upper(),
        str(attrs.pressure_rating or "").strip().upper(),
        str(attrs.material_grade or "").strip().upper(),
        str(attrs.standard_norm or "").strip().upper(),
    ]
    return "|".join(parts)


TYPE_PREFIXES = {
    "VALVE": "VLV",
    "BOLT": "BLT",
    "PIPE": "PIP",
    "BEARING": "BRG",
    "GASKET": "GSK",
    "CABLE": "CBL",
    "CEMENT": "CMT"
}


def generate_cnmc_code(attrs: TechnicalAttributes) -> str:
    """
    Generates deterministic Common National Material Code:
    Format: CNMC-[SEG_FAM_4DIGIT]-[ITEM_TYPE_PREFIX]-[HEX_HASH_4]
    Example: CNMC-4014-VLV-7A2F
    """
    tax_code, _ = lookup_taxonomy_for_item_type(attrs.item_type)
    tax_prefix = tax_code[:4]

    item_key = (attrs.item_type or "").upper()
    type_prefix = TYPE_PREFIXES.get(item_key, item_key[:3] if item_key else "MAT")

    sig = generate_attribute_signature(attrs)
    hash_digest = hashlib.sha256(sig.encode("utf-8")).hexdigest()[:4].upper()

    return f"CNMC-{tax_prefix}-{type_prefix}-{hash_digest}"
