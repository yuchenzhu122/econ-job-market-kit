"""Build a one-page academic cover letter PDF.

  python3 scripts/make_letter.py --employer "State University" --dept "Department of Economics" \
      --position "Assistant Professor of Economics" --variant research \
      --fit "Two to four sentences on why this department."

--variant research   research first, one page (research universities, policy schools)
--variant teaching   teaching first, up to two pages (liberal arts colleges, teaching-focused jobs)
--variant industry   industry jobs: kb opener, --body (flagship project + matching experience), --fit
                     ("why them"), kb closer; one page, to <industry dir>/<Employer> - <position>/
See skills/econ-cover-letter/templates.md for what each paragraph does.

Shared paragraphs come from My Materials/00-knowledge-base/10-cover-letter-kb.md (one "## <key>"
section per paragraph, plain text: & and quotes are escaped for you), and otherwise from
config.json ("cover_letter", written in LaTeX). Only --fit (and --body for industry) is new per
letter; --enclosures rewrites the closing's "I have enclosed ..." sentence to match what the
posting asks for.
Without --fit, a highlighted placeholder is inserted. Output: <job_market_dir>/<cover_letter_dir>/CL_<Employer>.pdf
"""
import argparse
import datetime as dt
import os
import re

from common import industry_path, jm_path, kb_sections, letterhead, load_config, run_pdflatex, tex_escape

ORDER = {
    "research": ["intro", "jmp", "other_research", "teaching", "fit", "closing"],
    "teaching": ["intro_teaching", "teaching_approach", "teaching_evidence", "research_brief", "fit", "closing_teaching"],
    "industry": ["industry_intro", "body", "fit", "industry_closing"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--employer", required=True)
    ap.add_argument("--dept", default="Department of Economics")
    ap.add_argument("--position", default="Assistant Professor")
    ap.add_argument("--variant", choices=list(ORDER), default="research")
    ap.add_argument("--fit", default="")
    ap.add_argument("--body", default="", help="industry: the job-specific middle paragraph(s); blank line = new paragraph")
    ap.add_argument("--out-dir", default="", help="where to write the letter (default: by variant)")
    ap.add_argument("--address", default="")
    ap.add_argument("--tag", default="", help="added to the file name when one employer has several letters")
    ap.add_argument("--enclosures", default="",
                    help='what is actually attached, e.g. "CV, job market paper, and teaching evaluations"; '
                         'replaces the "I have enclosed ..." sentence of the closing')
    a = ap.parse_args()
    cfg = load_config()

    fill = {"employer": tex_escape(a.employer), "dept": tex_escape(a.dept), "position": tex_escape(a.position),
            "letter_writers": cfg["letter_writers_sentence"]}
    fit = tex_escape(a.fit) if a.fit.strip() else (
        r"\colorbox{yellow}{[FIT PARAGRAPH: see templates.md --- courses, students, load, why this school.]}")
    paras = dict(cfg.get("cover_letter") or {})                                  # LaTeX already
    # plain text: escape it for LaTeX, but keep placeholders such as {letter_writers} intact
    paras.update({k: re.sub(r"\{([a-z\\_]+)\}", lambda m: "{" + m.group(1).replace("\\_", "_") + "}", tex_escape(v))
                  for k, v in kb_sections(cfg, "10-cover-letter-kb.md").items()})
    missing = [k for k in ORDER[a.variant] if k not in ("fit", "body") and k not in paras]
    if missing:
        raise SystemExit(f"10-cover-letter-kb.md (or config.json cover_letter) is missing {missing} "
                         f"(needed for --variant {a.variant})")
    if a.variant == "industry" and not a.body.strip():
        raise SystemExit("--variant industry needs --body (the job-specific middle paragraph).")
    middle = "\n\n".join(tex_escape(p.strip()) for p in a.body.split("\n\n") if p.strip())
    body = [fit if k == "fit" else middle if k == "body" else paras[k].format(**fill) for k in ORDER[a.variant]]
    if a.enclosures.strip():
        body[-1], n = re.subn(r"^I have enclosed [^.]*\.", lambda m: "I have enclosed my " + tex_escape(a.enclosures.strip()) + ".", body[-1])
        if not n:
            raise SystemExit("closing paragraph does not start with 'I have enclosed ...'; edit it by hand")
    ind = a.variant == "industry"
    recipient = (("Hiring Team\\\\\n" + fill["employer"]) if ind
                 else "Search Committee\\\\\n" + fill["dept"] + "\\\\\n" + fill["employer"])
    if a.address:
        recipient += "\\\\\n" + tex_escape(a.address)

    email = ((cfg.get("industry") or {}).get("email") if ind else None) or cfg["email"]   # optional job-search address
    tex = letterhead(cfg) + r"""\setlength{\parskip}{8pt}
\linespread{1.05}
\begin{document}
{\LARGE\bfseries """ + cfg["name"] + r"""}\hfill \href{mailto:""" + email + "}{" + email + r"""}\\[2pt]
""" + tex_escape(cfg["department"]) + ", " + tex_escape(cfg["city"]) + r"""\hfill \href{https://""" + cfg["website"] + "}{" + cfg["website"] + r"""}\\[-4pt]
{\color{accent}\rule{\textwidth}{0.6pt}}

""" + dt.date.today().strftime("%B %-d, %Y") + "\n\n" + recipient + r"""

""" + ("Dear Hiring Team," if ind else "Dear Members of the Search Committee,") + r"""

""" + "\n\n".join(body) + r"""

Sincerely,\\[4pt]
""" + cfg["name"] + "\n\\end{document}\n"

    if a.out_dir:
        out_dir = os.path.expanduser(a.out_dir)
    elif ind:
        out_dir = industry_path(cfg, re.sub(r'[/\\:*?"<>|]+', "-", f"{a.employer} - {a.position}").strip())
    else:
        out_dir = jm_path(cfg, cfg["cover_letter_dir"])
    os.makedirs(out_dir, exist_ok=True)
    stem = ("Cover_Letter_" if ind else "CL_") + re.sub(r"[^A-Za-z0-9]+", "_", a.employer + (" " + a.tag if a.tag else "")).strip("_")
    with open(os.path.join(out_dir, stem + ".tex"), "w", encoding="utf-8") as f:
        f.write(tex)
    print(run_pdflatex(out_dir, stem))


if __name__ == "__main__":
    main()
