# Job Hunting Automation

A shared [Claude Code](https://claude.com/claude-code) workspace for remote job hunting and outreach.
Anyone can use it. Each person sets up their own folder once, and from then on every search, resume,
cover letter and LinkedIn note is built from **their** files and **their** settings. The skills are the same for everyone.

**Your data stays on your machine.** Your profile, resume, accomplishments and every result are in
git-ignored folders. They are never pushed, so you can change anything in them without touching anyone
else's setup, and a `git pull` never overwrites them. The repo itself holds only the shared tool.

What it does for you:

- finds remote jobs that fit your real work, checks each one on the company's own page, and builds a tailored one-page resume for it
- writes cover letters, application emails and form answers in plain, human English
- prepares LinkedIn connection notes for founders, CTOs, clients and hiring teams
- finds small startups, tests their product like a user, and drafts a short email about a real bug
- writes your Upwork profile and catalog offers

**You stay in control.** Claude never sends an email, a LinkedIn request or a message, never types a
password, and never clicks Submit on a form without your yes. You send everything yourself.

---

## 1. What you need

| Tool | Why | How |
|---|---|---|
| Claude Code | runs the skills | [claude.com/claude-code](https://claude.com/claude-code), then `claude update` |
| Git | to get the repo and save your results | your system's installer |
| Python 3.10+ | the helper scripts | [python.org](https://www.python.org) (or your system Python) |
| Python packages | resumes, PDF checks, thumbnails | `pip install -r requirements.txt` (see 2.2) |
| pdftotext (Poppler) | resume page checks, reading PDFs | Linux: `sudo apt install poppler-utils` · macOS: `brew install poppler` · Windows: [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases), add its `bin` to PATH |
| Chrome + the Claude in Chrome extension | reading job sites, LinkedIn and Gmail as you | Chrome Web Store → "Claude", sign in with your Claude account |

You also need your own LinkedIn and Gmail accounts, logged in inside that Chrome.

## 2. First-time setup

### 2.1 Get the repo

```bash
git clone <repo url> job-hunting-automation
cd job-hunting-automation
```

### 2.2 Install the Python packages

The easy way, which works everywhere (including Linux systems that block `pip install`):

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt          # Windows: .venv\Scripts\pip install -r requirements.txt
.venv/bin/python -m playwright install chromium    # only for the "modern" resume style
```

`.venv` is git-ignored. The scripts find it on their own, so you never need to activate it.
If your normal Python allows it, `pip install -r requirements.txt` works too.

### 2.3 Start Claude Code with Chrome

```bash
claude --chrome
```

Inside a session, `/chrome` connects or shows the status. Allow the sites Claude asks for (linkedin.com,
mail.google.com, job boards). To test it, say: `Open linkedin.com in Chrome and tell me the name on my profile.`

### 2.4 Create your profile

Say **`profile setup`**. Have these ready:

- your resume (PDF)
- your career accomplishments (PDF, Markdown or Word): every project, what you built, for whom, and real numbers. **The more detail, the better every resume and note will be.** Everything Claude writes about you comes from here, and nothing is ever invented.
- your skill set (a simple list is fine; Claude can draft it from your resume for you to check)
- a profile photo, and a list of startup or product directories you like (for product outreach)
- your postal address and phone number (only used when a form asks; never committed)

Claude reads your files, then asks you **once** for what they can't tell: home country, time zone, pay
range, which countries you'll work for, how many LinkedIn notes a day, and your resume style (2.5).
It creates `skillsets-and-contributions/<your-slug>/` and writes your slug into `.me` on this machine.

Check it worked:

```bash
python .claude/skills/job-apply-shared/scripts/me.py check     # prints: ready: <your-slug>
```

If it prints `NOT READY`, it lists exactly what is missing.

### 2.5 Pick a resume style

Set in your `profile.json` as `"resume_style"`:

| Style | What you get | Good for |
|---|---|---|
| `classic` | your own resume's content, kept fixed (`resume/resume-base.json`). Per job, only the bullets, project text and skills change | people happy with their current resume |
| `modern` | a clean one-page resume built fresh for each job: tagline, short career summary, experience, a 6-category skills grid. Black, white and gray. A4 or US Letter. The page is always filled (no empty band at the bottom) | senior people with lots of work to pick from |

Optional: `resume/resume-guide.md` holds **your own rules** for how your resume reads: positioning,
tone, spelling, what to keep in the background (for example "DevOps only as a supporting skill"). Every
resume follows it. Copy the template's example and edit it.

## 3. Everyday use

Open the repo in Claude Code (`claude --chrome`) and type one of these:

| Say | What happens |
|---|---|
| `daily jobs` | **The easiest start.** 3 to 5 checked, solid remote jobs a day, each with a ready pack: job post, company research, tailored resume, cover letter and form answers. You apply by hand, then say `applied 1, 3` (or `skip 2 <reason>`). `daily jobs status` shows your week |
| `apply <job link>` | one job you found yourself: resume, cover letter, then the form (you approve Submit) or a Gmail draft |
| `custom resume` + a job post or link | just a tailored resume for that post |
| `job apply` | all job sources at once with agents. Variants: `job apply 10`, `job apply only hn, yc`, `job apply exclude linkedin job` |
| `hn job apply`, `himalayas job apply`, `yc job apply`, `wellfound job apply`, `linkedin job apply`, `linkedin post apply`, `twitter job apply`, `other job apply` | one source at a time |
| `outreach` | LinkedIn connection notes for three tracks: company (founders and CTOs), client (people who buy projects) and hiring team. You send each request yourself |
| `product outreach` | finds small funded startups, tries their product, and drafts an email to a founder about a real bug you can reproduce |
| `upwork profile` | Upwork title, overview, catalog offers and thumbnails |

A good daily rhythm: `daily jobs` in the morning, apply within 24 hours, `outreach` once a day.

### What happens to your results

Everything lands in your own folders on your machine (git-ignored, never pushed):

```
apply/<your-slug>/daily/<date>/01-company/   daily jobs packs (job post, company notes, resume PDF, apply kit)
apply/<your-slug>/<source>/<date>/<company>/ applications made by the job-apply skills
linkedin/<your-slug>/                         outreach lists, follow-ups and message logs
product-outreach/<your-slug>/                 product notes and drafts
upwork/<your-slug>/                           Upwork texts and thumbnails
```

A job you applied to from any source is blocked for 6 months everywhere, so you never apply twice.

## 4. Your settings (profile.json)

Everything personal lives in `skillsets-and-contributions/<your-slug>/profile.json`. Change it any time
(by hand, or say `update my profile`). Keys starting with `_` are notes and are ignored.

| Key | What it controls |
|---|---|
| `full_name`, `email`, `linkedin`, `github`, `portfolio` | your name and links on resumes and forms |
| `home_country`, `city`, `utc_offset`, `timezone_label` | which "remote" jobs are open to you, and time-zone checks |
| `target_roles`, `seniority` | the job titles searched, and what level to skip |
| `stack` (`fit`, `skip`, `terms`) | which tech stacks fit you and which roles to skip |
| `domains` | the industries of your past work; they widen searches and raise the rank of matching jobs |
| `pay` (`min_month`, `max_month`, `currency`) | your pay range. Jobs below the minimum are dropped; salary answers stay inside the range |
| `remote`, `company_countries`, `blocked_countries` | where companies may be based, and countries never to target |
| `resume_file`, `resume_style`, `resume_page` | resume file name, style (`classic` or `modern`) and default page size |
| `job_search` | search words per job board, title filters |
| `linkedin_daily`, `linkedin_weekly_cap` | how many LinkedIn notes per track per day, and the weekly cap (keep it at 90 or less) |
| `company_size` (`min_employees`, `max_employees`) | *optional* · only companies of this size |
| `quality_bar` | *optional* · what makes a company good enough for you (funding, product, team) |
| `realism` (`max_hard_gaps`, `note`) | *optional* · drop jobs with more than this many must-haves you have no proof for |
| `freshness_days` | *optional* · how old a post may be in `daily jobs` (default 14) |

Your other files in the same folder:

| File | What it's for |
|---|---|
| `contributions/` | your accomplishments: the only source of facts and numbers |
| `skills/my-skill-set.md` | what you can honestly claim |
| `proof-map.md` | your real work mapped to searches, services and offers (built by profile setup) |
| `profile-answers.md` | saved answers for application forms; `ASK` items are asked once, then saved |
| `resume/` | your resume PDF, `resume-base.json` (classic) and the optional `resume-guide.md` |
| `others/address/`, `others/contacts/` | address and phone, only read when a form asks |

The whole folder is git-ignored: it stays on your machine.

## 5. Several people, one repo

- Each person's folders are **git-ignored**: `skillsets-and-contributions/<slug>/`, `apply/<slug>/`,
  `linkedin/<slug>/`, `product-outreach/<slug>/` and `upwork/<slug>/`, plus `.me` and `.venv/`.
  Customize them however you like. Nobody else sees them, and pulls never touch them.
- Each machine works as one person, set in `.me`. Switch with `switch to <slug>` or
  `python .claude/skills/job-apply-shared/scripts/me.py set <slug>`.
- Everyone uses their own LinkedIn, Gmail, Upwork and Chrome. The LinkedIn limits are per person.
- The only things pushed are **shared** changes: skills, agents, scripts, `_template`, docs. A change
  there affects everyone, so agree on it first, keep personal facts out of it, and say in the commit
  that it affects every user. Pull before you push: `git pull --rebase origin main`.
- Want a different rule just for you? Put it in your own folder (`profile.json`, `resume/resume-guide.md`),
  not in a shared skill. Personal Claude notes can go in `CLAUDE.local.md` (also git-ignored).

### Back up your own data

Your folders live only on your computer. To keep a copy or use another machine, pick one:

- copy the folders (or zip them) to a drive or cloud folder now and then, or
- make your own **private** repo inside your folder, e.g.
  ```bash
  cd skillsets-and-contributions/<slug> && git init && git remote add origin <your private repo>
  ```
  (do the same for `apply/<slug>/` if you want your results backed up). The main repo ignores these.

## 6. Safety rules built into every skill

- Nothing is sent by Claude: emails become Gmail drafts, LinkedIn notes and DMs are text for you to send.
- Forms are filled, then Claude stops before Submit and shows you everything. Only items you approve are submitted.
- No passwords, no new accounts on job boards, no CAPTCHA solving. Login walls and checks go to you.
- Truth only: every fact comes from your files. A skill you don't have never appears on a resume; it's named as a gap instead.
- Sites are browsed like a person, with waits and daily limits. A site that shows a check is left for the day.

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `NOT READY` from `me.py check` | it lists what's missing. Run `profile setup` again, or add the file it names |
| `Python packages missing` | `pip install -r requirements.txt`, or the `.venv` steps in 2.2 |
| `NOT BUILT: ... needs Playwright` / `no Chromium found` | `.venv/bin/python -m playwright install chromium` |
| `NOT BUILT` with a list of bullets | the resume text broke a writing rule (AI-sounding word, a sentence over 30 words, a single word alone on the last line, too much or too little on the page). Claude fixes these itself; if you edit by hand, fix what it lists |
| Browser tools don't respond | `/chrome` in the session to reconnect; make sure you're logged in to the site in that Chrome |
| `daily jobs` finds 0 jobs | your filters may be strict. Loosen `company_size`, `quality_bar`, `freshness_days` or `pay.min_month`, or run again tomorrow (each weekday searches different sources) |
| Push rejected (shared changes) | `git pull --rebase origin main`, then push again |
| My folder disappeared after a pull | only possible once, when this repo stopped tracking personal folders. Restore it from your backup or from git history (`git checkout <old commit> -- skillsets-and-contributions/<slug>`) |

## 8. Layout

```
.claude/skills/        the shared skills (one folder each, SKILL.md inside)
.claude/agents/        the shared agents used by `job apply` and `outreach`
requirements.txt       Python packages
skillsets-and-contributions/
  _template/           what a new person's folder starts from
  <slug>/              your folder (git-ignored)
apply/ linkedin/ product-outreach/ upwork/   one <slug>/ folder per person inside each (git-ignored)
.me                    (git-ignored) which person this machine works as
.venv/                 (git-ignored) Python packages
CLAUDE.local.md        (git-ignored, optional) your own notes for Claude
```
