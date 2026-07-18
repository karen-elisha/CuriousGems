"""
Investigation Service for the VeriGem Financial Digital Twin.

Central orchestration layer that implements the full investigation pipeline:

  Digital Twin → Rule Engine → Risk Engine → Evidence Graph
  → Timeline → Prompt Builder → GemmaService → Structured JSON

ARCHITECTURAL BOUNDARY:
  - Rule Engine / Risk Engine / Timeline / Evidence Graph: UNCHANGED.
  - PromptBuilder compresses data into a Gemma-optimized investigation prompt.
  - GemmaService receives only the structured prompt, never raw financial data.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from .digital_twin import FinancialDigitalTwin
from .event_engine import EventEngine, TimelineEntry
from .evidence_graph import EvidenceGraph
from .gemma_service import GemmaService
from .models import Employee, Invoice, PurchaseOrder, Transaction, Vendor
from .prompt_builder import PromptBuilder
from .risk_engine import RiskPropagationEngine, RiskProfile
from .rule_engine import RuleEngine, RuleResult
from .timeline_manager import TimelineManager

logger = logging.getLogger(__name__)


class InvestigationService:
    """
    Executes deep investigations into specific entities or system anomalies.

    Coordinates the collection of:
    - Rule violations from the Rule Engine
    - Risk propagation scores from the Risk Engine
    - Event history from the Event Engine
    - Graph relationships from the Evidence Graph

    Passes the compressed payload via PromptBuilder to the Gemma Service
    to generate a human-readable investigation report.
    """

    def __init__(
        self,
        twin: FinancialDigitalTwin,
        rule_engine: RuleEngine,
        risk_engine: RiskPropagationEngine,
        event_engine: EventEngine,
        timeline_manager: TimelineManager,
        gemma_service: GemmaService,
    ) -> None:
        self.twin = twin
        self.rule_engine = rule_engine
        self.risk_engine = risk_engine
        self.event_engine = event_engine
        self.timeline_manager = timeline_manager
        self.gemma_service = gemma_service

        self.evidence_graph_builder = EvidenceGraph(self.twin)
        logger.info("InvestigationService initialised.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_entity_and_related(
        self, entity_id: str
    ) -> Tuple[str, Optional[Any], Dict[str, Any]]:
        """
        Resolve the focal entity from the DataStore and collect related entities.

        Returns:
            (entity_type, focal_entity_object, related_entities_dict)

        The related dict always has keys:
            vendor, employee, purchase_orders, invoices, transactions
        """
        store = self.twin.store
        related: Dict[str, Any] = {
            "vendor": None,
            "employee": None,
            "purchase_orders": [],
            "invoices": [],
            "transactions": [],
        }

        # ── Vendor ────────────────────────────────────────────────────────
        if entity_id in store.vendors:
            vendor = store.vendors[entity_id]
            related["vendor"] = vendor
            related["purchase_orders"] = [
                po for po in store.purchase_orders.values()
                if po.vendor_id == entity_id
            ][:5]
            related["invoices"] = [
                inv for inv in store.invoices.values()
                if inv.vendor_id == entity_id
            ][:5]
            related["transactions"] = [
                txn for txn in store.transactions.values()
                if txn.vendor_id == entity_id
            ][:5]
            return "vendor", vendor, related

        # ── Employee ──────────────────────────────────────────────────────
        if entity_id in store.employees:
            emp = store.employees[entity_id]
            related["employee"] = emp
            related["purchase_orders"] = [
                po for po in store.purchase_orders.values()
                if po.requested_by_employee_id == entity_id
                or po.approved_by_employee_id == entity_id
            ][:5]
            related["transactions"] = [
                txn for txn in store.transactions.values()
                if txn.approver_employee_id == entity_id
            ][:5]
            related["invoices"] = [
                inv for inv in store.invoices.values()
                if inv.verified_by_employee_id == entity_id
            ][:5]
            return "employee", emp, related

        # ── Purchase Order ────────────────────────────────────────────────
        if entity_id in store.purchase_orders:
            po = store.purchase_orders[entity_id]
            related["vendor"] = store.vendors.get(po.vendor_id)
            related["purchase_orders"] = [po]
            related["invoices"] = [
                inv for inv in store.invoices.values()
                if inv.purchase_order_id == entity_id
            ][:5]
            related["transactions"] = [
                txn for txn in store.transactions.values()
                if txn.purchase_order_id == entity_id
            ][:5]
            return "purchase_order", po, related

        # ── Invoice ───────────────────────────────────────────────────────
        if entity_id in store.invoices:
            inv = store.invoices[entity_id]
            related["vendor"] = store.vendors.get(inv.vendor_id)
            related["invoices"] = [inv]
            if inv.purchase_order_id in store.purchase_orders:
                related["purchase_orders"] = [store.purchase_orders[inv.purchase_order_id]]
            related["transactions"] = [
                txn for txn in store.transactions.values()
                if txn.invoice_id == entity_id
            ][:5]
            return "invoice", inv, related

        # ── Transaction ───────────────────────────────────────────────────
        if entity_id in store.transactions:
            txn = store.transactions[entity_id]
            related["vendor"] = store.vendors.get(txn.vendor_id)
            related["transactions"] = [txn]
            if txn.purchase_order_id in store.purchase_orders:
                related["purchase_orders"] = [store.purchase_orders[txn.purchase_order_id]]
            if txn.invoice_id in store.invoices:
                related["invoices"] = [store.invoices[txn.invoice_id]]
            return "transaction", txn, related

        return "unknown", None, related

    # ------------------------------------------------------------------
    # Core investigation method
    # ------------------------------------------------------------------

    def investigate_entity(self, entity_id: str) -> Dict[str, Any]:
        """
        Run a full-stack investigation on a specific entity.

        Pipeline:
          1. Rule Engine   → compliance violations for this entity
          2. Risk Engine   → risk profile + related entity profiles
          3. Evidence Graph→ React Flow subgraph JSON
          4. Timeline      → chronological event history
          5. Entity data   → Vendor / Employee / PO / Invoice / Transaction objects
          6. Prompt Builder→ Gemma 3 27B-optimized structured prompt
          7. GemmaService  → natural language explanation
          8. Return        → structured JSON (risk + violations + timeline +
                             evidence graph + gemma explanation)

        Returns:
            A fully structured dictionary ready for JSON serialisation.
        """
        logger.info("Starting investigation for entity: %s", entity_id)

        # ── Step 1: Rule Engine ────────────────────────────────────────────
        all_results: List[RuleResult] = self.rule_engine.evaluate_all(self.twin.store)
        entity_violations: List[RuleResult] = [
            res for res in all_results
            if entity_id in res.affected_entities
        ]
        logger.info(
            "Rule Engine: %d violation(s) found for entity %s",
            len(entity_violations), entity_id
        )

        # ── Step 2: Risk Engine ────────────────────────────────────────────
        risk_profile: Optional[RiskProfile] = self.risk_engine.get_profile(entity_id)

        # Collect risk profiles for all entities touched by violations
        related_entity_ids: set = {entity_id}
        for v in entity_violations:
            related_entity_ids.update(v.affected_entities)

        related_risk_profiles: List[RiskProfile] = [
            p for eid in related_entity_ids
            if (p := self.risk_engine.get_profile(eid)) is not None
        ]
        logger.info(
            "Risk Engine: total_risk=%.2f for %s (%d related profiles collected)",
            risk_profile.total_risk if risk_profile else 0.0,
            entity_id,
            len(related_risk_profiles),
        )

        # ── Step 3: Evidence Graph ─────────────────────────────────────────
        evidence_graph_json: Dict[str, Any] = self.evidence_graph_builder.generate_react_flow(
            entity_ids=list(related_entity_ids), depth=1
        )

        # ── Step 4: Timeline ───────────────────────────────────────────────
        try:
            entity_timeline: List[TimelineEntry] = self.event_engine.generate_timeline(
                entity_id=entity_id, limit=20
            )
        except Exception as exc:
            logger.warning(
                "Timeline generation skipped for %s: %s", entity_id, exc
            )
            entity_timeline = []

        # ── Step 5: Entity data resolution ────────────────────────────────
        entity_type, focal_entity, related = self._resolve_entity_and_related(entity_id)
        logger.info("Entity %s resolved as type: %s", entity_id, entity_type)

        # ── Step 6: Build anomaly description ─────────────────────────────
        if risk_profile:
            anomaly_description = (
                f"Entity '{entity_id}' (type: {entity_type}) has been flagged with "
                f"{len(entity_violations)} compliance violation(s). "
                f"The Risk Engine reports a total risk score of "
                f"{risk_profile.total_risk:.2f} "
                f"(base: {risk_profile.base_risk:.2f}, "
                f"propagated: {risk_profile.propagated_risk:.2f})."
            )
        else:
            anomaly_description = (
                f"Entity '{entity_id}' (type: {entity_type}) has been flagged with "
                f"{len(entity_violations)} compliance violation(s). "
                f"No risk profile exists for this entity in the Risk Engine."
            )

        # ── Step 7: Build structured Gemma investigation prompt ───────────
        investigation_prompt: str = PromptBuilder.build_investigation_prompt(
            entity_id=entity_id,
            anomaly_description=anomaly_description,
            rule_results=entity_violations,
            risk_profiles=related_risk_profiles,
            timeline=entity_timeline,
            evidence_graph=evidence_graph_json,
            vendor=related.get("vendor"),
            employee=related.get("employee"),
            purchase_orders=related.get("purchase_orders") or [],
            invoices=related.get("invoices") or [],
            transactions=related.get("transactions") or [],
        )

        # ── Step 8: Gemma AI explanation ───────────────────────────────────
        logger.info(
            "Delegating investigation reasoning to GemmaService (entity=%s, "
            "prompt_chars=%d)",
            entity_id, len(investigation_prompt)
        )
        gemma_report: str = self.gemma_service.ask_gemma(investigation_prompt)

        # ── Step 9: Serialize timeline for JSON ────────────────────────────
        timeline_payload: List[Dict[str, Any]] = [
            {
                "sequence": t.sequence_number,
                "timestamp": t.timestamp.isoformat(),
                "category": t.category,
                "entity_type": t.entity_type,
                "entity_id": t.entity_id,
                "actor_id": t.actor_id,
                "summary": t.summary,
            }
            for t in entity_timeline
        ]

        logger.info("Investigation complete for entity: %s", entity_id)

        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "risk": {
                "base_risk": risk_profile.base_risk if risk_profile else 0.0,
                "propagated_risk": risk_profile.propagated_risk if risk_profile else 0.0,
                "total_risk": risk_profile.total_risk if risk_profile else 0.0,
            },
            "violations": [
                {
                    "rule_name": v.rule_name,
                    "severity": v.severity,
                    "risk_score": v.risk_score,
                    "evidence": v.evidence,
                    "affected_entities": v.affected_entities,
                }
                for v in entity_violations
            ],
            "violation_count": len(entity_violations),
            "timeline": timeline_payload,
            "evidence_graph": evidence_graph_json,
            "related_entity_count": len(related_entity_ids) - 1,
            "gemma_report": gemma_report,
        }
