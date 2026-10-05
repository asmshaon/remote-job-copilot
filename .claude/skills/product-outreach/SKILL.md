---
name: product-outreach
description: Run when the user says "product outreach" (optionally with a number, e.g. "product outreach 3", or with one product link, "product outreach <url>"), or "product outreach replies" to only answer replies and draft follow-ups. A different way of reaching companies than the job-apply skills. Finds products in the startup and product directories from their product directories list, keeps only products of small funded startups (2-50 people, raised in the last 24 months) that actively care about their product and match their career accomplishments and skill set, ranks them by how likely the founders are to reply, uses each kept product like a real user (a free tier or public pages only) to find real, reproduced functional bugs (never typos or cosmetic issues), preferring signup, billing, the core feature and failing API requests seen in the browser's own network traffic, finds the CEO, CTO and technical co-founder, and emails one person per company first (the one who owns the bug's area), holding the teammates' emails until that thread goes quiet. Each email is personal, short (100-190 words) and 4 paragraphs (a short appreciation, the bug they found, the user through their accomplishments, how they could help or join the team, ending with an easy question to get a reply; a call is offered only in their 2nd or 3rd reply), with a subject about their product and the problem only (never about them), and with a greeting, tone and sign-off that fit the recipient's culture. Every person gets a LinkedIn connection request with a personal note (the user sends it themselves after the first email), and the email goes out as a Gmail draft (Claude never sends). LinkedIn is opened only after a product is final, and each person's profile only once, directly by URL. The connections live in their own LinkedIn track, product (linkedin/<me>/send-connection/linkedin-connections-by-product-outreach/YYYY-MM-DD.csv), run like the other outreach tracks (status check, 7-day reject list in linkedin/<me>/reject-connection/linkedin-connections-by-product-outreach/, never-again rules) but as a bonus on top of the 12-a-day target, inside the 90-in-7-days cap. Keeps notes per product in product-outreach/<me>/<YYYY-MM-DD>/<product-name>/ (product details, company and LinkedIn URLs, the people, the bugs, the emails, the LinkedIn notes) and records each email in product-outreach/<me>/contacted.csv with its score and bug area, so stats show what gets replies. One short follow-up in the same thread after 5 days without a reply. Never mentions their skill set or that they want a job.
---

# Product Outreach

Trigger: **`product outreach`**. Examples:
- `product outreach`: find and email up to **5 products** (default).
- `product outreach 3`: up to 3 products.
- `product outreach <product url>`: only this product. The filters are still checked, but a failed check is shown to the user instead of silently skipping (their blocked countries stay blocked).
- `product outreach replies`: **replies and follow-ups only**, fast. Runs Step 0a with "Answering replies" (Gmail checks, reply drafts, `$L due` follow-ups and held teammates) and Step 0c (LinkedIn messages due today, read from Messaging once), shows the drafts for their okay, saves them, updates `outreach.md` and the ledger, and commits. No new products, no LinkedIn. Run it whenever a founder may have replied: replies should be answered within hours, not at the next full run.

**How it differs from the job-apply skills:** there is no job post. The user reaches the people who build a product they could make better, shows they have used it and found real problems, and lets their past work speak. The email never asks for a job.

**Whose run.** Several people share this repo. `<me>` is the person running it: the slug in `.me` at the repo root (`python .claude/skills/job-apply-shared/scripts/me.py`). "The user" means that person. Read only `skillsets-and-contributions/<me>/` (profile.json, proof-map.md, their files) and write only under `product-outreach/<me>/` and `linkedin/<me>/`. Never read, write or reuse another person's folders. Run `me.py check` first; if it prints `NOT READY`, stop and offer the `profile-setup` skill.

## Hard rules

- **Claude never sends.** Every email is saved as a **Gmail draft**. The user opens Drafts and sends each one themselves. Claude never clicks Connect, Send, Withdraw, Follow or Message on LinkedIn, and sends no DMs, contact forms, support tickets or replies either.
- **Two channels, one email first.** Every CEO, CTO and technical co-founder gets a LinkedIn connection request with a personal note. Only **one person per company gets an email at first** (Step 6); the teammates' emails are written but held, and drafted only if that thread goes quiet (Step 0a). The user sends the email first, then the requests the same day. A person whose LinkedIn is blocked (Step 5b) or missing can still be the one emailed. A product needs at least one email draft to go ahead.
- **Truth only.** Every fact about the user comes from the accomplishments file (`skillsets-and-contributions/<me>/contributions/`). Every fact about the product comes from the product itself, its site, docs, changelog or public posts. **A bug is mentioned only if Claude reproduced it twice.** Never invent or inflate a bug.
- **Test like a normal user, never like an attacker.** See Step 4. No scanners, no fuzzing, no changing requests, no poking at other users' data, no load. Their name is on every email, so every test must be one the company would be fine seeing in their logs.
- **Browse like a person.** Follow [HUMAN-BROWSING.md](../job-apply-shared/HUMAN-BROWSING.md) on every site: random waits and real reading time, stop at the first CAPTCHA, login wall or rate limit.
- **LinkedIn: late, direct and once.** LinkedIn is not touched in Steps 0–4 or while finding people. It's opened only in Step 5c, **after a product is final** (it passed every filter and has a reproduced bug), and then only to open each person's profile **directly by its URL, once**. No LinkedIn search, no company pages, no browsing around, no Activity tab clicks beyond what the profile shows. **Never open the same profile twice**, in this run or any later run: everything needed is read in that one visit and saved in `people.md`, which is the record from then on. The only other LinkedIn pages this skill reads are **Sent invitations** and the recently added **Connections** list, once each, for the status check in Step 0b. These pages count toward the shared LinkedIn budget in [HUMAN-BROWSING.md](../job-apply-shared/HUMAN-BROWSING.md) (30 searches / 120 pages a day across all LinkedIn work). Never run this while another agent is on LinkedIn.
- **Passwords and payment.** Never type a password or payment details. A product that needs an account: The user types the password (or okays "Continue with Google" for that site). A product that needs a card for its trial is tested only on its public pages.
- **Countries.** The company is based in one of the user's `company_countries` (profile.json, the same list as the job-apply skills; `$L add` enforces it). **Never one of their `blocked_countries`**, and follow `company_countries_note` (e.g. skip companies whose team is mainly in a blocked country).
- **Human writing.** Every email, connection note and suggested message follows [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md): easy words, short sentences (never over 30 words), concrete details, nothing that sounds like an LLM wrote it. Bug details stay simple too: say what they clicked and what happened. Checked with the helpers (Step 6).
- **Privacy.** `product-outreach/<me>/` is committed to GitHub. Never save their address, phone number, passwords, cookies, auth tokens or API keys there. Redact tokens in saved API requests (`Authorization: Bearer <redacted>`). **Security issues are never written to the repo** (see Step 4).

