---
name: twitter-job-apply
description: Run when the user says "twitter job apply" (or "x job apply"). Also "apply job from twitter", and any of these with "without agent" (e.g. "apply job from twitter without agent") - this skill always runs in the main session (default mode), never with subagents. Follows the shared job-apply rules (job-apply-shared/RULES.md), the same as every source, but the jobs come from X/Twitter posts (founders, CTOs, engineers and in-house recruiters tweeting "we're hiring"). Targets 20 jobs per run that match their accomplishments, skills and resume (their stack and home country, from profile.json), are remote worldwide, at companies based in their target countries (profile.json, never their blocked countries), paying at least their pay floor (profile.json `pay.min_month`). Builds a tailored resume per job with the custom-resume skill, applies through the company's own form or saves a specific 3-paragraph email as a Gmail draft, and drafts an X DM when the tweet only says "DM me". Forms are submitted only after the user's go-ahead, and Claude never sends emails, DMs, replies or tweets. Only applied jobs are saved in apply/<me>/twitter/<YYYY-MM-DD>/<company-name>/ and recorded in apply/<me>/twitter/applied.csv. A job applied to from any source is blocked for 6 months in all of them.
---

# Twitter (X) Job Apply

Trigger: **`twitter job apply`** (or `x job apply`). Optional: a number (`twitter job apply 10`). Default target: **20 applications per run**. It's a target, not a quota: never pad with jobs that fail the filters.

Also triggered by **`apply job from twitter`**. **Default mode, no agents:** this skill always runs in the main session, step by step, and never calls the Agent tool, whether or not the user adds "without agent" (e.g. `apply job from twitter without agent`). See "Run mode" in [RULES.md](../job-apply-shared/RULES.md).

## Shared rules

**Read [job-apply-shared/RULES.md](../job-apply-shared/RULES.md) first and follow it**, with the changes on this page. Everything not changed here applies exactly as written there, for every source:

- All rules: forms submitted only after the user's yes, Claude never sends email, the password rules, truth only, human writing, and never saving their address or phone number in committed files.
- The common job checks (RULES Step 1): stack, experience, proof fit, **remote worldwide**, **company country** (their target countries in profile.json; never their blocked countries), **pay ≥ their floor** (profile.json `pay.min_month`) by market analysis (1c), real company, and the **6-month block**.
- Step 0 (checking earlier email drafts) and Steps 2–9: reading the application page, staging, custom resume, company research and bug hunt, filling forms (address file, profile photo, salary from 1c), 3-paragraph emails as Gmail drafts, the review gate, saving, and commit.
- `skillsets-and-contributions/<me>/profile-answers.md`.

Sources for every search and every piece of writing, as in job-apply: the accomplishments file (`skillsets-and-contributions/<me>/contributions/`), skill set (`skillsets-and-contributions/<me>/skills/my-skill-set.md`) and resume (`skillsets-and-contributions/<me>/resume/<resume_file>`).

**Helper, always with `--source twitter`:**
```bash
A="python .claude/skills/job-apply-shared/scripts/apply.py --source twitter"
$A check "<tweet url>" "<company>" "<title>" "<external apply url>"   # blocked 6 months across ALL sources
$A country "<country>"
$A email <email.md> [--fixed-subject]
$A text "<answer or DM>"
$A drafts
$A add '<json row>'     # writes apply/<me>/twitter/applied.csv; linkedin_url = the tweet URL
$A set "<tweet url>" applied|email-draft|withdrawn
```
(The ledger column is still called `linkedin_url` for all sources. Here it holds the tweet URL.)

## X-specific rules

- **Read-only on X.** Claude never tweets, replies, quote-tweets, likes, reposts, follows or sends DMs. It only reads search results, tweets, threads and profiles in the user's logged-in Chrome.
- **Login.** X search needs a logged-in session. If X shows a login page, CAPTCHA or "unusual activity" check, stop and hand control to the user. Never type their X password.
- **Pace.** Follow [HUMAN-BROWSING.md](../job-apply-shared/HUMAN-BROWSING.md): random waits, real reading time, at most 12 searches and 60 opened tweets/pages per run. If X rate-limits ("Something went wrong, try reloading") or shows any check, stop using X for this run and report it. Don't retry.

## Changed Step 1: Find jobs on X (read-only)

Open `https://x.com/search`, use the **Latest** tab, and build queries from their real work (roles, stack and the domains of their projects). X advanced search operators work in the search box:

```
(hiring OR "we're hiring" OR "we are hiring" OR "join our team") <profile.json job_search.x_stack_query> (remote) (worldwide OR anywhere OR "work from anywhere" OR global) -filter:replies since:<YYYY-MM-DD 14 days ago> lang:en
```

`x_stack_query` is their stack and role in X search syntax, e.g. `(node OR nodejs OR "node.js" OR nestjs OR typescript) (backend OR "full stack")`.

