"""
llm_client.py — thin client for home_orchestrator.

All LLM traffic goes through :4700 (SYSTEM_PROMPT PART 9).
Billing is tagged with agent="dealligence".
"""

from __future__ import annotations
import os
import httpx

_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:4700")
_KEY = os.getenv("ORCHESTRATOR_API_KEY", "")
_AGENT = "dealligence"


def complete(messages: list[dict],
             task_tier: str = "default",
             max_tokens: int = 4096,
             temperature: float = 0.0,
             timeout: float = 180.0) -> dict:
    """
    Returns the full orchestrator response:
    {text, provider, model, input_tokens, output_tokens, cost_usd, request_id}
    """
    payload = {
        "messages": messages,
        "task_tier": task_tier,
        "agent": _AGENT,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    with httpx.Client(timeout=timeout) as c:
        r = c.post(f"{_URL}/v1/llm/complete",
                   json=payload,
                   headers={"X-API-Key": _KEY})
        r.raise_for_status()
        return r.json()


def billing_summary(period: str = "month") -> dict:
    with httpx.Client(timeout=30.0) as c:
        r = c.get(f"{_URL}/v1/billing/summary", params={"period": period})
        r.raise_for_status()
        return r.json()
