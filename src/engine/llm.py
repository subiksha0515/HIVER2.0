"""
Configurable LLM Abstraction Layer for AI Support Decision Engine.
Supports OpenAI API integration with environment variable configuration.
Includes GroundedTemplateLLM fallback for offline, zero-hallucination execution.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()


class BaseLLMClient:
    def generate_json(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        raise NotImplementedError


class OpenAIClient(BaseLLMClient):
    """OpenAI API Client wrapper."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature

    def generate_json(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content
            return json.loads(raw_content)
        except Exception as e:
            print(f"[OpenAIClient Warning] API call failed: {e}. Falling back to GroundedTemplateLLM...")
            fallback = GroundedTemplateLLM()
            return fallback.generate_json(prompt, system_prompt)


class GroundedTemplateLLM(BaseLLMClient):
    """
    Deterministic Grounded LLM Fallback.
    Synthesizes grounded support replies strictly from historical retrieved support responses,
    ensuring zero hallucination of policies, prices, refunds, or false promises.
    """

    def generate_json(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        # Extract intent and historical cases from prompt string
        intent_match = re.search(r"Predicted Intent:\s*`?([^`\n]+)`?", prompt)
        intent = intent_match.group(1).strip() if intent_match else "OTHER / UNKNOWN"

        conf_match = re.search(r"Intent Confidence:\s*([0-9\.]+)", prompt)
        confidence = float(conf_match.group(1)) if conf_match else 0.5

        # Extract top retrieved response if present
        resp_match = re.search(r"Historical Response:\s*\"?([^\n\"]+)\"?", prompt)
        top_historical_resp = resp_match.group(1).strip() if resp_match else ""

        # Extract customer handle or greeting
        cust_msg_match = re.search(r"Customer Message:\s*\"?([^\n\"]+)\"?", prompt)
        cust_msg = cust_msg_match.group(1) if cust_msg_match else ""

        handle_match = re.search(r"(@\d+|@[A-Za-z0-9_]+)", cust_msg)
        handle = handle_match.group(1) if handle_match else ""

        # Clean historical response of original twitter handles and links
        cleaned_resp = top_historical_resp
        if cleaned_resp:
            cleaned_resp = re.sub(r"^\s*@\d+\s*", "", cleaned_resp)
            cleaned_resp = re.sub(r"^\s*@[A-Za-z0-9_]+\s*", "", cleaned_resp)
            cleaned_resp = re.sub(r"https?://\S+", "", cleaned_resp).strip()

        # Construct grounded draft reply
        if cleaned_resp and len(cleaned_resp) > 10:
            if handle and not cleaned_resp.startswith(handle):
                draft_reply = f"{handle} {cleaned_resp}"
            else:
                draft_reply = cleaned_resp
        else:
            draft_reply = f"{handle} I'm sorry for any trouble! We'd like to look into this for you. Please connect with our support team so we can assist. ^CS".strip()

        evidence = [top_historical_resp] if top_historical_resp else []

        return {
            "draft_reply": draft_reply,
            "intent": intent,
            "confidence": confidence,
            "evidence": evidence,
            "escalate": False,
            "escalation_reason": ""
        }


def get_llm_client() -> BaseLLMClient:
    """Factory function returning configured LLM client."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    api_key = os.getenv("OPENAI_API_KEY", "")
    model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")

    if provider == "openai" and api_key and not api_key.startswith("your_"):
        print(f"Initializing OpenAI LLM Client ({model_name})...")
        return OpenAIClient(api_key=api_key, model_name=model_name)
    else:
        print("Using GroundedTemplateLLM (Deterministic offline grounded synthesis)...")
        return GroundedTemplateLLM()
