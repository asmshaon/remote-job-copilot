---
name: job-apply
description: Run when the user says "job apply" (all sources at once), optionally with a number and exclusions, e.g. "job apply", "job apply 10", "job apply exclude linkedin job, twitter", "job apply only hn, yc". Orchestrates the job-apply skills with subagents. It launches one job-source agent per included source (LinkedIn Jobs, LinkedIn posts, X/Twitter, Hacker News, Himalayas, Wellfound, Y Combinator, other boards), in parallel across different sites but never two on the same site at once, all browsing like a person (HUMAN-BROWSING.md), then one resume-builder agent for all shortlisted jobs. The main session then fills forms, creates Gmail drafts, runs one review with the user, submits only what they approve, saves each application under its source's apply/<me>/ folder, and commits once. Excluded sources get no agent. If the user adds "without agent" (e.g. "job apply without agent", "job apply only hn, yc without agent"), no subagents are used and the main session runs each included source's skill itself, one after another. A single source ("apply job from twitter", with or without "without agent") goes to that source's own skill, not this one. All shared rules in job-apply-shared/RULES.md apply.
---

# Job Apply (all sources, with agents)

Trigger: **`job apply`**. Examples:
- `job apply`: every source, each with its default target (20).
- `job apply 10`: every source, up to 10 each.
- `job apply exclude linkedin job, twitter`: every source except LinkedIn Jobs and X/Twitter.
- `job apply only hn, himalayas`: just those sources.
- `job apply 5 exclude others`: combined.

The single-source commands (`linkedin job apply`, `hn job apply`, `apply job from twitter`...) still work on their own and always run without agents. This command runs them together through agents, unless the user says "without agent".

## Without agents (default mode)

If the command contains **"without agent"** (or "without agents", "no agent", "no agents", "without subagent"), e.g. `job apply without agent`, `job apply 5 only hn, himalayas without agent`:

1. **Never call the Agent tool** in this run: no `job-source-*` agents and no `job-resume-builder`.
2. Parse included sources and TARGET exactly as in Phase 0, and say in one line which sources will run (in the main session) and which are excluded.
3. Run RULES Step 0 once for all included sources.
4. For each included source, in the table order: run that source's skill (the "Skill" column) yourself in the main session: its Step 1 search, then RULES Steps 2–6 (staging, custom resume, company notes, cover letter / email, form filling up to Submit). Skip jobs another source already staged in this run (Phase 2 de-dup rules).
5. Then one review with the user for everything (Phase 4), save per source (Phase 5) and commit once.

If only one source is named with "without agent" (`apply job from twitter without agent`), just run that source's skill; this orchestrator isn't needed.

The sections below (Phase 0–5) are the **with agents** mode.

## Sources and their agents

