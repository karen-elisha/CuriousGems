"""
FastAPI Router: Reports

Generates four types of Gemma-powered financial reports:
  - Executive Report      : Full org-level performance and risk narrative
  - Department Report     : Department-specific spend, headcount, and risk
  - Compliance Report     : System-wide policy violations and anomaly narrative
  - Risk Summary          : Top-risk entities with propagated scores

All endpoints collect real deterministic metrics from the Digital Twin,
pass them to PromptBuilder to build a structured report prompt, and
delegate to GemmaService for the narrative.

Returns structured JSON — no mock data.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_gemma_service, get_risk_engine, get_rule_engine, get_twin
from core.digital_twin import FinancialDigitalTwin
from core.gemma_service import GemmaService
from core.risk_engine import RiskPropagationEngine
from core.rule_engine import RuleEngine

logger = logging.getLogger("verigem.routers.reports")

router = APIRouter(prefix="/api/reports", tags=["Reports"])


# ---------------------------------------------------------------------------
# Internal prompt builders for each report type
# ---------------------------------------------------------------------------

def _executive_report_prompt(
    twin: FinancialDigitalTwin,
    rule_engine: RuleEngine,
    risk_engine: RiskPropagationEngine,
) -> tuple[str, Dict[str, Any]]:
    """
    Builds the executive report prompt and returns it alongside the
    raw metrics dict used to populate the structured JSON response.
    """
    # Digital Twin metrics
    try:
        spend = twin.get_spend_summary()
    except Exception:
        spend = {}

    departments = []
    try:
        departments = twin.list_departments()
    except Exception:
        pass

    try:
        high_risk_vendors = twin.get_high_risk_vendors()
    except Exception:
        high_risk_vendors = []

    # Rule Engine — all violations
    try:
        all_violations = rule_engine.evaluate_all(twin.store)
    except Exception:
        all_violations = []

    # Risk Engine — top-N risk entities
    all_profiles = [risk_engine.get_profile(eid) for eid in twin.store.vendors]
    all_profiles = [p for p in all_profiles if p and p.total_risk > 0]
    all_profiles.sort(key=lambda p: p.total_risk, reverse=True)
    top_risks = all_profiles[:5]

    metrics = {
        "vendors": len(twin.store.vendors),
        "employees": len(twin.store.employees),
        "purchase_orders": len(twin.store.purchase_orders),
        "invoices": len(twin.store.invoices),
        "transactions": len(twin.store.transactions),
        "departments": departments,
        "total_violations": len(all_violations),
        "high_risk_vendors": len(high_risk_vendors),
        "total_po_value_inr": str(spend.get("total_po_value_inr", "N/A")),
        "total_invoiced_inr": str(spend.get("total_invoiced_inr", "N/A")),
        "total_transaction_spend_inr": str(spend.get("total_transaction_spend_inr", "N/A")),
        "outstanding_invoice_count": spend.get("outstanding_invoice_count", "N/A"),
    }

    # Severity breakdown
    severity_counts: Dict[str, int] = {}
    for v in all_violations:
        severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1

    # Build prompt
    severity_str = " | ".join(f"{k}: {v}" for k, v in severity_counts.items())
    top_risk_str = "\n".join(
        f"  - [{p.entity_type}] {p.entity_id}: Total Risk = {p.total_risk:.2f}"
        for p in top_risks
    )

    prompt = (
        "You are VeriGem, a financial forensics AI. "
        "Generate a concise, executive-level financial intelligence report "
        "based on the deterministic metrics below. "
        "Include a brief narrative on overall risk posture, "
        "compliance health, and key action priorities.\n\n"
        f"## Organisation Metrics\n"
        f"- Vendors           : {metrics['vendors']}\n"
        f"- Employees         : {metrics['employees']}\n"
        f"- Purchase Orders   : {metrics['purchase_orders']}\n"
        f"- Invoices          : {metrics['invoices']}\n"
        f"- Transactions      : {metrics['transactions']}\n"
        f"- Departments       : {len(departments)}\n\n"
        f"## Financial Overview\n"
        f"- Total PO Value    : ₹{metrics['total_po_value_inr']}\n"
        f"- Total Invoiced    : ₹{metrics['total_invoiced_inr']}\n"
        f"- Total Paid        : ₹{metrics['total_transaction_spend_inr']}\n"
        f"- Outstanding Invoices: {metrics['outstanding_invoice_count']}\n\n"
        f"## Compliance Status\n"
        f"- Total Violations  : {len(all_violations)}\n"
        f"- By Severity       : {severity_str if severity_str else 'None'}\n"
        f"- High-Risk Vendors : {len(high_risk_vendors)}\n\n"
        f"## Top 5 Highest-Risk Entities\n"
        f"{top_risk_str if top_risk_str else '  No high-risk entities detected.'}\n\n"
        "## Required Report Format\n"
        "1. **Executive Summary** (3–4 sentences)\n"
        "2. **Key Risks** (3–5 bullets)\n"
        "3. **Compliance Overview** (2–3 sentences)\n"
        "4. **Immediate Action Items** (3 numbered recommendations)\n"
    )

    return prompt, metrics


def _department_report_prompt(
    twin: FinancialDigitalTwin,
    rule_engine: RuleEngine,
    risk_engine: RiskPropagationEngine,
    department_id: str,
) -> tuple[str, Dict[str, Any]]:
    """Build the department report prompt and return it with raw metrics."""
    try:
        dept_summary = twin.get_department_summary(department_id)
    except Exception:
        dept_summary = {}

    # Department-specific entities
    dept_employees = [
        emp for emp in twin.store.employees.values()
        if emp.department == department_id
    ]
    dept_pos = [
        po for po in twin.store.purchase_orders.values()
        if po.department == department_id
    ]
    dept_txns = [
        txn for txn in twin.store.transactions.values()
        if txn.department == department_id
    ]

    # Violations for dept entities
    all_violations = rule_engine.evaluate_all(twin.store)
    dept_entity_ids = (
        {emp.employee_id for emp in dept_employees}
        | {po.purchase_order_id for po in dept_pos}
        | {txn.transaction_id for txn in dept_txns}
    )
    dept_violations = [
        v for v in all_violations
        if any(eid in dept_entity_ids for eid in v.affected_entities)
    ]

    # Risk profiles for dept employees
    emp_risks = [
        p for eid in (emp.employee_id for emp in dept_employees)
        if (p := risk_engine.get_profile(eid)) and p.total_risk > 0
    ]
    emp_risks.sort(key=lambda p: p.total_risk, reverse=True)

    metrics = {
        "department": department_id,
        "employee_count": len(dept_employees),
        "po_count": len(dept_pos),
        "transaction_count": len(dept_txns),
        "violation_count": len(dept_violations),
        "summary": dept_summary,
    }

    violation_lines = "\n".join(
        f"  - [{v.severity}] {v.rule_name}"
        for v in dept_violations[:10]
    ) or "  None detected."

    emp_risk_lines = "\n".join(
        f"  - {p.entity_id}: {p.total_risk:.2f}"
        for p in emp_risks[:5]
    ) or "  No elevated employee risk."

    prompt = (
        "You are VeriGem, a financial forensics AI. "
        "Generate a department-level financial and risk report.\n\n"
        f"## Department: {department_id}\n"
        f"- Employees      : {len(dept_employees)}\n"
        f"- Purchase Orders: {len(dept_pos)}\n"
        f"- Transactions   : {len(dept_txns)}\n"
        f"- Violations     : {len(dept_violations)}\n\n"
        f"## Compliance Violations:\n{violation_lines}\n\n"
        f"## Employee Risk Rankings:\n{emp_risk_lines}\n\n"
        "## Required Report Format\n"
        "1. **Department Summary** (2–3 sentences)\n"
        "2. **Compliance Issues** (describe violations)\n"
        "3. **Risk Areas** (describe highest-risk employees/actions)\n"
        "4. **Recommendations** (3 numbered, specific steps)\n"
    )

    return prompt, metrics


def _compliance_report_prompt(
    twin: FinancialDigitalTwin,
    rule_engine: RuleEngine,
) -> tuple[str, Dict[str, Any]]:
    """Build the system-wide compliance report prompt."""
    all_violations = rule_engine.evaluate_all(twin.store)

    severity_counts: Dict[str, int] = {}
    affected_entity_set: set = set()
    for v in all_violations:
        severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1
        affected_entity_set.update(v.affected_entities)

    active_policies = [p for p in twin.store.compliance_policies.values() if p.status == "Active"]

    metrics = {
        "total_violations": len(all_violations),
        "severity_breakdown": severity_counts,
        "affected_entities": len(affected_entity_set),
        "active_policies": len(active_policies),
        "total_policies": len(twin.store.compliance_policies),
    }

    severity_str = "\n".join(f"  - {k}: {v}" for k, v in severity_counts.items())
    top_violations = all_violations[:10]
    violation_detail = "\n".join(
        f"  - [{v.severity}] {v.rule_name} — affects: {', '.join(v.affected_entities[:3])}"
        for v in top_violations
    ) or "  No violations found."

    policy_summary = "\n".join(
        f"  - [{p.severity}] {p.policy_name}: {p.description[:80]}…"
        for p in active_policies[:8]
    ) or "  No active policies found."

    prompt = (
        "You are VeriGem, a financial forensics AI. "
        "Generate a compliance report based on the rule engine output below.\n\n"
        f"## Compliance Summary\n"
        f"- Total Violations     : {len(all_violations)}\n"
        f"- Affected Entities    : {len(affected_entity_set)}\n"
        f"- Active Policies      : {len(active_policies)}\n\n"
        f"## Severity Breakdown:\n{severity_str or '  None'}\n\n"
        f"## Top Violations:\n{violation_detail}\n\n"
        f"## Active Policy Rules:\n{policy_summary}\n\n"
        "## Required Report Format\n"
        "1. **Compliance Health Score** (narrative, not a number)\n"
        "2. **Critical Violations** (describe top issues)\n"
        "3. **Systemic Patterns** (recurring themes in violations)\n"
        "4. **Regulatory Risk** (potential exposure)\n"
        "5. **Remediation Priorities** (3–5 numbered steps)\n"
    )

    return prompt, metrics


def _risk_summary_prompt(
    twin: FinancialDigitalTwin,
    risk_engine: RiskPropagationEngine,
) -> tuple[str, Dict[str, Any]]:
    """Build the organisation-wide risk summary prompt."""
    all_entity_ids = (
        list(twin.store.vendors.keys())
        + list(twin.store.employees.keys())
        + list(twin.store.purchase_orders.keys())
        + list(twin.store.invoices.keys())
        + list(twin.store.transactions.keys())
    )

    profiles = [
        p for eid in all_entity_ids
        if (p := risk_engine.get_profile(eid)) and p.total_risk > 0
    ]
    profiles.sort(key=lambda p: p.total_risk, reverse=True)
    top_profiles = profiles[:20]

    # Group by entity type
    by_type: Dict[str, List] = {}
    for p in top_profiles:
        by_type.setdefault(p.entity_type, []).append(p)

    metrics = {
        "total_entities_with_risk": len(profiles),
        "top_risk_entities": [
            {
                "entity_id": p.entity_id,
                "entity_type": p.entity_type,
                "base_risk": round(p.base_risk, 2),
                "propagated_risk": round(p.propagated_risk, 2),
                "total_risk": round(p.total_risk, 2),
            }
            for p in top_profiles
        ],
    }

    top_risk_lines = "\n".join(
        f"  [{p.entity_type:12s}] {p.entity_id}: "
        f"base={p.base_risk:.2f}, propagated={p.propagated_risk:.2f}, "
        f"total={p.total_risk:.2f}"
        for p in top_profiles[:15]
    ) or "  No entities with elevated risk."

    type_breakdown = "\n".join(
        f"  - {etype}: {len(plist)} entities"
        for etype, plist in sorted(by_type.items())
    )

    prompt = (
        "You are VeriGem, a financial forensics AI. "
        "Generate a risk summary report based on the Risk Engine output below. "
        "Risk = base (intrinsic) + propagated (inherited from connected entities).\n\n"
        f"## Risk Overview\n"
        f"- Entities with elevated risk: {len(profiles)}\n"
        f"- Risk type breakdown:\n{type_breakdown}\n\n"
        f"## Top 15 High-Risk Entities:\n{top_risk_lines}\n\n"
        "## Required Report Format\n"
        "1. **Risk Overview** (2–3 sentences on overall risk posture)\n"
        "2. **Highest-Risk Entities** (describe top 3–5 entities and why they are risky)\n"
        "3. **Propagation Analysis** (explain how risk is spreading through the network)\n"
        "4. **Mitigation Priorities** (3–5 numbered, actionable steps)\n"
    )

    return prompt, metrics


# ---------------------------------------------------------------------------
# Executive Report
# ---------------------------------------------------------------------------

@router.get(
    "/executive",
    summary="Generate an executive-level financial intelligence report",
)
async def generate_executive_report(
    twin: FinancialDigitalTwin = Depends(get_twin),
    rule_engine: RuleEngine = Depends(get_rule_engine),
    risk_engine: RiskPropagationEngine = Depends(get_risk_engine),
    gemma: GemmaService = Depends(get_gemma_service),
) -> Dict[str, Any]:
    """
    Generate a complete executive-level report covering:
    - Organisation financial overview (spend, PO, invoices)
    - Compliance violation summary (counts by severity)
    - Top-5 highest-risk entities
    - Gemma narrative: summary, key risks, compliance status, action items
    """
    logger.info("Executive report requested.")
    try:
        prompt, metrics = _executive_report_prompt(twin, rule_engine, risk_engine)
        report = gemma.ask_gemma(prompt)
    except Exception as exc:
        logger.error("Executive report failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Executive report generation failed: {exc}")

    return {
        "status": "success",
        "report_type": "executive",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "report": report,
    }


# ---------------------------------------------------------------------------
# Department Report
# ---------------------------------------------------------------------------

@router.post(
    "/department/{department_id}",
    summary="Generate a department-level financial and risk report",
)
async def generate_department_report(
    department_id: str,
    twin: FinancialDigitalTwin = Depends(get_twin),
    rule_engine: RuleEngine = Depends(get_rule_engine),
    risk_engine: RiskPropagationEngine = Depends(get_risk_engine),
    gemma: GemmaService = Depends(get_gemma_service),
) -> Dict[str, Any]:
    """
    Generate a department-specific report covering:
    - Headcount, PO count, transaction count
    - Compliance violations for the department
    - Employee risk rankings
    - Gemma narrative: summary, compliance, risks, recommendations
    """
    logger.info("Department report requested for: %s", department_id)
    try:
        prompt, metrics = _department_report_prompt(twin, rule_engine, risk_engine, department_id)
        report = gemma.ask_gemma(prompt)
    except Exception as exc:
        logger.error("Department report failed for %s: %s", department_id, exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Department report generation failed: {exc}"
        )

    return {
        "status": "success",
        "report_type": "department",
        "department": department_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "report": report,
    }


# ---------------------------------------------------------------------------
# Compliance Report
# ---------------------------------------------------------------------------

@router.post(
    "/compliance",
    summary="Generate a system-wide compliance and anomaly report",
)
async def generate_compliance_report(
    twin: FinancialDigitalTwin = Depends(get_twin),
    rule_engine: RuleEngine = Depends(get_rule_engine),
    gemma: GemmaService = Depends(get_gemma_service),
) -> Dict[str, Any]:
    """
    Generate a full compliance report covering:
    - Violation counts by severity
    - Affected entity count
    - Active policy summary
    - Gemma narrative: health score, critical issues, systemic patterns, remediation
    """
    logger.info("Compliance report requested.")
    try:
        prompt, metrics = _compliance_report_prompt(twin, rule_engine)
        report = gemma.ask_gemma(prompt)
    except Exception as exc:
        logger.error("Compliance report failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Compliance report generation failed: {exc}")

    return {
        "status": "success",
        "report_type": "compliance",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "report": report,
    }


# ---------------------------------------------------------------------------
# Risk Summary Report
# ---------------------------------------------------------------------------

@router.get(
    "/risk",
    summary="Generate an organisation-wide risk summary report",
)
async def generate_risk_report(
    twin: FinancialDigitalTwin = Depends(get_twin),
    risk_engine: RiskPropagationEngine = Depends(get_risk_engine),
    gemma: GemmaService = Depends(get_gemma_service),
) -> Dict[str, Any]:
    """
    Generate a risk summary report covering:
    - Total entities with elevated risk
    - Top 20 highest-risk entities with base and propagated scores
    - Breakdown by entity type
    - Gemma narrative: overview, top entities, propagation analysis, mitigation
    """
    logger.info("Risk summary report requested.")
    try:
        prompt, metrics = _risk_summary_prompt(twin, risk_engine)
        report = gemma.ask_gemma(prompt)
    except Exception as exc:
        logger.error("Risk report failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Risk report generation failed: {exc}")

    return {
        "status": "success",
        "report_type": "risk_summary",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "report": report,
    }
