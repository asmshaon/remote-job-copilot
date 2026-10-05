---
name: outreach
description: Run when the user says "outreach" (also "outrich", "linkedin outreach"), optionally with a number and exclusions, e.g. "outreach", "outreach 5", "outreach except client", "outreach exclude hiring team", "outreach only company". Runs their three daily LinkedIn connection tracks with agents. Company = CEO/CTO/technical co-founder (5), client = project buyers (5), hiring team = recruiters and engineering managers at companies they applied to (2), for 12 a day, with a hard cap of 90 requests in any 7 days. The main session does the status check and reject lists once for all tracks, runs one outreach agent per included track, one after another (never two on LinkedIn at once), to find people and write notes, removes cross-track duplicates, hands the user one combined list to send themselves, and commits once. Excluded tracks get no agent. Claude never clicks anything on LinkedIn.
---

# Outreach (all LinkedIn tracks, with agents)

Trigger: **`outreach`** (also `outrich`, `linkedin outreach`). Examples:
- `outreach`: all three tracks at their defaults (company 5, client 5, hiring team 2 = **12**).
- `outreach 5`: all included tracks, 5 each.
- `outreach except client` / `outreach exclude client, hiring team`: skip those tracks.
- `outreach only company, hiring`: just those tracks.
- `outreach 5 except client`: combined.

The single-track commands (`linkedin company outreach`...) still work on their own.

## Tracks and agents

| Say (any of) | Ledger track | Agent (`.claude/agents/`) | Skill | Default |
|---|---|---|---|---|
| company, job, cto, founder | `company` | `outreach-company` | linkedin-company-outreach | 5 |
| client, clients, project, projects | `client` | `outreach-client` | linkedin-client-outreach | 5 |
| hiring, hiring team, recruiter, recruiters | `hiring` | `outreach-hiring-team` | linkedin-hiring-team-outreach | 2 |

If a name doesn't match, ask the user which track they meant before launching anything.

**Per-person numbers.** The defaults above (5 / 5 / 2 = 12 a day) and the weekly cap of 90 are the template's. Each person's own numbers are in their profile.json: `linkedin_daily` (`company`, `client`, `hiring`) and `linkedin_weekly_cap`. Use theirs wherever this skill or the track skills say 5, 2, 12 or 90. All of it counts only the current person's own files under `linkedin/<me>/`, since every person sends from their own LinkedIn account.

**Whose run.** `<me>` is the person in `.me` (`python .claude/skills/job-apply-shared/scripts/me.py`); run `me.py check` first. The ledger (`linkedin/scripts/ledger.py`) reads and writes only `linkedin/<me>/`, `apply/<me>/` and `product-outreach/<me>/`.

