---
name: profile-setup
description: Run when someone says "profile setup", "set me up", "add me", "new person", "switch to <name>" or "update my profile", or when any skill finds `.me` missing or `me.py check` printing NOT READY. Sets up one person in this shared job-hunting workspace. Creates their folder skillsets-and-contributions/<slug>/ from _template, writes `.me` on this machine, collects their files (resume, career accomplishments, skill set, photo, product directories, private address and phone), and builds from those files their profile.json (role, stack, home country, time zone, pay range, target and blocked countries, LinkedIn numbers, job-search words), resume-base.json (the fixed parts of their resume for the tailored resume builder), proof-map.md (their real work mapped to searches, outreach services and offers) and profile-answers.md. Asks for anything the files don't say in one message and never guesses. Commits only that person's folder (the address and phone stay git-ignored).
---

# Profile Setup

Trigger: **`profile setup`** (also "set me up", "add me", "new person", "update my profile"). **`switch to <slug>`** only changes `.me` on this machine.

Every other skill reads only `skillsets-and-contributions/<me>/` and writes only to `apply/<me>/`, `linkedin/<me>/`, `product-outreach/<me>/` and `upwork/<me>/`. This skill creates and fills that `<me>` folder. The rest of the workspace stays the same for everyone.

```bash
M="python .claude/skills/job-apply-shared/scripts/me.py"
$M set <slug>     # this machine now works as <slug> (.me, git-ignored)
$M check          # what is still missing
$M paths          # every file the skills will read for this person
```

## Hard rules

- **Their files only.** Every fact in profile.json, resume-base.json, proof-map.md and profile-answers.md comes from the files they give or their answers in chat. Never copy anything from another person's folder or from `_template`'s example values. Never guess a country, pay figure, number or skill.
- **Never touch another person's folder.** Not to read it as an example, and not to "fix" it.
- **Privacy.** Their whole folder is git-ignored and stays on this machine. It is never pushed, so nobody else sees it and nobody else's setup can overwrite it. Tell them to back it up themselves if they want a copy elsewhere (see README, "Back up your own data").
- **Human writing.** Any text that ends up in front of other people later (resume lines, profile summary) follows [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md).

## Step 1: Who is this