## Sources of truth (read at the start of every run)

1. product directories list (`skillsets-and-contributions/<me>/product-directories/`): where to look for products.
2. Career accomplishments (`skillsets-and-contributions/<me>/contributions/`): what they have built. Drives the filter and paragraph 3.
3. Skill set (`skillsets-and-contributions/<me>/skills/my-skill-set.md`): used **only to filter** products (stack fit). Never quoted in an email.
4. `skillsets-and-contributions/<me>/profile-answers.md`: name, sign-off, email, LinkedIn, portfolio.

## Helpers (run from the repo root)

```bash
L="python .claude/skills/product-outreach/scripts/ledger.py"
$L seen                                  # company domains already in the ledger
$L check <company_site> "<company>"      # SKIP if emailed in the last 180 days; info if they applied or connected there
$L person <email> [<linkedin_url>]       # SKIP if this person was ever emailed
$L add '<json row>'                      # record one email draft (status email-draft)
$L set <email> <status>                 # email-draft held sent followed-up no-reply replied call interview offer withdrawn
$L drafts                                # drafts not yet confirmed sent
$L due                                   # follow-ups due, threads gone quiet, held teammates now free to email
$L stats                                 # reply rate by score, bug area and directory

A="python .claude/skills/job-apply-shared/scripts/apply.py"
$A email <email.md> --paras 4            # check the email (4 paragraphs, 100-190 words, no skills in para 3)
$A text "<any text>"                     # check a single line, e.g. the subject
$A country "<country>"                   # ok if the company's country is a target

P="python linkedin/scripts/ledger.py product"   # the product LinkedIn track (same ledger as the outreach tracks)
$P check <url> "<name>" "<company>"      # SKIP if the person is in any send or reject file of any track
$P company <site> "<company>"            # SKIP if any LinkedIn track reached this company in the last 30 days
$P lint "<note>"                         # connection note must print ok
$P add '<json row>'                      # add one prepared row to today's product send file
$P today | open | set <url> pending|accepted|not-sent|messaged|replied|call|interview|offer|no-reply | due --days 7 | reject <url> <reason> | stats
$P convo                                 # LinkedIn messages due after acceptance (Step 0c)
$P followup add|today|open|sent|skip      # today's LinkedIn follow-up file (Step 0c)
```

## Folder layout

```
product-outreach/<me>/
  contacted.csv                         ledger, one row per person emailed
  2026-10-01/
    <product-name>/                     lowercase, hyphens
      product.md                        product, company, links, basic info, why it matches them
      people.md                         CEO / CTO / technical co-founder, with sources
      bugs.md                           every reproduced bug, with steps and API details
      screenshots/                      optional, only screenshots that show a bug
      emails/
        <first-last>-<role>.md          the exact email: drafted for the first person, held for teammates
        <first-last>-followup.md        the follow-up, if one was drafted
      linkedin.md                       the LinkedIn track notes for this product (see Step 8)
      outreach.md                       status: drafted, sent, replied, LinkedIn request, next step

linkedin/<me>/
  send-connection/linkedin-connections-by-product-outreach/
    2026-10-01.csv                      the product track: one row per connection request, status prepared/pending/accepted/not-sent
  reject-connection/linkedin-connections-by-product-outreach/
    2026-10-08.csv                      not accepted within 7 days, or invitation gone
  follow-up/linkedin-connections-by-product-outreach/
    2026-10-02.csv                      LinkedIn messages to send that day to people who accepted (Step 0c)
```

The product track works like the other LinkedIn tracks (company, client, hiring team): the same ledger, columns, statuses, 7-day reject list and "already on file / rejected = never again" rules across all four tracks. It's a **bonus track**: its rows don't count toward the daily target (profile.json `linkedin_daily`, e.g. company 5, client 5, hiring team 2), but they do count toward the weekly cap (`linkedin_weekly_cap`, e.g. **90 requests in any 7 days**).

Work in a staging folder `<scratchpad>/product-outreach/<product-name>/` until the drafts exist. Products that get skipped leave nothing in `product-outreach/<me>/`; they're only listed in the chat report.

Run order: **check old drafts, follow-ups and held teammates → LinkedIn status check and reject list (product track) → LinkedIn messages to people who accepted → find products → filter → research → test and find bugs → find the people (off LinkedIn) → one LinkedIn visit per new person → write emails and connection notes → review → Gmail drafts → save notes and product-track rows → commit.**

## Step 0: Check earlier drafts and connection requests

### 0a. Email drafts

`$L drafts`. For each row, search Gmail **Sent** (read-only) for that subject and recipient:
- found in Sent: `$L set <email> sent`, and update that product's `outreach.md`
- a reply from them in the Inbox: `$L set <email> replied`, note the reply's gist in `outreach.md`, tell the user, and offer to draft their answer (see "Answering replies" below)
- still only in Drafts after 7 days: ask the user whether to drop it. If yes, `$L set <email> withdrawn` and delete the Gmail draft.

