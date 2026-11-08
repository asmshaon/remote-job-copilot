# skillsets-and-contributions

One folder per person. Everything the skills know about you comes from your folder, and nothing else.

```
skillsets-and-contributions/
  _template/                   copy this to start (or say "profile setup" in Claude Code)
  <your-slug>/                 e.g. jane-doe (lowercase, hyphens)
    profile.json               who you are and your job-hunt settings: role, stack, home country, time zone,
                               pay range, target countries, LinkedIn daily numbers, job-search words,
                               resume style (classic or modern). See the main README, section 4
    profile-answers.md         saved answers for application forms (filled in as forms ask)
    proof-map.md               your real work mapped to searches, outreach services and offers
    contributions/             your career accomplishments (PDF or .md): projects, systems, real numbers
    skills/my-skill-set.md     what you can honestly claim
    resume/<Your_Name>.pdf     your current resume (file name = profile.json "resume_file")
    resume/resume-base.json    the fixed parts of that resume (only for resume_style "classic")
    resume/resume-guide.md     optional: your own rules for how your resumes read (both styles)
    profile-picture/           your photo (profile.jpg), used only when a form asks
    product-directories/       your list of startup and product directories (for product outreach)
    others/address/address.txt your postal address   } only read when a form asks
    others/contacts/phone.txt  your phone number     }
```

## Who am I on this machine

Each person writes their slug into `.me` at the repo root (git-ignored):

```bash
python .claude/skills/job-apply-shared/scripts/me.py set jane-doe
python .claude/skills/job-apply-shared/scripts/me.py check     # what is still missing
```

Your output then goes into your own folders: `apply/<slug>/`, `linkedin/<slug>/`, `product-outreach/<slug>/`
and `upwork/<slug>/`.

## Your folder is private to your machine

- Your folder (and your `apply/`, `linkedin/`, `product-outreach/`, `upwork/` folders) is **git-ignored**.
  It is never pushed, so change anything in it without affecting anyone else, and pulls never overwrite it.
- Only `_template/` and this README are shared. Improve them for everyone only after agreeing on it.
- Back it up yourself (copy it, or make it its own private git repo). See the main README, "Back up your own data".
