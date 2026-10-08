# econ-job-market-kit

A small toolkit for the economics job market, academic and industry, built to work with Claude Code.
It finds postings twice a week, keeps an Excel tracker of everything you apply to (one academic,
one industry), writes a tailored cover letter per position (research, teaching-focused or industry
template) and a tailored one-page resume for industry jobs, records when you submit (by hand, or
optionally from confirmation emails), and gives your letter writers one list that updates itself.
Everything is written from one folder you maintain, **My Materials** (your master files plus a
knowledge base about you).

[中文说明见下方](#中文说明)

## What's inside

| | |
|---|---|
| `scripts/build_tracker.py` | Builds an Excel tracker: one row per job, deadline countdown, Submitted date, academic / industry / government tracks, a column per letter writer (Received, from the mail check), a summary tab, and the AEA key dates. The tracker stays private; writers only ever see the Letter Requests list. |
| `scripts/scan_postings.py` | Pulls current postings from JOE, EconJobMarket, the IMF and World Bank career sites, and Chronicle Jobs and Inside Higher Ed Careers; filters by rank, field, deadline and section; skips ones already seen. |
| `scripts/leads.py` | Adds rated postings to a **Leads** sheet in the tracker, and moves the ones you mark Add into the Tracker. |
| `scripts/update_tracker.py` | One step, no Claude needed: moves Leads marked Add into the Tracker and refreshes the letter-writer file. Works while Excel has the tracker open (it saves, updates and reopens it). Also runs from a **▶ Update Tracker** link in the sheet (see below). |
| `scripts/make_letter.py` | Builds a cover letter PDF from your own paragraphs in `config.json`, in two templates: `research` (one page) and `teaching` (up to two pages). Only the fit paragraph is new per school. |
| `scripts/export_letter_list.py` | Builds the list your letter writers see (the only thing you share; the tracker stays private): positions that need letters, soonest deadline first, with type of job, deadline, where to submit, link, your status, the date you applied, and when letters are due (Letters Due: from the tracker; filled only when the ad says by when materials should be received, otherwise blank), then a status column per writer (Sent / Waiting) and Comments columns for you and each writer. Always writes an Excel file to `letter_share_file` in which only the writer status and Comments columns are editable (share it with edit access); writers' entries are read back and kept on every refresh, a refresh is skipped if someone saved the file in the last 10 minutes, and Dropbox conflicted copies are merged in. A writer's column turns Received when the mail check finds the system's confirmation. **Optionally** it also writes a Google Sheet (see [Google Sheet for letter writers](#google-sheet-for-letter-writers-optional)). Rewritten on every update, so the link never changes. |
| `scripts/mail_scan.py` | Optional. Reads recent mail through the Mail app already signed in on your Mac (no passwords). Opens only emails that look like application-system or letter notifications, never senders in `mail.skip_senders` (e.g. your own university). |
| `scripts/industry_scan.py` | Industry postings: your LinkedIn / Indeed job-alert emails (read through the Mail app) and the public job APIs of company career pages (Greenhouse, Lever, Ashby, Workday, Amazon); filters titles by your four directions; skips jobs already in either tracker. |
| `scripts/make_resume.py` | Builds a tailored one-page resume for one job from your LaTeX master: only the sections that change (usually objective and skills) are rewritten. |
| `scripts/sync_materials.py` | Copies the newest version of each master in My Materials (PDF, Word, or a PDF compiled from .tex / .md) into the folders you chose in the job market folder. Never deletes your files. |
| `scripts/md2pdf.py` | Converts a Markdown research or teaching statement into a PDF with the same letterhead. |
| `skills/econ-job-scan` | Claude Code skill: runs the scan, rates each new posting against your `profile`, checks visa rules, writes the Leads sheet. |
| `skills/econ-tracker-fill` | Claude Code skill: reads the links in your tracker and fills employer, position, Deadline (the earliest date in the ad, e.g. when review begins), Letters Due (only if the ad says by when materials should be received), where to apply, whether letters are needed, and extra materials. |
| `skills/econ-cover-letter` | Claude Code skill: picks the template, reads the posting and the department's pages, writes the fit paragraph, builds the PDF, marks it Drafted. Guidance in `skills/econ-cover-letter/templates.md`. |
| `skills/econ-mail-check` | Optional Claude Code skill: runs the mail scan, records Submitted dates and letters Received in the tracker, refreshes the writers' list. |
| `skills/econ-materials` | Claude Code skill: sets up My Materials (finds your existing files, builds the index and knowledge base, suggests a folder layout), reviews your CV / statements / resume, and saves advice and employer notes from chat. |
| `skills/econ-industry-scan` | Claude Code skill: runs the industry scan, rates postings against your knowledge base, writes the industry Leads sheet. |
| `skills/econ-industry-apply` | Claude Code skill: for one industry job, fills the row, tailors the resume, writes a cover letter and form answers into the job's folder, and can fill the online form in Chrome for you to review and submit. |
| `templates/` | Knowledge-base files (00–15, including public advice for econ PhDs with sources), the My Materials guide, and the LaTeX resume. |

## Setup (about 10 minutes)

Requirements: macOS for the Mail and Shortcuts features, Python 3 with `openpyxl`, a LaTeX
install with `pdflatex` (TinyTeX is enough), and Claude Code (desktop app or CLI). Optional:
`gspread` and a Google service account, only if you want the Google Sheet for letter writers.

```bash
git clone https://github.com/<you>/econ-job-market-kit.git ~/econ-job-market-kit
cd ~/econ-job-market-kit
cp config.example.json config.json        # then edit config.json (it is git-ignored)
python3 scripts/build_tracker.py          # creates the tracker inside job_market_dir
mkdir -p ~/.claude/skills
for s in econ-tracker-fill econ-cover-letter econ-job-scan econ-mail-check \
         econ-materials econ-industry-scan econ-industry-apply; do
  ln -s "$PWD/skills/$s" ~/.claude/skills/$s
done
```

In `config.json` set:

- your name and contact details, your letter writers, `job_market_dir`, and the shared
  `letter_share_file`; leave `letter_share_gsheet` empty unless you set up the optional Google
  Sheet;
- `cover_letter`: your own paragraphs for both templates (see Cover letters);
- `profile` and `scan`: fields, what you want in order of priority, work authorization, filters;
- `mail` (optional): the Mail account and the mailboxes to read (e.g. Inbox, Clutter, Junk Email),
  how many days back, and `skip_senders`. Delete the block if you would rather type Submitted dates yourself.

Then say "set up My Materials" (建立 My Materials) in Claude Code: it finds your existing CV,
statements and papers, indexes them (they can stay where they are), fills the knowledge base and
drafts a one-page resume for you to check. For the industry side, set `industry` in config.json
and run `python3 scripts/build_tracker.py --industry`.

## My Materials

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
  paragraphs (the academic letters read them too), form answers, references, **advice** people
  gave you, **employer** notes, and **market wisdom** (public advice for econ PhDs with sources).
  Mention advice or a contact in any chat and Claude files it there.
- **Index** (`materials-index.md`): where each master is and which folder its copy goes to. Keep
  files where they are (e.g. your website repo), or put a Finder alias / symlink in My Materials.
- The suggested academic layout is only a suggestion; Claude asks before moving anything.

## Your own version of the skills

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

## Industry track

Directions and keywords (config.json `industry.categories`): Economist / economic consulting;
causal inference, experimentation, data science; pricing, marketplace, demand forecasting;
economic research, quant, risk modeling.

1. **Find jobs.** The main sources are **LinkedIn and Indeed** job-alert emails (neither allows
   scraping), sent to an account in the Mail app (`industry.alert_mail`; set up as below), and
   **NABE EconJobs** ([econjobs.nabe.com](https://econjobs.nabe.com/jobs/)), which Claude reads
   directly in its built-in browser (no account or alert needed; `scripts/nabe_jobs.js`). "Scan for industry jobs" (扫业界职位) reads the alerts,
   rates each posting, and writes the industry Leads sheet. Company career pages
   (`industry.companies`: Amazon, Google, Netflix and others through their public job APIs) are
   off by default; set `scan_companies` to true to add them. Consulting and tech jobs posted on JOE come in through the academic scan. A job already
   in your academic tracker is flagged and never added twice.
2. **Materials.** "Apply to <company>" (给XX做材料): Claude reads the posting, fills the row
   (category, level, visa, pursue / gap / skip), tailors the one-page resume, writes a cover letter
   and short form answers, all from your knowledge base, into `Industry 2026-27/<Company> - <Role>/`.
3. **Form.** Open the application in Chrome and sign in; Claude can fill the basic fields and
   upload the files after you approve the list. It never types passwords, ID numbers or EEO
   answers and never clicks Submit.
4. **Letters.** Jobs with Letters? = Yes appear on the same Letter Requests list as academic jobs.

### Setting up the job alerts (once, about 20 minutes)

Use one email address for both, one that the Mail app on this Mac is signed in to, and put
that account's name in `industry.alert_mail.account`. NABE needs nothing: the scan reads its board.

- **LinkedIn**: Jobs → search a keyword → filter Experience level: Entry level / Associate,
  Date posted → turn on **Set alert** (daily, email). One alert per keyword below.
- **Indeed**: search a keyword and location → **Get new jobs for this search by email**.
- Keywords (one alert each; the scan's filter drops senior and engineering titles):
  `Economist`, `PhD Economics`, `Economic Consulting`, `Causal Inference`, `Experimentation`,
  `Data Scientist economics`, `Research Scientist economics`, `Pricing`, `Marketplace`,
  `Demand Forecasting`, `Quantitative Researcher`, `Economic Research`, `Risk Modeling`.
- After the first alert of each site arrives, run the scan once; if it reports 0 alert emails,
  add that email's sender to the board's `senders` in config.json.

NABE also runs the **Tech Economics Conference (TEC)** with an industry job fair (2026:
Nov 1–3, San Diego; student registration from $100, virtual from $50): see the knowledge base's
`15-market-wisdom.md`.

## Daily use

1. **Find jobs.** Twice a week the scan adds matching postings to the **Leads** sheet. Set
   Decision = Add for the ones you want, then click **▶ Update Tracker** (or say "add my leads to
   the tracker"). You can also paste links into the Tracker yourself.
2. **Fill the rows.** Say "fill the tracker": Claude reads each posting and fills Deadline (the
   earliest date in the ad, e.g. when review begins), Letters Due (only if the ad says by when
   materials should be received, e.g. full consideration by; otherwise blank), where to apply, letters, extra materials and visa notes, without overwriting what you typed.
3. **Write letters.** Say "write the cover letter for <Employer>". You review the PDF and set Final.
4. **Submit** on the employer's site yourself.
5. **Record submissions.** Set Status to Submitted, type the date in Submitted, and click
   **▶ Update Tracker** so the writers' list picks it up; mark a writer Received when their letter
   is in. Or turn on the optional mail check: every evening it records the Submitted date when a
   confirmation email arrives and marks writers Received from letter notifications. It never
   overwrites a date you typed. The writers' list shows your status and the date you applied.
6. Share the writers' list once, with edit access: the Excel file's link (Dropbox/OneDrive "can
   edit"), or the Google Sheet (as Editor) if you set it up. Writers mark Sent / Waiting and add
   comments; it refreshes after every tracker update and keeps what they typed. **To change a date on it
   (Deadline, Letters Due, I Applied On), edit Deadline, Letters Due or Submitted in your own tracker**,
   then click ▶ Update Tracker; what you type in the tracker always wins, and Claude only fills
   empty cells. Changes made directly in those columns of the list are overwritten.

## Cover letters

Two templates, distilled from economics job market guides (Cawley's AEA guide; Holmes and
Colander on liberal arts hiring) and university career centers (UNC, Binghamton); details and
sources in `skills/econ-cover-letter/templates.md`.

| | `research` | `teaching` |
|---|---|---|
| For | research universities, policy schools, central banks | liberal arts colleges, teaching tracks, regional universities, community colleges |
| Length | one page | up to two pages |
| Order | intro, job market paper, other research, short teaching paragraph, fit, closing | intro, how you teach, evidence and what you changed, short research paragraph, fit, closing |
| Fit paragraph | 1 to 3 sentences, only where there is a real match | 3 to 6 sentences: their courses you can teach, their students and mission, load, why this kind of school |

Every letter is tailored: the template, the exact title and department, and the fit paragraph,
which Claude writes after reading the ad and the department's own pages (course listings,
centers). It also answers anything the ad asks the letter to address. The shared paragraphs stay
the same across letters unless you approve a change for one letter. Facts about you come only
from `config.json`, your CV and your statements; facts about the school only from its ad and pages.

## Job scan

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
   posted on several boards, and skips anything seen before or already in your tracker.
2. Claude reads the rest, rates each one High / Medium / Low against your `profile`, reads the
   full ad for High and Medium, and writes them to **Leads** with a one-line Why and Flags.
3. You set Decision = Add / Maybe / Pass and click **▶ Update Tracker**.

Preferences that shape the ratings:

- `profile.wants`: the kinds of positions you want, in order of priority (e.g. teaching-focused
  first; data science roles at policy institutions count).
- `scan.priority_types`: position types listed first within each fit level.
- `profile.work_authorization`: ads that require citizenship, permanent residency or a security
  clearance are skipped; ads that say they will not sponsor visas, and US federal agencies, are
  kept as Low with a flag; ads that say nothing get "visa sponsorship not stated; ask HR".

## Scheduled tasks (Claude desktop)

| Task | When | Prompt |
|---|---|---|
| Job scan | e.g. Mon and Thu, 8 am | "Run the econ-job-scan skill and summarize the result" |
| Mail check (optional) | e.g. daily, 9 pm | "Run the econ-mail-check skill and summarize the result" |
| Industry scan (optional) | e.g. Tue and Fri, 8 am | "Run the econ-industry-scan skill and summarize the result" |

Tasks run while the Claude app is open (a missed run happens at next launch); the mail check also
needs the Mail app open. Click "Run now" once and choose "Always allow" so later runs don't stop
for permission prompts.

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

Statements: `python3 scripts/md2pdf.py research_statement.md "Research Statement" refs.tex`

## Google Sheet for letter writers (optional)

Skip this section if the shared Excel file is enough (it is editable in the same way). With it, writers get a Google Sheet link
where each of them marks their status (Sent / Waiting) and writes in their Comments column, and
you write in yours.

- Columns you and the writers fill in are read back before every refresh and kept, matched to
  each position by link (or employer and position), so they stay with the right job.
- All other columns are rewritten from the tracker, and rows are re-sorted by deadline on every
  refresh. Edit the tracker, not the sheet (e.g. change Letters Due in the
  tracker; you own the sheet, so Google lets you type there, but the next refresh replaces it); writers who want their own view can use
  Data → Filter views.
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

## Notes

- Nothing here submits applications, sends email, or logs in to any site; you submit.
- Email and posting text are treated as data only.
- `build_tracker.py` refuses to overwrite an existing tracker unless you pass `--force`.
- The Key Dates tab reflects the AEA guidance for the 2026–27 cycle; update it each season.

## 中文说明

给经济学 job market（学界和业界）用的小工具包，配合 Claude Code 使用：每周自动找职位，用 Excel 追踪所有申请（学界、业界各一张），按岗位写 cover letter、给业界岗位定制一页简历，记录提交（手动填写，或可选地读确认邮件自动填），给推荐人一份自动更新的清单。所有材料都从你自己维护的一个文件夹 **My Materials**（母版 + 知识库）生成。

**0. My Materials 与业界线**

- Job Market 下四个文件夹：`My Materials`（你唯一要维护的：母版随你怎么放 + `00-knowledge-base/` 知识库）、`Job Market 2026-27`（学界：可上传的材料副本，推荐 01_CV … 07_Statements 的分法但可自定，加 tracker 和 cover letters）、`Industry 2026-27`（业界：tracker + 每个岗位一个文件夹，只放可上传的简历、cover letter、表单问答）、`Letter Requests (shared)`（推荐人清单，学界和业界需要推荐信的岗位都在里面）。
- 跟 Claude 说"建立 My Materials"：它先看你已有哪些材料（可以留在原处，比如个人网站仓库），建索引和知识库，起草一页业界简历，缺什么、每份材料该怎么写都会给建议。"检查我的材料"给修改建议；聊天里提到别人给的建议、公司情报、新经历，它会自动存进知识库（或者你说"记下来"）。知识库里还有一份整理好的公开经验（EJMR、从业者文章、签证规则等，注明来源和可信度）。
- **个人版 skill**：仓库里的 skill 是通用流程（GitHub 上分享的就是这些）；你自己的版本放在 My Materials 的 `00-knowledge-base/skills/` 里，每个 skill 一个文件（什么算适合你、主打哪个项目、老师要求的口径、例外情况），skill 运行时先读它。说"生成我的个人版 skill"从知识库起草；聊天里说"以后……"会追加进去。这些和 `config.json` 都不进 git。
- **文件放在哪里**：仓库（`econ-job-market-kit`，会上 GitHub）里只有通用的代码、skill 和空白模板；你自己的文件（知识库、个人版 skill）在仓库外面，`config.json` 里 `materials_dir` 指到哪里就在哪里（比如 Dropbox 的 `Job Market/My Materials/`），skill 运行时通过这个路径去读。`config.json` 在仓库文件夹里，但被 `.gitignore` 排除、不会上传。这样分开：个人文件不可能被误提交；通过 Dropbox 在多台电脑同步；以后从 GitHub 更新通用版也不会碰到它们。
- 业界找职位：主要来源是 **LinkedIn、Indeed** 的职位提醒邮件（发到"邮件"App 里的账户，设置步骤见上面英文的 "Setting up the job alerts"），以及 **NABE EconJobs**（econjobs.nabe.com，Claude 用浏览器直接读，不用注册、不用提醒）；公司招聘页的公开接口默认关闭，config 里 `scan_companies` 改成 true 才读；说"扫业界职位"，结果写进业界表的 Leads 页。学界表里已有的同一份工作会被标出、不会重复加入。JOE 上咨询公司、科技公司的岗位由学术扫描转到业界 Leads。
- 每个岗位说"给XX做材料"：读职位、补全该行（方向、级别、签证、pursue/gap/skip），定制一页简历、写 cover letter 和表单问答；需要时用 Chrome 代填基础信息、上传文件（先列给你确认，不填密码、证件号、EEO，不点提交）。

**1. 自动找职位（每周一、四）**

- 扫 JOE、EconJobMarket、IMF、World Bank、Chronicle Jobs、Inside Higher Ed Careers（HigherEdJobs 禁止自动抓取，没有包含，可以在它网站上设邮件提醒补上）。
- 按你的 CV 和偏好打分（High / Medium / Low），写进追踪表的 **Leads** 页：Why 写为什么适合，Flags 写要注意的地方（签证、额外材料、只是开始审的日期等）。
- 偏好在 `config.json` 里设：`profile.wants` 写想投什么、优先顺序（比如教学型优先、政策机构的数据科学岗也算）；`scan.priority_types` 决定同一档里哪类排前面；`profile.work_authorization` 写身份情况。要求公民 / 绿卡或 security clearance 的直接跳过；写明不 sponsor 签证的、美国联邦机构，评 Low 并标出来；没写的标"未说明，需问 HR"。

**2. 追踪表**

- 在 Leads 页把想投的选 Add，点表格顶部的 **▶ Update Tracker**（或跟 Claude 说"把 leads 加到追踪表"），就会进主表 Tracker。Excel 开着也没关系。
- 跟 Claude 说"补全追踪表"，它会读每个广告，填申请截止日期（Deadline）、推荐信截止日（Letters Due）。Deadline 取广告里最早的日期（比如开始审核）；Letters Due 只在广告写明材料某天前要收到（比如 full consideration by）时才填，否则先空着、投递平台、要不要推荐信、额外材料、签证说明，不会覆盖你自己填的内容。
- 按钮的一次性设置（Mac）：在"快捷指令"App 新建一个叫 `Update Tracker` 的快捷指令，加"运行 Shell 脚本"动作，内容是 `<python3 完整路径> "$HOME/econ-job-market-kit/scripts/update_tracker.py"`（用 `which python3` 查路径），并在 设置 › 高级 里勾选"允许运行脚本"。

**3. Cover letter（两套模板）**

- 参考了 Cawley 的 AEA 求职指南、Holmes & Colander 关于文理学院招人的研究，以及 UNC、Binghamton 职业中心的写法（详见 `skills/econ-cover-letter/templates.md`）。
- **研究型**（研究型大学、政策机构、央行）：一页，研究在前，"为什么适合"只写 1–3 句真对口的地方。
- **教学型**（文理学院、教学岗、地区性大学、社区学院）：最多两页，教学在前、篇幅最大，研究压成一段；"为什么适合"写 3–6 句：他们课表里你能教的课、学生和办学定位、课量、为什么想去这类学校。
- 每封都按岗位定制：选模板、写准确的职位和系名、读广告和系里官网后重写契合段、回答广告要求信里写的内容。固定段落默认不变，某封需要调整会先问你。关于你的事实只来自你的材料，关于学校的只来自它的广告和官网，不编造。
- 用法：跟 Claude 说"给 XX 写 cover letter"，看完 PDF 后在 Tracker 里标 Final。

**4. 记录提交（手动，或可选的每晚查邮件）**

- 手动：在 Tracker 里把状态改成 Submitted、在 **Submitted** 列填日期，老师的信到了就在对应列选 Received，然后点 **▶ Update Tracker**，推荐人清单就会更新。
- 可选：每晚自动查邮件。不想用的话，`config.json` 里删掉 `mail` 那一段、不建这个定时任务即可。自动填写不会覆盖你手动填的日期。
- 查邮件会读 Mac "邮件" App 里最近的邮件（不需要密码；`skip_senders` 里的发件人，比如本校邮箱，一律不打开）。
- 看到申请确认，就在 Tracker 的 **Submitted** 列填上日期、状态改成 Submitted；看到推荐信已收到的通知，就在 Tracker 里对应老师那一列标 Received；对不上的、面试邀请、拒信会在小结里提醒你。
- 运行时 Claude 桌面版和"邮件"都要开着。

**5. 给推荐人的清单**

- 只分享这份清单，追踪表始终是你自己的，不给任何人。
- **要手动改清单上的日期（截止日期、Letters Due、I Applied On），请在自己的 Tracker 里改** Deadline、Letters Due、Submitted 这几列，再点 ▶ Update Tracker。Tracker 里你手写的永远优先，Claude 只填空格子。直接在清单（包括 Google Sheet）里改这些列，下次刷新会被覆盖。
- 列：需要推荐信的岗位（按截止日期排序）、工作类型（Type）、截止日期、从哪交、广告链接、你的进展（Status）、你哪天提交的（I Applied On）、Letters Due（推荐信应到的日期：广告写明材料某天前要收到时才有，否则空着；取自 Tracker 的同名列，补全追踪表时从广告读，不知道就留空。截止日期是你自己的申请截止日，两者分开）；然后每位老师一列 Sent / Waiting，最后是你和每位老师的 Comments。
- 默认：生成一个 Excel，放在共享网盘里，用"可编辑"权限分享一次链接。只有老师状态（Sent / Waiting）和 Comments 几列能改，其他列锁定；老师填的内容每次刷新都会读回来保留。邮件确认某位老师的信已收到时，那一栏自动变成 Received。有人 10 分钟内刚改过文件时，这次刷新会跳过，避免冲突；Dropbox 万一生成"冲突副本"，里面填的内容也会自动合并回来。
- **可选：Google Sheet**（不想用可以不设）。老师同样可以在里面自己标 Sent / Waiting、写 Comments，你也可以写自己的 Comments。这些内容每次刷新都保留，并且跟着对应岗位走；其他列每次按追踪表重写，行按截止日期重新排序；这些列和表头受保护，只有你和脚本能改（分享设置和你自己加的保护不会被动）。Excel 照样生成作备份；Google 连不上时表格不动，其他更新照常。
  - 设置（一次，约 10 分钟）：在 Google Cloud 建项目、启用 Google Sheets API、建 service account 并下载 JSON 密钥，放到 `google_credentials` 指的位置；在自己的 Google Drive 新建空表，共享给密钥里的 `client_email`（编辑者）；把表格链接填进 `letter_share_gsheet`，`pip3 install gspread`；运行一次 `export_letter_list.py`，再把表以"编辑者"权限分享给老师。也可以直接跟 Claude 说"设置 Google Sheet"，它会一步步带你做。不用的话 `letter_share_gsheet` 留空即可。
- 你的追踪表里另有每位老师一列，由每晚查邮件根据"信已收到"的邮件标 Received，只有你自己看得到。

**6. Statement 转 PDF**：research / teaching statement 用 Markdown 写，一条命令排成 PDF。

**定时任务**：在 Claude 桌面版左侧 **Scheduled** 里设置，扫职位和查邮件（可选）各一个，运行小结也在那里看。第一次点 Run now，弹窗选"始终允许"。

个人信息全部放在 `config.json`（不会上传到 GitHub），复制 `config.example.json` 改名后填写即可。工具不会替你提交申请、发邮件或登录任何网站。

## License

MIT
