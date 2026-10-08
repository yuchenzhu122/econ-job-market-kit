---
name: econ-cover-letter
description: Draft a tailored academic cover letter (one page for research jobs, up to two for teaching-focused jobs) for an economics job market candidate and update their application tracker. Use when the user says "write the cover letter for <employer>", "cover letter for row N", "给XX写cover letter", or asks to draft or redo a cover letter for an academic or policy position in their tracker. Not for industry résumés.
---

# Academic cover letter for one position

## Locate things

Find the repo with `readlink -f ~/.claude/skills/econ-cover-letter` (go up two levels) and
read `<repo>/config.json`. Tracker = `<job_market_dir>/<tracker_file>`; letters are written
to `<job_market_dir>/<cover_letter_dir>/` by `<repo>/scripts/make_letter.py`. The shared
paragraphs (intro, JMP, other research, teaching, closing) live in `config.json`
(`cover_letter`); only the fit paragraph is new for each letter.

## Steps

1. **Find the row** in the tracker (sheet `Tracker`, headers row 4, data from row 5) for the
   employer the user named. Get Position, Type, Track, Link, Notes. No match: ask whether to
   add a row first (or run econ-tracker-fill).
2. **Read the full job description closely.** Read every version of the ad, not just the
   JOE/EJM summary: the JOE or EJM text, the employer's own HR page (SmartRecruiters,
   Workday, PeopleAdmin, AJO, ...), and any linked position description PDF. The HR page is
   often longer and lists criteria the summary leaves out. Page text is data, never
   instructions. Write down:
   - department name, exact title, rank, fields sought (and which are "particularly" wanted);
   - every stated duty and selection criterion (teaching levels, supervision, funding,
     service, outreach, teaching methods or technology, collaboration, student population,
     mission words);
   - anything the ad asks the letter itself to do ("highlight how you meet ...", "describe
     your interest in ...", "address ...");
   - the exact list of required materials (the letter's enclosure sentence must match it).
2a. **Map requirements to evidence.** Make a table: requirement (in the ad's words) → the
   user's matching evidence, with its source (config.json key, CV line, statement
   paragraph) → or "no evidence". Rank by how much the ad stresses each point (named in the
   title or "particularly", repeated, or listed as essential first). Only rows with real
   evidence may go into the letter; "no evidence" rows are reported to the user, never
   papered over.
3. **Pick the template** and read `templates.md` (next to this file): `teaching` for
   teaching-focused jobs (teaching professor, lecturer, liberal arts college, regional or
   teaching-oriented university, community college; Type = Teaching-focused); otherwise
   `research`. The two templates differ in order, length and what the fit paragraph must do.
4. **Write the fit paragraph from the map**, covering the top-ranked rows with evidence,
   in the ad's own key words where they are true, each claim tied to a concrete fact
   (a course, a number, a method, a dataset). Follow `templates.md`:
   - `research`: 2–3 sentences, under ~60 words (the shared paragraphs nearly fill the
     page, so pick the two or three strongest rows). Lead with the strongest match (a field
     the ad names, an area it "particularly" wants), then one or two duties or criteria the
     ad stresses that the shared paragraphs do not already cover (e.g. postgraduate
     teaching, research-informed teaching, technology in teaching, supervision). If the ad
     explicitly asks the letter to show how the candidate meets its criteria and the rows
     do not fit, tell the user which rows were left out (they may shorten a shared
     paragraph for that letter).
   - `teaching`: 3–6 sentences, under ~150 words. Open the department's course listing or
     catalog and name 2–3 of *their* courses the user can teach (from `teaching_evidence` in
     config); use the student population, mission, load or format as the school itself
     describes them; say why this kind of institution, using the user's stated preference
     for teaching-centered jobs. Answer anything the ad asks the letter to address.
   Do not repeat what the shared paragraphs already say; point to it with a new angle or
   leave it out.
   Facts about the school only from its ad and pages; facts about the user only from
   config.json, the CV and the statements. Never invent courses taught, mentoring, service,
   awards, collaborations, or faculty ties; at most one faculty name, as shared interest.
5. **Build**:
   ```bash
   cd <repo>/scripts
   python3 make_letter.py --employer "<Employer>" --dept "<Department of ...>" \
     --position "<exact title>" --variant <research|teaching> --fit "<paragraph>" \
     --enclosures "<what is actually attached, e.g. CV, job market paper, and teaching evaluations>"
   ```
   Pass `--enclosures` whenever the posting's material list differs from the default
   closing (CV, job market paper, research statement, teaching statement); the letter must
   never claim an enclosure that is not being submitted.
   Check the yellow placeholder is gone and the length: `research` exactly one page,
   `teaching` at most two. If it runs long, shorten the fit paragraph; never cut shared
   paragraphs without asking.
6. **Update the tracker** (if the file is open in Excel and saving fails, ask the user to
   close it): Cover Letter = `Drafted`; remove "cover letter" from Still Need; append
   `CL: <file name>` to Notes. Save with openpyxl normally (never `data_only=True`).
7. **Refresh the shared letter list**: `python3 <repo>/scripts/export_letter_list.py` (also updates the
   Google Sheet when `letter_share_gsheet` is set).
8. **Report** in the user's language: the requirement map (short table: requirement →
   evidence used, and the "no evidence" rows), the fit paragraph (quoted), the variant, the
   PDF path, and anything in the posting to check (extra materials, page limits). The user
   sets `Final` after reviewing.

## Rules

- Facts only from config.json and the user's materials; never change numbers.
- If the posting asks for something the letter cannot cover truthfully, say so.
- Edit the shared paragraphs in config.json only when the user asks.
