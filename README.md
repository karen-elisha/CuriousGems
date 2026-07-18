# CuriousGems: VeriGem Financial Digital Twin

This is the final submission for Build with Gemma 2026.

VeriGem is a production-grade, in-memory **Financial Digital Twin** built purely in Python. It models a complete organizational ecosystem (Vendors, Purchase Orders, Invoices, Transactions, Employees, Departments) as a topological graph, allowing for deep anomaly detection, risk propagation, and what-if simulation branching. 

The core deterministic engines are augmented by **Google Gemma (google/gemma-3-27b-it)** via Hugging Face to provide natural language investigation, explanation, and reporting, maintaining strict architectural separation from mathematical rule evaluations.

## 🏗️ Architecture & Core Engines

The backend is completely database-free, operating entirely in-memory using highly optimized Python dataclasses and `NetworkX` graphs.

1. **Digital Twin Core (`models.py`, `digital_twin.py`)**: Immutable, frozen dataclasses representing the financial domain.
2. **Graph Engine (`relationships.py`)**: Translates tabular data into a directed graph, modeling hierarchical and transactional relationships (e.g., `Employee -> belongs_to -> Department`, `Invoice -> pays -> PO`).
3. **Event Engine (`event_engine.py`)**: An append-only ledger for all system mutations. Supports time-travel, exact state replay, and timeline generation.
4. **Rule Engine (`rule_engine.py`)**: Evaluates 9 deterministic compliance protocols (e.g., Segregation of Duties violations, missing POs, weekend approvals, duplicate invoices).
5. **Risk Engine (`risk_engine.py`)**: A hierarchical propagation engine that cascades intrinsic risk upwards from Vendors through Transactions and Employees, all the way to the Organization root.
6. **Simulation Engine (`simulation_engine.py`)**: Facilitates "What-If" branching. Safely deep-copies the Twin state for hypothetical testing (e.g., blocking a vendor) with full rollback support.
7. **Timeline Manager (`timeline_manager.py`)**: Performs deep structural diffing between live states, historical snapshots, and simulated branches.
8. **Evidence Graph (`evidence_graph.py`)**: Extracts highly targeted ego-graphs centered on anomalies and formats them natively into React Flow JSON for frontend rendering.
9. **Gemma AI Service (`prompt_builder.py`, `gemma_service.py`, `investigation_service.py`)**: Extracts heavily token-optimized graph/rule/timeline contexts and feeds them to `google/gemma-3-27b-it`. Gemma acts purely as an investigative agent, translating mathematical violations into actionable human intelligence.

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- A Hugging Face account with access to `google/gemma-3-27b-it`

### 1. Environment Setup

```bash
# Navigate to the backend directory
cd backend 

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn networkx huggingface_hub pydantic
# Or use: pip install -r requirements.txt (if available)
```

### 2. API Keys

You must provide a Hugging Face token to utilize the Gemma AI layer. If no token is provided, the service will run in a graceful "Mock Mode".

```bash
export HF_TOKEN="your_hugging_face_token_here"
```

### 3. Running the API

The backend is exposed via a modular FastAPI application.

```bash
# Run from the /backend directory
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`. You can view the interactive Swagger API documentation at `http://localhost:8000/docs`.

## 📡 API Routes

The API is fully modularized under `backend/api/routers/`:

- **`/api/dashboard`**: High-level overview metrics and global timelines.
- **`/api/investigation`**: Deep-dive AI-driven entity analyses orchestrating the Rule, Risk, and Gemma engines.
- **`/api/simulation`**: What-If scenario branching, action execution, rollback, and state comparison.
- **`/api/graph`**: Extracting React Flow JSON evidence subgraphs.
- **`/api/chat`**: Interactive natural language Q&A traversing the Twin state.
- **`/api/reports`**: Generating synthesized executive and compliance reports via Gemma.
