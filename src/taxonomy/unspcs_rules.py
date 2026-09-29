"""
National CPSE Material Taxonomy Structure.
Implements hierarchical 4-tier taxonomy (Segment > Family > Class > Commodity)
loosely aligned with standard industrial UNSPSC conventions.
"""

from typing import Dict, Optional, Tuple


TAXONOMY_DIRECTORY: Dict[str, Dict[str, str]] = {
    "VALVE": {
        "segment_code": "40",
        "segment_name": "Industrial Distribution & Piping",
        "family_code": "14",
        "family_name": "Fluid & Gas Control",
        "class_code": "18",
        "class_name": "Piping Valves",
        "commodity_code": "01",
        "commodity_name": "Ball Valves"
    },
    "BOLT": {
        "segment_code": "31",
        "segment_name": "Manufacturing Components",
        "family_code": "16",
        "family_name": "Hardware & Fasteners",
        "class_code": "15",
        "class_name": "Bolts & Studs",
        "commodity_code": "04",
        "commodity_name": "Hex Head Bolts"
    },
    "PIPE": {
        "segment_code": "40",
        "segment_name": "Industrial Distribution & Piping",
        "family_code": "17",
        "family_name": "Pipes & Tubing",
        "class_code": "24",
        "class_name": "Steel Pipes",
        "commodity_code": "02",
        "commodity_name": "Seamless Carbon Steel Pipe"
    },
    "BEARING": {
        "segment_code": "31",
        "segment_name": "Manufacturing Components",
        "family_code": "17",
        "family_name": "Bearings & Bushings",
        "class_code": "15",
        "class_name": "Ball Bearings",
        "commodity_code": "01",
        "commodity_name": "Deep Groove Ball Bearings"
    },
    "GASKET": {
        "segment_code": "31",
        "segment_name": "Manufacturing Components",
        "family_code": "40",
        "family_name": "Seals & Gaskets",
        "class_code": "16",
        "class_name": "Industrial Gaskets",
        "commodity_code": "03",
        "commodity_name": "Spiral Wound Metallic Gaskets"
    },
    "CABLE": {
        "segment_code": "26",
        "segment_name": "Electrical & Power Distribution",
        "family_code": "12",
        "family_name": "Electrical Wire & Cable",
        "class_code": "16",
        "class_name": "Power Cables",
        "commodity_code": "08",
        "commodity_name": "Armoured Power Cable"
    },
    "CEMENT": {
        "segment_code": "30",
        "segment_name": "Civil & Construction Materials",
        "family_code": "11",
        "family_name": "Concrete & Cement",
        "class_code": "16",
        "class_name": "Portland Cement",
        "commodity_code": "02",
        "commodity_name": "Pozzolana Portland Cement"
    }
}


def lookup_taxonomy_for_item_type(item_type: Optional[str]) -> Tuple[str, str]:
    """
    Returns (taxonomy_code, taxonomy_hierarchy_path).
    Example: ('40141801', 'Industrial Distribution & Piping > Fluid & Gas Control > Piping Valves > Ball Valves')
    """
    if not item_type or item_type.upper() not in TAXONOMY_DIRECTORY:
        return "99000000", "General Industrial > Miscellaneous Supplies"

    entry = TAXONOMY_DIRECTORY[item_type.upper()]
    tax_code = f"{entry['segment_code']}{entry['family_code']}{entry['class_code']}{entry['commodity_code']}"
    tax_path = f"{entry['segment_name']} > {entry['family_name']} > {entry['class_name']} > {entry['commodity_name']}"
    return tax_code, tax_path
