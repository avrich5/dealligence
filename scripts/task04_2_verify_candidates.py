#!/usr/bin/env python3
"""
task04_2_verify_candidates.py — TASK 04 Step 2.
Reads detector_results.jsonl, produces analysis/detector_report.md.
Verifies revshare and execution_control against GROUNDTRUTH §7.
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
DETECTOR = BASE / "out" / "detector_results.jsonl"
REPORT = BASE / "analysis" / "detector_report.md"
TODAY = "2026-06-27"

# GROUNDTRUTH §7 expectations — do not auto-correct deviations, flag as UNEXPECTED
GROUNDTRUTH_EXPECTATIONS = {
    "revshare": {
        "expected_status": "observed_absent",
        "note": "101 declared, 1 done in GROUNDTRUTH §7. SLA signed but no payment/calculation done.",
    },
    "execution_control": {
        "expected_status": "observed_absent",
        "note": "187 declared, 5 done. WB deployed own executor (diverges from declared: execution полностью на стороне MMI).",
    },
}


def fmt_atom(a, idx=None):
    prefix = f"[{idx}] " if idx is not None else ""
    ts = a.get("timestamp") or "?"
    seq = a.get("seq", "?")
    speaker = a.get("speaker") or "?"
    side = a.get("side") or "?"
    src = a.get("source_file", "?")
    raw = a.get("raw_text", "")[:200]
    return (
        f"{prefix}seq={seq} | {ts} | {speaker} ({side})\n"
        f"    src: {src}\n"
        f"    \"{raw}\""
    )


def main():
    if not DETECTOR.exists():
        print(f"ERROR: {DETECTOR} not found. Run Step 1 first.", file=sys.stderr)
        sys.exit(1)

    results = [json.loads(l) for l in DETECTOR.open(encoding="utf-8")]
    if not results:
        print("ERROR: detector_results.jsonl is empty.", file=sys.stderr)
        sys.exit(1)

    lines = []
    lines.append(f"# Detector Report — TASK 04 Step 2")
    lines.append(f"\nDate: {TODAY}")
    lines.append(f"Source: {DETECTOR}")
    lines.append(f"Total axes: {len(results)}\n")

    # Summary table
    lines.append("## Summary table (all axes)\n")
    lines.append(f"| Axis | Status | decl | done | resolved | obs_absent | unresolved | closure |")
    lines.append(f"|---|---|---|---|---|---|---|---|")
    for r in results:
        lines.append(
            f"| `{r['about_canon']}` | **{r['status']}** | {r['declared_count']} "
            f"| {r['done_count']} | {r['resolved_count']} | {r['observed_absent_count']} "
            f"| {r['unresolved_count']} | {r['closure_signal'] or 'none'} |"
        )

    # Top-5 axes detail
    lines.append("\n\n## Top-5 axes by declared_count — detail\n")
    top5 = sorted(results, key=lambda x: -x["declared_count"])[:5]

    for r in top5:
        axis = r["about_canon"]
        lines.append(f"### `{axis}` — {r['status']}")
        lines.append(
            f"declared={r['declared_count']} done={r['done_count']} "
            f"resolved={r['resolved_count']} obs_absent={r['observed_absent_count']} "
            f"unresolved={r['unresolved_count']}  "
            f"closure={r['closure_signal'] or 'none'} ({r['closure_date'] or 'N/A'})"
        )
        lines.append("\n**Sample declared (up to 3):**\n```")
        for i, a in enumerate(r["top_declared"], 1):
            lines.append(fmt_atom(a, i))
        lines.append("```")

        if r["top_done"]:
            lines.append("\n**All done atoms:**\n```")
            for i, a in enumerate(r["top_done"], 1):
                lines.append(fmt_atom(a, i))
            lines.append("```")
        else:
            lines.append("\n**Done atoms: none.**")
        lines.append("")

    # GROUNDTRUTH §7 verification
    lines.append("\n## GROUNDTRUTH §7 verification\n")
    all_ok = True
    for axis, expectation in GROUNDTRUTH_EXPECTATIONS.items():
        result = next((r for r in results if r["about_canon"] == axis), None)
        if result is None:
            lines.append(f"### `{axis}` — UNEXPECTED: axis not found in results")
            lines.append(f"  Note: {expectation['note']}")
            all_ok = False
            continue

        actual = result["status"]
        expected = expectation["expected_status"]
        match = actual == expected

        tag = "OK" if match else "UNEXPECTED"
        lines.append(f"### `{axis}` — {tag}")
        lines.append(f"- Expected status: `{expected}`")
        lines.append(f"- Actual status:   `{actual}`")
        lines.append(
            f"- declared={result['declared_count']} done={result['done_count']} "
            f"resolved={result['resolved_count']} obs_absent={result['observed_absent_count']} "
            f"unresolved={result['unresolved_count']}"
        )
        lines.append(f"- GROUNDTRUTH note: {expectation['note']}")
        if not match:
            lines.append(
                f"\n⚠️  UNEXPECTED: actual `{actual}` ≠ expected `{expected}`. "
                "Do NOT auto-correct — requires Andriy decision."
            )
            all_ok = False
        lines.append("")

    if all_ok:
        lines.append("All GROUNDTRUTH §7 verifications passed.\n")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Stdout summary
    print(f"\nGROUNDTRUTH §7 checks:")
    for axis, expectation in GROUNDTRUTH_EXPECTATIONS.items():
        result = next((r for r in results if r["about_canon"] == axis), None)
        if result is None:
            print(f"  [{axis}] UNEXPECTED: axis missing")
        else:
            actual = result["status"]
            expected = expectation["expected_status"]
            tag = "OK" if actual == expected else "UNEXPECTED"
            print(f"  [{axis}] {tag}: expected={expected}, actual={actual} "
                  f"(decl={result['declared_count']}, done={result['done_count']})")
    print(f"\nReport written: {REPORT}")


if __name__ == "__main__":
    main()
