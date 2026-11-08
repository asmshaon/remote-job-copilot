---
name: custom-resume
description: Build a one-page resume for the person in `.me` tailored to one job post, in their chosen resume style (profile.json resume_style - classic keeps their own resume layout, modern builds a clean one-page summary, experience and skills page), from their own files in skillsets-and-contributions/<me>/. Reads the job post first, then their career accomplishments, skill set, resume and resume-base.json. Header, contact, role/company/location/date lines, projects, additional experience, education and skills categories stay fixed; only the highlight bullets under each job, the featured project descriptions, and the items inside the fixed skills categories change to match the job description. Text must read human-written (no AI-sounding words) and be ATS friendly. Saves the PDF, the job post and a match report in apply/<me>/<YYYY-MM-DD>/<company-name>/. Use when the user says "custom resume", "tailor my resume", "resume for this job", or pastes a job post / job URL and asks for a resume.
---

# Custom Resume

Trigger: **`custom resume`** plus a job post (pasted text, a URL, or a file path).

**Whose resume.** `<me>` is the person in `.me` (`python .claude/skills/job-apply-shared/scripts/me.py`). Everything below reads only their folder, `skillsets-and-contributions/<me>/`, and saves only under `apply/<me>/`. If `me.py check` reports a missing `resume/resume-base.json`, run the `profile-setup` skill first.

## Resume style: read it first

Each person picks a style in profile.json `resume_style`. Every caller (job-apply skills, daily jobs, apply-job-link, the job-resume-builder agent) runs the same build command, and the script follows the person's style:

| `resume_style` | What it is | Steps to follow |
|---|---|---|
| `classic` (default) | their own resume layout, kept fixed (`resume-base.json`); only bullets, project text and skills items change | Steps 1 to 7 as written below |
| `modern` | a clean one-page resume built fresh for each job: tagline, 3 to 4 sentence career summary, experience, 6-category skills grid; black, white and gray only | Steps 1, 2, then **"Modern style"** below, then Steps 6 and 7 |

Both styles also read `skillsets-and-contributions/<me>/resume/resume-guide.md` when it exists: the person's own rules for positioning, tone, what to keep in the background and the shape of the page. Follow it on top of everything here. When it conflicts with this page, the guide wins, except for Truth only (never invent anything).

## Modern style (when `resume_style` is `modern`)

Facts, numbers and technologies come only from their accomplishments (every file in `contributions/`, including any detailed project inventory PDF: read it with `pdftotext -layout`) and their skill set. Name and contact links come from profile.json and are drawn by the script.

1. From the post (Step 2), pick the 3 to 5 things the employer cares about most.
2. Write `content.json`:
   ```json
   {
     "style": "modern",
     "job": {"company": "...", "title": "...", "url": "..."},
     "keywords": ["..."],
     "page": "Letter",
     "tagline": "Senior Backend Engineer · Payments and APIs",
     "summary": "3 to 4 sentences: years in the industry, new and existing systems, business needs turned into production software.",
     "jobs": [{"company": "...", "role": "...", "dates": "May 2026 – Present · Remote",
               "ctx": "optional one-line context", "bullets": ["...", "..."]}],
     "earlier": ["2009 to 2015", "one short paragraph for older roles"],
     "skills": [["Frontend:", ["React", "Next.js", "TypeScript"]], ["Backend:", ["Node.js", "Laravel"]]]
   }
   ```
   - `page`: `Letter` for US and Canada companies, `A4` for everyone else (default: profile.json `resume_page`).
   - Tagline on one line. No physical location anywhere; dates end with `· Remote`.
   - Most relevant roles get 3 to 5 bullets, others 1 to 2. Each bullet is one contribution: the situation or problem, what they did, what changed, with real numbers. Bullets follow Step 4's human-writing rules (the build lints them).
   - Skills: 4 to 8 categories (6 fills the grid best), 3 to 4 items each, only what they really have. Mark personal-only skills as personal.
3. Build with the same command as Step 5. The script refuses (and writes no PDF) when the page is longer than one page, when **more than 24pt is empty at the bottom**, when a bullet ends with one word alone on its last line, or when the text fails the lint.
   - **Bottom gap too big:** add real content, best first: bullets that answer the job's top needs, numbers from the accomplishments, a context line for a role, an extra relevant role, a fuller Earlier Experience line. A line is about 12pt. Never enlarge fonts or spacing.
   - **Two pages:** cut or merge bullets. Never shrink anything.
4. Then Step 6 (look at it) and Step 7 (report).

## What stays fixed and what changes (classic style)

| Part | Rule |
|---|---|
| Header: name, designation | fixed |
| Contact rows (up to 4) | fixed |
| Experience: company, location, role + stack line, dates | fixed |
| **Experience: highlight bullets under each job** | **rewritten for this job post** |
| Projects: name and subtitle | fixed |
| **Projects: each featured project's description** | **rewritten for this job post** |
| Additional Experience, Education | fixed |
| Skills: the categories in `resume-base.json` (names, order, one line each) | fixed |
| **Skills: the items inside each category** | **re-picked and re-ordered for this job post**, only from the skill pool |
| Layout, fonts, sizes, spacing, rules, bullet glyphs, page size (A4, 1 page) | fixed, produced by the build script |

