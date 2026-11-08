---
name: daily-jobs
description: Run when the user says "daily jobs" (also "today's jobs", "find jobs today", "daily jobs 5"), or "applied <numbers or companies>" / "skip <numbers>" right after a daily-jobs list. Research-only daily routine for people who apply by hand. Every day it finds 3 to 5 solid jobs (default 5) that are remote and open to the user's home country, at real, healthy companies in their target countries, paying at least their pay floor and fitting their real work (profile.json, accomplishments, skill set). It searches the free job APIs every day plus a different set of browser sources each weekday, checks each job on the company's own page, and prepares one ready-to-apply pack per job (job post, company research, fit and pay notes, tailored resume PDF, short cover note or email text, answers to likely form questions) in apply/<me>/daily/<YYYY-MM-DD>/. Claude never fills or submits forms, never creates drafts and never sends anything. When the user says which ones they applied to, it records them in the shared applied ledgers, so the 6-month block works across every job-apply skill. All shared rules in job-apply-shared/RULES.md apply except where this page changes them.
---

# Daily Jobs (research only, 3 to 5 a day)

Trigger: **`daily jobs`** (default 5), `daily jobs 3`, `daily jobs 4 only payments`, `today's jobs`.
Follow-up: **`applied 1, 3`** / `applied Acme` (record), **`skip 2 <reason>`** (don't show again), **`daily jobs status`** (this week's numbers).

Goal: a short list the user can apply to by hand in about an hour. **Quality over count.** 3 solid jobs beat 5 weak ones. Never pad.

## What this skill never does

- Never fills, uploads to or submits a form, never creates a Gmail draft, never sends an email, DM or connection request. It only reads pages.
- Never creates accounts on job boards. Login walls, CAPTCHAs and checks go to the user, or the source is skipped for the day.
- Never claims a skill on a resume or in a note that the user's files don't support (RULES "Truth only").

## Step 0: Start

```bash
M="python .claude/skills/job-apply-shared/scripts/me.py"
A="python .claude/skills/job-apply-shared/scripts/apply.py"
D="python .claude/skills/daily-jobs/scripts/daily.py"
$M check          # must print ready; otherwise offer profile-setup and stop
$M date           # today
$D status         # picks still waiting for an answer, and this week's numbers
```

Read from `skillsets-and-contributions/<me>/`: `profile.json` (roles, stack, domains, pay, countries, and when present `company_size`, `quality_bar`, `realism`, `_workflow`, `_domains_rule`), `contributions/` (accomplishments), `skills/my-skill-set.md`, `proof-map.md`, `resume/resume-base.json`, `profile-answers.md`.

**Open picks first.** If `$D status` shows picks from earlier days still `picked`, list them in one line each and ask once: "Did you apply to any of these?" Record the answer (Step 7) before searching. Don't block the run if the user doesn't answer.

## Step 1: Search (APIs daily, browser sources by weekday)

**Every day, APIs** (fast, no browser, polite gaps built in):
```bash
python .claude/skills/job-apply-shared/scripts/fetch_jobs.py all <scratchpad>/daily/api.json --days 14
```
(Hacker News, Himalayas with the home-country filter, Remotive, RemoteOK, Jobicy, We Work Remotely.)

