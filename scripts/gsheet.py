"""Write the letter-request list into a native Google Sheet (optional; used by export_letter_list.py).

Needs `pip3 install gspread`, a Google service-account JSON key at config["google_credentials"],
and a Google Sheet (config["letter_share_gsheet"], its URL or id) shared with the service
account's client_email as Editor. Share the sheet with your writers as Editor too, so they can
fill in their status (Sent / Waiting) and Comments columns. What is entered in the hand-filled
columns (yours and theirs) is read back and kept on every refresh; the script never writes to
them. The columns filled from the tracker and the header rows are protected, so only you (the
owner) and the script can change them. Sharing settings and any protections you add yourself
are never touched.
"""
import datetime as dt
import os
import re

# Received is filled automatically when the mail check finds the system's confirmation
WRITER_CHOICES = [("Waiting", "FFEB9C", "9C5700"), ("Sent", "C6EFCE", "006100"), ("Received", "BDD7EE", "1F3864")]
LOCK_TRACKER = "Filled from the tracker (econ-job-market-kit)"
LOCK_HEADERS = "Column headers (econ-job-market-kit)"
HEADER_ROW = 3          # 1-based row of the column headers in the Google Sheet; positions start below it


def _sheet_id(s):
    m = re.search(r"/d/([A-Za-z0-9_-]+)", s)
    return m.group(1) if m else s.strip()


def _col(n):
    """1-based column number -> letter(s)."""
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _rgb(hexcolor):
    h = hexcolor.lstrip("#")
    return {k: int(h[i:i + 2], 16) / 255 for k, i in (("red", 0), ("green", 2), ("blue", 4))}


def _cell(v):
    if isinstance(v, dt.datetime):
        v = v.date()
    if isinstance(v, dt.date):
        return v.isoformat()          # USER_ENTERED parses ISO dates into real dates
    return "" if v is None else v


def row_keys(link, employer, position):
    """Keys that identify a position across refreshes: its link, and employer + position."""
    keys = []
    if link:
        keys.append("L:" + str(link).strip())
    if employer:
        keys.append("E:" + f"{employer}|{position or ''}".strip().lower())
    return keys


def _open(cfg):
    import warnings
    warnings.filterwarnings("ignore", module="google.*|urllib3.*")   # Python 3.9 / LibreSSL notices
    import gspread
    gc = gspread.service_account(filename=os.path.expanduser(cfg["google_credentials"]))
    book = gc.open_by_key(_sheet_id(cfg["letter_share_gsheet"]))
    return book, book.sheet1


def _header_row(vals):
    """0-based index of the column-header row (the one with "Employer"), or None."""
    return next((i for i, row in enumerate(vals[:6]) if "Employer" in row), None)


def read_writer_status(cfg, headers):
    """{row key: {header: value}} for the given hand-filled headers, from the sheet as it is now."""
    _, ws = _open(cfg)
    vals = ws.get_all_values()
    h = _header_row(vals)
    if h is None:
        return {}
    head = vals[h]
    col = {name: i for i, name in enumerate(head) if name}
    out = {}
    for row in vals[h + 1:]:
        row = row + [""] * (len(head) - len(row))
        got = {name: row[col[name]].strip() for name in headers if name in col and row[col[name]].strip()}
        if got:
            for k in row_keys(row[col["Link"]] if "Link" in col else "", row[col["Employer"]],
                              row[col["Position"]] if "Position" in col else ""):
                out[k] = got
    return out


