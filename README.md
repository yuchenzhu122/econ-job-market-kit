# econ-job-market-kit

A small toolkit for the economics academic job market, built to work with Claude Code.
Paste posting links into a spreadsheet and let Claude fill in the rest; get a tailored
one-page cover letter per position; turn your research and teaching statements into
matching PDFs; and give your letter writers a list that updates itself.

[中文说明见下方](#中文说明)

## What's inside

| | |
|---|---|
| `scripts/build_tracker.py` | Builds an Excel tracker: one row per job, deadline countdown, academic / industry / government tracks, a **For Letter Writers** tab sorted by deadline, a summary tab, and the AEA key dates. |
| `scripts/make_letter.py` | One-page cover letter in two variants (`research` or `teaching` first). Your fixed paragraphs live in `config.json`; only a short "fit" paragraph changes per school. |
| `scripts/export_letter_list.py` | Writes a separate, view-only Excel file with only the positions that need letters (deadline, where to submit, link, each writer's status) to a shared Dropbox/OneDrive/Google Drive folder. Share its link once; re-running keeps the same file, so the link always shows the latest list. |
| `scripts/scan_postings.py` | Pulls current postings from JOE (XML export), EconJobMarket (public JSON feed), the IMF and World Bank career sites, and the Economics category RSS of Chronicle Jobs and Inside Higher Ed Careers (good for teaching-focused and regional colleges; HigherEdJobs blocks automated access and is not scanned), filters by rank, field, deadline and section, and skips ones already seen. |
| `scripts/leads.py` | Adds rated postings to a **Leads** sheet in the tracker, and moves the ones you mark Add into the Tracker. |
| `scripts/update_tracker.py` | One step, no Claude needed: moves Leads marked Add into the Tracker (guessing Apply Via and Letters? from the ad) and refreshes the letter-writer file. If Excel has the tracker open, it asks Excel to save and close it, then reopens it. The first run also adds a clickable **▶ Update Tracker** link at the top of the Tracker and Leads sheets, which runs it through a macOS Shortcuts shortcut (see below). |
| `scripts/mail_scan.py` | Reads recent mail through the Mail app already signed in on your Mac (no passwords), opens only emails that look like application-system or letter notifications (never senders in `mail.skip_senders`, e.g. your own university), and lets Claude record the Submitted date and each writer's Uploaded status in the tracker. |
| `scripts/md2pdf.py` | Converts a Markdown research or teaching statement into a PDF with the same letterhead. |
| `skills/econ-tracker-fill` | Claude Code skill: reads the links in your tracker and fills employer, position, deadline, where to apply, whether letters are needed, and extra materials. |
| `skills/econ-job-scan` | Claude Code skill: runs the scan, reads each new posting, rates fit (High / Medium / Low) against `profile` in config.json (ranking your `priority_types` first and checking visa / work-authorization rules), and writes the Leads sheet. Schedule it (e.g. Mon and Thu mornings) as a Claude desktop scheduled task. |
| `skills/econ-mail-check` | Claude Code skill: runs the mail scan, matches confirmations and letter notifications to tracker rows, updates them, and refreshes the letter writers' list (which shows the date you applied). Schedule it daily. |
| `skills/econ-cover-letter` | Claude Code skill: reads one posting, writes the fit paragraph, builds the letter, and marks it Drafted in the tracker. |

## Setup (about 10 minutes)

Requirements: Python 3 with `openpyxl`, a LaTeX install with `pdflatex` (TinyTeX is
enough), and Claude Code (desktop app or CLI).

```bash
git clone https://github.com/<you>/econ-job-market-kit.git ~/econ-job-market-kit
cd ~/econ-job-market-kit
cp config.example.json config.json        # then edit config.json (it is git-ignored)
python3 scripts/build_tracker.py          # creates the tracker inside job_market_dir
mkdir -p ~/.claude/skills
ln -s "$PWD/skills/econ-tracker-fill"  ~/.claude/skills/econ-tracker-fill
ln -s "$PWD/skills/econ-cover-letter"  ~/.claude/skills/econ-cover-letter
ln -s "$PWD/skills/econ-job-scan"      ~/.claude/skills/econ-job-scan
ln -s "$PWD/skills/econ-mail-check"    ~/.claude/skills/econ-mail-check
```

In `config.json` set your name and contact details, your letter writers, the folder where
your job market files live (`job_market_dir`), the fixed cover-letter paragraphs, and your
`profile` (fields, what you want, work authorization) for the job scan.

## Daily use

0. Twice a week, **"scan for jobs"** (or a scheduled task) adds new matching postings to the **Leads** sheet. Mark the ones you want **Add**, then click **▶ Update Tracker** at the top of the sheet (or say **"add my leads to the tracker"**).
1. Or paste posting links into the **Link** column of the tracker yourself.
2. In Claude Code: **"fill the tracker"**. Claude reads each posting and fills the row
   without overwriting anything you typed.
3. **"Write the cover letter for <Employer>"**. Claude writes the fit paragraph from the
   posting, builds the PDF, and sets Cover Letter = Drafted. You review and set Final.
4. Mark letter requests (Requested / Uploaded) and application status as you go.
5. Share the file at `letter_share_file` with your letter writers once (view-only link).
   Claude refreshes it after every tracker update, or run `python3 scripts/export_letter_list.py`.

## Job scan

| Source | How it is read | Best for |
|---|---|---|
| JOE | AEA's XML export | US and international academic, policy and nonacademic jobs |
| EconJobMarket | public JSON feed | international and policy jobs |
| Chronicle Jobs | Economics category RSS | liberal arts, regional and teaching-focused colleges |
| Inside Higher Ed Careers | Economics faculty RSS | same, plus some Asian and Middle East schools |
| IMF | Workday career site (public JSON) | Economist Program and other IMF jobs |
| World Bank Group | Cornerstone career site (public search) | economist, research and data jobs (titles filtered) |

HigherEdJobs blocks automated access, so it is not scanned; most of its economics faculty
ads also appear on Chronicle or Inside Higher Ed. If you want to be sure, set up a free
HigherEdJobs "Job Agent" email alert for Economics faculty jobs.

How a run works:

1. `scan_postings.py` fetches all four sources (about 2 minutes), drops postdoc, visiting,
   adjunct, part-time, senior-only, other-discipline and expired ads, merges the same job
   posted on several boards (the other links go into Flags), and skips anything seen
   before or already in your tracker. Filters live in `config.json` → `scan`.
2. Claude reads the rest, rates each one High / Medium / Low against `profile` in
   `config.json`, reads the full ad for High and Medium (eligibility, deadline, extra
   materials), and writes them to the **Leads** sheet with a one-line Why and Flags.
3. You set Decision = Add / Maybe / Pass, then click **▶ Update Tracker** (or say "add my
   leads to the tracker") to move the Add rows into the Tracker.

Preferences that shape the ratings, in `config.json`:

- `profile.wants`: the kinds of positions you want, in order of priority.
- `scan.priority_types`: position types listed first within each fit level (e.g.
  `["Teaching-focused"]`).
- `profile.work_authorization`: e.g. "needs H-1B sponsorship for US jobs". Ads that require
  citizenship or permanent residency, or a security clearance, are skipped. Ads that say they
  will not sponsor visas, and US federal agencies (which usually hire only citizens), are kept
  as Low with a flag so you can check them. Ads that say nothing get the flag "visa
  sponsorship not stated; ask HR".

To run it on a schedule, create a Claude desktop scheduled task (e.g. Mondays and
Thursdays at 8 am) whose prompt is "Run the econ-job-scan skill and summarize the result".
The scan state (`scan_state.json`), the raw candidates (`scan_new.json`) and Claude's
ratings (`scan_eval.json`) are kept next to the tracker.

One-click update from inside Excel (macOS): Excel's sandbox will not run scripts, but it can
open a Shortcuts link. In the **Shortcuts** app create a shortcut named exactly
`Update Tracker` with one **Run Shell Script** action:

```bash
/full/path/to/python3 "$HOME/econ-job-market-kit/scripts/update_tracker.py"
```

Use the full path of the Python that has openpyxl (`which python3` in Terminal); Shortcuts does
not load your shell profile. In Shortcuts › Settings › Advanced, turn on "Allow Running Scripts".
Optionally give it a keyboard shortcut. After the first run, the **▶ Update Tracker** link at the
top of the Tracker and Leads sheets runs it.

Statements: `python3 scripts/md2pdf.py research_statement.md "Research Statement" refs.tex`

## Notes

- Nothing here submits applications or logs in to any site; you submit.
- `build_tracker.py` refuses to overwrite an existing tracker unless you pass `--force`.
- The Key Dates tab reflects the AEA guidance for the 2026–27 cycle; update it each season.

## 中文说明

给经济学 job market 用的小工具包，配合 Claude Code 使用：

- **自动找职位**：每周自动扫 JOE、EconJobMarket、IMF、World Bank、Chronicle Jobs 和 Inside Higher Ed Careers（HigherEdJobs 禁止自动抓取，没有包含），按你的 CV 和偏好打分（High / Medium / Low），写进追踪表的 Leads 页；你选 Add 的会转进主表。
  - 结果在哪看：打开追踪表 Excel，第三个标签页 **Leads**。按 Fit 和截止日期排序，Why 写了为什么适合，Flags 写了要注意的地方（要 diversity statement、只是 review 开始日期、同一职位也挂在别的网站等）。
  - 怎么处理：在 Decision 一列选 Add / Maybe / Pass，然后点表格顶部的 **▶ Update Tracker**（或跟 Claude 说"把 leads 加到追踪表"），Add 的就会进主表，推荐人分享表也会一起刷新。Excel 开着也没关系，会自动存盘、更新、重新打开。
  - 按钮的一次性设置（Mac）：打开"快捷指令"App，新建一个名字叫 `Update Tracker` 的快捷指令，加一个"运行 Shell 脚本"动作，内容是 `<python3 的完整路径> "$HOME/econ-job-market-kit/scripts/update_tracker.py"`（在终端里用 `which python3` 查路径）；在快捷指令的 设置 › 高级 里勾选"允许运行脚本"。想要快捷键的话，在快捷指令的 ⓘ 详细信息里"添加键盘快捷键"。
  - 偏好设置：`profile.wants` 写想投的岗位类型和优先顺序，`scan.priority_types` 决定同一档里哪类排前面（比如教学型），`profile.work_authorization` 写身份情况。要求公民/绿卡或 security clearance 的直接跳过；写明不 sponsor 签证的、美国联邦机构，评 Low 并在 Flags 里标出来；没写的标"未说明，需问 HR"。
  - 每次运行的简报在 Claude 桌面版左侧 **Scheduled** 里对应任务的运行记录中。
- **自动记录提交**：每天读一遍 Mac "邮件" App 里的邮件（不需要密码；本校邮箱发来的邮件不会打开），看到申请确认就在追踪表填上提交日期、状态改成 Submitted，看到推荐信已收到的通知就把对应老师标成 Uploaded；给老师的分享表会显示你哪天交的。
- **给推荐人的分享文件**：只包含需要推荐信的职位，放在共享网盘里，链接分享一次就行，每次更新追踪表后自动刷新。
- **追踪表**：把职位链接贴进 Link 一列，跟 Claude 说"补全追踪表"，它会读链接并填好学校、职位、截止日期、投递平台、是否要推荐信、额外材料。自带"给推荐人看"的页面，按截止日期自动排序。
- **Cover letter**：说"给 XX 写 cover letter"，它会读职位、写一段"为什么适合这个学校"，生成一页 PDF（研究型 / 教学型两个版本），并在追踪表里标为 Drafted。
- **Statement 转 PDF**：research / teaching statement 用 Markdown 写，一条命令排成 PDF。

个人信息全部放在 `config.json`（不会上传到 GitHub），复制 `config.example.json` 改名后填写即可。

## License

MIT
