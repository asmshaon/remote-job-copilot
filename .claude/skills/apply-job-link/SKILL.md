---
name: apply-job-link
description: Run when the user shares one job post link to apply to, e.g. "apply <url>", "apply this job <url>", "apply to this <url>", or just pastes a job link and asks to apply. Reads the post, builds a tailored resume with the custom-resume skill, applies on the company's side (form filled and submitted only after their yes, or a 3-paragraph email saved as a Gmail draft, or an in-site application), and, only if the application is actually made, saves everything in apply/<me>/<YYYY-MM-DD>/<company-name>/ and records it in apply/<me>/applied.csv. Follows the shared job-apply rules. The filters are checked, but because the user chose the job themselves, a failed check is shown to them instead of silently skipping, except that companies in their blocked countries stay blocked.
---

# Apply to a Job Link

Trigger: **`apply <job link>`** (also "apply this job <link>", or a pasted job link with a request to apply). One link per run. For several links, run it once per link, or list them and handle them one after another.

**Follow [job-apply-shared/RULES.md](../job-apply-shared/RULES.md)** for everything below that doesn't say otherwise: rules (Submit only after the user's yes, Claude never sends email, passwords, truth only, human writing, privacy), pay analysis (1c), and Steps 2–9. The resume comes from the [custom-resume skill](../custom-resume/SKILL.md).

| Setting | Value |
|---|---|
| `--source` | `direct` |
| Saved in | **`apply/<me>/<YYYY-MM-DD>/<company-name>/`** (only if the application is made) |
| Ledger | `apply/<me>/applied.csv` |

```bash
A="python .claude/skills/job-apply-shared/scripts/apply.py --source direct"
```

## Step 1: Read the job from the link

1. Open the link: WebFetch for plain pages, Chrome for LinkedIn, Wellfound, Workday and other pages that need a login or JavaScript. If it needs a login the user hasn't done, hand it to them. Never type a password.
2. Get: company, role, full description, location / remote terms, pay if posted, and **how to apply**. If the link is a board or LinkedIn page, follow its Apply button to the company's own page and use that text when it's more complete.
3. If the link is dead, the job is closed, or it isn't a job post, stop and tell the user.

## Step 2: Check the job (show, don't silently skip)

Run the **common job checks** from RULES Step 1 and put the result in one short block for the user:

| Check | Result |
|---|---|
| Stack fit / experience / proof fit | ok, or what's off |
| Remote worldwide (quote the sentence) | ok / region-locked / unclear |
| Company country (`$A country`) | ok / not a target |
| Pay (RULES 1c: posted or estimated, USD/month) | the number and source |
| 6-month block (`$A check "<link>" "<company>" "<title>" "<apply url>"`) | new / applied on <date> |
| Apply method (RULES Step 2) | form / account / email / in-site |

- **All ok:** go straight on.
- **Anything fails:** show the table and ask "Apply anyway?" Continue only on yes. They chose this job, so it's their call.
- **Always stop, even if they say yes:** the company is based in one of their **blocked countries** (profile.json `blocked_countries`, their standing rule), or the site is a complex-account system they told us to skip (Workday, Taleo, iCIMS...), unless they explicitly says to handle it this time.
- **LinkedIn Easy Apply links** are fine here, because they picked the job. Fill the Easy Apply steps in Chrome with the tailored resume and stop before Submit, as for any form.

## Step 3: Stage it

Staging folder: `<scratchpad>/direct/<company-name>/`. Save `job-description.md` per RULES Step 3: the link they shared, the company's apply URL, date, the Step 2 check table, the worldwide quote and a Pay section.

## Step 4: Build the tailored resume

custom-resume in the person's resume style (its "Resume style" section: classic Steps 2–6, or modern) plus their `resume/resume-guide.md`, into the staging folder (write the content, build, check the PDF visually):
```bash
python .claude/skills/custom-resume/scripts/build_resume.py <staging>/content.json <staging>/<resume_file>
```
Write its `report.md` there too. Don't use custom-resume's own commit.

## Step 5: Company notes

RULES Step 5 (company description, domain, culture, job description match, sincere praise, optional reproduced bug, contact name) into `company-notes.md`. The cover letter and email are built from these notes and the accomplishments file (RULES 6c).

This skill always runs in the main session without agents (default mode), with or without "without agent" in the command.

## Step 6: Fill the application

RULES Step 6 by method:
- **Form / account / Easy Apply:** 6a. Upload the tailored PDF, fill from profile-answers, and use photo, address and phone only when asked. Answer free-text questions in plain words (`$A text`). A cover letter, when needed, is written per 6c. Ask all `ASK` items in one message. **Stop before Submit.**
- **Email:** 6b. Write `email.md` (`$A email` must print `ok`) and save it as a **Gmail draft** with the PDF attached. Never Send.
- **In-site** (Wellfound, Work at a Startup): write the short note (`$A text`), attach the PDF, and stop before Send.
- **DM only:** write the DM (`$A text`) for the user to send.

## Step 7: Review and submit

Show the user, per RULES Step 7: the link, method, pay, why it fits, the resume path and tailored lines, every answer entered or the full email/note/DM. Then:
- **Form / in-site:** click Submit/Send only after they say yes, and confirm the success page or email.
- **Email:** it's already in Gmail Drafts for them to send.
- **DM:** they send it and tells you.

If they say no, or the submission fails and can't be fixed, **save nothing**: delete the staging folder and record nothing.

## Step 8: Save (only if the application was made)

1. Move the staging folder to **`apply/<me>/<YYYY-MM-DD>/<company-name>/`**. The date is the user's local date (`python .claude/skills/job-apply-shared/scripts/me.py date`), and the company name is lowercase with hyphens (add `-<role-slug>` if that folder already exists today). It then holds `job-description.md`, `<resume_file>`, `content.json`, `report.md`, `company-notes.md`, `application.md` and `email.md` / `note.md` / `dm.md` when used.
2. `application.md` per RULES Step 8: links, method, time, pay, every answer, how it was confirmed. **No address or phone number.**
3. Record it:
   ```bash
   $A add '{"company":"...","title":"...","company_country":"...","pay_range":"...","pay_usd_month":"...","linkedin_url":"<the link they shared>","apply_url":"<company apply url>","method":"form|account|email|easy-apply|in-site|dm","folder":"apply/<me>/<date>/<company-name>","status":"applied|email-draft"}'
   ```
   Emails stay `email-draft` until a later run of any job-apply skill finds them in Gmail Sent (RULES Step 0). Check `$A drafts` at the start of this skill too.

## Step 9: Commit and push

```bash
git add "apply/<me>/<date>/<company-name>" apply/<me>/applied.csv
git commit -m "<me>: apply (link): $(python .claude/skills/job-apply-shared/scripts/me.py stamp) — <company> <role>"
git push
```
Only those two paths.

## Report

- Applied or not, and how (form submitted / email draft waiting / in-site sent / DM for them to send).
- The check table from Step 2, and whether they chose to override anything.
- Resume keyword coverage and gaps (from `report.md`).
- Folder path and commit hash.
