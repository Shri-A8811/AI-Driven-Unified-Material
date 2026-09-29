"""
Mock SAP RFC / BAPI Connector for CPSE Enterprise Resource Planning systems.
Simulates bi-directional synchronization between CPSE ERP and the National Material Master Framework.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from src.models.material import CPSEIdentifier
from src.engine.preprocessor import preprocess_material_description
from src.engine.attribute_extractor import extract_technical_attributes
from src.engine.code_generator import generate_cnmc_code
from src.engine.mapping_registry import MappingRegistry


class SAPRFCResponse:
    def __init__(self, return_code: str, message: str, data: Optional[Dict[str, Any]] = None):
        self.return_code = return_code  # 'S' = Success, 'E' = Error, 'W' = Warning
        self.message = message
        self.data = data or {}


class MockSAPConnector:
    """
    Simulates standard SAP BAPI integration for CPSEs.
    """

    def __init__(self, cpse_id: CPSEIdentifier, registry: MappingRegistry):
        self.cpse_id = cpse_id
        self.registry = registry
        # Simulated SAP local material database (table MARA)
        self.sap_mara_table: Dict[str, Dict[str, Any]] = {}

    def bapi_material_get_detail(self, local_material_code: str) -> SAPRFCResponse:
        """
        Emulates BAPI_MATERIAL_GET_DETAIL:
        Fetches material master record from local CPSE SAP system.
        """
        record = self.registry.get_by_cpse_code(self.cpse_id.value, local_material_code)
        if record:
            return SAPRFCResponse(
                return_code="S",
                message="Material master details retrieved successfully",
                data={
                    "MATNR": local_material_code,
                    "CNMC": record.assigned_cnmc,
                    "MAKTX": record.standard_description,
                    "MEINS": record.standard_uom,
                    "STATUS": record.status
                }
            )
        return SAPRFCResponse(return_code="E", message=f"Material {local_material_code} not found in SAP")

    def bapi_material_savedata(self, local_material_code: str, cnmc_code: str) -> SAPRFCResponse:
        """
        Emulates BAPI_MATERIAL_SAVEDATA:
        Updates SAP MARA extension field ZZ_CNMC with Common National Material Code.
        """
        self.sap_mara_table[local_material_code] = {
            "ZZ_CNMC": cnmc_code,
            "LAST_SYNC_TS": datetime.now(timezone.utc).isoformat()
        }
        return SAPRFCResponse(
            return_code="S",
            message=f"Material {local_material_code} successfully updated with National Code {cnmc_code}"
        )

    def pre_procurement_duplicate_check(self, requisition_desc: str, uom: str) -> SAPRFCResponse:
        """
        Real-time interception:
        Called during PR/PO creation in SAP to verify if an identical/equivalent material
        already exists in another CPSE or in the National Master.
        """
        cleaned, norm_uom = preprocess_material_description(requisition_desc, uom)
        attrs = extract_technical_attributes(cleaned)
        candidate_cnmc = generate_cnmc_code(attrs)

        existing_cross_cpses = self.registry.get_by_cnmc(candidate_cnmc)
        if existing_cross_cpses:
            other_cpses = [r.cpse_id for r in existing_cross_cpses if r.cpse_id != self.cpse_id.value]
            return SAPRFCResponse(
                return_code="W",
                message="Pre-procurement duplicate alert: Material already standardized under Common National Code.",
                data={
                    "assigned_cnmc": candidate_cnmc,
                    "standard_description": existing_cross_cpses[0].standard_description,
                    "available_in_other_cpses": other_cpses,
                    "recommendation": "Leverage existing National Material Code or initiate cross-CPSE procurement."
                }
            )

        return SAPRFCResponse(
            return_code="S",
            message="No identical material conflict found in National Master.",
            data={"proposed_cnmc": candidate_cnmc}
        )
