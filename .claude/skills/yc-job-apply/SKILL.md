---
name: yc-job-apply
description: Run when the user says "yc job apply" (or "work at a startup apply"). Also "apply job from yc", and any of these with "without agent" (e.g. "apply job from yc without agent") - this skill always runs in the main session (default mode), never with subagents. Follows the shared job-apply rules (job-apply-shared/RULES.md), the same as every source, but the only source is Y Combinator's Work at a Startup (workatastartup.com) plus the YC jobs board (ycombinator.com/jobs). Applications there go straight to YC founders. Finds YC startup jobs matching their accomplishments, skills and resume (their stack, from profile.json) that are remote and open outside the US, at companies in their target countries (profile.json, never their blocked countries), paying at least their pay floor (profile.json `pay.min_month`). Keeps their one-time Work at a Startup profile in line with their resume, then applies with a tailored resume and a specific message to the founders, or through the company's own form or a Gmail email draft. Nothing is sent without the user's go-ahead. Only applied jobs are saved in apply/<me>/yc/<YYYY-MM-DD>/<company-name>/. A job applied to from any source is blocked for 6 months in all of them.
---

# Y Combinator (Work at a Startup) Job Apply

Trigger: **`yc job apply`** (or `work at a startup apply`). Optional: a number. Default target: **20 per run**, never padded (YC remote-anywhere roles are fewer, so expect less).

Also triggered by **`apply job from yc`**. **Default mode, no agents:** this skill always runs in the main session, step by step, and never calls the Agent tool, whether or not the user adds "without agent" (e.g. `apply job from yc without agent`). See "Run mode" in [RULES.md](../job-apply-shared/RULES.md).

**Why this source is valuable:** funded, vetted startups. Applying sends a message straight to the founders, listings show salary and equity, and the filters include "remote" with "open to candidates outside the US".

## Shared rules

**Read [job-apply-shared/RULES.md](../job-apply-shared/RULES.md) first and follow it**, with the changes on this page. Everything else applies exactly as written there: all rules (nothing submitted without the user's yes, Claude never sends email, passwords, truth only, human writing, no address/phone in committed files), common job checks in RULES Step 1 (including **remote worldwide**, **company country**, **pay ≥ their floor** (profile.json `pay.min_month`), the **6-month block**), Step 0 and Steps 3–9, and `skillsets-and-contributions/<me>/profile-answers.md`. Searches and writing come from the accomplishments file (`skillsets-and-contributions/<me>/contributions/`), skill set (`skillsets-and-contributions/<me>/skills/my-skill-set.md`) and resume (`skillsets-and-contributions/<me>/resume/<resume_file>`).

```bash
A="python .claude/skills/job-apply-shared/scripts/apply.py --source yc"   # ledger: apply/<me>/yc/applied.csv
```

## Step Y: One-time Work at a Startup profile (first run, then check each run)

1. Open `https://www.workatastartup.com` in Chrome. If they aren't logged in, hand over: The user logs in or signs up themselves (Claude never types a password).
2. **First run:** fill the profile from their files: name, location (city and country from address.txt (`skillsets-and-contributions/<me>/others/address/address.txt`)), photo (`skillsets-and-contributions/<me>/profile-picture/`), experience and education, skills from the skill set, links, the base resume PDF, and a short plain "about" built from the accomplishments file (written per [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md); check with `$A text`). Preferences: remote, full-time engineering, **needs to work remotely from outside the US**, salary expectation from their profile.json `pay` range, per year. Show the user the text first and save only after their yes.
3. **Every run:** make sure the profile still matches their files.

## Changed Step 1: Find YC jobs (read-only)

1. On Work at a Startup → Jobs: role **Engineering**, the types that fit their `target_roles`, **Remote**, and the option for candidates **outside the US / anywhere**. Search their stack terms (profile.json `stack.terms`) and the domains of their work (`domains`).
2. Also scan `https://www.ycombinator.com/jobs/role/software-engineer` (public, remote filter) for listings the logged-in search missed.
3. For each listing, open the job and the company page. Keep it only if:
   - remote is open to their location: "Remote (anywhere)", "worldwide", or an explicit list with their home country or time zones they can cover. Skip "Remote (US)", "US citizens/visa only", "must be in SF".
   - HQ in a target country (`$A country`). Most YC companies are US-based, which is fine when the US is a target. Never one of their blocked countries.
   - the salary shown reaches at least their `pay.min_month` at the top of its range (1c). Equity doesn't count toward the minimum.
   - the other common job checks in RULES Step 1 pass, including `$A check "<job url>" "<company>" "<title>"`.
4. Rank by salary, then proof fit. Take the top N.

## Changed Step 2 and 6: How to apply

- **Apply on Work at a Startup** (the usual case): Apply opens a message to the founders.
  1. Build the tailored resume (RULES Step 4) and attach it if the form allows. Otherwise the profile resume is used, so say which one in the review.
  2. Write the message with the same 3-part shape as the email in RULES 6b, but shorter (about 90–150 words, 3 short paragraphs, no subject). Greet the founder by first name (shown on the company page). Paragraph 1: what they're building and one specific compliment, plus a reproduced bug in one sentence if found. Paragraph 2: the user through what they built, no skills list. Paragraph 3: a warm close about their team or mission. Check it with `$A text "<message>"`.
  3. Stop before **Send**.
- **The listing links to the company's own ATS** → RULES Steps 2 and 6a.
- **Only an email is given** → RULES 6b (Gmail draft).
- In the Step 7 review, show each message. Click **Send** only for the ones the user approves.

## Changed Steps 3, 8 and 9

- `job-description.md` starts with the Work at a Startup job URL, company page, YC batch, founders' names, salary and equity as shown, remote terms quoted, and posted date, then the full description.
- Save the message as `message.md` in the job folder.
- Folder: **`apply/<me>/yc/<YYYY-MM-DD>/<company-name>/`**. Record with `$A add` (`method: waas`, `form`, or `email`) and set `linkedin_url` to the job URL.
- Saved locally: `apply/<me>/` is git-ignored, so nothing is committed or pushed.

## Report

Same as RULES, plus: profile changes made this run, and listings skipped as US-only remote.
