"""
atomize_one.py — atomize a SINGLE file, append to master atoms.jsonl,
print billing delta. For controlled, one-at-a-time runs.

Usage:
    python3 atomize_one.py corpus_txt/<file>.txt
"""
import sys, os, json, httpx
from atomizer import atomize_file
from atom import atoms_to_jsonl

K = os.getenv("ORCHESTRATOR_API_KEY", "")
URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:4700")
MASTER = "out/atoms.jsonl"


def balance():
    r = httpx.get(f"{URL}/v1/billing/summary", params={"period": "month"},
                  headers={"X-API-Key": K}, timeout=30)
    t = r.json()["totals"]["total_usd"]
    return round(t, 5)


def main(path: str):
    sf = os.path.basename(path)
    before = balance()
    print(f"balance before: ${before}")
    atoms, rep = atomize_file(path, sf)
    after = balance()
    print(f"file={sf} atoms={rep['atoms']} rejected={rep['rejected']}")
    print(f"balance after:  ${after}  (delta ${round(after-before,5)})")

    os.makedirs("out", exist_ok=True)
    existing = []
    if os.path.exists(MASTER):
        existing = [json.loads(l) for l in open(MASTER, encoding="utf-8")]
    merged = existing + [a.to_dict() for a in atoms]
    with open(MASTER, "w", encoding="utf-8") as fh:
        for a in merged:
            fh.write(json.dumps(a, ensure_ascii=False) + "\n")
    print(f"master total atoms: {len(merged)}  (was {len(existing)})")


if __name__ == "__main__":
    main(sys.argv[1])