Then `$L due` and handle its three lists:
- **`follow_up`** (sent 5+ days ago, no reply): first search Gmail once more for a reply. None → recheck the bug in the product (one quick visit as a normal user), then write **one** follow-up as a reply in the same Gmail thread, saved as a draft (never sent by Claude). Save it as `emails/<first-last>-followup.md` and `$L set <email> followed-up`. Rules:
  - 2–4 short sentences, same culture sign-off, `[Gmail default signature]` below
  - it brings something new: "Checked again today and the trial still isn't applied at checkout", or "Saw it's fixed now, nice work"; if fixed, no ask beyond a friendly line
  - ends with the same kind of easy question as the first email
  - never "just following up", "bumping this", "circling back", "did you get a chance", or any guilt or pressure
  - **only one follow-up per person, ever**
- **`set_no_reply`** (followed up 7+ days ago, still nothing): `$L set <email> no-reply`. Nothing more is sent to that person.
- **`email_next_person`** (a held teammate at a company where everyone emailed is `no-reply`): reread their held email, recheck the bug once (fixed → mention it kindly or drop it), run the checker again, show it in the review (Step 7), and after the user's okay draft it and `$L set <email> email-draft`. This teammate gets their own follow-up later the same way. At most one new person per company per week.

### Answering replies

The path is: first email → reply → a few short messages → a call → a job. Don't rush the call. Each answer is saved as a Gmail draft in the same thread (Claude never sends), follows HUMAN-WRITING.md, is short (2–5 sentences), and is logged in `outreach.md`.
- **Their 1st reply:** answer what they asked and give what they offered (exact steps, request details, a screenshot). Thank them. Maybe one useful idea from their closest work. **No call offer yet.**
- **Their 2nd or 3rd reply:** once they're engaged (they asked a question, fixed the bug, or talked about their plans), offer a short call in one easy line, e.g. "Happy to jump on a quick 15-minute call if it's easier to go through it live." No calendar link unless they ask for a time.
- **They offer a call first:** say yes right away at any point.
- **They say thanks and stop:** no follow-up push. Leave it there.
- **Before each answer**, recheck the bug once if it matters for the answer; if they fixed it, say so and thank them.
- **Track the funnel:** a call is booked → `$L set <email> call`; an interview → `interview`; an offer → `offer`. Once someone at a company replies, held teammates there stay held (no email), and the replier is the contact from then on.

### 0b. LinkedIn status check and reject list (product track)

The same as Steps 1–2 of the [client outreach skill](../linkedin-client-outreach/SKILL.md), for the product track. Skip it if `outreach` already did its Phase 1 today (it checks the product track too); otherwise:
1. `$P open` for every `prepared` and `pending` row. If there are none, skip LinkedIn here.
2. Open `https://www.linkedin.com/mynetwork/invitation-manager/sent/` once and scroll to the end. Collect the pending names and URLs. Then open **My Network → Connections** sorted by **Recently added** once, back to the oldest open row's date.
3. For each row: listed under Sent → `$P set <url> pending`. In the recent connections → `$P set <url> accepted`. Not listed, not connected, was `prepared` → `$P set <url> not-sent`. Not listed, not connected, was `pending` → `$P reject <url> "declined or withdrawn"`. Profile gone → `$P reject <url> "profile unavailable"`. Decide from the Sent page and what the ledger and `linkedin.md` already hold; **don't reopen a profile** this skill visited before (see the LinkedIn hard rule). If it can't be told without a visit, leave the row as it is.
4. `$P due --days 7`, and for each row `$P reject <url> "no response in 7 days"`. That writes today's `linkedin/<me>/reject-connection/linkedin-connections-by-product-outreach/<today>.csv`, which the user uses to withdraw those requests by hand.
5. Mirror the changes in each product's `linkedin.md` and `outreach.md` (accepted, rejected, not sent).

### 0c. LinkedIn messages to people who accepted

Someone who accepted is now reachable on two channels, so the email and LinkedIn must read as **one conversation**, not two campaigns.

1. If any product row is `accepted`, `messaged` or `replied`, open **Messaging** once and read only those threads. `$P followup open` first: sent ones → `$P followup sent <url>` (sets `messaged`), dropped ones → `$P followup skip <url>`. Their replies → `$P set <url> replied`, with the gist in `outreach.md`.
2. **Sync with the email.** For each person, also read their `outreach.md` and the Gmail thread. If they already talk with the user on either channel, record it (`$P set <url> replied`, then `messaged` for their answer) and **keep the conversation where they answered**. No separate "message 1" on the other channel.
3. Run `$P convo`. For each person due, read their `linkedin.md`, `people.md`, `outreach.md` and email status, then write the message:

| When | Message |
|---|---|
| Day 1–2 after they accept, **no email reply yet** | **Message 1**: thanks, one light line on the product (what they liked, or a new release), and one easy question about their work. Don't repeat the bug list and never ask "did you see my email?". If something changed (they fixed the bug, a PR is open), say it in one line |
| Day 1–2 after they accept, a **held teammate** (no email sent) | **Message 1**: thanks, the product, and the issue in one short line at most, as something the user noticed. One easy question |
| They replied on LinkedIn | **Answer within 24 hours** on LinkedIn, as in "Answering replies" (Step 0a): give what they offered, no call in the first answer, a call in the 2nd or 3rd once they're engaged |
| 7 days after LinkedIn message 1, no reply on any channel | **One LinkedIn follow-up** with something new (a release, their post, a fix that went live). Skip it if the email follow-up went out in the last 5 days; wait until 5 days have passed |
| Still nothing | Stop. **At most 3 unanswered touches across both channels** (email, email follow-up or LinkedIn message 1, LinkedIn follow-up). Then `$P set <url> no-reply` and `$L set <email> no-reply` |
| Quiet for 30 days after talking | **Check-in** with something useful about their product. Never "any roles?" |

