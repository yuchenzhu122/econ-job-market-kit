"""One-step tracker update, no Claude needed:
moves Leads rows marked Add into the Tracker, then refreshes the shared letter-writer file.

  python3 scripts/update_tracker.py

If Excel has the tracker open, it asks Excel to save and close it, updates it, and opens it
again (macOS asks once to let Terminal control Excel). It also puts a clickable
"Update Tracker" link at the top of the Tracker and Leads sheets that runs this script via
the "Update Tracker.command" file next to the tracker.
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


def lock_path(path):
    return os.path.join(os.path.dirname(path), "~$" + os.path.basename(path))


def excel_running():
    return subprocess.run(["pgrep", "-x", "Microsoft Excel"], capture_output=True).returncode == 0


def close_in_excel(path):
    """Save and close the workbook in Excel if it is open there. Returns True if it was open."""
    lock = lock_path(path)
    if not os.path.exists(lock):
        return False
    if not excel_running():                  # stale lock left by a crash or quit
        os.remove(lock)
        return False
    name = os.path.basename(path)
    script = (f'tell application "Microsoft Excel"\n'
              f'  if (exists workbook "{name}") then close workbook "{name}" saving yes\n'
              f'end tell')
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("Could not ask Excel to save and close the tracker "
                         f"({r.stderr.strip()}). Save and close it yourself, then run this again.")
    for _ in range(40):
        if not os.path.exists(lock):
            break
        time.sleep(0.25)
    if os.path.exists(lock) and excel_running():
        raise SystemExit("Excel still has the tracker open. Save and close it, then run this again.")
    return True


def add_buttons(path, command_file):
    wb = load_workbook(path)
    url = "file://" + urllib.parse.quote(command_file)
    for name, cell in (("Tracker", "H1"), ("Leads", "H1")):
        if name not in wb.sheetnames:
            continue
        c = wb[name][cell]
        if c.value != LABEL:
            c.value = LABEL
            c.hyperlink = url
            c.font = Font(name="Arial", size=11, bold=True, color="0563C1", underline="single")
    restore_dropdowns(wb, load_config()["letter_writers"])
    wb.save(path)


cfg = load_config()
tracker = jm_path(cfg, cfg["tracker_file"])
command_file = os.path.join(os.path.dirname(tracker), "Update Tracker.command")
was_open = close_in_excel(tracker)
moved = promote(cfg, tracker)
if os.path.exists(command_file):
    add_buttons(tracker, command_file)
subprocess.run([sys.executable, os.path.join(HERE, "export_letter_list.py")], check=True)
print(f"Done: {len(moved)} new row(s) in the Tracker; letter-writer file refreshed.")
if was_open:
    subprocess.run(["open", tracker])
