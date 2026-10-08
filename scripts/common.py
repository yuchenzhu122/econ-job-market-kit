"""Shared helpers: load config.json from the repo root and resolve paths."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB = "00-knowledge-base"
INDEX = "materials-index.md"


def load_config():
    # ECON_KIT_CONFIG points at another config file (e.g. a test copy that writes to a scratch folder)
    path = os.environ.get("ECON_KIT_CONFIG") or os.path.join(ROOT, "config.json")
    if not os.path.exists(path):
        raise SystemExit("config.json not found. Copy config.example.json to config.json and fill it in.")
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["job_market_dir"] = os.path.expanduser(cfg["job_market_dir"])
    if cfg.get("materials_dir"):
        cfg["materials_dir"] = os.path.expanduser(cfg["materials_dir"])
    if cfg.get("industry", {}).get("dir"):
        cfg["industry"]["dir"] = os.path.expanduser(cfg["industry"]["dir"])
    return cfg


def jm_path(cfg, rel):
    """Absolute path inside the job market folder."""
    return os.path.join(cfg["job_market_dir"], rel)


def industry_path(cfg, rel=""):
    """Absolute path inside the industry folder (config "industry" -> "dir")."""
    ind = cfg.get("industry") or {}
    if not ind.get("dir"):
        raise SystemExit('No industry folder set: add "industry": {"dir": ...} to config.json (see config.example.json).')
    return os.path.join(ind["dir"], rel)


def tracker_path(cfg, kind="academic"):
    if kind == "industry":
        return industry_path(cfg, cfg["industry"].get("tracker_file", "08_Applications/Industry_Application_Tracker.xlsx"))
    return jm_path(cfg, cfg["tracker_file"])


def trackers(cfg):
    """[(kind, path)] for every tracker that exists: the academic one and, if set up, the industry one."""
    out = [("academic", tracker_path(cfg))]
    if (cfg.get("industry") or {}).get("dir"):
        out.append(("industry", tracker_path(cfg, "industry")))
    return [(k, p) for k, p in out if os.path.exists(p)]


def norm_link(url):
    """One form per posting, so the same job is recognized across boards, alerts and trackers."""
    if not url:
        return ""
    u = str(url).strip()
    m = re.search(r"linkedin\.com/(?:comm/)?jobs/view/(?:[^/?]*-)?(\d+)", u)
    if m:
        return "linkedin.com/jobs/view/" + m.group(1)
    m = re.search(r"indeed\.[a-z.]+/.*[?&](?:jk|vjk)=([0-9a-f]+)", u)
    if m:
        return "indeed.com/viewjob?jk=" + m.group(1)
    m = re.search(r"econjobs\.nabe\.com/job/(?:[^/?]+/)?(\d+)", u)
    if m:
        return "econjobs.nabe.com/job/" + m.group(1)
    u = re.sub(r"^https?://(www\.)?", "", u)
    u = re.sub(r"[?#].*$", "", u) if not re.search(r"[?&](JOE_ID|id|gh_jid|jobId|jk)=", u) else u
    return u.rstrip("/").lower()


# ---------------- My Materials: masters + knowledge base

def kb_path(cfg, name=""):
    """Path inside My Materials/00-knowledge-base (None if materials_dir is not set)."""
    if not cfg.get("materials_dir"):
        return None
    return os.path.join(cfg["materials_dir"], KB, name)


def resolve_alias(path):
    """Follow a symlink, or a Finder alias (Python does not follow those on its own)."""
    path = os.path.realpath(os.path.expanduser(path))
    if os.path.isfile(path) and os.path.getsize(path) < 20000:
        with open(path, "rb") as f:
            head = f.read(16)
        if head.startswith(b"book\x00\x00\x00\x00mark"):
            import subprocess
            r = subprocess.run(["osascript", "-e", f'tell application "Finder" to get POSIX path of '
                                f'(original item of (POSIX file "{path}" as alias) as alias)'],
                               capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip():
                return os.path.realpath(r.stdout.strip())
    return path


def read_index(cfg):
    """Rows of My Materials/00-knowledge-base/materials-index.md: [{key, source, target, note}].
    The index is a Markdown table | Key | Source | Target folder | Note |; Source is relative to
    My Materials (or absolute / ~); Target folder is relative to the job market folder ("" = not copied)."""
    p = kb_path(cfg, INDEX)
    if not p or not os.path.exists(p):
        return []
    rows = []
    for line in open(p, encoding="utf-8"):
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not line.lstrip().startswith("|") or set(cells[0]) <= set("-: ") or cells[0].lower() == "key":
            continue
        rows.append({"key": cells[0], "source": cells[1], "target": cells[2] if len(cells) > 2 else "",
                     "note": cells[3] if len(cells) > 3 else ""})
    return rows


def material_path(cfg, key, must_exist=True):
    """Absolute path of the master file registered under `key` in the materials index."""
    for row in read_index(cfg):
        if row["key"] == key and row["source"]:
            src = os.path.expanduser(row["source"])
            if not os.path.isabs(src):
                src = os.path.join(cfg["materials_dir"], src)
            if os.path.lexists(src):
                return resolve_alias(src)
            if must_exist:
                raise SystemExit(f"'{key}' is listed in {INDEX} as {row['source']}, but that file is gone. "
                                 "Ask Claude to 'update the materials index' (更新材料索引).")
            return None
    if must_exist:
        raise SystemExit(f"No '{key}' in {INDEX}. Ask Claude to 'update the materials index' (更新材料索引).")
    return None


def kb_sections(cfg, name):
    """{heading: text} for the '## heading' sections of a knowledge-base Markdown file."""
    p = kb_path(cfg, name)
    if not p or not os.path.exists(p):
        return {}
    out, cur = {}, None
    for line in open(p, encoding="utf-8"):
        m = re.match(r"##\s+(.+?)\s*$", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = ""
        elif cur and not line.lstrip().startswith("<!--"):
            out[cur] += line
    return {k: v.strip() for k, v in out.items() if v.strip()}


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
            "Letters?": "Yes/No", "Cover Letter": "Cover Letter", **{w: "Letter" for w in writers},
            # industry tracker only (missing lists are skipped)
            "Category": "Category", "Source": "Source", "Visa": "Visa", "Verdict": "Verdict",
            "Resume": "Resume", "Form Answers": "Form Answers"}
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


def excel_open_names():
    import subprocess
    if subprocess.run(["pgrep", "-x", "Microsoft Excel"], capture_output=True).returncode != 0:
        return ""
    r = subprocess.run(["osascript", "-e", 'tell application "Microsoft Excel" to get name of workbooks'],
                       capture_output=True, text=True)
    return r.stdout


def close_in_excel(path):
    """If Excel has the workbook open, save and close it. Returns True if it was open (reopen later
    with reopen_in_excel). Asks Excel directly; the ~$ lock file is unreliable."""
    import subprocess, time
    name = os.path.basename(path)
    was_open = name in excel_open_names()
    if was_open:
        r = subprocess.run(["osascript", "-e", f'tell application "Microsoft Excel" to close workbook "{name}" saving yes'],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"Could not ask Excel to save and close the tracker ({r.stderr.strip()}). "
                             "Save and close it yourself, then run this again.")
        for _ in range(40):
            if name not in excel_open_names():
                break
            time.sleep(0.25)
        else:
            raise SystemExit("Excel still has the tracker open. Save and close it, then run this again.")
    lock = os.path.join(os.path.dirname(path), "~$" + name)
    if os.path.exists(lock):
        try:
            os.remove(lock)
        except OSError:
            pass
    return was_open


def reopen_in_excel(path, was_open):
    import subprocess
    if was_open:
        subprocess.run(["open", path])


def tracker_headers(ws):
    return {ws.cell(row=4, column=c).value: c for c in range(1, ws.max_column + 1) if ws.cell(row=4, column=c).value}


def ensure_submitted_column(ws):
    """Add a 'Submitted' date column at the right edge of an older Tracker sheet. Returns its index."""
    return ensure_date_column(ws, "Submitted")


def ensure_text_column(ws, name, width=22):
    """Add a plain text column (e.g. 'Field') at the right edge of an older Tracker sheet if it is
    missing. Returns its index."""
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter as L
    H = tracker_headers(ws)
    if name in H:
        return H[name]
    col = max(H.values()) + 1
    src = ws.cell(row=4, column=H["Position"])
    c = ws.cell(row=4, column=col, value=name)
    c.font = Font(name=src.font.name, size=src.font.sz, bold=True, color=src.font.color.rgb if src.font.color else None)
    c.fill = PatternFill("solid", fgColor=src.fill.fgColor.rgb)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.column_dimensions[L(col)].width = width
    for r in range(5, 155):
        ws.cell(row=r, column=col).alignment = Alignment(wrap_text=True, vertical="top")
    return col


def ensure_date_column(ws, name):
    """Add a date column (e.g. 'Submitted', 'Letters Due') at the right edge of an older Tracker
    sheet if it is missing. Returns its index."""
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter as L
    from openpyxl.worksheet.datavalidation import DataValidation
    H = tracker_headers(ws)
    if name in H:
        return H[name]
    col = max(H.values()) + 1
    src = ws.cell(row=4, column=H["Deadline"])
    c = ws.cell(row=4, column=col, value=name)
    c.font = Font(name=src.font.name, size=src.font.sz, bold=True, color=src.font.color.rgb if src.font.color else None)
    c.fill = PatternFill("solid", fgColor=src.fill.fgColor.rgb)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.column_dimensions[L(col)].width = 12
    for name in ("_sort", "_order"):
        if name in H:
            ws.column_dimensions[L(H[name])].hidden = True
    for r in range(5, 155):
        ws.cell(row=r, column=col).number_format = "mmm d, yyyy"
    d = DataValidation(type="date", operator="greaterThan", formula1="DATE(2026,1,1)", allow_blank=True)
    d.error = "Enter a date, e.g. 11/15/2026."
    ws.add_data_validation(d)
    d.add(f"{L(col)}5:{L(col)}154")
    return col
