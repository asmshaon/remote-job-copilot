# Proof map

What this person has really built, mapped to the searches and offers the skills make. **Every row comes from
the accomplishments file, resume or skill set in this folder.** Claude builds this file in `profile setup`,
re-reads the accomplishments each run, and adds rows when it finds more. Never add a row for work that isn't
in those files.

The rows below are made-up examples showing the shape. Replace them.

## Headline numbers

The real numbers writing may use, exactly as in the accomplishments file (never rounded up):

- 300+ small businesses on PayFlow
- 20,000+ orders a day through the order sync
- 40+ online stores on the Store API

## 1. Company outreach and job search: proof → product types

Used by linkedin-company-outreach (3a), the job-apply searches (RULES Step 1) and product-outreach (Step 2).

| Proof (from the accomplishments file) | Product types to search for |
|---|---|
| PayFlow: plans, trials, failed-payment retries, 300+ businesses | subscription billing, usage-based pricing, payments SaaS |
| Order Sync: 20,000+ orders a day into the warehouse system | e-commerce operations, inventory and order sync, fulfillment |

## 2. Client outreach: service map

Used by linkedin-client-outreach (3a) and product-outreach (8b `domain_match`).

| Service (`domain_match`) | Proof | Who buys it |
|---|---|---|
| `payments-integration` | PayFlow billing: plans, trials, retries | SaaS founders adding paid plans |
| `ecommerce-backend` | Store API for 40+ stores, order sync | e-commerce brands, store-builder startups |

## 3. Upwork portfolio and catalog candidates

Used by upwork-profile (Steps 8 and 9).

| Project / offer | Shows | Keywords |
|---|---|---|
| PayFlow billing | plans, webhooks, failed-payment retries | Stripe, subscription billing |
| Store API | product, cart and checkout endpoints | REST API, e-commerce backend |

## 4. Resume: which projects each job may draw from

Mirrors `projects` in `resume/resume-base.json`. Projects with no job slot (side or client work) are listed
here so the resume report can point them out.

| Job id | Company | Projects | Bullets |
|---|---|---|---|
| `acme` | Acme Billing | PayFlow | 2-4 |
| `shopco` | ShopCo | Store API, Order Sync | 1-3 |

No job slot: (none yet)
