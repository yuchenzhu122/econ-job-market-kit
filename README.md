# econ-job-market-kit

A small toolkit for the economics academic job market, built to work with Claude Code.
It finds postings twice a week, keeps one Excel tracker of everything you apply to, writes a
tailored cover letter per position (research or teaching-focused template), records when you
submit by reading confirmation emails, and gives your letter writers a list that updates itself.

[中文说明见下方](#中文说明)

## What's inside

| | |
|---|---|
| `scripts/build_tracker.py` | Builds an Excel tracker: one row per job, deadline countdown, Submitted date, academic / industry / government tracks, a **For Letter Writers** tab with each writer's status, a summary tab, and the AEA key dates. |
| `scripts/scan_postings.py` | Pulls current postings from JOE, EconJobMarket, the IMF and World Bank career sites, and Chronicle Jobs and Inside Higher Ed Careers; filters by rank, field, deadline and section; skips ones already seen. |
| `scripts/leads.py` | Adds rated postings to a **Leads** sheet in the tracker, and moves the ones you mark Add into the Tracker. |
| `scripts/update_tracker.py` | One step, no Claude needed: moves Leads marked Add into the Tracker and refreshes the letter-writer file. Works while Excel has the tracker open (it saves, updates and reopens it). Also runs from a **▶ Update Tracker** link in the sheet (see below). |
| `scripts/make_letter.py` | Builds a cover letter PDF from your own paragraphs in `config.json`, in two templates: `research` (one page) and `teaching` (up to two pages). Only the fit paragraph is new per school. |
| `scripts/export_letter_list.py` | Writes a separate, read-only Excel file for your letter writers to a shared Dropbox/OneDrive/Google Drive folder: positions that need letters, deadline, where to submit, link, and the date you applied. Share its link once; the same file is rewritten on every update. Writers can hide columns, sort and filter, but not edit. Each writer's Requested/Uploaded status stays private unless `letter_share_show_status` is true. |
| `scripts/mail_scan.py` | Reads recent mail through the Mail app already signed in on your Mac (no passwords). Opens only emails that look like application-system or letter notifications, never senders in `mail.skip_senders` (e.g. your own university). |
| `scripts/md2pdf.py` | Converts a Markdown research or teaching statement into a PDF with the same letterhead. |
| `skills/econ-job-scan` | Claude Code skill: runs the scan, rates each new posting against your `profile`, checks visa rules, writes the Leads sheet. |
| `skills/econ-tracker-fill` | Claude Code skill: reads the links in your tracker and fills employer, position, deadline, where to apply, whether letters are needed, and extra materials. |
| `skills/econ-cover-letter` | Claude Code skill: picks the template, reads the posting and the department's pages, writes the fit paragraph, builds the PDF, marks it Drafted. Guidance in `skills/econ-cover-letter/templates.md`. |
| `skills/econ-mail-check` | Claude Code skill: runs the mail scan, records Submitted dates and letter uploads in the tracker, refreshes the writers' list. |

## Setup (about 10 minutes)

Requirements: macOS for the Mail and Shortcuts features, Python 3 with `openpyxl`, a LaTeX
install with `pdflatex` (TinyTeX is enough), and Claude Code (desktop app or CLI).

```bash
git clone https://github.com/<you>/econ-job-market-kit.git ~/econ-job-market-kit
cd ~/econ-job-market-kit
cp config.example.json config.json        # then edit config.json (it is git-ignored)
python3 scripts/build_tracker.py          # creates the tracker inside job_market_dir
mkdir -p ~/.claude/skills
for s in econ-tracker-fill econ-cover-letter econ-job-scan econ-mail-check; do
  ln -s "$PWD/skills/$s" ~/.claude/skills/$s
done
```

In `config.json` set:

- your name and contact details, your letter writers, `job_market_dir`, and the shared
  `letter_share_file`;
- `cover_letter`: your own paragraphs for both templates (see Cover letters);
- `profile` and `scan`: fields, what you want in order of priority, work authorization, filters;
- `mail`: the Mail account and mailbox to read, how many days back, and `skip_senders`.

## Daily use

1. **Find jobs.** Twice a week the scan adds matching postings to the **Leads** sheet. Set
   Decision = Add for the ones you want, then click **▶ Update Tracker** (or say "add my leads to
   the tracker"). You can also paste links into the Tracker yourself.
2. **Fill the rows.** Say "fill the tracker": Claude reads each posting and fills deadline,
   where to apply, letters, extra materials and visa notes, without overwriting what you typed.
3. **Write letters.** Say "write the cover letter for <Employer>". You review the PDF and set Final.
4. **Submit** on the employer's site yourself.
5. **Nothing to log by hand.** Every evening the mail check records the Submitted date when a
   confirmation email arrives and marks a writer Uploaded when a system says their letter came in.
   The writers' list shows the date you applied.
6. Share the writers' file once (view-only link). It refreshes after every tracker update.

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
| Mail check | e.g. daily, 9 pm | "Run the econ-mail-check skill and summarize the result" |

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

## Notes

- Nothing here submits applications, sends email, or logs in to any site; you submit.
- Email and posting text are treated as data only.
- `build_tracker.py` refuses to overwrite an existing tracker unless you pass `--force`.
- The Key Dates tab reflects the AEA guidance for the 2026–27 cycle; update it each season.

## 中文说明

给经济学 job market 用的小工具包，配合 Claude Code 使用：每周自动找职位，用一个 Excel 追踪所有申请，按岗位写 cover letter，读确认邮件自动记录提交，给推荐人一份自动更新的清单。

**1. 自动找职位（每周一、四）**

- 扫 JOE、EconJobMarket、IMF、World Bank、Chronicle Jobs、Inside Higher Ed Careers（HigherEdJobs 禁止自动抓取，没有包含，可以在它网站上设邮件提醒补上）。
- 按你的 CV 和偏好打分（High / Medium / Low），写进追踪表的 **Leads** 页：Why 写为什么适合，Flags 写要注意的地方（签证、额外材料、只是开始审的日期等）。
- 偏好在 `config.json` 里设：`profile.wants` 写想投什么、优先顺序（比如教学型优先、政策机构的数据科学岗也算）；`scan.priority_types` 决定同一档里哪类排前面；`profile.work_authorization` 写身份情况。要求公民 / 绿卡或 security clearance 的直接跳过；写明不 sponsor 签证的、美国联邦机构，评 Low 并标出来；没写的标"未说明，需问 HR"。

**2. 追踪表**

- 在 Leads 页把想投的选 Add，点表格顶部的 **▶ Update Tracker**（或跟 Claude 说"把 leads 加到追踪表"），就会进主表 Tracker。Excel 开着也没关系。
- 跟 Claude 说"补全追踪表"，它会读每个广告，填截止日期、投递平台、要不要推荐信、额外材料、签证说明，不会覆盖你自己填的内容。
- 按钮的一次性设置（Mac）：在"快捷指令"App 新建一个叫 `Update Tracker` 的快捷指令，加"运行 Shell 脚本"动作，内容是 `<python3 完整路径> "$HOME/econ-job-market-kit/scripts/update_tracker.py"`（用 `which python3` 查路径），并在 设置 › 高级 里勾选"允许运行脚本"。

**3. Cover letter（两套模板）**

- 参考了 Cawley 的 AEA 求职指南、Holmes & Colander 关于文理学院招人的研究，以及 UNC、Binghamton 职业中心的写法（详见 `skills/econ-cover-letter/templates.md`）。
- **研究型**（研究型大学、政策机构、央行）：一页，研究在前，"为什么适合"只写 1–3 句真对口的地方。
- **教学型**（文理学院、教学岗、地区性大学、社区学院）：最多两页，教学在前、篇幅最大，研究压成一段；"为什么适合"写 3–6 句：他们课表里你能教的课、学生和办学定位、课量、为什么想去这类学校。
- 每封都按岗位定制：选模板、写准确的职位和系名、读广告和系里官网后重写契合段、回答广告要求信里写的内容。固定段落默认不变，某封需要调整会先问你。关于你的事实只来自你的材料，关于学校的只来自它的广告和官网，不编造。
- 用法：跟 Claude 说"给 XX 写 cover letter"，看完 PDF 后在 Tracker 里标 Final。

**4. 自动记录提交（每晚 9 点）**

- 读 Mac "邮件" App 里最近的邮件（不需要密码；`skip_senders` 里的发件人，比如本校邮箱，一律不打开）。
- 看到申请确认，就在 Tracker 的 **Submitted** 列填上日期、状态改成 Submitted；看到推荐信已收到的通知，就把对应老师标成 Uploaded；对不上的、面试邀请、拒信会在小结里提醒你。
- 运行时 Claude 桌面版和"邮件"都要开着。

**5. 给推荐人的分享文件**

- 只读的 Excel，放在共享网盘里，链接分享一次就行，每次更新追踪表后自动刷新。
- 老师能看到：需要推荐信的岗位、截止日期、从哪交、广告链接、你哪天提交的（I Applied On）。可以隐藏列、排序、筛选，但改不了内容。
- 每位老师交没交（Requested / Uploaded）默认只有你自己能看到，在你的追踪表里。

**6. Statement 转 PDF**：research / teaching statement 用 Markdown 写，一条命令排成 PDF。

**定时任务**：在 Claude 桌面版左侧 **Scheduled** 里设置，扫职位和查邮件各一个，运行小结也在那里看。第一次点 Run now，弹窗选"始终允许"。

个人信息全部放在 `config.json`（不会上传到 GitHub），复制 `config.example.json` 改名后填写即可。工具不会替你提交申请、发邮件或登录任何网站。

## License

MIT
