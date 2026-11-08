---
name: linkedin-hiring-team-outreach
description: Run when the user says "linkedin hiring team outreach". Third daily LinkedIn track, next to company outreach (CEO/CTO/technical co-founder, 5 a day) and client outreach (5 a day), filling the rest of their 12-a-day target (2 a day by default). Connects with the hiring team at companies they have applied to through the job-apply skills: in-house technical recruiters and talent partners, engineering managers, heads of engineering and engineering leads. Every note is written for that person from their profile and their real work (accomplishments file, resume, skill set) and may mention the role they applied for. Picks the applications where the role matches their work best and the company is most likely to hire (a hire-chance score), and after someone accepts, writes the messages that follow on a set timeline (message 1 the day after acceptance, one follow-up after 7 days, answers within 24 hours, never a push for status). Saves today's list to linkedin/<me>/send-connection/linkedin-connections-by-hiring-team/YYYY-MM-DD.csv. Never sends, withdraws or clicks anything on LinkedIn; the user sends every request themselves. Each run also checks earlier requests and writes the not-accepted-in-7-days / rejected list to linkedin/<me>/reject-connection/linkedin-connections-by-hiring-team/YYYY-MM-DD.csv.
---

# LinkedIn Hiring Team Outreach

Trigger: **`linkedin hiring team outreach`**. Optional: a number. Default: **2 per run**.

**Whose run.** Several people share this repo. `<me>` is the person running it: the slug in `.me` at the repo root (`python .claude/skills/job-apply-shared/scripts/me.py`). "The user" means that person. Read only `skillsets-and-contributions/<me>/` (profile.json, proof-map.md, their files) and write only under `linkedin/<me>/`. Never read, write or reuse another person's folders. Run `me.py check` first; if it prints `NOT READY`, stop and offer the `profile-setup` skill.

## Where this fits in their 12 a day

| Track | Command | Who | Per day |
|---|---|---|---|
| Company (job) | `linkedin company outreach` | CEO, CTO, technical co-founder, founder | 5 |
| Client (projects) | `linkedin client outreach` | people who buy software projects | 5 |
| **Hiring team (applications)** | **`linkedin hiring team outreach`** | **recruiters, talent partners, engineering managers and leads at companies they applied to** | **2** |

**Why this track:** the job-apply skills send applications, but a recruiter reviews hundreds of them. A short, specific connection note to the recruiter or engineering manager a few days after applying puts a face on their application, and the people most likely to move it forward will know their name.

Two things must both be true for every company:
1. **Match:** the role fits their career accomplishments and skill set closely (the job-apply match, plus Step 3b).
2. **May hire:** the role is still open and the company shows it will hire soon (the hire-chance score in Step 3b).

The connection is only the start. The path is: **accepted → message 1 → a few short messages → a call → an interview → an offer** (Step 2b).

## Hard rules (same as the other two tracks)

