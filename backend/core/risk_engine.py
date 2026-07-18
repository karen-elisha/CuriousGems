"""
Risk Propagation Engine for the VeriGem Financial Digital Twin.

Propagates intrinsic risks upwards through the organizational hierarchy:
Vendor -> Purchase Order -> Invoice -> Transaction -> Employee -> Department -> Organization

Whenever base risks are applied, the engine automatically recalculates 
propagated risk scores across the entire entity graph.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from .models import DataStore

logger = logging.getLogger(__name__)


@dataclass
class RiskProfile:
    """Holds the intrinsic and propagated risk for a single entity."""
    entity_id: str
    entity_type: str
    base_risk: float = 0.0
    propagated_risk: float = 0.0

    @property
    def total_risk(self) -> float:
        """The total risk is the sum of intrinsic base risk and inherited risk."""
        return self.base_risk + self.propagated_risk


class RiskPropagationEngine:
    """
    Cascades risk scores through the ecosystem.
    
    Usage::
    
        engine = RiskPropagationEngine(store, decay_factor=0.8)
        engine.apply_base_risk("VEN-100234", 85.0)
        # Affected POs, Invoices, Txns, Employees, Departments, and the Org 
        # are automatically recalculated.
    """

    def __init__(self, store: DataStore, decay_factor: float = 0.8) -> None:
        """
        Initialize the Risk Engine.
        
        Args:
            store: The DataStore containing all entities.
            decay_factor: Multiplier applied at each step of propagation to 
                          dampen risk (e.g., 0.8 means 80% carries over).
        """
        self.store = store
        self.decay_factor = decay_factor
        self.profiles: dict[str, RiskProfile] = {}
        
        self._initialize_profiles()

    def _initialize_profiles(self) -> None:
        """Create empty risk profiles for every entity in the datastore."""
        for vendor_id in self.store.vendors:
            self.profiles[vendor_id] = RiskProfile(vendor_id, "vendor")
            
        for po_id in self.store.purchase_orders:
            self.profiles[po_id] = RiskProfile(po_id, "purchase_order")
            
        for inv_id in self.store.invoices:
            self.profiles[inv_id] = RiskProfile(inv_id, "invoice")
            
        for txn_id in self.store.transactions:
            self.profiles[txn_id] = RiskProfile(txn_id, "transaction")
            
        for emp in self.store.employees.values():
            self.profiles[emp.employee_id] = RiskProfile(emp.employee_id, "employee")
            
            # Virtual nodes for Departments
            dept_id = f"DEPT:{emp.department}"
            if dept_id not in self.profiles:
                self.profiles[dept_id] = RiskProfile(dept_id, "department")
                
        # Virtual node for the Organization
        self.profiles["ORG:ROOT"] = RiskProfile("ORG:ROOT", "organization")
        logger.info("RiskPropagationEngine initialised with %d entity profiles.", len(self.profiles))

    def get_profile(self, entity_id: str) -> Optional[RiskProfile]:
        """Retrieve the risk profile for a given entity."""
        return self.profiles.get(entity_id)

    def apply_base_risk(self, entity_id: str, risk_score: float) -> None:
        """
        Apply intrinsic risk to an entity and automatically trigger 
        full propagation to update all downstream affected entities.
        """
        profile = self.profiles.get(entity_id)
        if profile:
            profile.base_risk += risk_score
            logger.debug("Applied base risk +%.2f to %s", risk_score, entity_id)
            self._recalculate_all()
        else:
            logger.warning("Attempted to apply risk to unknown entity: %s", entity_id)

    def reset_base_risks(self) -> None:
        """Clear all intrinsic base risks and recalculate."""
        for profile in self.profiles.values():
            profile.base_risk = 0.0
        self._recalculate_all()

    def _recalculate_all(self) -> None:
        """
        Propagate risk level by level. Because the graph strictly follows
        the defined hierarchy, we can sequentially compute the inherited risk
        without complex recursive graph traversal.
        """
        # 0. Reset all propagated risks
        for profile in self.profiles.values():
            profile.propagated_risk = 0.0

        damp = self.decay_factor

        # 1. Vendor -> Purchase Order
        for po in self.store.purchase_orders.values():
            vendor_profile = self.profiles.get(po.vendor_id)
            po_profile = self.profiles.get(po.purchase_order_id)
            if vendor_profile and po_profile:
                po_profile.propagated_risk += vendor_profile.total_risk * damp

        # 2. Purchase Order -> Invoice
        for inv in self.store.invoices.values():
            po_profile = self.profiles.get(inv.purchase_order_id)
            inv_profile = self.profiles.get(inv.invoice_id)
            if po_profile and inv_profile:
                inv_profile.propagated_risk += po_profile.total_risk * damp

        # 3. Invoice -> Transaction
        for txn in self.store.transactions.values():
            inv_profile = self.profiles.get(txn.invoice_id)
            txn_profile = self.profiles.get(txn.transaction_id)
            if inv_profile and txn_profile:
                txn_profile.propagated_risk += inv_profile.total_risk * damp

        # 4. Transaction -> Employee (Approver)
        for txn in self.store.transactions.values():
            txn_profile = self.profiles.get(txn.transaction_id)
            emp_profile = self.profiles.get(txn.approver_employee_id)
            if txn_profile and emp_profile:
                emp_profile.propagated_risk += txn_profile.total_risk * damp

        # 5. Employee -> Department
        for emp in self.store.employees.values():
            emp_profile = self.profiles.get(emp.employee_id)
            dept_profile = self.profiles.get(f"DEPT:{emp.department}")
            if emp_profile and dept_profile:
                dept_profile.propagated_risk += emp_profile.total_risk * damp

        # 6. Department -> Organization
        org_profile = self.profiles.get("ORG:ROOT")
        if org_profile:
            for profile in self.profiles.values():
                if profile.entity_type == "department":
                    org_profile.propagated_risk += profile.total_risk * damp

    def get_top_risks(self, entity_type: Optional[str] = None, limit: int = 10) -> list[RiskProfile]:
        """Return the highest risk entities, optionally filtered by type."""
        candidates = list(self.profiles.values())
        if entity_type:
            candidates = [p for p in candidates if p.entity_type == entity_type]
            
        candidates.sort(key=lambda p: p.total_risk, reverse=True)
        return candidates[:limit]