4. Each message follows [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md): 2–4 sentences, under about 500 characters, first name, no links unless they asked (a PR or issue they agreed to is fine), no job ask. Then add it to **today's follow-up file**:
   ```bash
   $P followup add '{"linkedin_url":"...","message_type":"message-1|follow-up|answer|call-offer|check-in|thank-you","message":"<exact message>","log":"product-outreach/<me>/<date>/<product-name>/linkedin.md"}'
   ```
   This writes `linkedin/<me>/follow-up/linkedin-connections-by-product-outreach/<today>.csv`. Also log it under the person in `linkedin.md`. `add` checks the writing and refuses a second message to the same person on the same day; `convo` leaves out anyone with a message still waiting. A message unsent after 3 days is rewritten for the current state or dropped.
5. In the report: the path of today's follow-up file and each message in a code block with its character count. The user sends each one themselves (profile → **Message** → paste → **Send**).

## Step 1: Find products in the directories

1. Read the directories PDF. It groups them: launch platforms (Product Hunt, Launch YC, BetaList, Indie Hackers, Show HN, BetaPage, Uneed, Fazier, Microns...), AI directories (TAAFT, Futurepedia, Toolify...), open source (Open Alternative, GitHub Trending, Devpost...), funded startups (YC directory, Wellfound, Techstars...), and SaaS review sites (G2, Capterra, AlternativeTo, SaaSHub, GetApp, Software Advice). Not all of them fit the targets (small, funded, active, backend-heavy):
   - **Use first:** YC directory and Launch YC (newest batches), Show HN, Wellfound (funded startups), Techstars and other accelerator portfolios, recent funding news (seed and Series A rounds of the last 6 months), Product Hunt (recent launches with a funded team).
   - **Use sometimes:** open-source lists (Open Alternative, GitHub Trending) for commercial open-source startups; BetaList and Indie Hackers only when the listing shows a funded team.
   - **Skip:** SaaS review sites (G2, Capterra, GetApp, Software Advice, AlternativeTo, SaaSHub), which list mostly bigger or older companies, and AI directories, which list mostly thin AI wrappers with no real backend and no funding. Use them only to look up one product already found elsewhere.
2. Pick **2–3 directories per run** from the "use first" list, rotating: count the `directory` column in `contacted.csv` and prefer the least-used ones, and once `$L stats` has 20+ companies, prefer the directories with the best reply rate. **Always include at least one funded-startup source** (YC directory, Launch YC, Wellfound, Techstars, or funding news), since every product must be a funded small startup (Step 2). Mix it with a launch platform. Prefer categories and search terms from the table in Step 2.
3. Browse each directory's category pages, search results or recent launches with the directory's own filters, newest first (recent batches, recent launches, recently funded). Collect about **15–25 candidates**: product name, product URL, directory page URL, one-line description.
4. Drop anything whose domain is already in `$L seen`.

## Step 2: Filter by their accomplishments and skill set

