"""
FastAPI Router: Chat

Handles natural-language queries about the Digital Twin.

Users can ask about any entity or topic. The router:
  1. Detects the context type from the request (vendor / employee / po /
     invoice / transaction / compliance / investigation / global)
  2. Resolves entity-specific data from the Digital Twin store
  3. Uses PromptBuilder to build a context-enriched system prompt
  4. Delegates to GemmaService and returns only the Gemma response

No mock responses. Real Gemma output (or graceful fallback if unavailable).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.dependencies import get_gemma_service, get_twin
from core.digital_twin import FinancialDigitalTwin
from core.gemma_service import GemmaService
from core.prompt_builder import PromptBuilder

logger = logging.getLogger("verigem.routers.chat")

router = APIRouter(prefix="/api/chat", tags=["Chat"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

VALID_CONTEXT_TYPES = {
    "global",
    "vendor",
    "employee",
    "purchase_order",
    "po",
    "invoice",
    "transaction",
    "compliance",
    "investigation",
}


class ChatMessage(BaseModel):
    """
    A natural-language chat message directed at the Financial Digital Twin.

    - `query`        : The user's question (plain English).
    - `context_type` : Domain area to anchor the response.
                       One of: vendor, employee, purchase_order (po), invoice,
                       transaction, compliance, investigation, global.
    - `target_id`    : (Optional) Specific entity ID to focus on
                       (e.g. "VEN-001", "EMP-042", "TXN-1234").
    - `history`      : (Optional) Previous conversation turns for multi-turn chat.
    """
    query: str = Field(..., min_length=1, max_length=2000)
    context_type: str = Field(default="global")
    target_id: Optional[str] = Field(default=None)
    history: Optional[List[Dict[str, str]]] = Field(default=None)


class ChatResponse(BaseModel):
    status: str
    response: str
    context_type: str
    target_id: Optional[str]


# ---------------------------------------------------------------------------
# Context builders per topic type
# ---------------------------------------------------------------------------

def _build_vendor_context(
    twin: FinancialDigitalTwin,
    target_id: str,
    query: str,
) -> str:
    """Build a structured prompt for a vendor-focused query."""
    vendor = twin.store.vendors.get(target_id)
    if not vendor:
        return (
            f"The user is asking about vendor '{target_id}', "
            f"but no vendor with that ID exists in the Digital Twin.\n"
            f"User query: {query}"
        )
    vendor_section = PromptBuilder.build_vendor_prompt(vendor)

    pos = [po for po in twin.store.purchase_orders.values() if po.vendor_id == target_id][:3]
    invoices = [inv for inv in twin.store.invoices.values() if inv.vendor_id == target_id][:3]
    transactions = [txn for txn in twin.store.transactions.values() if txn.vendor_id == target_id][:3]

    sections = [
        "You are VeriGem, a financial forensics AI analyzing Digital Twin data.",
        "Answer the user's question using the entity data provided below.",
        "",
        vendor_section,
    ]
    for po in pos:
        sections.append(PromptBuilder.build_purchase_order_prompt(po))
    for inv in invoices:
        sections.append(PromptBuilder.build_invoice_prompt(inv))
    for txn in transactions:
        sections.append(PromptBuilder.build_transaction_prompt(txn))
    sections += ["", f"**User Question:** {query}"]
    return "\n\n".join(sections)


def _build_employee_context(
    twin: FinancialDigitalTwin,
    target_id: str,
    query: str,
) -> str:
    """Build a structured prompt for an employee-focused query."""
    emp = twin.store.employees.get(target_id)
    if not emp:
        return (
            f"The user is asking about employee '{target_id}', "
            f"but no employee with that ID exists in the Digital Twin.\n"
            f"User query: {query}"
        )
    emp_section = PromptBuilder.build_employee_prompt(emp)

    approved_pos = [
        po for po in twin.store.purchase_orders.values()
        if po.approved_by_employee_id == target_id
    ][:3]
    approved_txns = [
        txn for txn in twin.store.transactions.values()
        if txn.approver_employee_id == target_id
    ][:3]

    sections = [
        "You are VeriGem, a financial forensics AI analyzing Digital Twin data.",
        "Answer the user's question using the entity data provided below.",
        "",
        emp_section,
    ]
    for po in approved_pos:
        sections.append(PromptBuilder.build_purchase_order_prompt(po))
    for txn in approved_txns:
        sections.append(PromptBuilder.build_transaction_prompt(txn))
    sections += ["", f"**User Question:** {query}"]
    return "\n\n".join(sections)


def _build_purchase_order_context(
    twin: FinancialDigitalTwin,
    target_id: str,
    query: str,
) -> str:
    """Build a structured prompt for a Purchase Order query."""
    po = twin.store.purchase_orders.get(target_id)
    if not po:
        return (
            f"The user is asking about PO '{target_id}', "
            f"but no purchase order with that ID exists.\n"
            f"User query: {query}"
        )
    vendor = twin.store.vendors.get(po.vendor_id)
    invoices = [inv for inv in twin.store.invoices.values() if inv.purchase_order_id == target_id][:3]
    transactions = [txn for txn in twin.store.transactions.values() if txn.purchase_order_id == target_id][:3]

    sections = [
        "You are VeriGem, a financial forensics AI analyzing Digital Twin data.",
        "Answer the user's question using the entity data provided below.",
        "",
        PromptBuilder.build_purchase_order_prompt(po),
    ]
    if vendor:
        sections.append(PromptBuilder.build_vendor_prompt(vendor))
    for inv in invoices:
        sections.append(PromptBuilder.build_invoice_prompt(inv))
    for txn in transactions:
        sections.append(PromptBuilder.build_transaction_prompt(txn))
    sections += ["", f"**User Question:** {query}"]
    return "\n\n".join(sections)


def _build_invoice_context(
    twin: FinancialDigitalTwin,
    target_id: str,
    query: str,
) -> str:
    """Build a structured prompt for an Invoice query."""
    inv = twin.store.invoices.get(target_id)
    if not inv:
        return (
            f"The user is asking about invoice '{target_id}', "
            f"but no invoice with that ID exists.\n"
            f"User query: {query}"
        )
    vendor = twin.store.vendors.get(inv.vendor_id)
    po = twin.store.purchase_orders.get(inv.purchase_order_id)
    transactions = [txn for txn in twin.store.transactions.values() if txn.invoice_id == target_id][:3]

    sections = [
        "You are VeriGem, a financial forensics AI analyzing Digital Twin data.",
        "Answer the user's question using the entity data provided below.",
        "",
        PromptBuilder.build_invoice_prompt(inv),
    ]
    if vendor:
        sections.append(PromptBuilder.build_vendor_prompt(vendor))
    if po:
        sections.append(PromptBuilder.build_purchase_order_prompt(po))
    for txn in transactions:
        sections.append(PromptBuilder.build_transaction_prompt(txn))
    sections += ["", f"**User Question:** {query}"]
    return "\n\n".join(sections)


def _build_transaction_context(
    twin: FinancialDigitalTwin,
    target_id: str,
    query: str,
) -> str:
    """Build a structured prompt for a Transaction query."""
    txn = twin.store.transactions.get(target_id)
    if not txn:
        return (
            f"The user is asking about transaction '{target_id}', "
            f"but no transaction with that ID exists.\n"
            f"User query: {query}"
        )
    vendor = twin.store.vendors.get(txn.vendor_id)
    po = twin.store.purchase_orders.get(txn.purchase_order_id)
    inv = twin.store.invoices.get(txn.invoice_id)

    sections = [
        "You are VeriGem, a financial forensics AI analyzing Digital Twin data.",
        "Answer the user's question using the entity data provided below.",
        "",
        PromptBuilder.build_transaction_prompt(txn),
    ]
    if vendor:
        sections.append(PromptBuilder.build_vendor_prompt(vendor))
    if po:
        sections.append(PromptBuilder.build_purchase_order_prompt(po))
    if inv:
        sections.append(PromptBuilder.build_invoice_prompt(inv))
    sections += ["", f"**User Question:** {query}"]
    return "\n\n".join(sections)


def _build_compliance_context(twin: FinancialDigitalTwin, query: str) -> str:
    """Build a structured prompt for a compliance-focused query."""
    active_policies = [
        p for p in twin.store.compliance_policies.values()
        if p.status == "Active"
    ][:10]

    policy_lines = "\n".join(
        f"- [{p.severity}] {p.policy_name}: {p.description}"
        for p in active_policies
    )

    return (
        "You are VeriGem, a financial forensics AI specializing in compliance analysis.\n"
        "Answer the user's question using the compliance policy data below.\n\n"
        f"## Active Compliance Policies ({len(active_policies)} shown)\n"
        f"{policy_lines}\n\n"
        f"**User Question:** {query}"
    )


def _build_global_context(twin: FinancialDigitalTwin, query: str) -> str:
    """Build a general overview prompt for unrestricted queries."""
    try:
        spend = twin.get_spend_summary()
        spend_line = (
            f"Total PO Value: ₹{spend.get('total_po_value_inr', 'N/A'):,} | "
            f"Total Invoiced: ₹{spend.get('total_invoiced_inr', 'N/A'):,} | "
            f"Total Paid: ₹{spend.get('total_transaction_spend_inr', 'N/A'):,}"
        )
    except Exception:
        spend_line = "Financial summary unavailable."

    return (
        "You are VeriGem, a financial forensics AI for a Financial Digital Twin system.\n"
        "You have full awareness of the organization's vendors, employees, "
        "purchase orders, invoices, transactions, and compliance policies.\n\n"
        f"## Organization Overview\n"
        f"- Vendors      : {len(twin.store.vendors)}\n"
        f"- Employees    : {len(twin.store.employees)}\n"
        f"- Purchase Orders: {len(twin.store.purchase_orders)}\n"
        f"- Invoices     : {len(twin.store.invoices)}\n"
        f"- Transactions : {len(twin.store.transactions)}\n"
        f"- {spend_line}\n\n"
        f"**User Question:** {query}"
    )


# ---------------------------------------------------------------------------
# Main chat endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/",
    summary="Ask VeriGem a question about the Financial Digital Twin",
    response_model=ChatResponse,
)
async def chat_with_twin(
    message: ChatMessage,
    twin: FinancialDigitalTwin = Depends(get_twin),
    gemma: GemmaService = Depends(get_gemma_service),
) -> ChatResponse:
    """
    Send a natural-language query. The router detects the context type,
    resolves entity data from the Digital Twin, builds a PromptBuilder-generated
    context block, and returns Gemma's response.

    **Supported context_type values:**
    - `global`           — general organisation-level question
    - `vendor`           — question about a specific vendor (needs `target_id`)
    - `employee`         — question about a specific employee (needs `target_id`)
    - `purchase_order` / `po` — question about a PO (needs `target_id`)
    - `invoice`          — question about an invoice (needs `target_id`)
    - `transaction`      — question about a transaction (needs `target_id`)
    - `compliance`       — question about rules, policies, or violations
    - `investigation`    — free-form investigation question (global context)
    """
    ctx = message.context_type.lower().strip()

    if ctx not in VALID_CONTEXT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Invalid context_type '{ctx}'. "
                f"Must be one of: {sorted(VALID_CONTEXT_TYPES)}"
            ),
        )

    entity_types_needing_id = {"vendor", "employee", "purchase_order", "po", "invoice", "transaction"}
    if ctx in entity_types_needing_id and not message.target_id:
        raise HTTPException(
            status_code=422,
            detail=f"context_type='{ctx}' requires a 'target_id' (entity ID)."
        )

    # ── Build context-enriched prompt ─────────────────────────────────────
    try:
        if ctx == "vendor":
            prompt = _build_vendor_context(twin, message.target_id, message.query)
        elif ctx == "employee":
            prompt = _build_employee_context(twin, message.target_id, message.query)
        elif ctx in ("purchase_order", "po"):
            prompt = _build_purchase_order_context(twin, message.target_id, message.query)
        elif ctx == "invoice":
            prompt = _build_invoice_context(twin, message.target_id, message.query)
        elif ctx == "transaction":
            prompt = _build_transaction_context(twin, message.target_id, message.query)
        elif ctx == "compliance":
            prompt = _build_compliance_context(twin, message.query)
        else:
            # global / investigation
            prompt = _build_global_context(twin, message.query)

    except Exception as exc:
        logger.error("Context build failed for ctx=%s: %s", ctx, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Context build error: {str(exc)}")

    # ── Delegate to GemmaService ───────────────────────────────────────────
    logger.info("Chat request — ctx=%s target=%s", ctx, message.target_id)

    if message.history:
        # Multi-turn: use chat() with full message history
        messages = list(message.history)
        messages.append({"role": "user", "content": prompt})
        response_text = gemma.chat(messages)
    else:
        # Single-turn: use ask_gemma()
        response_text = gemma.ask_gemma(prompt)

    return ChatResponse(
        status="success",
        response=response_text,
        context_type=ctx,
        target_id=message.target_id,
    )


# ---------------------------------------------------------------------------
# Health check — tests Gemma connectivity without loading Twin data
# ---------------------------------------------------------------------------

@router.get(
    "/health",
    summary="Check GemmaService connectivity",
)
async def chat_health(
    gemma: GemmaService = Depends(get_gemma_service),
) -> Dict[str, Any]:
    """
    Run GemmaService.health_check() and return its result.
    Useful for verifying HF_TOKEN and model availability.
    """
    result = gemma.health_check()
    return {"status": "success", **result}
