# My Materials

The one folder you maintain. Every cover letter, tailored resume and form answer is written from
what is here; the job market folders only hold copies and per-job files generated from it.

- `00-knowledge-base/`: facts about you, in small Markdown files (the only fixed folder name).
  `materials-index.md` says where each master file is and where its uploadable copy goes.
- Everything else: organize it your way. Keep files where they already live (for example your
  website repo) and point the index at them, or drop a Finder alias / symlink here.

Ask Claude: "检查我的材料" (review my materials) for suggestions on any file, "记下来" (save this)
to add advice or employer notes to the knowledge base, "更新材料索引" (update the materials index)
after moving files.

## Suggested layout for the academic folder (Job Market 2026-27)

Uploadable copies, filled by `scripts/sync_materials.py`. Rename, merge or drop any of these:

```
01_CV/  02_Job_Market_Paper/  03_Working_Papers/  04_Work_in_Progress/
05_Teaching/  06_Website/  07_Statements/  08_Applications/ (tracker)  09_Cover_Letters/
```

## What makes each master good

**Academic CV** (2+ pages is fine): contact; fields; education with expected date and committee;
job market paper first with a 3–4 line abstract and link; other papers by status; teaching (instructor of
record above TA), with evaluation scores; presentations; awards; skills; references with emails.
Reverse chronological; no photo; one consistent date format.

**Industry resume** (exactly one page; master in LaTeX, see `templates/resume/`): two-line
objective; education; experience and research written as projects with numbers ("built a
3,000-firm panel...", "estimated...", "found..."); skills only from `06-skills.md`. No abstract-style
paragraphs, no paper list, no jargon without a plain-words gloss.

**Job market paper**: an abstract a non-specialist can follow, a first page that states the
question, the answer and why it matters, and a link that always points to the latest version.

**Research statement** (2–3 pages): agenda in one paragraph; each paper as question, approach,
finding; a concrete pipeline of next projects.

**Teaching statement** (1–2 pages): philosophy through specific practices, evidence (scores
against department means, comments), courses you can teach, an example of something you changed.

**Diversity statement** (when asked, 1 page): concrete actions, not values alone.

**Cover letter paragraphs** (`10-cover-letter-kb.md`): written once, reused; only the fit
paragraph changes per letter.

**Knowledge base**: each fact once, in the file where it belongs; bullets with numbers in
`02-experience.md` and `03-projects.md`; a strict do-not-claim list in `06-skills.md`.
