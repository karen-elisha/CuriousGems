"""
Prompt Builder for the VeriGem Financial Digital Twin.

Responsible for extracting, compressing, and structuring data from the ecosystem 
(Digital Twin, Timeline, Evidence Graph, Risk, Audit, Policies) into highly 
token-efficient context blocks for the Gemma LLM.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from .digital_twin import FinancialDigitalTwin
from .event_engine import TimelineEntry
from .risk_engine import RiskProfile

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Constructs token-optimized context blocks for LLM ingestion.
    Strips visual metadata, null fields, and verbose keys to maximize context window.
    """
    
    @staticmethod
    def _optimize_dict(d: dict, drop_keys: Optional[set] = None) -> dict:
        """Removes nulls, empty collections, and strictly backend-only timestamps."""
        drop_keys = drop_keys or {"created_at", "updated_at"}
        return {
            k: v for k, v in d.items() 
            if v is not None and v != "" and v != [] and v != {} and k not in drop_keys
        }

    @staticmethod
    def build_entity_context(twin: FinancialDigitalTwin, entity_id: str) -> str:
        """Extracts and compresses a single entity's state."""
        try:
            profile = twin.get_entity_profile(entity_id)
        except KeyError:
            return json.dumps({"error": f"Entity {entity_id} not found."})
            
        # Optimize entity data recursively if it exists
        entity_data = profile.get("entity_data")
        if entity_data:
            entity_data_dict = asdict(entity_data) if hasattr(entity_data, "__dataclass_fields__") else dict(entity_data)
            profile["entity_data"] = PromptBuilder._optimize_dict(entity_data_dict)
            
        return json.dumps({
            "id": profile.get("entity_id"),
            "type": profile.get("node_type"),
            "data": profile.get("entity_data"),
            "rels": profile.get("relationships")
        }, separators=(',', ':'))

    @staticmethod
    def build_timeline_context(timeline: List[TimelineEntry], limit: int = 15) -> str:
        """Compresses a timeline, keeping only the most recent N events with abbreviated keys."""
        recent = timeline[-limit:] if len(timeline) > limit else timeline
        
        compressed = [
            {
                "seq": t.sequence_number,
                "cat": t.category,
                "actor": t.actor_id,
                "summary": t.summary
            } for t in recent
        ]
            
        return json.dumps(compressed, separators=(',', ':'))

    @staticmethod
    def build_evidence_graph_context(graph_json: Dict[str, Any]) -> str:
        """
        Compresses a React Flow JSON graph. LLMs do not need UI positioning data (x, y),
        CSS styles, or frontend-specific node types.
        """
        compressed_nodes = [
            {"id": str(n.get("id")), "label": n.get("data", {}).get("label", n.get("id"))}
            for n in graph_json.get("nodes", [])
        ]
            
        compressed_edges = [
            {"src": str(e.get("source")), "tgt": str(e.get("target")), "rel": e.get("label")}
            for e in graph_json.get("edges", [])
        ]
            
        return json.dumps({
            "nodes": compressed_nodes,
            "edges": compressed_edges
        }, separators=(',', ':'))

    @staticmethod
    def build_risk_context(risk_profiles: List[RiskProfile]) -> str:
        """Compresses risk profiles into a tight summary."""
        compressed = [
            {
                "id": p.entity_id,
                "type": p.entity_type,
                "risk": round(p.total_risk, 2)
            } for p in risk_profiles if p.total_risk > 0
        ]
        return json.dumps(compressed, separators=(',', ':'))

    @staticmethod
    def build_audit_context(twin: FinancialDigitalTwin, entity_id: str, limit: int = 10) -> str:
        """Extracts and compresses recent audit logs relevant to a specific entity."""
        logs = []
        for log in twin.store.audit_logs.values():
            if log.entity_id == entity_id or log.employee_id == entity_id:
                logs.append(log)
                
        logs.sort(key=lambda x: x.timestamp)
        recent = logs[-limit:] if len(logs) > limit else logs
        
        compressed = [
            {
                "act": log.action,
                "by": log.employee_id,
                "stat": log.status,
                "rem": log.remarks
            } for log in recent
        ]
            
        return json.dumps(compressed, separators=(',', ':'))

    @staticmethod
    def build_policies_context(twin: FinancialDigitalTwin, active_only: bool = True) -> str:
        """Compresses compliance policies down to essential identifiers and rules."""
        compressed = [
            {
                "id": p.policy_id,
                "sev": p.severity,
                "desc": p.description
            } 
            for p in twin.store.compliance_policies.values()
            if not active_only or p.status == "Active"
        ]
        return json.dumps(compressed, separators=(',', ':'))

    @staticmethod
    def build_comprehensive_context(
        twin: FinancialDigitalTwin,
        entity_id: str,
        timeline: Optional[List[TimelineEntry]] = None,
        evidence_graph: Optional[Dict[str, Any]] = None,
        risk_profiles: Optional[List[RiskProfile]] = None
    ) -> Dict[str, str]:
        """
        Assembles all available token-optimized context blocks into a dictionary.
        This dictionary can be passed directly to GemmaService._generate(prompt, context_data).
        """
        context: Dict[str, str] = {
            "entity": PromptBuilder.build_entity_context(twin, entity_id),
            "audit": PromptBuilder.build_audit_context(twin, entity_id),
            "policies": PromptBuilder.build_policies_context(twin),
        }
        
        if timeline:
            context["timeline"] = PromptBuilder.build_timeline_context(timeline)
            
        if evidence_graph:
            context["evidence_graph"] = PromptBuilder.build_evidence_graph_context(evidence_graph)
            
        if risk_profiles:
            context["risk"] = PromptBuilder.build_risk_context(risk_profiles)
            
        return context
