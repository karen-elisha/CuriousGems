"""
CSV dataset loader for the VeriGem Financial Digital Twin.

Reads all 7 datasets from the VeriGem_Datasets directory, parses each row
into the corresponding domain dataclass, and returns a populated DataStore.
"""

from __future__ import annotations

import csv
import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Optional

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

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _parse_date(value: str) -> Optional[date]:
    """Parse an ISO date string (YYYY-MM-DD) into a date object."""
    value = value.strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        logger.warning("Unparseable date: %r", value)
        return None


def _parse_datetime(value: str) -> Optional[datetime]:
    """Parse an ISO datetime string into a datetime object."""
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        logger.warning("Unparseable datetime: %r", value)
        return None


def _parse_decimal(value: str) -> Decimal:
    """Parse a numeric string into Decimal. Returns Decimal('0') on failure."""
    value = value.strip().replace(",", "")
    if not value:
        return Decimal("0")
    try:
        return Decimal(value)
    except InvalidOperation:
        logger.warning("Unparseable decimal: %r", value)
        return Decimal("0")


def _parse_int(value: str, default: int = 0) -> int:
    """Parse an integer string. Returns *default* on failure."""
    value = value.strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning("Unparseable int: %r", value)
        return default


def _parse_approval_level(value: str) -> int:
    """Convert approval level codes like 'L3' into the integer 3."""
    value = value.strip().upper()
    if value.startswith("L"):
        return _parse_int(value[1:], default=0)
    return _parse_int(value, default=0)


def _strip(value: str) -> str:
    """Strip whitespace (and stray \\r) from a field."""
    return value.strip().strip("\r")


# ---------------------------------------------------------------------------
# Row → Model converters
# ---------------------------------------------------------------------------

def _row_to_employee(row: dict[str, str]) -> Employee:
    return Employee(
        employee_id=_strip(row["employee_id"]),
        employee_name=_strip(row["employee_name"]),
        department=_strip(row["department"]),
        designation=_strip(row["designation"]),
        approval_level=_parse_approval_level(row["approval_level"]),
        max_approval_limit_inr=_parse_decimal(row["max_approval_limit_inr"]),
        email=_strip(row["email"]),
        phone=_strip(row["phone"]),
        city=_strip(row["city"]),
        date_of_joining=_parse_date(row["date_of_joining"]),
        employment_status=_strip(row["employment_status"]),
        reporting_manager_id=_strip(row["reporting_manager_id"]) or None,
    )


def _row_to_vendor(row: dict[str, str]) -> Vendor:
    return Vendor(
        vendor_id=_strip(row["vendor_id"]),
        vendor_name=_strip(row["vendor_name"]),
        vendor_type=_strip(row["vendor_type"]),
        gst_number=_strip(row["gst_number"]),
        pan_number=_strip(row["pan_number"]),
        bank_account_number=_strip(row["bank_account_number"]),
        ifsc_code=_strip(row["ifsc_code"]),
        city=_strip(row["city"]),
        state=_strip(row["state"]),
        onboarding_date=_parse_date(row["onboarding_date"]),
        vendor_status=_strip(row["vendor_status"]),
        risk_category=_strip(row["risk_category"]),
        contact_email=_strip(row["contact_email"]),
        contact_phone=_strip(row["contact_phone"]),
        payment_terms_days=_parse_int(row["payment_terms_days"]),
        last_transaction_date=_parse_date(row.get("last_transaction_date", "")),
    )


def _row_to_purchase_order(row: dict[str, str]) -> PurchaseOrder:
    return PurchaseOrder(
        purchase_order_id=_strip(row["purchase_order_id"]),
        vendor_id=_strip(row["vendor_id"]),
        requested_by_employee_id=_strip(row["requested_by_employee_id"]),
        approved_by_employee_id=_strip(row["approved_by_employee_id"]),
        department=_strip(row["department"]),
        po_type=_strip(row["po_type"]),
        procurement_category=_strip(row["procurement_category"]),
        po_date=_parse_date(row["po_date"]),
        expected_delivery_date=_parse_date(row["expected_delivery_date"]),
        po_amount_inr=_parse_decimal(row["po_amount_inr"]),
        currency=_strip(row["currency"]),
        payment_terms_days=_parse_int(row["payment_terms_days"]),
        po_status=_strip(row["po_status"]),
        priority=_strip(row["priority"]),
        fiscal_year=_strip(row["fiscal_year"]),
        created_at=_parse_datetime(row["created_at"]),
        updated_at=_parse_datetime(row["updated_at"]),
    )


def _row_to_invoice(row: dict[str, str]) -> Invoice:
    return Invoice(
        invoice_id=_strip(row["invoice_id"]),
        purchase_order_id=_strip(row["purchase_order_id"]),
        vendor_id=_strip(row["vendor_id"]),
        vendor_invoice_number=_strip(row["vendor_invoice_number"]),
        invoice_date=_parse_date(row["invoice_date"]),
        due_date=_parse_date(row["due_date"]),
        invoice_amount_inr=_parse_decimal(row["invoice_amount_inr"]),
        tax_amount_inr=_parse_decimal(row["tax_amount_inr"]),
        total_amount_inr=_parse_decimal(row["total_amount_inr"]),
        currency=_strip(row["currency"]),
        gst_invoice_number=_strip(row["gst_invoice_number"]),
        match_status=_strip(row["match_status"]),
        invoice_status=_strip(row["invoice_status"]),
        verified_by_employee_id=_strip(row["verified_by_employee_id"]),
        verification_date=_parse_date(row.get("verification_date", "")),
        created_at=_parse_datetime(row.get("created_at", "")),
        updated_at=_parse_datetime(row.get("updated_at", "")),
    )


