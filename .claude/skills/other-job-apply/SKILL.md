---
name: other-job-apply
description: Run when the user says "other job apply" (or "job apply others"). Also "apply job from others", and any of these with "without agent" (e.g. "apply job from others without agent") - this skill always runs in the main session (default mode), never with subagents. Follows the shared job-apply rules (job-apply-shared/RULES.md), the same as every source, but the jobs come from sources no other apply skill covers - remote job boards and APIs (Remotive, RemoteOK, We Work Remotely, Jobicy, Welcome to the Jungle, 4dayweek, Indeed, and others), company ATS boards (Greenhouse, Lever, Ashby, Workable...), company careers pages, and the careers pages of newly funded startups (fundedstartupsdaily.com, projectstartups.com). It never uses LinkedIn, X/Twitter, Hacker News, Himalayas, Wellfound or Y Combinator, which have their own skills. Finds all jobs that match their accomplishments, skills and resume, remote worldwide, at companies in their target countries (profile.json, never their blocked countries), paying at least their pay floor (profile.json `pay.min_month`). Applies to up to 20 per run with a tailored resume per job, through the company's form or a 3-paragraph email saved as a Gmail draft. Forms are submitted only after the user's go-ahead, and Claude never sends emails. Only applied jobs are saved in apply/<me>/others/<YYYY-MM-DD>/<company-name>/ and recorded in apply/<me>/others/applied.csv. A job applied to from any source is blocked for 6 months in all of them.
---

# Other Job Apply (sources without their own skill)

## Excluded sources (never use them here)

These sources have their own skills, so this skill **never searches them, never takes jobs from them, and never applies through them**:

| Excluded source | Its own skill |
|---|---|
| LinkedIn Jobs and LinkedIn posts | `linkedin job apply`, `linkedin post apply` |
| X / Twitter | `twitter job apply` |
| Hacker News "Who is hiring?" | `hn job apply` |
| Himalayas (himalayas.app) | `himalayas job apply` |
| Wellfound / AngelList (wellfound.com, angel.co) | `wellfound job apply` |
| Y Combinator (workatastartup.com, ycombinator.com/jobs) | `yc job apply` |

- A job found on an allowed board whose only link goes to an excluded site (e.g. a Wellfound or Himalayas listing, an HN comment, a tweet, a LinkedIn job) is **dropped**. Leave it for that source's skill.
- A job found on an allowed board that links to the **company's own** careers page or ATS is fine, even if the same job is also posted on an excluded site. The 6-month block stops a double application.
- Company ATS searches (C) must not use `site:` queries for the excluded domains.
- In the report, mention excluded-source jobs only as "left for `<skill>`".

Trigger: **`other job apply`**. Optional: a number (`other job apply 10`) or `all`. Default: collect **every** matching job from all sources, list them all in the report, and apply to the **top 20** this run. Never pad with jobs that fail the filters.

Also triggered by **`apply job from others`**. **Default mode, no agents:** this skill always runs in the main session, step by step, and never calls the Agent tool, whether or not the user adds "without agent" (e.g. `apply job from others without agent`). See "Run mode" in [RULES.md](../job-apply-shared/RULES.md).

## Shared rules

**Read [job-apply-shared/RULES.md](../job-apply-shared/RULES.md) first and follow it**, with the changes on this page. Everything not changed here applies exactly as written there, for every source:

- All rules: forms submitted only after the user's yes, Claude never sends email, the password rules, truth only, human writing, and never saving their address or phone number in committed files.
- The common job checks (RULES Step 1): stack, experience, proof fit, **remote worldwide**, **company country** (their target countries in profile.json; never their blocked countries), **pay ≥ their floor** (profile.json `pay.min_month`) by market analysis (1c), real company, and the **6-month block**.
- Step 0 (checking earlier email drafts) and Steps 2–9: reading the application page, staging, custom resume, company research and bug hunt, filling forms (address file, profile photo, salary from 1c), 3-paragraph emails as Gmail drafts, the review gate, saving, and commit.
- `skillsets-and-contributions/<me>/profile-answers.md`.

**Helper, always with `--source others`:**
```bash
A="python .claude/skills/job-apply-shared/scripts/apply.py --source others"
$A check "<job page url>" "<company>" "<title>" "<external apply url>"   # blocked 6 months across ALL sources
$A country "<country>"
$A email <email.md> [--fixed-subject]
$A text "<answer>"
$A drafts
$A add '<json row>'     # writes apply/<me>/others/applied.csv; linkedin_url = the job page URL where it was found
$A set "<job page url>" applied|email-draft|withdrawn
```
(The ledger column is still called `linkedin_url` for all sources. For this skill it holds the job-board or careers-page URL.)

## Changed Step 1: Find jobs outside LinkedIn

Build every search from their real work (accomplishments file, skill set, resume): roles (profile.json `target_roles`), stack (`stack.terms`) and the domains of their projects (`domains`, `proof-map.md` section 1).

Go through **all** of these sources, and note in the report any source that failed:

**A. Job board APIs and feeds.** Run the shared fetcher on **these sources only**: Remotive, RemoteOK, Jobicy and We Work Remotely. **Never `all`**, which would pull in Hacker News and Himalayas. It keeps titles that fit their profile.json `job_search` words, drops region-locked ones, de-duplicates, and marks each `worldwide: yes | check`:
```bash
python .claude/skills/job-apply-shared/scripts/fetch_jobs.py remotive,remoteok,jobicy,wwr <scratchpad>/others/all.json --days 30
```