| Say (any of) | `--source` | Agent (`.claude/agents/`) | Skill | Saved in |
|---|---|---|---|---|
| linkedin job, linkedin jobs, linkedin | `linkedin` | `job-source-linkedin` | linkedin-job-apply | `apply/<me>/linkedin-job/` |
| linkedin post, linkedin posts | `post` | `job-source-linkedin-post` | linkedin-post-apply | `apply/<me>/linkedin-post/` |
| twitter, x | `twitter` | `job-source-twitter` | twitter-job-apply | `apply/<me>/twitter/` |
| hn, hacker news | `hn` | `job-source-hn` | hn-job-apply | `apply/<me>/hackernews/` |
| himalayas | `himalayas` | `job-source-himalayas` | himalayas-job-apply | `apply/<me>/himalayas/` |
| wellfound, angellist | `wellfound` | `job-source-wellfound` | wellfound-job-apply | `apply/<me>/wellfound/` |
| yc, y combinator, work at a startup | `yc` | `job-source-yc` | yc-job-apply | `apply/<me>/yc/` |
| other, others, other job | `others` | `job-source-others` | other-job-apply | `apply/<me>/others/` |
| (always runs, can't be excluded) | | `job-resume-builder` | custom-resume | |

"exclude linkedin" means LinkedIn Jobs only. To drop LinkedIn posts too, say "exclude linkedin job, linkedin post". If a name doesn't match the table, ask the user which source they meant before launching anything.

All rules in [job-apply-shared/RULES.md](../job-apply-shared/RULES.md) apply to the whole run: forms and in-site applications submitted only after the user's yes, Claude never sends email/DMs, no passwords, truth only, human writing, remote worldwide, company country, pay, the 6-month block, and privacy.

## Phase 0: Set up (main session)

1. Parse the command into **included sources**, **excluded sources** and **TARGET** per source (default 20). Say in one line which agents will launch and which are excluded.
2. Make the run folder: `RUN_DIR = <scratchpad>/job-apply-run-<YYYYMMDD-HHMM>` (absolute path).
3. **RULES Step 0 for every included source:** `python .claude/skills/job-apply-shared/scripts/apply.py --source <key> drafts`, check Gmail Sent, and update statuses. Do this once here, so agents don't all open Gmail.
4. Browser check: if any included source needs the browser (LinkedIn Jobs, LinkedIn posts, X, Wellfound, YC) and Chrome tools aren't available, tell the user and offer to run the API sources only (HN, Himalayas, others).

## Phase 1: Launch the job-source agents (parallel)

Launch **one agent per included source** (Agent tool, `subagent_type` from the table). Per [HUMAN-BROWSING.md](../job-apply-shared/HUMAN-BROWSING.md), **never two agents on the same site at once**:
- **Wave 1 (one message, in parallel):** at most one agent per site: `job-source-linkedin` (or `job-source-linkedin-post` if LinkedIn Jobs is excluded), `twitter`, `wellfound`, `yc`, and the API sources `hn`, `himalayas`, `others`.
- **Wave 2:** `job-source-linkedin-post`, launched only after the LinkedIn Jobs agent has returned, with whatever LinkedIn budget is left.

Each prompt contains:
- `RUN_DIR=<absolute path>`, `TARGET=<n>`
- `BUDGET=<searches>/<pages>` for its site: the HUMAN-BROWSING budget minus what was already used today on that site (earlier agents' `usage`, and today's `outreach` run for LinkedIn if it happened)
- "Follow your agent instructions. Return the shortlist JSON."

Don't launch agents for excluded sources. If an agent reports a challenge or rate limit on a site, don't launch any more agents for that site this run. While they run, don't do their work in the main session. Wait for their results.

**If an agent returns `blocked`** (login page, CAPTCHA, rate limit), tell the user what's needed. When they say it's fixed, continue that same agent with SendMessage (don't start a new one). If they'd rather skip it, drop that source for this run.

## Phase 2: Merge, de-duplicate, build resumes

1. Read every `RUN_DIR/<source>/shortlist.json`.
2. **Cross-source de-duplication:** the same job often appears on several sources. Treat jobs as the same when company + title match, or the apply URLs match. Keep one: the one with the most direct route (company form or founder email over a board page), then higher pay. Delete the other staging folders. Note which source was kept.
3. Re-run `apply.py --source <key> check "<job_url>" "<company>" "<title>" "<apply_url>"` for every remaining job (the 6-month block across all sources) and drop any that print SKIP.
4. Launch **one `job-resume-builder` agent** with the list of remaining staging folders (`JOBS=[...]`). Wait for it. Jobs in its `failed` list are dropped from this run, with the reason kept for the report.

## Phase 3: Prepare applications (main session, one at a time)

1. **Questions for the user:** collect every `needs_from_user` item from all agents (ASK answers, passwords to type, verification codes) and ask **in one message**. Save ASK answers into `skillsets-and-contributions/<me>/profile-answers.md`.
2. Then, **one job at a time** in Chrome (one browser, so no parallel form filling), by method:
   - **form / account:** RULES Step 6a with `<staging>/<resume_file>`, photo/address/phone only when asked, drafted answers from `form-questions.md`. If the form has a cover letter field and the agent didn't write `cover-letter.md`, write it now per RULES 6c (accomplishments file, job description, company description, domain, culture). Stop before Submit. For account sites, hand the password step to the user.
   - **email:** create the Gmail draft from `<staging>/email.md` with the PDF attached (RULES Step 7). Never Send.
   - **wellfound / waas (YC):** fill the in-site application with `note.md` / `message.md` and the PDF, per that skill. Stop before Send.
   - **dm:** nothing to fill. The user sends it.

## Phase 4: One review with the user (gate)

Show one numbered list, **grouped by source**, per RULES Step 7: company, title, links, method, pay, why it fits, resume path + tailored lines, every answer or the full email/note/DM. Then:
- Submit/Send only the forms and in-site applications the user approves ("submit all", "submit 1-12, 15").
- Email drafts are already in Gmail Drafts for them to send. DMs are for them to send, and are recorded only after they confirm.
- Unapproved items are dropped: close their tabs, delete their staging folders.

## Phase 5: Save and commit (main session)

For every application actually made, per RULES Step 8 **using that job's own source**:
- Move its staging folder to `apply/<me>/<source folder>/<YYYY-MM-DD>/<company-name>/` (local date `python .claude/skills/job-apply-shared/scripts/me.py date`), and add `application.md` (no address or phone).
- `python .claude/skills/job-apply-shared/scripts/apply.py --source <key> add '<json>'`.

Then commit **once** for the whole run:
```bash
git add apply/<me>
git commit -m "<me>: apply (all): $(python .claude/skills/job-apply-shared/scripts/me.py stamp) — <N> applied (<source: count, ...>)"
git push
```
Only `apply/<me>/` changes go in this commit. Leave anything else alone.

## Report

- Agents launched and excluded. Per source: found → shortlisted → after de-dup → applied.
- Applied list grouped by source (company, title, country, pay, method, folder) and the commit hash.
- Email drafts waiting in Gmail, and DMs waiting for the user to send.
- Skipped / dropped jobs with reasons (source checks, de-dup, 6-month block, resume failed, not approved).
- Sources that were blocked (login, rate limit) and what the user needs to do.
- Site usage per site (searches, pages) from the agents' `usage`, and any budget that was reached.