def _row_to_transaction(row: dict[str, str]) -> Transaction:
    return Transaction(
        transaction_id=_strip(row["transaction_id"]),
        purchase_order_id=_strip(row["purchase_order_id"]),
        invoice_id=_strip(row["invoice_id"]),
        vendor_id=_strip(row["vendor_id"]),
        approver_employee_id=_strip(row["approver_employee_id"]),
        transaction_date=_parse_date(row["transaction_date"]),
        transaction_amount_inr=_parse_decimal(row["transaction_amount_inr"]),
        currency=_strip(row["currency"]),
        payment_method=_strip(row["payment_method"]),
        payment_reference=_strip(row["payment_reference"]),
        payment_status=_strip(row["payment_status"]),
        payment_bank=_strip(row["payment_bank"]),
        department=_strip(row["department"]),
        branch=_strip(row["branch"]),
        created_at=_parse_datetime(row["created_at"]),
        updated_at=_parse_datetime(row["updated_at"]),
    )


def _row_to_audit_log(row: dict[str, str]) -> AuditLog:
    return AuditLog(
        log_id=_strip(row["log_id"]),
        timestamp=_parse_datetime(row["timestamp"]),
        employee_id=_strip(row["employee_id"]),
        action=_strip(row["action"]),
        entity_type=_strip(row["entity_type"]),
        entity_id=_strip(row["entity_id"]),
        ip_address=_strip(row["ip_address"]),
        device_type=_strip(row["device_type"]),
        location=_strip(row["location"]),
        status=_strip(row["status"]),
        severity=_strip(row["severity"]),
        remarks=_strip(row["remarks"]),
    )


def _row_to_compliance_policy(row: dict[str, str]) -> CompliancePolicy:
    return CompliancePolicy(
        policy_id=_strip(row["policy_id"]),
        policy_name=_strip(row["policy_name"]),
        policy_category=_strip(row["policy_category"]),
        description=_strip(row["description"]),
        severity=_strip(row["severity"]),
        risk_score=_parse_int(row["risk_score"]),
        applies_to=_strip(row["applies_to"]),
        trigger_condition=_strip(row["trigger_condition"]),
        recommended_action=_strip(row["recommended_action"]),
        status=_strip(row["status"]),
        created_by=_strip(row["created_by"]),
        created_date=_parse_date(row["created_date"]),
        last_updated=_parse_date(row["last_updated"]),
    )


# ---------------------------------------------------------------------------
# Generic CSV reader
# ---------------------------------------------------------------------------

def _load_csv(filepath: Path, converter, id_field: str) -> dict[str, Any]:
    """
    Read a CSV file and return a dict keyed by *id_field*.

    Uses the stdlib csv.DictReader which handles quoted fields with commas,
    Windows line-endings, etc.
    """
    entities: dict[str, Any] = {}
    errors = 0

    with open(filepath, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row_num, row in enumerate(reader, start=2):  # header is row 1
            try:
                entity = converter(row)
                key = getattr(entity, id_field)
                entities[key] = entity
            except Exception as exc:
                errors += 1
                if errors <= 5:
                    logger.warning(
                        "Row %d in %s: %s — %s",
                        row_num, filepath.name, type(exc).__name__, exc,
                    )

    loaded = len(entities)
    if errors:
        logger.warning(
            "Loaded %d entities from %s (%d rows had errors)",
            loaded, filepath.name, errors,
        )
    else:
        logger.info("Loaded %d entities from %s", loaded, filepath.name)

    return entities


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class DatasetLoader:
    """
    Loads all VeriGem CSV datasets and returns a populated DataStore.

    Usage::

        loader = DatasetLoader("/path/to/backend/datasets/VeriGem_Datasets")
        store = loader.load()
    """

    # Mapping: (filename, converter function, ID field on the dataclass)
    _DATASETS: list[tuple[str, Any, str, str]] = [
        ("employees.csv",           _row_to_employee,           "employee_id",        "employees"),
        ("vendors.csv",             _row_to_vendor,             "vendor_id",           "vendors"),
        ("purchase_orders.csv",     _row_to_purchase_order,     "purchase_order_id",   "purchase_orders"),
        ("invoices.csv",            _row_to_invoice,            "invoice_id",          "invoices"),
        ("transactions.csv",        _row_to_transaction,        "transaction_id",      "transactions"),
        ("audit_logs.csv",          _row_to_audit_log,          "log_id",              "audit_logs"),
        ("compliance_policies.csv", _row_to_compliance_policy,  "policy_id",           "compliance_policies"),
    ]

    def __init__(self, datasets_dir: str | Path) -> None:
        self._dir = Path(datasets_dir)
        if not self._dir.is_dir():
            raise FileNotFoundError(f"Datasets directory not found: {self._dir}")

    def load(self) -> DataStore:
        """Load all datasets and return a fully populated DataStore."""
        store = DataStore()

        for filename, converter, id_field, attr_name in self._DATASETS:
            filepath = self._dir / filename
            if not filepath.exists():
                logger.error("Missing dataset file: %s", filepath)
                continue

            entities = _load_csv(filepath, converter, id_field)
            setattr(store, attr_name, entities)

        logger.info(
            "DataStore ready — %d total entities across %d types",
            store.total_entities(),
            len(store.entity_types()),
        )
        return store
