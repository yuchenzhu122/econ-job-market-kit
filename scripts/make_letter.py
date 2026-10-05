"""Build a one-page academic cover letter PDF.

  python3 scripts/make_letter.py --employer "State University" --dept "Department of Economics" \
      --position "Assistant Professor of Economics" --variant research \
      --fit "Two to four sentences on why this department."

--variant research   research first (research universities, policy schools)
--variant teaching   teaching first (liberal arts colleges, teaching-focused jobs)

Shared paragraphs come from config.json ("cover_letter"); only --fit is new per letter.
Without --fit, a highlighted placeholder is inserted. Output: <job_market_dir>/<cover_letter_dir>/CL_<Employer>.pdf
"""
import argparse
import datetime as dt
import os
import re

from common import jm_path, letterhead, load_config, run_pdflatex, tex_escape

ORDER = {
    "research": ["intro", "jmp", "other_research", "teaching", "fit", "closing"],
    "teaching": ["intro", "teaching", "jmp", "other_research", "fit", "closing"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--employer", required=True)
    ap.add_argument("--dept", default="Department of Economics")
    ap.add_argument("--position", default="Assistant Professor")
    ap.add_argument("--variant", choices=list(ORDER), default="research")
    ap.add_argument("--fit", default="")
    ap.add_argument("--address", default="")
    a = ap.parse_args()
    cfg = load_config()

    fill = {"employer": tex_escape(a.employer), "dept": tex_escape(a.dept), "position": tex_escape(a.position),
            "letter_writers": cfg["letter_writers_sentence"]}
    fit = tex_escape(a.fit) if a.fit.strip() else (
        r"\colorbox{yellow}{[FIT PARAGRAPH: 2--4 sentences on why this department --- fields, centers, courses.]}")
    paras = cfg["cover_letter"]
    body = [fit if k == "fit" else paras[k].format(**fill) for k in ORDER[a.variant]]
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
    stem = "CL_" + re.sub(r"[^A-Za-z0-9]+", "_", a.employer).strip("_")
    with open(os.path.join(out_dir, stem + ".tex"), "w", encoding="utf-8") as f:
        f.write(tex)
    print(run_pdflatex(out_dir, stem))


if __name__ == "__main__":
    main()
