"""
Timeline Manager for the VeriGem Financial Digital Twin.

Manages discrete timelines and states of the ecosystem:
- Current State (Live data)
- Previous States (Historical snapshots from the Event Engine)
- Future Simulated States (Branches from the Simulation Engine)

Provides deep comparison capabilities to calculate exact differences 
(additions, deletions, and field-level mutations) between any two states.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from .digital_twin import FinancialDigitalTwin

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Comparison Data Structures
# ---------------------------------------------------------------------------

@dataclass
class EntityDiff:
    """
    Represents the difference for a single entity between two states.
    
    Status can be "ADDED", "REMOVED", or "MODIFIED".
    For "MODIFIED", changes is a dict mapping field names to {"old": val, "new": val}.
    """
    entity_id: str
    entity_type: str
    status: str
    changes: Dict[str, Dict[str, Any]]


@dataclass
class StateComparison:
    """The complete result of comparing two Digital Twin states."""
    base_state_label: str
    target_state_label: str
    added_entities: int
    removed_entities: int
    modified_entities: int
    diffs: List[EntityDiff]

    @property
    def total_changes(self) -> int:
        return self.added_entities + self.removed_entities + self.modified_entities


# ---------------------------------------------------------------------------
# Timeline Manager
# ---------------------------------------------------------------------------

class TimelineManager:
    """
    Manages multiple versions of the Digital Twin across time.
    
    Usage::
    
        manager = TimelineManager(live_twin)
        
        # Load a historical twin from the Event Engine
        manager.register_previous_state("start_of_fy", past_twin)
        
        # Load a branched twin from the Simulation Engine
        manager.register_future_state("sim_vendor_blocked", branched_twin)
        
        # Compare what changed in the simulation against the live data
        comparison = manager.compare_states("current", "sim_vendor_blocked")
        print(f"Entities modified: {comparison.modified_entities}")
    """
    
    def __init__(self, current_state: FinancialDigitalTwin) -> None:
        self.current_state = current_state
        self.previous_states: Dict[str, FinancialDigitalTwin] = {}
        self.future_states: Dict[str, FinancialDigitalTwin] = {}
        logger.info("TimelineManager initialised with Current State.")

    # ------------------------------------------------------------------
    # State Registration
    # ------------------------------------------------------------------

    def register_previous_state(self, label: str, twin: FinancialDigitalTwin) -> None:
        """Register a historical state (e.g., reconstructed from an event snapshot)."""
        self.previous_states[label] = twin
        logger.info("Registered Previous State: '%s'", label)
        
    def register_future_state(self, label: str, twin: FinancialDigitalTwin) -> None:
        """Register a simulated future state (e.g., from the Simulation Engine)."""
        self.future_states[label] = twin
        logger.info("Registered Future Simulated State: '%s'", label)
        
    def get_state(self, label: str) -> Optional[FinancialDigitalTwin]:
        """Retrieve a registered state by its label. ('current' returns the active state)."""
        if label == "current":
            return self.current_state
        if label in self.previous_states:
            return self.previous_states[label]
        if label in self.future_states:
            return self.future_states[label]
        return None

    def list_states(self) -> Dict[str, List[str]]:
        """Return a summary of all registered state labels."""
        return {
            "current": ["current"],
            "previous": list(self.previous_states.keys()),
            "future": list(self.future_states.keys()),
        }

    # ------------------------------------------------------------------
    # State Comparison
    # ------------------------------------------------------------------

    def compare_states(self, base_label: str, target_label: str) -> StateComparison:
        """
        Perform a deep diff between two registered states.
        
        Args:
            base_label: The label of the state to use as the baseline.
            target_label: The label of the state to compare against the baseline.
            
        Returns:
            A StateComparison object containing all additions, removals, and modifications.
        """
        base_twin = self.get_state(base_label)
        target_twin = self.get_state(target_label)
        
        if not base_twin:
            raise ValueError(f"Base state '{base_label}' not found.")
        if not target_twin:
            raise ValueError(f"Target state '{target_label}' not found.")
            
        logger.info("Comparing state '%s' against base '%s'.", target_label, base_label)
        
        diffs: List[EntityDiff] = []
        added_count = 0
        removed_count = 0
        modified_count = 0
        
        base_store = base_twin.store
        target_store = target_twin.store
        
        # Iterate over all entity collections defined in the DataStore
        for entity_type in base_store.entity_types():
            base_collection = base_store.collection(entity_type)
            target_collection = target_store.collection(entity_type)
            
            # Find REMOVED and MODIFIED entities
            for entity_id, base_entity in base_collection.items():
                if entity_id not in target_collection:
                    diffs.append(EntityDiff(
                        entity_id=entity_id,
                        entity_type=entity_type,
                        status="REMOVED",
                        changes={}
                    ))
                    removed_count += 1
                else:
                    # Check for modifications field by field
                    target_entity = target_collection[entity_id]
                    
                    base_dict = asdict(base_entity)
                    target_dict = asdict(target_entity)
                    
                    changes = {}
                    for key, old_val in base_dict.items():
                        new_val = target_dict.get(key)
                        if old_val != new_val:
                            changes[key] = {"old": old_val, "new": new_val}
                            
                    if changes:
                        diffs.append(EntityDiff(
                            entity_id=entity_id,
                            entity_type=entity_type,
                            status="MODIFIED",
                            changes=changes
                        ))
                        modified_count += 1
                        
            # Find ADDED entities
            for entity_id, target_entity in target_collection.items():
                if entity_id not in base_collection:
                    diffs.append(EntityDiff(
                        entity_id=entity_id,
                        entity_type=entity_type,
                        status="ADDED",
                        changes={}
                    ))
                    added_count += 1
                    
        comparison = StateComparison(
            base_state_label=base_label,
            target_state_label=target_label,
            added_entities=added_count,
            removed_entities=removed_count,
            modified_entities=modified_count,
            diffs=diffs
        )
        
        logger.info(
            "Comparison complete: %d additions, %d removals, %d modifications.",
            added_count, removed_count, modified_count
        )
        return comparison
