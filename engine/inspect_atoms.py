import json, sys
from collections import Counter
path = sys.argv[1] if len(sys.argv) > 1 else "out_probe/atoms.jsonl"
rows = [json.loads(l) for l in open(path, encoding="utf-8")]
print("N atoms:", len(rows))
print("TYPES:", dict(Counter(r["type"] for r in rows)))
print("MODALITY:", dict(Counter(r["modality"] for r in rows)))
print("ABOUT:", dict(Counter(r["about"] for r in rows)))
print("SIDE:", dict(Counter(r["side"] for r in rows)))
print()
for r in rows:
    head = "[%s/%s/%s/about=%s]" % (r["side"], r["type"], r["modality"], r["about"])
    print(head)
    print("   " + r["raw_text"][:100])
