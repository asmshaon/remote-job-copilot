# n-job-hunting-generics

A shared Claude Code workspace for job hunting and outreach. Each person keeps their own files and results in their own folders. The skills are the same for everyone.

What it does for each person:

| Say in Claude Code | What happens |
|---|---|
| `profile setup` | creates your folder and settings from your resume and accomplishments (do this first) |
| `outreach` | LinkedIn connection notes for founders/CTOs (company), project buyers (client) and hiring teams. You send them yourself |
| `job apply` / `hn job apply` / `apply <link>` ... | finds remote jobs that fit you, tailors your resume, fills forms (you approve every Submit) or saves emails as Gmail drafts |
| `custom resume` + a job post | a one-page resume tailored to that post |
| `product outreach` | finds small funded startups, tests their product like a user, and drafts a short email about a real bug to a founder |
| `upwork profile` | Upwork title, overview, catalog offers and thumbnails, ranked by search impact |

Claude never sends emails, LinkedIn requests or messages, and never types passwords. You send everything yourself.

## Getting started

1. **Tools:** [Claude Code](https://claude.com/claude-code), Python 3.10+ with `pip install reportlab pypdf pillow`, and the Claude in Chrome extension logged in to your own LinkedIn and Gmail (see `notes/1-linkedin/1-linkedin-automation.txt`).
2. **Clone** the repo and open it in Claude Code with Chrome on: `claude --chrome`.
3. **Say `profile setup`.** Have these ready:
   - your resume PDF
   - your career accomplishments (PDF or Markdown): projects, what you built, for whom, real numbers
   - your skill set (or let Claude draft it from your resume)
   - a profile photo, your list of product/startup directories, and your address and phone (these two stay on your machine)
4. Check: `python .claude/skills/job-apply-shared/scripts/me.py check` prints `ready: <your-slug>`.

## Layout

```
.claude/skills/, .claude/agents/     the shared skills and agents (same for everyone)
linkedin/scripts/ledger.py           the shared LinkedIn ledger script
skillsets-and-contributions/
  _template/                         what a new person's folder starts from
  <slug>/                            one folder per person: profile.json, resume, accomplishments...
apply/<slug>/                        that person's job applications
linkedin/<slug>/                     their LinkedIn ledgers, follow-ups and message logs
product-outreach/<slug>/             their product outreach notes and ledger
upwork/<slug>/                       their Upwork profile files
.me                                  (not committed) which person this machine works as
```

## Rules for collaborators

- Work only in your own folders. Don't open, copy or change anyone else's.
- Everything in your folder is visible to all collaborators, except `others/address/` and `others/contacts/` (git-ignored).
- Every person uses their own LinkedIn, Gmail, Upwork and Chrome. The daily and weekly LinkedIn limits are per person (`linkedin_daily`, `linkedin_weekly_cap` in your profile.json).
- Commits start with your slug (`jane-doe: apply (hn): ...`). Pull before you push: `git pull --rebase origin main`.
- Changes to the shared skills affect everyone. Discuss them first.
