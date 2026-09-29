"""
AI Hybrid Matcher for CPSE Material Records.
Combines Lexical Token Matching, Attribute Constraint Checking, and Semantic Cosine Similarity.
"""

import math
import re
from typing import Dict, List, Tuple, Optional
from collections import Counter
from src.models.material import NormalizedMaterial, TechnicalAttributes


def calculate_token_cosine_similarity(text1: str, text2: str) -> float:
    """Computes TF-IDF-like cosine similarity between two text strings."""
    tokens1 = re.findall(r'\w+', text1.upper())
    tokens2 = re.findall(r'\w+', text2.upper())
    if not tokens1 or not tokens2:
        return 0.0

    vec1 = Counter(tokens1)
    vec2 = Counter(tokens2)
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([val ** 2 for val in vec1.values()])
    sum2 = sum([val ** 2 for val in vec2.values()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return float(numerator) / denominator


def calculate_jaccard_token_similarity(text1: str, text2: str) -> float:
    """Computes Jaccard set overlap between tokens."""
    tokens1 = set(re.findall(r'\w+', text1.upper()))
    tokens2 = set(re.findall(r'\w+', text2.upper()))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    return len(intersection) / len(union)


def check_attribute_compatibility(attr1: TechnicalAttributes, attr2: TechnicalAttributes) -> Tuple[bool, float, List[str], List[str]]:
    """
    Validates if two materials are technically compatible.
    Returns:
        (is_compatible, attribute_score, matching_attributes, conflicting_attributes)
    """
    matching = []
    conflicts = []

    # 1. Item Type must match if both are present
    if attr1.item_type and attr2.item_type:
        if attr1.item_type == attr2.item_type:
            matching.append(f"Type: {attr1.item_type}")
        else:
            conflicts.append(f"Type mismatch: {attr1.item_type} vs {attr2.item_type}")
            return False, 0.0, matching, conflicts

    # 2. Item Subtype must not conflict
    if attr1.item_subtype and attr2.item_subtype:
        if attr1.item_subtype == attr2.item_subtype:
            matching.append(f"Subtype: {attr1.item_subtype}")
        else:
            conflicts.append(f"Subtype mismatch: {attr1.item_subtype} vs {attr2.item_subtype}")
            return False, 0.0, matching, conflicts

    # 3. Size / Dimension must not conflict
    if attr1.size_dimension and attr2.size_dimension:
        if attr1.size_dimension == attr2.size_dimension:
            matching.append(f"Size: {attr1.size_dimension}")
        else:
            conflicts.append(f"Size conflict: {attr1.size_dimension} vs {attr2.size_dimension}")
            return False, 0.0, matching, conflicts

    # 4. Pressure rating must not conflict
    if attr1.pressure_rating and attr2.pressure_rating:
        if attr1.pressure_rating == attr2.pressure_rating:
            matching.append(f"Rating: {attr1.pressure_rating}")
        else:
            conflicts.append(f"Rating conflict: {attr1.pressure_rating} vs {attr2.pressure_rating}")
            return False, 0.0, matching, conflicts

    # 5. Length / Thickness
    if attr1.length_thickness and attr2.length_thickness:
        if attr1.length_thickness == attr2.length_thickness:
            matching.append(f"Length/Thk: {attr1.length_thickness}")
        else:
            conflicts.append(f"Length/Thk conflict: {attr1.length_thickness} vs {attr2.length_thickness}")
            return False, 0.0, matching, conflicts

    # 6. Material Grade
    if attr1.material_grade and attr2.material_grade:
        if attr1.material_grade == attr2.material_grade:
            matching.append(f"Grade: {attr1.material_grade}")
        else:
            conflicts.append(f"Grade mismatch: {attr1.material_grade} vs {attr2.material_grade}")
            return False, 0.0, matching, conflicts

    # 7. Standard Norm
    if attr1.standard_norm and attr2.standard_norm:
        if attr1.standard_norm == attr2.standard_norm:
            matching.append(f"Standard: {attr1.standard_norm}")

    total_checked = len(matching) + len(conflicts)
    attr_score = len(matching) / max(total_checked, 1) if total_checked > 0 else 0.5
    return True, attr_score, matching, conflicts


def compute_match_confidence(item1: NormalizedMaterial, item2: NormalizedMaterial) -> Tuple[float, List[str], str]:
    """
    Computes overall confidence score (0.0 to 100.0) between two normalized records.
    Returns (confidence_score, rationale_list, match_type).
    """
    # Quick exit: same CPSE and same code is identical
    if item1.cpse_id == item2.cpse_id and item1.local_material_code == item2.local_material_code:
        return 100.0, ["Exact internal identity"], "IDENTICAL"

    # Check engineering attribute compatibility
    is_compatible, attr_score, matching_attrs, conflicts = check_attribute_compatibility(
        item1.attributes, item2.attributes
    )
    if not is_compatible:
        return 0.0, conflicts, "CONFLICT"

    # Compute text similarity on cleaned & standard descriptions
    sim_clean = calculate_token_cosine_similarity(item1.cleaned_description, item2.cleaned_description)
    sim_std = calculate_token_cosine_similarity(item1.standard_description, item2.standard_description)
    jaccard = calculate_jaccard_token_similarity(item1.cleaned_description, item2.cleaned_description)

    text_similarity = (sim_clean * 0.4) + (sim_std * 0.4) + (jaccard * 0.2)

    # Weighted confidence formula: 55% attributes + 45% text similarity
    if len(matching_attrs) >= 3:
        # Strong attribute evidence
        confidence = (attr_score * 50.0) + (text_similarity * 50.0)
    elif len(matching_attrs) >= 1:
        confidence = (attr_score * 40.0) + (text_similarity * 60.0)
    else:
        confidence = text_similarity * 80.0

    confidence = round(min(max(confidence, 0.0), 100.0), 1)

    # Determine classification tag
    if confidence >= 90.0 and len(matching_attrs) >= 3:
        match_type = "NEAR_DUPLICATE"
    elif confidence >= 75.0:
        match_type = "FUNCTIONALLY_EQUIVALENT"
    else:
        match_type = "LOW_SIMILARITY"

    rationale = [f"Matched on: {', '.join(matching_attrs)}"] if matching_attrs else ["Partial lexical match"]
    return confidence, rationale, match_type
