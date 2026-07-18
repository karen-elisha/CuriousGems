"""
Relationship graph builder for the VeriGem Financial Digital Twin.

Constructs a NetworkX DiGraph that encodes every meaningful relationship
between entities in the financial ecosystem.  Each node is identified by
its entity ID (e.g. "EMP-20001", "VEN-100234").  Virtual nodes are created
for departments and entity-type categories.

Every edge carries a ``relationship_type`` attribute for filtered traversal.
"""

from __future__ import annotations

import logging
from typing import Optional

import networkx as nx

from .models import DataStore

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants — relationship type labels
# ---------------------------------------------------------------------------

REL_REPORTS_TO         = "REPORTS_TO"
REL_EMPLOYED_BY        = "EMPLOYED_BY"
REL_REQUESTED_PO       = "REQUESTED_PO"
REL_APPROVED_PO        = "APPROVED_PO"
REL_PO_TO_VENDOR       = "PO_TO_VENDOR"
REL_INVOICE_FOR_PO     = "INVOICE_FOR_PO"
REL_INVOICE_FROM_VENDOR = "INVOICE_FROM_VENDOR"
REL_INVOICE_VERIFIED_BY = "INVOICE_VERIFIED_BY"
REL_TXN_FOR_PO         = "TXN_FOR_PO"
REL_TXN_FOR_INVOICE    = "TXN_FOR_INVOICE"
REL_TXN_TO_VENDOR      = "TXN_TO_VENDOR"
REL_TXN_APPROVED_BY    = "TXN_APPROVED_BY"
REL_AUDIT_BY_EMPLOYEE  = "AUDIT_BY_EMPLOYEE"
REL_AUDIT_ON_ENTITY    = "AUDIT_ON_ENTITY"
REL_POLICY_APPLIES_TO  = "POLICY_APPLIES_TO"


def _dept_node(department: str) -> str:
    """Generate a virtual department node ID."""
    return f"DEPT:{department}"


