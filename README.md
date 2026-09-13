# Customer Evidence Tools for Optimizely Opal

A custom Opal tool that pulls a closed-won deal from Salesforce so an agent workflow can build a customer case study from real CRM data instead of asking sales for it.

Built as the data layer for a **Case Study Pipeline** workflow in Opal: Win Researcher → (condition) → Story Writer → Asset Producer, with Approval Requester and Not Found Notifier on the other branches.

## Tool

`get_customer_win(account_name: str, opportunity_id: str | None)`

Returns the account, the closed-won opportunity, and the rep's `Win_Notes__c` field as one JSON object. Handles three cases:

- `found: true` with the full record
- `found: false` with `candidates` when more than one closed-won deal matches
- `found: false` with a `reason` when nothing matches

Why a custom tool instead of Opal's Salesforce connector: the connector is per-user OAuth and generic CRUD. This is a typed, opinionated, service-authenticated endpoint that returns exactly what the workflow needs, including a custom field, so the LLM never writes SOQL and can't pull the wrong deal.

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in SF_DOMAIN (with https://), SF_CLIENT_ID, SF_CLIENT_SECRET
uvicorn main:app --port 8000
```

Then expose it (`cloudflared tunnel --url http://localhost:8000`) and register `<public-url>/discovery` in Opal under Connectors → Registries.

## Salesforce setup

Developer org. Connected App with **client credentials flow** enabled and a Run As user set. Custom field `Opportunity.Win_Notes__c` (long text). `seed_salesforce.py` creates four fictional accounts and closed-won deals; `update_notes.py` enriches the notes. Accounts are fictional on purpose so no real company is attributed results it didn't achieve.

## Deploy to Vercel

Root directory is this folder. `api/index.py` exposes the FastAPI app and `vercel.json` routes everything to it. Set these environment variables in the Vercel project:

- `SF_DOMAIN`, `SF_CLIENT_ID`, `SF_CLIENT_SECRET`, `SF_API_VERSION` (62.0)
- `TOOL_BEARER_TOKEN` (any long random string; paste the same value into the Opal registry's Bearer Token field)

Then register `https://<project>.vercel.app/discovery` in Opal.

## Files

- `main.py` — the Opal tool (FastAPI + `optimizely-opal.opal-tools-sdk`), bearer middleware
- `sf_client.py` — client credentials auth with token caching and one 401 retry
- `api/index.py`, `vercel.json` — Vercel wiring
- `seed_salesforce.py`, `update_notes.py` — one-off data setup