The hard rules of the three skills apply to the whole run: Claude never clicks Connect, Send, Withdraw or anything else on LinkedIn (the user sends every request), never types a password, and applies the location rules (the user's outreach countries, never a blocked country), the "already on file" rule across all tracks, the "rejected = never again" rule, and [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md) for every note and suggested message.

## Phase 0: Set up (main session)

1. Parse the command: included tracks, excluded tracks, COUNT per track (the number if given, otherwise each track's default). For each track, subtract the rows already prepared today in that track's send file, since they count toward the day's number. Rows in the **product** track (from `product outreach`) are a bonus and don't reduce any track's COUNT. Say in one line which agents will launch and the day's total.
2. **Weekly cap (hard stop).** Count the requests in the send files of all four tracks (company, client, hiring, product) dated in the last 7 days (today included), leaving out rows marked `not-sent`. The cap is **90 in any 7 days**, which stays under LinkedIn's weekly invitation limit (about 100, shared by all tracks). If this run would push the total over 90, lower COUNT so it fits, taking from the hiring track first, then client, then company, and tell the user. If nothing fits, don't run: say how many were sent in the last 7 days and on which day room opens up again. Only the user can raise the cap for one run, by asking for it explicitly.
3. Chrome tools must be available (`claude --chrome` or `/chrome`). If not, stop and say so.

## Phase 1: Status check and reject lists (main session, once)

The tracks all read the same **Sent invitations** page, so do it once here instead of in each agent. The **product** track (bonus connections from `product outreach`) is always checked here too, even though it has no agent:
1. For each **included** track and the product track, `python linkedin/scripts/ledger.py <track> open`.
2. Open `https://www.linkedin.com/mynetwork/invitation-manager/sent/` once, scroll to the end, and collect the pending names/URLs.
3. Open **My Network → Connections** sorted by **Recently added** once, and scroll back to the oldest open row's date. Then for every open row of every included track and the product track, apply Step 1 of that track's skill (`set pending` / `set accepted` / `set not-sent` / `reject "declined or withdrawn"`), matching names on these two list pages instead of opening profiles.
   Then, if any **company, client, hiring or product** row is `accepted`, `messaged` or `replied`, open **Messaging** once and do the Messages item of Step 1 of each track's skill (product: its Step 0c): confirm messages from earlier follow-up files with `followup sent` / `followup skip`, mark replies, write the gist to the person's log.
4. For each included track and the product track, run Step 2 (`due --days 7` → `reject "no response in 7 days"`), which writes that track's reject file for today.
5. For each included track (company, client, hiring) and the product track, run its Step 2b (product: Step 0c) with `python linkedin/scripts/ledger.py <track> convo`, write the messages due today following that skill's timeline and rules, and add each with `followup add` to `linkedin/<me>/follow-up/<track folder>/<today>.csv`. They go in the Phase 4 hand-over.

## Phase 2: Run the outreach agents (one after another)

All three tracks use LinkedIn, and [HUMAN-BROWSING.md](../job-apply-shared/HUMAN-BROWSING.md) allows only one agent on a site at a time (three at once doesn't look like a person). So launch **one agent per included track, one at a time**, in the table order (Agent tool, `subagent_type` from the table), and wait for each to finish before starting the next. Each prompt: `COUNT=<n>`, `LINKEDIN_LEFT=<searches>/<pages>` (the day's LinkedIn budget minus what Phase 1 and earlier agents used, from their `usage`), then "Follow your agent instructions. Return the JSON."

Don't launch agents for excluded tracks, and don't do their work in the main session. If the LinkedIn budget runs out, don't start the remaining tracks. Report them as "budget reached".

If an agent reports `blocked` (login, CAPTCHA, rate limit), tell the user. When they say it's fixed, continue that same agent with SendMessage. **If any agent reports an invitation-limit, rate-limit, CAPTCHA or "unusual activity" warning, don't start the remaining tracks**, and don't use LinkedIn again today.

## Phase 3: Merge and remove duplicates (main session)

1. `python linkedin/scripts/ledger.py company dupes` lists anyone recorded more than once across tracks.
2. For each duplicate still `prepared` today, keep the track that fits the person best (CTO/founder → company, recruiter/EM → hiring, buyer → client) and remove the other with `python linkedin/scripts/ledger.py <other track> drop <url>`. Never drop a row that isn't `prepared`.
3. Re-count per track and compare with COUNT.

## Phase 4: Hand over (one list)

Give the user one numbered list, **grouped by track** (Company, Client, Hiring team). For each person: name, title, company, profile URL, why them, and the note in its own code block with its character count. Hiring-team entries also show the role they applied for. If `product outreach` prepared rows today that the user hasn't sent yet, list them last under **Product (bonus)**, with a reminder to send the email first.

Then the **messages due** of every included track and the product track, with the path of each track's follow-up file for today: name, profile URL, which message it is, the message in a code block with its character count.

Tell them: open each profile → **Connect** → **Add a note** → paste → **Send**. For messages: profile → **Message** → paste → **Send**. For anyone they skip: `python linkedin/scripts/ledger.py <track> set <url> not-sent`. The next run's Phase 1 confirms who was actually sent.

## Phase 5: Commit and push (once)

```bash
git add linkedin/<me>/send-connection linkedin/<me>/reject-connection linkedin/<me>/messages linkedin/<me>/follow-up
git commit -m "<me>: outreach: $(python .claude/skills/job-apply-shared/scripts/me.py stamp) — <company N, client N, hiring N> prepared, <A> accepted, <R> rejected"
git push
```
Only the `linkedin/<me>/send-connection` and `linkedin/<me>/reject-connection` folders go in this commit.

## Report

- Tracks run and excluded. Prepared per track vs COUNT, and today's total vs 12 (plus any bonus product-track rows), and the 7-day total across all four tracks vs the cap of 90.
- Phase 1: newly pending, newly accepted, not sent, rejected (per track, product track included), and the reject-list names for the user to withdraw by hand.
- Duplicates removed in Phase 3.
- Acceptance rate per track (`stats`).
- Newly accepted people worth a follow-up, per track, with the follow-up idea from that track's skill.
- Any blocked agent or limit warning, and LinkedIn usage (searches, pages) per HUMAN-BROWSING.md.
