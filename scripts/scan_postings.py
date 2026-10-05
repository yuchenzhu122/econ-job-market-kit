"""Pull new academic/policy postings from JOE and EconJobMarket and pre-filter them.

  python3 scripts/scan_postings.py            # writes <job_market_dir>/08_Applications/scan_new.json
  python3 scripts/scan_postings.py --all      # ignore the 'already seen' list (for testing)

Sources (both public, machine-readable):
  JOE: the AEA's XML export of current listings
  EJM: EconJobMarket's public JSON feed of ads

Rule-based pre-filter (settings in config.json "scan"): section / position type, rank
(drops senior-only and postdoc/visiting), field (JEL prefixes, categories, keywords),
deadline not passed, not already seen, not already in the tracker. What survives is
written to scan_new.json for Claude to read in full and judge fit (see skills/econ-job-scan).
"""
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.request

from openpyxl import load_workbook

from common import jm_path, load_config

UA = {"User-Agent": "Mozilla/5.0 (econ-job-market-kit scanner)"}
JOE_LIST = "https://www.aeaweb.org/joe/listings"
EJM_JSON = "https://backend.econjobmarket.org/data/zz_public/json/Ads"

JUNIOR = re.compile(r"assistant prof|lecturer|instructor|teaching|tenure[- ]track|open rank|economist|"
                    r"research (?:associate|fellow|scientist)|policy|analyst|all ranks|any rank", re.I)
EXCLUDE = re.compile(r"post-?doc|visiting|pre-?doc|research assistant|phd (?:student|position|fellowship)|"
                     r"doctoral (?:student|fellowship)|adjunct|part-time|dean|chair\b|director|head of", re.I)


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8", errors="ignore")


def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()


def joe_postings():
    page = fetch(JOE_LIST)
    m = re.search(r'href="(/joe/resultset_output\.php\?mode=full_xml[^"]*)"', page)
    if not m:
        raise RuntimeError("JOE export link not found")
    xml = fetch("https://www.aeaweb.org" + html.unescape(m.group(1)))
    out = []
    for p in re.findall(r"<position jp_id=\"(\d+)\">(.*?)</position>", xml, re.S):
        jid, body = p
        g = lambda t: clean((re.search(rf"<{t}>(.*?)</{t}>", body, re.S) or [None, ""])[1])
        countries = re.findall(r"<country>(.*?)</country>", body)
        cities = re.findall(r"<city>(.*?)</city>", body)
        out.append({
            "source": "JOE", "id": "JOE-" + jid,
            "url": f"https://www.aeaweb.org/joe/listing.php?JOE_ID=",  # completed below
            "jid": jid, "section": g("jp_section"), "title": g("jp_title"),
            "employer": g("jp_institution"), "department": " / ".join(x for x in (g("jp_division"), g("jp_department")) if x),
            "location": ", ".join(x for x in (clean(cities[0]) if cities else "", clean(countries[0]) if countries else "") if x),
            "deadline": g("jp_application_deadline")[:10],
            "fields": [c for c in re.findall(r"<jc_code>(.*?)</jc_code>", body)],
            "field_names": [clean(c) for c in re.findall(r"<jc_description>(.*?)</jc_description>", body)],
            "text": g("jp_full_text"),
        })
    # JOE listing URLs need the issue id; the listings page lists JOE_IDs ending in _<jp_id>
    ids = dict((i.split("_")[-1], i) for i in re.findall(r"JOE_ID=([\w-]+)", page))
    for x in out:
        x["url"] = ("https://www.aeaweb.org/joe/listing.php?JOE_ID=" + ids[x["jid"]]) if x["jid"] in ids else \
            "https://www.aeaweb.org/joe/listings (search: " + x["employer"] + ")"
    return out


def ejm_postings():
    out = []
    for a in json.loads(fetch(EJM_JSON)):
        loc = (a.get("locations") or [{}])[0] or {}
        out.append({
            "source": "EJM", "id": "EJM-" + a["url"].rstrip("/").split("/")[-1], "url": a["url"],
            "section": "; ".join(t["name"] for t in a.get("position_types") or []),
            "title": clean(a.get("adtitle")), "employer": clean(a.get("name")),
            "department": clean(a.get("department")),
            "location": ", ".join(x for x in (loc.get("city"), loc.get("country_code")) if x),
            "deadline": (a.get("deadline_date") or a.get("enddate") or "")[:10],
            "end": (a.get("enddate") or "")[:10],
            "fields": [], "field_names": [c["name"] for c in a.get("categories") or []],
            "text": clean(a.get("adtext")),
        })
    return out


