---
name: linkedin-post-apply
description: Run when the user says "linkedin post apply". Also "apply job from linkedin post", and any of these with "without agent" (e.g. "apply job from linkedin post without agent") - this skill always runs in the main session (default mode), never with subagents. Follows the shared job-apply rules (job-apply-shared/RULES.md), the same as every source, except the jobs come from normal LinkedIn posts (founders, CTOs, engineering managers and in-house recruiters posting "we're hiring") instead of the LinkedIn Jobs section. Targets 20 jobs per run that match their accomplishments and skills (their stack and home country, from profile.json), are remote worldwide, at companies based in their target countries (profile.json, never their blocked countries), paying in their range (profile.json `pay`). Builds a tailored resume per job with the custom-resume skill, applies through the company's own form or saves a specific 3-paragraph email as a Gmail draft, and drafts a LinkedIn message when the post only says "DM me". Forms are submitted only after the user's go-ahead, and Claude never sends emails or messages. Only applied jobs are saved in apply/<me>/linkedin-post/<YYYY-MM-DD>/<company-name>/ and recorded in apply/<me>/linkedin-post/applied.csv. A job applied to from any of the apply skills is blocked for 6 months in all of them.
---

# LinkedIn Post Apply

Trigger: **`linkedin post apply`**. Optional: a number (`linkedin post apply 10`). Default target: **20 applications per run**. It's a target, not a quota: never pad with jobs that fail the filters.

Also triggered by **`apply job from linkedin post`**. **Default mode, no agents:** this skill always runs in the main session, step by step, and never calls the Agent tool, whether or not the user adds "without agent" (e.g. `apply job from linkedin post without agent`). See "Run mode" in [RULES.md](../job-apply-shared/RULES.md).

## Shared rules

**Read [job-apply-shared/RULES.md](../job-apply-shared/RULES.md) first and follow it**, with the changes listed on this page. Everything not changed here applies as written there:

- All rules: forms submitted only after the user's yes, Claude never sends email, the password rules, truth only, human writing.
- The common job checks (RULES Step 1), including remote worldwide, company country, pay market analysis (1c), and the 6-month block.
- Steps 2–9: reading the application page, staging folder, custom resume, company research and bug hunt, filling forms, 3-paragraph emails as Gmail drafts, the review gate, saving, and commit.
- `skillsets-and-contributions/<me>/profile-answers.md`, the address file and profile photo, salary expectations.

**Helper, always with `--source post`:**
```bash
A="python .claude/skills/job-apply-shared/scripts/apply.py --source post"
$A check "<post url>" "<company>" "<title>" "<external apply url>"   # blocked 6 months across ALL apply skills
$A email <email.md> [--fixed-subject]
$A text "<answer>"
$A country "<country>"
$A drafts
$A add '<json row>'        # writes apply/<me>/linkedin-post/applied.csv; linkedin_url = the post URL
$A set "<post url>" applied|email-draft|withdrawn
```

## Changed Step 1: Find jobs in LinkedIn posts (read-only)