def push_letter_list(cfg, title, note, cols, table, link_col, date_cols, status_col, status_colors,
                     hand_cols, hide, frozen_cols=0):
    """cols: [(header, xlsx width)]; table: list of row value lists; *_col(s): 1-based column numbers;
    status_colors: [(text, background hex, font hex)] for the status column;
    hand_cols: [(column, "status" | "comment", writer name or None for you)];
    frozen_cols: number of columns kept in view when scrolling right.

    Layout: row 1 holds the title (over the frozen columns) and the note beside it, row 2 is blank,
    row 3 has the headers and the positions start on row 4. The columns filled from the tracker are
    rewritten in full. The hand-filled columns (writers' status and comments) keep their formats and
    widths; only their values are written, so that what was typed moves with its position when the
    deadline order changes."""
    book, ws = _open(cfg)
    n_cols = len(cols)
    first_hand = min(c for c, *_ in hand_cols) - 1 if hand_cols else n_cols   # tracker columns: 0..first_hand-1
    head_r = HEADER_ROW - 1                                                     # 0-based
    n_rows = HEADER_ROW + max(len(table), 1)
    old = ws.get_all_values()
    old_h = _header_row(old)
    old_last = len(old) if old_h is not None else 0

    tracker_vals = [[h for h, _ in cols[:first_hand]]]
    for row in table:
        out = [_cell(v) for v in row[:first_hand]]
        url = str(out[link_col - 1]).replace('"', "%22")
        if url:
            out[link_col - 1] = f'=HYPERLINK("{url}", "{url}")'
        tracker_vals.append(out)
    if not table:
        tracker_vals.append(["No positions need letters yet."])
    # hand-filled values, realigned to the new row order; rows the list no longer reaches are blanked
    hand_vals = [[h for h, _ in cols[first_hand:]]] + [[_cell(v) for v in row[first_hand:]] for row in table]
    hand_vals += [[""] * (n_cols - first_hand)] * max(0, old_last - HEADER_ROW - len(table))

    writer_cols = [c for c, kind, _ in hand_cols if kind == "status"]
    title_end = frozen_cols or 3
    note_end = max(title_end + 1, min((c for c, kind, _ in hand_cols if kind == "comment"), default=n_cols + 1) - 1)

    # clear the tracker columns and row 1, and the rules this script added (status and writer colors);
    # anything else in the hand-filled columns stays; protected ranges are left alone (yours, and the
    # two this script keeps up to date below)
    meta = book.fetch_sheet_metadata({"includeGridData": False})
    sheet_meta = next(sh for sh in meta["sheets"] if sh["properties"]["sheetId"] == ws.id)
    ours = {status_col - 1, *(c - 1 for c in writer_cols)}
    reqs = [{"deleteConditionalFormatRule": {"sheetId": ws.id, "index": i}}
            for i, rule in reversed(list(enumerate(sheet_meta.get("conditionalFormats", []))))
            if any(r.get("startColumnIndex") in ours for r in rule.get("ranges", []))]
    reqs.append({"unmergeCells": {"range": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": 2}}})
    # freeze before merging row 1, since a merge may not cross the frozen columns
    reqs.append({"updateSheetProperties": {"properties": {"sheetId": ws.id, "gridProperties": {
        "frozenRowCount": HEADER_ROW, "frozenColumnCount": frozen_cols, "hideGridlines": True}},
        "fields": "gridProperties(frozenRowCount,frozenColumnCount,hideGridlines)"}})
    reqs.append({"updateCells": {"range": {"sheetId": ws.id, "startColumnIndex": 0, "endColumnIndex": first_hand},
                                 "fields": "*"}})
    reqs.append({"updateCells": {"range": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": 2}, "fields": "*"}})
    # English month names for the writers, whatever locale the owner's account created the sheet in
    reqs.append({"updateSpreadsheetProperties": {"properties": {"locale": "en_US"}, "fields": "locale"}})
    book.batch_update({"requests": reqs})
    ws.update_title("Letter Requests")
    ws.resize(rows=max(n_rows, old_last, 20), cols=max(n_cols, ws.col_count, 8))
    ws.batch_update([
        {"range": "A1", "values": [[title]]},
        {"range": f"{_col(title_end + 1)}1", "values": [[note]]},
        {"range": f"A{HEADER_ROW}", "values": tracker_vals},
    ], value_input_option="USER_ENTERED")
    if hand_cols:
        ws.update(hand_vals, f"{_col(first_hand + 1)}{HEADER_ROW}", value_input_option="RAW")

    accent = _rgb(cfg.get("accent_color", "0021A5"))
    font = {"fontFamily": "Arial", "fontSize": 10}
    rng = lambda r0, r1, c0, c1: {k: v for k, v in (("sheetId", ws.id), ("startRowIndex", r0), ("endRowIndex", r1),
                                                    ("startColumnIndex", c0), ("endColumnIndex", c1)) if v is not None}
    fmt = lambda r, f, fields: {"repeatCell": {"range": r, "cell": {"userEnteredFormat": f}, "fields": fields}}
    border = {"style": "SOLID", "color": _rgb("D0D0D0")}
    px = lambda c0, c1: sum(int(w * 7.5) for _, w in cols[c0:c1])
    lines = lambda text, per_char, width: -(-len(text or "") * per_char // width) or 1
    reqs = [
        {"mergeCells": {"range": rng(0, 1, 0, title_end), "mergeType": "MERGE_ALL"}},
        {"mergeCells": {"range": rng(0, 1, title_end, note_end), "mergeType": "MERGE_ALL"}},
        fmt(rng(0, 1, 0, 1), {"wrapStrategy": "WRAP", "verticalAlignment": "TOP",
                              "textFormat": {**font, "fontSize": 15, "bold": True, "foregroundColor": accent}},
            "userEnteredFormat(wrapStrategy,verticalAlignment,textFormat)"),
        fmt(rng(0, 1, title_end, title_end + 1), {"wrapStrategy": "WRAP", "verticalAlignment": "TOP",
                                                  "textFormat": {**font, "italic": True, "foregroundColor": _rgb("555555")}},
            "userEnteredFormat(wrapStrategy,verticalAlignment,textFormat)"),
        # Google does not size rows of merged cells: about 10 px per title character, 6 per note character
        {"updateDimensionProperties": {"range": {"sheetId": ws.id, "dimension": "ROWS", "startIndex": 0, "endIndex": 1},
                                       "properties": {"pixelSize": 6 + max(26 * lines(title, 10, px(0, title_end)),
                                                                           17 * lines(note, 6, px(title_end, note_end)))},
                                       "fields": "pixelSize"}},
        fmt(rng(head_r, head_r + 1, 0, n_cols), {"backgroundColor": accent, "horizontalAlignment": "CENTER",
                                                 "verticalAlignment": "TOP", "wrapStrategy": "WRAP",
                                                 "textFormat": {**font, "bold": True, "foregroundColor": _rgb("FFFFFF")}},
            "userEnteredFormat(backgroundColor,horizontalAlignment,verticalAlignment,wrapStrategy,textFormat)"),
        fmt(rng(head_r + 1, n_rows, 0, first_hand), {"verticalAlignment": "TOP", "wrapStrategy": "WRAP", "textFormat": font},
            "userEnteredFormat(verticalAlignment,wrapStrategy,textFormat)"),
        {"updateBorders": {"range": rng(head_r, n_rows, 0, first_hand), "top": border, "bottom": border, "left": border,
                           "right": border, "innerHorizontal": border, "innerVertical": border}},
    ]
    # centered columns: #, dates, status (as in the xlsx)
    for c in sorted({1, *date_cols, status_col}):
        reqs.append(fmt(rng(head_r + 1, n_rows, c - 1, c), {"horizontalAlignment": "CENTER"},
                        "userEnteredFormat.horizontalAlignment"))
    for c in date_cols:
        reqs.append(fmt(rng(head_r + 1, n_rows, c - 1, c), {"numberFormat": {"type": "DATE", "pattern": "mmm d, yyyy"}},
                        "userEnteredFormat.numberFormat"))
    for i, (h, w) in enumerate(cols[:first_hand]):
        reqs.append({"updateDimensionProperties": {
            "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i + 1},
            "properties": {"pixelSize": int(w * 7.5), "hiddenByUser": h in hide}, "fields": "pixelSize,hiddenByUser"}})

    def colors(c0, c1, choices):
        for text, bg, fg in choices:
            reqs.append({"addConditionalFormatRule": {"index": 0, "rule": {"ranges": [rng(head_r + 1, n_rows, c0, c1)], "booleanRule": {
                "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": text}]},
                "format": {"backgroundColor": _rgb(bg), "textFormat": {"foregroundColor": _rgb(fg)}}}}}})
    colors(status_col - 1, status_col, status_colors)

    for c in writer_cols:
        colors(c - 1, c, WRITER_CHOICES)
        reqs.append({"setDataValidation": {"range": rng(head_r + 1, n_rows, c - 1, c), "rule": {
            "condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": t} for t, *_ in WRITER_CHOICES]},
            "strict": True, "showCustomUi": True}}})

    # lock the columns filled from the tracker (everything left of the first hand-filled column) and
    # the header rows, so only you and the script can change them; writers keep their own columns
    mine = {p.get("description"): p for p in sheet_meta.get("protectedRanges", [])}
    me = book.client.auth.service_account_email   # Google requires the script itself to stay an editor
    for desc, r in ((LOCK_TRACKER, rng(None, None, 0, first_hand)), (LOCK_HEADERS, rng(0, HEADER_ROW, first_hand, None))):
        if desc in mine:
            reqs.append({"updateProtectedRange": {"protectedRange": {
                "protectedRangeId": mine[desc]["protectedRangeId"], "range": r}, "fields": "range"}})
        else:
            reqs.append({"addProtectedRange": {"protectedRange": {
                "range": r, "description": desc, "editors": {"users": [me]}}}})
    book.batch_update({"requests": reqs})
    return book.url
