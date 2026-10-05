# n-job-hunting-generics

A shared job hunting and outreach workspace. Several people use it, each with their own folder. The skills live in `.claude/skills/`, the agents in `.claude/agents/`.

What it does, per person:
1. LinkedIn outreach to companies (founders, CTOs), clients and hiring managers (`outreach`)
2. Job applications from many sources (`job apply`, `apply <link>`, `custom resume`)
3. Product outreach: real bugs found in startups' products, emailed to their founders (`product outreach`)
4. Upwork profile and catalog (`upwork profile`)

## Who is using it: `.me`

At the start of every task, find out whose task it is:

```bash
python .claude/skills/job-apply-shared/scripts/me.py          # the slug, e.g. jane-doe
python .claude/skills/job-apply-shared/scripts/me.py check    # ready, or what is missing
```

- `<me>` in every skill and agent means that slug. "The user" means that person.
- Their inputs: `skillsets-and-contributions/<me>/` (profile.json, profile-answers.md, proof-map.md, contributions, skills, resume, profile-picture, product-directories, others).
- Their outputs: `apply/<me>/`, `linkedin/<me>/`, `product-outreach/<me>/`, `upwork/<me>/`.
- No `.me` yet, or `check` prints `NOT READY`: run the [profile-setup skill](.claude/skills/profile-setup/SKILL.md) before anything else.
- **Never read, use, change or commit another person's folders.** Their settings, contacts, ledgers and notes are theirs.

## After every task: push to GitHub

When a task that changed files in this repo is finished, the **last step is always the [git-push skill](.claude/skills/git-push/SKILL.md)**. Run it without being asked: commit only that task's files (only `<me>` folders, unless the task was a skill or script edit) and push to `origin/main`. Then include the commit hash in the final message.

Skip it only when nothing changed, the task isn't finished or is waiting on the user, or they said not to push or commit.

## Writing anything another person will read

Follow [HUMAN-WRITING.md](.claude/skills/job-apply-shared/HUMAN-WRITING.md): easy words, short sentences, nothing that sounds LLM-written. Emails end with a closing that fits the recipient's culture, then the Gmail default signature.

## Changing the shared skills

Skills, agents, scripts and `_template` are shared by everyone. Change them only when the user asks, keep every personal fact out of them (personal facts go in `skillsets-and-contributions/<me>/`), and say in the commit that the change affects every user.
