# VeriGem Backend Core
"""
Core engine for the VeriGem Financial Digital Twin.

Modules:
    models          - Domain dataclasses (Employee, Vendor, PurchaseOrder, etc.)
    loader          - CSV dataset loader and DataStore builder
    relationships   - NetworkX relationship graph builder
    digital_twin    - Central FinancialDigitalTwin orchestrator
    event_engine    - Immutable event sourcing, history, replay, timelines, snapshots
    rule_engine     - Business logic and compliance rule evaluation
    risk_engine     - Hierarchical risk propagation engine
    simulation_engine- What-If scenario testing with immutable branched states
    timeline_manager- State management and deep comparison of twin timelines
    evidence_graph  - Subgraph extraction and React Flow JSON exporter
    gemma_service   - LLM integration layer for investigation and reporting
    runner          - Boot script to load, build, verify, and demonstrate
"""