Also vary them:
- by domain, from profile.json `domains` (e.g. `(billing OR payments OR fintech)`, `(saas)`, `(ecommerce)`)
- by role, from `target_roles` (e.g. `"backend engineer"`, `"senior backend"`, `"founding engineer"`)
- `min_faves:3` to cut spam when results are noisy
- `url:ashbyhq.com OR url:greenhouse.io OR url:lever.co OR url:workable.com` to find tweets that link straight to an ATS

Also check:
- the timelines of founders/CTOs they follow or who accepted their LinkedIn requests (`linkedin/<me>/send-connection/*/`, status `accepted`), for "hiring" tweets
- hiring threads ("Who's hiring? Drop your company below") and their replies from companies. Each reply is its own candidate.

**Who may post it:** the company's founder, CEO, CTO, engineer, engineering manager, in-house recruiter, or the company account. **Skip** third-party recruiters and job-aggregator bots that don't name the company or link to its own page, and skip reposts from job-board accounts when the original company posting can't be found.

**From each tweet, collect:** author (name, @handle, bio, profile URL), company, role, tweet URL and date, and every link or email in the tweet, its thread and the author's replies. Open the company's careers page and the linked job page. The full job description comes from there.

**Keep the job only if all of these hold:**
1. **A real way to apply:**
   - a link to the company's careers page or ATS → **form** (RULES Steps 2 and 6a)
   - an email address in the tweet, thread or linked page → **email** (Gmail draft, RULES Step 6b)
   - only "DM me" / "reply below" with no link or email → **DM** (see "DM-only tweets" below). Never reply publicly.
   - a link to a LinkedIn Easy Apply job → skip
2. The common job checks in RULES Step 1 all pass. The **company's own page** decides remote-worldwide, country and pay. If they can't be confirmed from the tweet plus the company's site, skip.
3. **Scam and junk check.** Skip tweets that ask for any payment, only allow contact through Telegram/WhatsApp, come from new or empty accounts, promise pay far above market with no details, are crypto "earn per task" gigs, or have no real company site.
4. **Fresh:** tweeted in the last 30 days, and not marked "filled" / "closed" in the thread.

Rank by pay, then proof fit. Take the top N.

## Changed Step 3: Staging and the job description

Same as RULES Step 3, plus: at the top of `job-description.md` record the **tweet URL, author (name, @handle, profile URL) and tweet date**, then paste the **tweet or thread text**, then the full job description from the company's page.

## Changed Step 6b: Email to the tweet author

Same rules as RULES 6b (unique subject, no generic greeting, exactly 3 paragraphs, no skills list in paragraph 2, never needy, checked with `$A email`, saved as a **Gmail draft**, never sent). Differences:
- **Greeting:** the tweet author's first name when the email goes to them or to an address they shared.
- **Paragraph 1** may mention their tweet in one short line (what they said they're building), then the product appreciation and any reproduced bug.
- If the tweet dictates the subject, use it exactly and check with `--fixed-subject`.

## New: DM-only tweets

When the only way to apply is an X DM:
1. Claude **never sends DMs or replies**. It writes the message for the user to send.
2. Same 3-part shape as the email but short (about 60–110 words, 3 short paragraphs): their product and tweet, the user through what they built (no skills list), a warm close. It may end by offering to send their resume. Check it with `$A text "<message>"`.
3. Save it as `<staging>/dm.md`. In the Step 7 review, give the user the author's profile link and the message in a code block. Note if the author's DMs look closed (no Message button), since the user may need to reply to the tweet themselves instead.
4. Record it (Step 8) **only after the user says they sent it**, with `method: dm` and `status: applied`. Until then it stays in staging and isn't saved under `apply/<me>/`.

## Changed Step 8: Where applied jobs are saved

- Folder: **`apply/<me>/twitter/<YYYY-MM-DD>/<company-name>/`** (local date `python .claude/skills/job-apply-shared/scripts/me.py date`; add the role slug if the folder exists).
- Files: as in RULES Step 8 (`job-description.md`, `<resume_file>`, `content.json`, `report.md`, `company-notes.md`, `application.md`, plus `email.md` or `dm.md`). Never write their address or phone number into these files.
- Record: `$A add '{"company":"...","title":"...","company_country":"...","pay_range":"...","pay_usd_month":"...","linkedin_url":"<tweet url>","apply_url":"...","method":"form|account|email|dm","folder":"apply/<me>/twitter/<date>/<company-name>","status":"applied|email-draft"}'`

## Changed Step 9: Saved locally (nothing to push)

Everything this run made is saved in the person's own folders, which are git-ignored and stay on this machine. There is nothing to commit or push. End the report with where the files are.

## Report

Same as RULES, plus:
- For each application: the tweet author (@handle) and tweet link.
- **DMs waiting for the user to send**, with the profile link for each.
- Tweets skipped as recruiter/aggregator, vague, scam or closed, one line each.
- Whether X rate-limited or asked for a login during the run.
