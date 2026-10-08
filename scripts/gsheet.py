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


def _sheet_id(s):
    m = re.search(r"/d/([A-Za-z0-9_-]+)", s)
    return m.group(1) if m else s.strip()


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


def read_writer_status(cfg, headers):
    """{row key: {header: value}} for the given hand-filled headers, from the sheet as it is now."""
    _, ws = _open(cfg)
    vals = ws.get_all_values()
    if len(vals) < 4:
        return {}
    head = vals[3]
    col = {h: i for i, h in enumerate(head) if h}
    if "Employer" not in col:
        return {}
    out = {}
    for row in vals[4:]:
        row = row + [""] * (len(head) - len(row))
        got = {h: row[col[h]].strip() for h in headers if h in col and row[col[h]].strip()}
        if got:
            for k in row_keys(row[col["Link"]] if "Link" in col else "", row[col["Employer"]],
                              row[col["Position"]] if "Position" in col else ""):
                out[k] = got
    return out


def push_letter_list(cfg, title, note, cols, table, link_col, date_cols, status_col, status_colors,
                     hand_cols, hide):
    """cols: [(header, xlsx width)]; table: list of row value lists; *_col(s): 1-based column numbers;
    status_colors: [(text, background hex, font hex)] for the status column;
    hand_cols: [(column, "status" | "comment", writer name or None for you)]."""
    book, ws = _open(cfg)
    n_cols, n_rows = len(cols), 4 + max(len(table), 1)

    values = [[title], [note], [], [h for h, _ in cols]]
    for row in table:
        out = [_cell(v) for v in row]
        url = str(out[link_col - 1]).replace('"', "%22")
        if url:
            out[link_col - 1] = f'=HYPERLINK("{url}", "{url}")'
        values.append(out)
    if not table:
        values.append(["No positions need letters yet."])

    # clear values, formats, validation and old conditional rules so reruns start fresh; protected
    # ranges are left alone (yours, and the two this script keeps up to date below)
    meta = book.fetch_sheet_metadata({"includeGridData": False})
    sheet_meta = next(s for s in meta["sheets"] if s["properties"]["sheetId"] == ws.id)
    reqs = [{"deleteConditionalFormatRule": {"sheetId": ws.id, "index": 0}}
            for _ in sheet_meta.get("conditionalFormats", [])]
    reqs.append({"updateCells": {"range": {"sheetId": ws.id}, "fields": "*"}})
    # English month names for the writers, whatever locale the owner's account created the sheet in
    reqs.append({"updateSpreadsheetProperties": {"properties": {"locale": "en_US"}, "fields": "locale"}})
    reqs.append({"updateDimensionProperties": {"range": {"sheetId": ws.id, "dimension": "COLUMNS"},
                                               "properties": {"hiddenByUser": False}, "fields": "hiddenByUser"}})
    book.batch_update({"requests": reqs})
    ws.update_title("Letter Requests")
    ws.resize(rows=max(n_rows, 20), cols=max(n_cols, 8))
    ws.update(values, "A1", value_input_option="USER_ENTERED")

    accent = _rgb(cfg.get("accent_color", "0021A5"))
    font = {"fontFamily": "Arial", "fontSize": 10}
    rng = lambda r0, r1, c0, c1: {k: v for k, v in (("sheetId", ws.id), ("startRowIndex", r0), ("endRowIndex", r1),
                                                    ("startColumnIndex", c0), ("endColumnIndex", c1)) if v is not None}
    fmt = lambda r, f, fields: {"repeatCell": {"range": r, "cell": {"userEnteredFormat": f}, "fields": fields}}
    border = {"style": "SOLID", "color": _rgb("D0D0D0")}
    reqs = [
        fmt(rng(0, 1, 0, 1), {"textFormat": {**font, "fontSize": 15, "bold": True, "foregroundColor": accent}},
            "userEnteredFormat.textFormat"),
        fmt(rng(1, 2, 0, 1), {"textFormat": {**font, "italic": True, "foregroundColor": _rgb("555555")}},
            "userEnteredFormat.textFormat"),
        fmt(rng(3, 4, 0, n_cols), {"backgroundColor": accent, "horizontalAlignment": "CENTER",
                                   "verticalAlignment": "TOP", "wrapStrategy": "WRAP",
                                   "textFormat": {**font, "bold": True, "foregroundColor": _rgb("FFFFFF")}},
            "userEnteredFormat(backgroundColor,horizontalAlignment,verticalAlignment,wrapStrategy,textFormat)"),
        fmt(rng(4, n_rows, 0, n_cols), {"verticalAlignment": "TOP", "wrapStrategy": "WRAP", "textFormat": font},
            "userEnteredFormat(verticalAlignment,wrapStrategy,textFormat)"),
        {"updateBorders": {"range": rng(3, n_rows, 0, n_cols), "top": border, "bottom": border, "left": border,
                           "right": border, "innerHorizontal": border, "innerVertical": border}},
        {"updateSheetProperties": {"properties": {"sheetId": ws.id, "gridProperties": {
            "frozenRowCount": 4, "hideGridlines": True}},
            "fields": "gridProperties(frozenRowCount,hideGridlines)"}},
    ]
    writer_cols = [c for c, kind, _ in hand_cols if kind == "status"]
    # centered columns: #, dates, status, writers (as in the xlsx)
    for c in sorted({1, *date_cols, status_col, *writer_cols}):
        reqs.append(fmt(rng(4, n_rows, c - 1, c), {"horizontalAlignment": "CENTER"},
                        "userEnteredFormat.horizontalAlignment"))
    for c in date_cols:
        reqs.append(fmt(rng(4, n_rows, c - 1, c), {"numberFormat": {"type": "DATE", "pattern": "mmm d, yyyy"}},
                        "userEnteredFormat.numberFormat"))
    for i, (h, w) in enumerate(cols):
        props = {"pixelSize": int(w * 7.5), "hiddenByUser": h in hide}
        reqs.append({"updateDimensionProperties": {
            "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i + 1},
            "properties": props, "fields": "pixelSize,hiddenByUser"}})

    def colors(c0, c1, choices):
        for text, bg, fg in choices:
            reqs.append({"addConditionalFormatRule": {"index": 0, "rule": {"ranges": [rng(4, n_rows, c0, c1)], "booleanRule": {
                "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": text}]},
                "format": {"backgroundColor": _rgb(bg), "textFormat": {"foregroundColor": _rgb(fg)}}}}}})
    colors(status_col - 1, status_col, status_colors)

    for c in writer_cols:
        colors(c - 1, c, WRITER_CHOICES)
        reqs.append({"setDataValidation": {"range": rng(4, n_rows, c - 1, c), "rule": {
            "condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": t} for t, *_ in WRITER_CHOICES]},
            "strict": True, "showCustomUi": True}}})

    # lock the columns filled from the tracker (everything left of the first hand-filled column) and
    # the header rows, so only you and the script can change them; writers keep their own columns
    first_hand = min(c for c, *_ in hand_cols) - 1 if hand_cols else n_cols
    mine = {p.get("description"): p for p in sheet_meta.get("protectedRanges", [])}
    me = book.client.auth.service_account_email   # Google requires the script itself to stay an editor
    for desc, r in ((LOCK_TRACKER, rng(None, None, 0, first_hand)), (LOCK_HEADERS, rng(0, 4, first_hand, None))):
        if desc in mine:
            reqs.append({"updateProtectedRange": {"protectedRange": {
                "protectedRangeId": mine[desc]["protectedRangeId"], "range": r}, "fields": "range"}})
        else:
            reqs.append({"addProtectedRange": {"protectedRange": {
                "range": r, "description": desc, "editors": {"users": [me]}}}})
    book.batch_update({"requests": reqs})
    return book.url
