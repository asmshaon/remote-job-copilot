# Job Apply: shared rules for every source

Every job-apply skill follows this file. The skills differ only in **where jobs come from** (their own Step 1, plus any source-specific steps). Everything else here is the same for all of them:

| Skill | Command | `--source` | Applied jobs saved in |
|---|---|---|---|
| linkedin-job-apply | `linkedin job apply` | `linkedin` | `apply/<me>/linkedin-job/` |
| linkedin-post-apply | `linkedin post apply` | `post` | `apply/<me>/linkedin-post/` |
| twitter-job-apply | `twitter job apply` | `twitter` | `apply/<me>/twitter/` |
| hn-job-apply | `hn job apply` | `hn` | `apply/<me>/hackernews/` |
| himalayas-job-apply | `himalayas job apply` | `himalayas` | `apply/<me>/himalayas/` |
| wellfound-job-apply | `wellfound job apply` | `wellfound` | `apply/<me>/wellfound/` |
| yc-job-apply | `yc job apply` | `yc` | `apply/<me>/yc/` |
| other-job-apply | `other job apply` | `others` | `apply/<me>/others/` |
| apply-job-link | `apply <job link>` (one job they share) | `direct` | `apply/<me>/<date>/<company>/` |

In this file, `<source>` is the skill's `--source` value and `<folder>` is its `apply/<me>/...` folder from the table.

**Whose run is this.** Several people share this repo. `<me>` is the person running it: the slug in `.me` at the repo root (`python .claude/skills/job-apply-shared/scripts/me.py`). "The user" in these files means that person. Everything about them comes from `skillsets-and-contributions/<me>/`, and everything this run saves goes under `apply/<me>/`. Never read, write or reuse another person's folders. Run `me.py check` first. If it prints `NOT READY`, stop and offer the `profile-setup` skill.

**All sources at once:** `job apply` (the [job-apply](../job-apply/SKILL.md) skill) runs these same rules with agents. One `job-source-*` agent per included source does Steps 1–3, 5 and the outreach text, the `job-resume-builder` agent does Step 4, and the main session does Steps 0, 6–9 once for the whole run. Sources can be excluded (`job apply exclude linkedin job, twitter`).

### Run mode: with agents or without agents

- **Without agents (default mode).** When the user's command says **"without agent"** (also "without agents", "no agent", "no agents", "without subagent"), the whole run happens in the main session. **Never call the Agent tool**: no `job-source-*` agents and no `job-resume-builder` agent. Claude runs the skill itself, step by step (Steps 0–9 of this file plus the skill's own steps). Examples:
  - `apply job from twitter without agent` / `twitter job apply without agent`: run the [twitter-job-apply](../twitter-job-apply/SKILL.md) skill directly.
  - `apply job from hn, himalayas without agent`: run those skills one after another, then one review and one commit per source.
  - `job apply without agent`: every included source, one after another in the main session (see [job-apply](../job-apply/SKILL.md) "Without agents").
  - `apply <link> without agent`: [apply-job-link](../apply-job-link/SKILL.md) as written.
- **Single-source commands** (`twitter job apply`, `apply job from twitter`, `hn job apply`...) always run in the default mode, with or without the words "without agent". They never launch agents.
- **With agents** is used only by `job apply` when "without agent" is not said.

"apply job from <source>" means the same as "<source> job apply" (source names as in the [job-apply](../job-apply/SKILL.md) table).

Default target: **20 applications per run** (forms + drafts), or the number the user gives. 20 is a target, not a quota: never pad with jobs that fail the filters, and report how many were found.

## Rules that always apply

