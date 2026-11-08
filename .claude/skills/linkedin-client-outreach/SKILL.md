---
name: linkedin-client-outreach
description: Run when the user says "linkedin client outreach". Finds potential clients who could pay the user (their role and stack from profile.json) for project work that matches what they have already built, per their accomplishments file, resume and skill set. Targets include founders without a CTO, business owners, e-commerce brands, agencies that outsource, and ops leaders. The goal is repeatable client work they can grow into their own company. Keeps only people who match their work and show they may buy now (a buy-chance score). Writes a personal note for each, and after someone accepts, writes the messages that follow on a set timeline (message 1 a day or two after acceptance, one follow-up after 7 days, answers to replies, a call once they describe a need, a proposal only after the call), and saves today's list to linkedin/<me>/send-connection/linkedin-connection-by-client-projects/YYYY-MM-DD.csv. Never sends, withdraws or clicks anything on LinkedIn; the user sends every request themselves. Each run also checks earlier requests and writes the not-accepted-in-7-days / rejected list to linkedin/<me>/reject-connection/linkedin-connection-by-client-projects/YYYY-MM-DD.csv.
---

# LinkedIn Client Outreach

Trigger: **`linkedin client outreach`**. (For people who might hire them as an employee, use the `linkedin-company-outreach` skill instead.)

**Whose run.** Several people share this repo. `<me>` is the person running it: the slug in `.me` at the repo root (`python .claude/skills/job-apply-shared/scripts/me.py`). "The user" means that person. Read only `skillsets-and-contributions/<me>/` (profile.json, proof-map.md, their files) and write only under `linkedin/<me>/`. Never read, write or reuse another person's folders. Run `me.py check` first; if it prints `NOT READY`, stop and offer the `profile-setup` skill.

## Goal

Build a network of **people who buy software projects** and need exactly what the user has already delivered. Each client project should be work they can repeat for the next client in the same niche, because that repeatable work is what their future company will be built on. So prefer clients in a few niches where they have deep proof, not one-off gigs.

Two things must both be true for every person:
1. **Match:** what they need is a system they have already built (the service map in 3a, from their accomplishments and skill set).
2. **May buy:** they show they're likely to pay for that work soon (the buy-chance score in 3d). A perfect match with no budget, no need right now, or a full in-house team is a weak target.

The connection is only the start. The path is: **accepted → message 1 → a few short messages → a call → a proposal → a project** (Step 2b).

## Hard rules

- **Browse like a person.** Follow [HUMAN-BROWSING.md](../job-apply-shared/HUMAN-BROWSING.md): random waits and real reading time on every profile, the shared LinkedIn budget (30 searches / 120 pages a day across all LinkedIn work), never two agents on LinkedIn at once, no tricks to hide automation, and stop using LinkedIn at the first challenge, rate limit or invitation-limit warning.
- **No automated LinkedIn actions.** Claude never clicks Connect, Send, Withdraw, Follow or Message, and never sends anything. Claude only **reads** LinkedIn pages (search results, profiles, posts, the Sent invitations page) in the user's logged-in Chrome, and writes CSV files. The user does every send and withdrawal by hand.
- **Only their own files decide who to target and what to say.** Read all three at the start of every run:
  1. Career accomplishments (`skillsets-and-contributions/<me>/contributions/`): projects, systems and numbers. This is the main source.
  2. Resume (`skillsets-and-contributions/<me>/resume/<resume_file>`): roles, headline numbers, side work (courses, open source).
  3. Skill set (`skillsets-and-contributions/<me>/skills/my-skill-set.md`): the stack they can deliver in.
  Every service offered, `why_target` line and note must come from something real in these files. Never promise work they haven't done.
