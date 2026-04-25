"""
AXON Reasoning Engine
=====================
Bridges AXON runtime with Claude API to produce
confidence-scored, uncertainty-aware AI responses.
"""

import os
import re
import json
import random
import time
from typing import Optional
from axon_core import AxonRuntime, AxonValue, AxonType


# ─────────────────────────────────────────────
# REASONING ENGINE
# ─────────────────────────────────────────────

class AxonReasoningEngine:
    """
    The core product engine.
    Takes a user question → runs full AXON reasoning pipeline.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.runtime = AxonRuntime()
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.session_start = time.time()
        self.query_count = 0

        # Pre-load some truth anchors
        self.runtime.truth("session_valid", True)
        self.runtime.truth("reasoning_mode", "probabilistic")

    def _call_claude(self, prompt: str, system: str = "") -> dict:
        """
        Call Claude API and return structured AXON response.
        Returns dict with answer, confidence, hypotheses, attention_areas.
        """
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)

        full_system = system or """You are AXON — an AI reasoning assistant that thinks in probabilities, 
not certainties. You must respond ONLY with a JSON object (no markdown, no backticks).

For every question you must:
1. Give a primary answer
2. Rate your confidence (0.0-1.0) honestly
3. Generate 3 alternative hypotheses with confidence scores
4. Identify 4 key attention areas (concepts most relevant to the answer)
5. Describe your internal epistemic state (qualia)
6. Note any paradoxes or contradictions in the problem

Respond ONLY with this exact JSON structure:
{
  "primary_answer": "your main answer here",
  "confidence": 0.85,
  "confidence_reasoning": "why you are this confident",
  "hypotheses": [
    {"label": "Primary path", "answer": "...", "confidence": 0.85},
    {"label": "Alternative A", "answer": "...", "confidence": 0.55},
    {"label": "Alternative B", "answer": "...", "confidence": 0.30}
  ],
  "attention_areas": ["concept1", "concept2", "concept3", "concept4"],
  "qualia_state": "Curiosity",
  "qualia_intensity": 0.7,
  "paradox": null,
  "memory_note": "what you would store in long-term memory about this"
}

qualia_state must be one of: Curiosity, Uncertainty, Confidence, Dissonance, Insight
If there is a genuine contradiction in the question, set paradox to a short string describing it."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=full_system,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = message.content[0].text.strip()

        # Strip any accidental markdown fences
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw)

        return json.loads(raw)

    def reason(self, question: str) -> dict:
        """
        Full AXON reasoning pipeline.
        Returns everything needed for the UI.
        """
        self.query_count += 1
        start_time = time.time()

        # ── Step 1: Get Claude's structured reasoning ──
        raw = self._call_claude(question)

        # ── Step 2: Wrap answer in AXON types ──
        answer_value = self.runtime.know(
            name=f"answer_{self.query_count}",
            value=raw["primary_answer"],
            confidence=raw["confidence"]
        )

        # ── Step 3: Memory — store with decay ──
        self.runtime.remember(
            name=f"query_{self.query_count}",
            value=question[:100],
            decay_rate=0.008  # fades over ~2 minutes
        )

        if raw.get("memory_note"):
            self.runtime.remember(
                name=f"insight_{self.query_count}",
                value=raw["memory_note"],
                decay_rate=0.003  # persists longer
            )

        # ── Step 4: consider() — branch on confidence ──
        consider_result = self.runtime.consider(answer_value)

        # ── Step 5: explore() — run hypothesis streams ──
        hypotheses = raw.get("hypotheses", [])
        explore_result = self.runtime.explore(hypotheses)

        # ── Step 6: attend() — focus on key areas ──
        attention_areas = raw.get("attention_areas", [])
        attend_result = self.runtime.attend(
            corpus=attention_areas,
            query=question,
            heads=4
        )

        # ── Step 7: qualia — register internal state ──
        qualia_obj = self.runtime.qualia(
            name=raw.get("qualia_state", "Uncertainty"),
            intensity=raw.get("qualia_intensity", 0.5),
            triggered_by=question[:50]
        )

        # ── Step 8: paradox check ──
        paradox_obj = None
        if raw.get("paradox"):
            paradox_obj = self.runtime.paradox(
                state_a="The question implies X",
                state_b="The question implies not-X",
                label=raw["paradox"]
            )

        elapsed = time.time() - start_time

        return {
            # Core answer
            "question": question,
            "answer": raw["primary_answer"],
            "confidence": answer_value.current_confidence(),
            "confidence_label": answer_value.confidence_label(),
            "confidence_reasoning": raw.get("confidence_reasoning", ""),

            # AXON constructs
            "consider": consider_result,
            "explore": explore_result,
            "attend": attend_result,
            "qualia": qualia_obj,
            "paradox": paradox_obj,

            # Memory state
            "memory_dump": self.runtime.memory_dump(),

            # Meta
            "cycle": self.runtime.cycle,
            "elapsed_ms": round(elapsed * 1000),
            "query_number": self.query_count,
        }
