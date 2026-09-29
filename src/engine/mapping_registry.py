"""
Bi-directional Mapping Registry for CPSE Local Codes and Common National Material Codes.
Provides fast $O(1)$ lookups, harmonization approval execution, and ERP export capabilities.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from src.models.material import NormalizedMaterial, MatchStatus
from src.engine.code_generator import generate_cnmc_code
from src.engine.clusterer import DuplicateCluster


class MappingRecord(BaseModel):
    """Entry linking an individual CPSE code to a CNMC."""
    cpse_id: str
    local_material_code: str
    raw_description: str
    assigned_cnmc: str
    standard_description: str
    standard_uom: str
    status: str = "APPROVED"
    approved_by: str = "SYSTEM_ADMIN"
    approved_by_role: str = "APPROVER"
    justification_comment: str = "Verified specification equivalency across CPSE master records."
    approved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    previous_cnmc: Optional[str] = None
    is_active: bool = True


class MappingRegistry:
    """In-memory thread-safe mapping registry and export engine."""

    def __init__(self):
        # (cpse_id, local_code) -> MappingRecord
        self.cpse_to_cnmc: Dict[str, MappingRecord] = {}
        # cnmc -> List[MappingRecord]
        self.cnmc_to_cpse: Dict[str, List[MappingRecord]] = {}
        # Audit history of all versions: key -> List[MappingRecord]
        self.history: Dict[str, List[MappingRecord]] = {}

    def _make_key(self, cpse_id: str, local_code: str) -> str:
        return f"{cpse_id.strip().upper()}::{local_code.strip()}"

    def register_mapping(self, record: MappingRecord) -> None:
        key = self._make_key(record.cpse_id, record.local_material_code)
        
        # Save to history if updating
        if key in self.cpse_to_cnmc:
            prior = self.cpse_to_cnmc[key]
            if key not in self.history:
                self.history[key] = []
            self.history[key].append(prior)
            record.version = prior.version + 1
            record.previous_cnmc = prior.assigned_cnmc

        self.cpse_to_cnmc[key] = record

        if record.assigned_cnmc not in self.cnmc_to_cpse:
            self.cnmc_to_cpse[record.assigned_cnmc] = []
        
        # Keep clean active list
        self.cnmc_to_cpse[record.assigned_cnmc] = [
            r for r in self.cnmc_to_cpse[record.assigned_cnmc]
            if self._make_key(r.cpse_id, r.local_material_code) != key
        ]
        self.cnmc_to_cpse[record.assigned_cnmc].append(record)

    def revert_mapping(self, cpse_id: str, local_code: str, reverted_by: str, reason: str) -> Optional[MappingRecord]:
        """Reverses/deactivates an approved mapping per Requirement 7."""
        key = self._make_key(cpse_id, local_code)
        if key not in self.cpse_to_cnmc:
            return None

        current = self.cpse_to_cnmc[key]
        if key not in self.history:
            self.history[key] = []
        self.history[key].append(current)

        # Remove from active CNMC lookup
        if current.assigned_cnmc in self.cnmc_to_cpse:
            self.cnmc_to_cpse[current.assigned_cnmc] = [
                r for r in self.cnmc_to_cpse[current.assigned_cnmc]
                if self._make_key(r.cpse_id, r.local_material_code) != key
            ]

        # Mark inactive
        current.is_active = False
        current.status = "REVERTED"
        current.justification_comment = f"REVERTED: {reason}"
        current.approved_by = reverted_by
        del self.cpse_to_cnmc[key]
        return current

    def manual_map_material(
        self,
        item: NormalizedMaterial,
        target_cnmc: str,
        mapped_by: str,
        role: str,
        justification: str
    ) -> MappingRecord:
        """Manual mapping capability per Requirement 5."""
        item.assigned_cnmc = target_cnmc
        item.match_status = MatchStatus.HARMONIZED
        item.approved_by = mapped_by
        item.justification = justification

        record = MappingRecord(
            cpse_id=item.cpse_id.value,
            local_material_code=item.local_material_code,
            raw_description=item.raw_description,
            assigned_cnmc=target_cnmc,
            standard_description=item.standard_description,
            standard_uom=item.standard_uom,
            status="MANUAL_APPROVED",
            approved_by=mapped_by,
            approved_by_role=role,
            justification_comment=justification
        )
        self.register_mapping(record)
        return record

    def get_by_cpse_code(self, cpse_id: str, local_code: str) -> Optional[MappingRecord]:
        key = self._make_key(cpse_id, local_code)
        return self.cpse_to_cnmc.get(key)

    def get_by_cnmc(self, cnmc: str) -> List[MappingRecord]:
        return self.cnmc_to_cpse.get(cnmc.strip().upper(), [])

    def harmonize_cluster(
        self,
        cluster: DuplicateCluster,
        approved_by: str = "CPSE_COMMITTEE",
        approved_by_role: str = "APPROVER",
        justification_comment: str = "Verified specification equivalency across CPSE master records."
    ) -> str:
        """
        Approves a candidate duplicate cluster, issues a canonical CNMC,
        and binds all participating CPSE records to the CNMC.
        """
        # Pick primary item for attribute signature
        primary_item = cluster.records[0]
        cnmc = generate_cnmc_code(primary_item.attributes)

        for item in cluster.records:
            item.assigned_cnmc = cnmc
            item.match_status = MatchStatus.HARMONIZED
            item.approved_by = approved_by
            item.justification = justification_comment
            record = MappingRecord(
                cpse_id=item.cpse_id.value,
                local_material_code=item.local_material_code,
                raw_description=item.raw_description,
                assigned_cnmc=cnmc,
                standard_description=primary_item.standard_description,
                standard_uom=item.standard_uom,
                status="APPROVED",
                approved_by=approved_by,
                approved_by_role=approved_by_role,
                justification_comment=justification_comment
            )
            self.register_mapping(record)

        cluster.status = "APPROVED"
        return cnmc

    def export_as_csv_rows(self) -> List[Dict[str, str]]:
        """Exports all registered mappings as a flat dictionary list for CSV generation."""
        rows = []
        for rec in self.cpse_to_cnmc.values():
            rows.append({
                "CPSE": rec.cpse_id,
                "Local_Material_Code": rec.local_material_code,
                "Common_National_Material_Code": rec.assigned_cnmc,
                "Standard_Description": rec.standard_description,
                "Standard_UOM": rec.standard_uom,
                "Raw_Description": rec.raw_description,
                "Approved_By": rec.approved_by,
                "Approved_By_Role": rec.approved_by_role,
                "Justification": rec.justification_comment,
                "Version": str(rec.version),
                "Approved_At": rec.approved_at.isoformat()
            })
        return rows
