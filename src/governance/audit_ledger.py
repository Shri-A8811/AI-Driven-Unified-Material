"""
Tamper-Evident Audit Ledger for Material Master Governance.
Implements SHA-256 block-style hash chaining for all approval and override events.
"""

import hashlib
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class AuditTransaction(BaseModel):
    tx_id: str
    timestamp: str
    actor: str
    action: str
    cluster_id: Optional[str]
    assigned_cnmc: Optional[str]
    participating_records: List[str]
    previous_hash: str
    current_hash: str


class TamperEvidentAuditLedger:
    """
    Append-only cryptographically chained ledger for governance compliance.
    """

    def __init__(self):
        self.chain: List[AuditTransaction] = []
        self._genesis()

    def _genesis(self):
        genesis_tx = AuditTransaction(
            tx_id="TX-GENESIS-0000",
            timestamp="2026-01-01T00:00:00Z",
            actor="SYSTEM_INIT",
            action="GENESIS_BLOCK",
            cluster_id=None,
            assigned_cnmc=None,
            participating_records=[],
            previous_hash="0" * 64,
            current_hash=hashlib.sha256(b"NATIONAL_MATERIAL_MASTER_GENESIS").hexdigest()
        )
        self.chain.append(genesis_tx)

    def append_event(
        self,
        actor: str,
        action: str,
        cluster_id: Optional[str],
        assigned_cnmc: Optional[str],
        participating_records: List[str]
    ) -> AuditTransaction:
        prev_hash = self.chain[-1].current_hash
        tx_id = f"TX-{len(self.chain):06d}"
        now_ts = datetime.now(timezone.utc).isoformat()

        payload = {
            "tx_id": tx_id,
            "timestamp": now_ts,
            "actor": actor,
            "action": action,
            "cluster_id": cluster_id,
            "assigned_cnmc": assigned_cnmc,
            "participating_records": participating_records,
            "previous_hash": prev_hash
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        current_hash = hashlib.sha256(encoded).hexdigest()

        tx = AuditTransaction(
            tx_id=tx_id,
            timestamp=now_ts,
            actor=actor,
            action=action,
            cluster_id=cluster_id,
            assigned_cnmc=assigned_cnmc,
            participating_records=participating_records,
            previous_hash=prev_hash,
            current_hash=current_hash
        )
        self.chain.append(tx)
        return tx

    def verify_integrity(self) -> bool:
        """Verifies that no entry in the audit chain has been altered."""
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.previous_hash != prev.current_hash:
                return False

            payload = {
                "tx_id": curr.tx_id,
                "timestamp": curr.timestamp,
                "actor": curr.actor,
                "action": curr.action,
                "cluster_id": curr.cluster_id,
                "assigned_cnmc": curr.assigned_cnmc,
                "participating_records": curr.participating_records,
                "previous_hash": curr.previous_hash
            }
            recomputed = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
            if recomputed != curr.current_hash:
                return False
        return True
