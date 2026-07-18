"""
Prompt Builder for the VeriGem Financial Digital Twin.

Responsible for extracting, compressing, and structuring data from the ecosystem 
(Digital Twin, Timeline, Evidence Graph, Risk, Audit, Policies) into highly 
token-efficient context blocks for the Gemma LLM.

DESIGN RULE:
  This module ONLY builds prompts. It never calls Hugging Face or any LLM.
  All prompt strings returned here are ready to pass to GemmaService.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from decimal import Decimal
from typing import Any, Dict, List, Optional

from .digital_twin import FinancialDigitalTwin
from .event_engine import TimelineEntry
from .models import (
    Employee,
    Invoice,
    PurchaseOrder,
    Transaction,
    Vendor,
)
from .risk_engine import RiskProfile
from .rule_engine import RuleResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_str(value: Any) -> str:
    """Safely convert any value (including Decimal/date) to a plain string."""
    if value is None:
        return "N/A"
    if isinstance(value, Decimal):
        return f"₹{value:,.2f}"
    return str(value)


class PromptBuilder:
    """
    Constructs token-optimized context blocks and full structured prompts
    for ingestion by Gemma 3 27B.

    Two layers of output:
      - Context blocks (JSON strings)  → used by _generate() in GemmaService.
      - Prompt strings (plain text)    → used by ask_gemma() / investigate().
    """

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _optimize_dict(d: dict, drop_keys: Optional[set] = None) -> dict:
        """Removes nulls, empty collections, and backend-only timestamps."""
        drop_keys = drop_keys or {"created_at", "updated_at"}
        return {
            k: v for k, v in d.items()
            if v is not None and v != "" and v != [] and v != {} and k not in drop_keys
        }

    # -----------------------------------------------------------------------
    # Existing context-block builders (JSON strings)
    # -----------------------------------------------------------------------

    @staticmethod
    def build_entity_context(twin: FinancialDigitalTwin, entity_id: str) -> str:
        """Extracts and compresses a single entity's graph profile."""
        try:
            profile = twin.get_entity_profile(entity_id)
        except KeyError:
            return json.dumps({"error": f"Entity {entity_id} not found."})

        entity_data = profile.get("entity_data")
        if entity_data:
            entity_data_dict = (
                asdict(entity_data)
                if hasattr(entity_data, "__dataclass_fields__")
                else dict(entity_data)
            )
            profile["entity_data"] = PromptBuilder._optimize_dict(entity_data_dict)

        return json.dumps(
            {
                "id": profile.get("entity_id"),
                "type": profile.get("node_type"),
                "data": profile.get("entity_data"),
                "rels": profile.get("relationships"),
            },
            separators=(",", ":"),
            default=str,
        )

    @staticmethod
    def build_timeline_context(timeline: List[TimelineEntry], limit: int = 15) -> str:
        """Compresses a timeline, keeping the most recent N events."""
        recent = timeline[-limit:] if len(timeline) > limit else timeline
        compressed = [
            {
                "seq": t.sequence_number,
                "cat": t.category,
                "actor": t.actor_id,
                "summary": t.summary,
            }
            for t in recent
        ]
        return json.dumps(compressed, separators=(",", ":"))

    @staticmethod
    def build_evidence_graph_context(graph_json: Dict[str, Any]) -> str:
        """
        Compresses a React Flow JSON graph.
        Strips UI positioning data (x, y), CSS styles, and frontend node types.
        """
        compressed_nodes = [
            {"id": str(n.get("id")), "label": n.get("data", {}).get("label", n.get("id"))}
            for n in graph_json.get("nodes", [])
        ]
        compressed_edges = [
            {"src": str(e.get("source")), "tgt": str(e.get("target")), "rel": e.get("label")}
            for e in graph_json.get("edges", [])
        ]
        return json.dumps(
            {"nodes": compressed_nodes, "edges": compressed_edges},
            separators=(",", ":"),
        )

    @staticmethod
    def build_risk_context(risk_profiles: List[RiskProfile]) -> str:
        """Compresses risk profiles into a tight summary."""
        compressed = [
            {
                "id": p.entity_id,
                "type": p.entity_type,
                "risk": round(p.total_risk, 2),
            }
            for p in risk_profiles
            if p.total_risk > 0
        ]
        return json.dumps(compressed, separators=(",", ":"))

    @staticmethod
    def build_audit_context(twin: FinancialDigitalTwin, entity_id: str, limit: int = 10) -> str:
        """Extracts and compresses recent audit logs relevant to a specific entity."""
        logs = [
            log
            for log in twin.store.audit_logs.values()
            if log.entity_id == entity_id or log.employee_id == entity_id
        ]
        logs.sort(key=lambda x: x.timestamp)
        recent = logs[-limit:] if len(logs) > limit else logs
        compressed = [
            {
                "act": log.action,
                "by": log.employee_id,
                "stat": log.status,
                "rem": log.remarks,
            }
            for log in recent
        ]
        return json.dumps(compressed, separators=(",", ":"))

    @staticmethod
    def build_policies_context(twin: FinancialDigitalTwin, active_only: bool = True) -> str:
        """Compresses compliance policies down to essential identifiers and rules."""
        compressed = [
            {"id": p.policy_id, "sev": p.severity, "desc": p.description}
            for p in twin.store.compliance_policies.values()
            if not active_only or p.status == "Active"
        ]
        return json.dumps(compressed, separators=(",", ":"))

    @staticmethod
    def build_comprehensive_context(
        twin: FinancialDigitalTwin,
        entity_id: str,
        timeline: Optional[List[TimelineEntry]] = None,
        evidence_graph: Optional[Dict[str, Any]] = None,
        risk_profiles: Optional[List[RiskProfile]] = None,
    ) -> Dict[str, str]:
        """
        Assembles all token-optimized context blocks into a dictionary.
        This dictionary can be passed directly to GemmaService._generate(prompt, context_data).
        """
        context: Dict[str, str] = {
            "entity": PromptBuilder.build_entity_context(twin, entity_id),
            "audit": PromptBuilder.build_audit_context(twin, entity_id),
            "policies": PromptBuilder.build_policies_context(twin),
        }
        if timeline:
            context["timeline"] = PromptBuilder.build_timeline_context(timeline)
        if evidence_graph:
            context["evidence_graph"] = PromptBuilder.build_evidence_graph_context(evidence_graph)
        if risk_profiles:
            context["risk"] = PromptBuilder.build_risk_context(risk_profiles)
        return context

    # -----------------------------------------------------------------------
    # Per-entity prompt section builders (plain-text for Gemma 3 27B)
    # -----------------------------------------------------------------------

    @staticmethod
    def build_vendor_prompt(vendor: Vendor) -> str:
        """
        Builds a Gemma-optimized plain-text section describing a single vendor.
        Omits bank account numbers and sensitive PII while retaining key risk signals.
        """
        lines = [
            "## Vendor Profile",
            f"- ID            : {vendor.vendor_id}",
            f"- Name          : {vendor.vendor_name}",
            f"- Type          : {vendor.vendor_type}",
            f"- Status        : {vendor.vendor_status}",
            f"- Risk Category : {vendor.risk_category}",
            f"- Location      : {vendor.city}, {vendor.state}",
            f"- Onboarded     : {_safe_str(vendor.onboarding_date)}",
            f"- Last Txn Date : {_safe_str(vendor.last_transaction_date)}",
            f"- Payment Terms : {vendor.payment_terms_days} days",
            # GST/PAN present but masked — signals tax registration, not values
            f"- GST Registered: {'Yes' if vendor.gst_number else 'No'}",
            f"- PAN Available : {'Yes' if vendor.pan_number else 'No'}",
        ]
        return "\n".join(lines)

    @staticmethod
    def build_employee_prompt(employee: Employee) -> str:
        """
        Builds a Gemma-optimized plain-text section describing an employee.
        Excludes contact details; retains approval authority signals.
        """
        lines = [
            "## Employee Profile",
            f"- ID              : {employee.employee_id}",
            f"- Name            : {employee.employee_name}",
            f"- Department      : {employee.department}",
            f"- Designation     : {employee.designation}",
            f"- Approval Level  : L{employee.approval_level}",
            f"- Max Approval    : {_safe_str(employee.max_approval_limit_inr)}",
            f"- Status          : {employee.employment_status}",
            f"- City            : {employee.city}",
            f"- Joined          : {_safe_str(employee.date_of_joining)}",
            f"- Reports To      : {employee.reporting_manager_id or 'Top-level / None'}",
        ]
        return "\n".join(lines)

    @staticmethod
    def build_purchase_order_prompt(po: PurchaseOrder) -> str:
        """
        Builds a Gemma-optimized plain-text section describing a Purchase Order.
        """
        lines = [
            "## Purchase Order",
            f"- PO ID           : {po.purchase_order_id}",
            f"- Vendor          : {po.vendor_id}",
            f"- Department      : {po.department}",
            f"- Requested By    : {po.requested_by_employee_id}",
            f"- Approved By     : {po.approved_by_employee_id}",
            f"- Type            : {po.po_type}",
            f"- Category        : {po.procurement_category}",
            f"- Amount          : {_safe_str(po.po_amount_inr)} {po.currency}",
            f"- Status          : {po.po_status}",
            f"- Priority        : {po.priority}",
            f"- Fiscal Year     : {po.fiscal_year}",
            f"- PO Date         : {_safe_str(po.po_date)}",
            f"- Expected Delivery: {_safe_str(po.expected_delivery_date)}",
            f"- Payment Terms   : {po.payment_terms_days} days",
        ]
        return "\n".join(lines)

    @staticmethod
    def build_invoice_prompt(invoice: Invoice) -> str:
        """
        Builds a Gemma-optimized plain-text section describing an Invoice.
        """
        lines = [
            "## Invoice",
            f"- Invoice ID      : {invoice.invoice_id}",
            f"- Linked PO       : {invoice.purchase_order_id}",
            f"- Vendor          : {invoice.vendor_id}",
            f"- Invoice Date    : {_safe_str(invoice.invoice_date)}",
            f"- Due Date        : {_safe_str(invoice.due_date)}",
            f"- Base Amount     : {_safe_str(invoice.invoice_amount_inr)} {invoice.currency}",
            f"- Tax Amount      : {_safe_str(invoice.tax_amount_inr)}",
            f"- Total Amount    : {_safe_str(invoice.total_amount_inr)}",
            f"- Match Status    : {invoice.match_status}",
            f"- Invoice Status  : {invoice.invoice_status}",
            f"- Verified By     : {invoice.verified_by_employee_id}",
            f"- Verification Date: {_safe_str(invoice.verification_date)}",
            f"- GST Registered  : {'Yes' if invoice.gst_invoice_number else 'No'}",
        ]
        return "\n".join(lines)

    @staticmethod
    def build_transaction_prompt(transaction: Transaction) -> str:
        """
        Builds a Gemma-optimized plain-text section describing a Transaction.
        Omits payment reference/bank account details; retains amount, method, and status.
        """
        lines = [
            "## Transaction",
            f"- Transaction ID  : {transaction.transaction_id}",
            f"- Linked PO       : {transaction.purchase_order_id}",
            f"- Linked Invoice  : {transaction.invoice_id}",
            f"- Vendor          : {transaction.vendor_id}",
            f"- Approved By     : {transaction.approver_employee_id}",
            f"- Date            : {_safe_str(transaction.transaction_date)}",
            f"- Amount          : {_safe_str(transaction.transaction_amount_inr)} {transaction.currency}",
            f"- Payment Method  : {transaction.payment_method}",
            f"- Payment Status  : {transaction.payment_status}",
            f"- Department      : {transaction.department}",
            f"- Branch          : {transaction.branch}",
        ]
        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Engine-output prompt section builders
    # -----------------------------------------------------------------------

    @staticmethod
    def build_rule_engine_prompt(rule_results: List[RuleResult]) -> str:
        """
        Builds a Gemma-optimized plain-text section summarising all Rule Engine
        violations. Does NOT expose raw transaction or financial amounts.
        """
        if not rule_results:
            return "## Rule Engine Output\nNo violations detected."

        lines = [f"## Rule Engine Output ({len(rule_results)} violation(s) detected)"]
        for i, r in enumerate(rule_results, 1):
            lines.append(f"\n### Violation {i}: {r.rule_name}")
            lines.append(f"- Severity        : {r.severity}")
            lines.append(f"- Risk Score      : {r.risk_score}")
            lines.append(f"- Affected Entities: {', '.join(r.affected_entities) if r.affected_entities else 'N/A'}")
            # Evidence is a list of human-readable strings — safe to include
            if r.evidence:
                lines.append("- Evidence:")
                for ev in r.evidence[:5]:          # cap at 5 evidence items per rule
                    lines.append(f"    • {ev}")
                if len(r.evidence) > 5:
                    lines.append(f"    • … and {len(r.evidence) - 5} more evidence items")
        return "\n".join(lines)

    @staticmethod
    def build_risk_engine_prompt(
        risk_profiles: List[RiskProfile],
        top_n: int = 10
    ) -> str:
        """
        Builds a Gemma-optimized plain-text section summarising Risk Engine scores.
        Shows only entities with non-zero risk, sorted descending by total risk.
        """
        active = [p for p in risk_profiles if p.total_risk > 0]
        active.sort(key=lambda p: p.total_risk, reverse=True)
        top = active[:top_n]

        if not top:
            return "## Risk Engine Output\nNo significant risk scores detected."

        lines = [
            f"## Risk Engine Output "
            f"({len(active)} entity/entities with elevated risk; showing top {len(top)})"
        ]
        for p in top:
            lines.append(
                f"- [{p.entity_type.upper():12s}] {p.entity_id} | "
                f"Base: {p.base_risk:.2f} | "
                f"Propagated: {p.propagated_risk:.2f} | "
                f"Total: {p.total_risk:.2f}"
            )
        return "\n".join(lines)

    @staticmethod
    def build_timeline_prompt(timeline: List[TimelineEntry], limit: int = 15) -> str:
        """
        Builds a Gemma-optimized plain-text section summarising the event timeline.
        """
        if not timeline:
            return "## Event Timeline\nNo events recorded for this entity."

        recent = timeline[-limit:] if len(timeline) > limit else timeline
        lines = [f"## Event Timeline (most recent {len(recent)} of {len(timeline)} events)"]
        for t in recent:
            lines.append(
                f"- [#{t.sequence_number}] {t.timestamp.strftime('%Y-%m-%d %H:%M')} "
                f"| {t.category} | Actor: {t.actor_id} | {t.summary}"
            )
        return "\n".join(lines)

    @staticmethod
    def build_evidence_graph_prompt(graph_json: Dict[str, Any]) -> str:
        """
        Builds a Gemma-optimized plain-text section summarising the Evidence Graph.
        Strips all React Flow UI metadata; focuses on entity relationships.
        """
        nodes = graph_json.get("nodes", [])
        edges = graph_json.get("edges", [])

        if not nodes:
            return "## Evidence Graph\nNo graph data available."

        lines = [
            f"## Evidence Graph Summary",
            f"- Total Entities   : {len(nodes)}",
            f"- Total Connections: {len(edges)}",
        ]

        if nodes:
            lines.append("\n### Entities in Subgraph:")
            for n in nodes[:20]:          # cap for token safety
                label = n.get("data", {}).get("label") if isinstance(n.get("data"), dict) else None
                nid = str(n.get("id", ""))
                lines.append(f"  • {label or nid}")
            if len(nodes) > 20:
                lines.append(f"  • … and {len(nodes) - 20} more entities")

        if edges:
            lines.append("\n### Key Relationships:")
            for e in edges[:20]:
                src = str(e.get("source", ""))
                tgt = str(e.get("target", ""))
                rel = e.get("label") or "→"
                lines.append(f"  • {src}  —[{rel}]→  {tgt}")
            if len(edges) > 20:
                lines.append(f"  • … and {len(edges) - 20} more relationships")

        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Master investigation prompt (Gemma 3 27B optimized)
    # -----------------------------------------------------------------------

    @staticmethod
    def build_investigation_prompt(
        entity_id: str,
        anomaly_description: str,
        rule_results: List[RuleResult],
        risk_profiles: List[RiskProfile],
        timeline: List[TimelineEntry],
        evidence_graph: Dict[str, Any],
        vendor: Optional[Vendor] = None,
        employee: Optional[Employee] = None,
        purchase_orders: Optional[List[PurchaseOrder]] = None,
        invoices: Optional[List[Invoice]] = None,
        transactions: Optional[List[Transaction]] = None,
    ) -> str:
        """
        Assembles a complete, structured investigation prompt for Gemma 3 27B.

        The prompt follows a deliberate top-down layout:
          1. Task framing (what Gemma must do)
          2. Anomaly summary (the triggering observation)
          3. Entity profiles (Vendor / Employee / PO / Invoice / Transaction)
          4. Rule Engine findings
          5. Risk Engine scores
          6. Event Timeline
          7. Evidence Graph
          8. Final instruction (Gemma's expected output format)

        This ordering mirrors how a human analyst would approach an investigation,
        front-loading the most important anchoring facts to maximise Gemma's
        attention on the critical signals before diving into supporting data.

        Returns:
            A plain-text prompt string ready to pass to GemmaService.ask_gemma().
        """
        divider = "\n" + ("─" * 70) + "\n"

        # ── 1. Task framing ────────────────────────────────────────────────
        task_frame = (
            "You are VeriGem, a specialized financial-forensics AI.\n"
            "You have been provided with fully computed outputs from the VeriGem "
            "deterministic engines (Rule Engine, Risk Engine, Timeline, Evidence Graph).\n\n"
            "YOUR TASK:\n"
            "  • Investigate the described anomaly.\n"
            "  • Explain in clear, non-technical language why the violations occurred.\n"
            "  • Trace the causal chain through the evidence graph.\n"
            "  • Identify the root cause.\n"
            "  • Provide 3–5 specific, actionable recommendations.\n\n"
            "CONSTRAINTS:\n"
            "  • Do NOT calculate new risk scores — use only the scores provided.\n"
            "  • Do NOT determine compliance — use only the violations provided.\n"
            "  • Be precise, structured, and executive-ready."
        )

        # ── 2. Anomaly summary ─────────────────────────────────────────────
        anomaly_block = (
            f"## Anomaly Under Investigation\n"
            f"- Focal Entity : {entity_id}\n"
            f"- Description  : {anomaly_description}"
        )

        # ── 3. Entity profiles ─────────────────────────────────────────────
        entity_blocks: List[str] = []

        if vendor:
            entity_blocks.append(PromptBuilder.build_vendor_prompt(vendor))

        if employee:
            entity_blocks.append(PromptBuilder.build_employee_prompt(employee))

        if purchase_orders:
            for po in purchase_orders[:3]:      # top 3 to manage token budget
                entity_blocks.append(PromptBuilder.build_purchase_order_prompt(po))
            if len(purchase_orders) > 3:
                entity_blocks.append(
                    f"  *(+{len(purchase_orders) - 3} more Purchase Orders not shown)*"
                )

        if invoices:
            for inv in invoices[:3]:
                entity_blocks.append(PromptBuilder.build_invoice_prompt(inv))
            if len(invoices) > 3:
                entity_blocks.append(
                    f"  *(+{len(invoices) - 3} more Invoices not shown)*"
                )

        if transactions:
            for txn in transactions[:3]:
                entity_blocks.append(PromptBuilder.build_transaction_prompt(txn))
            if len(transactions) > 3:
                entity_blocks.append(
                    f"  *(+{len(transactions) - 3} more Transactions not shown)*"
                )

        entity_section = (
            "\n\n".join(entity_blocks)
            if entity_blocks
            else "## Entity Profiles\nNo detailed entity data available."
        )

        # ── 4. Rule Engine ─────────────────────────────────────────────────
        rule_section = PromptBuilder.build_rule_engine_prompt(rule_results)

        # ── 5. Risk Engine ─────────────────────────────────────────────────
        risk_section = PromptBuilder.build_risk_engine_prompt(risk_profiles)

        # ── 6. Timeline ────────────────────────────────────────────────────
        timeline_section = PromptBuilder.build_timeline_prompt(timeline)

        # ── 7. Evidence Graph ──────────────────────────────────────────────
        graph_section = PromptBuilder.build_evidence_graph_prompt(evidence_graph)

        # ── 8. Final output instruction ────────────────────────────────────
        output_instruction = (
            "## Required Output Format\n"
            "Respond with the following clearly labelled sections:\n\n"
            "**1. EXECUTIVE SUMMARY** (2–3 sentences)\n"
            "**2. ROOT CAUSE ANALYSIS** (explain the causal chain)\n"
            "**3. ANOMALY EXPLANATION** (what happened and why it is suspicious)\n"
            "**4. ENTITY RISK NARRATIVE** (describe each involved entity's role)\n"
            "**5. RECOMMENDATIONS** (3–5 numbered, specific, actionable steps)\n"
        )

        # ── Assemble ───────────────────────────────────────────────────────
        prompt = divider.join([
            task_frame,
            anomaly_block,
            entity_section,
            rule_section,
            risk_section,
            timeline_section,
            graph_section,
            output_instruction,
        ])

        logger.debug(
            "Investigation prompt built for entity=%s | rules=%d | risk_profiles=%d | "
            "timeline_events=%d | graph_nodes=%d | graph_edges=%d",
            entity_id,
            len(rule_results),
            len(risk_profiles),
            len(timeline),
            len(evidence_graph.get("nodes", [])),
            len(evidence_graph.get("edges", [])),
        )
        return prompt
