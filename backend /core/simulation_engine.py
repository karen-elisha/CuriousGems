"""
Simulation Engine for the VeriGem Financial Digital Twin.

Provides "What-If" scenario branching by creating new, immutable states 
of the Digital Twin. Never mutates the original state.
Maintains a state history tree to support full rollback capabilities.

Supported operations:
- Approve Payment
- Reject Payment
- Delay Payment
- Freeze Transaction
- Replace Approver
- Modify Invoice
- Block Vendor
- Create Vendor
"""

from __future__ import annotations

import copy
import logging
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
from typing import Optional

from .digital_twin import FinancialDigitalTwin
from .models import Vendor
from .relationships import RelationshipBuilder

logger = logging.getLogger(__name__)


class SimulationState:
    """
    A single discrete state within a simulation timeline.
    Holds a snapshot of the Digital Twin and a reference to its parent state.
    """

    def __init__(
        self,
        twin: FinancialDigitalTwin,
        description: str,
        parent: Optional[SimulationState] = None,
    ) -> None:
        self.twin = twin
        self.description = description
        self.parent = parent


class SimulationEngine:
    """
    Executes what-if scenarios on the Financial Digital Twin.
    
    Usage::
    
        engine = SimulationEngine(base_twin)
        engine.block_vendor("VEN-100234")
        engine.modify_invoice("INV-30001", Decimal("500000.00"))
        
        # Access the simulated twin
        simulated_twin = engine.current_twin
        
        # Undo the last action
        engine.rollback()
    """

    def __init__(self, initial_twin: FinancialDigitalTwin) -> None:
        self._initial_twin = initial_twin
        self._current_state = SimulationState(initial_twin, "Initial State")
        logger.info("SimulationEngine initialised.")

    @property
    def current_twin(self) -> FinancialDigitalTwin:
        """Returns the FinancialDigitalTwin representing the current simulated state."""
        return self._current_state.twin

    def rollback(self) -> bool:
        """
        Revert the simulation to the previous state.
        
        Returns:
            True if rollback was successful, False if already at the initial state.
        """
        if self._current_state.parent is not None:
            prev_desc = self._current_state.parent.description
            logger.info("Rolling back from '%s' to '%s'.", self._current_state.description, prev_desc)
            self._current_state = self._current_state.parent
            return True
        logger.warning("Cannot rollback: already at the initial state.")
        return False

    def reset(self) -> None:
        """Discard all simulations and reset to the initial state."""
        self._current_state = SimulationState(self._initial_twin, "Initial State")
        logger.info("SimulationEngine reset to initial state.")

    def _branch(self, description: str, rebuild_graph: bool = False) -> FinancialDigitalTwin:
        """
        Create a branched copy of the current Twin for mutation.
        Deep-copies the DataStore to guarantee immutability of previous states.
        """
        logger.info("Simulating: %s", description)
        
        # 1. Deepcopy the in-memory data store
        new_store = copy.deepcopy(self.current_twin.store)
        
        # 2. Handle the relationship graph
        if rebuild_graph:
            builder = RelationshipBuilder(new_store)
            new_graph = builder.build()
        else:
            # If nodes/edges haven't conceptually changed, we can just copy the graph
            new_graph = self.current_twin.graph.copy()
            
        # 3. Instantiate the new twin
        new_twin = FinancialDigitalTwin(new_store, new_graph)
        
        # 4. Advance the state pointer
        new_state = SimulationState(new_twin, description, parent=self._current_state)
        self._current_state = new_state
        
        return new_twin

    # ------------------------------------------------------------------
    # Simulation Actions
    # ------------------------------------------------------------------

    def approve_payment(self, transaction_id: str) -> None:
        """Simulate approving a pending transaction."""
        twin = self._branch(f"Approve Payment: {transaction_id}")
        txn = twin.store.transactions.get(transaction_id)
        if txn:
            txn.payment_status = "Completed"
        else:
            logger.warning("Transaction %s not found for approval.", transaction_id)

    def reject_payment(self, transaction_id: str) -> None:
        """Simulate rejecting a transaction."""
        twin = self._branch(f"Reject Payment: {transaction_id}")
        txn = twin.store.transactions.get(transaction_id)
        if txn:
            txn.payment_status = "Failed" # or Rejected/Reversed
        else:
            logger.warning("Transaction %s not found for rejection.", transaction_id)

    def delay_payment(self, transaction_id: str, days: int = 30) -> None:
        """Simulate delaying a payment by shifting its transaction date forward."""
        twin = self._branch(f"Delay Payment: {transaction_id} by {days} days")
        txn = twin.store.transactions.get(transaction_id)
        if txn and txn.transaction_date:
            txn.transaction_date = txn.transaction_date + timedelta(days=days)
        else:
            logger.warning("Transaction %s not found or missing date.", transaction_id)

    def freeze_transaction(self, transaction_id: str) -> None:
        """Simulate freezing a transaction (e.g., due to an active investigation)."""
        twin = self._branch(f"Freeze Transaction: {transaction_id}")
        txn = twin.store.transactions.get(transaction_id)
        if txn:
            txn.payment_status = "Frozen"
        else:
            logger.warning("Transaction %s not found for freezing.", transaction_id)

    def replace_approver(self, transaction_id: str, new_approver_id: str) -> None:
        """
        Simulate swapping the approving employee for a transaction.
        Rebuilds the graph to accurately reflect the new reporting/approval edges.
        """
        # Graph rebuild required because an edge (REL_TXN_APPROVED_BY) will change
        twin = self._branch(f"Replace Approver on {transaction_id} with {new_approver_id}", rebuild_graph=True)
        txn = twin.store.transactions.get(transaction_id)
        if txn:
            txn.approver_employee_id = new_approver_id
        else:
            logger.warning("Transaction %s not found for replacing approver.", transaction_id)

    def modify_invoice(self, invoice_id: str, new_amount: Decimal) -> None:
        """Simulate modifying an invoice's total amount."""
        twin = self._branch(f"Modify Invoice: {invoice_id} to ₹{new_amount:,.2f}")
        inv = twin.store.invoices.get(invoice_id)
        if inv:
            inv.total_amount_inr = new_amount
            # When an invoice amount changes, the match status against the PO usually breaks
            inv.match_status = "Mismatched"
        else:
            logger.warning("Invoice %s not found for modification.", invoice_id)

    def block_vendor(self, vendor_id: str) -> None:
        """Simulate blacklisting a vendor."""
        twin = self._branch(f"Block Vendor: {vendor_id}")
        vendor = twin.store.vendors.get(vendor_id)
        if vendor:
            vendor.vendor_status = "Blacklisted"
        else:
            logger.warning("Vendor %s not found for blocking.", vendor_id)

    def create_vendor(self, vendor: Vendor) -> None:
        """
        Simulate onboarding a brand new vendor.
        Rebuilds the graph to incorporate the new vendor node.
        """
        # Graph rebuild required to add the new vendor node
        twin = self._branch(f"Create Vendor: {vendor.vendor_id}", rebuild_graph=True)
        twin.store.vendors[vendor.vendor_id] = vendor
