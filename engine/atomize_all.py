"""
atomize_all.py — atomize every corpus_txt/*.txt NOT yet in master,
one file at a time, append to out/atoms.jsonl, print billing per file.
Resumable: skips files already present in master by source_file.

Usage:
    python3 atomize_all.py
"""
import os, json, glob, httpx
from atomizer import atomize_file

K = os.getenv("ORCHESTRATOR_API_KEY", "")
URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:4700")
MASTER = "out/atoms.jsonl"
CORPUS = "corpus_txt"


def balance():
    r = httpx.get(f"{URL}/v1/billing/summary", params={"period": "month"},
                  headers={"X-API-Key": K}, timeout=30)
    return round(r.json()["totals"]["total_usd"], 5)


def load_master():
    if not os.path.exists(MASTER):
        return []
    return [json.loads(l) for l in open(MASTER, encoding="utf-8")]


def main():
    master = load_master()
    done = {r["source_file"] for r in master}
    files = sorted(glob.glob(os.path.join(CORPUS, "*.txt")))
    todo = [p for p in files if os.path.basename(p) not in done]
    print(f"master has {len(master)} atoms from {len(done)} files")
    print(f"to process: {len(todo)} files\n")

    start = balance()
    for i, p in enumerate(todo, 1):
        sf = os.path.basename(p)
        atoms, rep = atomize_file(p, sf)
        master.extend(a.to_dict() for a in atoms)
        with open(MASTER, "w", encoding="utf-8") as fh:
            for a in master:
                fh.write(json.dumps(a, ensure_ascii=False) + "\n")
        bal = balance()
        print(f"[{i}/{len(todo)}] {sf[:50]:50} "
              f"atoms={rep['atoms']:3} rej={rep['rejected']:2} "
              f"bal=${bal} master={len(master)}")
        if bal > 4.5:
            print("!! approaching $5 budget, stopping")
            break

    print(f"\nDONE. spent this run: ${round(balance()-start,4)}  "
          f"total master atoms: {len(master)}")


if __name__ == "__main__":
    main()
