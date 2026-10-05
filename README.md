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
| `scripts/scan_postings.py` | Pulls current postings from JOE (XML export) and EconJobMarket (public JSON feed), filters by rank, field, deadline and section, and skips ones already seen. |
| `scripts/leads.py` | Adds rated postings to a **Leads** sheet in the tracker, and moves the ones you mark Add into the Tracker. |
| `scripts/md2pdf.py` | Converts a Markdown research or teaching statement into a PDF with the same letterhead. |
| `skills/econ-tracker-fill` | Claude Code skill: reads the links in your tracker and fills employer, position, deadline, where to apply, whether letters are needed, and extra materials. |
| `skills/econ-job-scan` | Claude Code skill: runs the scan, reads each new posting, rates fit (High / Medium / Low) against `profile` in config.json, and writes the Leads sheet. Schedule it (e.g. Mon and Thu mornings) as a Claude desktop scheduled task. |
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
```

In `config.json` set your name and contact details, your letter writers, the folder where
your job market files live (`job_market_dir`), and the fixed cover-letter paragraphs.

## Daily use

0. Twice a week, **"scan for jobs"** (or a scheduled task) adds new matching postings to the **Leads** sheet. Mark the ones you want **Add**, then say **"add my leads to the tracker"**.
1. Or paste posting links into the **Link** column of the tracker yourself.
2. In Claude Code: **"fill the tracker"**. Claude reads each posting and fills the row
   without overwriting anything you typed.
3. **"Write the cover letter for <Employer>"**. Claude writes the fit paragraph from the
   posting, builds the PDF, and sets Cover Letter = Drafted. You review and set Final.
4. Mark letter requests (Requested / Uploaded) and application status as you go.
5. Share the file at `letter_share_file` with your letter writers once (view-only link).
   Claude refreshes it after every tracker update, or run `python3 scripts/export_letter_list.py`.

Statements: `python3 scripts/md2pdf.py research_statement.md "Research Statement" refs.tex`

## Notes

- Nothing here submits applications or logs in to any site; you submit.
- `build_tracker.py` refuses to overwrite an existing tracker unless you pass `--force`.
- The Key Dates tab reflects the AEA guidance for the 2026–27 cycle; update it each season.

## 中文说明

给经济学 job market 用的小工具包，配合 Claude Code 使用：

- **自动找职位**：每周自动扫 JOE 和 EconJobMarket，按你的 CV 和偏好打分（High / Medium / Low），写进追踪表的 Leads 页；你选 Add 的会转进主表。
- **给推荐人的分享文件**：只包含需要推荐信的职位，放在共享网盘里，链接分享一次就行，每次更新追踪表后自动刷新。
- **追踪表**：把职位链接贴进 Link 一列，跟 Claude 说"补全追踪表"，它会读链接并填好学校、职位、截止日期、投递平台、是否要推荐信、额外材料。自带"给推荐人看"的页面，按截止日期自动排序。
- **Cover letter**：说"给 XX 写 cover letter"，它会读职位、写一段"为什么适合这个学校"，生成一页 PDF（研究型 / 教学型两个版本），并在追踪表里标为 Drafted。
- **Statement 转 PDF**：research / teaching statement 用 Markdown 写，一条命令排成 PDF。

个人信息全部放在 `config.json`（不会上传到 GitHub），复制 `config.example.json` 改名后填写即可。

## License

MIT
