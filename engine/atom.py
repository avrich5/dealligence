"""
atom.py — schema for a single semantic atom.

An atom = one verifiable statement inside one utterance.
LLM produces atoms; every atom MUST carry verbatim raw_text.
No raw_text -> atom is rejected (anti-fabrication).

type / about / link.relation are EMERGENT (free labels in pass 1).
They converge to a canon only after the whole corpus is seen.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import json


# modality is the one closed vocabulary we fix up front, because the
# declared-vs-observed detector depends on it. Everything else is emergent.
MODALITY = {
    "declared",        # said / promised / claimed
    "done",            # confirmed actually happened
    "observed_absent", # expected from a declaration, not seen in reality
    "denied",          # explicitly refused / negated
    "unknown",
}

CONFIDENCE_SOURCE = {
    "document",       # signed contract, PRD, written artifact
    "transcript",     # call/meeting transcript
    "chat",           # telegram / slack text
    "oral_andriy",    # Andriy's own recollection, not in corpus text
}


@dataclass
class Link:
    relation: str      # emergent: contradicts | fulfills | defers | causes ...
    target_id: str


@dataclass
class Atom:
    id: str
    source_file: str
    speaker: str
    side: str                     # MMI | WB | legal | external
    raw_text: str                 # verbatim, mandatory
    type: str                     # emergent
    modality: str                 # from MODALITY
    about: str                    # emergent axis label
    confidence_source: str        # from CONFIDENCE_SOURCE
    timestamp: Optional[str] = None   # ISO date if extractable, else None
    links: list = field(default_factory=list)
    notes: Optional[str] = None

    def validate(self) -> Optional[str]:
        if not self.raw_text or not self.raw_text.strip():
            return f"{self.id}: empty raw_text"
        if self.modality not in MODALITY:
            return f"{self.id}: bad modality {self.modality!r}"
        if self.confidence_source not in CONFIDENCE_SOURCE:
            return f"{self.id}: bad confidence_source {self.confidence_source!r}"
        return None

    def to_dict(self) -> dict:
        return asdict(self)


def atoms_to_jsonl(atoms: list, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for a in atoms:
            fh.write(json.dumps(a.to_dict(), ensure_ascii=False) + "\n")
