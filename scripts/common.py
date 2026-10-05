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
