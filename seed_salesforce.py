"""Seed a Salesforce dev org with fake closed-won deals for the Opal case study tool.

Run once: python seed_salesforce.py
Requires .env with SF_DOMAIN, SF_CLIENT_ID, SF_CLIENT_SECRET.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()
DOMAIN = os.environ["SF_DOMAIN"].rstrip("/")
API = os.environ.get("SF_API_VERSION", "62.0")


def get_token() -> tuple[str, str]:
    r = requests.post(
        f"{DOMAIN}/services/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": os.environ["SF_CLIENT_ID"],
            "client_secret": os.environ["SF_CLIENT_SECRET"],
        },
        timeout=30,
    )
    r.raise_for_status()
    body = r.json()
    return body["access_token"], body["instance_url"]


SEED = [
    {
        "account": {"Name": "Northwind Medical Devices", "Industry": "Healthcare", "NumberOfEmployees": 2400, "Website": "northwindmed.example.com"},
        "opp": {
            "Name": "Northwind - Personalization Platform",
            "StageName": "Closed Won", "CloseDate": "2026-06-18", "Amount": 185000,
            "Win_Notes__c": (
                "Northwind's marketing team was running 40+ landing page variants by hand across three regions. "
                "Pilot on their cardiology product line cut time-to-launch for a campaign page from 11 days to 2. "
                "Q2 conversion on the pilot pages was up 23% vs control. Champion: Dana Whitfield, VP Digital Marketing. "
                "She's already agreed in principle to a case study."
            ),
        },
    },
    {
        "account": {"Name": "Harbor & Vale Outfitters", "Industry": "Retail", "NumberOfEmployees": 900, "Website": "harborvale.example.com"},
        "opp": {
            "Name": "Harbor & Vale - Experimentation + CMS",
            "StageName": "Closed Won", "CloseDate": "2026-04-30", "Amount": 96000,
            "Win_Notes__c": (
                "DTC apparel brand. Replaced a homegrown A/B tool nobody trusted. First 90 days: 31 experiments shipped, "
                "checkout redesign test drove a 9.4% lift in mobile revenue per visitor. Marketing ops lead (Marcus Bell) "
                "wants to talk about how they went from 2 tests a quarter to 10 a month."
            ),
        },
    },
    {
        "account": {"Name": "Kestrel Financial", "Industry": "Financial Services", "NumberOfEmployees": 5200, "Website": "kestrelfin.example.com"},
        "opp": {
            "Name": "Kestrel - Content Marketing Platform",
            "StageName": "Closed Won", "CloseDate": "2026-07-22", "Amount": 240000,
            "Win_Notes__c": (
                "Regulated content workflow was the whole story. Compliance review used to add 3 weeks to every campaign. "
                "With structured approvals in CMP they got it to 4 days. 60-person marketing org across 4 business units. "
                "Legal has NOT cleared external use of their name yet. Anything public needs sign-off from their comms team."
            ),
        },
    },
    {
        "account": {"Name": "Brightline Logistics", "Industry": "Transportation", "NumberOfEmployees": 1300, "Website": "brightlinelogistics.example.com"},
        "opp": {
            "Name": "Brightline - Web Experimentation",
            "StageName": "Closed Won", "CloseDate": "2026-05-12", "Amount": 58000,
            "Win_Notes__c": (
                "Small deal, good story. B2B freight quote form had a 71% abandonment rate. Three rounds of tests got it to 44%. "
                "That's roughly 300 extra qualified quotes a month. Contact is Priya Raman, Director of Demand Gen."
            ),
        },
    },
]


def main() -> None:
    token, instance = get_token()
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    base = f"{instance}/services/data/v{API}/sobjects"

    for item in SEED:
        r = requests.post(f"{base}/Account", json=item["account"], headers=h, timeout=30)
        r.raise_for_status()
        acct_id = r.json()["id"]
        opp = {**item["opp"], "AccountId": acct_id}
        r = requests.post(f"{base}/Opportunity", json=opp, headers=h, timeout=30)
        r.raise_for_status()
        print(f"created {item['account']['Name']} -> {r.json()['id']}")


if __name__ == "__main__":
    main()
