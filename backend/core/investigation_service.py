"""
Investigation Service for the VeriGem Financial Digital Twin.

Central orchestration layer that combines deterministic evaluations 
(Rule Engine, Risk Engine, Timeline, Evidence Graph) with generative AI (Gemma) 
to produce comprehensive investigation reports for any given entity or anomaly.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .digital_twin import FinancialDigitalTwin
from .event_engine import EventEngine
from .evidence_graph import EvidenceGraph
from .gemma_service import GemmaService
from .prompt_builder import PromptBuilder
from .risk_engine import RiskPropagationEngine
from .rule_engine import RuleEngine
from .timeline_manager import TimelineManager

logger = logging.getLogger(__name__)


class InvestigationService:
    """
    Executes deep investigations into specific entities or system anomalies.
    
    Coordinates the collection of:
    - Rule violations from the Rule Engine
    - Risk propagation scores from the Risk Engine
    - Event history from the Event Engine
    - Graph relationships from the Evidence Graph
    
    Passes the compressed payload via PromptBuilder to the Gemma Service 
    to generate a human-readable investigation report.
    """

    def __init__(
        self,
        twin: FinancialDigitalTwin,
        rule_engine: RuleEngine,
        risk_engine: RiskPropagationEngine,
        event_engine: EventEngine,
        timeline_manager: TimelineManager,
        gemma_service: GemmaService,
    ) -> None:
        self.twin = twin
        self.rule_engine = rule_engine
        self.risk_engine = risk_engine
        self.event_engine = event_engine
        self.timeline_manager = timeline_manager
        self.gemma_service = gemma_service
        
        self.evidence_graph_builder = EvidenceGraph(self.twin)
        logger.info("InvestigationService initialised.")

    def investigate_entity(self, entity_id: str) -> Dict[str, Any]:
        """
        Run a full-stack investigation on a specific entity.
        
        Returns:
            A dictionary containing the raw structural data (violations, risk, graph) 
            alongside the natural language `gemma_report`.
        """
        logger.info("Starting investigation for entity: %s", entity_id)

        # 1. Gather Rule Violations
        all_results = self.rule_engine.evaluate_all(self.twin.store)
        entity_violations = [
            res for res in all_results if entity_id in res.affected_entities
        ]

        # 2. Gather Risk Data
        risk_profile = self.risk_engine.get_profile(entity_id)

        # 3. Build Evidence Graph
        # Expand the focal nodes to include the entity and everything implicated in its violations
        focal_nodes = {entity_id}
        for violation in entity_violations:
            focal_nodes.update(violation.affected_entities)
            
        evidence_graph_json = self.evidence_graph_builder.generate_react_flow(
            entity_ids=list(focal_nodes), 
            depth=1
        )

        # 4. Extract Timeline History
        # Find all events in the event engine where this entity was the actor or target
        entity_timeline = []
        for event in self.event_engine.history:
            if event.entity_id == entity_id or event.actor_id == entity_id:
                entity_timeline.append(event)
                
        # 5. Delegate to Gemma for the Report
        # Compress the data for LLM consumption
        rule_payload = [
            {"rule": v.rule_name, "severity": v.severity, "evidence": v.evidence}
            for v in entity_violations
        ]
        
        anomaly_description = (
            f"Entity {entity_id} has a total risk score of "
            f"{risk_profile.total_risk if risk_profile else 'Unknown'} and is associated "
            f"with {len(entity_violations)} compliance violations."
        )
        
        logger.info("Delegating investigation reasoning to GemmaService...")
        gemma_report = self.gemma_service.investigate(
            anomaly_description=anomaly_description,
            evidence_graph=evidence_graph_json,
            rule_results=rule_payload
        )
        
        logger.info("Investigation complete for %s.", entity_id)
        
        return {
            "entity_id": entity_id,
            "violations": [
                {
                    "rule_name": v.rule_name, 
                    "severity": v.severity, 
                    "risk_score": v.risk_score, 
                    "evidence": v.evidence
                } for v in entity_violations
            ],
            "risk": {
                "base_risk": risk_profile.base_risk if risk_profile else 0.0,
                "propagated_risk": risk_profile.propagated_risk if risk_profile else 0.0,
                "total_risk": risk_profile.total_risk if risk_profile else 0.0
            },
            "evidence_graph": evidence_graph_json,
            "gemma_report": gemma_report
        }
