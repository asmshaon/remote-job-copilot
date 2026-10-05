---
name: wellfound-job-apply
description: Run when the user says "wellfound job apply" (or "angellist job apply"). Also "apply job from wellfound", and any of these with "without agent" (e.g. "apply job from wellfound without agent") - this skill always runs in the main session (default mode), never with subagents. Follows the shared job-apply rules (job-apply-shared/RULES.md), the same as every source, but the only source is Wellfound (formerly AngelList Talent), a startup job site that shows salary and equity up front and has a "remote, open to anywhere" filter. Finds startup jobs matching their accomplishments, skills and resume (their stack, from profile.json) that are remote worldwide, at companies in their target countries (profile.json, never their blocked countries), paying at least their pay floor (profile.json `pay.min_month`). Keeps their one-time Wellfound profile in line with their resume, then applies with a tailored resume and a specific note to the hiring team, or through the company's own form or a Gmail email draft. Nothing is submitted without the user's go-ahead. Only applied jobs are saved in apply/<me>/wellfound/<YYYY-MM-DD>/<company-name>/. A job applied to from any source is blocked for 6 months in all of them.
---

# Wellfound Job Apply

Trigger: **`wellfound job apply`** (or `angellist job apply`). Optional: a number. Default target: **20 per run**, never padded.

Also triggered by **`apply job from wellfound`**. **Default mode, no agents:** this skill always runs in the main session, step by step, and never calls the Agent tool, whether or not the user adds "without agent" (e.g. `apply job from wellfound without agent`). See "Run mode" in [RULES.md](../job-apply-shared/RULES.md).

**Why this source is valuable:** startups post here directly, salary and equity ranges are shown on every listing, the remote filter separates "remote, anywhere" from "remote in the US", and applications go straight to founders and hiring managers.

## Shared rules

**Read [job-apply-shared/RULES.md](../job-apply-shared/RULES.md) first and follow it**, with the changes on this page. Everything else applies exactly as written there: all rules (nothing submitted without the user's yes, Claude never sends email, passwords, truth only, human writing, no address/phone in committed files), common job checks in RULES Step 1 (including **remote worldwide**, **company country**, **pay ≥ their floor** (profile.json `pay.min_month`), the **6-month block**), Step 0 and Steps 3–9, and `skillsets-and-contributions/<me>/profile-answers.md`. Searches and writing come from the accomplishments file (`skillsets-and-contributions/<me>/contributions/`), skill set (`skillsets-and-contributions/<me>/skills/my-skill-set.md`) and resume (`skillsets-and-contributions/<me>/resume/<resume_file>`).

```bash
A="python .claude/skills/job-apply-shared/scripts/apply.py --source wellfound"   # ledger: apply/<me>/wellfound/applied.csv
```

## Step W: One-time Wellfound profile (first run, then check each run)

Wellfound applications use their Wellfound profile, so it must match their resume.
1. Open `https://wellfound.com/login` in Chrome. If they aren't logged in, hand over: The user logs in or signs up themselves (Claude never types a password).
2. **First run:** fill the profile from their files: name, headline (profile.json `headline`), location from address.txt (`skillsets-and-contributions/<me>/others/address/address.txt`) (city and country only), profile photo (`skillsets-and-contributions/<me>/profile-picture/`), each job (company, title, dates, 1–2 plain lines from the accomplishments file, written per [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md) and checked with `$A text`), education, skills from the skill set, links (LinkedIn, portfolio), and the base resume PDF. Job preferences: remote, full-time, roles Backend / Full-Stack Engineer, desired salary **their profile.json `pay` range, per year**, "open to remote anywhere". Show the user the profile text before saving and save only after their yes.
3. **Every run:** check nothing on the profile contradicts their files. Fix anything that does, with their okay.

## Changed Step 1: Find jobs on Wellfound (read-only)

1. Go to `https://wellfound.com/jobs`. Filters: **Remote only**, remote location **"Anywhere"** / worldwide, roles from profile.json `job_search.wellfound_roles`, skills from `job_search.wellfound_skills`, job type full-time, posted in the last 30 days. Also search keywords from their work: their stack terms and their `domains`.
2. For each listing, read the job page and the company page (HQ location, team size, funding). Keep it only if:
   - the listing's remote policy says anywhere / worldwide, or lists their home country (skip "Remote • US only", "Remote in Europe", "hires in: United States"...)
   - the company page shows HQ in a target country (`$A country`), never one of their blocked countries
   - the **salary shown** converts to at least their `pay.min_month` at the top of the range (1c). Equity doesn't count toward the minimum.
   - the other common job checks in RULES Step 1 pass, including `$A check "<wellfound job url>" "<company>" "<title>"`.
3. Rank by salary, then proof fit. Take the top N.

## Changed Step 2 and 6: How to apply

- **Apply on Wellfound** (the usual case): the Apply button opens a form with a **note to the hiring team** and, sometimes, questions.
  1. Build the tailored resume (RULES Step 4). Upload it for this application if Wellfound allows it; otherwise the profile resume is used, so say which one in the review.
  2. Write the note with the same 3-part shape as the email in RULES 6b, but shorter (about 90–150 words, 3 short paragraphs, no subject, no generic greeting): their product (and a reproduced bug in one sentence if found), the user through what they built with no skills list, a warm close. Check it with `$A text "<note>"`.
  3. Answer any questions from profile-answers or their files (salary from 1c). Stop before **Send application**.
- **The listing sends them to the company's own site** → follow RULES Steps 2 and 6a.
- **Only an email is given** → RULES 6b (Gmail draft).
- In the Step 7 review, show the note and answers for each job. Click **Send application** only for the ones the user approves.

## Changed Steps 3, 8 and 9

- `job-description.md` starts with the Wellfound job URL, company page URL, salary and equity as shown, remote policy text, and posted date, then the full description.
- Save the note as `note.md` in the job folder.
- Folder: **`apply/<me>/wellfound/<YYYY-MM-DD>/<company-name>/`**. Record with `$A add` (`method: wellfound`, `form`, or `email`) and set `linkedin_url` to the Wellfound job URL.
- Commit: `git add apply/<me>/wellfound` and use the message `<me>: apply (wellfound): <date time> — <N> applied (<companies>)`.

## Report

Same as RULES, plus: profile changes made this run, and listings skipped because the remote policy was region-locked.
