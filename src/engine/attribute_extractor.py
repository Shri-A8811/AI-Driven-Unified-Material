"""
Technical attribute extractor for CPSE Material Masters.
Parses normalized industrial descriptions into structured engineering specifications.
"""

import re
from typing import Optional
from src.models.material import TechnicalAttributes


def extract_technical_attributes(text: str) -> TechnicalAttributes:
    """
    Extracts key engineering parameters from preprocessed text using pattern recognition.
    """
    attrs = TechnicalAttributes()
    upper = text.upper()

    # 1. Item Type (Noun)
    if "VALVE" in upper:
        attrs.item_type = "VALVE"
    elif "BOLT" in upper or "FASTENER" in upper:
        attrs.item_type = "BOLT"
    elif "PIPE" in upper or "PIPES" in upper:
        attrs.item_type = "PIPE"
    elif "GASKET" in upper:
        attrs.item_type = "GASKET"
    elif "BEARING" in upper:
        attrs.item_type = "BEARING"
    elif "CABLE" in upper:
        attrs.item_type = "CABLE"
    elif "CEMENT" in upper:
        attrs.item_type = "CEMENT"

    # 2. Item Subtype (Modifier)
    if attrs.item_type == "VALVE":
        if "BALL" in upper:
            attrs.item_subtype = "BALL"
        elif "GATE" in upper:
            attrs.item_subtype = "GATE"
        elif "GLOBE" in upper:
            attrs.item_subtype = "GLOBE"
        elif "CHECK" in upper:
            attrs.item_subtype = "CHECK"
    elif attrs.item_type == "BOLT":
        if "HEX" in upper:
            attrs.item_subtype = "HEX HEAD"
    elif attrs.item_type == "PIPE":
        if "SEAMLESS" in upper:
            attrs.item_subtype = "SEAMLESS"
        elif "ERW" in upper:
            attrs.item_subtype = "ERW"
    elif attrs.item_type == "GASKET":
        if "SPIRAL WOUND" in upper:
            attrs.item_subtype = "SPIRAL WOUND"
    elif attrs.item_type == "BEARING":
        if "DEEP GROOVE" in upper or "DGBB" in upper or "BALL BEARING" in upper:
            attrs.item_subtype = "DEEP GROOVE BALL"
    elif attrs.item_type == "CABLE":
        if "XLPE" in upper or "ARMOURED" in upper:
            attrs.item_subtype = "XLPE ARMOURED"
    elif attrs.item_type == "CEMENT":
        if "POZZOLANA" in upper or "PPC" in upper:
            attrs.item_subtype = "PORTLAND POZZOLANA (PPC)"

    # 3. Material Grade / Metallurgy
    grade_match = re.search(r'\b(SS\s*316|SS\s*304|SS316|SS304|ASTM\s+A106(?:\s+GR(?:\.|\s+)[AB])?|WCB|GRADE\s+8\.8|GR\s+8\.8|CLASS\s+8\.8|8\.8|COPPER)\b', upper)
    if grade_match:
        val = grade_match.group(1).replace(" ", "")
        if "316" in val:
            attrs.material_grade = "SS316"
        elif "304" in val:
            attrs.material_grade = "SS304"
        elif "A106" in val:
            attrs.material_grade = "ASTM A106 GR.B"
        elif "8.8" in val:
            attrs.material_grade = "GRADE 8.8"
        elif "WCB" in val:
            attrs.material_grade = "WCB"
        elif "COPPER" in val:
            attrs.material_grade = "COPPER"

    # 4. Bolt size and length handling (e.g. M16X65 or M16 X 65 MM)
    bolt_dim = re.search(r'\bM(\d+)\s*[X*x]\s*(\d+)(?:\s*MM)?\b', upper)
    if bolt_dim:
        attrs.size_dimension = f"M{bolt_dim.group(1)}"
        attrs.length_thickness = f"{bolt_dim.group(2)} MM"

    # 4b. General Size / Dimension if not already set
    if not attrs.size_dimension:
        size_match = re.search(r'(\d+(?:\.\d+)?\s*INCH|\bM\d+\b|\b\d+\s*MM\s*NB\b|\b6205(?:-2RS)?\b|\b\d+(?:\.\d+)?\s*SQ\.?MM\b|\b50\s*KG\b)', upper)
        if size_match:
            attrs.size_dimension = size_match.group(1).strip()

    # 5. Length / Thickness / Schedule if not already set
    if not attrs.length_thickness:
        len_match = re.search(r'(\b\d+\s*MM\b(?!\s*NB)|\bSCH(?:EDULE)?\s*40\b|\bSCH(?:EDULE)?\s*80\b|\b1\.1\s*KV\b|\b\d+(?:\.\d+)?\s*CORE\b)', upper)
        if len_match:
            raw_len = len_match.group(1).strip()
            # Standardize '65MM' -> '65 MM' and 'SCHEDULE 40' -> 'SCH 40'
            raw_len = re.sub(r'(\d+)\s*MM', r'\1 MM', raw_len)
            raw_len = re.sub(r'SCHEDULE\s*(\d+)', r'SCH \1', raw_len)
            attrs.length_thickness = raw_len

    # 6. Pressure Rating
    pres_match = re.search(r'(150#|300#|600#|900#|1500#|PN\s*16|PN\s*40)', upper)
    if pres_match:
        attrs.pressure_rating = pres_match.group(1).strip()

    # 7. Standard / Norm
    std_match = re.search(r'((?:ASME\s+)?B16\.34|(?:ASME\s+)?B16\.20|(?:ASME\s+)?B36\.10|API\s+600|API\s+6D|IS\s+1363|IS\s+1489|IS\s+7098|ISO\s+4014)', upper)
    if std_match:
        matched_std = std_match.group(1).strip()
        if "B16.34" in matched_std:
            attrs.standard_norm = "ASME B16.34"
        elif "B16.20" in matched_std:
            attrs.standard_norm = "ASME B16.20"
        elif "B36.10" in matched_std:
            attrs.standard_norm = "ASME B36.10"
        else:
            attrs.standard_norm = matched_std

    # 8. End Connection
    if "FLANGED" in upper or "RF" in upper:
        attrs.end_connection = "FLANGED RAISED FACE (RF)"
    elif "BEVEL END" in upper or "BE" in upper:
        attrs.end_connection = "BEVEL END"

    return attrs


def build_standard_description(attrs: TechnicalAttributes, raw_desc: str) -> str:
    """
    Synthesizes a clean, canonical standardized description:
    [TYPE], [SUBTYPE], [SIZE], [RATING/THICKNESS], [GRADE], [STANDARD]
    """
    components = []
    if attrs.item_type:
        components.append(attrs.item_type)
    if attrs.item_subtype:
        components.append(attrs.item_subtype)
    if attrs.size_dimension:
        components.append(attrs.size_dimension)
    if attrs.length_thickness:
        components.append(attrs.length_thickness)
    if attrs.pressure_rating:
        components.append(attrs.pressure_rating)
    if attrs.material_grade:
        components.append(attrs.material_grade)
    if attrs.end_connection:
        components.append(attrs.end_connection)
    if attrs.standard_norm:
        components.append(attrs.standard_norm)

    if components:
        return ", ".join(components)
    return raw_desc.strip().upper()
