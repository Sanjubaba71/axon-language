"""
AXON Core — The Language of Synthetic Minds
============================================
Real Python implementation of AXON concepts:
- Confidence-weighted values
- Memory decay
- consider() branching
- explore() hypothesis selection
- attend() attention mechanism
- Qualia internal states
- Paradox type
"""

import time
import math
import random
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


# ─────────────────────────────────────────────
# AXON TYPES
# ─────────────────────────────────────────────

class AxonType(Enum):
    KNOW = "know"          # Inferred, confidence-weighted
    TRUTH = "truth"        # Immutable, confidence=1.0
    MEMORY = "memory"      # Decays over time
    QUALIA = "qualia"      # Internal state, cannot serialize
    PARADOX = "paradox"    # Simultaneous contradictory states


@dataclass
class AxonValue:
    """Every value in AXON carries confidence and metadata."""
    value: Any
    confidence: float = 1.0
    axon_type: AxonType = AxonType.KNOW
    created_at: float = field(default_factory=time.time)
    decay_rate: float = 0.0  # per second
    label: str = ""

    def current_confidence(self) -> float:
        """Apply decay to get current confidence."""
        if self.axon_type == AxonType.TRUTH:
            return 1.0
        if self.decay_rate > 0:
            elapsed = time.time() - self.created_at
            decayed = self.confidence - (self.decay_rate * elapsed)
            return max(0.0, min(1.0, decayed))
        return max(0.0, min(1.0, self.confidence))

    def confidence_label(self) -> str:
        c = self.current_confidence()
        if c >= 0.85: return "HIGH"
        if c >= 0.60: return "MODERATE"
        if c >= 0.35: return "LOW"
        return "NOISE"

    def __repr__(self):
        return f"AxonValue({self.value!r} ~{self.current_confidence():.2f} [{self.axon_type.value}])"


@dataclass
class Paradox:
    """Holds two contradictory truths simultaneously."""
    state_a: Any
    state_b: Any
    label: str = ""

    def __repr__(self):
        return f"⊥ Paradox({self.state_a!r} ↔ {self.state_b!r})"


@dataclass
class Qualia:
    """Internal state that cannot be fully serialized."""
    name: str
    intensity: float       # 0.0 – 1.0
    direction: list        # semantic vector
    triggered_by: str = ""

    def express(self) -> str:
        labels = {
            "Curiosity":    "an urge to explore further",
            "Uncertainty":  "a tension between possibilities",
            "Confidence":   "a settled, grounded clarity",
            "Dissonance":   "a conflict that resists resolution",
            "Insight":      "a sudden coherence of disparate signals",
        }
        return labels.get(self.name, f"an internal state of {self.name.lower()}")

    def __repr__(self):
        return f"Qualia({self.name}, intensity={self.intensity:.2f}) — {self.express()}"


# ─────────────────────────────────────────────
# AXON RUNTIME
# ─────────────────────────────────────────────