Read section 1 of `skillsets-and-contributions/<me>/proof-map.md` (their proof → products that match). Re-read the accomplishments every run and add rows to that file when you see more, always from their own files. The product must match at least one row **strongly** (its core problem is the same kind of system they built). Example rows (one engineer's map):

| Their proof (from the accomplishments) | Products that match |
|---|---|
| a monitoring product: 1,200+ servers, metrics every minute, dashboards, 200+ teams | server/infra monitoring, observability, uptime, telemetry |
| alert rules and delivery over 8 channels (email, SMS, Slack, webhooks...) | alerting, incident management, notification infrastructure |
| Boolean search over 50,000+ resumes, CV parsing, Gmail sync | ATS, recruiting, HR tech, talent marketplaces |

Keep a product only if **all** hold:
1. **Domain match** with a row above. Write which row and why.
2. **Backend-heavy web product** (SaaS, API, platform, marketplace) where their kind of work matters. Skip games, hardware, pure mobile apps, crypto tokens, agencies, and thin AI wrappers with no real backend.
3. **Stack fit (from the skill set and profile.json `stack`):** their stack is used or likely (job posts, GitHub, engineering blog, public repos), or unknown. Skip it if the product is clearly built only in what `stack.skip` names, unless the domain match is very strong; say so in `product.md`.
4. **Company country** is a target: `$A country "<country>"` prints `ok` (site footer, imprint, about page, YC/Crunchbase profile).
5. **Founders who read their own messages.** Skip a product whose founders get flooded (10,000+ followers, a creator or influencer profile, a well-known name in tech).
6. **A small startup that has raised money.** About **2–50 people**, founders named somewhere public, and outside funding (pre-seed, seed or Series A, an accelerator like YC or Techstars, or known angels) raised in the **last 24 months**, shown by a public source (YC page, Crunchbase, Wellfound, a funding post or press release). Funded teams have money to hire and pressure to ship. Small teams mean the founders still read their own email. Skip bootstrapped side projects, companies past Series A, and anything over 50 people.
7. **The team cares about the product.** At least two of these: a changelog, release or launch in the last 60 days; founders posting about the product or answering users in public (Show HN or Product Hunt comments, X or LinkedIn posts, GitHub issues); a public roadmap, feedback board or community (Discord, Slack); docs that are kept up to date. A product that has gone quiet won't care about a bug email.
8. **Testable:** public pages plus a free plan, free trial without a card, demo or public API docs.
9. **New:** `$L check <site> "<company>"` prints `new`, and `$P company <site> "<company>"` prints `new` (no LinkedIn track reached anyone there in the last 30 days; this one track per company rule keeps a startup from getting a company-track note and a product email in the same month). If it prints `info:` lines (they applied there or sent a LinkedIn request), keep going but mention it in the review.

### Reply-chance score

The goal is a reply, then a call, then a job, so rank the products that are left by how likely the founders are to answer. One point each, written in `product.md` with the source. It's scored twice: **before testing** on the first eight signals (out of 8), and **after testing** with the money-flow point added (out of 9):

| Signal | Point if |
|---|---|
| Fresh money | funding round or accelerator batch in the last 6 months |
| Fresh launch | launched or made a big release in the last 60 days |
| Tiny team | 2–20 people, or 0–2 engineers besides the founders |
| Hiring | an open engineering role (any region), best of all one in the user's stack |
| Remote team | team already spread across countries, says remote-first, or hires through Deel/Remote.com |
| Founders reply in public | founders answer comments, issues or posts themselves |
| Bug in a money flow | the reproduced bug (Step 4) is in signup, onboarding, checkout, billing, the core feature or the public API |
| Easy time zone | as profile.json `easy_time_zones` says (a few hours or less from the user's time zone) |
| Open source | public repo, so the fix can also go in as an issue or pull request |

1. **Before testing:** rank by the domain match first, then by the score out of 8, then by how much can be tested. Drop anything under 2. Test the top **N + 2** (default 7), not more, since each test takes 15–30 minutes.
2. **After testing (Step 4):** add the money-flow point. **Drop a product under 3 out of 9** unless its domain match is very strong; say why in the review. Keep the top N by the final score.

Never pad with weak matches: report how many passed each stage.

## Step 3: Research the product and company

Write `<staging>/product.md`:

```
# <Product>
- Product URL / company site:
- Company LinkedIn page:    (URL from the company site's footer or a web search result; never opened)
- Directory: <name>, <directory page url>
- HQ country / city:        (source)
- Founded, team size, funding stage and investors:   (source; "unknown" if not public)
- Pricing and plans:
- Stack signals:            (job posts, GitHub, blog; or "unknown")

## What it does
Who it's for, the problem it solves, main features, how a user gets value.

## Recent activity
Launches, changelog entries, funding news, founder posts, from the last 6 months.

## Match with the user
The Step 2 row(s), and the specific accomplishments (with real numbers) that sit closest to this product.

## Funding and care
- Last round: <stage, amount if public, date, investors> (source)
- Signs they care about the product: (at least two, with dates and links)

## Reply-chance score: <before>/8 before testing, <final>/9 after
One line per point earned, with its source.

## Worth praising
One or two specific, sincere things: a feature, a design choice, clear docs, a fast onboarding, a public post-mortem.
```

Sources: the product site, docs, changelog, blog, pricing page, careers page, the directory listing, founder posts, YC/Crunchbase/Wellfound profiles. Write only what a source says.

## Step 4: Test the product and find bugs

Use the product in Chrome the way a new customer would, for about **15–30 minutes per product**, with the browser's network and console views open (Claude in Chrome's network requests and console messages).

**What to do:**
- Walk the main flows a real user would: landing page, pricing, docs, signup (the user types any password), onboarding, the core feature on the free tier, settings, and mobile width.
- Watch **the requests the product itself makes** during those flows: failed calls (4xx/5xx), error bodies shown to users, very slow endpoints (note the time), duplicate or looping calls, CORS or mixed-content errors, requests that fail silently while the UI says "saved".
- Watch the console for errors that break something.
- Check public API docs examples the way a developer would, if the product has a public API with a free key: does the documented example work as written?
- Other real bugs: broken links that block a flow, wrong prices or plan limits, form validation that lets bad input through or blocks good input, layout broken so a user can't finish a task at common widths, emails from the product with broken links.

**A bug means something that doesn't work.** A user can't sign up, pay, save, invite, export, get the right data, or finish what they came for; or data is wrong, lost or shown to the wrong place; or an API call fails or returns the wrong thing. **Typos, grammar, wording, colors, spacing, alignment and other small cosmetic issues are not bugs** and never go in `bugs.md` or an email. Pointing them out makes them look like a proofreader, not an engineer. Look first where it hurts the business most: **signup and onboarding, checkout and billing, the core feature, and the public API**. Those are the bugs founders answer.

**What never to do:**
- Never edit, replay with changes, or hand-craft requests to endpoints, never change IDs to reach other accounts' data, never send injection or fuzzing payloads, never run scanners, crawlers or load, never bypass paywalls, limits or CAPTCHAs.
- Never invite, message or affect real users, never spam their forms, and never enter someone else's data. Use the user's own details only.
- Never pay or enter card details.

**Reproduce every bug twice**, some minutes apart. If it doesn't reproduce, it isn't a bug for the email. Then write it to `<staging>/bugs.md`:

```
## <short title>
- Where: <url / screen>
- Severity: minor | annoying | blocks a flow
- Steps: 1. ... 2. ... 3. ...
- Expected / actual:
- API: <METHOD /path> -> <status>, <time ms>, response snippet (tokens and personal data redacted)
- Console: <error line>
- Reproduced: <date time>, <date time>
- Screenshot: screenshots/<file>.png (optional)
```

Also note **observations that aren't bugs** (a slow step, a confusing flow) in a separate section. They may be used only if they're concrete and measured, and labelled as suggestions, never as bugs.

**Security issues** (another user's data visible, secret keys in the page source, an endpoint that works without login when it clearly shouldn't): stop testing that area right away, don't dig further or try to confirm it by changing anything. Don't write it in `bugs.md`, in the repo or in the email body. Tell the user in chat only. If they want to report it, use the company's `security.txt` or disclosure policy, and the email may say only that they noticed "a security issue I'd rather share privately".

**No reproduced functional bug and no concrete, measured observation → skip the product.** Paragraph 2 must be real. A product with only cosmetic issues is skipped too.

Log out and close the product's tabs when done.

## Step 5: Find the CEO, CTO and technical co-founder

### 5a. Find them without LinkedIn

1. Look on the company's **about/team page, imprint** (EU companies list their directors), YC/Crunchbase/Wellfound profiles, launch posts (the maker on Product Hunt, the poster on Show HN), press releases, founder blogs and podcasts. Then a web search: `"<company>" CTO`, `"<company>" co-founder`, `"<name>" linkedin`.
2. Take each person's **LinkedIn profile URL** from those pages or from the web search result itself (the link, not a LinkedIn page visit). Also note their location, background and a few lines of how they write (blog, posts, talks) from these sources.
3. **Email address, from public sources only:** the company site, their personal site, a talk or podcast page, a public GitHub profile, a press release, the YC page. If one teammate's address is public (e.g. `anna@company.com`), the same pattern for the others is `medium` confidence. Never use paid email finders, scraping tools or SMTP checks.
4. Mark each email `confirmed` (published), `medium` (pattern confirmed from another published address) or `guess` (pattern not confirmed). **`guess` addresses are shown to the user in the review and drafted only if they okay them.** No email at all → no draft for that person, but they still get the LinkedIn request (Step 6 note); mention it in the report.
5. `$L person <email> <linkedin_url>` must print `new`.
6. The **same person holding two titles** (CEO and CTO) counts as one person. The person must be based in a target country; skip anyone located in one of the user's blocked countries.

### 5b. Check before any LinkedIn visit

For each person with a LinkedIn URL, run `$P check <url> "<name>" "<company>"` (it covers all four LinkedIn tracks, all dates).
- **Already on file** (any track, any status): **don't open the profile.** Use what the ledger and the earlier notes already hold. No new connection row (Step 8b). The email still goes ahead unless they were rejected on LinkedIn; mention it in the review. If they're `accepted` already, the report suggests a short LinkedIn message for the user to send after the email.
- **New:** goes to 5c.

### 5c. One direct visit per person (only now)

Only after the product is final (Steps 2 and 4 passed), open each new person's profile **directly by URL, once**, with the HUMAN-BROWSING reading time (15–40 s). In that single visit, read and save everything needed:
- current title and company (confirm they're still there; if not, drop them)
- location (country)
- headline and About, current and past roles
- their recent posts or comments, if shown on the profile
- whether **Connect** is available (directly or under **More**), or LinkedIn wants their email address
- how they write (first names, casual or formal), for Step 6's culture choice

Write it all into `people.md` right away and close the tab. **Never open that profile again**, not for the email, the note or the review. If something was missed, work without it.

No LinkedIn URL found in 5a → no LinkedIn request, email only; say so in `people.md`.

Write `<staging>/people.md`: per person, name, title, LinkedIn URL (and `visited <date>` or `not visited: already on file`), email with its source and confidence, location, background, recent posts, how they write, the chosen greeting and sign-off (Step 6), the **hook** for their email, and the LinkedIn connection note (Step 8b).

## Step 6: Write the emails

**One email per company first.** Several emails about the same bug on the same day to a small team look like a campaign, and they forward them to each other. So:
- **Pick the first person** by who owns the bug's area: an API, data or technical bug → CTO or technical co-founder; a signup, pricing, checkout or customer-facing bug → CEO. Tie → the one who replies in public more, then the CTO. Write why in `people.md`.
- **Write a held email for each teammate** too, for their role, saved in `emails/` and recorded with status `held` (Step 8). It's drafted only if the first thread goes quiet (Step 0a). Held emails get no Gmail draft now.
- People at the same company may still compare emails later, so no two may share a subject, an opening sentence or the same paragraph 3.
- Teammates still get their LinkedIn request now (see the connection note below), without saying anyone was emailed.

**Angle by role:**
- **CTO / technical co-founder:** engineering. In paragraph 2, give the technical detail: the endpoint, the status code, the steps. In paragraph 3, the systems they built for the same kind of problem.
- **CEO / non-technical founder:** product and customers. In paragraph 2, describe what the user sees and why it costs them (a failed signup, a wrong price), in plain words, without API detail. In paragraph 3, the outcomes their work delivered, with numbers.

Write `<staging>/emails/<first-last>-<role>.md`:

```
Subject: <subject>
To: <email>

<greeting>

<paragraph 1>

<paragraph 2>

<paragraph 3>

<paragraph 4>

<closing>,
[Gmail default signature]
```

**Greeting, tone and sign-off follow the recipient's culture.** Decide per person, in this order:
1. **How they write themselves** (from 5a/5c: their posts, blog, talks, how they sign public emails or newsletters, whether the team page uses first names). This always wins. A German founder who signs "Cheers, Max" gets "Hi Max," and "Best,".
2. **The company's tone** (site copy, docs, careers page): a casual startup vs a formal B2B or enterprise company.
3. **Their country**, as the default:

| Country / region | Greeting | Sign-off | Tone |
|---|---|---|---|
| USA, Canada | `Hi <First>,` | `Best,` | friendly, direct |
| UK, Ireland | `Hi <First>,` | `Best wishes,` or `Kind regards,` | polite, understated, soften the bugs a little |
| Australia | `Hi <First>,` | `Cheers,` (if their own tone is casual) or `Best,` | relaxed, plain |
| Netherlands, Nordics, Estonia, Israel | `Hi <First>,` | `Best,` | very direct and short, no flattery padding |
| Germany, Austria, Switzerland | startup: `Hi <First>,` / formal company: `Dear <First> <Last>,` | `Best regards,` | precise, factual, exact bug steps |
| France, Italy, Spain, Portugal, Belgium | `Hi <First>,` (startup) or `Dear <First>,` | `Best regards,` or `Kind regards,` | warm but polite |
| Poland, Czechia and the rest of Central/Eastern Europe | `Hi <First>,` | `Best regards,` | factual, polite |
| Singapore, Hong Kong, Taiwan | `Hi <First>,` or `Dear <First>,` | `Best regards,` | polite, clear |
| Japan, South Korea | `Dear <First> <Last>,` | `Best regards,` | most formal: respectful, modest, frame the bugs as small things the user noticed |
| UAE, Qatar | `Dear <First>,` | `Kind regards,` | courteous, respectful |

Never use Mr./Ms. or any title that assumes gender; when a formal greeting is needed, use the full name (`Dear Yuki Tanaka,`). Never "Dear Sir/Madam" or "Dear Team". The closing comes from this table or [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md) section 4, and below it is always **Gmail's default signature** (`[Gmail default signature]` in the file). Claude never types their name or links. Write the chosen greeting, sign-off and the reason (their own style, company tone or country) in `people.md`.

**Exactly 4 paragraphs, short.** A founder skims, so the useful part (the bug) comes right after a short opening, and they come after the bug:

1. **Short, real appreciation (1–2 sentences).** What the user did with the product and one specific, sincere compliment (a feature, a design choice, the docs) from `product.md`, said the way someone who used it would. No summary of what the product does; they know.
2. **The bug (the core).** One or two reproduced bugs from `bugs.md`, best one first: where it happens, how to trigger it, what goes wrong and why it matters to a user. Friendly and helpful (the user noticed it while using the product, not an audit). No blame, no "your app is broken".
3. **Who the user is, in 2–3 sentences.** From the top of their accomplishments, the work closest to this product: what they built, for whom, and the result, with real numbers from the "Headline numbers" in `proof-map.md` (e.g. "the monitoring platform 200+ teams rely on"). **Never** name languages, frameworks, databases or tools (the checker rejects them), and **never** say or hint that they need a job, is looking for work, is open to work or is exploring new opportunities.
4. **How the user could help, and an easy reason to reply.** They'd be glad to help sort out issues like these, or to be part of the team that makes the product smoother, tied to the work in paragraph 3. A soft "be part of the team" line is allowed; it's interest, not a job ask. The first email's only goal is **a reply**, so end with one short, easy question they can answer in a line, e.g. "Want me to send the exact steps and the request details?" or "Is this already on your list?" **No meeting or call offer in the first email**, no calendar link. Confident, not pushy.

**Subject:** about **the company's product and the problem only, never about the user.** Founders open emails about their own product; a line about the sender reads like a pitch. Under 60 characters, plain words, sentence case, written the way a user would write it. Never "I built", "200+ teams", "from someone who...", their name or their work. Not generic ("Collaboration", "Quick question", "Opportunity"), no "bug report", no clickbait, no all-caps, no emoji. Good shapes:
- `Dub's 14-day trial isn't applied at checkout`
- `Mumbai never shows up in the speed test`
- `Discord connect fails on the alerts page`
- `<Product> signup loops back to step one`

Each person at a company gets a different subject (the held ones too). Check it with `$A text "<subject>"`.

**Tone and rules:** written per [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md). **100–190 words** in the body (shorter is better), at most 5 sentences per paragraph, no sentence over 30 words. Warm, plain, specific, adjusted to the culture above. Greeting and closing from the culture table, then `[Gmail default signature]` (never a hand-typed name or links). No attachment. Never needy: no "I need", "any opportunity", "please consider me", "open to work", "new opportunities", "looking for a role". No "I came across", "I hope this finds you well", "reach out", "look forward to hearing from you".

`$A email <staging>/emails/<file>.md --paras 4` must print `ok`. Then reread it as the recipient would: every paragraph must be impossible to send to another company unchanged. Rewrite anything that sounds like a template.

### LinkedIn connection note (for each person visited in 5c)

**Every person gets one**, as long as their profile was opened in 5c, has **Connect** available (not "email required"), and they're based in one of the user's `outreach_countries` (the LinkedIn ledger's country list). This is the second channel next to the email. It follows the [client outreach note rules](../linkedin-client-outreach/SKILL.md) (Step 4 there):
- at most 300 characters, aim for 200–280, starts with their first name, written per [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md), no links, no job ask
- **different from the email**: one short hook from the product (what they liked, or the flow where they hit the bug), not the full bug list
- only the person emailed first may be told about the email, in a few words (e.g. "sent you a short email about the invite flow"). Held teammates and people with no email get one short line on what they liked or the flow they used instead, never the full bug, and never "I emailed your co-founder"
- the same culture rules as the email (first name for casual cultures, a more polite line for formal ones)

`$P lint "<note>"` must print `ok`. Save the note in `people.md`. People already on file (5b), without Connect, or outside that country list get no note; say why in `people.md`.

## Step 7: Review with the user, then Gmail drafts

Show one numbered list, grouped by product:
- product, company, country, directory, product URL, company LinkedIn
- why it matches (Step 2 row and their closest work), last funding round, and the reply-chance score with its points
- bugs found (short), plus any security note (chat only)
- each person: name, title, LinkedIn, email with confidence and source, and whether their email is **first** (drafted now) or **held**, with the reason for the pick
- each email in full in a code block, with its subject, greeting and sign-off, and the culture reason
- each LinkedIn connection note in its own code block with its character count (or why there's none)
- `info:` lines from `$L check` (they applied there, or already sent a LinkedIn request)

Then create the drafts for the approved **first** emails only (held ones stay in the files) (the user can approve all, some, or ask for edits; `guess` addresses only with their explicit okay):
1. Open Gmail in Chrome, **Compose**, fill **To**, **Subject** and the body exactly as in the email file (greeting, 4 paragraphs and the closing line), typed **above** the default signature Gmail inserts. Don't type the `[Gmail default signature]` line, their name or links, and don't change the signature. If no signature appears, stop and ask the user to set one. No attachment.
2. Close the compose window so Gmail saves it to **Drafts**. **Never click Send.** Check it is in Drafts with the right recipient and subject.

Spread cold email: at most **profile.json `product_outreach_daily_drafts` drafts a day** (15 in the template) in total. If a run would go over, keep the rest for the next run.

Products with no approved emails: delete their staging folder and record nothing, LinkedIn notes included.

## Step 8: Save the notes and record

For each product with at least one draft:
1. Move the staging folder to **`product-outreach/<me>/<YYYY-MM-DD>/<product-name>/`** (local date, `python .claude/skills/job-apply-shared/scripts/me.py date`; add `-2` if that folder already exists today). Keep the drafted emails and the approved held ones in `emails/`.
2. Write `outreach.md`:
   ```
   # <Product> outreach
   | Person | Role | Email | Subject | Drafted | Status | LinkedIn request | Notes |
   |---|---|---|---|---|---|---|---|
   | ... | CTO | ... | ... | 2026-10-01 | email-draft | prepared (product track) | |

   ## Next step
   e.g. when the user sends, or anything to follow up (a new release to recheck, a reply to answer).
   ```
3. Write `linkedin.md`, the LinkedIn track notes for this product (later runs' Step 0b keep the status up to date):
   ```
   # <Product> LinkedIn
   - Company LinkedIn page: <url> (never opened)

   | Person | Role | Profile URL | Visited | Country | Connect | Track row | Status | Checked |
   |---|---|---|---|---|---|---|---|---|
   | ... | CTO | ... | 2026-10-01 (once) | France | under More | product 2026-10-01 | prepared | 2026-10-01 |

   ## <Person>
   - Headline / current role:
   - Recent posts (gist, date):
   - How they write:
   - Hook used in the note:
   - Note (<N> chars):
     <exact note>
   - Why no request (if none): already on file in <track> / no Connect / country / no LinkedIn URL / weekly cap
   - After they accept: a one-line idea for a first message (the user sends it themselves)
   ```
4. Record each email:
   ```bash
   $L add '{"product":"...","company":"...","company_site":"...","company_country":"...","person":"...","role":"CEO|CTO|Technical co-founder","email":"...","email_source":"<where, confidence>","linkedin_url":"...","directory":"...","subject":"...","folder":"product-outreach/<me>/<date>/<product-name>","score":"<reply-chance score>","bug_area":"signup|onboarding|checkout|billing|core|api|other","status":"email-draft|held"}'
   ```

### 8b. Store the LinkedIn connections in the product track

Every approved connection note goes into the **product** LinkedIn track, so the status check, the 7-day reject list and the "never again" rules handle these people like any other outreach track:

1. **Weekly cap first.** Count the rows in all four tracks' send files (company, client, hiring, product) dated in the last 7 days (not counting `not-sent`). If adding this person would go over **90**, don't add them. Keep the note in `linkedin.md` and say in the report that it waits for room.
2. Add the row (the ledger refuses duplicates in any track and people outside its country list):
   ```bash
   $P add '{"name":"...","title":"...","company":"...","company_site":"...","country":"...","linkedin_url":"...","domain_match":"<client service, e.g. monitoring-alerts, payments-integration, saas-mvp>","why_target":"product outreach: <product> <-> <their closest work>; emailed about <bug in a few words>","source":"product-outreach","note":"<exact note>"}'
   ```
   `domain_match` is the service from the client skill's service map that fits the product best.
3. **Bonus:** these rows don't reduce the day's company, client or hiring numbers. They only count toward the 90-in-7-days cap, so a later `outreach` run sees less room in the week, not a smaller daily list.

Tell the user the order: **send the email first, then the connection request** with the note, the same day. If they skip a request, `$P set <url> not-sent`. The next run's Step 0b (or `outreach` Phase 1) confirms who was actually sent.

Follow-ups: one per person, only as in Step 0a, always as a draft the user sends. If someone asks not to be contacted, `$L set <email> withdrawn` and never email that company again.

## Step 9: Commit and push

```bash
git add product-outreach/<me> linkedin/<me>/send-connection/linkedin-connections-by-product-outreach linkedin/<me>/reject-connection/linkedin-connections-by-product-outreach linkedin/<me>/follow-up/linkedin-connections-by-product-outreach
git commit -m "<me>: product outreach: $(python .claude/skills/job-apply-shared/scripts/me.py stamp) — <N> products, <M> drafts, <K> connection notes (<product list>)"
git push
```

Commit only `product-outreach/<me>/` and the product track's `linkedin/<me>/send-connection/`, `linkedin/<me>/reject-connection/` and `linkedin/<me>/follow-up/` folders.

## Report

- Directories used, candidates found, how many passed each filter.
- Products drafted: product, company, country, people and roles, subjects, bugs used, folder.
- **Drafts waiting in Gmail Drafts** for the user to send (first emails, follow-ups, next-person emails), and earlier drafts still unsent (Step 0). Any replies, calls, interviews or offers.
- **Held emails** per company, waiting for the first thread to go quiet.
- **Stats** from `$L stats`: reply rate overall and by score, bug area and directory.
- **Connection requests to send after the emails:** name, profile URL and the note in a code block with its character count, saved in the product track (or why a person got none, e.g. already on file, weekly cap).
- **LinkedIn messages (Step 0c):** today's follow-up file path and each message to send, with its character count.
- **LinkedIn track (Step 0b):** newly pending, accepted, not sent, and today's reject list (names and URLs) for the user to withdraw by hand. From `$P stats`: accepted of sent and still pending, the 7-day total vs the cap of 90, and a suggested first message for anyone newly accepted.
- Skipped products, one line each with the reason (no domain match, country, stack, no funding, too big, gone quiet, reply-chance score under 3, no functional bug, no founder email, already contacted).
- Security notes (chat only, never in files).
- Site usage (searches and pages per site, LinkedIn pages used, any challenge or rate limit) per [HUMAN-BROWSING.md](../job-apply-shared/HUMAN-BROWSING.md).
