#!/usr/bin/env python3
"""
task04_1_build_detector.py — TASK 04 Step 1.
Builds out/detector_results.jsonl from timeline.jsonl + detector_config.json.
No LLM calls. Deterministic.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).parent.parent
TIMELINE = BASE / "out" / "timeline.jsonl"
CONFIG = BASE / "config" / "detector_config.json"
ANCHORS = BASE / "config" / "timeline_anchors.json"
OUT = BASE / "out" / "detector_results.jsonl"
TODAY = "2026-06-27"


def load_json(path):
    if not path.exists():
        print(f"ERROR: {path} not found.", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_closure(axis, closure_signals, anchors_cfg):
    """Return (signal_label, date_or_none) for the axis."""
    sig = closure_signals.get(axis)
    if not sig or sig.get("type") == "none":
        return None, None
    if sig["type"] == "anchor":
        key = sig["anchor"]
        date = anchors_cfg.get("anchors", {}).get(key)
        return key, date
    if sig["type"] == "file_date":
        return f"file_date:{sig['date']}", sig["date"]
    return None, None


def atom_stub(a):
    return {
        "seq": a["seq"],
        "raw_text": a["raw_text"],
        "source_file": a["source_file"],
        "speaker": a.get("speaker"),
        "side": a.get("side"),
        "phase": a.get("phase"),
        "timestamp": a.get("timestamp"),
    }


def main():
    cfg = load_json(CONFIG)
    anch = load_json(ANCHORS)

    deal_id = cfg["deal_id"]
    exclude = set(cfg.get("exclude_sources", []))
    closure_signals = cfg.get("closure_signals", {})
    min_declared = cfg.get("min_declared_count", 2)

    atoms = [json.loads(l) for l in TIMELINE.open(encoding="utf-8")]

    # Split by axis × modality, excluding SLA drafts
    by_axis = defaultdict(lambda: {"declared": [], "done": []})
    excluded_atoms = 0
    for a in atoms:
        if a["source_file"] in exclude:
            excluded_atoms += 1
            continue
        axis = a.get("about_canon")
        modality = a.get("modality", "")
        if not axis:
            continue
        if modality == "declared":
            by_axis[axis]["declared"].append(a)
        elif modality == "done":
            by_axis[axis]["done"].append(a)

    print(f"Atoms excluded (SLA drafts): {excluded_atoms}")
    print(f"Axes with data: {len(by_axis)}")

    results = []
    for axis in sorted(by_axis):
        declared = sorted(by_axis[axis]["declared"], key=lambda x: x["seq"])
        done = sorted(by_axis[axis]["done"], key=lambda x: x["seq"])

        if len(declared) < min_declared:
            continue

        signal_label, closure_date = resolve_closure(axis, closure_signals, anch)
        closure_passed = bool(closure_date and closure_date <= TODAY)

        done_seqs = [d["seq"] for d in done]

        resolved_count = 0
        observed_absent_count = 0
        unresolved_count = 0

        for decl in declared:
            has_later_done = any(s > decl["seq"] for s in done_seqs)
            if has_later_done:
                resolved_count += 1
            elif closure_passed:
                observed_absent_count += 1
            else:
                unresolved_count += 1

        # Axis status = most critical present
        if observed_absent_count > 0:
            status = "observed_absent"
        elif unresolved_count > 0:
            status = "unresolved"
        else:
            status = "resolved"

        results.append({
            "deal_id": deal_id,
            "about_canon": axis,
            "status": status,
            "declared_count": len(declared),
            "done_count": len(done),
            "resolved_count": resolved_count,
            "observed_absent_count": observed_absent_count,
            "unresolved_count": unresolved_count,
            "closure_signal": signal_label,
            "closure_date": closure_date,
            "closure_passed": closure_passed,
            "top_declared": [atom_stub(a) for a in declared[:3]],
            "top_done": [atom_stub(a) for a in done],
        })

    # Sort: observed_absent first, then by declared_count desc
    STATUS_ORDER = {"observed_absent": 0, "unresolved": 1, "resolved": 2}
    results.sort(key=lambda x: (STATUS_ORDER[x["status"]], -x["declared_count"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Print table (top 20 by priority)
    W = 24
    print(
        f"\n{'Axis':<{W}} {'status':<17} {'decl':>5} {'done':>5} "
        f"{'res':>5} {'obs_ab':>7} {'unres':>6}  closure"
    )
    print("-" * 88)
    for r in results[:20]:
        print(
            f"{r['about_canon']:<{W}} {r['status']:<17} "
            f"{r['declared_count']:>5} {r['done_count']:>5} "
            f"{r['resolved_count']:>5} {r['observed_absent_count']:>7} "
            f"{r['unresolved_count']:>6}  {r['closure_signal'] or 'none'}"
        )

    by_status = defaultdict(int)
    for r in results:
        by_status[r["status"]] += 1

    print(f"\nTotal axes in results: {len(results)}")
    for s in ("observed_absent", "unresolved", "resolved"):
        print(f"  {s}: {by_status[s]}")
    print(f"\nWrote: {OUT}")


if __name__ == "__main__":
    main()
