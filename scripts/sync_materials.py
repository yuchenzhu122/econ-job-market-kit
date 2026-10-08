"""Copy the latest version of each master file from My Materials into the job market folders.

  python3 scripts/sync_materials.py           # copy what changed
  python3 scripts/sync_materials.py --check   # only report what would change and what is missing

Reads My Materials/00-knowledge-base/materials-index.md, a Markdown table:

  | Key | Source | Target folder | Note |
  |-----|--------|---------------|------|
  | cv  | ~/Documents/website/materials/research/Jane_Doe_CV.tex | 01_CV | |
  | jmp | Papers/JMP.pdf | 02_Job_Market_Paper | |

Source is relative to My Materials (or absolute / ~); symlinks and Finder aliases are followed.
Target folder is relative to the academic job market folder (job_market_dir); "industry:<folder>"
puts it in the industry folder; empty = not copied (the file is only used to write materials).
You choose the folders: the 01_CV ... 07_Statements layout is only a suggestion.

What is copied: a PDF or Word file as is; a .tex file as its PDF (the PDF next to it if that one
is newer, otherwise compiled in a scratch copy of its folder, so your folder is not touched); a
.md file through md2pdf.py (title = the Note column, or the file name). A file is replaced only
when the master is newer; files you put in the target folders yourself are never deleted.
"""
import os
import shutil
import subprocess
import sys
import tempfile

from common import industry_path, jm_path, load_config, read_index, resolve_alias, run_pdflatex

HERE = os.path.dirname(os.path.abspath(__file__))


def built_pdf(src, note):
    """Path of an up-to-date PDF for src (may be a temporary file), or the file itself."""
    stem, ext = os.path.splitext(src)
    ext = ext.lower()
    if ext in (".pdf", ".docx", ".doc"):
        return src
    if ext == ".tex":
        if os.path.exists(stem + ".pdf") and os.path.getmtime(stem + ".pdf") >= os.path.getmtime(src):
            return stem + ".pdf"
        tmp = tempfile.mkdtemp()
        work = os.path.join(tmp, "src")
        shutil.copytree(os.path.dirname(src), work, ignore=shutil.ignore_patterns(".git", "*.pdf", "_archive"))
        pdf = run_pdflatex(work, os.path.basename(stem))
        return pdf if os.path.exists(pdf) else None
    if ext == ".md":
        tmp = tempfile.mkdtemp()
        shutil.copy(src, tmp)
        md = os.path.join(tmp, os.path.basename(src))
        title = note or os.path.basename(stem).replace("_", " ").replace("-", " ").title()
        subprocess.run([sys.executable, os.path.join(HERE, "md2pdf.py"), md, title],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pdf = os.path.splitext(md)[0] + ".pdf"
        return pdf if os.path.exists(pdf) else None
    return src          # anything else (e.g. a .zip of code): copied as is


def main():
    cfg = load_config()
    check = "--check" in sys.argv
    rows = [r for r in read_index(cfg) if r["target"]]
    if not rows:
        print("Nothing to sync: no materials index with target folders yet "
              "(ask Claude to 'set up My Materials' / 建立 My Materials).")
        return
    updated, same, missing = [], 0, []
    from collections import Counter
    names = Counter((r["target"], os.path.splitext(os.path.basename(os.path.expanduser(r["source"])))[0]) for r in rows)
    for r in rows:
        src = os.path.expanduser(r["source"])
        if not os.path.isabs(src):
            src = os.path.join(cfg["materials_dir"], src)
        if not os.path.lexists(src):
            missing.append(f"{r['key']}: {r['source']}")
            continue
        src = resolve_alias(src)
        tgt = r["target"]
        dest_dir = industry_path(cfg, tgt.split(":", 1)[1]) if tgt.startswith("industry:") else jm_path(cfg, tgt)
        out_ext = ".pdf" if src.lower().endswith((".tex", ".md")) else os.path.splitext(src)[1]
        stem = os.path.splitext(os.path.basename(src))[0]
        if names[(tgt, stem)] > 1:      # e.g. three CV versions all called <Name>_CV.tex
            stem += "_" + r["key"]
        dest = os.path.join(dest_dir, stem + out_ext)
        if os.path.exists(dest) and os.path.getmtime(dest) >= os.path.getmtime(src):
            same += 1
            continue
        if check:
            updated.append(f"{r['key']} -> {os.path.relpath(dest, os.path.dirname(cfg['job_market_dir']))} (would update)")
            continue
        made = built_pdf(src, r["note"])
        if not made:
            missing.append(f"{r['key']}: could not build a PDF from {src}")
            continue
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy2(made, dest)
        os.utime(dest)          # newer than the master, so it is not copied again next time
        updated.append(f"{r['key']} -> {os.path.relpath(dest, os.path.dirname(cfg['job_market_dir']))}")
    print(f"{len(updated)} updated, {same} already current, {len(missing)} missing")
    for u in updated:
        print("  " + u)
    for m in missing:
        print("  MISSING " + m)
    if missing:
        print("Ask Claude to 'update the materials index' (更新材料索引) if you moved or renamed files.")


if __name__ == "__main__":
    main()
