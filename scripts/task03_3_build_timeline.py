#!/usr/bin/env python3
"""
task03_3_build_timeline.py — TASK 03 Step 3.
Builds out/timeline.jsonl from:
  - out/atoms_canon.jsonl
  - analysis/file_dates.json
  - config/timeline_anchors.json  (must be filled by Andriy first)

Assigns: timestamp, timestamp_confidence, seq, phase, deal_id to every atom.
Prints distribution summary to stdout.
"""

import json
import re
import sys
from pathlib import Path
from collections import Counter
from typing import Optional

BASE = Path(__file__).parent.parent
ATOMS_FILE = BASE / "out" / "atoms_canon.jsonl"
FILE_DATES = BASE / "analysis" / "file_dates.json"
ANCHORS_FILE = BASE / "config" / "timeline_anchors.json"
OUT_FILE = BASE / "out" / "timeline.jsonl"

# ISO date extraction from raw_text (exact confidence)
DATE_RE = re.compile(
    r"\b(20\d{2})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b"
    r"|"
    r"\b(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[0-2])\.(20\d{2})\b"
    r"|"
    r"\b(0[1-9]|[12]\d|3[01])-(0[1-9]|1[0-2])-(20\d{2})\b"
)


def _extract_date_from_rawtext(raw: str):
    """Return first YYYY-MM-DD found in raw_text, or None."""
    m = re.search(r"\b(20\d{2})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b", raw)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.search(r"\b(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[0-2])\.(20\d{2})\b", raw)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    m = re.search(r"\b(0[1-9]|[12]\d|3[01])-(0[1-9]|1[0-2])-(20\d{2})\b", raw)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    return None


def _resolve_anchor(value, anchors: dict) -> Optional[str]:
    """Resolve anchor value: a named key or an ISO date string."""
    if value is None:
        return None
    if re.match(r"^\d{4}-\d{2}-\d{2}$", str(value)):
        return value
    return anchors.get(value)


def determine_phase(ts, phases: dict, anchors: dict) -> str:
    if ts is None:
        return "unknown"

    for phase_name, bounds in phases.items():
        from_anchor = _resolve_anchor(bounds.get("from"), anchors)
        to_anchor = _resolve_anchor(bounds.get("to"), anchors)

        after_from = (from_anchor is None) or (ts >= from_anchor)
        before_to = (to_anchor is None) or (ts < to_anchor)

        if after_from and before_to:
            return phase_name

    return "unknown"


def _atom_order(atom: dict) -> tuple:
    """Extract (chunk_idx, atom_in_chunk) from atom id for within-file ordering."""
    parts = atom["id"].split(":")
    if len(parts) >= 3:
        try:
            return (int(parts[1]), int(parts[2]))
        except ValueError:
            pass
    return (0, 0)


def main():
    # Guard: anchors file must exist and be filled
    if not ANCHORS_FILE.exists():
        print(
            f"ERROR: {ANCHORS_FILE} not found.\n"
            "Run Step 1 first, then Andriy fills config/timeline_anchors.json.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(ANCHORS_FILE, encoding="utf-8") as f:
        anchors_cfg = json.load(f)

    anchors = anchors_cfg.get("anchors", {})
    phases_cfg = anchors_cfg.get("phases", {})
    deal_id = anchors_cfg["deal_id"]
    # file_date_overrides: manually verified dates for specific files (higher priority than file_dates.json)
    overrides = anchors_cfg.get("file_date_overrides", {})

    # Check that at least sla_signed is set (minimum to define pre_sla / post_sla)
    if not anchors.get("sla_signed"):
        print(
            "WARNING: anchors.sla_signed is not set in timeline_anchors.json.\n"
            "Phase assignment will produce mostly 'unknown'.",
            file=sys.stderr,
        )

    with open(FILE_DATES, encoding="utf-8") as f:
        file_dates = json.load(f)

    atoms = [json.loads(l) for l in open(ATOMS_FILE, encoding="utf-8")]

    enriched = []
    for atom in atoms:
        raw = atom.get("raw_text", "")
        source = atom["source_file"]
        chunk_idx, atom_in_chunk = _atom_order(atom)

        # 1. Explicit date in raw_text → exact
        exact_ts = _extract_date_from_rawtext(raw)
        if exact_ts:
            ts = exact_ts
            ts_conf = "exact"
        # 2. Manual override from timeline_anchors.json → exact (Andriy-verified)
        elif source in overrides and overrides[source].get("date"):
            ts = overrides[source]["date"]
            ts_conf = "exact"
        # 3. File date from file_dates.json → inferred
        # (atomizer timestamps are skipped: they may contain wrong year inferences)
        elif source in file_dates and file_dates[source]["file_date"]:
            ts = file_dates[source]["file_date"]
            ts_conf = "inferred"
        # 4. No date
        else:
            ts = None
            ts_conf = "file_order"

        phase = determine_phase(ts, phases_cfg, anchors)

        enriched.append({
            "_sort_ts": ts or "9999-99-99",  # nulls last
            "_sort_file": source,
            "_sort_chunk": chunk_idx,
            "_sort_atom": atom_in_chunk,
            "deal_id": deal_id,
            "atom_id": atom["id"],
            "source_file": source,
            "timestamp": ts,
            "timestamp_confidence": ts_conf,
            "seq": 0,  # assigned after sorting
            "phase": phase,
            "speaker": atom.get("speaker"),
            "side": atom.get("side"),
            "type_canon": atom.get("type_canon"),
            "about_canon": atom.get("about_canon"),
            "modality": atom.get("modality"),
            "raw_text": raw,
        })

    # Sort: timestamp nulls_last, then source_file, then chunk, then atom
    enriched.sort(
        key=lambda x: (
            x["_sort_ts"],
            x["_sort_file"],
            x["_sort_chunk"],
            x["_sort_atom"],
        )
    )

    # Assign seq 1..N
    for i, item in enumerate(enriched, 1):
        item["seq"] = i

    # Strip sort keys
    timeline = []
    for item in enriched:
        row = {k: v for k, v in item.items() if not k.startswith("_sort")}
        timeline.append(row)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for row in timeline:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Print stats
    total = len(timeline)
    conf_counts = Counter(r["timestamp_confidence"] for r in timeline)
    phase_counts = Counter(r["phase"] for r in timeline)

    print(f"\nTimeline built: {total} atoms → {OUT_FILE}")

    print("\nPhase distribution:")
    for phase, cnt in sorted(phase_counts.items()):
        print(f"  {phase:<15} {cnt:>5}  ({100*cnt/total:.1f}%)")

    print("\ntimestamp_confidence:")
    for conf, cnt in sorted(conf_counts.items()):
        print(f"  {conf:<12} {cnt:>5}  ({100*cnt/total:.1f}%)")

    # Top-5 files with most file_order atoms
    fo_atoms = [r for r in timeline if r["timestamp_confidence"] == "file_order"]
    if fo_atoms:
        per_file = Counter(r["source_file"] for r in fo_atoms)
        print("\nTop-5 files with most atoms without date (file_order):")
        for fname, cnt in per_file.most_common(5):
            print(f"  {fname}: {cnt}")


if __name__ == "__main__":
    main()
