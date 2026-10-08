"""Build a one-page academic cover letter PDF.

  python3 scripts/make_letter.py --employer "State University" --dept "Department of Economics" \
      --position "Assistant Professor of Economics" --variant research \
      --fit "Two to four sentences on why this department."

--variant research   research first, one page (research universities, policy schools)
--variant teaching   teaching first, up to two pages (liberal arts colleges, teaching-focused jobs)
See skills/econ-cover-letter/templates.md for what each paragraph does.

Shared paragraphs come from config.json ("cover_letter"); only --fit (and --enclosures, to match
the materials the posting asks for) changes per letter.
Without --fit, a highlighted placeholder is inserted. Output: <job_market_dir>/<cover_letter_dir>/CL_<Employer>.pdf
"""
import argparse
import datetime as dt
import os
import re

from common import jm_path, letterhead, load_config, run_pdflatex, tex_escape

ORDER = {
    "research": ["intro", "jmp", "other_research", "teaching", "fit", "closing"],
    "teaching": ["intro_teaching", "teaching_approach", "teaching_evidence", "research_brief", "fit", "closing_teaching"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--employer", required=True)
    ap.add_argument("--dept", default="Department of Economics")
    ap.add_argument("--position", default="Assistant Professor")
    ap.add_argument("--variant", choices=list(ORDER), default="research")
    ap.add_argument("--fit", default="")
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
    paras = cfg["cover_letter"]
    missing = [k for k in ORDER[a.variant] if k != "fit" and k not in paras]
    if missing:
        raise SystemExit(f"config.json cover_letter is missing {missing} (needed for --variant {a.variant})")
    body = [fit if k == "fit" else paras[k].format(**fill) for k in ORDER[a.variant]]
    if a.enclosures.strip():
        body[-1], n = re.subn(r"^I have enclosed [^.]*\.", lambda m: "I have enclosed my " + tex_escape(a.enclosures.strip()) + ".", body[-1])
        if not n:
            raise SystemExit("closing paragraph does not start with 'I have enclosed ...'; edit it by hand")
    recipient = "Search Committee\\\\\n" + fill["dept"] + "\\\\\n" + fill["employer"]
    if a.address:
        recipient += "\\\\\n" + tex_escape(a.address)

    tex = letterhead(cfg) + r"""\setlength{\parskip}{8pt}
\linespread{1.05}
\begin{document}
{\LARGE\bfseries """ + cfg["name"] + r"""}\hfill \href{mailto:""" + cfg["email"] + "}{" + cfg["email"] + r"""}\\[2pt]
""" + tex_escape(cfg["department"]) + ", " + tex_escape(cfg["city"]) + r"""\hfill \href{https://""" + cfg["website"] + "}{" + cfg["website"] + r"""}\\[-4pt]
{\color{accent}\rule{\textwidth}{0.6pt}}

""" + dt.date.today().strftime("%B %-d, %Y") + "\n\n" + recipient + r"""

Dear Members of the Search Committee,

""" + "\n\n".join(body) + r"""

Sincerely,\\[4pt]
""" + cfg["name"] + "\n\\end{document}\n"

    out_dir = jm_path(cfg, cfg["cover_letter_dir"])
    os.makedirs(out_dir, exist_ok=True)
    stem = "CL_" + re.sub(r"[^A-Za-z0-9]+", "_", a.employer + (" " + a.tag if a.tag else "")).strip("_")
    with open(os.path.join(out_dir, stem + ".tex"), "w", encoding="utf-8") as f:
        f.write(tex)
    print(run_pdflatex(out_dir, stem))


if __name__ == "__main__":
    main()
