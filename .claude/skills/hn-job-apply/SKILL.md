---
name: hn-job-apply
description: Run when the user says "hn job apply" (or "hacker news job apply"). Also "apply job from hn", and any of these with "without agent" (e.g. "apply job from hn without agent") - this skill always runs in the main session (default mode), never with subagents. Follows the shared job-apply rules (job-apply-shared/RULES.md), the same as every source, but the only source is Hacker News "Ask HN - Who is hiring?" (the current and previous monthly threads), where founders and engineers post their own jobs. Finds posts matching their accomplishments, skills and resume (their stack and home country, from profile.json) that are remote worldwide, at companies in their target countries (profile.json, never their blocked countries), paying at least their pay floor (profile.json `pay.min_month`). Applies with a tailored resume per job through the company's form, or with a specific 3-paragraph email to the poster saved as a Gmail draft. Forms are submitted only after the user's go-ahead, and Claude never sends emails or posts on HN. Only applied jobs are saved in apply/<me>/hackernews/<YYYY-MM-DD>/<company-name>/. A job applied to from any source is blocked for 6 months in all of them.
---

# Hacker News Job Apply

Trigger: **`hn job apply`** (or `hacker news job apply`). Optional: a number. Default target: **20 per run**, never padded.

Also triggered by **`apply job from hn`**. **Default mode, no agents:** this skill always runs in the main session, step by step, and never calls the Agent tool, whether or not the user adds "without agent" (e.g. `apply job from hn without agent`). See "Run mode" in [RULES.md](../job-apply-shared/RULES.md).

**Why this source is valuable:** posts come from people inside the company (recruiting firms are banned from the thread), and many list salary, remote terms and a direct email to a founder or engineer. Replies from engineers land with people who read them.

## Shared rules

**Read [job-apply-shared/RULES.md](../job-apply-shared/RULES.md) first and follow it**, with the changes on this page. Everything else applies exactly as written there: all rules (forms submitted only after the user's yes, Claude never sends email, passwords, truth only, human writing, no address/phone in committed files), the common job checks in RULES Step 1 (stack, experience, proof fit, **remote worldwide**, **company country**, **pay ≥ their floor** (profile.json `pay.min_month`), real company, **6-month block**), Step 0 and Steps 2–9, and `skillsets-and-contributions/<me>/profile-answers.md`. Every search and every piece of writing comes from the accomplishments file (`skillsets-and-contributions/<me>/contributions/`), skill set (`skillsets-and-contributions/<me>/skills/my-skill-set.md`) and resume (`skillsets-and-contributions/<me>/resume/<resume_file>`).

```bash
A="python .claude/skills/job-apply-shared/scripts/apply.py --source hn"   # ledger: apply/<me>/hackernews/applied.csv
F="python .claude/skills/job-apply-shared/scripts/fetch_jobs.py"
```

**HN is read-only.** Claude never comments, replies or votes on Hacker News.

## Changed Step 1: Find jobs in the "Who is hiring?" threads

1. Fetch and pre-filter the current and previous month's threads:
   ```bash
   $F hn <scratchpad>/hn/hn.json --days 45
   ```
   Each result has the company, role, location line, the comment URL (`news.ycombinator.com/item?id=...`), links, emails in the post, and `worldwide`: `yes` or `check`. The script already dropped posts whose titles don't fit their profile.json `job_search` words and posts marked ONSITE, REMOTE (US), REMOTE (EU) and similar.
2. Read every kept post in full (open the comment URL). HN posts use `Company | Role | Location | REMOTE | Salary | URL`. Decide:
   - **Remote worldwide:** "REMOTE (Global)", "Worldwide", "Anywhere", "any timezone". A bare "REMOTE" is `check`: confirm on the company's careers page, and skip if it can't be confirmed. "REMOTE (US)", "US timezones", "NYC or remote" mean region-locked, so skip.
   - Then the common job checks in RULES Step 1, using the company's site for country and pay. Many HN posts give salary directly. Use it for 1c.
   - Skip "Who wants to be hired?" threads and replies from people who aren't the company.
3. Rank by pay, then proof fit. Take the top N.

## Changed Step 2: How to apply

- The post links to a careers page or ATS → **form** (RULES Steps 2 and 6a).
- The post gives an email (often a founder's), sometimes obfuscated like `jane [at] co.com` → **email** to that address (RULES 6b). Fix the obfuscation, and use the subject the post asks for when it gives one (`--fixed-subject`).
- Both → follow what the post prefers. If it doesn't say, use the email, since a note to a founder is the strength of this source.

## Changed Step 3 and 6b

- `job-description.md` starts with the HN comment URL, the thread title (e.g. "Ask HN: Who is hiring? (September 2026)"), the poster's HN username and date, then the full post text, then the careers-page description if any.
- Email: greet the poster by first name when the post or the company site shows it. Paragraph 1 may refer to their HN post in one short line. All other 6b rules apply unchanged.

## Changed Steps 8 and 9

- Folder: **`apply/<me>/hackernews/<YYYY-MM-DD>/<company-name>/`**. Record with `$A add` and set `linkedin_url` to the HN comment URL.
- Commit: `git add apply/<me>/hackernews` and use the message `<me>: apply (hn): <date time> — <N> applied (<companies>)` (date via `me.py stamp`).

## Report

Same as RULES, plus which month's threads were read, how many posts the fetcher kept, and how many were confirmed worldwide.