**Plus one browser block per weekday** (user's local day, `$M date`). Search each the way its own skill's Step 1 says, read-only, within [HUMAN-BROWSING.md](../job-apply-shared/HUMAN-BROWSING.md) budgets, and stop a site at its first check:

| Day | Sources (skill whose Step 1 to follow) |
|---|---|
| Mon | VC portfolio job boards, company ATS search ([other-job-apply](../other-job-apply/SKILL.md) B and C) |
| Tue | Newly funded startups → careers pages (other-job-apply E), Y Combinator ([yc-job-apply](../yc-job-apply/SKILL.md)) |
| Wed | LinkedIn Jobs, external apply only ([linkedin-job-apply](../linkedin-job-apply/SKILL.md)) |
| Thu | Wellfound ([wellfound-job-apply](../wellfound-job-apply/SKILL.md)), stack boards and remote boards (other-job-apply B) |
| Fri | LinkedIn "we're hiring" posts ([linkedin-post-apply](../linkedin-post-apply/SKILL.md)), X / Twitter ([twitter-job-apply](../twitter-job-apply/SKILL.md)) |
| Sat | Indeed and remote boards (other-job-apply B) |
| Sun | Remote-first company lists (other-job-apply F), company ATS search (other-job-apply C) |

The user can override: `daily jobs only hn, yc` or `daily jobs skip linkedin`. If the browser isn't connected, run the APIs only and say so.

**Small-company mode** (profile.json `company_size.max_employees` is 100 or less). Big remote-first companies dominate the boards, so search where small teams post:
- **Every day, add one small-startup source** on top of the weekday block, rotating: HN "Who is hiring" (founders post there), Y Combinator Work at a Startup (filter team size 1-50, remote), Wellfound (filter company size 1-10, 11-50), newly funded startups → careers pages (other-job-apply E), VC portfolio boards filtered to seed and Series A.
- **Search words:** add `founding engineer`, `first engineer`, `early-stage`, `seed`, `Series A`, `small team` to the role queries.
- **Skip feeds of companies known to be over the size limit** (e.g. the Ashby/Greenhouse feeds of large remote-first companies). Don't spend checks on them.

Build searches from their `target_roles`, `stack.terms`, `job_search` queries and `domains` (plus `job_search.domain_queries` when present). Domains widen the search and raise the rank. They don't filter unless the profile says so.

## Step 2: Filter

Drop anything already handled:
```bash
$D seen "<job url>" "<company>" "<title>"      # SKIP if picked or skipped in the last 60 days
$A check "<job url>" "<company>" "<title>" "<apply url>"   # SKIP if applied from any source in 6 months
```

Then keep a job only if it passes **all** the RULES Step 1 common checks (stack, experience, proof fit, remote worldwide or home country named on the **company's own page** with the proving sentence quoted, company country via `$A country`, pay by RULES 1c, real company, not applied), plus:

- **Fresh:** posted in the last 14 days, or profile.json `freshness_days` when set (30 for a company careers page with no date, if it's clearly still open).
- **Applies on the company's side:** company form, ATS or an email address. Skip Easy Apply only, paid boards, freelance marketplaces, vetting platforms (Toptal, Turing, Andela, Arc, Crossover, Lemon.io, Proxify), and complex systems (Workday, Taleo, iCIMS) unless the user asked for them.
- **Company size** (when profile.json `company_size` is set): headcount between `min_employees` and `max_employees`. Check it on the company's LinkedIn page, team page, YC or Wellfound profile, or Himalayas "employee count", and note the source. Over the limit: drop. Unknown after two sources: drop.
- **Quality bar** (when profile.json `quality_bar` is set): the company meets it, with each point sourced.
- **Realistic fit** (when profile.json `realism` is set): count the post's must-haves with no proof in the user's files. More than `realism.max_hard_gaps`: drop. Also drop anything the `realism.note` rules out (e.g. 5+ years in a language they barely used, a people-manager-only or staff role above their record, domain experience they lack). Don't keep a job "as a stretch" in the picks. At most one stretch job may be mentioned at the end of the report, labelled as such.

## Step 3: Solid-company check

"Solid" means the company is real, healthy and actually hires remote people abroad. Score each survivor 0 to 2 on each line and note the source of every point in `company.md`:

| Signal | 2 | 1 | 0 |
|---|---|---|---|
| Money | raised in the last 24 months, or public revenue/profit | older funding or clear paying customers | nothing found |
| Product | live product with real users (customers, reviews, changelog in the last 3 months) | live site, little activity | landing page only |
| Team | 15+ people on LinkedIn or the team page, growing (small-company mode: 10 to `max_employees`, growing, with a technical founder or CTO) | 5 to 14 (small-company mode: 5 to 9) | under 5 or unknown |
| Remote abroad | team members already in Asia or many countries, or uses Deel/Remote.com/Oyster | remote-first, but team in one region | no sign |
| Hiring health | several open roles, no recent layoffs | one role | layoffs in the last 6 months, or reposted for months |

**Keep only scores of 6 or more out of 10.** Below 6 goes in the report's "seen but not solid" line with the reason. Glassdoor or similar rating under 3.0 with recent complaints about unpaid contractors is an automatic drop.

## Step 4: Rank and pick

Rank by: realistic fit first (fewest gaps, most main responsibilities matched by real work), then pay (`pay_usd_month`, RULES 1c, counted only up to their `pay.max_month`: a job paying more than that ranks the same as one paying exactly that), then solid score, then proof fit (how many main responsibilities match real work), with a bonus for a domain in their `domains` and for posts under 3 days old. Take the top N (default 5, minimum 3 if 3 good ones exist). If fewer than 3 pass, show what passed and say which sources were thin today. Never lower the bars to reach the number.

## Step 5: Build one pack per pick

Folder: `apply/<me>/daily/<YYYY-MM-DD>/<NN>-<company-slug>/` (NN = rank, 01 to 05). In it:

1. **`job-description.md`:** title, company, where it was found, the company's own job URL and apply URL, posted date, the full post text, the **quoted remote sentence**, and a **Pay** section (posted or estimated, with sources).
2. **`company.md`:** RULES Step 5 notes (description, domain, culture, job description match with real numbers, one sincere thing to praise), plus the solid-company table with scores and sources, HQ country, size, funding, and the hiring manager's or founder's name if shown.
3. **Tailored resume:** [custom-resume skill](../custom-resume/SKILL.md) in the person's resume style (its "Resume style" section: classic Steps 2 to 6, or modern), plus their `resume/resume-guide.md` when present, built into this folder:
   ```bash
   python .claude/skills/custom-resume/scripts/build_resume.py <folder>/content.json <folder>/<resume_file>
   ```
   plus its `report.md`. Open the PDF and check it (one page, nothing cut off).
4. **`apply-kit.md`** (what the user pastes while applying by hand), every text per [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md):
   - **How to apply:** the method (form, email, DM) and the exact link.
   - **Cover note:** for a form's cover letter field, written per RULES 6c. For an email apply, the 3-paragraph email per RULES 6b (check with `$A email <file>`), saved as `email.md` next to it.
   - **Likely form answers:** "Why us?", "Tell us about a project", salary (one figure inside their `pay` range from 1c, never above `pay.max_month`, in the form's currency and period), notice period, visa and work authorization from `profile-answers.md`. An `ASK` value stays `ASK` with a note to answer it once in chat. Check every free-text answer with `$A text "<answer>"`.
   - **Watch out:** anything odd (time zone overlap asked, assessment step, a gap between the post and their stack). Name stack gaps honestly; never hide them.

Then record each pick:
```bash
$D add '{"rank":1,"company":"...","title":"...","source":"himalayas","job_url":"...","apply_url":"...","company_country":"...","pay_range":"...","pay_usd_month":5500,"solid":8,"folder":"apply/<me>/daily/<date>/01-acme"}'
```
(`source` is the apply.py source name: linkedin, post, twitter, hn, himalayas, wellfound, yc or others.)

## Step 6: Report (short, in chat)

One table, best first:

| # | Company · role | Size | Pay / month | Solid | Why it fits (2 real proofs) | Gaps | Apply via | Pack |

Then one line each: sources searched today (and any that failed or were skipped), how many jobs were seen, and "seen but not solid" or "close but failed X" (max 5, one reason each). End with: "Apply by hand, then tell me `applied 1, 3`."

## Step 7: Record what the user applied to

When the user says `applied <numbers or company names>` (numbers refer to the latest list unless a date is given):
```bash
$D applied <date> <rank> [<rank>...]
```
This marks the picks `applied` and writes each into the shared ledger of its source (through apply.py `add`, status `applied`, `method` manual), so every job-apply skill blocks it for 6 months.

`skip <numbers> <reason>` → `$D skip <date> <rank> "<reason>"`. Skipped jobs aren't shown again for 60 days; the folder stays as a record.

## Step 8: Saved locally

`apply/<me>/` is git-ignored, so nothing is committed. End the report with where the packs are (`apply/<me>/daily/<date>/`).

## Weekly rhythm (tips for the user, not rules)

- Run `daily jobs` once a day, apply within 24 hours (fresh posts get read first).
- After 2 weeks, `daily jobs status` shows which sources gave the jobs you actually applied to. Tell Claude to drop weak sources from the weekday table in your profile notes.
