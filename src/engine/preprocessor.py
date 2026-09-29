"""
Text preprocessor and domain normalizer for CPSE Material Descriptions.
Expands industrial abbreviations, standardizes Units of Measure, and cleans text.
"""

import re
from typing import Tuple, Dict

# Standard unit of measure normalization table
UOM_NORMALIZATION_MAP: Dict[str, str] = {
    "NOS": "NOS",
    "PCS": "NOS",
    "PC": "NOS",
    "EA": "NOS",
    "EACH": "NOS",
    "NUMBER": "NOS",
    "MTR": "MTR",
    "METRE": "MTR",
    "METER": "MTR",
    "M": "MTR",
    "KG": "KG",
    "KGS": "KG",
    "KILOGRAM": "KG",
    "TON": "MT",
    "MT": "MT",
    "BAG": "BAG",
    "SET": "SET",
    "ROLL": "ROLL"
}

# Domain abbreviations expansion dictionary for industrial materials
ABBREVIATION_MAP: Dict[str, str] = {
    r"\bVLV\b": "VALVE",
    r"\bFLG\b": "FLANGED",
    r"\bFLGD\b": "FLANGED",
    r"\bSMLS\b": "SEAMLESS",
    r"\bS\.S\.?(?=\s|$)": "SS",
    r"\bSTAINLESS\s+STEEL\b": "SS",
    r"\bC\.S\.?(?=\s|$)": "CS",
    r"\bCARBON\s+STEEL\b": "CS",
    r"\bSP\.?\s*WOUND\b": "SPIRAL WOUND",
    r"\bDGBB\b": "DEEP GROOVE BALL BEARING",
    r"\bRADIAL BALL BEARING\b": "DEEP GROOVE BALL BEARING",
    r"\bCL[- ]?150\b": "150#",
    r"\b150\s*LBS\b": "150#",
    r"\bCL[- ]?300\b": "300#",
    r"\b300\s*LBS\b": "300#",
    r"\bCL[- ]?600\b": "600#",
    r"\b600\s*LBS\b": "600#",
    r"\bDIA\b": "DIAMETER",
    r"\bBE\b": "BEVEL END",
    r"\bBEVELLED END\b": "BEVEL END",
    r"\bC/W\b": "WITH",
    r"\bGI\b": "GALVANIZED",
    r"\bGALV\b": "GALVANIZED",
    r"\bHT\s+GR\b": "GRADE",
    r"\bHT\b": "HIGH TENSILE",
    r"\bCLASS\s+8\.8\b": "GRADE 8.8",
    r"\bASTM\s+A[- ]?106\b": "ASTM A106",
    r"\b(?:ASME[- ]?)?B16\.34\b": "ASME B16.34",
    r"\b(?:ASME[- ]?)?B16\.20\b": "ASME B16.20",
    r"\b(?:ASME[- ]?)?B36\.10\b": "ASME B36.10",
    r"\bIS[- :]+1363\b": "IS 1363",
    r"\bIS[- :]+1489\b": "IS 1489",
    r"\bIS[- :]+7098\b": "IS 7098",
}

# Cross-reference map for imperial/metric nominal pipe size (NPS vs NB/DN)
NPS_NB_EQUIVALENTS: Dict[str, str] = {
    r"\b50\s*(?:MM)?\s*NB\b": "2 INCH",
    r"\b80\s*(?:MM)?\s*NB\b": "3 INCH",
    r"\b100\s*(?:MM)?\s*NB\b": "4 INCH",
    r"\b150\s*(?:MM)?\s*NB\b": "6 INCH",
}


def clean_raw_text(text: str) -> str:
    """Performs primary text cleanup and normalization."""
    if not text:
        return ""
    text = text.upper()
    # Normalize slashes, commas, and hyphens with clean spacing
    text = re.sub(r'[,;/]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def expand_industrial_abbreviations(text: str) -> str:
    """Expands industrial shorthand and unifies nomenclature."""
    processed = text
    # Convert quote notations e.g. 2" -> 2 INCH, 4" NB -> 4 INCH
    processed = re.sub(r'(\d+(?:\.\d+)?)"(?:\s*NB)?', r'\1 INCH', processed)

    for pattern, replacement in ABBREVIATION_MAP.items():
        processed = re.sub(pattern, replacement, processed, flags=re.IGNORECASE)

    # Standardize metric/imperial nominal size designations
    for pattern, canonical in NPS_NB_EQUIVALENTS.items():
        processed = re.sub(pattern, canonical, processed, flags=re.IGNORECASE)

    return re.sub(r'\s+', ' ', processed).strip()


def normalize_uom(raw_uom: str) -> str:
    """Standardizes Unit of Measurement to canonical form."""
    if not raw_uom:
        return "NOS"
    cleaned = raw_uom.strip().upper()
    return UOM_NORMALIZATION_MAP.get(cleaned, cleaned)


def preprocess_material_description(raw_desc: str, raw_uom: str) -> Tuple[str, str]:
    """
    Returns (cleaned_description, normalized_uom).
    """
    cleaned = clean_raw_text(raw_desc)
    expanded = expand_industrial_abbreviations(cleaned)
    uom = normalize_uom(raw_uom)
    return expanded, uom
