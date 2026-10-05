"""Manage the Leads sheet of the tracker.

  python3 scripts/leads.py add <evaluated.json>   append evaluated postings to the Leads sheet
  python3 scripts/leads.py promote                 copy Leads rows with Decision = Add into Tracker

evaluated.json is a list of objects with keys:
  id, url, source, employer, position, track, type, location, deadline (YYYY-MM-DD or ""),
  fit (High | Medium | Low), why, flags, also_at (optional list of other links)

Leads columns: Found, Fit, Employer, Position, Track, Type, Location, Deadline, Why, Flags,
Source, Link, Decision (Add / Maybe / Pass; "Added" once promoted).
"""
import datetime as dt
import json
import sys

from openpyxl import load_workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

from common import jm_path, load_config

COLS = [("Found", 11), ("Fit", 8), ("Employer", 26), ("Position", 30), ("Track", 12), ("Type", 15),
        ("Location", 16), ("Deadline", 11), ("Why", 44), ("Flags", 26), ("Source", 7), ("Link", 22),
        ("Decision", 10)]
FONT = "Arial"
side = Side(style="thin", color="D0D0D0")
BD = Border(left=side, right=side, top=side, bottom=side)
FIT_ORDER = {"High": 0, "Medium": 1, "Low": 2}


def ensure_sheet(wb, accent):
    if "Leads" in wb.sheetnames:
        return wb["Leads"]
    ws = wb.create_sheet("Leads", 2)
    ws["A1"] = "Leads · found automatically on JOE, EconJobMarket, Chronicle and Inside Higher Ed"
    ws["A1"].font = Font(name=FONT, size=15, bold=True, color=accent)
    ws["A2"] = ("Pick a Decision for each row: Add = move it to the Tracker (ask Claude 'add my leads to the "
                "tracker'), Maybe = keep, Pass = ignore. Fit is Claude's judgment against your CV; check the Why and Flags.")
    ws["A2"].font = Font(name=FONT, size=10, italic=True, color="555555")
    for i, (h, w) in enumerate(COLS, start=1):
        c = ws.cell(row=4, column=i, value=h)
        c.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=accent)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BD
        ws.column_dimensions[L(i)].width = w
    dv = DataValidation(type="list", formula1='"Add,Maybe,Pass,Added"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"M5:M2000")
    for val, fill, color in (("High", "C6EFCE", "006100"), ("Medium", "FFEB9C", "9C5700"), ("Low", "EDEDED", "7F7F7F")):
        ws.conditional_formatting.add("B5:B2000", FormulaRule(formula=[f'$B5="{val}"'],
                                      fill=PatternFill("solid", fgColor=fill), font=Font(name=FONT, color=color, bold=True)))
    for val, fill in (("Add", "BDD7EE"), ("Added", "D9D9D9"), ("Pass", "F2F2F2")):
        ws.conditional_formatting.add("M5:M2000", FormulaRule(formula=[f'$M5="{val}"'], fill=PatternFill("solid", fgColor=fill)))
    ws.freeze_panes = "C5"
    ws.auto_filter.ref = "A4:M2000"
    ws.sheet_view.showGridLines = False
    return ws


def add(cfg, path, items):
    wb = load_workbook(path)
    ws = ensure_sheet(wb, cfg.get("accent_color", "0021A5"))
    have = {ws.cell(row=r, column=12).value for r in range(5, ws.max_row + 1)}
    items = [x for x in items if x.get("url") not in have]
    items.sort(key=lambda x: (FIT_ORDER.get(x.get("fit"), 3), x.get("deadline") or "9999"))
    r = max(5, ws.max_row + 1)
    while r > 5 and ws.cell(row=r - 1, column=3).value in (None, ""):
        r -= 1
    today = dt.date.today()
    for x in items:
        dl = None
        if x.get("deadline"):
            try:
                dl = dt.date.fromisoformat(x["deadline"][:10])
            except ValueError:
                dl = None
        flags = x.get("flags") or ""
        if x.get("also_at"):
            flags = (flags + "; " if flags else "") + "also posted at " + ", ".join(x["also_at"])
        vals = [today, x.get("fit"), x.get("employer"), x.get("position"), x.get("track"), x.get("type"),
                x.get("location"), dl, x.get("why"), flags, x.get("source"), x.get("url"), None]
        for i, v in enumerate(vals, start=1):
            c = ws.cell(row=r, column=i, value=v)
            c.font = Font(name=FONT, size=10)
            c.border = BD
            c.alignment = Alignment(wrap_text=True, vertical="top",
                                    horizontal="center" if i in (1, 2, 5, 8, 11, 13) else None)
        ws.cell(row=r, column=1).number_format = "mmm d"
        ws.cell(row=r, column=8).number_format = "mmm d, yyyy"
        if x.get("url"):
            ws.cell(row=r, column=12).hyperlink = x["url"]
            ws.cell(row=r, column=12).font = Font(name=FONT, size=10, color="0563C1", underline="single")
        r += 1
    wb.save(path)
    print(f"added {len(items)} lead(s) to {path}")


def promote(cfg, path):
    wb = load_workbook(path)
    if "Leads" not in wb.sheetnames:
        raise SystemExit("No Leads sheet yet.")
    lead, tr = wb["Leads"], wb["Tracker"]
    H = {tr.cell(row=4, column=c).value: c for c in range(1, tr.max_column + 1) if tr.cell(row=4, column=c).value}
    nxt = 5
    while tr.cell(row=nxt, column=H["Employer"]).value not in (None, ""):
        nxt += 1
    moved = []
    type_map = {"Tenure-track": "Tenure-track", "Teaching-focused": "Teaching-focused",
                "Fed / Central bank": "Fed / Central bank", "Government": "Government",
                "Think tank / Research": "Think tank / Research"}
    for r in range(5, lead.max_row + 1):
        if lead.cell(row=r, column=13).value != "Add":
            continue
        g = lambda c: lead.cell(row=r, column=c).value
        row = {"Track": g(5), "Employer": g(3), "Position": g(4), "Type": type_map.get(g(6), "Other"),
               "Link": g(12), "Deadline": g(8), "Status": "Not started",
               "Cover Letter": "To write", "Notes": f"From scan ({g(2)} fit): {g(9) or ''} {g(10) or ''}".strip()}
        for h, v in row.items():
            if h in H:
                tr.cell(row=nxt, column=H[h], value=v)
        if g(12):
            tr.cell(row=nxt, column=H["Link"]).hyperlink = g(12)
        lead.cell(row=r, column=13, value="Added")
        moved.append(g(3))
        nxt += 1
    wb.save(path)
    print(f"promoted {len(moved)}: {moved}")


if __name__ == "__main__":
    cfg = load_config()
    tracker = jm_path(cfg, cfg["tracker_file"])
    if len(sys.argv) >= 3 and sys.argv[1] == "add":
        add(cfg, tracker, json.load(open(sys.argv[2], encoding="utf-8")))
    elif len(sys.argv) >= 2 and sys.argv[1] == "promote":
        promote(cfg, tracker)
    else:
        print(__doc__)