- **Browser.** LinkedIn pages are read with Claude in Chrome (`claude --chrome` or `/chrome`). If browser tools aren't available, stop and say so. Never ask for or type their password. If LinkedIn shows a login page, CAPTCHA or security check, stop and hand control back.
- **Already on file = never again.** Before researching or listing anyone, check them against **every send and reject file of every track** (all dates, any status: prepared, pending, accepted, not-sent, rejected). If they're already in any of those files, skip them. Run `$L check <url> "<name>" "<company>"` for each candidate; it matches on the profile URL and on name + company, because one person can have more than one LinkedIn URL. `add` runs the same check again and refuses duplicates.
- **One track per company per 30 days.** Before researching anyone, run `$L company <company_site> "<company>"`. It prints `SKIP` if any LinkedIn track or product outreach already reached someone at that company in the last 30 days, so one business never gets a client note, a company note and a product email in the same month.
- **Rejected = never again.** Anyone who has ever landed in a reject file (any track, any date) is never proposed, listed or re-sent again, even if they show up in a new search or a buying-signal post. The ledger's `add` refuses them with `blocked, rejected earlier`. When that happens, drop the person and move on.
- **Location: the user's outreach countries only.** The person's LinkedIn profile location must be in one of the user's `outreach_countries` (profile.json, see `outreach_countries_note`; e.g. the USA, UK, Europe, Canada, Australia, Singapore), and the company must be based there too. **Never include anyone located in one of their `blocked_countries`**, or any company headquartered there, even if everything else fits. Skip every other country as well. Put the person's country in the `country` field; the ledger refuses a row whose country isn't on that list.
- **Per run:** up to **5** people unless the user asks for a different number. Never pad the list. (The product-outreach skill keeps its CEO/CTO connection notes in its own bonus `product` track, which doesn't reduce this number.) Both outreach skills share LinkedIn's weekly invitation limit (about 100 a week). All LinkedIn tracks together (company, client, hiring team, and the bonus product track from `product outreach`) are capped at **90 requests in any 7 days**; count the send files of all four tracks from the last 7 days (not counting `not-sent` rows) before starting, and lower the number to fit.

## Files

```
linkedin/
  scripts/ledger.py                                          shared by every person and every outreach skill
  <me>/                  this person's files only
    send-connection/linkedin-connection-by-client-projects/
      2026-09-29.csv        today's prepared list (one file per run day)
    reject-connection/linkedin-connection-by-client-projects/
      2026-10-06.csv        not accepted within 7 days, or invitation gone, found on that day's run
    messages/client/
      <first-last>-<company>.md   the conversation after acceptance: each message the user sent (exact text, date),
                                  the gist of each reply (not their words in full), and the next step
```

Send-file columns: `date_sent,name,title,company,company_site,country,linkedin_url,domain_match,why_target,source,note,status,status_checked,accepted_date,last_msg_date,msg_count,replied_date`. Here `domain_match` holds the **service** from the map below (e.g. `payments-integration`). Reject files add `reject_reason`.

All reads and writes go through the ledger. Never hand-edit the CSVs:

```bash
L="python linkedin/scripts/ledger.py client"
$L seen                  # every URL in any send or reject file, all tracks (skip these)
$L check <url> "<name>" "<company>"   # SKIP if already in any file; run before researching
$L today                 # today's file + count
$L lint "<note>"         # note must print ok (no AI-sounding text)
$L add '<json row>'      # add one prepared row (status=prepared)
$L open                  # prepared + pending rows to check
$L company <site> "<company>"   # SKIP if any track touched this company in 30 days
$L set <url> pending     # also: accepted | not-sent | messaged | replied | call | proposal | won | no-reply
$L convo                 # messages due after acceptance: message 1, follow-up, answers, check-ins, no-reply
$L due --days 7          # pending rows sent 7+ days ago
$L reject <url> <reason> # move row to today's reject file
$L stats                 # accepted of sent, still pending, replied of accepted, calls
$L rejected              # everyone ever rejected (blocked for good)
```

Dates use the user's local time (profile.json `utc_offset`). `date_sent` is the date the row was prepared; the user is expected to send it the same day.

Run order: **status check (invitations and messages) → reject list → messages due → find clients → research + notes → save CSV → hand over → commit + push.**

## Step 1: Check earlier requests (read-only)

Read the list pages once each, instead of opening profiles one by one (each profile costs a page of the daily LinkedIn budget):
1. Run `$L open` to get every `prepared` and `pending` row.
2. Open `https://www.linkedin.com/mynetwork/invitation-manager/sent/` and scroll to the end. Collect the name and profile URL of every pending invitation.
3. Open **My Network → Connections** (`https://www.linkedin.com/mynetwork/invite-connect/connections/`), sorted by **Recently added**, and scroll back to the date of the oldest open row. Collect the names and URLs.
4. For each row from step 1:
   - **Listed under Sent invitations** → `$L set <url> pending`.
   - **In the recent connections** → `$L set <url> accepted`.
   - **On neither list, and the row was `prepared`** → the user never sent it: `$L set <url> not-sent`. It stays on file and is never proposed again.
   - **On neither list, and the row was `pending`** → declined or withdrawn: `$L reject <url> "declined or withdrawn"`.
   - Open a profile only when a name can't be matched (two people with the same name, a changed URL). If it's gone → `$L reject <url> "profile unavailable"`.
5. **Messages.** If any row is `accepted`, `messaged` or `replied`, open **Messaging** (`https://www.linkedin.com/messaging/`) once and read only the threads with those people:
   - the user sent the suggested message (or their own) → `$L set <url> messaged` (once per message they sent since the last run).
   - They answered → `$L set <url> replied`. Write the gist in their `linkedin/<me>/messages/client/<first-last>-<company>.md`, never their full words.
   - A call is booked → `call`; a proposal sent → `proposal`; the project is agreed → `won`.

## Step 2: Build the reject list

1. Run `$L due --days 7`. For each row, `$L reject <url> "no response in 7 days"`.
2. This moves every row that wasn't accepted within 7 days into `linkedin/<me>/reject-connection/linkedin-connection-by-client-projects/<today>.csv`. That file is today's reject list.
3. In the report, list these people (name, company, profile URL) so the user can **withdraw them themselves** on the Sent invitations page.

## Step 2b: Messages after acceptance

Run `$L convo`. It lists who needs a message today. For each person, reread their row, the note that was sent, their `messages/client/` file and (for replies) the thread from Step 1, then write the next message for the user to send themselves. Claude never sends.

**Timeline (expected; the real conversation always wins):**

| When | Message | After the user sends it |
|---|---|---|
| Day 1–2 after they accept (not the same hour; not after day 3) | **Message 1**: thanks, one question about the problem behind your note (how they handle it today), and one short point from the matching system they built. No pitch | `set messaged` |
| They reply | **Answer within 24 hours**: answer, one concrete idea for their case, one question back | `set messaged` |
| 7 days after message 1, no reply | **The one follow-up**: something new (their latest post, launch, a hire, a new feature) plus one small, useful idea for their problem. No ask | `set messaged` |
| 14 days after the follow-up, still nothing | Nothing more. `set no-reply` | `no-reply` |
| As soon as they describe a need, a pain, or ask what they'd do | **The call offer**: "Happy to take a quick look on a 15-minute call, no strings." | `call` once booked |
| After the call, if they want it | **A short proposal** (scope, timeline, price, what they need from them), sent the way they asked (message or email). Never prices or proposals in DMs before a call | `proposal` |
| They agree | Confirm the start and the first step | `won` |
| "Not now" or "no budget yet" | Thank them: "Mind if I check back in a couple of months?" | stays `messaged` |
| Quiet for 30 days after talking | **Check-in**: something useful for their business (a small idea, a related thing they built). Never "any projects for me?" | `set messaged` |

**Predicted messages** (patterns only; write each one fresh). The examples come from one engineer's real files; every real note uses only the current user's own proof.
- **Message 1, recruitment agency owner:** `Thanks for connecting, Sarah. How does your team search old CVs today, a shared drive or an ATS? On the platform I built, Boolean search over 50,000+ resumes cut most of that digging.`
- **Message 1, e-commerce founder:** `Thanks for connecting, Omar. Is the NetSuite stock synced to the store on a schedule, or updated by hand? On a wheel brand's store I built it to run every few minutes, and oversells mostly stopped.`
- **Follow-up:** `Saw the new dealer portal is live, nice. If dealers ever need live stock in their own systems, a small reseller API with keys per dealer works well. I built one last year.`
- **Call offer:** `Happy to take a quick look on a 15-minute call, no strings.`

**Message rules:** written per [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md), checked with `python .claude/skills/job-apply-shared/scripts/apply.py text "<message>"`. 2–4 sentences, under about 500 characters, first name, no links, no portfolio unless asked. **No pitch, prices or "hire me" in message 1 or the follow-up.** Never more than two messages in a row without a reply. Never "just following up", "bumping this", or guilt. Save each suggested message in their `messages/client/<first-last>-<company>.md` (the history), and add it to today's follow-up file `linkedin/<me>/follow-up/linkedin-connection-by-client-projects/<today>.csv` with `$L followup add` (same commands and rules as company outreach Step 2b). In Step 1, confirm sent ones with `$L followup open` → `$L followup sent <url>` or `skip <url>`.

## Step 3: Find clients

### 3a. Service map (what they can sell, from their files)

Read section 2 of `skillsets-and-contributions/<me>/proof-map.md` (service, their proof, who buys it). Re-read the accomplishments each run and add rows to that file when you see more, always from their own files. Example rows (one engineer's map):

| Service (`domain_match`) | Their proof | Who buys it |
|---|---|---|
| `payments-integration` | Stripe and PayPal gateways, subscriptions with signed webhooks, failed-payment recovery | SaaS founders adding paid plans, marketplaces, subscription businesses |
| `recruitment-platform` | Boolean search over 50,000+ resumes, CV parsing, Gmail sync | recruitment/staffing agencies, niche job boards |
| `devops-deploy` | Docker, CI/CD, cloud deploys | only as an add-on to another service, never on its own |

**Niche focus:** count `domain_match` in the send files. Rotate through services, but keep coming back to the 2–3 services where connections accept and reply most. Those are the niches their company should grow from. Note in the report which services do best. **This only breaks ties:** a person with a higher buy-chance score (3d) always comes first.

### 3b. Who to target

- **Titles:** Founder, Co-founder, CEO, Owner, Managing Director, COO, Head of Operations, Head of Product, Product Owner, Agency Owner / Director at a digital, marketing or dev agency (white-label partner).
- **Best signals** (look for at least one):
  - Founder has **no CTO or engineering team** listed on LinkedIn or the company site.
  - Recent post asking for a developer, a "technical partner", an MVP build, an integration or automation ("looking for a developer", "need help with Stripe", "moving off Shopify/WordPress", "anyone built X?").
  - Recently funded (pre-seed/seed) with a small team and no backend lead yet.
  - An agency that outsources development or shows many client projects with a tiny in-house team.
  - A business visibly running on spreadsheets, no-code tools or manual exports in one of the service areas.
- **Company:** 1–50 people, or a larger non-tech business that needs one system built. The person and the company must be in one of the user's `outreach_countries`. Never a blocked country, and no other regions.
- **Skip:** founders who get flooded with requests (10,000+ followers, a creator or influencer profile, a well-known name in tech), recruiters, job seekers, other freelancers/dev shops competing for the same work (unless they're a white-label partner fit), large enterprises with procurement, and companies with a clear in-house backend team (those belong to company outreach).

### 3c. Search LinkedIn (read-only)

- **People search:** a title + a buyer keyword from the service map, e.g. `founder subscription app`, `CEO recruitment agency`, `owner ecommerce NetSuite`, `founder online academy`, `COO courier company`, `agency owner Shopify`, `founder no-code MVP`.
- **Content search (posts):** search **Posts** for buying signals, e.g. `"looking for a backend developer"`, `"need a developer" Stripe`, `"technical co-founder" SaaS`, `"migrating from WordPress"`, `"NetSuite integration"`, `"LMS" "developer"`, from the past week. The post author is the target. Use `source=linkedin-post` and put the post's gist in `why_target`.
- **Companies search** with buyer keywords, then the **People** tab for the founder/owner.
- Use LinkedIn's **Locations** filter with the user's `outreach_countries` (e.g. United States, United Kingdom, Germany, Netherlands, Canada, Australia). Never add a blocked country.
- Skip anyone in `$L seen`, which already includes everyone in `$L rejected`. Then run `$L company <site> "<company>"` for the company and `$L check` for the person, before opening their profile for research.

### 3d. Buy-chance score

Check each company off LinkedIn first where you can (their site, careers page, funding news, job boards), so LinkedIn pages are spent only on people worth it. One point each, with a source:

| Signal | Point if |
|---|---|
| Asked for help | a post in the last 30 days asking for a developer, a technical partner, an integration, an MVP or automation |
| No tech team | no CTO or engineers on LinkedIn or the team page |
| Money to spend | funding in the last 12 months, or clear revenue (paying customers, a team of 5+, a real store or service with volume) |
| Visible pain | running on spreadsheets, manual exports, no-code tools stretched past their limit, or a broken or slow flow in the service area |
| Changing now | a launch, a new market, a migration, or a new product line announced in the last 60 days |
| Already outsources | uses freelancers or agencies (posts, job boards, a partner page) |
| Decides alone | founder or owner of a company under ~30 people, who can say yes without procurement |

**Skip** people with nothing to pay with (a hobby project, a solo idea with no revenue or funding), and companies that clearly have an in-house backend team.

Keep people with **2 or more points**, and fill the list from the highest scores down. Never pad with 0–1 point people.

Write `why_target` as one line linking their need to their proof, then the buy score and its signals, e.g. `recruitment agency, 12 staff, no dev team, posts about sourcing time ↔ recruiting platform: Boolean search over 50K resumes + Gmail sync | buy 4/7: asked for help, no tech team, 12 staff, decides alone`.

## Step 4: Research each person and write their note

A note that could be sent to anyone is not saved.

**Research:**
1. Open the profile. Confirm name, current title and company.
2. Read the headline, About, and recent posts (Activity tab).
3. Open the company site. Note what they sell and **the one system they seem to be missing or struggling with**.
4. Find **one specific hook**, in this order: a post about a need or problem → a visible gap on their site or product → a recent launch or funding.
5. Pick **one matching proof** from the accomplishments file that shows they have already built that system.
6. Check the profile has a **Connect** option (directly or under **More**). Drop anyone where LinkedIn would require their email address.

**No specific hook → skip the person.**

**Angle:** talk business outcome, not tech jargon. Name the problem in their words (failed payments, manual order sync, recruiters digging through CVs, students waiting for video uploads), then the result they delivered with a number. Plain words, like one business person talking to another.

**Note rules:**
- Up to 300 characters (Premium limit). Aim for 200–280.
- Start with their first name. Their hook goes in the first sentence.
- One proof, with a number when there is one. It's fine to say they build this kind of system for businesses.
- No hard pitch: no prices, no "hire me", no "DM me for a quote", no links, no portfolio drop, no flattery, no clichés ("I came across your profile", "expand my network", "hope you're doing well").
- End with a light, low-pressure reason to connect (e.g. happy to share how they handled X), not a sales question.
- No two notes in a run share the same sentence structure.
- **Self-check:** if you swapped in another person's name and company, would the note still make sense? If yes, rewrite it or skip them.

**Write like the user typed it themselves:** follow [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md) for every note (easy words, short sentences, no LLM words, phrases, characters or habits). For notes in particular:
- Short sentences a busy founder or engineer would type on a phone. Say what they built and what it did, then stop. No build-up, no summing up at the end.
- No links, no emojis.
- Vary the openings. Don't start every note with "Hi <name>, saw/noticed...". Sometimes lead with their post, sometimes with the product, sometimes with a plain observation.
- Before saving, run `$L lint "<note>"`. It must print `ok`. If it prints `REWRITE`, rewrite the note in plainer words (don't just swap in a synonym). `add` runs the same check and refuses notes that fail.
- Read it aloud in your head. If it sounds like a LinkedIn post or a marketing email, rewrite it.

**Examples** (show the pattern; never copy). The examples come from one engineer's real files; every real note uses only the current user's own proof.
- Recruitment agency owner who posted about sourcing: `Hi Sarah, your post about recruiters losing hours in old CV folders rang true. I built a recruitment platform where a team searches 50,000+ resumes with Boolean queries and candidate emails sync from Gmail into each profile. Happy to share what worked.`
- E-commerce founder on NetSuite: `Hi Omar, noticed Forgeline lists stock that lives in NetSuite. I built the NetSuite sync for a wheel brand's store, moving products, inventory and pricing automatically, plus a reseller API so partners pull live stock. Glad to connect.`

## Step 5: Save today's list

For each kept person, in order of fit:

```bash
$L add '{"name":"...","title":"...","company":"...","company_site":"...","country":"<e.g. United States, United Kingdom, Germany, Canada>","linkedin_url":"...","domain_match":"<service>","why_target":"...","source":"linkedin-search","note":"<exact note>"}'
```

This writes `linkedin/<me>/send-connection/linkedin-connection-by-client-projects/<today>.csv` with `status=prepared`. Check that the row count matches the list.

## Step 6: Hand over to the user

Give one numbered list in chat. For each person:
- name, title, company, clickable profile URL
- service + one line on why them (`why_target`), with the buy-chance score and its signals
- the note in its own code block, with its character count

Then tell them: open each profile → **Connect** → **Add a note** → paste → **Send**. If they skip someone, run `$L set <url> not-sent`. The next run's Step 1 confirms who was actually sent.

Then the **messages due** from Step 2b, one block per person: name, profile URL, which message it is (message 1, follow-up, answer, call offer, check-in), the message in a code block with its character count, and the date it should go out. For messages: profile → **Message** → paste → **Send**. Claude never sends.

## Step 7: Saved locally (nothing to push)

Everything this run made is saved in the person's own folders, which are git-ignored and stay on this machine. There is nothing to commit or push. End the report with where the files are.

## Report

Keep it short:
- Prepared this run: N (why fewer than 5, if so), grouped by service, with each person's buy-chance score; how many were dropped for 0–1 points.
- Status check: X newly pending, Y newly accepted, Z not sent.
- Reject list: path to today's reject file and the people in it, for the user to withdraw by hand.
- From `$L stats`: accepted of sent and still pending, plus which services accept best (niche signal for their future company).
- Conversations: messages due today (Step 2b), new replies, calls, proposals and projects won.
- Path to today's send file (saved locally, not pushed).
