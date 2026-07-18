"""
Evidence Graph Module for the VeriGem Financial Digital Twin.

Extracts subgraphs from the central NetworkX relationship graph based
on affected entities (e.g., from compliance violations) and exports 
them into a JSON format compatible with React Flow for frontend visualization.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import networkx as nx

from .digital_twin import FinancialDigitalTwin

logger = logging.getLogger(__name__)


class EvidenceGraph:
    """
    Generates visual evidence graphs for anomalies and violations.
    
    Extracts a subgraph centered around specific affected entities and 
    formats it as React Flow compatible JSON for direct rendering in the UI.
    """
    
    def __init__(self, twin: FinancialDigitalTwin) -> None:
        self.twin = twin

    def generate_react_flow(self, entity_ids: List[str], depth: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate React Flow JSON nodes and edges for the given entities and their neighbors.
        
        Args:
            entity_ids: The list of focal entity IDs (e.g., from RuleResult.affected_entities).
            depth: How many degrees of separation to include in the visual evidence.
            
        Returns:
            A dictionary containing 'nodes' and 'edges' arrays structured for React Flow.
        """
        if not entity_ids:
            return {"nodes": [], "edges": []}
            
        # 1. Build the subgraph containing the focal nodes and their neighbors
        subgraph = nx.DiGraph()
        
        for entity_id in entity_ids:
            if not self.twin.graph.has_node(entity_id):
                logger.warning("Entity '%s' not found in graph. Skipping.", entity_id)
                continue
                
            # Extract ego graph for this node up to 'depth' radius (undirected traversal)
            ego = nx.ego_graph(self.twin.graph, entity_id, radius=depth, undirected=True)
            subgraph = nx.compose(subgraph, ego)
            
        # 2. Format Nodes for React Flow
        nodes: List[Dict[str, Any]] = []
        for node_id, data in subgraph.nodes(data=True):
            node_type = data.get("node_type", "unknown")
            name = data.get("name", node_id)
            is_focal = node_id in entity_ids
            
            nodes.append({
                "id": str(node_id),
                # If you have custom node types mapped in React Flow, this binds to them
                "type": node_type,
                # Default position to 0,0 - React Flow UI should run a layout engine (like dagre/elk)
                "position": {"x": 0, "y": 0}, 
                "data": {
                    "label": name,
                    "node_type": node_type,
                    "is_focal": is_focal,
                    # We can pass raw node data if the UI needs it for tooltips
                    "raw_data": data,
                },
                # Optionally style the focal nodes directly
                "style": {
                    "border": "2px solid red" if is_focal else "1px solid #ccc"
                }
            })
            
        # 3. Format Edges for React Flow
        edges: List[Dict[str, Any]] = []
        for u, v, data in subgraph.edges(data=True):
            rel_type = data.get("relationship_type", "CONNECTED_TO")
            # Generate a stable edge ID
            edge_id = f"e_{u}_{v}_{rel_type}"
            
            # Animate the edge if it directly connects to a focal entity
            is_focal_edge = (u in entity_ids) or (v in entity_ids)
            
            edges.append({
                "id": edge_id,
                "source": str(u),
                "target": str(v),
                "label": rel_type,
                "type": "smoothstep", # standard React Flow edge type
                "animated": is_focal_edge,
                "style": {
                    "stroke": "#f00" if is_focal_edge else "#888",
                    "strokeWidth": 2 if is_focal_edge else 1
                }
            })
            
        logger.info(
            "Generated Evidence Graph: %d nodes, %d edges (centered on %d entities).",
            len(nodes), len(edges), len(entity_ids)
        )
            
        return {
            "nodes": nodes,
            "edges": edges
        }

    def generate_full_graph_react_flow(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Utility to export the entire Digital Twin graph as React Flow JSON.
        WARNING: This can be extremely large for rendering in the browser.
        """
        # Pass all nodes as focal nodes, but depth=0 to avoid redundant processing
        return self.generate_react_flow(list(self.twin.graph.nodes()), depth=0)