Fixed content lives in `skillsets-and-contributions/<me>/resume/resume-base.json`, copied from their current resume. Edit it only when their real resume changes, never to fit a job. The build script draws everything in the shared layout: Calibri header, Arial body, the same point sizes, positions and 0.75pt section rules (standard PDF fonts on machines without them). You only supply the bullets.

## Sources (read all of them every run)

1. **The job post.** Read it first and fully.
2. Career accomplishments (`skillsets-and-contributions/<me>/contributions/`). The **only** source of facts, systems and numbers for bullets.
3. Skill set (`skillsets-and-contributions/<me>/skills/my-skill-set.md`). What they can honestly claim.
4. Current resume (`skillsets-and-contributions/<me>/resume/<resume_file>`, the file named in profile.json) and `resume-base.json`. The format and the fixed text.
5. `proof-map.md` section 4: which projects each job may draw from, and projects with no job slot.
6. `resume/resume-guide.md`, when it exists: their own rules for positioning, tone and shape.

Never invent a project, number, tool or result. If the job post asks for something they haven't done, it goes in the gap list in the report, never on the resume.

## Step 1: Get and save the job post

- **Pasted text:** use it as is.
- **URL:** fetch it (WebFetch). If the page needs a login (LinkedIn, Workday and similar) or comes back empty, ask the user to paste the text. Don't guess the content.
- Make the output folder **`apply/<me>/<YYYY-MM-DD>/<company-name>/`**:
  - `<YYYY-MM-DD>` is today's date in the user's time zone: `python .claude/skills/job-apply-shared/scripts/me.py date`.
  - `<company-name>` is the company name in lowercase with hyphens (e.g. `acme-billing`, `superglue`).
  - If that folder already exists today (a second role at the same company), add the role: `apply/<me>/<date>/<company-name>-<role-slug>/`.
- Save the post there as `job-description.md`, with the company, title, URL and date at the top.

## Step 2: Analyze the job post

Write down:
- **Must-have skills and tools**, spelled exactly as the post spells them (`Node.js` vs `NodeJS`, `PostgreSQL` vs `Postgres`). An ATS matches exact strings.
- **Nice-to-haves.**
- **Domain and product** (billing, monitoring, e-commerce, HR tech, logistics, EdTech, fintech...).
- **Main responsibilities** (build APIs, own integrations, scale data pipelines, lead features...).
- **Keywords:** 10–20 hard skills and terms from the post. These go into `content.json` as `keywords` for the coverage check.
- **Gaps:** requirements they have no proof for in the accomplishments or skill set.

## Step 3: Pick the accomplishments

Each job in `resume-base.json` may only use accomplishments from **its own** projects (its `projects` list, mirrored in `proof-map.md` section 4), with a bullet count inside its `bullets: [min, max]`. When a job has several projects, a bullet may start with a `label` naming the project (e.g. `"label": "Store API:"`), like the base resume does.

- Rank each job's accomplishments by how directly they answer the post's must-haves and responsibilities. Take the top ones.
- Never move an accomplishment to a different job.
- Projects with **no job slot** (side, freelance or client work listed under "No job slot" in `proof-map.md`) can't be used. If they match the post well, say so in the report so the user can decide whether to add them to their base resume.
- Mention a tool in a bullet only if that project actually used it per the accomplishments or the role line.

## Step 4: Write the bullets

**Content**
- One accomplishment per bullet: **what was built + the tech + the result or scale**, e.g. `Built ... in NestJS and PostgreSQL, ... for 200+ teams.`
- Use the post's exact term when it is truly the same thing they did. Put the most important keywords early in the bullet.
- Keep the numbers from the accomplishments exactly (the "Headline numbers" in `proof-map.md`). Never round up or invent.
- Start with a strong plain verb: Built, Designed, Added, Integrated, Migrated, Delivered, Replaced, Cut, Moved, Wrote. Past tense, except the current job, which may use present tense like the base resume.

**Human, not AI** (the build refuses text that fails). Follow [HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md), sections 1–3: easy words, short sentences, nothing that sounds like an LLM wrote it.
- Plain words and short clauses, like the base resume. Say what was done, not how great it was. A hiring manager should get each bullet in one quick read.
- No sentence over 30 words. If a bullet runs long, split it into two short sentences or cut a detail.
- **Never use:** spearheaded, leveraged, utilized, robust, seamless, cutting-edge, state-of-the-art, innovative, passionate, synergy, orchestrated, pivotal, instrumental, transformative, holistic, meticulous, empowered, elevate, streamlined, showcasing, fostering, comprehensive, significantly, drastically, successfully, effectively, efficiently, strategically, various, numerous, "ensuring ..." tails, results-driven, proven track record.
- **Never use:** em or en dashes (use `-` with spaces, like the base resume), semicolons, curly quotes, `!`, emojis, or first person (I, my, we).
- Don't repeat the same verb or the same sentence shape across bullets.
- Don't stuff keywords. Each keyword appears where it's true, once or twice in the whole page.
- Every bullet ends with a full stop.

