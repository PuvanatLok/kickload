# KickLoad — Claude Project Context

## Who I Am
- Name: Cartoon (Puvanat)
- Role: Learning data engineering by building a real product
- Goal: Ship a working app + strong portfolio demonstrating DE skills

## What This Project Is
A Thai football gathering mobile app. Players find matches, fill rosters,
match by skill level, find stadiums, track gang leaderboards, and split
field costs. Thai market only (Phase 1).

Full spec: `docs/PRD.md`
Data model: `docs/ERD.dbml` (visualize at dbdiagram.io)

## Current Phase
Step 0-1 complete: PRD written, ERD designed, Git initialized.
Next: Step 2 — Terraform dev environment on GCP.

## Tech Stack
| Layer        | Tool                        |
|--------------|-----------------------------|
| Mobile       | Flutter (iOS + Android)     |
| Backend API  | FastAPI (Python)            |
| Database     | PostgreSQL + PostGIS        |
| Auth         | Supabase Auth (LINE Login)  |
| Real-time    | Supabase Realtime           |
| Events       | GCP Pub/Sub                 |
| Warehouse    | BigQuery                    |
| Transforms   | dbt                         |
| Infra        | Terraform on GCP            |
| Dashboards   | Looker Studio               |

## Key Architectural Decisions (already made — don't re-debate)
- **Pub/Sub over Kafka for the product**: serverless, zero ops, handles Thai
  market scale. Kafka goes in a separate `data-platform` repo as a DE showcase.
- **Supabase for prototype → GCP Cloud SQL for production**: clean migration
  path via pg_dump. Supabase Pro is production-ready for Thai scale.
- **ELO rating system**: starts at 1000, K=32 under 20 games, K=16 after.
- **Team-level payments**: one treasurer per team, internal player splits tracked
  in `player_payment_shares`. PromptPay is external — no in-app payment Phase 1.
- **Position slots**: declared per team at match creation, stored in
  `match_position_slots`. Prevents post-join position conflicts.

## Project Folder Structure
```
kickmate/
├── CLAUDE.md           ← you are here
├── README.md
├── .gitignore
├── docs/
│   ├── PRD.md          ← product requirements
│   └── ERD.dbml        ← database schema (paste to dbdiagram.io)
├── terraform/          ← not created yet
├── backend/            ← not created yet
├── mobile/             ← not created yet
└── data/               ← not created yet (dbt, dashboards)
```

## Git Conventions
- Branch: `main` (production), `develop` (integration), `feature/*`, `hotfix/*`
- Commits: `type(scope): description`
  - Types: `feat` | `fix` | `chore` | `docs` | `refactor` | `test`
  - Examples: `feat(match): add position slot validation`
  - Examples: `fix(payment): correct split rounding for odd player counts`
- Always commit to a feature branch, never directly to main

## What NOT to Do
- Do not add Kafka to the product — it is over-engineering at this scale
- Do not add features outside `docs/PRD.md` Section 3 without asking
- Do not create markdown documentation files unless Cartoon explicitly asks
- Do not use emojis
- Do not add comments that explain what the code does — only add comments
  when the WHY is non-obvious

## Thai Market Context
- Primary auth: LINE Login (not Google/Apple)
- Payment: PromptPay (not Stripe/credit card)
- Language: Thai UI first
- Server region: GCP asia-southeast1 (Singapore) — lowest latency from Thailand
- Target users: Thai male 18-35, casual football players