1. Read `.me` (`$M` prints it, or says it's missing) and list the folders in `skillsets-and-contributions/` (ignore `_template`).
2. **Switch only** (`switch to <slug>`, and that folder exists): `$M set <slug>`, `$M check`, report, stop.
3. **New person:** ask for their full name. The slug is the name in lowercase with hyphens (`Jane Doe` → `jane-doe`). If that folder already exists and isn't theirs, add something to make it unique and confirm with them.
4. **Update** (their folder exists): skip to the step they want to redo, or Step 3 to refresh everything from new files.

## Step 2: Create the folder

```bash
cp -r skillsets-and-contributions/_template skillsets-and-contributions/<slug>
python .claude/skills/job-apply-shared/scripts/me.py set <slug>
```

Then ask them, in **one** message, to put their files in place (or give the paths and Claude copies them):

| File | Where | Needed for |
|---|---|---|
| Resume PDF | `resume/<First_Last>.pdf` (this file name is what recruiters see) | everything |
| Career accomplishments (PDF, .md or .docx): projects, what they built, for whom, real numbers | `contributions/` | every search and every piece of writing |
| Skill set (a list is enough; Claude can draft it from the resume for them to check) | `skills/my-skill-set.md` | stack filters |
| Profile photo | `profile-picture/profile.jpg` | only forms that ask |
| Product directories list (startup and product directories they want to browse) | `product-directories/` | product outreach |
| Postal address, phone number (private, never committed) | `others/address/address.txt`, `others/contacts/phone.txt` | only forms that ask |

Delete the template's `.gitkeep` files in folders that now have a real file.

## Step 3: Read their files

Read the resume, the accomplishments and the skill set in full. Note: name, contact links, current title, every job (company, location, role line, dates, what was built there), projects, side work, education, skills, and every real number.

## Step 4: profile.json

Start from the template's keys and replace every value. From the files: names, email, links, headline, summary, years of experience and `experience_since`, `target_roles` (from their titles and work), `stack` (`fit`, `skip`, `terms`), `domains` (from their projects), and `job_search` (the stack and title words, the queries per job board, written for their stack, e.g. a Python engineer gets `python`, `django`, `fastapi` and drops them from `title_exclude`).

Ask in **one** message for what the files can't tell, with the template's value as a suggestion where it fits:
- home country, city, UTC offset (a number, e.g. `5.5` or `-5`) and a time zone label
- pay range per month and currency (`pay.min_month`, `pay.max_month`), and anything like "never below X"
- remote rule (worldwide only? regions they can work for?), `company_countries`, `outreach_countries`, `blocked_countries`, `easy_time_zones`
- LinkedIn numbers per day (`linkedin_daily`), weekly cap (keep it at 90 or less: LinkedIn's limit is about 100 a week), product outreach drafts per day
- **resume style** (`resume_style`): `classic` keeps their own resume's content layout and only changes bullets, project text and skills per job. `modern` builds a clean one-page resume per job (tagline, 3 to 4 sentence summary, experience, 6-category skills grid, black/white/gray), and needs `pip install -r requirements.txt` (Playwright). Default page size `resume_page` (`A4`, or `Letter` if most target companies are in the US/Canada)
- any rules for how their resume should read (positioning, tone, what to keep in the background, spelling). These go in `resume/resume-guide.md` (Step 5b)
- optional daily-jobs filters: company size (`company_size.min_employees`/`max_employees`), a quality bar (`quality_bar`), realism (`realism.max_hard_gaps`), and how old a post may be (`freshness_days`)

Set `slug` to the folder name and `resume_file` to the resume's file name.

## Step 5: resume-base.json (classic style only)

Skip this step when `resume_style` is `modern`: that style builds every resume fresh from their accomplishments, so it has no fixed base. (`me.py check` only asks for `resume-base.json` in the classic style.)

Copy the **fixed parts of their resume exactly** into `resume/resume-base.json`, in the template's shape:
- `name` (as printed), `designation`, `contact` (up to 4 rows: label, text, url)
- `experience`: one entry per job, in resume order, with a short `id` (lowercase company), `company`, `location`, `role` (the italic role line, with its stack), `dates`, `projects` (the accomplishment projects this job may draw from), `bullets` (`[min, max]`: min = 1 or 2, max = the base count + 1, lower for old jobs), and `items` (the bullets as printed, with a `label` when a bullet starts with a project name)
- `projects` (featured projects with `id`, `name`, `subtitle`, `text`), `additional`, `education`
- `skills`: their categories and lines as printed. `skill_pool`: for each category, every item from the skill set, resume and accomplishments they can honestly claim

The builder uses one shared layout for everyone (Calibri header, Arial body, A4, one page), so the PDF won't look like their original design. That is expected. Then check it:

```bash
python .claude/skills/custom-resume/scripts/build_resume.py --base <scratchpad>/base.pdf
```

Open the PDF (Read tool): one page, every fixed line the same as their resume, nothing cut off. If it overflows, show them and agree on what to shorten in their base. Never cut a job or a date on your own.

## Step 5b: resume-guide.md (optional, both styles)

If they gave rules for how their resume should read, write them into `resume/resume-guide.md`, starting from the template's sections (Sources, Positioning, Things to keep in the background, Writing, Shape). Use their own words. Leave the file out when they have no rules; the defaults then apply.

For the modern style, build one sample resume from a real job post they like (custom-resume "Modern style") and show it, so they can adjust the guide before the first real run.

## Step 6: proof-map.md

Build it from the accomplishments, in the template's four sections, every row traced to a project in their files:
1. Headline numbers: every real number, exactly as written.
2. Proof → product types to search for (company outreach, job search, product outreach).
3. Service map: service slug, proof, who buys it (client outreach).
4. Upwork portfolio and catalog candidates, and resume job → projects (matching `resume-base.json`), plus projects with no job slot.

## Step 7: profile-answers.md

Fill what the files say (name, preferred name, email, links, current title and company, years, education). Leave everything else `ASK`. Forms ask later, and the answers get saved there with the date. Never copy the address or phone into this file.

## Step 8: Check and show

1. `$M check` must print `ready: <slug>`. Fix anything it lists (or tell them which file is still missing).
2. Show them, briefly: the profile.json settings, their resume style (classic: the jobs and bullet ranges in resume-base.json and the base resume PDF path; modern: the sample resume and their resume-guide.md), the proof-map rows, and every `ASK` left.
3. Remind them that their folder stays on this machine only (git-ignored). To use it on another computer, they copy the folder there.

## Step 9: Nothing to push

Their folder is git-ignored, so there is no commit. Confirm `git status --porcelain` shows nothing from `skillsets-and-contributions/<slug>/`. If it does, `.gitignore` was changed: stop and tell them.

## Report

- Slug and `.me` set on this machine.
- Files in place, and anything still missing.
- `ASK` items left, and the next commands to try (`job apply`, `outreach`, `product outreach`, `custom resume <job link>`).