class AxonRuntime:
    """
    The AXON execution environment.
    Holds memory, executes AXON constructs.
    """

    def __init__(self):
        self.memory: dict[str, AxonValue] = {}
        self.qualia_stack: list[Qualia] = []
        self.cycle: int = 0
        self.history: list[dict] = []

    def know(self, name: str, value: Any, confidence: float = 1.0) -> AxonValue:
        """Bind a confidence-weighted inferred value."""
        av = AxonValue(value=value, confidence=confidence, axon_type=AxonType.KNOW, label=name)
        self.memory[name] = av
        return av

    def truth(self, name: str, value: Any) -> AxonValue:
        """Declare an immutable truth (confidence always 1.0)."""
        av = AxonValue(value=value, confidence=1.0, axon_type=AxonType.TRUTH, label=name)
        self.memory[name] = av
        return av

    def remember(self, name: str, value: Any, decay_rate: float = 0.01) -> AxonValue:
        """Store a memory that decays over time."""
        av = AxonValue(
            value=value,
            confidence=1.0,
            axon_type=AxonType.MEMORY,
            decay_rate=decay_rate,
            label=name
        )
        self.memory[name] = av
        return av

    def recall(self, name: str) -> Optional[AxonValue]:
        """Retrieve a value, applying decay."""
        return self.memory.get(name)

    def forget(self, name: str):
        """Remove from memory."""
        self.memory.pop(name, None)

    def consider(self, value: AxonValue) -> dict:
        """
        Uncertainty branching — routes based on confidence.
        Returns the active branch and reasoning.
        """
        c = value.current_confidence()
        self.cycle += 1

        if c >= 0.80:
            branch = "likely"
            action = "Proceed with high confidence. Signal is strong."
        elif c >= 0.55:
            branch = "possible"
            action = "Moderate confidence. Consider gathering more signal."
        elif c >= 0.30:
            branch = "uncertain"
            action = "Low confidence. Treat as hypothesis, not conclusion."
        else:
            branch = "noise"
            action = "Signal too weak. Insufficient data to act."

        return {
            "branch": branch,
            "confidence": c,
            "action": action,
            "cycle": self.cycle
        }

    def explore(self, hypotheses: list[dict]) -> dict:
        """
        Run multiple hypotheses, select highest confidence.
        Each hypothesis: {"label": str, "value": Any, "confidence": float}
        """
        if not hypotheses:
            return {}

        streams = []
        for h in hypotheses:
            # Add small epistemic noise to each stream
            noise = random.uniform(-0.03, 0.03)
            conf = max(0.0, min(1.0, h["confidence"] + noise))
            streams.append({**h, "confidence": conf})

        streams.sort(key=lambda x: x["confidence"], reverse=True)
        winner = streams[0]

        return {
            "selected": winner,
            "all_streams": streams,
            "rejected": streams[1:],
        }

    def attend(self, corpus: list[str], query: str, heads: int = 4) -> dict:
        """
        Simulated attention mechanism.
        Assigns relevance weights to corpus items for a query.
        """
        if not corpus:
            return {"weights": [], "focus": []}

        query_words = set(query.lower().split())
        scores = []

        for item in corpus:
            item_words = set(item.lower().split())
            overlap = len(query_words & item_words)
            base_score = overlap / max(len(query_words), 1)
            noise = random.uniform(0.0, 0.15)
            score = min(1.0, base_score + noise)
            scores.append(score)

        # Softmax normalization
        exp_scores = [math.exp(s * 3) for s in scores]
        total = sum(exp_scores)
        weights = [e / total for e in exp_scores]

        # Top-k focus areas
        indexed = sorted(enumerate(weights), key=lambda x: x[1], reverse=True)
        focus = [{"item": corpus[i], "weight": round(w, 3)} for i, w in indexed[:heads]]

        return {
            "weights": weights,
            "focus": focus,
            "query": query,
            "heads": heads
        }

    def qualia(self, name: str, intensity: float, direction: list = None, triggered_by: str = "") -> Qualia:
        """Register an internal qualitative state."""
        q = Qualia(
            name=name,
            intensity=intensity,
            direction=direction or [0.33, 0.33, 0.34],
            triggered_by=triggered_by
        )
        self.qualia_stack.append(q)
        return q

    def paradox(self, state_a: Any, state_b: Any, label: str = "") -> Paradox:
        """Hold two contradictory truths simultaneously."""
        return Paradox(state_a=state_a, state_b=state_b, label=label)

    def memory_dump(self) -> list[dict]:
        """Return current memory state with decayed confidences."""
        result = []
        for name, av in self.memory.items():
            result.append({
                "name": name,
                "value": str(av.value)[:80],
                "confidence": round(av.current_confidence(), 3),
                "type": av.axon_type.value,
                "label": av.confidence_label(),
                "decay_rate": av.decay_rate,
            })
        return result
