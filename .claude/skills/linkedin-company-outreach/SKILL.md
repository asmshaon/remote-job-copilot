---
name: linkedin-company-outreach
description: Run when the user says "linkedin company outreach". Finds the people who could hire the user (their role and stack from profile.json) — CEO, CTO, technical co-founder, founder — at small funded startups whose products match the work in their accomplishments file, resume and skill set, and that show they are likely to hire now (open engineering roles, recent funding, a growing or remote team), ranked by a hire-chance score. Writes a personal note for each, and after someone accepts, writes the messages that follow on a set timeline (message 1 a day or two after acceptance, one follow-up after 7 days, answers to replies, a call once they're engaged), and saves today's list to linkedin/<me>/send-connection/linkedin-connections-by-company-jobs/YYYY-MM-DD.csv. Never sends, withdraws or clicks anything on LinkedIn; the user sends every request themselves. Each run also checks earlier requests and writes the not-accepted-in-7-days / rejected list to linkedin/<me>/reject-connection/linkedin-connections-by-company-jobs/YYYY-MM-DD.csv.
---

# LinkedIn Company Outreach

Trigger: **`linkedin company outreach`**. (For clients and projects, use the `linkedin-client-outreach` skill instead.)

**Whose run.** Several people share this repo. `<me>` is the person running it: the slug in `.me` at the repo root (`python .claude/skills/job-apply-shared/scripts/me.py`). "The user" means that person. Read only `skillsets-and-contributions/<me>/` (profile.json, proof-map.md, their files) and write only under `linkedin/<me>/`. Never read, write or reuse another person's folders. Run `me.py check` first; if it prints `NOT READY`, stop and offer the `profile-setup` skill.

## Goal

Get the user into the network of the people who can **hire them**: CEO, CTO, technical co-founder or founder of a small startup whose product is in an area where they have already shipped real systems.

Two things must both be true for every person:
1. **Match:** their product fits their career accomplishments and their stack (Step 3a, 3d).
2. **May hire:** the company shows it is likely to hire an engineer like them soon (Step 3e). A perfect match at a company that isn't hiring, has no money, or only hires on-site is a weak target. A connection is worth most when the founder will need engineers in the next few months.

The connection is only the start. The path is: **accepted → message 1 → a few short messages → a call → a job** (Step 2b).

## Hard rules

- **Browse like a person.** Follow [HUMAN-BROWSING.md](../job-apply-shared/HUMAN-BROWSING.md): random waits and real reading time on every profile, the shared LinkedIn budget (30 searches / 120 pages a day across all LinkedIn work), never two agents on LinkedIn at once, no tricks to hide automation, and stop using LinkedIn at the first challenge, rate limit or invitation-limit warning.
- **No automated LinkedIn actions.** Claude never clicks Connect, Send, Withdraw, Follow or Message, and never sends anything. Claude only **reads** LinkedIn pages (search results, profiles, the Sent invitations page) in the user's logged-in Chrome, and writes CSV files. The user does every send and withdrawal by hand.
- **Only their own files decide who to target and what to say.** Read all three at the start of every run:
  1. Career accomplishments (`skillsets-and-contributions/<me>/contributions/`): projects, systems and numbers. This is the main source.
  2. Resume (`skillsets-and-contributions/<me>/resume/<resume_file>`): roles, dates, headline numbers.
  3. Skill set (`skillsets-and-contributions/<me>/skills/my-skill-set.md`): the stack used for the stack-fit check.
  Every search query, `why_target` line and note must come from something real in these files. Never invent experience, and never use other skills' lists (`5-target-products/`, `targets.csv`, etc.) as a source.
- **Browser.** LinkedIn pages are read with Claude in Chrome (`claude --chrome` or `/chrome`). If browser tools aren't available, stop and say so. Never ask for or type their password. If LinkedIn shows a login page, CAPTCHA or security check, stop and hand control back.
- **Already on file = never again.** Before researching or listing anyone, check them against **every send and reject file of every track** (all dates, any status: prepared, pending, accepted, not-sent, rejected). If they're already in any of those files, skip them. Run `$L check <url> "<name>" "<company>"` for each candidate; it matches on the profile URL and on name + company, because one person can have more than one LinkedIn URL. `add` runs the same check again and refuses duplicates.
- **One track per company per 30 days.** Before researching anyone, run `$L company <company_site> "<company>"`. It prints `SKIP` if any LinkedIn track or product outreach already reached someone at that company in the last 30 days, so one startup never gets a company note, a product email and a hiring-team request in the same month. `info:` lines (they applied there) are fine; show them in the hand-over.
- **Rejected = never again.** Anyone who has ever landed in a reject file (any track, any date) is never proposed, listed or re-sent again, even if they show up in a new search or a buying-signal post. The ledger's `add` refuses them with `blocked, rejected earlier`. When that happens, drop the person and move on.
- **Location: the user's outreach countries only.** The person's LinkedIn profile location must be in one of the user's `outreach_countries` (profile.json, see `outreach_countries_note`; e.g. the USA, UK, Europe, Canada, Australia, Singapore), and the company must be based there too. **Never include anyone located in one of their `blocked_countries`**, or any company headquartered there, even if everything else fits. Skip every other country as well. Put the person's country in the `country` field; the ledger refuses a row whose country isn't on that list.
- **Per run:** up to **5** people unless the user asks for a different number. Never pad the list with weak matches. Both outreach skills share LinkedIn's weekly invitation limit (about 100 a week). All LinkedIn tracks together (company, client, hiring team, and the bonus product track from `product outreach`) are capped at **90 requests in any 7 days**; count the send files of all four tracks from the last 7 days (not counting `not-sent` rows) before starting, and lower the number to fit.

## Files

```
linkedin/
  scripts/ledger.py                                      shared by every person and every outreach skill
  <me>/                  this person's files only
    send-connection/linkedin-connections-by-company-jobs/
      2026-09-29.csv        today's prepared list (one file per run day)
    reject-connection/linkedin-connections-by-company-jobs/
      2026-10-06.csv        not accepted within 7 days, or invitation gone, found on that day's run
    follow-up/linkedin-connections-by-company-jobs/
      2026-10-02.csv        the messages to send that day (message 1, follow-ups, answers), status prepared/sent/skipped
    messages/company/
      <first-last>-<company>.md   the conversation after acceptance: each message the user sent (exact text, date),
                                  the gist of each reply (not their words in full), and the next step
```

Send-file columns: `date_sent,name,title,company,company_site,country,linkedin_url,domain_match,why_target,source,note,status,status_checked,accepted_date,last_msg_date,msg_count,replied_date`. Reject files have the same columns plus `reject_reason`.

All reads and writes go through the ledger. Never hand-edit the CSVs:

```bash
L="python linkedin/scripts/ledger.py company"
$L seen                  # every URL in any send or reject file, all tracks (skip these)
$L check <url> "<name>" "<company>"   # SKIP if already in any file; run before researching
$L today                 # today's file + count
$L lint "<note>"         # note must print ok (no AI-sounding text)
$L add '<json row>'      # add one prepared row (status=prepared)
$L open                  # prepared + pending rows to check
$L company <site> "<company>"   # SKIP if any track touched this company in 30 days; info if they applied there
$L set <url> pending     # also: accepted | not-sent | messaged | replied | call | interview | offer | no-reply
$L convo                 # messages due after acceptance: message 1, follow-up, answers, check-ins, no-reply
$L followup add|today|open|sent|skip   # today's follow-up file (Step 2b)
$L due --days 7          # pending rows sent 7+ days ago
$L reject <url> <reason> # move row to today's reject file
$L stats                 # accepted of sent, still pending, replied of accepted, calls
$L rejected              # everyone ever rejected (blocked for good)
```

Dates use the user's local time (profile.json `utc_offset`). `date_sent` is the date the row was prepared; the user is expected to send it the same day.

Run order: **status check (invitations and messages) → reject list → messages due → find targets → research + notes → save CSV → hand over → commit + push.**

## Step 1: Check earlier requests and messages (read-only)

Read three list pages, once each, instead of opening profiles one by one (each profile costs a page of the daily LinkedIn budget):
1. Run `$L open` to get every `prepared` and `pending` row.
2. Open `https://www.linkedin.com/mynetwork/invitation-manager/sent/` and scroll to the end. Collect the name and profile URL of every pending invitation.
3. Open **My Network → Connections** (`https://www.linkedin.com/mynetwork/invite-connect/connections/`), sorted by **Recently added**, and scroll back to the date of the oldest open row. Collect the names and URLs.
4. For each row from step 1:
   - **Listed under Sent invitations** → `$L set <url> pending`.
   - **In the recent connections** → `$L set <url> accepted` (stamps the acceptance date).
   - **On neither list, and the row was `prepared`** → the user never sent it: `$L set <url> not-sent`. It stays on file and is never proposed again.
   - **On neither list, and the row was `pending`** → declined or withdrawn: `$L reject <url> "declined or withdrawn"`.
   - Open a profile only when a name can't be matched (two people with the same name, a changed URL). If it's gone → `$L reject <url> "profile unavailable"`.
5. **Messages.** If any row is `accepted`, `messaged` or `replied`, open **Messaging** (`https://www.linkedin.com/messaging/`) once and read only the threads with those people:
   - First run `$L followup open`. Each message there that the user sent → `$L followup sent <url>` (it also sets `messaged`); one they decided not to send → `$L followup skip <url>`.
   - A message they wrote themselves (not from the file) → `$L set <url> messaged` (once per message they sent since the last run).
   - They answered → `$L set <url> replied`. Write the gist in their `linkedin/<me>/messages/company/<first-last>-<company>.md`, never their full words.
   - A call is booked → `call`; an interview → `interview`; an offer → `offer`.

## Step 2: Build the reject list

1. Run `$L due --days 7`. For each row, `$L reject <url> "no response in 7 days"`.
2. This moves every row that wasn't accepted within 7 days into `linkedin/<me>/reject-connection/linkedin-connections-by-company-jobs/<today>.csv`. That file is today's reject list.
3. In the report, list these people (name, company, profile URL) so the user can **withdraw them themselves** on the Sent invitations page. LinkedIn blocks re-inviting a withdrawn person for about 3 weeks, and the ledger keeps them out of future runs for good.

## Step 2b: Messages after acceptance

Run `$L convo`. It lists who needs a message today. For each person, reread their row, the note that was sent, their `messages/company/` file and (for replies) the thread from Step 1, then write the next message for the user to send themselves. Claude never sends.

**Timeline (expected; the real conversation always wins):**

| When | Message | After the user sends it |
|---|---|---|
| Day 1–2 after they accept (not the same hour, it looks automatic; not after day 3, it goes cold) | **Message 1**: thanks, one specific thing about their product or post that the note didn't use, one short concrete point from their work, and one easy question about their work | `set messaged` |
| They reply | **Answer within 24 hours**: answer what they asked, one concrete detail from their work, one question back | `set messaged` |
| 7 days after message 1, no reply | **The one follow-up**: something new (their latest post, launch, funding or release) plus a short, useful thought. No ask, or a very light question | `set messaged` |
| 14 days after the follow-up, still nothing | Nothing more. `set no-reply`. The user may still like or comment on their posts themselves, which keeps their name visible without pressure | `no-reply` |
| After 2–3 exchanges, or as soon as they mention hiring, a backend problem, growth, or ask about their work | **The call offer**, in one easy line: "Happy to do a quick 15-minute call if it's easier to go through it live." | `call` once booked |
| They're engaged and a matching role is open (careers page, the hire signals in `why_target`) | **The role**, plainly and once: they saw the role, their closest work, and whether they'd be open to a short chat about it. Also offer `apply-job-link` for the formal application | `interview` when one is set |
| They say they're not hiring now | Thank them, keep it warm: "Mind if I check back in a few months?" | stays `messaged` |
| A conversation went quiet for 30 days (they had replied before) | **Check-in**: a short update or something useful about their product (a launch, a related fix they built). Never "any updates on hiring?" | `set messaged` |
| Right after a call | **Thank-you, same day**: one specific point from the call and the next step they agreed | `call` / `interview` |

**Predicted messages** (patterns only; write each one fresh from the real profile and thread). The examples come from one engineer's real files; every real note uses only the current user's own proof.
- **Message 1, CTO:** `Thanks for connecting, Rylan. Curious how you handle a broker editing a load after it's synced: last write wins, or do you flag the conflict? On the NetSuite sync I built, conflicts were the hardest part.`
- **Message 1, CEO:** `Thanks for connecting, Daniel. How are customers taking to proof of delivery so far? In the dispatch system I built for a bank, the OTP handover cut most of the "where is my parcel" calls.`
- **Follow-up:** `Saw the new carrier integrations go live, nice. Rate sync is usually where the odd edge cases hide, so that's a big piece to ship.`
- **Answer to a reply:** `Makes sense. We hit the same thing with failed payments: retries alone weren't enough, so I added a state for each step and a daily check that fixed any drift. How do you handle it today?`
- **Call offer:** `Happy to do a quick 15-minute call if it's easier to talk it through.`
- **The role:** `I saw the backend role on your careers page. The billing and alert systems I built for 200+ teams are close to what it describes. Would you be open to a short chat about it?`

**Message rules:**
- Written per [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md), checked with `python .claude/skills/job-apply-shared/scripts/apply.py text "<message>"`, which must print `ok`.
- Short: 2–4 sentences, under about 500 characters. First name, no "Dear". No links, no CV, no portfolio unless they ask.
- **No job ask in message 1 or the follow-up.** The role comes up only once they've engaged (2+ replies) or they bring up hiring themselves.
- Never more than **two messages in a row without a reply** (message 1 + the follow-up). Never "just following up", "bumping this", "did you see my message", or guilt.
- Never InMail, voice notes or attachments.
- Save each suggested message in their `messages/company/<first-last>-<company>.md` (the history), and add it to today's follow-up file (below).

**Today's follow-up file.** Every message due today goes into **`linkedin/<me>/follow-up/linkedin-connections-by-company-jobs/<today>.csv`**, one row per person, so the user opens one file and sends them all:
```bash
$L followup add '{"linkedin_url":"...","message_type":"message-1|follow-up|answer|call-offer|role|check-in|thank-you","message":"<exact message>","log":"linkedin/<me>/messages/company/<first-last>-<company>.md"}'
$L followup today          # the file and its rows
$L followup open           # written earlier, not yet confirmed sent
$L followup sent <url>     # the user sent it: marks it sent and sets the person to messaged
$L followup skip <url>     # the user won't send it
```
`add` checks the writing and refuses a second message to the same person on the same day. `convo` leaves out anyone with a message still waiting (`waiting_to_send`), so nobody gets two messages written for them. A message still unsent after 3 days is rewritten for the current state (or dropped), never sent stale.


## Step 3: Find targets

### 3a. Build the query bank from their files

Read section 1 of `skillsets-and-contributions/<me>/proof-map.md` (their proof → product types to search for). Re-read the accomplishments each run and add rows to that file when you see more, always from their own files. Example rows (one engineer's map):

| Their proof (from the accomplishments / resume) | Product types to search for |
|---|---|
| a monitoring product: 1,200+ servers reporting every minute, dashboards, 200+ teams | server/infra monitoring, observability, uptime, time-series analytics |
| subscription billing: plans, webhook sync, dunning, reconciliation | subscription billing, usage-based pricing, payments SaaS |
| Docker, CI/CD, cloud deploys | dev tools, deployment platforms (secondary, only with a domain match above) |

### 3b. Choose today's domain

Count `domain_match` across the send files and lean toward the one or two domains with the fewest rows, so outreach covers all of their experience over time. **This only breaks ties:** a company with a higher hire-chance score (3e) always comes before one that fills a quiet domain.

### 3c. Search LinkedIn (read-only)

- **People search:** a title keyword + a product keyword from the bank, e.g. `CTO observability`, `co-founder subscription billing`, `founder ATS`, `CTO LMS startup`, `technical co-founder logistics SaaS`, `founder payments startup`.
  Titles: `CEO`, `CTO`, `Co-founder`, `Technical Co-founder`, `Founder`. (Engineering managers, heads of engineering and recruiters belong to `linkedin hiring team outreach`.)
- **Companies search** with the same product keywords, then the company's **People** tab to find the CTO/founder.
- **Hiring first (main route, about half the list):** start from companies that are hiring, then check the match. Sources, cheapest first:
  - off LinkedIn (no LinkedIn budget): YC Work at a Startup and the YC jobs board, Wellfound, the current Hacker News "Who is hiring?" thread, company ATS boards (Greenhouse, Lever, Ashby, Workable), recent funding news (seed to Series B in the last 12 months)
  - LinkedIn **Jobs**: their stack and role words with `remote` (profile.json `job_search.linkedin_queries`, e.g. `Node.js remote`, `backend engineer startup remote`)
  - LinkedIn **posts**: founders and CTOs posting "we're hiring", "growing the team", "just raised" in the last 60 days
  Then find the CTO or founder at the companies whose product matches the bank. Put `source=linkedin-jobs`, `hiring-post`, `funding-news` or the board's name, and the job title or post, in `why_target`.
- Use LinkedIn's **Locations** filter with the user's `outreach_countries` (e.g. United States, United Kingdom, Germany, Netherlands, Canada, Australia). Never add a blocked country.
- Skip anyone in `$L seen`, which already includes everyone in `$L rejected`. Then run `$L company <site> "<company>"` for the company and `$L check` for the person, before opening their profile for research.

### 3d. Keep a person only if all of these hold

- **Role:** CEO, CTO, technical co-founder, founder. Skip VP/Head of Engineering, engineering managers and recruiters (they're covered by `linkedin hiring team outreach`), plus sales, investors and non-lead engineers.
- **Company:** a startup of about **5–150 people** with a live product and **outside funding** (pre-seed to Series B, a YC or other accelerator batch, or known angels) raised in the **last 24 months**, shown by a public source. Under 5 people they rarely hire yet; over 150, hiring runs through recruiters. Skip bootstrapped side projects, agencies, outsourcing shops and large enterprises. When their profile.json sets `company_size`, use its `min_employees` to `max_employees` range instead of 5–150, and when it sets `quality_bar`, the company must meet it too.
- **Domain match:** the product fits at least one row in the query bank.
- **Stack fit** (from the skill set and profile.json `stack`): their stack, or unknown. Skip it if the product is clearly built only in what `stack.skip` names, unless the domain match is very strong; say so in `why_target`.
- **Location:** profile location in one of their `outreach_countries`, and the company based there too. Never a blocked country.
- **Remote reachable:** skip it if the company is clearly on-site only or requires US/EU work authorization.
- **May hire:** at least **2 points** on the hire-chance score (Step 3e).
- **Reachable, not famous:** skip founders who get flooded with requests: 10,000+ followers, a creator or influencer profile, or a well-known name in tech. Mid-known founders at small companies answer far more often.
- **Right person for the size:** under ~30 people, the CEO or CTO both decide on hires. Over ~30, prefer the CTO or technical co-founder (the CEO rarely picks engineers there).

### 3e. Hire-chance score

Check the company off LinkedIn first (careers page, ATS board, YC/Wellfound/Crunchbase, funding news, the company blog), so LinkedIn pages are spent only on people worth it. One point each, with a source:

| Signal | Point if |
|---|---|
| Open engineering role | a backend, full-stack or platform role is open now (any region), on their careers page, ATS board, YC, Wellfound, HN or LinkedIn Jobs |
| Fits their stack | that role, or their job posts or repos, use the user's main stack (profile.json `stack`) |
| Fresh money | a funding round or accelerator batch in the last 12 months |
| Hiring post | the founder or CTO posted "we're hiring", "growing the team" or "just raised" in the last 60 days |
| Remote team | the team already works across countries, says remote-first, or hires through Deel/Remote.com or contractors |
| Growing | headcount or engineering team grew in the last 6 months (company page, team page, new hires announced) |
| Small eng team | 0–5 engineers besides the founders, so one strong backend engineer changes a lot |

**Skip** a company with layoffs or a hiring freeze in the last 6 months, or whose roles all say on-site or "must live in <country>".

Keep people at companies with **2 or more points**, and fill the list from the highest scores down. Never pad with 0–1 point companies.

### 3f. Write the match lines

Write `domain_match` as a short domain (e.g. `billing`, `monitoring`, `recruitment`, `logistics`). Write `why_target` as one line linking their product to their proof, then the hire score and its signals, e.g. `usage-based billing SaaS ↔ Pulse Stripe lifecycle, dunning, usage snapshots | hire 4/7: Node backend role open, seed Mar 2026, remote team, 3 engineers`. Use `source=linkedin-search`, `linkedin-jobs`, `hiring-post`, `funding-news` or the board's name, and include the query you used.

## Step 4: Research each person and write their note

A note that could be sent to anyone is not saved.

**Research:**
1. Open the profile. Confirm name, current title and company.
2. Read the headline, About, current and past roles, and their recent posts or comments (Activity tab).
3. Open the company site. Note what the product does and one technical or business challenge it must have. Confirm the hiring signals from 3e are still current (the role is still open, the post is recent).
4. Find **one specific hook**, in this order: something they posted recently (a hiring or launch post works well) → a concrete feature, launch or funding → an overlap with their past work. If the hook is a hiring post or open role, talk about the work the role is for, never about applying.
5. Pick **one matching proof** from the accomplishments file (a system, feature or number) that relates to that hook.
6. Check the profile has a **Connect** option (directly or under **More**). Drop anyone where LinkedIn would require their email address.

**No specific hook → skip the person.** Don't fall back to a template.

**Angle by role:**
- **CTO / technical co-founder:** talk engineering. Name the system problem their product implies (webhook-driven billing sync, high-volume ingestion, multi-channel delivery, bulk imports, multi-tenant provisioning) and the system they built for the same kind of problem.
- **CEO / non-technical founder:** talk product and outcome. Name what their customers rely on and the result they delivered, with a number from the "Headline numbers" in `proof-map.md`.

**Note rules:**
- Up to 300 characters (Premium limit). Aim for 200–280.
- Start with their first name. Their hook goes in the first sentence.
- One proof from their work, stated plainly, with a number when there is one.
- No job ask, no "I'm looking for opportunities", no links, no flattery ("impressive journey"), no clichés ("I came across your profile", "expand my network", "hope you're doing well").
- Warm and plain. End with a light reason to connect, not a question they must answer.
- No two notes in a run share the same sentence structure.
- **Self-check:** if you swapped in another person's name and company, would the note still make sense? If yes, rewrite it or skip them.

**Write like the user typed it themselves:** follow [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md) for every note (easy words, short sentences, no LLM words, phrases, characters or habits). For notes in particular:
- Short sentences a busy founder or engineer would type on a phone. Say what they built and what it did, then stop. No build-up, no summing up at the end.
- No links, no emojis.
- Vary the openings. Don't start every note with "Hi <name>, saw/noticed...". Sometimes lead with their post, sometimes with the product, sometimes with a plain observation.
- Before saving, run `$L lint "<note>"`. It must print `ok`. If it prints `REWRITE`, rewrite the note in plainer words (don't just swap in a synonym). `add` runs the same check and refuses notes that fail.
- Read it aloud in your head. If it sounds like a LinkedIn post or a marketing email, rewrite it.

**Examples** (show the pattern; never copy). The examples come from one engineer's real files; every real note uses only the current user's own proof.
- CTO, usage-based billing: `Hi Maya, your post on moving plan limits into Stripe metering hit home. At Pulse I built our Stripe lifecycle with dunning states, usage snapshots and reconciliation logs so billing and entitlements never drifted. Would be good to follow what you're building.`
- CEO, courier software: `Hi Daniel, saw RouteDesk now handles proof of delivery. I built a bank's central dispatch module end to end, from manifests to rider OTP handover and 50,000-row courier rate uploads, so I know where those flows break. Glad to connect.`

## Step 5: Save today's list

For each kept person, in order of fit:

```bash
$L add '{"name":"...","title":"...","company":"...","company_site":"...","country":"<e.g. United States, United Kingdom, Germany, Canada>","linkedin_url":"...","domain_match":"...","why_target":"...","source":"linkedin-search","note":"<exact note>"}'
```

This writes `linkedin/<me>/send-connection/linkedin-connections-by-company-jobs/<today>.csv` with `status=prepared`. Check that the row count matches the list.

## Step 6: Hand over to the user

Give one numbered list in chat. For each person:
- name, title, company, clickable profile URL
- one line on why them (`why_target`), with the hire-chance score and its signals
- if a matching role is open, the job link, so the user can also apply through `apply-job-link` (the note still never mentions it)
- the note in its own code block, with its character count

Then the **messages due** from Step 2b: the path of today's follow-up file (`linkedin/<me>/follow-up/linkedin-connections-by-company-jobs/<today>.csv`), and one block per person: name, profile URL, which message it is (message 1, follow-up, answer, check-in, call offer, role), the message in a code block with its character count, and the date it should go out.

Then tell them: open each profile → **Connect** → **Add a note** → paste → **Send**. For messages: open the profile → **Message** → paste → **Send**. If they edit a note or skips someone, they can say so; update the row by running `$L set <url> not-sent` for skipped people. An edited note doesn't need changing in the CSV unless they ask. The next run's Step 1 confirms who was actually sent.

## Step 7: Commit and push

```bash
git add linkedin/<me>/send-connection/linkedin-connections-by-company-jobs linkedin/<me>/reject-connection/linkedin-connections-by-company-jobs linkedin/<me>/messages/company linkedin/<me>/follow-up/linkedin-connections-by-company-jobs
git commit -m "<me>: linkedin company: $(python .claude/skills/job-apply-shared/scripts/me.py stamp) — <N> prepared, <A> accepted, <R> rejected"
git push
```

Commit only these folders. Leave unrelated working-tree changes alone.

## Report

Keep it short:
- Prepared this run: N (why fewer than 5, if so), with each person's hire-chance score; how many companies were dropped for 0–1 points.
- Status check: X newly pending, Y newly accepted, Z not sent.
- Reject list: path to today's reject file and the people in it, for the user to withdraw by hand.
- From `$L stats`: accepted of sent, still pending, replied of accepted, calls or more.
- Conversations: today's follow-up file and how many messages it holds, messages written earlier and still unsent, new replies, calls, interviews or offers.
- Path to today's send file and the commit hash.
