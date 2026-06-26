"""
atomizer.py — pass 1: corpus -> atoms (JSONL).

Reads each text file, calls the orchestrator, parses the JSON array,
verifies each raw_text actually occurs in the source (anti-fabrication),
assigns stable ids, writes atoms.jsonl + a run report.

Usage:
    python3 atomizer.py /path/to/corpus_dir /path/to/out_dir
"""

from __future__ import annotations
import sys, os, json, re, hashlib, glob
from atom import Atom
from prompts import SYSTEM, USER_TEMPLATE
import llm_client


def _confidence_source(fname: str) -> str:
    low = fname.lower()
    if "telegram" in low or "slack" in low:
        return "chat"
    if "sla" in low or "prd" in low or "agreement" in low or "nda" in low:
        return "document"
    return "transcript"


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def _chunk(text: str, max_chars: int = 12000) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    lines, chunks, buf = text.splitlines(keepends=True), [], ""
    for ln in lines:
        if len(buf) + len(ln) > max_chars:
            chunks.append(buf); buf = ""
        buf += ln
    if buf:
        chunks.append(buf)
    return chunks


def _parse_json_array(raw: str) -> list:
    raw = raw.strip()
    raw = re.sub(r"^```(json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        return []
    return json.loads(raw[start:end + 1])


def atomize_file(path: str, source_file: str) -> tuple[list, dict]:
    text = open(path, encoding="utf-8").read()
    cs = _confidence_source(source_file)
    norm_src = _norm(text)
    atoms, rejected, cost = [], 0, 0.0

    for ci, chunk in enumerate(_chunk(text)):
        msgs = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER_TEMPLATE.format(
                source_file=source_file, confidence_source=cs, text=chunk)},
        ]
        resp = llm_client.complete(msgs, task_tier="default", max_tokens=8000)
        cost += resp.get("cost_usd", 0.0)
        try:
            raw_atoms = _parse_json_array(resp["text"])
        except Exception as e:
            print(f"  ! parse fail {source_file} chunk{ci}: {e}")
            continue

        for j, ra in enumerate(raw_atoms):
            rt = (ra.get("raw_text") or "").strip()
            if not rt or _norm(rt) not in norm_src:
                rejected += 1          # anti-fabrication: citation not found
                continue
            aid = f"{source_file}:{ci}:{j}:" + hashlib.md5(
                rt.encode("utf-8")).hexdigest()[:8]
            a = Atom(
                id=aid, source_file=source_file,
                speaker=ra.get("speaker", "?"), side=ra.get("side", "external"),
                raw_text=rt, type=ra.get("type", "unknown"),
                modality=ra.get("modality", "unknown"),
                about=ra.get("about", "unknown"),
                confidence_source=cs, timestamp=ra.get("timestamp"),
                notes=ra.get("notes"),
            )
            err = a.validate()
            if err:
                rejected += 1; continue
            atoms.append(a)

    return atoms, {"file": source_file, "atoms": len(atoms),
                   "rejected": rejected, "cost_usd": round(cost, 5)}


def main(corpus_dir: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(corpus_dir, "**", "*.txt"),
                             recursive=True))
    all_atoms, report = [], []
    for p in files:
        sf = os.path.relpath(p, corpus_dir)
        print(f"-> {sf}")
        atoms, rep = atomize_file(p, sf)
        all_atoms.extend(atoms); report.append(rep)
        print(f"   atoms={rep['atoms']} rejected={rep['rejected']} "
              f"cost=${rep['cost_usd']}")

    from atom import atoms_to_jsonl
    atoms_to_jsonl(all_atoms, os.path.join(out_dir, "atoms.jsonl"))
    json.dump(report, open(os.path.join(out_dir, "run_report.json"), "w"),
              ensure_ascii=False, indent=2)
    total_cost = round(sum(r["cost_usd"] for r in report), 4)
    print(f"\nTOTAL atoms={len(all_atoms)} cost=${total_cost}")
    print(f"written: {out_dir}/atoms.jsonl")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