- **Forms: nothing is submitted without the user's yes.** Claude fills every field, **stops before the final Submit**, shows the user everything, and clicks Submit only for the items they approve in chat ("submit all", "submit 1-8, 11"). An approval covers only the items they name. The same goes for in-site application notes or messages (Wellfound, Work at a Startup): nothing is sent without their yes.
- **Emails: Claude never sends.** It creates a **Gmail draft** (recipient, subject, body, resume attached). The user opens Drafts and clicks Send themselves.
- **DMs, replies, comments, posts: Claude never sends them** on any platform (LinkedIn, X, HN...). When a DM is the only way to apply, Claude writes it and the user sends it.
- **Passwords.** Claude never makes up, types or stores a password. If a site needs a new account, the user types the password themselves. "Continue with Google/LinkedIn" is used only after the user okays it for that site. Login pages, CAPTCHAs, email-verification codes and security checks are handed to the user.
- **Truth only.** Every fact in a resume, form answer, note or email comes from the user's own files or their answers in chat. Salary, visa, notice period and similar questions come only from `skillsets-and-contributions/<me>/profile-answers.md` or from the user in chat, never guessed.
- **Human writing.** Everything another person will read (the tailored resume, cover letters, emails, form answers and any description they submit, in-site notes and messages, DMs, profile text) follows [HUMAN-WRITING.md](HUMAN-WRITING.md): easy words, short sentences (never over 30 words), concrete details, nothing that sounds like an LLM wrote it. It must pass the helper (`$A email` / `$A text`) and the read-aloud, swap and phone tests before the user sees it.
- **Browser.** All site work happens in the user's logged-in Chrome via Claude in Chrome (`claude --chrome` or `/chrome`). If browser tools aren't available, stop and say so.
- **Browse like a person.** Follow [HUMAN-BROWSING.md](HUMAN-BROWSING.md) on every site: random waits and real reading time, a search and page budget per site per run, never two agents on the same site at once, no tricks to hide automation, and **stop using a site at its first challenge or rate limit**. The user's accounts matter more than any one run.
- **Only applied jobs are saved** under `<folder>`: submitted forms, sent in-site applications, emails saved as Gmail drafts, and DMs the user confirms they sent. Jobs found but skipped or not submitted leave no files there. They're only mentioned in the chat report.
- **Privacy.** Never write the user's postal address or phone number into any file under `apply/<me>/` (it's committed to the shared repo, which every collaborator can read). Write "(from address.txt)" / "(from phone.txt)" instead.

## Sources of truth (read at the start of every run)

All from `skillsets-and-contributions/<me>/` (`me.py paths` prints every path):

0. `profile.json`: their role, stack, years, home country, time zone, pay range, target and blocked countries, and job-search words. Every check below that names "their" stack, country, pay or time zone reads it from here.
1. Career accomplishments (`skillsets-and-contributions/<me>/contributions/`): what they have built. Drives every search and every piece of writing. `proof-map.md` maps it to product types and domains.
2. Skill set (`skillsets-and-contributions/<me>/skills/my-skill-set.md`): the stack filter, next to profile.json `stack`.
3. Resume (`skillsets-and-contributions/<me>/resume/<resume_file>`).
4. Profile picture (`skillsets-and-contributions/<me>/profile-picture/`), address (`skillsets-and-contributions/<me>/others/address/address.txt`), phone (`skillsets-and-contributions/<me>/others/contacts/phone.txt`): only when a form asks.
5. `skillsets-and-contributions/<me>/profile-answers.md`: saved answers for application forms.
6. [custom-resume skill](../custom-resume/SKILL.md): how the resume is built (Step 4).

## Helpers (run from the repo root)

```bash
A="python .claude/skills/job-apply-shared/scripts/apply.py --source <source>"
$A check "<job url>" "<company>" "<title>" "<apply url>"   # SKIP if applied in the last 6 months (all sources)
$A country "<country>"                                   # ok if the company's country is a target
$A email <email.md> [--fixed-subject]                    # check an application email
$A text "<answer, note or DM>"                           # check any other free text
$A drafts                                                # this source's email drafts not yet confirmed sent
$A add '<json row>'                                      # record an application in <folder>/applied.csv
$A set "<job url>" applied|email-draft|withdrawn

F="python .claude/skills/job-apply-shared/scripts/fetch_jobs.py"   # job-board APIs: hn, himalayas, remotive, remoteok, jobicy, wwr
```

