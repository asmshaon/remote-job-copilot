---
name: upwork-profile
description: Run when the user says "upwork profile" (also "set up my upwork profile", "update upwork profile", "upwork catalog", "upwork video"). Goal number one is search ranking - getting their Upwork profile (with whatever Job Success Score, reviews and earnings it already has) and catalog projects into the top results for the searches clients actually make. Audits the live profile, past jobs and reviews, researches demand, then writes every field in order of ranking impact, from their past Upwork work, accomplishments file, resume and skill set only. Fields the official Upwork MCP server can change (skills, availability and badge, employment, education, languages) Claude updates through it, each one as a draft the user confirms. Everything else (category, title, overview and summary, hourly rate, portfolio, 6 catalog offers with thumbnails, video) goes into upwork/<me>/profile/<YYYY-MM-DD>/ as numbered copy-paste files with click-by-click directions, in ranking order, so the user only copies and pastes. Text is easy, plain and human (HUMAN-WRITING.md, checked by apply.py text). Tracks rank before and after every change. Never invents work, reviews or numbers, never types a password, never sends proposals, messages or boost ads, never pays.
---

# Upwork Profile

Trigger: **`upwork profile`**. Also:
- `upwork profile refresh`: redo the audit, the demand research and the rank check, and update only what changed
- `upwork catalog`: only the Project Catalog files (Step 9)
- `upwork video`: only the video scripts (Step 10)
- `upwork rank`: only the rank check (Step 1c and Step 13)

**Whose run.** Several people share this repo. `<me>` is the person running it: the slug in `.me` at the repo root (`python .claude/skills/job-apply-shared/scripts/me.py`). "The user" means that person. Read only `skillsets-and-contributions/<me>/` (profile.json, proof-map.md, their files) and write only under `upwork/<me>/` (and their own `profile-answers.md`). Never read, write or reuse another person's folders. Run `me.py check` first; if it prints `NOT READY`, stop and offer the `profile-setup` skill.

## Goal: ranking first

**The first priority is search ranking.** Every choice in this skill is judged by one question: does it move their profile or their catalog offers up in the searches clients really make? Looking good comes second, and only because a click is worth nothing if the client doesn't message.

Start from where the user really is (Step 0 and the Upwork section of their `profile-answers.md`): a new profile, or one with a Job Success Score, client reviews and earnings. Upwork ranks by:
1. **Relevance:** category and specialties, then title, skills and the overview, matched to what the client typed.
2. **Trust:** Job Success Score, reviews, earnings, badges (Top Rated).
3. **Activity:** availability badge, response time, recent jobs and proposals.

If their trust is already good, the skill works on relevance in this order of impact, then on growing trust (Top Rated, Step 12), then on activity (weekly habits, Step 13). If the profile is new, the first catalog Starter tiers and small jobs that bring reviews matter more.

Be honest with them: no setting promises the top 3 for a very broad search (e.g. "Node.js developer"). Specific searches with steady demand in their strongest area (e.g. "Stripe subscription billing Node.js") are where they can rank first. Those wins bring the reviews and earnings that lift the broad searches.

## Who updates what

| Field | Ranking impact | Who updates it |
|---|---|---|
| Category and specialties | very high | **The user pastes** (file 01) |
| Title | very high | **The user pastes** (file 02) |
| Skills (20 hard + 2 soft) | very high | **Claude, through the Upwork MCP server** (Step 6) |
| Overview and its first 2 lines (the search summary) | high | **The user pastes** (file 03) |
| Catalog offers (6) with thumbnails | high, in catalog search | **The user pastes and uploads** (files 05, catalogs/) |
| Hourly rate | medium (clients filter by rate) | **The user pastes** (file 06) |
| Availability and availability badge | medium (activity) | **Claude, through the MCP server** |
| Portfolio projects with thumbnails | medium (conversion, trust) | **The user pastes and uploads** (file 07, portfolio/) |
| Employment history, education, languages and English level | medium (filters, completeness) | **Claude, through the MCP server** |
| Intro video and portfolio videos | medium (conversion) | **The user records and uploads** (file 08) |