**ATS**
- The build keeps one plain text column, standard section headings, real selectable text with embedded fonts, no tables, images or icons, and PDF title/author metadata. Don't add anything that breaks that.
- Spell out an acronym once if the post uses the long form (e.g. `continuous integration (CI/CD)`).
- Dates, titles and company names stay exactly as in the base.

**Space budget:** the page holds what the base resume holds. Keep the total number of experience lines about the same as the base: adding a bullet or a line somewhere means taking one away elsewhere. Aim for 2 lines per bullet. The build reports lines per bullet, refuses a page that overflows (and says the base's line budget), and refuses a bullet longer than 3 lines.

Check any bullet on its own with:
```bash
python .claude/skills/custom-resume/scripts/build_resume.py --lint "<bullet text>"
```

## Step 4a: Tailor the featured project descriptions

Each project under `projects` in `resume-base.json` keeps its name and subtitle. Only the description under it changes.

- Facts come only from that project's section of the accomplishments. No other project's work goes here.
- Show the side of the project that fits the job post best, as a product: what it does and for whom, with a number.
- **Don't repeat the experience bullets.** When the same product appears under a job, the description must add a different angle, not restate the same system or number in the same words.
- Same writing rules as the bullets ([HUMAN-WRITING.md](../job-apply-shared/HUMAN-WRITING.md)): easy words, short sentences, no AI words, no first person, ends with a full stop. It may name tools, as the base does.
- **Length:** keep it at the base's length (2 lines, 3 at most). It counts toward the page budget.
- Leave `projects` out of `content.json` to keep the base description.

## Step 4b: Tailor the skills

The categories never change: the labels in `resume-base.json` `skills`, in that order, one line each. No new categories.

The items inside them can change:
- Pick only from `skill_pool` in `resume-base.json`. Every item there traces to their skill set, resume or accomplishments. If the post names a skill that isn't in the pool, it's a gap, not a skills item. Add to the pool only when the user confirms they really have it.
- Put the post's must-have skills first in each line, spelled the way the pool spells them (the build fixes case, e.g. `nestjs` → `NestJS`).
- Drop pool items the post doesn't care about to make room. Each line must fit on one line (about 8 short items). The build refuses a line that's too long.
- A category left out of `content.json` keeps its base text.
- Don't repeat an item in two categories.

## Step 5: Build

Save `content.json` in `apply/<me>/<date>/<company-name>/`. Job ids, project ids and category names are the ones in their `resume-base.json` (shown here with the template's example ids):

```json
{
  "job": {"company": "...", "title": "...", "url": "..."},
  "keywords": ["Node.js", "TypeScript", "PostgreSQL", "..."],
  "experience": {
    "acme":   [{"text": "..."}, {"text": "..."}],
    "shopco": [{"label": "Store API:", "text": "..."}, {"label": "Order Sync:", "text": "..."}]
  },
  "projects": {
    "payflow": "Shipped a billing product with ..."
  },
  "skills": {
    "Languages":    ["TypeScript", "JavaScript", "SQL"],
    "Frameworks":   ["NestJS", "Express.js", "React"],
    "Technologies": ["Node.js", "PostgreSQL", "Redis", "Docker", "AWS", "CI/CD"]
  }
}
```

Then:
```bash
python .claude/skills/custom-resume/scripts/build_resume.py apply/<me>/<date>/<company-name>/content.json apply/<me>/<date>/<company-name>/<resume_file>
```

- `NOT BUILT` → fix what it lists (rewrite flagged words, shorten, or drop a bullet) and run again.
- On success it prints the text an ATS will read and `keywords present x/y` plus the missing list. For each missing keyword: if they truly have it and a bullet can say so honestly, work it in and rebuild. If they don't have it, leave it out and list it as a gap.
- Keep the file name `<resume_file>` (profile.json), since recruiters see it.

## Step 6: Check it

1. Open the PDF with the Read tool and look at it: one page, nothing cut off. Classic: the layout matches the base resume (`build_resume.py --base <scratchpad>/base.pdf` to compare). Modern: header on one line, no empty band at the bottom.
2. Reread every bullet and project description as a hiring manager would. If one sounds like marketing copy, takes two reads to understand, or could have been written by anyone, rewrite it in easier words.
3. Confirm every fact traces to the accomplishments.

## Step 7: Report and save

Write `apply/<me>/<date>/<company-name>/report.md` and give the user the same summary in chat:
- Job: company, title, link.
- Keyword coverage: present x/y, and the missing ones split into **gap** (they don't have it) and **left out** (they have it but there was no room).
- What changed per job: which accomplishments were chosen and why, in one line each.
- Projects: which angle each description now shows, and why.
- Skills: what was added, dropped or moved up in each category, and why.
- Relevant work that isn't on the resume (projects with no job slot), if any.
- Path to the PDF.

Then commit and push only that folder (through the [git-push skill](../git-push/SKILL.md)):
```bash
git add apply/<me>/<date>/<company-name>
git commit -m "<me>: resume: $(python .claude/skills/job-apply-shared/scripts/me.py stamp) — <company> <role>"
git push
```
