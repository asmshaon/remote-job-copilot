---
name: git-push
description: Commit and push the finished task's shared changes (skills, agents, scripts, template, docs) to the GitHub repo (origin/main). Personal folders are git-ignored and never pushed. Run it automatically at the end of every task that changed shared files in this repo (a skill run, a skill edit, a fix, notes), and whenever the user says "push", "git push", "commit and push", "push to github" or "save to github". Stages only the shared files the task changed (never personal folders), never secrets, never an address or phone number, writes a commit message in the repo's style, pushes, and reports the commit hash. Never force-pushes, never skips hooks.
---

# Git Push

Trigger: **automatically at the end of every task that changed files in this repo**, as its last step (see [CLAUDE.md](../../../CLAUDE.md)). Also when the user says `push`, `git push`, `commit and push`, `push to github` or `save to github`.

Skills that have their own "Commit and push" step (job-apply, outreach, product-outreach...) run that step **through this skill**: their step decides the paths and the message, and this skill adds the checks below.

## Personal folders are never pushed

Each person's folders are **git-ignored** (see `.gitignore`): `skillsets-and-contributions/<me>/`, `apply/<me>/`, `linkedin/<me>/`, `product-outreach/<me>/`, `upwork/<me>/`, plus `.me` and `.venv/`. They stay on the person's machine, so everyone can customize their own files without overwriting anyone else's.

- When a skill's commit step names only personal paths, there is nothing to push. Say "saved locally in <folder> (personal, not pushed)" and stop.
- **Never** `git add -f` a personal path, and never edit `.gitignore` to let one in.
- Only shared files are committed: `.claude/`, `linkedin/scripts/`, `CLAUDE.md`, `README.md`, `GUIDE.md`, `requirements.txt`, `.gitignore`, `notes/`, `skillsets-and-contributions/_template/` and `skillsets-and-contributions/README.md`. They change only when the task was a skill, script or doc edit the user asked for. Say in the commit body that it changes the workflow for everyone.

## When not to push

- Nothing shared changed (`git status --porcelain` is empty): say "nothing to push" and stop.
- The task isn't finished, failed, or is waiting on the user (a review, an approval, a password): don't push half-done work. Push once it's done.
- The user said "don't push", "commit only" or "don't commit": do only what they asked.

## Step 1: See what changed

```bash
git status --porcelain
git diff --stat
git log --oneline -5
```

Sort the changes into:
- **This task's files:** what this task created, edited, moved or deleted.
- **Other changes:** files changed by something else (the user's own edits, another session, an earlier unfinished task).

**Only this task's files are committed.** Leave other changes alone and mention them in the report. If the user says "push everything", commit them too, after the checks in Step 2.

## Step 2: Safety checks (before staging)

Never stage, and stop to tell the user if a task's file contains:
- passwords, API keys, tokens, cookies, `.env` files, private keys, OAuth or session data
- anyone's postal address or phone number. The two source files (`skillsets-and-contributions/<me>/others/address/address.txt`, `.../contacts/phone.txt`) are git-ignored and must stay that way. A copy anywhere else (e.g. in `apply/<me>/` notes) is never committed
- security issues found in someone's product (product-outreach keeps those out of the repo)
- large build junk: `__pycache__/`, `node_modules/`, temp or scratchpad files, or anything over 20 MB

Quick scan of what's about to be staged:
```bash
git diff -- <paths> | grep -inE "password|api[_-]?key|secret|token|bearer [a-z0-9]|BEGIN .*PRIVATE KEY" || echo "clean"
```
A hit isn't automatically a problem (a skill file may mention the word "password"). Read each one, and stop only for real secrets.

## Step 3: Stage and commit

Stage explicit paths, never `git add -A` or `git add .` (unless the user said "push everything" and Step 2 is clean):
```bash
git add <path> <path> ...
git diff --cached --stat     # confirm only the intended files are staged
```

**Message**, in the repo's style: `<me>: <area>: <what changed>`, so everyone can see whose commit it is. Runs of a skill use its own message format with the user's local time, e.g.:
- `jane-doe: product outreach: 2026-10-01 11:13 +0100 — 2 products, 3 drafts, 3 connection notes (openstatus, Dub)`
- `jane-doe: apply (hn): 2026-10-01 14:02 +0100 — 4 applied (Atria, ...)`
- skill or script edits: `skills: shared human-writing guide and email signature rule` (no `<me>` needed, it's shared)
- fixes or notes: a short plain line saying what changed

Time: `python .claude/skills/job-apply-shared/scripts/me.py stamp`. Plain words, no AI-sounding phrasing. Add a short body (bullets) when the change touches several areas. End with the attribution line the session's instructions give.

```bash
git commit -F - <<'EOF'
<subject line>

<optional body>

Co-Authored-By: ...
EOF
```

If a pre-commit hook fails, fix the cause and make a **new** commit. Never `--no-verify`, never `--amend` a commit that's already pushed.

## Step 4: Push

```bash
git push origin main
```

- **Rejected because the remote is ahead** (common here, others push too): `git pull --rebase origin main`, then push again. If the rebase has conflicts, stop, leave the repo as it is (or run `git rebase --abort`), and tell the user which files conflict. Never resolve a conflict by throwing away anyone's changes.
- **Auth or network error** (SSH key, no connection): the commit stays local. Tell the user it's committed but not pushed, with the error.
- **No remote yet** (`git remote -v` is empty): the commit stays local. Tell the user to add the shared repo with `git remote add origin <url>`.
- **Never** `git push --force`, never push to another branch or remote unless the user asks, never rewrite pushed history.

The repo works directly on `main` (that's how its history looks), so no branch or PR is needed unless the user asks for one.

## Step 5: Report (short)

- Commit hash and message, and that it's pushed to `origin/main` (or why not).
- Files committed (count, or the list if few).
- Other changes left uncommitted, if any.
- Anything stopped by the safety checks.
