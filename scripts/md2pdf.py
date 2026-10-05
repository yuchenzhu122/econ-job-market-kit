"""Turn a statement written in Markdown into a PDF with your letterhead.

  python3 scripts/md2pdf.py statement.md "Research Statement" [references.tex]

Supports '## Section' headings, '- ' bullets, **bold**, [links](url) (printed as text).
A first-level '# Title' line and a byline starting with your name are dropped.
Writes <statement>.tex and <statement>.pdf next to the Markdown file.
"""
import os
import re
import sys

from common import letterhead, load_config, run_pdflatex

src, title = sys.argv[1], sys.argv[2]
refs = open(sys.argv[3], encoding="utf-8").read() if len(sys.argv) > 3 else ""
cfg = load_config()


def inline(s):
    s = s.replace("\\", "\\textbackslash{}")
    for c in "&%$#_":
        s = s.replace(c, "\\" + c)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = s.replace("’", "'").replace("“", "``").replace("”", "''")
    return re.sub(r'"(\S)', r"``\1", s).replace('"', "''")


out, in_list = [], False
for line in open(src, encoding="utf-8").read().split("\n"):
    if line.startswith("# ") or line.startswith(cfg["name"] + " ·"):
        continue
    if line.startswith("## "):
        if in_list:
            out.append("\\end{itemize}"); in_list = False
        out.append("\\section*{" + inline(line[3:]) + "}")
    elif line.startswith("- "):
        if not in_list:
            out.append("\\begin{itemize}\\setlength{\\itemsep}{3pt}\\setlength{\\parskip}{0pt}"); in_list = True
        out.append("\\item " + inline(line[2:]))
    else:
        if in_list and line.strip():
            out.append("\\end{itemize}"); in_list = False
        out.append(inline(line))
if in_list:
    out.append("\\end{itemize}")

tex = letterhead(cfg) + r"""\setlength{\parskip}{7pt}
\linespread{1.08}
\makeatletter
\renewcommand\section{\@startsection{section}{1}{0pt}{12pt}{4pt}{\normalfont\large\bfseries\scshape\raggedright\hyphenpenalty=10000}}
\makeatother
\begin{document}
\begin{center}
{\LARGE\bfseries """ + title + r"""}\\[4pt]
""" + cfg["name"] + r""" \quad\textperiodcentered{}\quad """ + inline(cfg["department"]) + r""" \quad\textperiodcentered{}\quad \href{mailto:""" + cfg["email"] + "}{" + cfg["email"] + r"""}\\[2pt]
{\color{accent}\rule{\textwidth}{0.6pt}}
\end{center}
\vspace{-6pt}
""" + "\n".join(out).strip() + "\n\n" + refs + "\n\\end{document}\n"

workdir = os.path.dirname(os.path.abspath(src))
stem = os.path.splitext(os.path.basename(src))[0]
with open(os.path.join(workdir, stem + ".tex"), "w", encoding="utf-8") as f:
    f.write(tex)
print(run_pdflatex(workdir, stem))
