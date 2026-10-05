"""Export a shareable letter-request list from the tracker.

  python3 scripts/export_letter_list.py

Reads the Tracker sheet, keeps rows with Letters? = Yes (skipping Withdrawn/Rejected), sorts them by deadline, and writes a
separate, read-only-style workbook to config["letter_share_file"] (e.g. a file in OneDrive or
Google Drive). Share that file's link once with your letter writers; re-running this script
overwrites the same file, so the link keeps working and always shows the latest list.
Only the columns writers need are copied: no notes, no application status.
"""
import datetime as dt
import os

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L

from common import jm_path, load_config

cfg = load_config()
src = jm_path(cfg, cfg["tracker_file"])
dst = os.path.expanduser(cfg["letter_share_file"])
writers = cfg["letter_writers"]

ws = load_workbook(src, data_only=False)["Tracker"]
hdr = {ws.cell(row=4, column=c).value: c for c in range(1, ws.max_column + 1) if ws.cell(row=4, column=c).value}
need = ["Employer", "Position", "Apply Via", "Link", "Deadline", "Letters?"] + writers
missing = [h for h in need if h not in hdr]
if missing:
    raise SystemExit(f"Tracker is missing columns: {missing}")

rows = []
for r in range(5, ws.max_row + 1):
    get = lambda h: ws.cell(row=r, column=hdr[h]).value
    emp = get("Employer")
    if not emp or str(emp).startswith("EXAMPLE") or str(get("Letters?")).strip() != "Yes":
        continue
    if "Status" in hdr and str(get("Status")).strip() in ("Withdrawn", "Rejected"):
        continue
    d = get("Deadline")
    if isinstance(d, dt.datetime):
        d = d.date()
    rows.append({"Deadline": d, "Employer": emp, "Position": get("Position"), "Apply Via": get("Apply Via"),
                 "Link": get("Link"), **{w: get(w) or "" for w in writers}})
rows.sort(key=lambda x: x["Deadline"] or dt.date(2099, 12, 31))

FONT = "Arial"
accent = cfg.get("accent_color", "0021A5")
fb = Font(name=FONT, size=10)
fh = Font(name=FONT, size=10, bold=True, color="FFFFFF")
side = Side(style="thin", color="D0D0D0")
bd = Border(left=side, right=side, top=side, bottom=side)
wrap = Alignment(wrap_text=True, vertical="top")
ctr = Alignment(horizontal="center", vertical="top", wrap_text=True)

wb = Workbook()
sh = wb.active
sh.title = "Letter Requests"
sh["A1"] = f"Recommendation Letter Requests · {cfg['name']} · {cfg.get('season', '').replace('-', '–')}"
sh["A1"].font = Font(name=FONT, size=15, bold=True, color=accent)
sh["A2"] = (f"Positions that need a letter, soonest deadline first. Last updated "
            f"{dt.date.today().strftime('%B %-d, %Y')}. Thank you for your support!")
sh["A2"].font = Font(name=FONT, size=10, italic=True, color="555555")
# no formulas: the file is mostly viewed in a browser preview (Dropbox/OneDrive), which does not
# recalculate them, so a "Days Left" formula would show up blank
cols = [("#", 5), ("Deadline", 13), ("Employer", 30), ("Position", 32),
        ("Submit Letter Via", 20), ("Link", 30)] + [(w, 13) for w in writers]
for i, (h, w) in enumerate(cols, start=1):
    c = sh.cell(row=4, column=i, value=h)
    c.font = fh; c.fill = PatternFill("solid", fgColor=accent); c.alignment = ctr; c.border = bd
    sh.column_dimensions[L(i)].width = w
for k, x in enumerate(rows, start=1):
    r = 4 + k
    vals = [k, x["Deadline"], x["Employer"], x["Position"], x["Apply Via"], x["Link"]] + [x[w] for w in writers]
    for i, v in enumerate(vals, start=1):
        c = sh.cell(row=r, column=i, value=v)
        c.font = fb; c.border = bd
        c.alignment = ctr if i in (1, 2) or i > 6 else wrap
    sh.cell(row=r, column=2).number_format = "mmm d, yyyy"
    if x["Link"]:
        sh.cell(row=r, column=6).hyperlink = x["Link"]
        sh.cell(row=r, column=6).font = Font(name=FONT, size=10, color="0563C1", underline="single")
if not rows:
    sh["A5"] = "No positions need letters yet."
    sh["A5"].font = fb
last = 4 + max(len(rows), 1)
w1, w2 = L(7), L(6 + len(writers))
sh.conditional_formatting.add(f"{w1}5:{w2}{last}", FormulaRule(
    formula=[f'{w1}5="Uploaded"'], fill=PatternFill("solid", fgColor="C6EFCE"), font=Font(name=FONT, color="006100")))
sh.conditional_formatting.add(f"{w1}5:{w2}{last}", FormulaRule(
    formula=[f'{w1}5="Requested"'], fill=PatternFill("solid", fgColor="FFEB9C"), font=Font(name=FONT, color="9C5700")))
sh.freeze_panes = "A5"
sh.sheet_view.showGridLines = False
sh.protection.sheet = True          # view-only by default; no password, so you can still unprotect locally
os.makedirs(os.path.dirname(dst), exist_ok=True)
wb.save(dst)
print(f"{len(rows)} position(s) -> {dst}")
