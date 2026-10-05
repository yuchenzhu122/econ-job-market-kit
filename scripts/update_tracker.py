"""One-step tracker update, no Claude needed:
moves Leads rows marked Add into the Tracker, then refreshes the shared letter-writer file.

  python3 scripts/update_tracker.py

If Excel has the tracker open, it asks Excel to save and close it, updates it, and opens it
again (macOS asks once to allow controlling Excel). It also puts a clickable
"Update Tracker" link at the top of the Tracker and Leads sheets that runs the macOS Shortcuts
shortcut named "Update Tracker" (a "Run Shell Script" action calling this script).
Apply Via and Letters? are guessed from the ad; ask Claude to "fill the tracker" for a full check.
"""
import os
import subprocess
import sys
import time
import urllib.parse

from openpyxl import load_workbook
from openpyxl.styles import Font

from common import jm_path, load_config, restore_dropdowns
from leads import promote

HERE = os.path.dirname(os.path.abspath(__file__))
LABEL = "▶ Update Tracker (click: moves Leads marked Add, refreshes the letter list)"
SHORTCUT = "Update Tracker"   # macOS Shortcuts shortcut that runs this script (Excel may open its URL)


def lock_path(path):
    return os.path.join(os.path.dirname(path), "~$" + os.path.basename(path))


def excel_running():
    return subprocess.run(["pgrep", "-x", "Microsoft Excel"], capture_output=True).returncode == 0


def open_in_excel(name):
    if not excel_running():
        return False
    r = subprocess.run(["osascript", "-e", 'tell application "Microsoft Excel" to get name of workbooks'],
                       capture_output=True, text=True)
    return name in r.stdout


def close_in_excel(path):
    """Save and close the workbook in Excel if it is open there. Returns True if it was open.
    Asks Excel directly; the ~$ lock file is unreliable (Excel leaves stale ones behind)."""
    name = os.path.basename(path)
    was_open = open_in_excel(name)
    if was_open:
        script = f'tell application "Microsoft Excel" to close workbook "{name}" saving yes'
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("Could not ask Excel to save and close the tracker "
                             f"({r.stderr.strip()}). Save and close it yourself, then run this again.")
        for _ in range(40):
            if not open_in_excel(name):
                break
            time.sleep(0.25)
        else:
            raise SystemExit("Excel still has the tracker open. Save and close it, then run this again.")
    lock = lock_path(path)
    if os.path.exists(lock):
        try:
            os.remove(lock)          # stale once the workbook is closed
        except OSError:
            pass
    return was_open


def add_buttons(path):
    """Excel's sandbox will not launch a .command file, but it may open a shortcuts:// URL."""
    wb = load_workbook(path)
    url = "shortcuts://run-shortcut?name=" + urllib.parse.quote(SHORTCUT)
    for name, cell in (("Tracker", "H1"), ("Leads", "H1")):
        if name not in wb.sheetnames:
            continue
        c = wb[name][cell]
        if c.value != LABEL or c.hyperlink is None or c.hyperlink.target != url:
            c.value = LABEL
            c.hyperlink = url
            c.font = Font(name="Arial", size=11, bold=True, color="0563C1", underline="single")
    restore_dropdowns(wb, load_config()["letter_writers"])
    wb.save(path)


cfg = load_config()
tracker = jm_path(cfg, cfg["tracker_file"])
was_open = close_in_excel(tracker)
moved = promote(cfg, tracker)
add_buttons(tracker)
subprocess.run([sys.executable, os.path.join(HERE, "export_letter_list.py")], check=True)
print(f"Done: {len(moved)} new row(s) in the Tracker; letter-writer file refreshed.")
if was_open:
    subprocess.run(["open", tracker])