**B. Job boards read in the browser or with WebFetch:** Welcome to the Jungle (Otta), 4dayweek.io, Remote Rocketship, Remote.co, JustRemote, NoDesk, DynamiteJobs, EU Remote Jobs, Landing.jobs, Built In (remote filter), Working Nomads, Arbeitnow, Jobgether (filter by their home country), startup.jobs (remote), Jobspresso, Pangian, Remote First Jobs, Glassdoor (remote filter), plus the stack boards that match their profile.json `stack.terms` (e.g. LaraJobs for Laravel, python.org/jobs for Python, Golang Cafe for Go). Read only. Don't create accounts on job boards just to browse. (Not Wellfound or Y Combinator, which are excluded.)

**Indeed** (indeed.com, browser): search with `remote` as the location and their `target_roles` / `stack.terms` as keywords, last 14 days. Keep only posts whose "Apply on company site" link goes to the company's own careers page or ATS; skip "Easily apply" / Indeed Apply posts and staffing agencies. Indeed is quick to show checks, so follow HUMAN-BROWSING.md and stop at the first one.

**C. Company ATS boards directly** (freshest, often not on boards). WebSearch, keeping posts from the last 30 days:
- `"remote" ("worldwide" OR "anywhere") <profile.json job_search.ats_query> site:jobs.ashbyhq.com`, e.g. with `("node.js" OR "nestjs" OR "typescript")`
- the same with `site:boards.greenhouse.io`, `site:job-boards.greenhouse.io`, `site:jobs.lever.co`, `site:apply.workable.com`, `site:*.recruitee.com`, `site:*.teamtailor.com`, `site:*.breezy.hr`.

**D. Their own lists:**
- Careers pages of founders/CTOs who accepted their LinkedIn requests (`linkedin/<me>/send-connection/*/`, status `accepted`). Use their **own careers page** only, not their LinkedIn, Wellfound or YC listings.

**E. Newly funded startups → their careers pages** (companies that just raised hire soon, often before posting on boards). These sites list companies, not jobs:
- fundedstartupsdaily.com: Today's Raises and This Week, or `/raises/<industry>/` (e.g. `/raises/fintech/`), each row's "web" link goes to the company site.
- projectstartups.com/pages/: `/pages/<market>/`, `/pages/<market>-<stage>/` (e.g. `/pages/fintech-seed/`, `/pages/saas-series-a/`).

Pick the industries that match their profile.json `domains` first, then general SaaS, fintech and AI. Keep startups based in their target countries that raised in the last 90 days. For each, open the company's **own** careers page or ATS (Ashby, Greenhouse, Lever, Workable...) and keep engineering roles that pass the checks below. Skip a startup with no careers page; it can go to outreach instead. Budget: at most 40 company sites per run.

**Merge and de-duplicate** across sources (the same job often appears on 3–4 boards). Keep the company's own posting as the job's main URL when it exists. Then drop anything whose only apply route is an excluded source.

**Keep a job only if all of these hold:**
1. **Applies on the company's side:** the company's own careers page or ATS form, or an email address. A board's "Apply" button that redirects to the company is fine. **Skip** boards that make you pay or subscribe to apply (e.g. FlexJobs-style), freelance marketplaces (Upwork, Fiverr, Freelancer, since those are client work, not jobs), and vetting marketplaces that need a long profile and tests (Toptal, Turing, Andela, Arc, Crossover).
2. The common job checks in RULES Step 1 all pass. The **company's own job page** decides remote-worldwide, and the board's tag alone isn't enough. Quote the proving sentence.
3. **Scam and junk check:** skip posts that ask for any payment, only allow contact through Telegram/WhatsApp, use a free email domain while claiming to be a large company, or have no real company site.
4. **Fresh:** posted in the last 30 days and still open on the company's page.

**Rank** all kept jobs by pay (`pay_usd_month`), then proof fit. List **all** of them in the report. Apply to the top N (20 by default) this run. The rest stay listed for the next run.

## Changed Step 3: Staging and the job description

Same as RULES Step 3, plus: at the top of `job-description.md` record **where it was found** (board name + URL), the **company's own job URL**, and the posted date. Use the full text from the company's own page.

## Changed Step 6b: Email

Same as RULES 6b. The greeting uses the hiring contact's first name when the post or the company's team page names one, otherwise "Hi <Company> team,".

## Changed Step 8: Where applied jobs are saved

- Folder: **`apply/<me>/others/<YYYY-MM-DD>/<company-name>/`** (local date `python .claude/skills/job-apply-shared/scripts/me.py date`; add the role slug if the folder exists).
- Files: as in RULES Step 8 (`job-description.md`, `<resume_file>`, `content.json`, `report.md`, `company-notes.md`, `application.md`, plus `email.md` when applied by email).
- Record: `$A add '{"company":"...","title":"...","company_country":"...","pay_range":"...","pay_usd_month":"...","linkedin_url":"<job page url where found>","apply_url":"<company apply url>","method":"form|account|email","folder":"apply/<me>/others/<date>/<company-name>","status":"applied|email-draft"}'`

## Changed Step 9: Commit and push

```bash
git add apply/<me>/others
git commit -m "<me>: apply (others): $(python .claude/skills/job-apply-shared/scripts/me.py stamp) — <N> applied (<company list>)"
git push
```

## Report

Same as RULES, plus:
- Jobs found per source (and any source that failed).
- **All matching jobs found**, ranked, with the ones applied to this run marked and the rest left for the next run (company, title, country, pay, link).
- Skipped jobs, one line each with the reason (not worldwide, country, pay, stack, marketplace or paid board, scam, closed, left for another skill).
