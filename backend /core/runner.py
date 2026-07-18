"""
VeriGem Backend Core — Runner

Boots the Financial Digital Twin, runs a health check, and executes
demonstration queries to prove the twin is fully operational.

Usage::

    cd backend
    python -m core.runner
"""

from __future__ import annotations

import logging
import sys
from decimal import Decimal
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("verigem.runner")


def _fmt_inr(amount: Decimal) -> str:
    """Format a Decimal amount as ₹X,XX,XXX.XX (Indian style for display)."""
    return f"₹{amount:,.2f}"


def main() -> None:
    from .digital_twin import FinancialDigitalTwin

    # ------------------------------------------------------------------
    # 1. Locate datasets
    # ------------------------------------------------------------------
    datasets_dir = Path(__file__).resolve().parent.parent / "datasets" / "VeriGem_Datasets"
    if not datasets_dir.is_dir():
        logger.error("Datasets directory not found: %s", datasets_dir)
        sys.exit(1)

    # ------------------------------------------------------------------
    # 2. Boot the Digital Twin
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  VeriGem Financial Digital Twin — Boot Sequence")
    print("=" * 70 + "\n")

    twin = FinancialDigitalTwin.boot(str(datasets_dir))

    # ------------------------------------------------------------------
    # 3. Health check
    # ------------------------------------------------------------------
    health = twin.health()
    print("\n" + "-" * 70)
    print("  HEALTH CHECK")
    print("-" * 70)
    print(f"  Status         : {health['status']}")
    print(f"  Booted at      : {health['booted_at']}")
    print(f"  Total entities : {health['total_entities']:,}")
    print(f"  Graph nodes    : {health['graph_nodes']:,}")
    print(f"  Graph edges    : {health['graph_edges']:,}")
    print()
    print("  Entity counts:")
    for etype, count in health["entity_counts"].items():
        print(f"    {etype:25s} : {count:,}")

    # ------------------------------------------------------------------
    # 4. Spend summary
    # ------------------------------------------------------------------
    spend = twin.get_spend_summary()
    print("\n" + "-" * 70)
    print("  FINANCIAL SUMMARY")
    print("-" * 70)
    print(f"  Total PO value            : {_fmt_inr(spend['total_po_value_inr'])}")
    print(f"  Total invoiced            : {_fmt_inr(spend['total_invoiced_inr'])}")
    print(f"  Total transaction spend   : {_fmt_inr(spend['total_transaction_spend_inr'])}")
    print(f"  Outstanding invoices      : {spend['outstanding_invoice_count']} ({_fmt_inr(spend['outstanding_invoice_amount_inr'])})")
    print()
    print("  Spend by fiscal year:")
    for fy, amt in spend["spend_by_fiscal_year"].items():
        print(f"    {fy:15s} : {_fmt_inr(amt)}")
    print()
    print("  Top 10 vendors by spend:")
    for i, v in enumerate(spend["top_10_vendors_by_spend"], 1):
        vendor = twin.store.vendors.get(v["vendor_id"])
        name = vendor.vendor_name if vendor else v["vendor_id"]
        print(f"    {i:2d}. {name:40s} {_fmt_inr(v['total_spend_inr'])}")

    # ------------------------------------------------------------------
    # 5. Department analysis
    # ------------------------------------------------------------------
    departments = twin.list_departments()
    print("\n" + "-" * 70)
    print("  DEPARTMENT ANALYSIS")
    print("-" * 70)
    for dept in departments:
        summary = twin.get_department_summary(dept)
        print(
            f"  {dept:20s}  | "
            f"Employees: {summary['employee_count']:3d}  | "
            f"POs: {summary['po_count']:4d}  | "
            f"Spend: {_fmt_inr(summary['total_transaction_amount_inr']):>20s}  | "
            f"Vendors: {summary['unique_vendors']:3d}"
        )

    # ------------------------------------------------------------------
    # 6. High-risk vendors
    # ------------------------------------------------------------------
    high_risk = twin.get_high_risk_vendors()
    print("\n" + "-" * 70)
    print(f"  HIGH-RISK VENDORS ({len(high_risk)} found)")
    print("-" * 70)
    for vp in high_risk[:10]:
        print(
            f"  {vp['vendor_id']}  {vp['vendor_name']:40s}  "
            f"Status: {vp['vendor_status']:12s}  "
            f"Txns: {vp['transaction_count']:3d}  "
            f"Total: {_fmt_inr(vp['total_transaction_amount_inr']):>18s}  "
            f"Match: {vp['match_rate']}"
        )

    # ------------------------------------------------------------------
    # 7. Sample entity profile
    # ------------------------------------------------------------------
    sample_vendor_id = next(iter(twin.store.vendors))
    profile = twin.get_entity_profile(sample_vendor_id)
    print("\n" + "-" * 70)
    print(f"  ENTITY PROFILE: {sample_vendor_id}")
    print("-" * 70)
    print(f"  Node type  : {profile['node_type']}")
    print(f"  Degree     : {profile['degree']}")
    print(f"  Relationships:")
    for rel_type, targets in profile["relationships"].items():
        print(f"    {rel_type:30s} → {len(targets)} connections")

    # ------------------------------------------------------------------
    # 8. Approval chain example
    # ------------------------------------------------------------------
    sample_emp_id = next(iter(twin.store.employees))
    chain = twin.get_approval_chain(sample_emp_id)
    print("\n" + "-" * 70)
    print(f"  APPROVAL CHAIN from {sample_emp_id}")
    print("-" * 70)
    for i, emp in enumerate(chain):
        indent = "  " + "  → " * i
        print(
            f"{indent}{emp.employee_id} — {emp.employee_name} "
            f"({emp.designation}, L{emp.approval_level}, "
            f"limit {_fmt_inr(emp.max_approval_limit_inr)})"
        )

    # ------------------------------------------------------------------
    # 9. Transaction timeline example
    # ------------------------------------------------------------------
    timeline = twin.get_transaction_timeline(sample_vendor_id)
    print("\n" + "-" * 70)
    print(f"  TRANSACTION TIMELINE for {sample_vendor_id} ({len(timeline)} transactions)")
    print("-" * 70)
    for txn in timeline[:5]:
        print(
            f"  {txn.transaction_date}  {txn.transaction_id}  "
            f"{_fmt_inr(txn.transaction_amount_inr):>18s}  "
            f"{txn.payment_method:6s}  {txn.payment_status}"
        )
    if len(timeline) > 5:
        print(f"  … and {len(timeline) - 5} more")

    # ------------------------------------------------------------------
    # 10. Compliance violations
    # ------------------------------------------------------------------
    violations = twin.get_compliance_violations()
    print("\n" + "-" * 70)
    print(f"  COMPLIANCE VIOLATIONS ({len(violations)} detected)")
    print("-" * 70)

    # Group by policy
    by_policy: dict[str, list] = {}
    for v in violations:
        by_policy.setdefault(v["policy_id"], []).append(v)

    for pid, vlist in sorted(by_policy.items()):
        sample = vlist[0]
        print(
            f"  {pid}  {sample['policy_name']:40s}  "
            f"[{sample['severity']:8s}]  "
            f"{len(vlist):4d} violation(s)"
        )

    # Show a few detail examples
    print()
    print("  Sample violations:")
    for v in violations[:5]:
        print(f"    [{v['severity']}] {v['policy_id']} | {v['entity_id']} — {v['detail']}")

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  ✅  Digital Twin is FULLY OPERATIONAL")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
