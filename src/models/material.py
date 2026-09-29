"""
Data models for CPSE Material Standardization & Harmonization.
Defines schemas for Raw Ingestion, Normalized Attributes, and Harmonized Material Records.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum


class CPSEIdentifier(str, Enum):
    IOCL = "IOCL"      # Indian Oil Corporation Ltd (Oil & Gas)
    ONGC = "ONGC"      # Oil and Natural Gas Corporation (Upstream Oil)
    NTPC = "NTPC"      # NTPC Ltd (Power Generation)
    SAIL = "SAIL"      # Steel Authority of India Ltd (Steel/Metals)
    BHEL = "BHEL"      # Bharat Heavy Electricals Ltd (Heavy Engineering)
    GAIL = "GAIL"      # Gas Authority of India Ltd (Gas Transmission)


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    DATA_STEWARD = "DATA_STEWARD"
    TECHNICAL_REVIEWER = "TECHNICAL_REVIEWER"
    APPROVER = "APPROVER"


class MatchStatus(str, Enum):
    UNPROCESSED = "UNPROCESSED"
    CANDIDATE_MATCH = "CANDIDATE_MATCH"
    HARMONIZED = "HARMONIZED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class TechnicalAttributes(BaseModel):
    """Extracted normalized technical parameters."""
    item_type: Optional[str] = Field(None, description="Core noun: e.g. VALVE, BOLT, GASKET, BEARING, PIPE")
    item_subtype: Optional[str] = Field(None, description="Modifier: e.g. BALL, HEX, SPIRAL WOUND, DEEP GROOVE, SEAMLESS")
    material_grade: Optional[str] = Field(None, description="Metallurgy/Grade: e.g. SS316, SS304, CS A105, ASTM A106 GR.B, 8.8")
    size_dimension: Optional[str] = Field(None, description="Size/Diameter: e.g. 2 INCH, 50MM, M16, 100MM NB")
    length_thickness: Optional[str] = Field(None, description="Length or thickness: e.g. 65MM, 100M, SCH 40")
    pressure_rating: Optional[str] = Field(None, description="Pressure Class: e.g. 150#, 300#, 600#, PN16, PN40")
    standard_norm: Optional[str] = Field(None, description="Industry standard: e.g. ASME B16.34, API 6D, IS 1363, DIN 933")
    end_connection: Optional[str] = Field(None, description="End prep: e.g. FLANGED, RF, THREADED, BUTT WELD")
    additional_attributes: Dict[str, Any] = Field(default_factory=dict)


class CoreAIOutputTuple(BaseModel):
    """
    The canonical 8-tuple mandated by Requirement 11:
    CPSE Code -> Standardized Description -> Standard Specifications -> Classification ->
    Similar/Equivalent Materials -> Confidence Score -> Common National Material Code -> Approval Status
    """
    cpse_code: str
    cpse_id: str
    raw_description: str
    standardized_description: str
    standard_specifications: Dict[str, Optional[str]]
    classification: Dict[str, str]
    similar_equivalent_materials: List[Dict[str, Any]]
    confidence_score: float
    common_national_material_code: Optional[str]
    approval_status: str
    approved_by: Optional[str] = None
    approval_justification: Optional[str] = None
    approval_timestamp: Optional[str] = None
    version: int = 1


class RawMaterialRecord(BaseModel):
    """Input record ingested directly from a CPSE ERP/SAP system."""
    cpse_id: CPSEIdentifier
    local_material_code: str = Field(..., description="Legacy material code in CPSE's SAP/ERP")
    raw_description: str = Field(..., description="Raw short/long description from legacy system")
    raw_uom: str = Field(..., description="Legacy Unit of Measurement e.g. NOS, PC, MTR, KG")
    category_hint: Optional[str] = None
    plant_location: Optional[str] = None
    unit_price_inr: Optional[float] = None
    stock_quantity: Optional[int] = None
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NormalizedMaterial(BaseModel):
    """Preprocessed and attribute-extracted material record."""
    record_id: str
    cpse_id: CPSEIdentifier
    local_material_code: str
    raw_description: str
    cleaned_description: str
    standard_description: str
    standard_uom: str
    attributes: TechnicalAttributes
    assigned_cnmc: Optional[str] = None
    match_status: MatchStatus = MatchStatus.UNPROCESSED
    confidence_score: float = 0.0
    cluster_id: Optional[str] = None
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    justification: Optional[str] = None
    approved_by: Optional[str] = None
    approved_by_role: Optional[UserRole] = None
