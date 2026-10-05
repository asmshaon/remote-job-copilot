---
name: himalayas-job-apply
description: Run when the user says "himalayas job apply". Also "apply job from himalayas", and any of these with "without agent" (e.g. "apply job from himalayas without agent") - this skill always runs in the main session (default mode), never with subagents. Follows the shared job-apply rules (job-apply-shared/RULES.md), the same as every source, but the only source is Himalayas (himalayas.app), whose API can return only jobs open to candidates in their home country. Finds jobs matching their accomplishments, skills and resume (their stack, from profile.json) that are remote worldwide (or explicitly include their home country), at companies in their target countries (profile.json, never their blocked countries), paying at least their pay floor (profile.json `pay.min_month`). Applies with a tailored resume per job on the company's own site, or with a 3-paragraph email saved as a Gmail draft. Forms are submitted only after the user's go-ahead, and Claude never sends emails. Only applied jobs are saved in apply/<me>/himalayas/<YYYY-MM-DD>/<company-name>/. A job applied to from any source is blocked for 6 months in all of them.
---

# Himalayas Job Apply

Trigger: **`himalayas job apply`**. Optional: a number. Default target: **20 per run**, never padded.

Also triggered by **`apply job from himalayas`**. **Default mode, no agents:** this skill always runs in the main session, step by step, and never calls the Agent tool, whether or not the user adds "without agent" (e.g. `apply job from himalayas without agent`). See "Run mode" in [RULES.md](../job-apply-shared/RULES.md).

**Why this source is valuable:** Himalayas lists location restrictions per job, and its API filters by candidate country. Querying with `country=<home_country>` (profile.json) returns only jobs they're allowed to take, which removes the most common reason remote jobs are closed to them. Many listings show salary.

## Shared rules

**Read [job-apply-shared/RULES.md](../job-apply-shared/RULES.md) first and follow it**, with the changes on this page. Everything else applies exactly as written there: all rules, common job checks in RULES Step 1 (including **company country**, **pay ≥ their floor** (profile.json `pay.min_month`) and the **6-month block**), Step 0 and Steps 2–9, and `skillsets-and-contributions/<me>/profile-answers.md`. Searches and writing come from the accomplishments file (`skillsets-and-contributions/<me>/contributions/`), skill set (`skillsets-and-contributions/<me>/skills/my-skill-set.md`) and resume (`skillsets-and-contributions/<me>/resume/<resume_file>`).

```bash
A="python .claude/skills/job-apply-shared/scripts/apply.py --source himalayas"   # ledger: apply/<me>/himalayas/applied.csv
F="python .claude/skills/job-apply-shared/scripts/fetch_jobs.py"
```

## Changed Step 1: Find jobs on Himalayas

1. Fetch and pre-filter:
   ```bash
   $F himalayas <scratchpad>/himalayas/jobs.json --days 30
   ```
   It searches the profile.json `job_search.queries.himalayas` terms with `country=<home_country>`, and keeps titles that fit their `job_search` title words. `location` shows `Worldwide` or the country list (which includes their home country). Salary comes as `salary_min`/`salary_max` + `currency` + `period` when posted.
2. Also browse `https://himalayas.app/jobs/countries/<home-country>` (lowercase, hyphens) with the categories that fit their roles, for anything the search missed.
3. For each job, open the Himalayas page and then the **company's own job page** (`apply_url`). Run the common job checks in RULES Step 1:
   - **Remote worldwide:** Himalayas already confirms their home country is allowed. Still confirm on the company's page. If the company's page says otherwise (e.g. "US only"), skip.
   - **Time zones:** skip jobs whose required time zone overlap can't work from their time zone (profile.json `timezone_label`, e.g. "must work 9-5 PST").
   - **Company country:** the Himalayas company page shows HQ. Confirm with `$A country`. Many Himalayas companies are outsourcing agencies; skip them, and skip any company in one of their blocked countries.
   - **Pay:** use the posted range. If none is posted, use 1c market analysis.
4. Rank by pay, then proof fit. Take the top N.

## Changed Step 2: How to apply

Himalayas links out to the company's ATS or careers page, so apply there (RULES Steps 2 and 6a). Himalayas "Easy apply" through a Himalayas account isn't used: go to the company's own form. If the only option is an email, use RULES 6b.

## Changed Steps 3, 8 and 9

- `job-description.md` starts with the Himalayas URL, the company's own job URL, the posted date, the location restrictions and time zones exactly as listed, then the full description from the company's page.
- Folder: **`apply/<me>/himalayas/<YYYY-MM-DD>/<company-name>/`**. Record with `$A add` and set `linkedin_url` to the Himalayas job URL.
- Commit: `git add apply/<me>/himalayas` and use the message `<me>: apply (himalayas): <date time> — <N> applied (<companies>)`.

## Report

Same as RULES, plus how many jobs the fetcher returned, and how many were skipped for agency, country or time zone.
