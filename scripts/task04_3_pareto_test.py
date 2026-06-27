#!/usr/bin/env python3
"""
task04_3_pareto_test.py — TASK 04 Step 3.
Pareto test: do top-3 detector signals include axes not in GROUNDTRUTH §7?
KNOWN = axis+status was in GROUNDTRUTH before detector run.
NEW   = detector found something not explicitly hypothesised before.
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
DETECTOR = BASE / "out" / "detector_results.jsonl"

# GROUNDTRUTH §7 axes hypothesised BEFORE the detector run (2026-06-27).
# Only axes explicitly listed with an expected status count as KNOWN.
GROUNDTRUTH_PRIOR = {
    "revshare":          "observed_absent",
    "execution_control": "observed_absent",  # "расхождение по стороне" = observed_absent
}


def main():
    if not DETECTOR.exists():
        print(f"ERROR: {DETECTOR} not found. Run Step 1 first.", file=sys.stderr)
        sys.exit(1)

    results = [json.loads(l) for l in DETECTOR.open(encoding="utf-8")]

    # Top-3 by criticality: observed_absent first, then unresolved, then by declared_count
    STATUS_ORDER = {"observed_absent": 0, "unresolved": 1, "resolved": 2}
    top3 = sorted(
        results,
        key=lambda x: (STATUS_ORDER.get(x["status"], 9), -x["declared_count"])
    )[:3]

    print("\n── Pareto Test — Top-3 detector signals ──────────────────────────")
    any_new = False
    for i, r in enumerate(top3, 1):
        axis = r["about_canon"]
        status = r["status"]
        prior_status = GROUNDTRUTH_PRIOR.get(axis)

        if prior_status is not None and prior_status == status:
            tag = "KNOWN"
        else:
            tag = "NEW"
            any_new = True

        print(
            f"  #{i} [{tag}] axis={axis} status={status} "
            f"decl={r['declared_count']} done={r['done_count']} "
            f"obs_absent={r['observed_absent_count']} unres={r['unresolved_count']}"
        )
        if tag == "KNOWN":
            print(f"       → was in GROUNDTRUTH §7 before detector run")
        else:
            print(f"       → NOT in GROUNDTRUTH §7 — detector added value ✓")

    print()
    if any_new:
        print("PARETO CRITERION: MET ✓")
        print("  ≥1 top-3 signal was not hypothesised before detector run.")
        print("  The engine surfaced new information beyond analyst memory.")
    else:
        print("PARETO CRITERION: NOT MET")
        print("  All top-3 signals were already in GROUNDTRUTH §7.")
        print("  Detector confirmed known hypotheses but added no new signals.")

    print()
    print("All axes by status+priority:")
    STATUS_ORDER_PRINT = {"observed_absent": "OBS_ABS", "unresolved": "UNRES", "resolved": "RESOL"}
    for r in results[:10]:
        tag = "KNOWN" if (
            GROUNDTRUTH_PRIOR.get(r["about_canon"]) == r["status"]
        ) else "new"
        print(
            f"  {tag:5} {STATUS_ORDER_PRINT.get(r['status'], r['status']):8} "
            f"{r['about_canon']:<25} decl={r['declared_count']:>4} done={r['done_count']:>3}"
        )


if __name__ == "__main__":
    main()
