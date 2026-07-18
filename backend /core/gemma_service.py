"""
Gemma Service Module for the VeriGem Financial Digital Twin.

Integration layer for Google Gemma via Hugging Face (google/gemma-3-27b-it).

CRITICAL ARCHITECTURAL BOUNDARY:
Gemma is explicitly forbidden from calculating risk scores or evaluating 
compliance rules. Those tasks belong purely to the deterministic Python engines.

Gemma's authorized capabilities are strictly limited to:
- Investigates
- Explains
- Summarizes
- Predicts
- Compares simulations
- Generates reports
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

GEMMA_MODEL_ID = "google/gemma-3-27b-it"


class GemmaService:
    """
    Connects the Financial Digital Twin to Google Gemma for advanced
    natural language reasoning and reporting over structured financial data.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialise the Gemma Service.
        If no API key is provided, the service operates in a mock mode for testing.
        """
        self.api_key = api_key or os.environ.get("HF_TOKEN", "")
        self.is_mock = not bool(self.api_key)
        
        if self.is_mock:
            logger.warning(
                "No HF_TOKEN provided. %s is running in MOCK mode.", 
                self.__class__.__name__
            )
        else:
            logger.info(
                "Initialised Gemma Service using model: %s", GEMMA_MODEL_ID
            )

    @property
    def system_instruction(self) -> str:
        """
        The absolute system prompt boundary that enforces the separation of concerns.
        """
        return (
            "You are VeriGem, a specialized financial analysis AI powered by Google Gemma. "
            "You sit on top of a deterministic Financial Digital Twin ecosystem.\n\n"
            "CRITICAL SYSTEM CONSTRAINTS:\n"
            "1. You MUST NEVER calculate or assign risk scores. The backend Risk Engine is the sole source of truth for risk.\n"
            "2. You MUST NEVER evaluate compliance or determine if a rule was broken. The backend Rule Engine handles all logic.\n\n"
            "YOUR AUTHORIZED CAPABILITIES:\n"
            "- INVESTIGATE anomalies provided in your context.\n"
            "- EXPLAIN complex financial states or compliance violations in human terms.\n"
            "- SUMMARIZE large datasets, profiles, and timelines.\n"
            "- PREDICT future trends (like cash flow bottlenecks) based ONLY on historical context.\n"
            "- COMPARE what-if simulation states (e.g., 'If we block this vendor, what happens to department spend?').\n"
            "- GENERATE comprehensive executive reports."
        )

    def _generate(self, prompt: str, context_data: Dict[str, Any]) -> str:
        """
        Internal wrapper to call the Gemma API (or mock it).
        """
        # Ensure context data is cleanly formatted for the LLM context window
        context_json = json.dumps(context_data, default=str, indent=2)
        
        full_prompt = (
            f"{self.system_instruction}\n\n"
            f"=== CONTEXT DATA ===\n{context_json}\n\n"
            f"=== USER TASK ===\n{prompt}"
        )

        if self.is_mock:
            logger.debug("Mocking Gemma call for task: %s...", prompt[:50])
            return (
                f"[MOCK GEMMA RESPONSE via {GEMMA_MODEL_ID}]\n\n"
                f"Successfully processed the context data (length: {len(context_json)} chars) "
                f"for the task:\n> {prompt}"
            )

        # In a production environment, this utilizes the huggingface_hub SDK
        try:
            from huggingface_hub import InferenceClient
        except ImportError:
            logger.error("huggingface_hub is not installed. Run: pip install huggingface_hub")
            return "Error: huggingface_hub missing."

        client = InferenceClient(token=self.api_key)
        
        try:
            logger.info("Calling Hugging Face Inference API for model %s", GEMMA_MODEL_ID)
            response = client.chat_completion(
                model=GEMMA_MODEL_ID,
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("Hugging Face API call failed: %s", e)
            return f"Error connecting to Hugging Face API: {e}"

    # ------------------------------------------------------------------
    # Authorized Capabilities
    # ------------------------------------------------------------------

    def investigate(
        self, 
        anomaly_description: str, 
        evidence_graph: Dict[str, Any], 
        rule_results: List[Dict[str, Any]]
    ) -> str:
        """
        Investigate a specific anomaly or entity using graph evidence and rule violations.
        """
        prompt = (
            f"Investigate the following anomaly: '{anomaly_description}'. "
            "Trace the path through the evidence graph and explain how the entities interacted "
            "to trigger the provided rule violations. Highlight the root cause."
        )
        context = {
            "evidence_graph": evidence_graph,
            "rule_results": rule_results
        }
        return self._generate(prompt, context)

    def explain(
        self, 
        complex_state: Dict[str, Any], 
        target_audience: str = "Executive"
    ) -> str:
        """
        Translate a complex digital twin state or data structure into plain language.
        """
        prompt = (
            f"Explain the provided financial state context in clear, non-technical terms "
            f"suitable for a {target_audience} audience. Break down the key implications."
        )
        return self._generate(prompt, {"state": complex_state})

    def summarize(
        self, 
        timeline_entries: List[Dict[str, Any]], 
        entity_profile: Dict[str, Any]
    ) -> str:
        """
        Summarize the chronological history and current status of an entity.
        """
        prompt = (
            "Summarize the historical timeline and current profile of this entity. "
            "Identify the most significant events and provide a concise overview of their current standing."
        )
        context = {
            "entity_profile": entity_profile,
            "timeline": timeline_entries
        }
        return self._generate(prompt, context)

    def predict(
        self, 
        historical_spend: Dict[str, Any], 
        current_pending_invoices: List[Dict[str, Any]]
    ) -> str:
        """
        Predict future bottlenecks or cash flow issues based on historical trends.
        """
        prompt = (
            "Based on the historical spend patterns and the current pending invoices in the context, "
            "predict potential cash flow bottlenecks or operational delays over the next 30-90 days. "
            "Do not calculate specific risk scores, just identify trend-based vulnerabilities."
        )
        context = {
            "historical_spend": historical_spend,
            "pending_invoices": current_pending_invoices
        }
        return self._generate(prompt, context)

    def compare_simulations(
        self, 
        comparison_data: Dict[str, Any], 
        scenario_description: str
    ) -> str:
        """
        Analyze the delta between two timeline states (e.g., Current vs. Simulated).
        """
        prompt = (
            f"Analyze the differences between the two simulation states based on this scenario: '{scenario_description}'. "
            "Using the provided state comparison data (additions, removals, modifications), explain the cascading impact "
            "of the what-if scenario across the financial ecosystem."
        )
        return self._generate(prompt, {"comparison": comparison_data})

    def generate_report(
        self, 
        department_id: str, 
        summary_stats: Dict[str, Any], 
        top_risks: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a comprehensive executive report for a department.
        """
        prompt = (
            f"Generate a formal, structured executive report for Department '{department_id}'. "
            "Incorporate the summary statistics and the top intrinsic risks identified by the backend engines. "
            "Provide actionable recommendations based purely on the provided data."
        )
        context = {
            "department_id": department_id,
            "summary_statistics": summary_stats,
            "top_risks": top_risks
        }
        return self._generate(prompt, context)