def keep(x, sc, today):
    why = []
    if x["source"] == "JOE":
        if x["section"] not in sc["joe_sections"]:
            return False, "section"
    else:
        types = [t.strip() for t in x["section"].split(";")]
        if not any(t in sc["ejm_position_types"] for t in types):
            return False, "type"
        if x.get("end") and x["end"] < today:
            return False, "expired"
    head = x["title"] + " " + x["section"]
    if EXCLUDE.search(x["title"]) and not re.search(r"assistant prof|lecturer", x["title"], re.I):
        return False, "rank"
    if not JUNIOR.search(head) and "Assistant Professor" not in x["section"] and "Lecturer" not in x["section"]:
        return False, "rank"
    if x["deadline"] and x["deadline"] < today and x["source"] == "JOE":
        return False, "deadline"
    text = (x["text"] + " " + " ".join(x["field_names"]) + " " + x["title"]).lower()
    field_ok = (any(f.startswith(tuple(sc["field_jel_prefixes"])) for f in x["fields"])
                or any(c in sc["ejm_categories"] for c in x["field_names"])
                or any(k in text for k in sc["field_keywords"]))
    if not field_ok:
        return False, "field"
    return True, ""


def main():
    cfg = load_config()
    sc = cfg["scan"]
    apps = jm_path(cfg, os.path.dirname(cfg["tracker_file"]))
    state_path = os.path.join(apps, "scan_state.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {"seen": []}
    seen = set() if "--all" in sys.argv else set(state["seen"])

    tracked = set()
    tracker = jm_path(cfg, cfg["tracker_file"])
    if os.path.exists(tracker):
        wb = load_workbook(tracker, read_only=True)
        for name in ("Tracker", "Leads"):
            if name in wb.sheetnames:
                for row in wb[name].iter_rows(values_only=True):
                    for v in row:
                        if isinstance(v, str) and v.startswith("http"):
                            tracked.add(v.strip())

    today = dt.date.today().isoformat()
    posts, errors = [], []
    for name, fn in (("JOE", joe_postings), ("EJM", ejm_postings)):
        try:
            posts += fn()
        except Exception as e:  # keep going if one source is down
            errors.append(f"{name}: {e}")

    stats, new = {}, []
    for x in posts:
        if x["id"] in seen or x["url"] in tracked:
            stats["seen"] = stats.get("seen", 0) + 1
            continue
        ok, reason = keep(x, sc, today)
        if ok:
            x["text"] = x["text"][:5000]
            x.pop("jid", None); x.pop("end", None)
            new.append(x)
        else:
            stats[reason] = stats.get(reason, 0) + 1

    # the same job is often posted on both JOE and EJM: keep one, remember the other link
    def key(x):
        emp = re.sub(r"[^a-z]", "", x["employer"].lower().replace("university", "").replace("the", ""))[:20]
        ttl = " ".join(re.findall(r"[a-z]+", x["title"].lower())[:3])
        return emp + "|" + ttl
    merged = {}
    for x in new:
        k = key(x)
        if k in merged:
            merged[k].setdefault("also_at", []).append(x["url"])
            stats["duplicate"] = stats.get("duplicate", 0) + 1
        else:
            merged[k] = x
    new = sorted(merged.values(), key=lambda x: x["deadline"] or "9999")
    for x in new:
        x["summary"] = x["text"][:1200]

    out_path = os.path.join(apps, "scan_new.json")
    json.dump({"date": today, "errors": errors, "filtered_out": stats, "candidates": new},
              open(out_path, "w"), indent=1, ensure_ascii=False)
    # remember everything we looked at, so the next run only shows new postings
    state["seen"] = sorted(set(state["seen"]) | {x["id"] for x in posts})
    state["last_run"] = today
    json.dump(state, open(state_path, "w"))
    print(f"{len(posts)} postings fetched, {len(new)} new candidates -> {out_path}")
    print("filtered out:", stats, "| errors:", errors or "none")


if __name__ == "__main__":
    main()
