# Browsing like a person

Every skill and agent that reads LinkedIn, X/Twitter, Wellfound, Work at a Startup, job boards or company sites follows this file. It covers the job-apply skills and agents and the outreach skills and agents.

Why: Claude uses the user's **own logged-in accounts**. If a site decides the account is automated, it can restrict or ban **their** account. That costs far more than a slower run. So the goal is to use each site the way one careful person would, with low volume and a calm pace. When a site pushes back, stop.

## Hard limits (never cross)

- **Stop on any challenge.** On a login page, CAPTCHA, "unusual activity", "are you a robot", a phone or email verification, a rate-limit message ("Something went wrong, try reloading", "You've reached the limit", HTTP 429), or an invitation or weekly-limit warning, **stop using that site for this run right away**. Report it in `blocked`, or tell the user. Don't retry, reload in a loop, or try another route into the same site. The user decides when to continue, and at the earliest that's after they have cleared it themselves.
- **No tricks to hide automation.** Never spoof the user agent or browser fingerprint, use proxies or VPN switching, solve or route around CAPTCHAs, use a second account, or call a site's private or internal APIs. Work only through normal pages in the user's normal Chrome, or through public APIs meant for scripts. If a site can only be used with such tricks, skip it.
- **Read only.** No likes, follows, connects, replies or messages (the skills already forbid these). The only clicks are search, filters, scroll, "see more", opening a result, and paging.

## Pace in the browser

- **Wait between actions**, with a different wait each time (never a fixed interval):
  - after opening a page: read it for real, **5–15 seconds** for a list page and **15–40 seconds** for a job post, profile or long thread
  - between searches: **20–60 seconds**
  - after every 10–15 pages: a longer break of **2–5 minutes**, or switch to other work (writing notes, company research on the company's own site)
- **Scroll like a person.** Scroll down in steps and let the content load. Don't jump straight to the bottom or read hidden page data in bulk.
- **Move through the site like a person.** Get to posts from search results or the feed by clicking, instead of typing dozens of direct URLs one after another. Use the site's own filters rather than rewriting URL parameters over and over.
- **Few tabs.** At most **3 tabs per site** open at once. Close each one when you're done with it.
- **No repeats.** Don't open the same post or profile twice in a run. Keep what you read in the staging notes instead of going back.
- **Mix it up.** Vary the order of queries and the wording between runs. Don't always use the same query list in the same order.

## Budget per site per run

These are ceilings, not targets. Stop early once you have enough candidates.

| Site | Searches | Pages opened (posts, jobs, profiles) |
|---|---|---|
| LinkedIn (all LinkedIn work in the run, jobs + posts + outreach together) | 30 | 120 |
| X / Twitter | 12 | 60 |
| Wellfound | 10 | 60 |
| Work at a Startup / YC jobs | 10 | 60 |
| Upwork, logged in (only to read their own profile and job history; use the Upwork MCP server and public pages first) | 0 | 15 |
| Any other site with a login | 10 | 50 |

Sites without a login (company careers pages, ATS pages like Greenhouse, Lever or Ashby, HN in the browser) still get the waits above. They don't have a budget.

If a run would go over a budget, stop at the limit, apply to what you have, and say in the report that the budget was reached. The rest waits for the next run. Don't run the same source twice on the same day unless the user asks.

## One person at a time per site

- **Never have two agents on the same site at the same time.** LinkedIn Jobs, LinkedIn posts and the LinkedIn outreach tracks all count as LinkedIn, so they run one after another and never side by side. The orchestrators (job-apply, outreach) schedule them that way.
- Agents on **different** sites may run at the same time. A person can have LinkedIn open in one tab and a careers page in another.
- The LinkedIn budget is shared across the whole day's LinkedIn work. If `outreach` already ran today, the job-apply LinkedIn sources get what is left. Each run reports its usage (searches and pages per site) so the next run can see it.

## Public APIs and feeds (HN Algolia, Himalayas, Remotive, RemoteOK, Jobicy, WWR RSS)

These are meant for scripts, so no pretending. Be polite:
- Use `fetch_jobs.py`. It waits 1.5–3 s between requests, respects `Retry-After` on HTTP 429, and caches each response for the day, so running it again doesn't fetch again.
- Keep the script's honest user agent.
- Fetch each source **once per run**, then work from the saved JSON.

## Report

Every run that used a browser site ends its report with **site usage**: searches and pages per site, and any challenge or rate limit seen (with the time). Agents put the same thing in their JSON as `"usage": {"<site>": {"searches": n, "pages": n}}`.
