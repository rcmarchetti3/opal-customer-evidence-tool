"""Opal custom tool: get_customer_win.

Pulls a closed-won opportunity and its account from Salesforce so an Opal agent
can build a case study from real deal data instead of asking sales for it.

Run locally:  uvicorn main:app --port 8000 --reload
Discovery:    GET /discovery
"""
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from opal_tools_sdk import ToolsService, tool
from pydantic import BaseModel, Field

from sf_client import SalesforceClient, soql_escape

load_dotenv()

app = FastAPI(title="Customer Evidence Tools")
tools_service = ToolsService(app)
sf = SalesforceClient()

BEARER = os.environ.get("TOOL_BEARER_TOKEN")


@app.middleware("http")
async def check_bearer(request: Request, call_next):
    """If TOOL_BEARER_TOKEN is set, require it on tool calls. Discovery stays open."""
    if BEARER and request.url.path.startswith("/tools/"):
        header = request.headers.get("authorization", "")
        if header != f"Bearer {BEARER}":
            return JSONResponse({"error": "unauthorized"}, status_code=401)
    return await call_next(request)


class CustomerWinParams(BaseModel):
    account_name: str = Field(
        description="Customer account name as it appears in Salesforce. Partial matches are allowed, e.g. 'Northwind'."
    )
    opportunity_id: Optional[str] = Field(
        default=None,
        description="Optional Salesforce Opportunity Id (starts with 006). Use when the account has more than one closed-won deal.",
    )


@tool(
    "get_customer_win",
    "Fetches a closed-won deal from Salesforce for a named customer account: account profile, opportunity details, "
    "and the sales rep's win notes. Use this before writing any customer case study or success story so the "
    "narrative is grounded in real CRM data. Returns found=false with candidates if the account is ambiguous or has no closed-won deal.",
)
async def get_customer_win(parameters: CustomerWinParams) -> dict:
    name = soql_escape(parameters.account_name.strip())

    where = ["StageName = 'Closed Won'", f"Account.Name LIKE '%{name}%'"]
    if parameters.opportunity_id:
        where.append(f"Id = '{soql_escape(parameters.opportunity_id)}'")

    soql = (
        "SELECT Id, Name, Amount, CloseDate, Description, Win_Notes__c, "
        "Account.Id, Account.Name, Account.Industry, Account.NumberOfEmployees, Account.Website "
        f"FROM Opportunity WHERE {' AND '.join(where)} ORDER BY CloseDate DESC LIMIT 5"
    )
    records = sf.query(soql)

    if not records:
        return {
            "found": False,
            "reason": f"No closed-won opportunity found for an account matching '{parameters.account_name}'.",
            "candidates": [],
        }

    if len(records) > 1 and not parameters.opportunity_id:
        return {
            "found": False,
            "reason": "More than one closed-won opportunity matched. Ask the user which one, or pass opportunity_id.",
            "candidates": [
                {
                    "opportunity_id": r["Id"],
                    "opportunity_name": r["Name"],
                    "account_name": r["Account"]["Name"],
                    "close_date": r["CloseDate"],
                    "amount": r.get("Amount"),
                }
                for r in records
            ],
        }

    r = records[0]
    acct = r["Account"]
    return {
        "found": True,
        "account": {
            "id": acct["Id"],
            "name": acct["Name"],
            "industry": acct.get("Industry"),
            "employees": acct.get("NumberOfEmployees"),
            "website": acct.get("Website"),
        },
        "opportunity": {
            "id": r["Id"],
            "name": r["Name"],
            "amount": r.get("Amount"),
            "close_date": r["CloseDate"],
            "description": r.get("Description"),
        },
        "win_notes": r.get("Win_Notes__c") or "",
        "source": "salesforce",
    }


@app.get("/")
async def root() -> dict:
    return {"service": "customer-evidence-tools", "discovery": "/discovery"}


@app.get("/health")
async def health() -> dict:
    return {"ok": True}
