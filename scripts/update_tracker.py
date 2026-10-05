"""One-step tracker update, no Claude needed:
moves Leads rows marked Add into the Tracker, then refreshes the shared letter-writer file.

  python3 scripts/update_tracker.py

Refuses to touch the workbook while Excel has it open (it would overwrite your unsaved edits).
Apply Via and Letters? are guessed from the ad; ask Claude to "fill the tracker" for a full check.
"""
import os
import subprocess
import sys

from common import jm_path, load_config
from leads import promote

HERE = os.path.dirname(os.path.abspath(__file__))


def excel_has_it_open(path):
    lock = os.path.join(os.path.dirname(path), "~$" + os.path.basename(path))
    if not os.path.exists(lock):
        return False
    running = subprocess.run(["pgrep", "-x", "Microsoft Excel"], capture_output=True).returncode == 0
    if not running:          # stale lock left by a crash or quit
        try:
            os.remove(lock)
        except OSError:
            pass
        return False
    return True


cfg = load_config()
tracker = jm_path(cfg, cfg["tracker_file"])
if excel_has_it_open(tracker):
    print("The tracker is open in Excel. Save it (Cmd+S), close it, and run this again.")
    sys.exit(1)
moved = promote(cfg, tracker)
subprocess.run([sys.executable, os.path.join(HERE, "export_letter_list.py")], check=True)
print(f"Done: {len(moved)} new row(s) in the Tracker; letter-writer file refreshed.")
