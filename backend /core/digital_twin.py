"""
Financial Digital Twin — the central orchestrator for VeriGem.

Holds all in-memory state (DataStore + relationship graph) and exposes
query, analytics, and compliance-checking methods.  No API layer here —
this is the pure domain engine that any interface (API, CLI, Gemma) calls.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

import networkx as nx

from .loader import DatasetLoader
from .models import (
    AuditLog,
    CompliancePolicy,
    DataStore,
    Employee,
    Invoice,
    PurchaseOrder,
    Transaction,
    Vendor,
)
from .relationships import (
    REL_APPROVED_PO,
    REL_AUDIT_BY_EMPLOYEE,
    REL_AUDIT_ON_ENTITY,
    REL_EMPLOYED_BY,
    REL_INVOICE_FOR_PO,
    REL_INVOICE_FROM_VENDOR,
    REL_INVOICE_VERIFIED_BY,
    REL_PO_TO_VENDOR,
    REL_REPORTS_TO,
    REL_REQUESTED_PO,
    REL_TXN_APPROVED_BY,
    REL_TXN_FOR_INVOICE,
    REL_TXN_FOR_PO,
    REL_TXN_TO_VENDOR,
    RelationshipBuilder,
    get_neighbors,
    get_node_type,
)

logger = logging.getLogger(__name__)


class FinancialDigitalTwin:
    """
    In-memory Financial Digital Twin.

    Lifecycle::

        twin = FinancialDigitalTwin.boot("/path/to/VeriGem_Datasets")
        print(twin.health())
        profile = twin.get_entity_profile("VEN-100234")
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, store: DataStore, graph: nx.DiGraph) -> None:
        self._store = store
        self._graph = graph
        self._booted_at = datetime.now()

    @classmethod
    def boot(cls, datasets_dir: str) -> "FinancialDigitalTwin":
        """
        Factory: load datasets → build graph → return a ready twin.
        """
        logger.info("Booting Financial Digital Twin …")

        # 1. Load
        loader = DatasetLoader(datasets_dir)
        store = loader.load()

        # 2. Build relationships
        builder = RelationshipBuilder(store)
        graph = builder.build()

        twin = cls(store, graph)
        logger.info("Digital Twin is ONLINE.")
        return twin

    # ------------------------------------------------------------------
    # Health & metadata
    # ------------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        """Return a health-check snapshot."""
        counts = {
            etype: len(self._store.collection(etype))
            for etype in self._store.entity_types()
        }
        return {
            "status": "ONLINE",
            "booted_at": self._booted_at.isoformat(),
            "total_entities": self._store.total_entities(),
            "entity_counts": counts,
            "graph_nodes": self._graph.number_of_nodes(),
            "graph_edges": self._graph.number_of_edges(),
        }

    @property
    def store(self) -> DataStore:
        return self._store

    @property
    def graph(self) -> nx.DiGraph:
        return self._graph

    # ------------------------------------------------------------------
    # Entity access
    # ------------------------------------------------------------------

    def get_entity(self, entity_type: str, entity_id: str) -> Any:
        """Retrieve a single entity by type and ID."""
        collection = self._store.collection(entity_type)
        entity = collection.get(entity_id)
        if entity is None:
            raise KeyError(
                f"{entity_type} '{entity_id}' not found "
                f"({len(collection)} entities in store)"
            )
        return entity

    def get_entities(self, entity_type: str, **filters) -> list[Any]:
        """
        Return entities of *entity_type* matching all keyword filters.

        Example::

            twin.get_entities("vendor", risk_category="High", vendor_status="Active")
        """
        collection = self._store.collection(entity_type)
        results = []
        for entity in collection.values():
            if all(
                getattr(entity, k, None) == v for k, v in filters.items()
            ):
                results.append(entity)
        return results

    # ------------------------------------------------------------------
    # Graph traversal
    # ------------------------------------------------------------------

    def get_related(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both",
    ) -> list[tuple[str, dict]]:
        """
        Return related node IDs (with edge data) for *entity_id*.
        Optionally filter by relationship_type and direction.
        """
        if not self._graph.has_node(entity_id):
            return []
        return get_neighbors(self._graph, entity_id, relationship_type, direction)

    # ------------------------------------------------------------------
    # Entity profiles
    # ------------------------------------------------------------------

    def get_entity_profile(self, entity_id: str) -> dict[str, Any]:
        """
        Build a comprehensive profile for any entity, including the entity
        data itself and all its graph relationships grouped by type.
        """
        # Determine entity type from graph
        node_type = get_node_type(self._graph, entity_id)

        # Try to find the entity in the store
        entity_data = None
        for etype in self._store.entity_types():
            coll = self._store.collection(etype)
            if entity_id in coll:
                entity_data = coll[entity_id]
                break

        # Gather relationships
        relationships: dict[str, list[str]] = defaultdict(list)
        for neighbour_id, edge_data in self.get_related(entity_id, direction="both"):
            rel = edge_data.get("relationship_type", "UNKNOWN")
            relationships[rel].append(neighbour_id)

        return {
            "entity_id": entity_id,
            "node_type": node_type,
            "entity_data": entity_data,
            "relationships": dict(relationships),
            "degree": self._graph.degree(entity_id) if self._graph.has_node(entity_id) else 0,
        }

    # ------------------------------------------------------------------
    # Department analytics
    # ------------------------------------------------------------------

    def get_department_summary(self, department: str) -> dict[str, Any]:
        """
        Aggregated financial summary for a department.
        """
        employees = self.get_entities("employee", department=department)
        emp_ids = {e.employee_id for e in employees}

        # POs requested by this department's employees
        dept_pos = [
            po for po in self._store.purchase_orders.values()
            if po.department == department
        ]
        total_po_amount = sum(po.po_amount_inr for po in dept_pos)

        # Transactions for this department
        dept_txns = [
            t for t in self._store.transactions.values()
            if t.department == department
        ]
        total_txn_amount = sum(t.transaction_amount_inr for t in dept_txns)

        # Unique vendors
        vendor_ids = {po.vendor_id for po in dept_pos}

        return {
            "department": department,
            "employee_count": len(employees),
            "po_count": len(dept_pos),
            "total_po_amount_inr": total_po_amount,
            "transaction_count": len(dept_txns),
            "total_transaction_amount_inr": total_txn_amount,
            "unique_vendors": len(vendor_ids),
            "vendor_ids": sorted(vendor_ids),
        }

    def list_departments(self) -> list[str]:
        """Return all unique department names."""
        return sorted({e.department for e in self._store.employees.values()})

    # ------------------------------------------------------------------
    # Vendor risk analytics
    # ------------------------------------------------------------------

    def get_vendor_risk_profile(self, vendor_id: str) -> dict[str, Any]:
        """
        Build a risk profile for a vendor: transaction stats, PO history,
        invoice match rates, and policy exposure.
        """
        vendor = self.get_entity("vendor", vendor_id)

        # Transactions to this vendor
        txns = [
            t for t in self._store.transactions.values()
            if t.vendor_id == vendor_id
        ]
        txn_amounts = [t.transaction_amount_inr for t in txns]

        # POs to this vendor
        pos = [
            po for po in self._store.purchase_orders.values()
            if po.vendor_id == vendor_id
        ]

        # Invoices from this vendor
        invs = [
            inv for inv in self._store.invoices.values()
            if inv.vendor_id == vendor_id
        ]
        matched = sum(1 for inv in invs if inv.match_status == "Matched")
        mismatched = sum(1 for inv in invs if inv.match_status == "Mismatched")

        return {
            "vendor_id": vendor_id,
            "vendor_name": vendor.vendor_name,
            "vendor_status": vendor.vendor_status,
            "risk_category": vendor.risk_category,
            "transaction_count": len(txns),
            "total_transaction_amount_inr": sum(txn_amounts) if txn_amounts else Decimal("0"),
            "avg_transaction_amount_inr": (
                sum(txn_amounts) / len(txn_amounts) if txn_amounts else Decimal("0")
            ),
            "max_transaction_amount_inr": max(txn_amounts) if txn_amounts else Decimal("0"),
            "po_count": len(pos),
            "invoice_count": len(invs),
            "invoices_matched": matched,
            "invoices_mismatched": mismatched,
            "match_rate": f"{matched / len(invs) * 100:.1f}%" if invs else "N/A",
        }

    def get_high_risk_vendors(self) -> list[dict[str, Any]]:
        """Return risk profiles for all High-risk vendors."""
        high_risk = self.get_entities("vendor", risk_category="High")
        return [self.get_vendor_risk_profile(v.vendor_id) for v in high_risk]

    # ------------------------------------------------------------------
    # Transaction timeline
    # ------------------------------------------------------------------

    def get_transaction_timeline(
        self, entity_id: str, entity_type: Optional[str] = None
    ) -> list[Transaction]:
        """
        Return chronologically sorted transactions linked to *entity_id*.

        Supports vendors, employees (as approvers), POs, and invoices.
        """
        txns: list[Transaction] = []

        for t in self._store.transactions.values():
            if entity_id in (
                t.vendor_id,
                t.approver_employee_id,
                t.purchase_order_id,
                t.invoice_id,
            ):
                txns.append(t)

        txns.sort(key=lambda t: t.transaction_date or date.min)
        return txns

    # ------------------------------------------------------------------
    # Financial aggregation
    # ------------------------------------------------------------------

    def get_spend_summary(self) -> dict[str, Any]:
        """Organisation-wide spend summary."""
        total_txn = sum(
            t.transaction_amount_inr for t in self._store.transactions.values()
        )
        total_po = sum(
            po.po_amount_inr for po in self._store.purchase_orders.values()
        )
        total_invoiced = sum(
            inv.total_amount_inr for inv in self._store.invoices.values()
        )

        # Per fiscal year
        by_fy: dict[str, Decimal] = defaultdict(Decimal)
        for po in self._store.purchase_orders.values():
            by_fy[po.fiscal_year] += po.po_amount_inr

        # Per department
        by_dept: dict[str, Decimal] = defaultdict(Decimal)
        for t in self._store.transactions.values():
            by_dept[t.department] += t.transaction_amount_inr

        # Per vendor (top 10)
        by_vendor: dict[str, Decimal] = defaultdict(Decimal)
        for t in self._store.transactions.values():
            by_vendor[t.vendor_id] += t.transaction_amount_inr
        top_vendors = sorted(by_vendor.items(), key=lambda x: x[1], reverse=True)[:10]

        # Outstanding invoices
        outstanding = [
            inv for inv in self._store.invoices.values()
            if inv.invoice_status not in ("Paid", "Cancelled", "Rejected")
        ]
        outstanding_amount = sum(inv.total_amount_inr for inv in outstanding)

        return {
            "total_transaction_spend_inr": total_txn,
            "total_po_value_inr": total_po,
            "total_invoiced_inr": total_invoiced,
            "outstanding_invoice_count": len(outstanding),
            "outstanding_invoice_amount_inr": outstanding_amount,
            "spend_by_fiscal_year": dict(sorted(by_fy.items())),
            "spend_by_department": dict(sorted(by_dept.items(), key=lambda x: x[1], reverse=True)),
            "top_10_vendors_by_spend": [
                {"vendor_id": vid, "total_spend_inr": amt} for vid, amt in top_vendors
            ],
        }

    # ------------------------------------------------------------------
    # Approval chain analysis
    # ------------------------------------------------------------------

    def get_approval_chain(self, employee_id: str) -> list[Employee]:
        """
        Walk the reporting chain upward from an employee to the top.
        Returns the list [employee, manager, manager's manager, …].
        """
        chain: list[Employee] = []
        visited: set[str] = set()
        current_id = employee_id

        while current_id and current_id not in visited:
            visited.add(current_id)
            emp = self._store.employees.get(current_id)
            if emp is None:
                break
            chain.append(emp)
            current_id = emp.reporting_manager_id

        return chain

    # ------------------------------------------------------------------
    # Compliance violation detection
    # ------------------------------------------------------------------

    def get_compliance_violations(
        self, policy_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Evaluate compliance policies against live data and return violations.

        If *policy_id* is given, check only that policy.  Otherwise check all
        active policies.

        Currently implements rule-based checks for the most impactful policies.
        """
        policies = (
            [self.get_entity("compliance_policy", policy_id)]
            if policy_id
            else [
                p for p in self._store.compliance_policies.values()
                if p.status == "Active"
            ]
        )

        violations: list[dict[str, Any]] = []

        for pol in policies:
            checker = self._POLICY_CHECKERS.get(pol.policy_id)
            if checker:
                found = checker(self, pol)
                violations.extend(found)

        return violations

    # ---- individual policy checkers ----

    def _check_pol_0001_high_value_approval(
        self, policy: CompliancePolicy
    ) -> list[dict[str, Any]]:
        """POL-0001: PO amount exceeds approver's max approval limit."""
        violations = []
        for po in self._store.purchase_orders.values():
            approver = self._store.employees.get(po.approved_by_employee_id)
            if approver and po.po_amount_inr > approver.max_approval_limit_inr:
                violations.append({
                    "policy_id": policy.policy_id,
                    "policy_name": policy.policy_name,
                    "severity": policy.severity,
                    "entity_type": "Purchase Order",
                    "entity_id": po.purchase_order_id,
                    "detail": (
                        f"PO amount ₹{po.po_amount_inr:,.2f} exceeds approver "
                        f"{approver.employee_id} ({approver.employee_name}) "
                        f"limit of ₹{approver.max_approval_limit_inr:,.2f}"
                    ),
                })
        return violations

    def _check_pol_0002_approval_limit(
        self, policy: CompliancePolicy
    ) -> list[dict[str, Any]]:
        """POL-0002: Same as POL-0001 but specifically for limit enforcement."""
        # Covered by POL-0001 logic — reuse
        return self._check_pol_0001_high_value_approval(policy)

    def _check_pol_0003_blacklisted_vendor(
        self, policy: CompliancePolicy
    ) -> list[dict[str, Any]]:
        """POL-0003: Transactions involving blacklisted vendors."""
        violations = []
        blacklisted = {
            v.vendor_id for v in self._store.vendors.values()
            if v.vendor_status == "Blacklisted"
        }
        if not blacklisted:
            return violations

        for txn in self._store.transactions.values():
            if txn.vendor_id in blacklisted:
                violations.append({
                    "policy_id": policy.policy_id,
                    "policy_name": policy.policy_name,
                    "severity": policy.severity,
                    "entity_type": "Transaction",
                    "entity_id": txn.transaction_id,
                    "detail": (
                        f"Transaction to blacklisted vendor {txn.vendor_id}"
                    ),
                })
        return violations

    def _check_pol_0004_duplicate_invoice(
        self, policy: CompliancePolicy
    ) -> list[dict[str, Any]]:
        """POL-0004: Duplicate invoices (same vendor, PO, and amount within 30 days)."""
        violations = []
        # Group invoices by (vendor, PO, amount)
        groups: dict[tuple, list[Invoice]] = defaultdict(list)
        for inv in self._store.invoices.values():
            key = (inv.vendor_id, inv.purchase_order_id, inv.total_amount_inr)
            groups[key].append(inv)

        for key, invs in groups.items():
            if len(invs) < 2:
                continue
            invs.sort(key=lambda i: i.invoice_date or date.min)
            for i in range(1, len(invs)):
                if invs[i].invoice_date and invs[i - 1].invoice_date:
                    delta = (invs[i].invoice_date - invs[i - 1].invoice_date).days
                    if delta <= 30:
                        violations.append({
                            "policy_id": policy.policy_id,
                            "policy_name": policy.policy_name,
                            "severity": policy.severity,
                            "entity_type": "Invoice",
                            "entity_id": invs[i].invoice_id,
                            "detail": (
                                f"Potential duplicate of {invs[i-1].invoice_id} — "
                                f"same vendor {key[0]}, PO {key[1]}, "
                                f"amount ₹{key[2]:,.2f}, {delta} days apart"
                            ),
                        })
        return violations

    def _check_pol_0005_amount_mismatch(
        self, policy: CompliancePolicy
    ) -> list[dict[str, Any]]:
        """POL-0005: Invoice amount deviates >10% from PO amount."""
        violations = []
        for inv in self._store.invoices.values():
            po = self._store.purchase_orders.get(inv.purchase_order_id)
            if po and po.po_amount_inr > 0:
                deviation = abs(inv.invoice_amount_inr - po.po_amount_inr) / po.po_amount_inr
                if deviation > Decimal("0.10"):
                    violations.append({
                        "policy_id": policy.policy_id,
                        "policy_name": policy.policy_name,
                        "severity": policy.severity,
                        "entity_type": "Invoice",
                        "entity_id": inv.invoice_id,
                        "detail": (
                            f"Invoice amount ₹{inv.invoice_amount_inr:,.2f} deviates "
                            f"{deviation * 100:.1f}% from PO {po.purchase_order_id} "
                            f"amount ₹{po.po_amount_inr:,.2f}"
                        ),
                    })
        return violations

    def _check_pol_0008_round_number(
        self, policy: CompliancePolicy
    ) -> list[dict[str, Any]]:
        """POL-0008: Round-number payments (multiples of 50,000 with no fraction)."""
        violations = []
        threshold = Decimal("50000")
        for txn in self._store.transactions.values():
            amt = txn.transaction_amount_inr
            if amt > 0 and amt % threshold == 0:
                violations.append({
                    "policy_id": policy.policy_id,
                    "policy_name": policy.policy_name,
                    "severity": policy.severity,
                    "entity_type": "Transaction",
                    "entity_id": txn.transaction_id,
                    "detail": (
                        f"Round-number payment ₹{amt:,.2f} "
                        f"to vendor {txn.vendor_id}"
                    ),
                })
        return violations

    def _check_pol_0012_duplicate_payment(
        self, policy: CompliancePolicy
    ) -> list[dict[str, Any]]:
        """POL-0012: Multiple completed payments for same invoice."""
        violations = []
        by_invoice: dict[str, list[Transaction]] = defaultdict(list)
        for txn in self._store.transactions.values():
            if txn.payment_status == "Completed":
                by_invoice[txn.invoice_id].append(txn)

        for inv_id, txns in by_invoice.items():
            if len(txns) > 1:
                ids = [t.transaction_id for t in txns]
                violations.append({
                    "policy_id": policy.policy_id,
                    "policy_name": policy.policy_name,
                    "severity": policy.severity,
                    "entity_type": "Transaction",
                    "entity_id": ids[0],
                    "detail": (
                        f"Invoice {inv_id} has {len(txns)} completed payments: "
                        f"{', '.join(ids)}"
                    ),
                })
        return violations

    def _check_pol_0014_payment_after_cancellation(
        self, policy: CompliancePolicy
    ) -> list[dict[str, Any]]:
        """POL-0014: Payments against rejected/disputed/cancelled invoices."""
        violations = []
        bad_statuses = {"Rejected", "Disputed", "Cancelled"}
        cancelled_invoices = {
            inv.invoice_id
            for inv in self._store.invoices.values()
            if inv.invoice_status in bad_statuses
        }
        for txn in self._store.transactions.values():
            if txn.invoice_id in cancelled_invoices:
                violations.append({
                    "policy_id": policy.policy_id,
                    "policy_name": policy.policy_name,
                    "severity": policy.severity,
                    "entity_type": "Transaction",
                    "entity_id": txn.transaction_id,
                    "detail": (
                        f"Payment against cancelled/rejected invoice {txn.invoice_id}"
                    ),
                })
        return violations

    def _check_pol_0018_inactive_vendor_txn(
        self, policy: CompliancePolicy
    ) -> list[dict[str, Any]]:
        """POL-0018: Transactions with inactive/suspended vendors."""
        violations = []
        bad_vendors = {
            v.vendor_id for v in self._store.vendors.values()
            if v.vendor_status in ("Inactive", "Suspended")
        }
        for txn in self._store.transactions.values():
            if txn.vendor_id in bad_vendors:
                violations.append({
                    "policy_id": policy.policy_id,
                    "policy_name": policy.policy_name,
                    "severity": policy.severity,
                    "entity_type": "Transaction",
                    "entity_id": txn.transaction_id,
                    "detail": (
                        f"Transaction to inactive/suspended vendor {txn.vendor_id}"
                    ),
                })
        return violations

    def _check_pol_0020_segregation_of_duties(
        self, policy: CompliancePolicy
    ) -> list[dict[str, Any]]:
        """POL-0020: Same employee requests, approves, or verifies the same PO chain."""
        violations = []
        for po in self._store.purchase_orders.values():
            actors = {po.requested_by_employee_id, po.approved_by_employee_id}

            # Check invoices linked to this PO
            linked_invoices = [
                inv for inv in self._store.invoices.values()
                if inv.purchase_order_id == po.purchase_order_id
            ]
            for inv in linked_invoices:
                if inv.verified_by_employee_id in actors:
                    violations.append({
                        "policy_id": policy.policy_id,
                        "policy_name": policy.policy_name,
                        "severity": policy.severity,
                        "entity_type": "Purchase Order",
                        "entity_id": po.purchase_order_id,
                        "detail": (
                            f"Employee {inv.verified_by_employee_id} verified invoice "
                            f"{inv.invoice_id} but also "
                            f"{'requested' if inv.verified_by_employee_id == po.requested_by_employee_id else 'approved'} "
                            f"the PO"
                        ),
                    })

            # Same requester and approver
            if po.requested_by_employee_id == po.approved_by_employee_id:
                violations.append({
                    "policy_id": policy.policy_id,
                    "policy_name": policy.policy_name,
                    "severity": policy.severity,
                    "entity_type": "Purchase Order",
                    "entity_id": po.purchase_order_id,
                    "detail": (
                        f"Employee {po.requested_by_employee_id} both requested "
                        f"and approved this PO"
                    ),
                })

        return violations

    # Registry mapping policy_id → checker method
    _POLICY_CHECKERS: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# Register policy checkers after class definition
# ---------------------------------------------------------------------------
FinancialDigitalTwin._POLICY_CHECKERS = {
    "POL-0001": FinancialDigitalTwin._check_pol_0001_high_value_approval,
    "POL-0002": FinancialDigitalTwin._check_pol_0002_approval_limit,
    "POL-0003": FinancialDigitalTwin._check_pol_0003_blacklisted_vendor,
    "POL-0004": FinancialDigitalTwin._check_pol_0004_duplicate_invoice,
    "POL-0005": FinancialDigitalTwin._check_pol_0005_amount_mismatch,
    "POL-0008": FinancialDigitalTwin._check_pol_0008_round_number,
    "POL-0012": FinancialDigitalTwin._check_pol_0012_duplicate_payment,
    "POL-0014": FinancialDigitalTwin._check_pol_0014_payment_after_cancellation,
    "POL-0018": FinancialDigitalTwin._check_pol_0018_inactive_vendor_txn,
    "POL-0020": FinancialDigitalTwin._check_pol_0020_segregation_of_duties,
}