- **Browse like a person.** Follow [HUMAN-BROWSING.md](../job-apply-shared/HUMAN-BROWSING.md): random waits and real reading time on every profile, the shared LinkedIn budget (30 searches / 120 pages a day across all LinkedIn work), never two agents on LinkedIn at once, no tricks to hide automation, and stop using LinkedIn at the first challenge, rate limit or invitation-limit warning.
- **No automated LinkedIn actions.** Claude never clicks Connect, Send, Withdraw, Follow or Message. It only **reads** LinkedIn pages in the user's logged-in Chrome and writes CSVs. The user sends every request themselves.
- **Their files decide what to say:** the accomplishments file (`skillsets-and-contributions/<me>/contributions/`), resume (`skillsets-and-contributions/<me>/resume/<resume_file>`) and skill set (`skillsets-and-contributions/<me>/skills/my-skill-set.md`). Read them at the start of every run. Never invent experience.
- **Browser.** Claude in Chrome (`claude --chrome` or `/chrome`). Login page, CAPTCHA or security check: stop and hand control back. Never type a password.
- **Location:** the person's LinkedIn location is in one of the user's `outreach_countries` (profile.json, the ledger's allowed list). **Never a blocked country**, and no other countries. Many companies use recruiters based elsewhere, so skip those people and look for another member of the hiring team.
- **Already on file = never again.** `$L check` before researching anyone. It covers all four tracks (company, client, hiring, product), all dates and statuses. A person already contacted in another track is skipped here.
- **Rejected = never again**, as in the other tracks.
- **One track per company per 30 days**, as in the other tracks: `$L company <site> "<company>"` once per company before finding its people (Step 3). `info:` lines saying they applied there are expected in this track.
- **Weekly limit.** All three tracks share LinkedIn's invitation limit (about 100 a week). 12 a day every day is 84 a week, and all tracks together (including the bonus product track from `product outreach`) are capped at **90 requests in any 7 days**. Count the send files of all tracks from the last 7 days (not counting `not-sent` rows) before starting and lower the number to fit. If LinkedIn warns about the limit anyway, stop and say so.

## Files and ledger

```
linkedin/<me>/send-connection/linkedin-connections-by-hiring-team/YYYY-MM-DD.csv
linkedin/<me>/reject-connection/linkedin-connections-by-hiring-team/YYYY-MM-DD.csv
linkedin/<me>/messages/hiring/<first-last>-<company>.md   the conversation after acceptance: each message the user sent
                                                     (exact text, date), the gist of each reply, the next step
```

```bash
L="python linkedin/scripts/ledger.py hiring"
$L check <url> "<name>" "<company>"   # SKIP if already in any file of any track
$L company <site> "<company>"   # SKIP if any track touched this company in 30 days
$L lint "<note>"                       # must print ok
$L add '<json row>'                    # status=prepared; country required
$L open | $L set <url> pending|accepted|not-sent|messaged|replied|call|interview|offer|no-reply | $L due --days 7 | $L reject <url> <reason> | $L stats | $L seen | $L rejected
$L convo                                # messages due after acceptance: message 1, follow-up, answers, check-ins, no-reply
```

`domain_match` holds **`applied: <role title>`** (or `hiring: <role>` for companies they haven't applied to yet), and `why_target` holds the link between their team and their proof, then the hire score and its signals, e.g. `payments team <-> Pulse Stripe lifecycle, dunning | hire 5/7: strong match, Node role, open, applied 4 days ago, seed 2026`.

Run order: **status check (invitations and messages) → reject list → messages due → pick companies → find the hiring team → research + notes → save CSV → hand over → commit + push.**

## Step 1 and Step 2: Status check and reject list

Exactly as in [linkedin-company-outreach](../linkedin-company-outreach/SKILL.md) Steps 1 and 2, with the `hiring` track (`$L`) and replies written to `linkedin/<me>/messages/hiring/`. Earlier requests are marked pending/accepted/not-sent from the Sent invitations page and the recently added Connections page, without opening profiles, sent messages and replies are read from Messaging once, and anyone not accepted in 7 days, or whose invitation disappeared, goes to today's reject file for the user to withdraw by hand.

## Step 2b: Messages after acceptance

Run `$L convo`. For each person, reread their row, the note, the application (`apply/<me>/.../<company>/`: job post, resume, what was sent), their `messages/hiring/` file and (for replies) the thread from Step 1. Then write the next message for the user to send themselves. Claude never sends. Applications move fast, so this track's timing is tighter.

**Timeline (expected; the real conversation always wins):**

| When | Message | After the user sends it |
|---|---|---|
| Day 1 after they accept (not the same hour; not after day 2) | **Message 1**: thanks, one line tying their closest work to the role, and one easy question about the team or the work (never about their application status) | `set messaged` |
| They reply | **Answer within 24 hours**, the same day if possible. If they ask for a CV, a call or times, say yes right away | `set messaged` / `call` |
| 7 days after message 1, no reply | **The one follow-up**: something new and useful (their engineering blog post, a release, a related thing they built). Still no "any update on my application?" | `set messaged` |
| 14 days after the follow-up, still nothing | Nothing more. `set no-reply` | `no-reply` |
| A call or interview is set | Confirm the time in one line, in their time zone and their | `call` / `interview` |
| Right after a call or interview | **Thank-you, same day**: one specific point from the conversation | `interview` / `offer` |
| They say they weren't picked, or the role closed | Thank them, ask to be kept in mind for future backend roles, and stay connected | stays `messaged` |
| Quiet for 30 days after talking | **Check-in**: a short update (something new they shipped) or a new matching role at their company. Never pressure | `set messaged` |

**Predicted messages** (patterns only; write each one fresh). The examples come from one engineer's real files; every real note uses only the current user's own proof.
- **Message 1, recruiter:** `Thanks for connecting, Ana. Quick question about the Senior Backend role: is the team mostly on the recording pipeline, or the billing and accounts side? Both are close to systems I've built.`
- **Message 1, engineering manager:** `Thanks for connecting, Marco. How does the team handle uploads that drop halfway on bad connections? I built chunked video upload with resume for a learning platform, so I'm curious how you approach it.`
- **Follow-up:** `Read your post on moving jobs off cron into a queue. We did the same on Pulse and retries got much easier to reason about.`
- **Not picked:** `Thanks for letting me know, Ana. I'd be glad if you kept me in mind for future backend roles. Good luck with the hire.`

**Message rules:** written per [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md), checked with `python .claude/skills/job-apply-shared/scripts/apply.py text "<message>"`. 2–4 sentences, under about 500 characters, first name, no links, no CV unless they ask. **Never ask for a status update, a referral, or for them to "take a look" at their application.** Never more than two messages in a row without a reply. Never "just following up", "bumping this", or guilt. Save each suggested message in their `messages/hiring/<first-last>-<company>.md` (the history), and add it to today's follow-up file `linkedin/<me>/follow-up/linkedin-connections-by-hiring-team/<today>.csv` with `$L followup add` (same commands and rules as company outreach Step 2b). In Step 1, confirm sent ones with `$L followup open` → `$L followup sent <url>` or `skip <url>`.

## Step 3: Pick the companies

In this order:
1. **Companies they applied to in the last 21 days**, from every applied list: `apply/<me>/*/applied.csv` rows with status `applied` or `email-draft`. Best timing is 2–10 days after applying. Skip applications from today (give the application a day or two to land first) and companies where someone from the hiring team is already in the ledger.
2. If fewer than the target remain: **companies on today's job-apply shortlists** (remote-worldwide, target-country companies hiring for their stack right now) that they haven't applied to yet. Use `domain_match: hiring: <role>`.

Never pick a company in one of their blocked countries or one excluded by the job-apply rules. Those jobs were filtered out anyway.

Run `$L company <site> "<company>"` for each picked company. `SKIP` → pick the next one. Run it once per company before Step 4, so the second person at the same company isn't blocked by the first one added in this run.

### 3b. Match and hire-chance score

Before spending LinkedIn pages on a company, check it off LinkedIn (the job post, careers page, ATS board, the application folder). **Drop** it if the role is closed, or they were already turned down there. Then one point each, with a source:

| Signal | Point if |
|---|---|
| Strong match | the role's main work is a system they have built (the match report in the application folder, or the job post against their accomplishments) |
| Fits their stack | the role asks for the user's main stack (profile.json `stack`) |
| Still open | the role is still listed today |
| Good timing | They applied 2–10 days ago |
| Small, funded team | 5–150 people with funding in the last 24 months, so one engineer matters and hiring is real |
| Hiring push | several engineering roles open, or a "we're hiring" post in the last 60 days |
| Remote-friendly | the team already works across countries or the post says remote worldwide |

Keep companies with **2 or more points** and fill the list from the highest scores down, instead of only by date. Never pad with 0–1 point companies.

## Step 4: Find the hiring team (read-only)

For each company, open its LinkedIn company page → **People**, and search inside it for:
- **In-house recruiters:** `recruiter`, `technical recruiter`, `talent acquisition`, `talent partner`, `people partner` (engineering), `head of talent`.
- **Engineering hiring managers:** `engineering manager`, `head of engineering`, `VP engineering`, `engineering lead`, `tech lead` for the team the role is on (backend, platform, payments...).

Also check the job post itself. Many ATS pages and LinkedIn job posts name the recruiter or "hiring team".

**Keep a person only if:**
- They currently work there (current role on the profile), in-house, not an agency recruiter.
- Recruiters: they recruit engineering / tech roles (headline or recent posts). Managers and leads: their team matches the role's area.
- Their location passes the location rule.
- `$L check` prints `new`.

**Prefer the person closest to the decision:** the engineering manager or lead of the role's team first (they choose who gets hired), then the recruiter who posted the role or is named on it, then another in-house tech recruiter.

Pick **at most 2 people per company** (usually one recruiter and one engineering manager), so one company doesn't take the whole day.

## Step 5: Research and write the note

Research each person as in company-outreach Step 4: profile, About, recent posts, company product. Find **one specific hook**: their hiring post, a team or product detail, something they wrote.

**Note rules** (up to 300 characters, aim for 200–280). Written per [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md): easy words, short sentences, no LLM words, phrases, characters or habits. `$L lint` must print `ok`.

- **Recruiter / talent partner:** first name, their hook or the company, **the exact role they applied for** (or is interested in), and one proof from the PDF that matches that role, with a number. It's fine to say they applied. It isn't fine to ask them to check it, push for an update, or ask for a referral.
  e.g. (one engineer's note) `Hi Ana, I applied for the Senior Backend Engineer role at Zencastr this week. Most of my work is backend for products people rely on daily, like Pulse, where 1,200+ servers report every minute. Glad to be connected.`
- **Engineering manager / head / lead:** talk engineering, like the CTO notes in company outreach. Name the system problem their team's product implies and the matching system they built. They may mention the role in a few words, but the note must stand on its own even without it.
  e.g. (one engineer's note) `Hi Marco, audio sync across flaky connections must keep your team busy. I work on Pulse's ingestion side, 1,200+ servers every minute, and applied for the backend role. Good to connect with the team.`
- **Self-check:** if it could be sent to any recruiter at any company, rewrite it or skip them.

## Step 6: Save today's list

```bash
$L add '{"name":"...","title":"...","company":"...","company_site":"...","country":"<person country>","linkedin_url":"...","domain_match":"applied: <role>","why_target":"<team/product> <-> <their proof>","source":"apply/<me>/<source>/applied.csv","note":"<exact note>"}'
```

## Step 7: Hand over

One numbered list: name, title, company, profile URL, the role they applied for (and when), why them with the hire-chance score, the note in a code block with its character count. The user sends each (Connect → Add a note → paste → Send). Skipped people: `$L set <url> not-sent`.

Then the **messages due** from Step 2b, one block per person: name, profile URL, which message it is, the message in a code block with its character count, and the date it should go out. For messages: profile → **Message** → paste → **Send**.

## Step 8: Saved locally (nothing to push)

Everything this run made is saved in the person's own folders, which are git-ignored and stay on this machine. There is nothing to commit or push. End the report with where the files are.

## Report

- Prepared this run: N of 6 (why fewer, if so), and which companies they cover.
- Status check: newly pending, newly accepted, not sent.
- Reject list path and names, for the user to withdraw.
- From `$L stats`: accepted of sent and still pending, split by recruiters vs engineering managers when there's enough data.
- Each prepared person's hire-chance score; companies dropped (role closed, already turned down, 0–1 points).
- Conversations: messages due today (Step 2b), new replies, calls, interviews and offers.
- Today's combined total across the three tracks, if the other two ran today.
