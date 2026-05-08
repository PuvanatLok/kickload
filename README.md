# KickMate — Football Gathering App

A mobile app for Thai football players to find matches, fill team rosters,
match by skill level, discover stadiums, track gang leaderboards, and split
field costs.

## Docs
- [Product Requirements Document](docs/PRD.md)
- [Entity Relationship Diagram](docs/ERD.dbml) — paste into https://dbdiagram.io

## Project Structure
```
football-app/
├── docs/           # PRD, ERD, API spec, architecture decisions
├── terraform/      # Infrastructure as Code (GCP)
├── backend/        # FastAPI (Python)
├── mobile/         # Flutter (iOS + Android)
└── data/           # dbt models, analytics
```

## Tech Stack

| Layer | Tool | Reason |
|---|---|---|
| Mobile | Flutter | Single codebase for iOS + Android |
| Backend | FastAPI (Python) | Async, typed, OpenAPI auto-docs |
| Database | PostgreSQL + PostGIS | Relational + geospatial in one |
| Auth | Supabase Auth | LINE Login + phone OTP |
| Real-time | Supabase Realtime | Live roster updates |
| Events | GCP Pub/Sub | Serverless event ingestion |
| Warehouse | BigQuery | Analytics and marketing insights |
| Transforms | dbt | SQL models on top of BigQuery |
| Infra | Terraform | All cloud resources as code |

## Getting Started
(Setup instructions added as each layer is built)
