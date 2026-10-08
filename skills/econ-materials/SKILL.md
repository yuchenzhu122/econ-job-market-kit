---
name: econ-materials
description: Set up and maintain the user's "My Materials" folder (master CV, resume, papers, statements, plus a knowledge base about them) for the economics job market kit, build the user's personal versions of the kit's skills from it, and save useful information from chat into that knowledge base. Use when the user says "set up My Materials", "建立 My Materials", "检查我的材料", "review my CV / statement / resume", "帮我改 research statement", "update the materials index", "更新材料索引", "整理 Job Market 文件夹", "记下来", "save this to my knowledge base", "build my personal skills", "生成我的个人版 skill", "更新个人版", or mentions advice someone gave them, a contact or referral at a company, or a new experience, award or preference worth keeping.
---

# My Materials: masters + knowledge base

## Locate things

Repo: `readlink -f ~/.claude/skills/econ-materials`, up two levels. Read `<repo>/config.json`:
`materials_dir` (My Materials), `job_market_dir` (academic folder), `industry.dir`. Knowledge
base = `<materials_dir>/00-knowledge-base/`; templates for every file are in
`<repo>/templates/my_materials/` (README with what makes each master good) and
`<repo>/templates/resume/` (one-page LaTeX resume). Helpers in `<repo>/scripts/common.py`:
`read_index`, `material_path`, `kb_sections`.

The user maintains only My Materials. The academic and industry folders hold uploadable copies
(from `sync_materials.py`) and per-job files. Respect the user's own way of organizing files.

## A. Set up ("set up My Materials" / 建立 My Materials)

1. **Look first.** List `materials_dir` (may not exist), the academic folder and its subfolders,
   and where the user's masters already live (ask if unknown; e.g. a website repo with
   `materials/research/*_CV.tex`). Read `08_Applications/Application_Info.md` if present and
   `config.json` → `cover_letter`, `profile`.
2. **Create** `materials_dir` with `README.md` and `00-knowledge-base/` copied from the templates
   (`cp -R`); never overwrite a file that exists.
3. **Index.** Build `materials-index.md`: one row per master (key, source, target folder, note).
   Keep masters where they are: point Source at the original path, or offer to put a Finder alias
   / symlink in My Materials if the user prefers. Use keys `cv`, `jmp`, `resume` for those three
   (the scripts look them up); others free-form (`research_statement`, `teaching_statement`,
   `wp_<short>`, `teaching_evals`, ...).
4. **The academic folder.** If it already holds material files: show a table "file → suggested
   folder" using the suggested layout (`01_CV/ 02_Job_Market_Paper/ 03_Working_Papers/
   04_Work_in_Progress/ 05_Teaching/ 06_Website/ 07_Statements/`), and move nothing until the
   user agrees or edits it; they may keep their own layout. If it holds none: ask which
   categories they want (not necessarily these), create those folders. Write the chosen folders
   into the index's Target column, then run `python3 <repo>/scripts/sync_materials.py` and report.
   Leave `08_Applications/` and `09_Cover_Letters/` alone.
5. **Knowledge base.** Fill the 00–12 files from the CV, statements, papers' abstracts,
   Application_Info.md and config.json: facts only, every number copied exactly. Move the
   `cover_letter` paragraphs into `10-cover-letter-kb.md` (one `## key` per paragraph, plain text:
   turn ``x'' into "x"; keep `{position}` etc.). Write industry-voice bullets in `02`/`03` and
   the summaries in `08` as drafts marked `<!-- draft: check -->`. Ask the user for what only they
   know (do-not-claim list in `06`, work-authorization wording, preferred name, locations).
   Copy `15-market-wisdom.md` from the template if missing.
6. **Resume master** (if none): copy `<repo>/templates/resume/` to where the user wants it in
   My Materials, fill it from the knowledge base (one page; projects with numbers), register its
   `main.tex` as `resume`, build with `python3 <repo>/scripts/make_resume.py --master`, check it is
   one page, and show it.
7. Report: what was found, what was indexed, what is missing (with one line each on how to write
   it), and the drafts to check.

## B. Review ("检查我的材料", "review my research statement")

Read the file(s) and the matching section of `<repo>/templates/my_materials/README.md`. Give
specific, ranked suggestions (quote the line, say what to change and why: length, order, numbers,
clarity for the audience, consistency with the CV and other files). Also check consistency across
masters (dates, titles, JMP findings, numbers). Change files only when the user agrees; edit the
master, never a copy in the job market folders.

## C. Save to the knowledge base ("记下来", or in any chat)

Whenever the user mentions something worth keeping (advice from a person, a contact or
referral, interview format at an employer, a salary data point, a new paper / talk / award /
course, a preference or a do-not-claim skill), add it without being asked, then say in one line
where it went:
- advice from someone → `13-advice.md` (row: date, who and where, advice, applies to)
- about a specific company or school → `14-employers.md` (dated bullet under its heading)
- facts about the user → the matching 00–12 file
- public information (forum posts, articles) → `15-market-wisdom.md` with source link and A/B/C
Append; never delete or rewrite earlier entries (mark outdated ones `[过时]`). Dates absolute.
If `materials_dir` is not set up yet, offer to set it up first.

## D. Update the index ("更新材料索引")

Scan My Materials (and the sources the index points to); for rows whose file moved, find it by
name and update Source; list new master-looking files and ask whether to add them; then run
`sync_materials.py --check` and report.

## E. Personal skill versions ("build my personal skills" / 生成我的个人版 skill)

The skills in the repo are generic and shared on GitHub. Each one starts by reading the user's
personal version, `00-knowledge-base/skills/<skill-name>.md`, which lives only in My Materials
(never in the repo, never committed). Build one per skill from the knowledge base, using the
template `<repo>/templates/my_materials/00-knowledge-base/skills/_template.md`:

- econ-job-scan, econ-industry-scan: what counts as High / Medium / Low for this user (fields,
  methods, kinds of employers in priority order, locations, visa constraints, deal-breakers),
  from `00-personal-info.md`, `08-summaries.md`, `06-skills.md`, `13-advice.md`, config `profile`.
- econ-cover-letter, econ-industry-apply: which project leads for which kind of job, the
  one-line positioning and other wording the user or their advisors insist on (`13-advice.md`),
  facts never to use, tone, length habits.
- econ-tracker-fill, econ-mail-check: personal conventions (e.g. which mailboxes, which
  confirmation senders, how to treat certain systems).
Each rule cites its source file or the date the user said it. Show the drafts and write them
after the user agrees. Later, when the user corrects how a skill behaves ("以后…"), append the rule
to that skill's file (dated) rather than editing the generic SKILL.md. Rebuild a file when the
knowledge base changes a lot ("更新个人版").

## Rules

- Never invent facts or numbers; never copy content from other people's materials.
- Never move, rename or delete the user's files without their OK.
- No passwords, ID numbers or EEO answers in the knowledge base.
- Personal material (knowledge base, personal skill versions, config.json) stays out of the repo;
  never copy it into `<repo>/skills/` or `<repo>/templates/`, which are generic and public.
