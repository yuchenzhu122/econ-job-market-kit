"""Shared helpers: load config.json from the repo root and resolve paths."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    path = os.path.join(ROOT, "config.json")
    if not os.path.exists(path):
        raise SystemExit("config.json not found. Copy config.example.json to config.json and fill it in.")
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["job_market_dir"] = os.path.expanduser(cfg["job_market_dir"])
    return cfg


def jm_path(cfg, rel):
    """Absolute path inside the job market folder."""
    return os.path.join(cfg["job_market_dir"], rel)


def tex_escape(s):
    import re
    for a, b in (("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_")):
        s = s.replace(a, b)
    s = s.replace("’", "'").replace("“", "``").replace("”", "''")
    return re.sub(r'"(\S)', r"``\1", s).replace('"', "''")


def run_pdflatex(workdir, stem):
    import subprocess
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", stem + ".tex"], cwd=workdir,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for ext in (".aux", ".log", ".out"):
        p = os.path.join(workdir, stem + ext)
        if os.path.exists(p):
            os.remove(p)
    return os.path.join(workdir, stem + ".pdf")


def letterhead(cfg):
    """LaTeX preamble + header shared by the cover letter and statements."""
    return r"""\documentclass[11pt]{article}
\usepackage[letterpaper,margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{mathptmx}
\usepackage[dvipsnames]{xcolor}
\usepackage[hidelinks]{hyperref}
\definecolor{accent}{HTML}{""" + cfg.get("accent_color", "0021A5") + r"""}
\pagestyle{empty}
\setlength{\parindent}{0pt}
"""


def restore_dropdowns(wb, writers):
    """Excel re-saves the Tracker's cross-sheet dropdowns in an extension format openpyxl drops on
    load. Call before saving the workbook with openpyxl to put the dropdowns back."""
    from openpyxl.utils import get_column_letter as L
    from openpyxl.worksheet.datavalidation import DataValidation
    tr, li = wb["Tracker"], wb["Lists"]
    have = {str(c) for v in tr.data_validations.dataValidation for c in v.sqref.ranges}
    lists = {li.cell(row=3, column=c).value: L(c) for c in range(1, li.max_column + 1) if li.cell(row=3, column=c).value}
    H = {tr.cell(row=4, column=c).value: L(c) for c in range(1, tr.max_column + 1) if tr.cell(row=4, column=c).value}
    want = {"Track": "Track", "Type": "Type", "Apply Via": "Platform", "Status": "Status",
            "Letters?": "Yes/No", "Cover Letter": "Cover Letter", **{w: "Letter" for w in writers}}
    last = max(154, tr.max_row)
    for head, name in want.items():
        if head not in H or name not in lists:
            continue
        rng = f"{H[head]}5:{H[head]}{last}"
        if any(r.startswith(H[head] + "5:") for r in have):
            continue
        col = lists[name]
        v = DataValidation(type="list", formula1=f"=Lists!${col}$4:${col}$30", allow_blank=True)
        tr.add_data_validation(v)
        v.add(rng)