def _entity_type_node(entity_type: str) -> str:
    """Generate a virtual entity-type category node ID."""
    return f"TYPE:{entity_type}"


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class RelationshipBuilder:
    """
    Builds the full relationship graph from a populated DataStore.

    Usage::

        builder = RelationshipBuilder(store)
        graph = builder.build()
    """

    def __init__(self, store: DataStore) -> None:
        self._store = store
        self._graph = nx.DiGraph()

    # ---- internal helpers ----

    def _add_node(self, node_id: str, node_type: str, **attrs) -> None:
        """Add a node (idempotent) with a type label."""
        self._graph.add_node(node_id, node_type=node_type, **attrs)

    def _add_edge(
        self,
        source: str,
        target: str,
        relationship_type: str,
        **attrs,
    ) -> None:
        """Add a directed edge with a relationship type."""
        self._graph.add_edge(
            source, target, relationship_type=relationship_type, **attrs
        )

    # ---- per-entity builders ----

    def _build_employee_relationships(self) -> None:
        for emp in self._store.employees.values():
            self._add_node(emp.employee_id, "employee", name=emp.employee_name)

            # → Department
            dept_id = _dept_node(emp.department)
            self._add_node(dept_id, "department", name=emp.department)
            self._add_edge(emp.employee_id, dept_id, REL_EMPLOYED_BY)

            # → Reporting manager
            if emp.reporting_manager_id:
                # Ensure target node exists (even if manager not in dataset)
                self._add_node(emp.reporting_manager_id, "employee")
                self._add_edge(
                    emp.employee_id, emp.reporting_manager_id, REL_REPORTS_TO
                )

    def _build_vendor_nodes(self) -> None:
        for ven in self._store.vendors.values():
            self._add_node(ven.vendor_id, "vendor", name=ven.vendor_name)

    def _build_purchase_order_relationships(self) -> None:
        for po in self._store.purchase_orders.values():
            self._add_node(po.purchase_order_id, "purchase_order")

            # Employee → PO (requested)
            self._add_node(po.requested_by_employee_id, "employee")
            self._add_edge(
                po.requested_by_employee_id, po.purchase_order_id, REL_REQUESTED_PO
            )

            # Employee → PO (approved)
            self._add_node(po.approved_by_employee_id, "employee")
            self._add_edge(
                po.approved_by_employee_id, po.purchase_order_id, REL_APPROVED_PO
            )

            # PO → Vendor
            self._add_node(po.vendor_id, "vendor")
            self._add_edge(po.purchase_order_id, po.vendor_id, REL_PO_TO_VENDOR)

    def _build_invoice_relationships(self) -> None:
        for inv in self._store.invoices.values():
            self._add_node(inv.invoice_id, "invoice")

            # Invoice → PO
            self._add_node(inv.purchase_order_id, "purchase_order")
            self._add_edge(inv.invoice_id, inv.purchase_order_id, REL_INVOICE_FOR_PO)

            # Invoice → Vendor
            self._add_node(inv.vendor_id, "vendor")
            self._add_edge(inv.invoice_id, inv.vendor_id, REL_INVOICE_FROM_VENDOR)

            # Invoice → verifying Employee
            if inv.verified_by_employee_id:
                self._add_node(inv.verified_by_employee_id, "employee")
                self._add_edge(
                    inv.invoice_id, inv.verified_by_employee_id, REL_INVOICE_VERIFIED_BY
                )

    def _build_transaction_relationships(self) -> None:
        for txn in self._store.transactions.values():
            self._add_node(txn.transaction_id, "transaction")

            # TXN → PO
            self._add_node(txn.purchase_order_id, "purchase_order")
            self._add_edge(txn.transaction_id, txn.purchase_order_id, REL_TXN_FOR_PO)

            # TXN → Invoice
            self._add_node(txn.invoice_id, "invoice")
            self._add_edge(txn.transaction_id, txn.invoice_id, REL_TXN_FOR_INVOICE)

            # TXN → Vendor
            self._add_node(txn.vendor_id, "vendor")
            self._add_edge(txn.transaction_id, txn.vendor_id, REL_TXN_TO_VENDOR)

            # TXN → approving Employee
            self._add_node(txn.approver_employee_id, "employee")
            self._add_edge(
                txn.transaction_id, txn.approver_employee_id, REL_TXN_APPROVED_BY
            )

    def _build_audit_log_relationships(self) -> None:
        for log in self._store.audit_logs.values():
            self._add_node(log.log_id, "audit_log")

            # AuditLog → Employee
            if log.employee_id:
                self._add_node(log.employee_id, "employee")
                self._add_edge(log.log_id, log.employee_id, REL_AUDIT_BY_EMPLOYEE)

            # AuditLog → target entity
            if log.entity_id:
                # We may not know the target node's type, so use a generic label
                if not self._graph.has_node(log.entity_id):
                    self._add_node(log.entity_id, log.entity_type.lower().replace(" ", "_"))
                self._add_edge(log.log_id, log.entity_id, REL_AUDIT_ON_ENTITY)

    def _build_compliance_policy_relationships(self) -> None:
        for pol in self._store.compliance_policies.values():
            self._add_node(pol.policy_id, "compliance_policy")

            # Policy → entity type(s) it applies to
            applies_to_types = [t.strip() for t in pol.applies_to.split(",")]
            for entity_type in applies_to_types:
                type_id = _entity_type_node(entity_type)
                self._add_node(type_id, "entity_type_category", name=entity_type)
                self._add_edge(pol.policy_id, type_id, REL_POLICY_APPLIES_TO)

    # ---- public API ----

    def build(self) -> nx.DiGraph:
        """Construct the full relationship graph and return it."""
        logger.info("Building relationship graph …")

        self._build_employee_relationships()
        self._build_vendor_nodes()
        self._build_purchase_order_relationships()
        self._build_invoice_relationships()
        self._build_transaction_relationships()
        self._build_audit_log_relationships()
        self._build_compliance_policy_relationships()

        logger.info(
            "Relationship graph built — %d nodes, %d edges",
            self._graph.number_of_nodes(),
            self._graph.number_of_edges(),
        )
        return self._graph


# ---------------------------------------------------------------------------
# Convenience query helpers (operate on an existing graph)
# ---------------------------------------------------------------------------

def get_neighbors(
    graph: nx.DiGraph,
    node_id: str,
    relationship_type: Optional[str] = None,
    direction: str = "outgoing",
) -> list[tuple[str, dict]]:
    """
    Return neighbours of *node_id*, optionally filtered by relationship type.

    Parameters
    ----------
    direction : "outgoing" | "incoming" | "both"
    """
    results: list[tuple[str, dict]] = []

    if direction in ("outgoing", "both"):
        for _, target, data in graph.out_edges(node_id, data=True):
            if relationship_type is None or data.get("relationship_type") == relationship_type:
                results.append((target, data))

    if direction in ("incoming", "both"):
        for source, _, data in graph.in_edges(node_id, data=True):
            if relationship_type is None or data.get("relationship_type") == relationship_type:
                results.append((source, data))

    return results


def get_node_type(graph: nx.DiGraph, node_id: str) -> Optional[str]:
    """Return the ``node_type`` attribute of a node, or None."""
    return graph.nodes[node_id].get("node_type") if graph.has_node(node_id) else None
