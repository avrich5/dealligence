"""
ingest.py — convert the full corpus (any format) to normalized .txt.

Strategy:
  - .txt / .md : copied as-is (already text)
  - everything else (.docx .pages .pdf .key .rtf .html) : LibreOffice headless
    --convert-to txt

Dedup rule (Andriy): drop a non-txt file ONLY if a file with the SAME stem
already produced text. Same stem = same content in another container.

Usage:
    python3 ingest.py "<SRC_DIR>" <OUT_TXT_DIR>
"""

from __future__ import annotations
import sys, os, glob, shutil, subprocess, hashlib

SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
TEXT_EXT = {".txt", ".md"}
SKIP_EXT = {".m4a", ".ds_store"}


def _slug(stem: str) -> str:
    # filesystem-safe, collision-resistant target name
    safe = "".join(c if c.isalnum() else "_" for c in stem).strip("_")
    h = hashlib.md5(stem.encode("utf-8")).hexdigest()[:6]
    return f"{safe[:60]}__{h}"


def _pdf_to_txt(src: str, out_dir: str) -> str | None:
    try:
        from pdfminer.high_level import extract_text
        txt = extract_text(src) or ""
    except Exception as e:
        print(f"   ! pdfminer fail {os.path.basename(src)}: {e}")
        return None
    if not txt.strip():
        return None
    stem = os.path.splitext(os.path.basename(src))[0]
    produced = os.path.join(out_dir, stem + ".pdftxt")
    with open(produced, "w", encoding="utf-8") as fh:
        fh.write(txt)
    return produced


def _soffice_to_txt(src: str, out_dir: str) -> str | None:
    # LibreOffice writes <stem>.txt into out_dir; we then rename to slug
    r = subprocess.run(
        [SOFFICE, "--headless", "--convert-to", "txt:Text",
         "--outdir", out_dir, src],
        capture_output=True, text=True, timeout=120)
    stem = os.path.splitext(os.path.basename(src))[0]
    produced = os.path.join(out_dir, stem + ".txt")
    if os.path.exists(produced):
        return produced
    print(f"   ! soffice no output for {os.path.basename(src)}: "
          f"{r.stdout.strip()[:120]} {r.stderr.strip()[:120]}")
    return None


def main(src_dir: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_tmp_soffice")
    os.makedirs(tmp, exist_ok=True)

    files = [p for p in glob.glob(os.path.join(src_dir, "**", "*"), recursive=True)
             if os.path.isfile(p)]
    # process text-native first so dedup can suppress their binary twins
    files.sort(key=lambda p: (os.path.splitext(p)[1].lower() not in TEXT_EXT,
                              os.path.basename(p)))

    seen_stems: set[str] = set()
    manifest = []
    for p in files:
        base = os.path.basename(p)
        stem, ext = os.path.splitext(base)
        ext = ext.lower()
        if base == ".DS_Store" or ext in SKIP_EXT:
            continue
        if stem in seen_stems:
            manifest.append((base, "skip_dup", ""))
            print(f"skip dup  {base}")
            continue

        target = os.path.join(out_dir, _slug(stem) + ".txt")
        if ext in TEXT_EXT:
            shutil.copyfile(p, target)
            seen_stems.add(stem)
            manifest.append((base, "copied", os.path.basename(target)))
            print(f"copied    {base}")
        else:
            produced = (_pdf_to_txt(p, tmp) if ext == ".pdf"
                        else _soffice_to_txt(p, tmp))
            if produced and os.path.getsize(produced) > 0:
                shutil.move(produced, target)
                seen_stems.add(stem)
                manifest.append((base, "converted", os.path.basename(target)))
                print(f"converted {base}")
            else:
                manifest.append((base, "FAILED", ""))
                print(f"FAILED    {base}")

    shutil.rmtree(tmp, ignore_errors=True)
    with open(os.path.join(out_dir, "_manifest.tsv"), "w", encoding="utf-8") as fh:
        fh.write("source\tstatus\ttarget\n")
        for row in manifest:
            fh.write("\t".join(row) + "\n")

    ok = sum(1 for _, s, _ in manifest if s in ("copied", "converted"))
    fail = sum(1 for _, s, _ in manifest if s == "FAILED")
    dup = sum(1 for _, s, _ in manifest if s == "skip_dup")
    print(f"\ningested={ok} failed={fail} dup_skipped={dup} -> {out_dir}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