The ledger column `linkedin_url` holds the job's URL on whatever source it was found (LinkedIn job, post, tweet, HN comment, board page). The name is historical.

## Step 0: Check earlier email drafts

Run `$A drafts`. For each row, search Gmail **Sent** (read-only) for that subject and recipient:
- found in Sent: `$A set "<job url>" applied`
- still only in Drafts: remind the user in the report (company, subject). After 7 days unsent, ask whether to drop it. If they say drop, `$A set "<job url>" withdrawn` and delete that job's folder.

## Step 1: Find jobs

**How to search is the skill's own Step 1.** Build every search from their real work: roles (profile.json `target_roles`), stack (`stack.terms`) and the domains of their projects (`domains`, and section 1 of `proof-map.md`). For example, for a Node.js backend engineer: `Senior Backend Engineer`, `Node.js Developer`, `NestJS`, `TypeScript`, plus billing, monitoring or e-commerce.

**Common job checks.** Every source keeps a job only if all of these hold (plus the skill's own source checks):

1. **Stack fit.** As profile.json `stack.fit` says (e.g. "main backend is Node.js/TypeScript, or the post clearly accepts it"), and skip what `stack.skip` lists (e.g. other-language backends, mobile, frontend-only roles).
2. **Experience fit.** The required years fit their `years_experience` (since `experience_since`). Follow `seniority` (e.g. skip staff/principal/lead-only posts asking for 10+ years).
3. **Proof fit.** At least two of the post's main responsibilities match something real in the accomplishments file. Note which ones.
4. **Remote worldwide.** The company's own job page says the role is open worldwide: "Remote - Worldwide", "Anywhere", "Global", "Work from anywhere", "any country", or a country list that includes their `home_country`. EOR/contractor hiring (Deel, Remote.com, Oyster) is fine. **Skip** regional-only remote that leaves out their home country ("US only", "EMEA", "Americas", "must reside in", "authorized to work in", time zone bands that exclude their `timezone_label`), on-site and hybrid. profile.json `remote` may say more. When the source and the company page disagree, the company page wins. Quote the sentence that proves it in `job-description.md`.
5. **Company based in a target country.** HQ (company page, site footer or imprint) is in one of their `company_countries` (profile.json, see `company_countries_note`), and **never** in one of their `blocked_countries`. Follow anything else the note says (e.g. skip companies whose engineering team is mainly in a blocked country). `$A country "<country>"` must print `ok`.
6. **Pays in their range.** See 1c. Skip anything that lands below their `pay.min_month`.
7. **Real company.** Skip staffing agencies reposting vague roles, scams (fees, Telegram/WhatsApp-only contact, free-email "big companies", empty accounts), and posts older than 30 days or marked filled.
8. **Not applied in the last 6 months.** `$A check "<job url>" "<company>" "<title>" "<apply url>"` must print `new`. A job they applied to from **any** source is blocked for **6 months (180 days)**, matched by source job ID, company + title, or the external apply link, so reposts and cross-posts are caught. Withdrawn drafts don't block.

Three more checks apply **only when their profile.json sets them** (people who leave them out get none of these):

9. **Company size** (`company_size`): headcount between `min_employees` and `max_employees`, from the company's LinkedIn page, team page, YC or Wellfound profile, or the Himalayas employee count (note the source). Over the limit, or unknown after two sources: skip. Don't spend checks on the job feeds of companies known to be bigger.
10. **Quality bar** (`quality_bar`): the company meets every point it lists, each with a source.
11. **Realistic fit** (`realism`): count the post's must-haves with no proof in their files. More than `realism.max_hard_gaps`: skip. Also skip what `realism.note` rules out (e.g. years in a language they barely used, a manager-only or staff/principal role above their record, domain experience they lack). Name the one allowed gap honestly in the report and the application text.

### 1c. Pay: market analysis

The user's range is profile.json `pay`: **`min_month` - `max_month` per month** in `currency` (x12 per year), plus anything in `pay.note`. For each kept job:
1. **Posted pay** (source listing, company page, pay-transparency ranges): convert to their currency per month. Keep it if the top of the range is at least `pay.min_month`.
2. **No posted pay:** estimate from market data for that role, level and company: Glassdoor, levels.fyi, Himalayas salary data, Wellfound, RemoteOK / We Work Remotely salary listings, the company's other posted roles, and its funding stage and size. Keep it only when the estimate for a remote hire clearly reaches `pay.min_month`. If the company publishes a location-based pay formula, use the figure for their `home_country`.
3. Record `pay_range` (as posted or estimated, with the source) and `pay_usd_month` (midpoint per month; the column name is historical, use their currency if it isn't USD), and put a short **Pay** section in `job-description.md`.
4. When a form asks for expected salary, answer with one number inside their range, set from this analysis (near the job's range when posted, higher for well-funded US/EU companies), in the form's currency and period. Never below `pay.min_month` and never above `pay.max_month`.

**Rank** what's left by pay first (higher `pay_usd_month`, counted only up to `pay.max_month`, so a job paying more ranks the same as one paying exactly that), then proof fit, and take the top N for this run. When profile.json sets `realism`, rank by realistic fit first (fewest gaps, most responsibilities matched by real work), then pay, then proof fit.

## Step 2: Read the application page and pick the method

Open the company's application page (following a link is navigation, not applying). Then:

| What the page is | What to do |
|---|---|
| Form with no account needed: Greenhouse, Lever, Ashby, Workable, BambooHR, SmartRecruiters, Recruitee, Teamtailor, Breezy, JazzHR, company forms | apply through the form (6a) |
| Needs a simple account: email + password + maybe an email code, done in a few minutes | Claude fills the non-password fields; the user types the password and any code; then continue |
| Complex: Workday, Taleo, iCIMS, SuccessFactors, Oracle, long multi-page profiles, a required assessment before applying, or CAPTCHA loops | **skip** it and say why in the report |
| The post gives an email address to apply | **email** (6b) |
| Both a form and an email | the form, unless the post prefers email |

If the role is closed, the link goes to a generic careers page with no matching job, or the page asks for things they don't have (security clearance, local ID), skip it. A skill may add its own methods (in-site apply, DM). Those follow the skill's own section.

## Step 3: Save the job post (staging)

Work in a **staging folder in the scratchpad**, not in `apply/<me>/`, until the application is actually made: `<scratchpad>/<source>/<company-name>/`.

Save the full post there as `job-description.md`, with the company, title, source URL, the company's apply URL and the date at the top (the skill may add source details). Use the company's own page text when it's more complete.

## Step 4: Build the tailored resume

Follow the [custom-resume skill](../custom-resume/SKILL.md) Steps 2–6 exactly (analyze the post, pick accomplishments, write bullets, tailor the featured project text and the skills items, build, check the PDF visually). Bullets and the project text follow [HUMAN-WRITING.md](HUMAN-WRITING.md) like every other text they send. The only change is the output folder, which is the staging folder:

```bash
python .claude/skills/custom-resume/scripts/build_resume.py <staging>/content.json <staging>/<resume_file>
```

Also write the custom-resume `report.md` into the staging folder. Skip custom-resume's own Step 7 commit.

## Step 5: Learn about the company and product

Keep notes in `<staging>/company-notes.md`. Every cover letter and application email is built from these notes, so fill all of the first four sections:
- **Company description:** what the product does, who it's for, what's recently shipped (site, about page, changelog, blog, docs, recent posts).
- **Domain:** the industry and problem space the company works in (e.g. fintech payments, observability, HR tech, logistics, e-commerce, EdTech), and which of their accomplishments sit in the same or a close domain.
- **Culture:** how they work and what they value, from their careers/about/values pages, engineering blog, handbook, the job post's "how we work" part, founder posts, and Glassdoor or similar reviews when available (async, remote-first, small team with high ownership, shipping fast, customer focus, open source, writing culture...). Note the source of each point. Write only what the sources say, never assume.
- **Job description match:** the post's 3–5 main responsibilities and requirements, each paired with the matching item in the accomplishments file (with its real numbers), or "no match".
- One or two specific things worth genuine praise: a feature, a design choice, a well-written doc, a public post-mortem.
- **Bug hunt (optional, only if real).** Public pages, docs, pricing, signup and any free tier that needs no payment: broken links or 404s, wrong copy or prices, broken form validation, UI glitches, console errors that break something. Reproduce it twice and note the steps and URL. **Mention a bug only if you reproduced it.** Never invent or exaggerate one, and never sign up for anything that needs payment details.
- The hiring manager's, recruiter's or founder's name if shown, for the greeting.

## Step 6: Fill the application

### 6a. Form

1. Upload `<staging>/<resume_file>` as the resume. If the site parses it into fields, correct any mistakes against the resume.
2. Fill standard fields from `skillsets-and-contributions/<me>/profile-answers.md`.
   - **Address:** when the form asks for a postal address, read address.txt (`skillsets-and-contributions/<me>/others/address/address.txt`) and fill it field by field.
   - **Phone:** read phone.txt (`skillsets-and-contributions/<me>/others/contacts/phone.txt`) when the form asks for a phone number.
   - **Photo:** when the form asks for a photo, headshot or avatar, upload profile.jpg (`skillsets-and-contributions/<me>/profile-picture/`). Don't add it where it isn't asked for.
3. **`ASK` fields or anything not in the file** (visa, notice period, start date, relocation...; salary comes from 1c): collect all of them for this run and ask the user in **one** message. Save the answers into their `profile-answers.md` so they're never asked twice. Never guess.
4. **Free-text questions** ("Why do you want to work here?", "Tell us about a project you're proud of"): answer from the accomplishments file and the company notes, per [HUMAN-WRITING.md](HUMAN-WRITING.md), within any stated length. `$A text "<answer>"` must print `ok`.
5. **Cover letter field: never skip it.** Whenever the form has a cover letter field (required or optional, text box, "Enter manually" or file upload), write a fresh letter per **6c** and paste it (text box / "Enter manually") or upload `cover-letter.pdf` (file field). Standing rule: a cover letter is never left out.
6. Voluntary/diversity questions: "Decline to answer" unless `profile-answers.md` says otherwise.
7. **Stop before Submit.** Note every value entered.

### 6b. Email application

The email is written from the same four inputs as a cover letter (see 6c): the accomplishments file, the job description, the company description and domain, and their culture. Write `<staging>/email.md`:

```
Subject: <subject>
To: <address from the post>

Hi <First name>,        (or "Hi <Company> team," when no name is known)

<paragraph 1>

<paragraph 2>

<paragraph 3>

<closing>,
[Gmail default signature]
```

**Subject.** Unique to this company and something a founder or engineer would want to open (a hook from their product or from the user's matching work). Under 75 characters. No "Application for...", "Job application", "Resume", "CV". **If the post dictates a subject format**, use exactly that and check with `--fixed-subject`.
- Lead with **the company's** product or problem, then what the user brings that they'd care about: a result with a scale number from the "Headline numbers" in `proof-map.md` (e.g. 200+ teams, 50,000+ resumes) or a system they need.
- **No timelines or build speed** ("built in 60 days", "in 3 months", "shipped in 2 weeks"). How fast the user built something long ago doesn't matter to the company. (rule added 2026-10-01)
- No vague "the X I built" endings. Name what it did.
- Bad: `Your training app and the learning platform I built in 60 days`. Better: `Steuart's training app, from an engineer whose courses reached 72,000+`.

**Greeting.** Never "Dear Hiring Manager", "Dear Sir/Madam", "To whom it may concern" or anything like them.

**Closing and signature.** Per [HUMAN-WRITING.md](HUMAN-WRITING.md) section 4: one closing line chosen for the recipient's culture (`Best,`, `Best regards,`, `Kind regards,`, `Regards,`...), then `[Gmail default signature]`. Gmail's default signature carries the user's name and links, so Claude never types them.

**Exactly 3 paragraphs:**
1. **About the company (description + domain).** What the company does, the problem it solves in its domain, and one or two specific, sincere compliments about the product. If Step 5 found a reproduced bug, add it in **one short, friendly sentence** with where it happens.
2. **About the user, matched to the job description, with no skills list.** No languages, frameworks, databases or tools named (the checker rejects them). Take the post's main responsibilities from the "Job description match" in `company-notes.md` and answer them with what the user built and for whom, with real numbers from their accomplishments (e.g. "the monitoring platform 200+ teams rely on", "a recruiting platform searching 50,000+ resumes"). Prefer work from the same or a close domain.
3. **Close about the company (culture).** A sincere appreciation of one or two real points from the Culture notes (how they work, their values, their mission), tied in a few words to how the user works when it's true (e.g. owning a feature end to end, working async across time zones), and the wish to be part of what they're building. Warm and confident.

**Tone.** Written per [HUMAN-WRITING.md](HUMAN-WRITING.md): easy words, short sentences, specific. The user wants to join because the work is interesting, never because they need a job. No "I really need this", "any opportunity", "please consider me", "I'm looking for a job", no begging, no over-thanking, no "I am writing to apply", "Please find attached", "Looking forward to hearing from you". 110–240 words in the body.

`$A email <staging>/email.md` must print `ok`. Then reread it as the recipient would and cut anything that sounds like a template. The resume PDF is attached. Don't paste it into the email.

**Short notes and DMs** (in-site application notes, LinkedIn/X messages): same 3-part shape and rules, shorter (the skill gives the length), no subject, written per [HUMAN-WRITING.md](HUMAN-WRITING.md) and checked with `$A text`.

### 6c. Cover letter (whenever one is needed)

Whenever a cover letter is needed (a form's cover letter field or upload, a "cover letter" / "motivation letter" / "why us" letter the post asks for, or an email application), Claude generates it **fresh for that job**, never from a template or an earlier letter, from these inputs only:

1. **Accomplishments** (`skillsets-and-contributions/<me>/contributions/`): read it for every letter. Every fact and number about the user comes from it.
2. **Job description** (`job-description.md`): the main responsibilities and requirements.
3. **Company description** (`company-notes.md`): what they build and for whom.
4. **Domain** (`company-notes.md`): the industry and problem space, matched with the user's work in the same or a close domain.
5. **Culture** (`company-notes.md`): how they work and what they value.

If the Domain or Culture notes are empty, do Step 5 research first. Don't write the letter without them.

Write `<staging>/cover-letter.md` with the same shape and rules as the 6b email: greeting to a real name (or "Hi <Company> team,"), **exactly 3 paragraphs** (1 = company description and domain, 2 = the user matched to the job description with real numbers and no skills list, 3 = culture and the wish to join), a closing chosen for the culture ([HUMAN-WRITING.md](HUMAN-WRITING.md) section 4) then their `preferred_name` from profile.json (full name, never just the first name; a cover letter has no Gmail signature), no subject line, 150–300 words, never needy, written per [HUMAN-WRITING.md](HUMAN-WRITING.md). If the post names things the letter must cover (a question, a word limit, a format), follow the post. `$A text "<letter>"` must print `ok`, then reread it as the hiring manager would and cut anything generic: every paragraph should be impossible to send to another company unchanged.

- **Text box:** paste the letter body.
- **File upload:** make `<staging>/cover-letter.pdf` (one page, plain layout, the user's name and email at the top, no address or phone) from `cover-letter.md` and upload it.
- **Email application:** the 6b email is the cover letter. Don't attach a separate one unless the post asks for it.

Show the full letter in the Step 7 review, and keep `cover-letter.md` (and the PDF) in the saved folder (Step 8).

## Step 7: Review with the user (gate)

Show one numbered list covering forms and in-site applications (waiting for Submit/Send), email drafts (already in Gmail Drafts) and DMs (for the user to send). For each:
- company, title, source link, company apply link, method
- why it fits (the proof matches from Step 1)
- resume path, plus the tailored bullets, project text and skills lines
- every form answer entered, or the full email / note / DM in a code block
- anything that needs the user: password step, verification codes, `ASK` answers

Then, for each item the user approves:
- **Form / in-site application:** click Submit/Send. Confirm the success page or confirmation email. If an error appears, fix it and show the user what changed before trying again.
- **Email:** doesn't wait for approval, because Claude never sends it. Right after `$A email` prints `ok`, open Gmail in Chrome, Compose, fill **To**, **Subject** and the body exactly as in `email.md` (greeting, paragraphs and the closing line), typed **above** the default signature Gmail inserts. Don't type the `[Gmail default signature]` line, the user's name or links, and don't change the signature. If no signature appears, stop and ask the user to set one. Attach `<resume_file>`, and close the compose window so Gmail saves it to **Drafts**. **Never click Send.** Check it's in Drafts with the attachment.
- **DM:** the user sends it. Record it only after they confirm.

Items the user doesn't approve are dropped: close the tab, delete their staging folder, record nothing.

## Step 8: Save only what was applied

For each application actually made (submitted, sent in-site, email drafted, or DM confirmed):

1. Move the staging folder to **`<folder>/<YYYY-MM-DD>/<company-name>/`**. The date is the user's local date (`python .claude/skills/job-apply-shared/scripts/me.py date`), and the company name is lowercase with hyphens (add `-<role-slug>` if that folder already exists today).
2. Add `application.md`: source URL, company apply URL, method, date and time, pay range and source, every form answer as entered, the cover letter / note / DM if any, and how it was confirmed. No address or phone number (see Privacy). Keep `email.md` / `cover-letter.md` / `cover-letter.pdf` / `note.md` / `message.md` / `dm.md` when used.
3. Record it:
   ```bash
   $A add '{"company":"...","title":"...","company_country":"...","pay_range":"...","pay_usd_month":"...","linkedin_url":"<job url on the source>","apply_url":"...","method":"form|account|email|dm|<in-site>","folder":"<folder>/<date>/<company-name>","status":"applied|email-draft"}'
   ```
   Forms, in-site applications and confirmed DMs use `status: applied`. Emails use `status: email-draft` until Step 0 of a later run finds them in Sent.

## Step 9: Commit and push

```bash
git add <folder>
git commit -m "<me>: apply (<source>): $(python .claude/skills/job-apply-shared/scripts/me.py stamp) — <N> applied (<company list>)"
git push
```

Commit only `<folder>` (plus any file the skill names). Leave other changes alone.

## Report

Short:
- Applied: N of the target (company, title, country, pay, method, folder) and the commit hash.
- **Email drafts waiting in Gmail Drafts**, and **DMs waiting for the user to send**.
- Earlier drafts still not sent (Step 0).
- Found but skipped, one line each with the reason (source-specific reasons, not worldwide remote, company country, pay, complex account, stack, scam, not approved).
- `ASK` answers saved to `profile-answers.md` this run.
- Site usage (searches and pages per site, any challenge or rate limit) per [HUMAN-BROWSING.md](HUMAN-BROWSING.md).
- Bugs found in products, with steps, so the user can mention them in a follow-up.
