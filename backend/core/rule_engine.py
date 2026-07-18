"""
Rule Engine for the VeriGem Financial Digital Twin.

Evaluates business logic rules and anomaly detection algorithms
to generate risk scores, severities, and evidence.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Protocol

from .models import DataStore

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rule Result Definition
# ---------------------------------------------------------------------------

@dataclass
class RuleResult:
    """The outcome of a single rule evaluation."""
    rule_name: str
    risk_score: int
    severity: str
    evidence: list[str]
    affected_entities: list[str] = field(default_factory=list)


class Rule(Protocol):
    """Protocol for all evaluation rules."""
    @property
    def name(self) -> str: ...
    def evaluate(self, store: DataStore) -> list[RuleResult]: ...


# ---------------------------------------------------------------------------
# Rule Implementations
# ---------------------------------------------------------------------------

class DuplicateInvoiceRule:
    @property
    def name(self) -> str:
        return "Duplicate Invoice"

    def evaluate(self, store: DataStore) -> list[RuleResult]:
        results = []
        # Group invoices by vendor_id and total_amount_inr
        groups = defaultdict(list)
        for inv in store.invoices.values():
            key = (inv.vendor_id, inv.total_amount_inr)
            groups[key].append(inv)

        for (vendor_id, amount), invs in groups.items():
            if len(invs) > 1:
                # Sort by date to compare consecutive invoices
                invs.sort(key=lambda x: x.invoice_date or date.min)
                for i in range(1, len(invs)):
                    inv1 = invs[i - 1]
                    inv2 = invs[i]
                    if inv1.invoice_date and inv2.invoice_date:
                        delta = abs((inv2.invoice_date - inv1.invoice_date).days)
                        if delta <= 30:
                            results.append(RuleResult(
                                rule_name=self.name,
                                risk_score=85,
                                severity="High",
                                evidence=[
                                    f"Invoices have the same vendor ({vendor_id}) and amount "
                                    f"(₹{amount:,.2f}) within {delta} days."
                                ],
                                affected_entities=[inv1.invoice_id, inv2.invoice_id, vendor_id]
                            ))
        return results


class InvoiceAfterPaymentRule:
    @property
    def name(self) -> str:
        return "Invoice After Payment"

    def evaluate(self, store: DataStore) -> list[RuleResult]:
        results = []
        for txn in store.transactions.values():
            if txn.payment_status == "Completed" and txn.invoice_id:
                inv = store.invoices.get(txn.invoice_id)
                if inv and inv.invoice_date and txn.transaction_date:
                    if txn.transaction_date < inv.invoice_date:
                        results.append(RuleResult(
                            rule_name=self.name,
                            risk_score=90,
                            severity="Critical",
                            evidence=[
                                f"Payment {txn.transaction_id} occurred on {txn.transaction_date}, "
                                f"which is before the invoice {inv.invoice_id} date of {inv.invoice_date}."
                            ],
                            affected_entities=[txn.transaction_id, inv.invoice_id]
                        ))
        return results


class InvoiceWithoutPORule:
    @property
    def name(self) -> str:
        return "Invoice Without Purchase Order"

    def evaluate(self, store: DataStore) -> list[RuleResult]:
        results = []
        for inv in store.invoices.values():
            if not inv.purchase_order_id or inv.purchase_order_id not in store.purchase_orders:
                results.append(RuleResult(
                    rule_name=self.name,
                    risk_score=75,
                    severity="Medium",
                    evidence=[
                        f"Invoice {inv.invoice_id} has no valid purchase order linked."
                    ],
                    affected_entities=[inv.invoice_id, inv.vendor_id]
                ))
        return results


class VendorRecentlyCreatedRule:
    @property
    def name(self) -> str:
        return "Vendor Recently Created"

    def evaluate(self, store: DataStore) -> list[RuleResult]:
        results = []
        for txn in store.transactions.values():
            vendor = store.vendors.get(txn.vendor_id)
            if vendor and vendor.onboarding_date and txn.transaction_date:
                days_since_onboarding = (txn.transaction_date - vendor.onboarding_date).days
                if 0 <= days_since_onboarding <= 30:
                    results.append(RuleResult(
                        rule_name=self.name,
                        risk_score=60,
                        severity="Medium",
                        evidence=[
                            f"Transaction {txn.transaction_id} was made to vendor {vendor.vendor_id} "
                            f"only {days_since_onboarding} days after onboarding."
                        ],
                        affected_entities=[txn.transaction_id, vendor.vendor_id]
                    ))
        return results


class HighValueTransactionRule:
    @property
    def name(self) -> str:
        return "High Value Transaction"

    def evaluate(self, store: DataStore) -> list[RuleResult]:
        results = []
        threshold = 1_000_000
        for txn in store.transactions.values():
            if txn.transaction_amount_inr > threshold:
                results.append(RuleResult(
                    rule_name=self.name,
                    risk_score=70,
                    severity="High",
                    evidence=[
                        f"Transaction {txn.transaction_id} amount (₹{txn.transaction_amount_inr:,.2f}) "
                        f"exceeds the high value threshold of ₹{threshold:,.2f}."
                    ],
                    affected_entities=[txn.transaction_id, txn.approver_employee_id]
                ))
        return results


class WeekendApprovalRule:
    @property
    def name(self) -> str:
        return "Weekend Approval"

    def evaluate(self, store: DataStore) -> list[RuleResult]:
        results = []
        # Check weekend transactions
        for txn in store.transactions.values():
            if txn.transaction_date and txn.transaction_date.weekday() >= 5:
                results.append(RuleResult(
                    rule_name=self.name,
                    risk_score=50,
                    severity="Low",
                    evidence=[
                        f"Transaction {txn.transaction_id} was approved/processed on a weekend ({txn.transaction_date})."
                    ],
                    affected_entities=[txn.transaction_id, txn.approver_employee_id]
                ))
        # Check weekend purchase orders
        for po in store.purchase_orders.values():
            if po.po_date and po.po_date.weekday() >= 5:
                results.append(RuleResult(
                    rule_name=self.name,
                    risk_score=50,
                    severity="Low",
                    evidence=[
                        f"Purchase Order {po.purchase_order_id} was approved/created on a weekend ({po.po_date})."
                    ],
                    affected_entities=[po.purchase_order_id, po.approved_by_employee_id]
                ))
        return results


class RepeatedApprovalsRule:
    @property
    def name(self) -> str:
        return "Repeated Approvals"

    def evaluate(self, store: DataStore) -> list[RuleResult]:
        results = []
        # Check for segregation of duties violations
        for txn in store.transactions.values():
            po = store.purchase_orders.get(txn.purchase_order_id)
            inv = store.invoices.get(txn.invoice_id)
            if po and inv:
                approvers = [
                    txn.approver_employee_id,
                    po.approved_by_employee_id,
                    inv.verified_by_employee_id
                ]
                approvers = [a for a in approvers if a]
                if len(approvers) >= 2 and len(set(approvers)) == 1:
                    emp = approvers[0]
                    results.append(RuleResult(
                        rule_name=self.name,
                        risk_score=95,
                        severity="Critical",
                        evidence=[
                            f"Employee {emp} repeatedly approved the PO, verified the Invoice, "
                            f"and approved the Transaction in the same chain."
                        ],
                        affected_entities=[txn.transaction_id, po.purchase_order_id, inv.invoice_id, emp]
                    ))
        return results


class PolicyViolationsRule:
    @property
    def name(self) -> str:
        return "Policy Violations"

    def evaluate(self, store: DataStore) -> list[RuleResult]:
        results = []
        # A simple check: PO amount exceeds the employee's maximum approval limit
        for po in store.purchase_orders.values():
            approver = store.employees.get(po.approved_by_employee_id)
            if approver and po.po_amount_inr > approver.max_approval_limit_inr:
                results.append(RuleResult(
                    rule_name=self.name,
                    risk_score=80,
                    severity="High",
                    evidence=[
                        f"PO {po.purchase_order_id} amount (₹{po.po_amount_inr:,.2f}) exceeds "
                        f"approver {approver.employee_id} limit (₹{approver.max_approval_limit_inr:,.2f})."
                    ],
                    affected_entities=[po.purchase_order_id, approver.employee_id]
                ))
        return results


class MissingTaxInformationRule:
    @property
    def name(self) -> str:
        return "Missing Tax Information"

    def evaluate(self, store: DataStore) -> list[RuleResult]:
        results = []
        for vendor in store.vendors.values():
            missing = []
            if not vendor.gst_number or vendor.gst_number.strip() == "" or vendor.gst_number == "N/A":
                missing.append("GST Number")
            if not vendor.pan_number or vendor.pan_number.strip() == "" or vendor.pan_number == "N/A":
                missing.append("PAN Number")

            if missing:
                results.append(RuleResult(
                    rule_name=self.name,
                    risk_score=65,
                    severity="Medium",
                    evidence=[
                        f"Vendor {vendor.vendor_id} is missing tax information: {', '.join(missing)}."
                    ],
                    affected_entities=[vendor.vendor_id]
                ))
        return results


# ---------------------------------------------------------------------------
# Rule Engine
# ---------------------------------------------------------------------------

class RuleEngine:
    """
    Evaluates a suite of rules against the DataStore to identify risks,
    anomalies, and compliance violations.
    """

    def __init__(self) -> None:
        self.rules: list[Rule] = [
            DuplicateInvoiceRule(),
            InvoiceAfterPaymentRule(),
            InvoiceWithoutPORule(),
            VendorRecentlyCreatedRule(),
            HighValueTransactionRule(),
            WeekendApprovalRule(),
            RepeatedApprovalsRule(),
            PolicyViolationsRule(),
            MissingTaxInformationRule(),
        ]
        logger.info("RuleEngine initialised with %d rules.", len(self.rules))

    def evaluate_all(self, store: DataStore) -> list[RuleResult]:
        """Run all registered rules against the datastore and return aggregated results."""
        all_results: list[RuleResult] = []
        for rule in self.rules:
            try:
                results = rule.evaluate(store)
                all_results.extend(results)
                if results:
                    logger.debug("Rule '%s' generated %d results.", rule.name, len(results))
            except Exception as e:
                logger.exception("Error evaluating rule '%s': %s", rule.name, e)
        return all_results