The MCP server's own page lists what it can change for a freelancer: availability, employment, languages, education, skills, and the availability badge. At the start of every run, list the server's tools and compare. If a tool for another field exists (title, overview, rate, portfolio, catalog), move that field to "Claude" for this run and say so in the report. If a listed tool is missing, move that field to a paste file.

## Hard rules

- **Protect the account.** Their account (its Job Success Score and real reviews) matters more than any trick. Upwork's terms forbid bots and scraping.
  - **Upwork MCP server first** (`upwork`, the user's own login; each person connects their own): reading their profile, jobs, dashboard and stats, and the profile changes it supports. It's Upwork's own approved way in.
  - **Public pages next:** logged-out web searches like `site:upwork.com/freelancers "<keyword>"`, public profiles and public catalog pages.
  - **Logged-in Upwork pages in Chrome: at most 15 a day**, read-only, only when the MCP server can't give the data. Stop at the first CAPTCHA or warning.
  - **Claude never edits Upwork through the browser.** Edits go through the MCP server only.
- **Every MCP write is confirmed.** The MCP server makes each change a draft. Claude shows the user the exact new value next to the old one, waits for their "yes" in chat, then confirms the draft. One field at a time. Write the old value in `audit.md` first, so any change can be undone.
- **Never through the MCP server:** proposals, messages, accepting or declining offers or invitations, milestones, profile boost ads (they cost money), or anything that spends Connects.
- **Truth only.** Every fact, number, project, skill and review comes from their Upwork history and reviews, their accomplishments file (`skillsets-and-contributions/<me>/contributions/`), resume (`skillsets-and-contributions/<me>/resume/<resume_file>`) and skill set (`skillsets-and-contributions/<me>/skills/my-skill-set.md`). Never invent a project, client, review, result or certification. Quote a client review only word for word, and only one that's public on their profile.
- **Human writing.** Every word a client reads follows [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md): easy words, short sentences (never over 30 words), real numbers, nothing that sounds like an LLM wrote it. `python .claude/skills/job-apply-shared/scripts/apply.py text "<text>"` must print `ok` for every title, overview paragraph, portfolio text, catalog text and video script.
- **Keywords, not stuffing.** The main keyword sits where it counts (category, title, first line, skills, catalog title and tags) and 2–3 times in the overview, always inside a real sentence.
- **Don't repeat what Upwork shows.** No "100% JSS", stars, earnings or badges in the text. Upwork already shows them next to their name.
- **Never type a password.** Login page, CAPTCHA or identity check: stop and hand control back.
- **Privacy.** `upwork/` is committed to GitHub. Never save their address, phone, ID, tax or payment details, exact earnings, or clients' names unless public on their profile.
- **No client secrets** in images or videos: no private admin screens, client data, keys or code.

## Sources of truth (read at the start of every run)

1. **Their live Upwork profile and work history** (Step 0), through the MCP server.
2. Accomplishments PDF, resume, skill set.
3. `skillsets-and-contributions/<me>/profile-answers.md`, section **Upwork**: hourly rate, minimum fixed price, hours per week, English level. `ASK` items are asked once, then saved there.
4. The last run's folder in `upwork/<me>/profile/` and `upwork/<me>/ranking.md`.

## Helpers

```bash
A="python .claude/skills/job-apply-shared/scripts/apply.py"
$A text "<any text>"            # must print ok

T="python .claude/skills/upwork-profile/scripts/thumbnail.py"
$T --headline "<3-6 words>" --sub "<one line>" --proof "<one real number>" --tags "A,B,C" \
   --theme blue|green|purple|dark|orange|teal [--photo] [--size 1000x750] --out <path>.png
```

## Output folder (what the user opens)

Everything goes into **`upwork/<me>/profile/<YYYY-MM-DD>/`** (the user's local date). The numbered files are in **ranking order**, so if the user only has time for the first three, they still get most of the ranking gain.

```
upwork/
  ranking.md                         rank of each search over time (Steps 1c and 13)
  profile/2026-10-02/
    00-START-HERE.md                 the checklist: what Claude already updated, what the user pastes, in order
    01-category.md                   category and specialties to select
    02-title.md                      the title to paste
    03-overview.md                   the overview to paste (its first 2 lines are the search summary)
    05-catalog.md                    how to create the 6 catalog offers, 2 first
    06-hourly-rate.md                the rate and why
    07-portfolio.md                  how to add each portfolio project
    08-video.md                      intro video and portfolio video scripts, and where to upload
    09-weekly-habits.md              what to do every week to keep ranking (activity)
    catalogs/<n>-<slug>/catalog.md   each offer, field by field, ready to paste
    catalogs/<n>-<slug>/thumbnail.png
    portfolio/<n>-<slug>.md          each project, field by field, ready to paste
    portfolio/<n>-<slug>.png
    research/audit.md                the live profile before changes (the undo copy), past jobs, reviews
    research/keywords.md             demand research
    research/mcp-changes.md          every field Claude changed through the MCP server: old value, new value, time
```

### How every paste file is written

The user only copies and pastes, so each file has the same shape:

````
# 02 Title  (ranking impact: very high)

**Where:** upwork.com → your photo (top right) → **View profile** → the **pencil** next to your title.
**Do:**
1. Delete the old title.
2. Copy the text in the box below and paste it.
3. Click **Save**.
**Check:** your profile shows the new title. Then tell Claude "title done".

```
<the title, e.g. Node.js Backend Developer | Stripe Billing, API Integration, SaaS>
```

Characters: 65 of 70.
Why this helps ranking: <one line, e.g. "the most searched client words for their strongest work come first">.
If the button moved: on Upwork, open Help and search "edit profile title".
````

Rules for every paste file:
- **One code block per field**, holding exactly what to paste and nothing else (no quotes around it, no notes inside it).
- **Where** (the click path), **Do** (numbered steps), **Check** (how they see it worked), the character count against Upwork's limit, and a one-line **why** for ranking.
- Images: the full file path to upload, and which box it goes in.
- Plain words. Upwork's layout changes, so the click paths are the best known path plus a fallback ("search Upwork Help for ...").
- `00-START-HERE.md` lists every file in order with a checkbox, marks what Claude already changed through the MCP server, and says which ones matter most for ranking.

## Step 0: Audit the live profile (through the MCP server)

1. List the MCP server's tools and update the "Who updates what" split for this run.
2. Read their current title, overview, skills, category and specialties, rate, specialized profiles, portfolio, catalog offers, video, availability, employment, education, languages.
3. Read **every past Upwork job**: title, type of work, what they delivered, the client's review text and stars, the client's country.
4. Write `research/audit.md`: the "before" copy (the undo record), plus:
   - **what Upwork already knows them for** (categories and skills of past jobs; build on them)
   - **words clients used in reviews** (real keywords and real proof)
   - **the best past job for the portfolio**
   Store review stars and text as they are. Never round a 4-star review up.

## Step 1: Research demand and check the starting rank

### 1a. Client keywords

Through the MCP server's job search (or public job pages if it's not connected), last 30 days, for each of their services. Start from their `stack.terms`, `domains`, `target_roles` and the services in `proof-map.md` sections 2 and 3, and add more from their past jobs. For example, for a Node.js backend engineer: `Node.js`, `NestJS`, `REST API`, `API integration`, `Stripe subscription`, `payment gateway integration`, `webhook`, `SaaS MVP`, `backend developer`, `PostgreSQL`, `Docker deployment`, `bug fix Node.js`.
Note the job counts and the words that repeat in job titles. Read the 15–20 best-fitting posts and copy clients' exact words for the problem.

### 1b. Competition

From public pages only: `site:upwork.com/freelancers "<keyword>"` and public catalog search. Read the titles, skills, catalog titles and tier prices of the top 10. Note what they all use and what nobody covers well.

### 1c. Starting rank

Before changing anything, search each target keyword the way a client would (logged out, public search, or a web search) and note their profile's and catalog's position, or "not in top 50". Add the rows to `upwork/<me>/ranking.md`: `date | search | profile position | catalog position | note: before changes`. Without this "before" number, nobody can tell whether the changes worked.

### 1d. Pick the keywords

Write `research/keywords.md`:
```
| Keyword (client words) | Jobs, last 30 days | Competition | Their proof (Upwork job or PDF) | Rank now | Use in |
```
- **1 primary keyword:** the most demand where their proof is strongest (an Upwork job in the same area counts most).
- **3–5 secondary keywords.**
- **Long-tail searches to win first:** steady demand, weak competition.

## Step 2: Category and specialties → `01-category.md`

The category decides which searches they show up in at all, so it's the first file. Upwork's form has two levels: a **category** (likely **Web, Mobile & Software Dev**) and, under it, a list of **subcategories** (Web Development, Ecommerce Development, Scripts & Utilities...). That subcategory list is the specialty choice; there is no separate specialties step. Pick **Web Development** first (where Back-End and Full-Stack jobs sit), then the subcategories their past jobs and keywords point to, in order. Back-End and Full-Stack themselves come through the title, skills and overview. Give the exact names to click in Upwork's list.

## Step 3: Title → `02-title.md`

- **70 characters at most.** Primary keyword first, then 2–3 secondary ones, in client words.
- Plain shape: `<Primary keyword> | <secondary> | <secondary>` or `<Primary role> for <outcome>`.
- No "expert", "guru", "rockstar", "ninja", no all-caps, no emojis, no "Top Rated".

Put the **recommended title in the paste box**, and 2 other options under it (each with its count and keywords), in case they prefer one. Examples of the shape (for a Node.js backend engineer):
- `Node.js Backend Developer | Stripe Billing, API Integration, SaaS` (65)
- `Node.js & NestJS Developer | Stripe, Payment Gateway, REST API` (62)
- `Backend Developer for SaaS | Node.js, Stripe, Webhooks, AWS` (59)

## Step 4: Overview → `03-overview.md`

Upwork shows only the **first 2 lines (about 200 characters)** in search. That's the summary (Step 5), and it comes first in the paste box.

1,200–2,000 characters (limit 5,000):
1. **Opening, 2 lines** (Step 5).
2. **What they can do for you,** 4–6 short lines, a service in client words with one real proof each:
   e.g. `Stripe subscriptions: plans, upgrades, webhooks and failed-payment recovery, built for a monitoring platform 200+ teams use.`
3. **Recent work,** 2–3 lines: a result from an Upwork job first (no client name unless public), then systems from their career with numbers (the "Headline numbers" in `proof-map.md`).
4. **How they work,** 2–3 lines: clear updates, a written plan before code, tests, hours that overlap with the client (their `timezone_label`, and remote teams they've worked with, from the resume).
5. **A light close:** what to send them to start.

The primary keyword 2–3 times, each secondary keyword at least once, inside real sentences. Plain text with `-` or `•` lines (Upwork doesn't render markdown). One paste box with the whole overview, its character count, and a line saying the first 2 lines are what shows in search.

## Step 5: The summary (the first 2 lines)

The summary a client sees in search is the **title plus the first 2 lines of the overview**. If Upwork's form has a separate summary or tagline field, `03-overview.md` gets a second paste box for it with the same text.

The first 2 lines hold the primary keyword and one secondary keyword in the first sentence, say the outcome and one real number, and stay under about 200 characters:
e.g. `I build Node.js backends for SaaS teams: Stripe subscriptions, API integrations and dashboards. My code runs a monitoring platform that 200+ teams use.`

Write 3 versions, use the best in the overview, list the other 2 under it.

## Step 6: Skills (Claude, through the MCP server)

Up to **20 hard skills plus 2 soft skills** (Upwork's limit since 2026-05-28), only from Upwork's own skill list, only skills in their skill set or shown in their work. **Most demanded first** (Step 1 counts), with their past jobs' skills near the top. Mix their core stack (`stack.terms`), service skills clients search for (e.g. `API Integration`, `API Development`, `Stripe`, `Payment Gateway Integration`, `Back-End Development`, `SaaS Development`), then data and deploy.

Show the user the old list and the new list side by side with each skill's job count. After their "yes", update through the MCP server, confirm the draft, read the profile back to check, and log it in `research/mcp-changes.md`. If the server can't change skills this run, write `06b-skills.md` as a paste file instead.

## Step 7: Other fields

**Through the MCP server (Claude), one at a time, each after the user's "yes":**
- **Availability and the availability badge:** on, with their real hours per week (`profile-answers.md`).
- **Employment history:** matching their resume exactly, one plain line per role about what they built.
- **Education:** matching their resume.
- **Languages and English level:** their real level (`ASK` once).
Old and new values go into `research/mcp-changes.md`.

**Paste file `06-hourly-rate.md` (the user):** the rate from `profile-answers.md`, with the rates of the top 10 profiles for their primary keyword next to it, and why. Too far above the market hides them from clients who filter by rate. Too low looks cheap. The final number is their call.

## Step 8: Portfolio → `07-portfolio.md` and `portfolio/`

Order by ranking value:
1. **Their Upwork jobs first.** Each finished job that fits their main keywords: what the client needed, what they built, the result. If the review is public, its best line can be quoted word for word.
2. **Then their career systems,** in the order of demand from Step 1:

Take the rows of section 3 of `skillsets-and-contributions/<me>/proof-map.md` (project, what it shows, keywords), in the order of demand from Step 1. Example rows (one engineer's map):

| Project (from the accomplishments) | Shows | Keywords |
|---|---|---|
| a monitoring product | 1,200+ servers every minute, dashboards, time-series data | monitoring, dashboards, SaaS |
| subscription billing | Stripe plans, webhooks, upgrades, dunning, reconciliation | Stripe, subscription billing |
| a recruiting platform | Boolean search over 50,000+ resumes, Gmail sync, data migration | ATS, search, data migration |

6–8 projects. Each `portfolio/<n>-<slug>.md` has one paste box per field (title under 70 characters with the keyword first, role, skills up to 5, description of 400–600 characters: the problem, what they built, the result with a real number), the thumbnail path, and the video from Step 10 if there is one. `07-portfolio.md` gives the click path once ("View profile → Portfolio → **+**"), then the projects in order.

Thumbnails: a real screenshot only if it's public and shows no client data. Otherwise the script, a different theme per project. Open each image and check it.

### 8b. Specialized profiles: removed by Upwork

Upwork removed specialized profiles on 2026-05-28. Don't write a file for them. The main profile now shows each client its most relevant parts on its own, and the general profile allows **20 hard skills plus 2 soft skills**. Put niche keywords into the title, the overview, the skills and the catalog offers (each offer ranks on its own in catalog search, which is the closest thing to a specialized profile now). If Upwork brings them back, check its Help page first.

## Step 9: Project Catalog → `05-catalog.md` and `catalogs/`

Catalog search ranks offers with sales and reviews higher, so six new offers compete with each other for the first orders. Write all 6, but **mark 2 to publish first**: the ones with the most demand where they already have an Upwork review in the same area. They link those 2 in proposals and messages to get their first orders. The other 4 follow once the first 2 have a sale, or right away if they prefer.

### 9a. Pick the 6

The 6 services with the most demand **and** strong proof, from `proof-map.md` sections 2 and 3. Example picks for a Node.js backend engineer, to confirm with the data:

| # | Offer | Their proof |
|---|---|---|
| 1 | Stripe subscription billing setup for your SaaS | their billing work: webhooks, dunning |
| 2 | Payment gateway integration (PayPal, Stripe, Adyen) | gateways they integrated |
| 3 | Third-party API integration and data sync | ad APIs, Trustpilot, Gmail, Zoom, cron sync |
| 4 | Node.js / NestJS REST API backend for your app | the backends they built |
| 5 | Alerts and notifications: Slack, Telegram, WhatsApp, email | their alert delivery work |
| 6 | Docker, CI/CD and AWS deployment for a Node.js app | GitHub Actions, Nginx, S3 + CloudFront, Jenkins |

Also possible if the data says so: NetSuite or ERP sync with a web store, Node.js API bug fixing and speed-up, multi-tenant SaaS setup.

### 9b. Each offer: `catalogs/<n>-<slug>/catalog.md`

One paste box per field, in the order Upwork's form asks for them:
- **Title:** Upwork adds its own fixed start (currently "You will get"). The box holds the rest: keyword first, the result, under the page's limit, e.g. `Stripe subscription billing set up in your Node.js SaaS`.
- **Category and project attributes:** the catalog uses its own list, not the profile's. Upwork suggests categories from the title, for example **Development & IT → Web Programming → Web Application Programming** (the usual pick for app backend work), and never a website or WordPress one for backend offers. Then the optional attributes clients filter by: programming languages (JavaScript, TypeScript; Node.js counts as JavaScript) and coding expertise (only what the offer really does, e.g. Security for payments).
- **Search tags: exactly 5** (Upwork's limit), the most searched keywords for this offer from `keywords.md`. Don't spend a tag on a word already in the offer's title (Upwork matches title words anyway); use tags for the other words clients search.
- **Pricing tiers** (Starter / Standard / Advanced), laid out exactly like Upwork's **Create pricing tiers** form, one block per row: **Custom Title** (30 characters at most per tier, plain, says what the tier delivers), **Custom Description** (80 characters at most per tier, a different text from the title), Delivery Days, Number of Revisions, Number of Pages (empty for backend work), the Service Tier Options (Design Customization, Content Upload, Responsive Design: off for backend work; Source Code: on), Project price, and add-ons: Fast Delivery (about 60% of the days, about +35% of the tier price, only if they can keep it) and Additional Revision (about one hour at their rate). Never Additional Page, Design Customization, Content Upload or Responsive Design for backend offers. Prices from their minimum fixed price (`profile-answers.md`) and the top offers' prices (shown next to their). The Starter tier of the 2 first offers is small and quick to deliver, to bring orders and reviews. Check every title and description length before saving.
- **Description:** 3 short paragraphs (what the client gets, how it works, proof from their work).
- **Requirements** (Upwork's "Requirements and steps" page): 2–3 separate requirements, each 10–250 characters, written as a plain request to the client, each marked whether "Client needs to answer before I can start working" is on (only what blocks the start). Never ask for live keys or passwords in chat; test or sandbox keys only.
- **Steps:** 5 steps from plan to handover, each with a **step title** (3–75 characters) and a **description** (up to 250 characters).
- **FAQ:** 3–4 real questions from job posts, each with its answer in its own box.
- **Gallery:** the thumbnail path (upload as the first image), and the video if there is one.
- **Sample Documents:** up to 2 PDFs under 2 MB each (clients see the first 3 pages): a 1-page case study of their closest real work (facts from the PDF only, no client data or code), and a 1 to 2 page example of the written plan a client gets, clearly marked "example". Built as HTML and printed to PDF with headless Chrome; every line passes `$A text`.

`05-catalog.md` gives the click path ("your photo → **Your projects** (Project Catalog) → **Create a project**"), the order (the 2 first offers at the top), and **Save as draft** for the other 4 until they decide.

### 9c. Thumbnails

The thumbnail decides the click in catalog search:
- The headline repeats the catalog's main keyword in 3–6 words, readable on a phone.
- One result line, one proof line with a real number, 2–3 tool chips.
- Their photo in the corner (`--photo`), a different theme color for each of the 6.
- Size: what the upload box asks for (pass it with `--size`).

```bash
$T --headline "Stripe subscription billing" --sub "Set up in your Node.js SaaS, with webhooks" \
   --proof "Built for a platform 200+ teams use" --tags "Node.js,Stripe,Webhooks" \
   --theme blue --photo --out upwork/<me>/profile/<today>/catalogs/1-stripe-billing/thumbnail.png
```
Open every thumbnail and check it before saving.

## Step 10: Video → `08-video.md`

The user records the videos. The file holds what to say, what to show, and where to upload.

**Intro video (profile, 60–90 seconds):** a script with times:
1. 0–10 s: name, what they build, for whom, with the primary keyword (e.g. "I'm Jane. I build Node.js backends for SaaS teams, mostly payments and API integrations.").
2. 10–40 s: one real result with a number, then one from an Upwork job.
3. 40–70 s: how they work.
4. 70–90 s: what to send them to start.
Tips: look at the camera, good light, quiet room. Upload: View profile → **Add video introduction** (Upwork asks for a link, usually YouTube, unlisted is fine).

**Portfolio and catalog videos (1–3 minutes):** a shot list per video of a screen recording of something they built and may show. Never client data, keys, emails or private admin screens (use test data or blur). Each video's upload place is named (which portfolio project or catalog offer).

## Step 11: Review with the user

Show one review in chat, in ranking order:
1. What the audit found and the starting rank.
2. Keywords: primary, secondary, long-tail searches to win first.
3. Category, title, summary and overview (code blocks with character counts).
4. **MCP changes Claude will make:** skills, availability, employment, education, languages, each with old and new values. Ask for a "yes" to each.
5. Catalog offers (2 first marked, tiers with market prices), rate, portfolio, video scripts.
6. Anything marked `ASK`.

## Step 12: Apply

1. **Claude, through the MCP server:** each approved field, one at a time, confirming each draft after their "yes", then reading it back to check. Log every change in `research/mcp-changes.md`.
2. **Paste files:** save everything approved into `upwork/<me>/profile/<today>/`, write `00-START-HERE.md`, and tell the user to open it. They work down the list and says "title done", "overview done", and so on. Claude ticks the box in `00-START-HERE.md` after reading the field back through the MCP server (or their say-so, if it can't be read).
3. **Top Rated:** check Upwork's current requirements (they change) on its help pages, and compare with their status from the MCP server: Job Success Score, earnings in the last 12 months, account age. Write the gap in plain terms in `00-START-HERE.md` ("about $400 more earned in the last 12 months"), and which catalog Starter tiers or small jobs can close it. Save only the gap, never their exact earnings.

## Step 13: Track the rank

Ranking is the first priority, so it's checked, not assumed:
- **3–5 days after the changes go live**, then every 2 weeks (`upwork rank`), search every target keyword logged out and add a row to `upwork/<me>/ranking.md`: `date | search | profile position | catalog position | what changed since last check`.
- Upwork's results change with who's logged in, so treat positions as a trend.
- If a search doesn't move in 4 weeks, change **one thing at a time** (the title order, the first line, a catalog title or tags), write that change in the paste files for them, and check again. Changing everything at once hides what worked.

`09-weekly-habits.md` (activity also ranks):
- reply to every message and invite within 24 hours, faster when they can
- send a few well-matched proposals each week, not many weak ones
- keep the availability badge on and the hours true
- ask each happy client for a review when a job closes

## Step 14: Saved locally (nothing to push)

Everything this run made is saved in the person's own folders, which are git-ignored and stay on this machine. There is nothing to commit or push. End the report with where the files are.

## Report

- Starting rank, the primary and secondary keywords with job counts.
- **Done by Claude through the MCP server:** each field, old and new value.
- **Waiting for the user:** the path of `00-START-HERE.md` and the files in order, the 2 catalog offers to publish first.
- The Top Rated gap.
- Latest rank rows.
- Logged-in browser pages used (15 or fewer) and MCP calls made.
