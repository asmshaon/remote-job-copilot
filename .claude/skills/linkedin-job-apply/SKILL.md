---
name: linkedin-job-apply
description: Run when the user says "linkedin job apply". Also "apply job from linkedin job", and any of these with "without agent" (e.g. "apply job from linkedin job without agent") - this skill always runs in the main session (default mode), never with subagents. Job source is the LinkedIn Jobs section only, and only jobs that apply through an external link (never Easy Apply). Everything else follows the shared job-apply rules (job-apply-shared/RULES.md), the same for every source. Targets 20 jobs per run that match their accomplishments, skills and resume (their stack and home country, from profile.json), are remote worldwide, at companies in their target countries (profile.json, never their blocked countries), paying in their range per market analysis. Builds a tailored resume per job with the custom-resume skill, applies on the company's own site (forms submitted only after the user's go-ahead) or saves a 3-paragraph email as a Gmail draft for them to send. Only applied jobs are saved in apply/<me>/linkedin-job/<YYYY-MM-DD>/<company-name>/. A job applied to from any source is blocked for 6 months in all of them.
---

# LinkedIn Job Apply

Trigger: **`linkedin job apply`**. Optional: a number (`linkedin job apply 10`). Default target: 20.

Also triggered by **`apply job from linkedin job`**. **Default mode, no agents:** this skill always runs in the main session, step by step, and never calls the Agent tool, whether or not the user adds "without agent" (e.g. `apply job from linkedin job without agent`). See "Run mode" in [RULES.md](../job-apply-shared/RULES.md).

**Follow [job-apply-shared/RULES.md](../job-apply-shared/RULES.md) for everything**: rules, sources of truth, Step 0, the common job checks, pay (1c), Steps 2–9 and the report. This page only covers what is specific to LinkedIn Jobs.

| Setting | Value |
|---|---|
| `--source` | `linkedin` |
| Applied jobs folder | `apply/<me>/linkedin-job/` |
| Job URL recorded | the LinkedIn job URL (`linkedin.com/jobs/view/<id>`) |

```bash
A="python .claude/skills/job-apply-shared/scripts/apply.py --source linkedin"
```

## Step 1 (LinkedIn): Find jobs in LinkedIn Jobs (read-only)

Search LinkedIn **Jobs** with the role, stack and domain terms from RULES Step 1, starting from profile.json `job_search.linkedin_queries` (e.g. `Senior Backend Engineer Node.js`, `NestJS developer`, `TypeScript backend payments`) and varying them.

**Filters:** Remote, Date posted = Past week (Past month if 20 good jobs aren't found), Experience level = Mid-Senior / Associate. Don't turn on the "Easy Apply" filter. Also run the searches with Location set to **Worldwide**, and add `worldwide`, `anywhere`, `global remote`, `work from anywhere` to the keywords. Expect to open 60–100 postings to keep 20.

**LinkedIn-specific check (before the common checks):**
- **External apply only.** The button says **Apply** with the external-link icon and opens the company's site or ATS. **Skip anything that shows Easy Apply.**

Then apply all the **common job checks** in RULES Step 1 (stack, experience, proof, remote worldwide on the company's page, company country, pay, real company, 6-month block), rank by pay then proof fit, and take the top N.

## LinkedIn-specific notes for later steps

- **Step 2:** clicking **Apply** opens the company's page. That's navigation, not applying.
- **Step 3:** `job-description.md` records the LinkedIn job URL and the LinkedIn company page next to the company's apply URL.
- **Step 7:** if LinkedIn asks "Did you apply?", answer **Yes** only for applications actually submitted.
- **Report:** add "Easy Apply only" to the skip reasons.