**Search LinkedIn content**, not LinkedIn Jobs. Use the search bar, then the **Posts** filter, **Sort by: Latest**, **Date posted: Past week** (Past month if 20 good jobs aren't found).

Queries, built from their real work (the accomplishments file and skill set), each combined with a hiring word and a remote word:
- Hiring words: `hiring`, `we're hiring`, `#hiring`, `join our team`, `looking for`, `open role`.
- Role and stack: profile.json `job_search.post_role_words` (e.g. `backend engineer`, `node.js developer`, `nestjs`).
- Remote words: `remote worldwide`, `work from anywhere`, `fully remote`, `global remote`, `remote anywhere`.
- Domains from their projects: profile.json `domains` and `proof-map.md` section 1.
Examples (for a Node.js backend engineer): `hiring node.js remote worldwide`, `we're hiring backend engineer typescript work from anywhere`, `#hiring nestjs remote`.

Also check the **Hiring** / "#hiring" posts of founders and CTOs the user is already connected with (their feed and the accepted rows in `linkedin/<me>/send-connection/*/`).

**Who may post it:** the company's founder, CEO, CTO, engineering manager or lead, or an **in-house** recruiter/talent partner, or the company page itself. **Skip** third-party agencies and recruiters who don't name the company. The company's country, pay and remote policy can't be checked without its name.

**From each post, collect:** author (name, title, profile URL), company, role, post URL, and any links or email in the post or its first comments. Open the company's careers page and the linked job page, since posts are short. The full job description comes from those pages when they exist.

**Keep the job only if all of these hold:**
1. **A real way to apply that isn't Easy Apply:**
   - a link to the company's careers page or ATS form → **form** (follow RULES Steps 2 and 6a)
   - an email address in the post or on the linked page → **email** (Gmail draft, RULES Step 6b)
   - the post only says "DM me", "send me your CV" or "comment below" with no link or email → **DM** (see "DM-only posts" below)
   - a link to a LinkedIn job with **Easy Apply** → skip
2. The common job checks in RULES Step 1 all pass: stack, experience, proof fit, **remote worldwide**, **company country** (`$A country`), **pay ≥ their floor** (profile.json `pay.min_month`) (1c), real company, and `$A check` prints `new`. When the post itself says little, use the careers page. If the remote policy, country or role still can't be confirmed, skip.
3. **Scam and junk check.** Skip posts that ask for any payment or "training fee", only allow contact through Telegram/WhatsApp, use a free email (gmail.com, outlook.com...) while claiming to be a large company, promise pay far above market for little detail, or come from an account with no history or company page.
4. **Fresh.** Posted in the last 30 days, and not marked "position filled" in the post or its comments.

Rank by pay, then proof fit. Take the top N.

## Changed Step 3: Staging and the job description

Same as RULES Step 3, plus: at the top of `job-description.md` record the **post URL, post author (name, title, profile URL) and post date**, then paste the **post text**, then the full job description from the careers/job page if there is one.

## Changed Step 6b: Email to the post author

Same rules as RULES 6b (unique subject, no generic greeting, exactly 3 paragraphs, no skills list in paragraph 2, never needy, checked with `$A email`, saved as a **Gmail draft**, never sent). Differences:
- **Greeting:** the post author's first name ("Hi Sarah,") when the email goes to them or to a generic jobs address named in their post.
- **Paragraph 1** may mention their post in one short line (e.g. what they said they're building), then the product appreciation and any reproduced bug, as usual.
- If the post dictates the subject, use it exactly and check with `--fixed-subject`.

## New: DM-only posts

When the only way to apply is messaging the author on LinkedIn:
1. Claude **never sends LinkedIn messages or comments**. It writes the message for the user to send.
2. Write it with the same 3-part shape as the email, but short enough for a LinkedIn message (about 80–130 words, 3 short paragraphs): their product and post, the user through what they built (no skills list), a warm close. No subject. Check it with `$A text "<message>"`.
3. Save it as `<staging>/dm.md`. In the Step 7 review, give the user the author's profile link and the message in a code block, and remind them to attach the resume PDF or say it's ready to share.
4. Record it (Step 8) **only after the user says they sent it**, with `method: dm` and `status: applied`. Until then it stays in staging and isn't saved under `apply/<me>/`.
5. If the author isn't a 1st-degree connection and LinkedIn won't allow a message, tell the user. Don't send a connection request (that belongs to the outreach skills).

## Changed Step 8: Where applied jobs are saved

- Folder: **`apply/<me>/linkedin-post/<YYYY-MM-DD>/<company-name>/`** (local date `python .claude/skills/job-apply-shared/scripts/me.py date`; add the role slug if the folder exists).
- Files: as in RULES Step 8 (`job-description.md`, `<resume_file>`, `content.json`, `report.md`, `company-notes.md`, `application.md`, plus `email.md` or `dm.md`). The same privacy rule applies: never write their address or phone number into these files.
- Record: `$A add '{"company":"...","title":"...","company_country":"...","pay_range":"...","pay_usd_month":"...","linkedin_url":"<post url>","apply_url":"...","method":"form|account|email|dm","folder":"apply/<me>/linkedin-post/<date>/<company-name>","status":"applied|email-draft"}'`

## Changed Step 9: Commit and push

```bash
git add apply/<me>/linkedin-post
git commit -m "<me>: apply (posts): $(python .claude/skills/job-apply-shared/scripts/me.py stamp) — <N> applied (<company list>)"
git push
```

## Report

Same as RULES, plus:
- For each application: the post author and post link.
- **DM messages waiting for the user to send**, with the profile link for each.
- Posts skipped as agency, vague or scam, one line each.
