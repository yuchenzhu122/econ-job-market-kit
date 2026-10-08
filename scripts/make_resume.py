"""Build a tailored one-page resume for one job.

  python3 scripts/make_resume.py --employer "Amazon" --role "Economist I"
  python3 scripts/make_resume.py --employer "Amazon" --role "Economist I" --pages 2   (allow two pages)
  python3 scripts/make_resume.py --master                                            (build the master itself)

The master resume is the LaTeX folder registered as "resume" (its main.tex) in My Materials/
00-knowledge-base/materials-index.md. For a job, put only the sections that change in
  <industry dir>/_build/<id>/sections/<name>.tex      (usually objective.tex and skills.tex)
and optionally _build/<id>/main.tex to reorder sections. Everything else comes from the master,
so a fix to the master reaches every later build. <id> = "<Employer>-<Role>" in lower case
(printed by this script).

Output: <industry dir>/<Employer> - <Role>/<First>_<Last>_Resume_<Employer>.pdf, checked to be
exactly one page (or --pages). The build folder keeps the .tex files so the PDF can be rebuilt.
"""
import argparse
import os
import re
import shutil

from common import industry_path, load_config, material_path, run_pdflatex


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def safe(s):
    return re.sub(r'[/\\:*?"<>|]+', "-", s).strip()


def pages(pdf):
    try:
        from pypdf import PdfReader
        return len(PdfReader(pdf).pages)
    except ImportError:
        import zlib
        data = open(pdf, "rb").read()
        # page objects may sit inside compressed object streams (pdfTeX's default), so inflate those too
        for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
            try:
                data += zlib.decompress(m.group(1))
            except zlib.error:
                pass
        return len(re.findall(rb"/Type\s*/Page(?![s\w])", data))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--employer")
    ap.add_argument("--role")
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--master", action="store_true", help="build the master resume PDF next to its main.tex")
    a = ap.parse_args()
    cfg = load_config()
    master_dir = os.path.dirname(material_path(cfg, "resume"))

    if a.master:
        pdf = run_pdflatex(master_dir, "main")
        n = pages(pdf)
        print(f"master: {pdf} ({n} page{'s' * (n != 1)})")
        return
    if not (a.employer and a.role):
        ap.error("--employer and --role are required (or --master)")

    job = slug(f"{a.employer}-{a.role}")
    over = industry_path(cfg, os.path.join("_build", job))
    build = os.path.join(over, "build")
    if os.path.exists(build):
        shutil.rmtree(build)
    shutil.copytree(master_dir, build, ignore=shutil.ignore_patterns("*.pdf", "*.aux", "*.log", "*.out", "build"))
    used = []
    for root, _, files in os.walk(over):
        if root.startswith(build):
            continue
        for f in files:
            if f.endswith(".tex"):
                rel = os.path.relpath(os.path.join(root, f), over)
                os.makedirs(os.path.dirname(os.path.join(build, rel)), exist_ok=True)
                shutil.copy(os.path.join(root, f), os.path.join(build, rel))
                used.append(rel)
    pdf = run_pdflatex(build, "main")
    if not os.path.exists(pdf):
        raise SystemExit(f"LaTeX failed; run pdflatex in {build} to see the error.")
    n = pages(pdf)
    first, *rest = cfg["name"].split()
    out_dir = industry_path(cfg, safe(f"{a.employer} - {a.role}"))
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{first}_{(rest or [''])[-1]}_Resume_{safe(a.employer).replace(' ', '_')}.pdf")
    shutil.copy(pdf, out)
    print(f"id: {job}\ntailored sections: {', '.join(sorted(used)) or 'none (same as master)'}\n{out}")
    if n != a.pages:
        print(f"WARNING: {n} pages, expected {a.pages}. Shorten the tailored sections (or the master) and rebuild.")


if __name__ == "__main__":
    main()
