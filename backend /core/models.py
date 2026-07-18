"""
Domain models for the VeriGem Financial Digital Twin.

Every entity in the financial ecosystem is represented as a frozen dataclass.
Monetary values use Decimal for precision. Dates use datetime/date from stdlib.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------
@dataclass
class Employee:
    """An employee within the organisation's hierarchy."""
    employee_id: str
    employee_name: str
    department: str
    designation: str
    approval_level: int                       # parsed from "L3" → 3
    max_approval_limit_inr: Decimal
    email: str
    phone: str
    city: str
    date_of_joining: date
    employment_status: str                    # Active / Inactive
    reporting_manager_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Vendor
# ---------------------------------------------------------------------------
@dataclass
class Vendor:
    """An external vendor / supplier / contractor."""
    vendor_id: str
    vendor_name: str
    vendor_type: str                          # Contractor, IT Vendor, Goods Supplier, …
    gst_number: str
    pan_number: str
    bank_account_number: str
    ifsc_code: str
    city: str
    state: str
    onboarding_date: date
    vendor_status: str                        # Active / Inactive / Blacklisted / Suspended
    risk_category: str                        # Low / Medium / High
    contact_email: str
    contact_phone: str
    payment_terms_days: int
    last_transaction_date: Optional[date] = None


# ---------------------------------------------------------------------------
# Purchase Order
# ---------------------------------------------------------------------------
@dataclass
class PurchaseOrder:
    """A purchase order raised against a vendor."""
    purchase_order_id: str
    vendor_id: str
    requested_by_employee_id: str
    approved_by_employee_id: str
    department: str
    po_type: str                              # Standard / Contract / Emergency
    procurement_category: str
    po_date: date
    expected_delivery_date: date
    po_amount_inr: Decimal
    currency: str
    payment_terms_days: int
    po_status: str                            # Approved / Closed / Cancelled / Pending
    priority: str                             # Low / Medium / High
    fiscal_year: str                          # "2023-24"
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Invoice
# ---------------------------------------------------------------------------
@dataclass
class Invoice:
    """An invoice submitted against a purchase order."""
    invoice_id: str
    purchase_order_id: str
    vendor_id: str
    vendor_invoice_number: str
    invoice_date: date
    due_date: date
    invoice_amount_inr: Decimal
    tax_amount_inr: Decimal
    total_amount_inr: Decimal
    currency: str
    gst_invoice_number: str
    match_status: str                         # Matched / Partially Matched / Mismatched
    invoice_status: str                       # Paid / Under Verification / Disputed / …
    verified_by_employee_id: str
    verification_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Transaction
# ---------------------------------------------------------------------------
@dataclass
class Transaction:
    """A financial payment transaction."""
    transaction_id: str
    purchase_order_id: str
    invoice_id: str
    vendor_id: str
    approver_employee_id: str
    transaction_date: date
    transaction_amount_inr: Decimal
    currency: str
    payment_method: str                       # NEFT / RTGS / Cheque / UPI
    payment_reference: str
    payment_status: str                       # Completed / Pending / Failed / Reversed
    payment_bank: str
    department: str
    branch: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Audit Log
# ---------------------------------------------------------------------------
@dataclass
class AuditLog:
    """An immutable audit trail entry."""
    log_id: str
    timestamp: datetime
    employee_id: str
    action: str                               # e.g. "Transaction Updated", "Invoice Verified"
    entity_type: str                          # Transaction, Invoice, Purchase Order, Vendor, …
    entity_id: str
    ip_address: str
    device_type: str
    location: str
    status: str                               # Success / Failed / Warning
    severity: str                             # Low / Medium / High / Critical
    remarks: str


# ---------------------------------------------------------------------------
# Compliance Policy
# ---------------------------------------------------------------------------
@dataclass
class CompliancePolicy:
    """A compliance / fraud-detection rule."""
    policy_id: str
    policy_name: str
    policy_category: str                      # Purchase Approval, Invoice Validation, Fraud Detection, …
    description: str
    severity: str                             # Low / Medium / High / Critical
    risk_score: int
    applies_to: str                           # "Purchase Order", "Transaction, Invoice", …
    trigger_condition: str
    recommended_action: str
    status: str                               # Active / Inactive
    created_by: str
    created_date: date
    last_updated: date


# ---------------------------------------------------------------------------
# DataStore — central typed container for all loaded entities
# ---------------------------------------------------------------------------
@dataclass
class DataStore:
    """
    In-memory store holding every loaded entity, keyed by ID.
    This is the single source of truth for the Digital Twin's state.
    """
    employees: dict[str, Employee] = field(default_factory=dict)
    vendors: dict[str, Vendor] = field(default_factory=dict)
    purchase_orders: dict[str, PurchaseOrder] = field(default_factory=dict)
    invoices: dict[str, Invoice] = field(default_factory=dict)
    transactions: dict[str, Transaction] = field(default_factory=dict)
    audit_logs: dict[str, AuditLog] = field(default_factory=dict)
    compliance_policies: dict[str, CompliancePolicy] = field(default_factory=dict)

    # ----- convenience accessors -----

    _ENTITY_MAP: dict[str, str] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self._ENTITY_MAP = {
            "employee": "employees",
            "vendor": "vendors",
            "purchase_order": "purchase_orders",
            "invoice": "invoices",
            "transaction": "transactions",
            "audit_log": "audit_logs",
            "compliance_policy": "compliance_policies",
        }

    def collection(self, entity_type: str) -> dict:
        """Return the dict for a given entity type name."""
        attr = self._ENTITY_MAP.get(entity_type.lower().replace(" ", "_"))
        if attr is None:
            raise KeyError(f"Unknown entity type: {entity_type}")
        return getattr(self, attr)

    def entity_types(self) -> list[str]:
        """Return all recognised entity type names."""
        return list(self._ENTITY_MAP.keys())

    def total_entities(self) -> int:
        """Total count of all loaded entities."""
        return sum(len(self.collection(t)) for t in self.entity_types())
