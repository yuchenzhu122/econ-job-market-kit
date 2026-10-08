# econ-job-market-kit

A small toolkit for the economics job market, built to work with Claude Code. It covers two
markets that need different materials:

- **Academic** (universities, liberal arts colleges, policy institutions, central banks): finds
  postings twice a week, tracks every application, writes a research or teaching-focused cover
  letter per position from your own paragraphs, and keeps your letter writers' list up to date.
- **Industry** (economist roles in tech, economic consulting, pricing and marketplace, economic
  research and finance): finds postings in your LinkedIn / Indeed job alerts, on NABE's job board
  and on JOE, and for each company and role writes a tailored one-page resume, cover letter and
  application-form answers, following the per-job workflow of
  [dayuan-wang/job-hunt-helper](https://github.com/dayuan-wang/job-hunt-helper) and the advice
  collected in your knowledge base (including NABE's).

Both are written from one folder you maintain, **My Materials** (your master files plus a
knowledge base about you), and jobs from either side that need recommendation letters go on one
shared list for your writers.

[中文说明见下方](#中文说明)

## What's inside

**Shared**

| | |
|---|---|
| `scripts/build_tracker.py` | Builds an Excel tracker: the academic one, or with `--industry` the industry one. One row per job, deadline countdown, Submitted date, a column per letter writer, a Leads sheet and a summary tab. Trackers stay private; writers only see the Letter Requests list. |
| `scripts/leads.py` | Adds rated postings to a tracker's **Leads** sheet and moves the ones you mark Add into its Tracker. Checks every tracker first: a job already in the other tracker is flagged and never added twice. |
| `scripts/update_tracker.py` | One step, no Claude needed: moves Leads marked Add into both trackers, refreshes the letter-writer list and syncs your materials. Works while Excel has a tracker open. Also runs from a **▶ Update Tracker** link in the sheets. |
| `scripts/export_letter_list.py` | Builds the list your letter writers see from both trackers (see [Letter writers' list](#letter-writers-list-academic-and-industry)). |
| `scripts/mail_scan.py` | Optional. Reads recent mail through the Mail app already signed in on your Mac (no passwords) for application confirmations and letter notifications, for both trackers. |
| `scripts/sync_materials.py` | Copies the newest version of each master in My Materials (PDF, Word, or a PDF compiled from .tex / .md) into the folders you chose. Never deletes your files. |
| `skills/econ-materials` | Sets up My Materials, reviews your CV / statements / resume, builds your personal version of each skill, and saves advice and employer notes from chat. |
| `skills/econ-mail-check` | Optional: records Submitted dates and letters Received from confirmation emails. |
| `templates/` | Knowledge-base files (00–15, including public advice for econ PhDs with sources), the My Materials guide, and the LaTeX resume. |

**Academic**

| | |
|---|---|
| `scripts/scan_postings.py` | Pulls postings from JOE, EconJobMarket, IMF, World Bank, Chronicle Jobs and Inside Higher Ed Careers; filters by rank, field, deadline and section. Consulting and tech jobs on JOE are passed to the industry side. |
| `scripts/make_letter.py` | Builds a cover letter PDF in the `research` (one page) or `teaching` (up to two pages) template from your paragraphs in the knowledge base; only the fit paragraph is new per school. |
| `scripts/md2pdf.py` | Converts a Markdown research or teaching statement into a PDF with the same letterhead. |
| `skills/econ-job-scan` | Runs the scan, rates postings against your profile, writes the academic Leads sheet. |
| `skills/econ-tracker-fill` | Reads the links in your tracker and fills employer, position, deadline, letters due, where to apply, extra materials. |
| `skills/econ-cover-letter` | Picks the template, reads the ad and the department's pages, writes the fit paragraph, builds the PDF. |

**Industry**

| | |
|---|---|
| `scripts/industry_scan.py` | Reads your LinkedIn / Indeed job-alert emails, NABE EconJobs postings read in the browser (`--board-file`), and optionally company career pages; filters titles by your directions. |
| `scripts/nabe_jobs.js` | Read-only browser script that lists every job on NABE's EconJobs board (the site blocks scripts, so Claude runs it in its built-in browser). |
| `scripts/make_resume.py` | Builds a one-page resume for one company and role from your LaTeX master; only the sections that change are rewritten. |
| `scripts/make_letter.py --variant industry` | One-page industry cover letter: your opener, the job-specific middle, why this company, your closer. |
| `skills/econ-industry-scan` | Runs the industry scan, rates postings, writes the industry Leads sheet. |
| `skills/econ-industry-apply` | For one company and role: fills the row, tailors the resume, writes the cover letter and form answers, and can fill the online form in Chrome for you to review and submit. Writing guide: `skills/econ-industry-apply/resume_guide.md`. |

## Setup (about 15 minutes)

Requirements: macOS for the Mail and Shortcuts features, Python 3 with `openpyxl`, a LaTeX
install with `pdflatex` (TinyTeX is enough), and Claude Code (desktop app or CLI). Optional:
`gspread` and a Google service account, only if you want the Google Sheet for letter writers.

```bash
git clone https://github.com/<you>/econ-job-market-kit.git ~/econ-job-market-kit
cd ~/econ-job-market-kit
cp config.example.json config.json        # then edit config.json (it is git-ignored)
python3 scripts/build_tracker.py          # academic tracker, inside job_market_dir
python3 scripts/build_tracker.py --industry   # industry tracker, inside industry.dir
mkdir -p ~/.claude/skills
for s in econ-tracker-fill econ-cover-letter econ-job-scan econ-mail-check \
         econ-materials econ-industry-scan econ-industry-apply; do
  ln -s "$PWD/skills/$s" ~/.claude/skills/$s
done
```

In `config.json` set:

- your name and contact details, your letter writers, `job_market_dir`, `materials_dir`, and the
  shared `letter_share_file`; leave `letter_share_gsheet` empty unless you set up the optional
  Google Sheet;
- `profile` and `scan`: fields, what you want in order of priority, work authorization, filters
  (academic);
- `industry`: its folder, the directions and keywords, the job-alert mail account (industry);
- `mail` (optional): the Mail account and mailboxes for the mail check, how many days back, and
  `skip_senders`. Delete the block if you would rather type Submitted dates yourself.

Then say "set up My Materials" (建立 My Materials) in Claude Code: it finds your existing CV,
statements and papers, indexes them (they can stay where they are), fills the knowledge base and
drafts a one-page industry resume for you to check.

## My Materials (shared)

```
Job Market/
  My Materials/              you maintain this: masters (any layout) + 00-knowledge-base/
  Job Market 2026-27/        academic: uploadable copies (suggested 01_CV ... 07_Statements), tracker, cover letters
  Industry 2026-27/          industry: tracker, one folder per job (resume, cover letter, form answers)
  Letter Requests (shared)/  the writers' list (academic + industry jobs that need letters)
```

- **Knowledge base** (`00-knowledge-base/`, after dayuan-wang/job-hunt-helper): personal info and
  work-authorization wording, education, experience and projects as bullet banks (academic and
  industry voice), skills with a do-not-claim list, summaries per direction, cover-letter
  paragraphs, form answers, references, **advice** people gave you, **employer** notes, and
  **market wisdom** (public advice for econ PhDs with sources, including NABE's). Mention advice
  or a contact in any chat and Claude files it there.
- **Index** (`materials-index.md`): where each master is and which folder its copy goes to. Keep
  files where they are (e.g. your website repo), or put a Finder alias / symlink in My Materials.
- The suggested academic layout is only a suggestion; Claude asks before moving anything.

### Your own version of the skills

The skills in `skills/` are the generic method and are what this repository shares. Your own
version lives in My Materials, never in the repository: one file per skill in
`00-knowledge-base/skills/` (what counts as a good fit for you, which project to lead with, the
wording your advisors want, exceptions). Every skill reads its file first and follows it. Say
"build my personal skills" (生成我的个人版 skill) to draft them from your knowledge base, and
"以后…" / "from now on…" in any chat to add a rule.

Where things live: the repository holds only generic code, skills and blank templates. Your own
files are in a separate folder outside it, wherever `materials_dir` in `config.json` points (e.g.
`~/Dropbox/Job Market/My Materials/`); the skills find them through that path.

```
~/econ-job-market-kit/              the repository (shared on GitHub)
  skills/, scripts/, templates/       generic
  config.json                         your settings; inside the folder but git-ignored
        │ materials_dir
        ▼
~/Dropbox/Job Market/My Materials/  not in the repository
  00-knowledge-base/                  knowledge base
  00-knowledge-base/skills/           your version of each skill
```

So your files cannot be committed by mistake, they sync through Dropbox to your other computers,
and updating the kit from GitHub never touches them. `.gitignore` also blocks personal files
(knowledge-base skill files, My Materials, scan results) in case one is ever copied into the repository.

---

## Part A · Academic job market

### Finding jobs

| Source | How it is read | Best for |
|---|---|---|
| JOE | AEA's XML export | US and international academic, policy and nonacademic jobs |
| EconJobMarket | public JSON feed | international and policy jobs |
| IMF | Workday career site (public JSON) | Economist Program and other IMF jobs |
| World Bank Group | Cornerstone career site (public search) | economist, research and data jobs (titles filtered) |
| Chronicle Jobs | Economics category RSS | liberal arts, regional and teaching-focused colleges |
| Inside Higher Ed Careers | Economics faculty RSS | same, plus some Asian and Middle East schools |

HigherEdJobs blocks automated access, so it is not scanned; most of its economics faculty ads
also appear on Chronicle or Inside Higher Ed. A free HigherEdJobs "Job Agent" email alert covers the rest.

How a run works:

1. `scan_postings.py` fetches all sources (about 2 minutes), drops postdoc, visiting, adjunct,
   part-time, internship, senior-only, other-discipline and expired ads, merges the same job
   posted on several boards, and skips anything seen before or already in either tracker.
2. Claude reads the rest, rates each one High / Medium / Low against your `profile` (and your
   personal version of the skill), reads the full ad for High and Medium, and writes them to
   **Leads** with a one-line Why and Flags. Consulting, tech and finance firms on JOE go to the
   industry Leads instead.
3. You set Decision = Add / Maybe / Pass and click **▶ Update Tracker**.

Preferences that shape the ratings:

- `profile.wants`: the kinds of positions you want, in order of priority (e.g. teaching-focused
  first; data science roles at policy institutions count).
- `scan.priority_types`: position types listed first within each fit level.
- `profile.work_authorization`: ads that require citizenship, permanent residency or a security
  clearance are skipped; ads that say they will not sponsor visas, and US federal agencies, are
  kept as Low with a flag; ads that say nothing get "visa sponsorship not stated; ask HR".

### Applying

1. **Fill the rows.** Say "fill the tracker": Claude reads each posting and fills Deadline (the
   earliest date in the ad, e.g. when review begins), Letters Due (only if the ad says by when
   materials should be received, e.g. full consideration by; otherwise blank), where to apply,
   letters, extra materials and visa notes, without overwriting what you typed.
2. **Write letters.** Say "write the cover letter for <Employer>". You review the PDF and set Final.
3. **Submit** on the employer's site yourself, then record it (see [Recording submissions](#recording-submissions)).

### Academic cover letters

Two templates, distilled from economics job market guides (Cawley's AEA guide; Holmes and
Colander on liberal arts hiring) and university career centers (UNC, Binghamton); details and
sources in `skills/econ-cover-letter/templates.md`.

| | `research` | `teaching` |
|---|---|---|
| For | research universities, policy schools, central banks | liberal arts colleges, teaching tracks, regional universities, community colleges |
| Length | one page | up to two pages |
| Order | intro, job market paper, other research, short teaching paragraph, fit, closing | intro, how you teach, evidence and what you changed, short research paragraph, fit, closing |
| Fit paragraph | 1 to 3 sentences, only where there is a real match | 3 to 6 sentences: their courses you can teach, their students and mission, load, why this kind of school |

The shared paragraphs live in `00-knowledge-base/10-cover-letter-kb.md` (or `config.json`
`cover_letter` before My Materials is set up). Every letter is tailored: the template, the exact
title and department, and the fit paragraph, which Claude writes after reading the ad and the
department's own pages (course listings, centers). It also answers anything the ad asks the letter
to address. The shared paragraphs stay the same across letters unless you approve a change for one
letter. Facts about you come only from My Materials; facts about the school only from its ad and pages.

The CV, job market paper and statements are your masters in My Materials;
`sync_materials.py` keeps their uploadable PDFs in the academic folder. Statements in Markdown:
`python3 scripts/md2pdf.py research_statement.md "Research Statement" refs.tex`.

---

## Part B · Industry

Directions and keywords (config.json `industry.categories`): Economist / economic consulting;
causal inference, experimentation, data science; pricing, marketplace, demand forecasting;
economic research, quant, risk modeling. Industry materials differ from academic ones: a one-page
resume instead of a CV, and a short cover letter written for one company and one role.

### Finding jobs

| Source | How it is read |
|---|---|
| LinkedIn, Indeed | your job-alert emails, read through the Mail app (neither site allows scraping) |
| NABE EconJobs ([econjobs.nabe.com](https://econjobs.nabe.com/jobs/)) | read directly in Claude's built-in browser with `scripts/nabe_jobs.js`; no account or alert needed |
| JOE (nonacademic) | consulting, tech and finance postings passed on by the academic scan |
| Company career pages (optional) | public job APIs (Amazon, Google, Netflix, Greenhouse / Lever / Ashby / Workday boards); off unless `scan_companies` is true |

"Scan for industry jobs" (扫业界职位) gathers these, rates each posting against your knowledge base
and your personal version of the skill, and writes the industry Leads sheet. A job already in your
academic tracker is flagged and never added twice. Set Decision = Add and click ▶ Update Tracker.

**Setting up the job alerts** (once, about 20 minutes). Use one email address for both, one that
the Mail app on this Mac is signed in to, and put that account's name in
`industry.alert_mail.account`. NABE needs nothing: the scan reads its board.

- **LinkedIn**: Jobs → search a keyword → filter Experience level: Entry level / Associate,
  Date posted → turn on **Set alert** (daily, email). One alert per keyword below.
- **Indeed**: search a keyword and location → **Get new jobs for this search by email**.
- Keywords (one alert each; the scan's filter drops senior and engineering titles):
  `Economist`, `PhD Economics`, `Economic Consulting`, `Causal Inference`, `Experimentation`,
  `Data Scientist economics`, `Research Scientist economics`, `Pricing`, `Marketplace`,
  `Demand Forecasting`, `Quantitative Researcher`, `Economic Research`, `Risk Modeling`.
- After the first alert of each site arrives, run the scan once; if it reports 0 alert emails,
  add that email's sender to the board's `senders` in config.json.

### Materials for one company and one role

Say "apply to <company>" (给XX做材料). Following dayuan-wang/job-hunt-helper's per-job workflow,
everything is written for that posting only and goes into `Industry 2026-27/<Company> - <Role>/`:

1. **Analyze.** Claude reads the posting (saved as `jd.md`), the company's or team's own pages,
   and your notes on that employer (`14-employers.md`, `13-advice.md`), fills the row (category,
   level, visa, letters, pursue / gap / skip) and tells you the two or three things the posting
   cares most about.
2. **Resume** (one page, from your LaTeX master; `make_resume.py`). Only the parts that change are
   rewritten: a title line naming the target role, a two-line objective, and the skills section in
   the posting's own words but only with skills from your bank (never the do-not-claim list); bullets
   are reordered when that helps. Following NABE EconJobs' career advice, the top third must pass a
   six-second scan (name with Ph.D., contact, LinkedIn, the role you want), and the skills wording
   matters because application systems screen on it first.
3. **Cover letter** (350–450 words, one page; `make_letter.py --variant industry`): your opener,
   one flagship project that matches the job's core problem, one more matching experience, why this
   company (from its own pages), your closer. No generic praise.
4. **Form answers** (`form_answers.md`): the posting's questions or the usual ones (why us, a data
   project, work authorization in your fixed wording, salary approach), each under 100 words.
5. **Form** (optional): open the application in Chrome and sign in; Claude fills the basic fields
   and uploads the files after you approve the list. It never types passwords, ID numbers or EEO
   answers and never clicks Submit.

What the resume and letter stress depends on the kind of role (from `15-market-wisdom.md`):
causal inference, experimentation and SQL for tech economist and data science roles; communication,
teamwork and antitrust / damages / demand estimation for economic consulting (whose JOE postings
usually want letters); time series and macro views for economic research and finance. Facts about
you come only from your knowledge base; if a job needs something you lack, Claude says so.

**NABE events.** NABE's Tech Economics Conference has an industry job fair (2026: Nov 1–3, San
Diego), and its Econ Careers Week recordings (free registration) cover the 2026–27 PhD job market
from recruiters at Analysis Group, Google and the Cleveland Fed. Details and dates in
`15-market-wisdom.md`.

---

## Letter writers' list (academic and industry)

`export_letter_list.py` builds the only thing you share (the trackers stay private): every
position in either tracker with Letters? = Yes, soonest deadline first, with type of job, deadline,
where to submit, link, your status, the date you applied, and when letters are due (Letters Due:
filled only when the ad says by when materials should be received, otherwise blank), then a status
column per writer (Sent / Waiting) and Comments columns for you and each writer.

- It always writes an Excel file to `letter_share_file` in which only the writer status and
  Comments columns are editable (share it with edit access). Writers' entries are read back and
  kept on every refresh, a refresh is skipped if someone saved the file in the last 10 minutes,
  and Dropbox conflicted copies are merged in. A writer's column turns Received when the mail check
  finds the system's confirmation. Rewritten on every update, so the link never changes.
- **To change a date on it** (Deadline, Letters Due, I Applied On), edit Deadline, Letters Due or
  Submitted in your own tracker, then click ▶ Update Tracker; what you type in the tracker always
  wins, and Claude only fills empty cells. Changes made directly in those columns of the list are
  overwritten.
- Share it once, with edit access: the Excel file's link (Dropbox/OneDrive "can edit"), or the
  Google Sheet (as Editor) if you set it up.

### Google Sheet for letter writers (optional)

Skip this if the shared Excel file is enough (it is editable in the same way). With it, writers get
a Google Sheet link where each of them marks their status (Sent / Waiting) and writes in their
Comments column, and you write in yours.

- Columns you and the writers fill in are read back before every refresh and kept, matched to
  each position by link (or employer and position), so they stay with the right job.
- All other columns are rewritten from the trackers, and rows are re-sorted by deadline on every
  refresh. Edit the tracker, not the sheet; writers who want their own view can use Data → Filter views.
- Those tracker columns and the header rows are protected: only you and the script can change
  them. Sharing settings and any protections you add yourself are never touched.
- The Excel file is still written as a backup. If Google is unreachable, the sheet is left
  untouched and the rest of the update goes on.

Setup (about 10 minutes, once):

1. In the [Google Cloud console](https://console.cloud.google.com/), create a project, enable the
   **Google Sheets API**, create a **service account** (no roles needed), and under Keys add a
   JSON key. Save it at the `google_credentials` path in `config.json`
   (default `~/.config/econ-job-market-kit/google-service-account.json`). Keep it private.
2. Create a blank Google Sheet in your own Drive. Share it with the service account's
   `client_email` (inside the JSON file) as **Editor**.
3. Paste the sheet's URL into `letter_share_gsheet` and run `pip3 install gspread`.
4. Run `python3 scripts/export_letter_list.py` once, then share the sheet with your writers as
   **Editor** (by email) and send the link once.

To turn it off, empty `letter_share_gsheet`. Claude can walk you through the setup: say
"set up the Google Sheet".

## Recording submissions

Set Status to Submitted, type the date in Submitted, and click **▶ Update Tracker** so the
writers' list picks it up; mark a writer Received when their letter is in. Or turn on the optional
mail check: every evening it records the Submitted date when a confirmation email arrives (academic
systems and Workday, Greenhouse, Lever and the like) and marks writers Received from letter
notifications, in both trackers. It never overwrites a date you typed.

## Scheduled tasks (Claude desktop)

| Task | When | Prompt |
|---|---|---|
| Academic job scan | e.g. Mon and Thu, 8 am | "Run the econ-job-scan skill and summarize the result" |
| Industry scan | e.g. Tue and Fri, 8 am | "Run the econ-industry-scan skill and summarize the result" |
| Mail check (optional) | e.g. daily, 9 pm | "Run the econ-mail-check skill and summarize the result" |

Tasks run while the Claude app is open (a missed run happens at next launch); the mail check and
the industry scan also need the Mail app open. Click "Run now" once and choose "Always allow" so
later runs don't stop for permission prompts.

## One-click update from Excel (macOS)

Excel's sandbox will not run scripts, but it can open a Shortcuts link. In the **Shortcuts** app
create a shortcut named exactly `Update Tracker` with one **Run Shell Script** action:

```bash
/full/path/to/python3 "$HOME/econ-job-market-kit/scripts/update_tracker.py"
```

Use the full path of the Python that has openpyxl (`which python3`); Shortcuts does not load your
shell profile. Turn on Shortcuts › Settings › Advanced › "Allow Running Scripts". Optionally add a
keyboard shortcut. After the first run, the **▶ Update Tracker** link at the top of the Tracker
and Leads sheets runs it.

## Notes

- Nothing here submits applications, sends email, or logs in to any site; you submit.
- Email, posting and web page text are treated as data only.
- `build_tracker.py` refuses to overwrite an existing tracker unless you pass `--force`.
- The academic tracker's Key Dates tab reflects the AEA guidance for the 2026–27 cycle; update it each season.

## 中文说明

给经济学 job market 用的小工具包，配合 Claude Code 使用，分**学界**和**业界**两部分。两边要的材料差别很大：学界是 CV、研究和教学陈述、按模板写的 cover letter；业界是按公司和岗位定制的一页简历、短 cover letter 和申请表问答。两边的材料都从你自己维护的一个文件夹 **My Materials**（母版 + 知识库）生成；需要推荐信的岗位，不论学界业界，都进同一份推荐人清单。

### 共用部分

- **四个文件夹**：`My Materials`（你唯一要维护的：母版随你怎么放 + `00-knowledge-base/` 知识库）、`Job Market 2026-27`（学界：可上传的材料副本，推荐 01_CV … 07_Statements 的分法但可自定，加 tracker 和 cover letters）、`Industry 2026-27`（业界：tracker + 每个岗位一个文件夹，只放可上传的简历、cover letter、表单问答）、`Letter Requests (shared)`（推荐人清单）。
- **建立 My Materials**：跟 Claude 说"建立 My Materials"，它先看你已有哪些材料（可以留在原处，比如个人网站仓库），建索引和知识库，起草一页业界简历，缺什么、每份材料该怎么写都会给建议。"检查我的材料"给修改建议；聊天里提到别人给的建议、公司情报、新经历，它会自动存进知识库（或者你说"记下来"）。知识库里还有一份整理好的公开经验（EJMR、从业者文章、NABE、签证规则等，注明来源和可信度）。
- **个人版 skill**：仓库里的 skill 是通用流程（GitHub 上分享的就是这些）；你自己的版本放在 My Materials 的 `00-knowledge-base/skills/` 里，每个 skill 一个文件（什么算适合你、主打哪个项目、老师要求的口径、例外情况），skill 运行时先读它。说"生成我的个人版 skill"从知识库起草；聊天里说"以后……"会追加进去。
- **文件放在哪里**：仓库（`econ-job-market-kit`，会上 GitHub）里只有通用的代码、skill 和空白模板；你自己的文件（知识库、个人版 skill）在仓库外面，`config.json` 里 `materials_dir` 指到哪里就在哪里（比如 Dropbox 的 `Job Market/My Materials/`），skill 运行时通过这个路径去读。`config.json` 在仓库文件夹里，但被 `.gitignore` 排除、不会上传。这样分开：个人文件不可能被误提交；通过 Dropbox 在多台电脑同步；以后从 GitHub 更新通用版也不会碰到它们。

### A. 学界

**1. 自动找职位（每周一、四）**

- 扫 JOE、EconJobMarket、IMF、World Bank、Chronicle Jobs、Inside Higher Ed Careers（HigherEdJobs 禁止自动抓取，没有包含，可以在它网站上设邮件提醒补上）。JOE 上咨询、科技、金融公司的岗位转到业界的 Leads。
- 按你的 CV、偏好和个人版 skill 打分（High / Medium / Low），写进学界追踪表的 **Leads** 页：Why 写为什么适合，Flags 写要注意的地方（签证、额外材料、只是开始审的日期等）。
- 偏好在 `config.json` 里设：`profile.wants` 写想投什么、优先顺序；`scan.priority_types` 决定同一档里哪类排前面；`profile.work_authorization` 写身份情况。要求公民 / 绿卡或 security clearance 的直接跳过；写明不 sponsor 签证的、美国联邦机构，评 Low 并标出来；没写的标"未说明，需问 HR"。

**2. 追踪表**

- 在 Leads 页把想投的选 Add，点表格顶部的 **▶ Update Tracker**（或跟 Claude 说"把 leads 加到追踪表"），就会进主表 Tracker。Excel 开着也没关系。
- 跟 Claude 说"补全追踪表"，它会读每个广告，填申请截止日期（Deadline，取广告里最早的日期，比如开始审核）、推荐信截止日（Letters Due，只在广告写明材料某天前要收到时才填，否则空着）、投递平台、要不要推荐信、额外材料、签证说明，不会覆盖你自己填的内容。

**3. Cover letter（两套模板）**

- 参考了 Cawley 的 AEA 求职指南、Holmes & Colander 关于文理学院招人的研究，以及 UNC、Binghamton 职业中心的写法（详见 `skills/econ-cover-letter/templates.md`）。
- **研究型**（研究型大学、政策机构、央行）：一页，研究在前，"为什么适合"只写 1–3 句真对口的地方。
- **教学型**（文理学院、教学岗、地区性大学、社区学院）：最多两页，教学在前、篇幅最大，研究压成一段；"为什么适合"写 3–6 句：他们课表里你能教的课、学生和办学定位、课量、为什么想去这类学校。
- 固定段落放在知识库的 `10-cover-letter-kb.md`；每封都按岗位定制：选模板、写准确的职位和系名、读广告和系里官网后重写契合段、回答广告要求信里写的内容。固定段落默认不变，某封需要调整会先问你。关于你的事实只来自 My Materials，关于学校的只来自它的广告和官网，不编造。
- 用法：跟 Claude 说"给 XX 写 cover letter"，看完 PDF 后在 Tracker 里标 Final。
- CV、JMP、statements 是 My Materials 里的母版，`sync_materials.py` 把可上传的 PDF 放进学界文件夹；Markdown 写的 statement 一条命令排成 PDF。

### B. 业界

方向和关键词（`config.json` 的 `industry.categories`）：经济学家 / 经济咨询；因果推断、实验、数据科学；定价、平台市场、需求预测；经济研究、量化、风险模型。

**1. 找职位**

- **LinkedIn、Indeed**：两家都不让抓取，用它们的职位提醒邮件（发到"邮件"App 里登录的账户，`industry.alert_mail.account` 填这个账户）。设置：LinkedIn 搜关键词 → Experience level 选 Entry level / Associate → 打开 Set alert（每天、邮件）；Indeed 搜关键词和地点 → "Get new jobs for this search by email"。关键词每个建一个提醒：`Economist`、`PhD Economics`、`Economic Consulting`、`Causal Inference`、`Experimentation`、`Data Scientist economics`、`Research Scientist economics`、`Pricing`、`Marketplace`、`Demand Forecasting`、`Quantitative Researcher`、`Economic Research`、`Risk Modeling`。
- **NABE EconJobs**（econjobs.nabe.com）：Claude 用内置浏览器直接读全部职位，不用注册、不用提醒。上面有 Analysis Group、Cornerstone、Keystone、Amazon 等的 PhD 岗位。
- **JOE**：学术扫描把咨询、科技、金融公司的岗位转过来。
- **公司招聘页**（可选）：Amazon、Google、Netflix 等的公开接口，默认关闭，`scan_companies` 改成 true 才读。
- 说"扫业界职位"，打分后写进业界表的 Leads 页；学界表里已有的同一份工作会被标出、不会重复加入。

**2. 按公司和岗位做材料**（说"给XX做材料"）

参考 dayuan-wang/job-hunt-helper 的做法，每份材料只为这一个岗位写，放进 `Industry 2026-27/<公司> - <岗位>/`：

- **分析**：读职位原文（存为 `jd.md`）、公司或团队自己的页面、知识库里关于这家的情报和建议，补全该行（方向、级别、签证、推荐信、pursue/gap/skip），告诉你这个岗位最看重的两三点。
- **简历**（一页，从 LaTeX 母版生成）：只改需要变的部分，包括一行写明目标岗位的职业标题、两行 objective、技能栏（用职位描述里的词，但只能用你技能库里有的，不写"不写清单"上的），必要时调整 bullet 顺序。按 NABE 求职建议：招聘者初筛只看约 6 秒，简历上方三分之一要一眼看清你是谁、要什么岗位、怎么联系；技能用词要和职位描述一致，因为申请系统先按这些词筛。
- **Cover letter**（350–450 词，一页）：你的开头 → 一个和岗位核心问题最匹配的旗舰项目 → 另一段相关经历 → 为什么是这家公司（来自它自己的页面）→ 你的结尾。不写空泛的客套话。
- **表单问答**（`form_answers.md`）：职位自己的问题或常见问题（为什么选我们、一个数据项目、工作授权用固定原话、薪资怎么答），每条 100 词以内。
- **代填表单**（可选）：你在 Chrome 打开申请页并登录；Claude 先把要填的内容和要上传的文件列给你确认，再填写、上传。不填密码、证件号、EEO，不点提交。
- 不同岗位侧重点不同（见知识库 `15-market-wisdom.md`）：科技公司 economist / 数据科学看因果推断、实验和 SQL；经济咨询看沟通、团队合作和反垄断 / 损害赔偿 / 需求估计（JOE 上的咨询岗通常要推荐信）；经济研究和金融看时间序列和宏观判断。关于你的事实只来自知识库，岗位要求你没有的，Claude 会直说。
- **NABE 活动**：Tech Economics Conference（2026 年 11 月 1–3 日，San Diego）有业界招聘会；Econ Careers Week 的录播（免费注册）里有 Analysis Group、Google、克利夫兰联储的招聘人员讲 2026–27 PhD 求职。日期和细节见 `15-market-wisdom.md`。

### 推荐人清单（学界 + 业界）

- 只分享这份清单，追踪表始终是你自己的，不给任何人。两张追踪表里 Letters? = Yes 的岗位都会进来，按截止日期排序；Type 列能看出是学界还是业界（比如 Consulting、Tech）。
- **要手动改清单上的日期（截止日期、Letters Due、I Applied On），请在自己的 Tracker 里改** Deadline、Letters Due、Submitted 这几列，再点 ▶ Update Tracker。Tracker 里你手写的永远优先，Claude 只填空格子。直接在清单（包括 Google Sheet）里改这些列，下次刷新会被覆盖。
- 列：岗位、工作类型（Type）、截止日期、从哪交、广告链接、你的进展（Status）、你哪天提交的（I Applied On）、Letters Due（广告写明材料某天前要收到时才有，否则空着）；然后每位老师一列 Sent / Waiting，最后是你和每位老师的 Comments。
- 默认：生成一个 Excel，放在共享网盘里，用"可编辑"权限分享一次链接。只有老师状态和 Comments 几列能改，其他列锁定；老师填的内容每次刷新都会读回来保留。邮件确认某位老师的信已收到时，那一栏自动变成 Received。有人 10 分钟内刚改过文件时，这次刷新会跳过；Dropbox 万一生成"冲突副本"，里面填的内容也会自动合并回来。
- **可选：Google Sheet**。老师同样可以在里面标 Sent / Waiting、写 Comments，内容每次刷新都保留并跟着对应岗位走；其他列每次按追踪表重写，受保护。Excel 照样生成作备份；Google 连不上时表格不动，其他更新照常。设置（一次，约 10 分钟）：在 Google Cloud 建项目、启用 Google Sheets API、建 service account 并下载 JSON 密钥，放到 `google_credentials` 指的位置；在自己的 Google Drive 新建空表，共享给密钥里的 `client_email`（编辑者）；把表格链接填进 `letter_share_gsheet`，`pip3 install gspread`；运行一次 `export_letter_list.py`，再把表以"编辑者"权限分享给老师。也可以跟 Claude 说"设置 Google Sheet"。

### 记录提交、定时任务

- **记录提交**：手动在 Tracker 里把状态改成 Submitted、填日期，老师的信到了就在对应列选 Received，再点 **▶ Update Tracker**。或者打开可选的每晚查邮件：读 Mac "邮件" App 里最近的邮件（不需要密码；`skip_senders` 里的发件人一律不打开），看到申请确认（学界系统，以及 Workday、Greenhouse、Lever 等业界系统）就填 Submitted，看到推荐信已收到就标 Received，两张表都管；不会覆盖你手动填的日期。不想用就删掉 `config.json` 里的 `mail` 那一段。
- **定时任务**：在 Claude 桌面版左侧 **Scheduled** 里设置：学界扫描（比如周一、四）、业界扫描（比如周二、五）、查邮件（可选，每晚）。第一次点 Run now，弹窗选"始终允许"。运行时 Claude 桌面版要开着，查邮件和业界扫描还要开着"邮件"。
- **Excel 里一键更新**（Mac）：在"快捷指令"App 新建一个叫 `Update Tracker` 的快捷指令，加"运行 Shell 脚本"动作，内容是 `<python3 完整路径> "$HOME/econ-job-market-kit/scripts/update_tracker.py"`（用 `which python3` 查路径），并在 设置 › 高级 里勾选"允许运行脚本"。

工具不会替你提交申请、发邮件或登录任何网站。

## License

MIT
