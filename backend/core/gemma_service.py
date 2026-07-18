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


def load_env(file_path: Optional[str] = None) -> None:
    """
    Manually parse and load a .env file into os.environ if it exists.
    Also tries importing dotenv and using it if available.
    """
    try:
        from dotenv import load_dotenv
        if file_path:
            load_dotenv(file_path)
        else:
            load_dotenv()
        return
    except ImportError:
        pass

    from pathlib import Path
    
    p = Path(file_path) if file_path else Path(".env")
    if not p.is_file():
        curr = Path.cwd()
        for parent in [curr] + list(curr.parents):
            p_try = parent / ".env"
            if p_try.is_file():
                p = p_try
                break
            p_try_backend = parent / "backend" / ".env"
            if p_try_backend.is_file():
                p = p_try_backend
                break
                
    if p.is_file():
        logger.info("Manually loading environment variables from %s", p)
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v


class GemmaService:
    """
    Connects the Financial Digital Twin to Google Gemma for advanced
    natural language reasoning and reporting over structured financial data.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None) -> None:
        """
        Initialise the Gemma Service.
        If no API key is provided, the service operates in a mock mode for testing.
        """
        load_env()
        self.api_key = api_key or os.environ.get("HF_TOKEN", "")
        self.model_name = model_name or os.environ.get("MODEL_NAME", GEMMA_MODEL_ID)
        self.is_mock = not bool(self.api_key)
        self.client = None
        
        if self.is_mock:
            logger.warning(
                "No HF_TOKEN provided. %s is running in MOCK mode.", 
                self.__class__.__name__
            )
        else:
            try:
                from huggingface_hub import InferenceClient
                self.client = InferenceClient(token=self.api_key)
                logger.info(
                    "Initialised Gemma Service using Hugging Face InferenceClient with model: %s", 
                    self.model_name
                )
            except Exception as e:
                logger.error(
                    "Failed to initialize Hugging Face InferenceClient: %s. "
                    "Falling back to MOCK mode.", e
                )
                self.is_mock = True

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

    def _handle_exception(self, e: Exception) -> str:
        """
        Centrally logs exceptions without exposing prompt/context details
        and returns a user-friendly error categorisation.
        """
        err_msg = str(e)
        if "401" in err_msg or "Unauthorized" in err_msg or "token" in err_msg.lower():
            logger.error("Hugging Face API Error: Invalid API Token / Unauthorized Access.")
            return "Hugging Face API Error: Invalid API Token."
        elif "429" in err_msg or "rate limit" in err_msg.lower() or "too many requests" in err_msg.lower():
            logger.error("Hugging Face API Error: Rate limit exceeded.")
            return "Hugging Face API Error: Rate limit exceeded."
        elif "404" in err_msg or "not found" in err_msg.lower() or "unavailable" in err_msg.lower() or "503" in err_msg:
            logger.error("Hugging Face API Error: Model is unavailable or overloaded.")
            return f"Hugging Face API Error: Model '{self.model_name}' is currently unavailable."
        elif "timeout" in err_msg.lower() or "timed out" in err_msg.lower():
            logger.error("Hugging Face API Error: Connection timed out.")
            return "Hugging Face API Error: Connection timed out."
        elif "connection" in err_msg.lower() or "network" in err_msg.lower() or "dns" in err_msg.lower():
            logger.error("Hugging Face API Error: Network/DNS connectivity issues.")
            return "Hugging Face API Error: Network connectivity issue."
        else:
            logger.error("Hugging Face API Error: Unexpected exception occurred.")
            return f"Hugging Face API Error: {err_msg}"

    def _generate(self, prompt: str, context_data: Dict[str, Any]) -> str:
        """
        Internal wrapper to call the Gemma API (or mock it/fallback).
        """
        # Ensure context data is cleanly formatted for the LLM context window
        context_json = json.dumps(context_data, default=str, indent=2)
        
        full_prompt = (
            f"{self.system_instruction}\n\n"
            f"=== CONTEXT DATA ===\n{context_json}\n\n"
            f"=== USER TASK ===\n{prompt}"
        )

        if self.is_mock or not self.client:
            logger.debug("Generating fallback/mock response for task (mock mode)...")
            return self._generate_fallback(prompt, context_data)

        try:
            logger.info("Calling Hugging Face Inference API for model %s", self.model_name)
            response = self.client.chat_completion(
                model=self.model_name,
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=1024,
                timeout=30.0
            )
            
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    return content
            
            logger.warning("Empty response received from Hugging Face Inference API.")
            return self._generate_fallback(prompt, context_data)
        except Exception as e:
            self._handle_exception(e)
            return self._generate_fallback(prompt, context_data)

    def _generate_fallback(self, prompt: str, context_data: Dict[str, Any]) -> str:
        """
        Graceful fallback response providing structured metrics and rules from the context
        when Gemma is unavailable.
        """
        fallback_msg = (
            "### VeriGem Analysis (AI Fallback Mode)\n\n"
            "**Notice:** The generative AI service is currently unavailable. "
            "Showing deterministic analysis from the VeriGem core engines.\n\n"
        )
        
        # Check for rule results / violations in context
        rule_results = context_data.get("rule_results")
        if rule_results:
            fallback_msg += "#### Rule Violations Detected:\n"
            for rule in rule_results:
                rule_name = rule.get("rule", "Unknown Rule")
                severity = rule.get("severity", "Low")
                evidence = rule.get("evidence", "No evidence details provided")
                if isinstance(evidence, list):
                    evidence_str = "; ".join(evidence)
                else:
                    evidence_str = str(evidence)
                fallback_msg += f"- **[{severity}] {rule_name}**: {evidence_str}\n"
            fallback_msg += "\n"

        # Check for evidence graph nodes/edges
        eg = context_data.get("evidence_graph")
        if eg:
            if isinstance(eg, str):
                try:
                    eg = json.loads(eg)
                except Exception:
                    eg = None
            if isinstance(eg, dict):
                nodes = eg.get("nodes", [])
                edges = eg.get("edges", [])
                fallback_msg += f"#### Evidence Subgraph Summary:\n"
                fallback_msg += f"- Total related entities: {len(nodes)}\n"
                fallback_msg += f"- Total transactional paths: {len(edges)}\n"
                if nodes:
                    labels = []
                    for n in nodes[:5]:
                        label = None
                        if isinstance(n, dict):
                            label = n.get("label") or n.get("id")
                        else:
                            label = str(n)
                        labels.append(label)
                    fallback_msg += f"- Highlighted entities: {', '.join(labels)}"
                    if len(nodes) > 5:
                        fallback_msg += "..."
                    fallback_msg += "\n"
                fallback_msg += "\n"
            
        # Check other context keys (comprehensive PromptBuilder formats)
        entity_str = context_data.get("entity")
        if entity_str:
            try:
                entity = json.loads(entity_str) if isinstance(entity_str, str) else entity_str
                fallback_msg += f"#### Entity Overview:\n"
                fallback_msg += f"- **ID**: {entity.get('id')}\n"
                fallback_msg += f"- **Type**: {entity.get('type')}\n"
                data = entity.get("data", {})
                if data:
                    fallback_msg += "  - **Key Attributes**:\n"
                    for k, v in list(data.items())[:5]:
                        fallback_msg += f"    - {k}: {v}\n"
                fallback_msg += "\n"
            except Exception:
                pass
                
        # Risk summaries
        risk_str = context_data.get("risk")
        if risk_str:
            try:
                risks = json.loads(risk_str) if isinstance(risk_str, str) else risk_str
                fallback_msg += "#### Risk Profiles:\n"
                for r in risks[:5]:
                    fallback_msg += f"- Entity {r.get('id')} ({r.get('type')}): Risk Score {r.get('risk')}\n"
                if len(risks) > 5:
                    fallback_msg += f"- and {len(risks) - 5} more entity profiles.\n"
                fallback_msg += "\n"
            except Exception:
                pass
                
        # Comparison data
        comp = context_data.get("comparison")
        if comp:
            fallback_msg += "#### Simulation Difference Comparison:\n"
            for k, v in comp.items():
                if isinstance(v, list):
                    fallback_msg += f"- **{k}**: {len(v)} entries affected\n"
                elif isinstance(v, dict):
                    fallback_msg += f"- **{k}**: {len(v)} items modified\n"
            fallback_msg += "\n"
            
        fallback_msg += (
            "**Recommendation:** Please verify these findings manually with the Risk and Rule Engines "
            "or check your Hugging Face API token configuration."
        )
        return fallback_msg

    # ------------------------------------------------------------------
    # Required Gemma Service APIs
    # ------------------------------------------------------------------

    def ask_gemma(self, prompt: str) -> str:
        """
        Query Gemma with a simple prompt.
        """
        return self._generate(prompt, {})

    def chat(self, messages: Any) -> str:
        """
        Conduct a multi-turn chat using the list of messages.
        """
        if self.is_mock or not self.client:
            logger.debug("Mocking chat response...")
            last_msg = messages[-1]["content"] if messages else "No message provided."
            return f"[MOCK CHAT RESPONSE] Replay of message: '{last_msg}'"
            
        try:
            logger.info("Calling chat completion on Hugging Face Inference Client")
            formatted_messages = []
            formatted_messages.append({"role": "system", "content": self.system_instruction})
            formatted_messages.extend(messages)
            
            response = self.client.chat_completion(
                model=self.model_name,
                messages=formatted_messages,
                max_tokens=1024,
                timeout=30.0
            )
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    return content
            return "No response generated from the model."
        except Exception as e:
            self._handle_exception(e)
            return (
                "Notice: The chat service is currently experiencing connection issues. "
                "Please verify your credentials or try again later."
            )

    def health_check(self) -> Dict[str, Any]:
        """
        Check connection health to Hugging Face Inference API.
        """
        if self.is_mock or not self.client:
            return {
                "status": "mock",
                "details": "Operating in mock mode (no HF_TOKEN provided)."
            }
        try:
            logger.info("Performing health check connection test...")
            # Use max_tokens=1 to minimize costs/latencies
            self.client.chat_completion(
                model=self.model_name,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
                timeout=5.0
            )
            return {
                "status": "healthy",
                "model": self.model_name,
                "details": "Connection to Hugging Face Inference API succeeded."
            }
        except Exception as e:
            err_msg = str(e)
            logger.error("Health check failed: %s", err_msg)
            reason = "Unknown error"
            if "401" in err_msg or "Unauthorized" in err_msg or "token" in err_msg.lower():
                reason = "Invalid API token"
            elif "timeout" in err_msg.lower():
                reason = "Connection timed out"
            elif "connection" in err_msg.lower() or "network" in err_msg.lower():
                reason = "Network/DNS error"
            elif "404" in err_msg or "not found" in err_msg.lower() or "unavailable" in err_msg.lower():
                reason = "Model unavailable"
            elif "429" in err_msg or "rate limit" in err_msg.lower() or "too many requests" in err_msg.lower():
                reason = "Rate limiting"
                
            return {
                "status": "unhealthy",
                "reason": reason,
                "details": err_msg
            }

    def generate_report(
        self, 
        department_id: Optional[str] = None, 
        summary_stats: Optional[Dict[str, Any]] = None, 
        top_risks: Optional[List[Dict[str, Any]]] = None,
        *args,
        **kwargs
    ) -> str:
        """
        Generate a comprehensive executive report for a department.
        Supports both direct keyword call and positional arguments mapping.
        """
        dept = department_id or kwargs.get("department_id") or "General"
        stats = summary_stats or kwargs.get("summary_stats") or {}
        risks = top_risks or kwargs.get("top_risks") or []
        
        prompt = (
            f"Generate a formal, structured executive report for Department '{dept}'. "
            "Incorporate the summary statistics and the top intrinsic risks identified by the backend engines. "
            "Provide actionable recommendations based purely on the provided data."
        )
        context = {
            "department_id": dept,
            "summary_statistics": stats,
            "top_risks": risks
        }
        return self._generate(prompt, context)

    # ------------------------------------------------------------------
    # Existing compatibility methods for the Twin core
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
        
        # Optimize graph data if it is a dictionary (React Flow JSON)
        try:
            from .prompt_builder import PromptBuilder
            compressed_graph = PromptBuilder.build_evidence_graph_context(evidence_graph)
            graph_data = json.loads(compressed_graph)
        except Exception as e:
            logger.warning("Could not compress evidence graph via PromptBuilder: %s", e)
            graph_data = evidence_graph

        context = {
            "evidence_graph": graph_data,
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
