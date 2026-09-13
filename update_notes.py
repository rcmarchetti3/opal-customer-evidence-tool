"""Enrich win notes on the four seeded opportunities so drafts have enough source material."""
import requests
from dotenv import load_dotenv
from sf_client import SalesforceClient

load_dotenv()
sf = SalesforceClient()
sf._auth()

NOTES = {
    "Northwind Medical Devices": (
        "Northwind makes cardiology and vascular devices sold to hospital systems in the US, EU, and Japan. "
        "Marketing team of 14 across three regional offices. Before us they were running 40+ landing page variants by hand "
        "across three regions; every regional launch meant a ticket to the web team and an average 11 days to get a campaign page live. "
        "Pilot ran April 6 to June 30, 2026 on the cardiology product line, 12 pages, US region only. "
        "Time-to-launch for a campaign page dropped from 11 days to 2. Q2 conversion on the pilot pages was up 23% vs control "
        "(control was the hand-built pages for the same products). Deployed Personalization Platform with the web experimentation module. "
        "Champion: Dana Whitfield, VP Digital Marketing. On the June 24 QBR call Dana said: "
        "\"We stopped waiting on the web team. My regional leads can put a page in market the same week the campaign is approved, "
        "and for the first time I can show the board a number instead of a feeling.\" "
        "Next: they plan to extend to the vascular line and the EU region in Q4. "
        "Dana agreed to a public case study and signed our customer reference release on July 8, 2026. "
        "Cleared for external use of the Northwind name and logo."
    ),
    "Harbor & Vale Outfitters": (
        "DTC outdoor apparel brand, about 900 employees, sells through their own site and 40 retail stores in the Pacific Northwest. "
        "They had a homegrown A/B tool nobody trusted; results were argued about more than acted on, and they shipped about 2 tests a quarter. "
        "Replaced it with Web Experimentation plus the CMS in March 2026. First 90 days: 31 experiments shipped. "
        "The checkout redesign test drove a 9.4% lift in mobile revenue per visitor. Their marketing ops lead, Marcus Bell, said on the wrap-up call: "
        "\"We went from arguing about whether the test was even valid to arguing about what to test next. That's the whole change.\" "
        "Marcus has agreed to a case study and their brand team has cleared use of the name. No legal review needed per Marcus."
    ),
    "Kestrel Financial": (
        "Regional bank and wealth manager, 5,200 employees, four business units each with its own marketing group (60 marketers total). "
        "Regulated content workflow was the whole story: compliance review added an average of 3 weeks to every campaign and there was no "
        "single place to see what was waiting on whom. Deployed Content Marketing Platform in May 2026 with structured approval steps per business unit. "
        "Compliance review time went from 3 weeks to 4 days. Campaign throughput roughly doubled in the first quarter. "
        "Contact is Elena Ruiz, Director of Marketing Operations. "
        "Legal has NOT cleared external use of the Kestrel name. Their comms team requires a written release before anything public. "
        "Do not publish or share externally until that comes through."
    ),
    "Brightline Logistics": (
        "B2B freight and logistics, 1,300 employees, serves mid-market shippers in the US Midwest. "
        "The freight quote form on their site had a 71% abandonment rate and it was their main lead source. "
        "Three rounds of experiments on the form (field order, progressive disclosure, inline validation) took abandonment from 71% to 44% over eight weeks. "
        "That works out to roughly 300 extra qualified quote requests a month. Contact is Priya Raman, Director of Demand Gen. "
        "Priya on the results call: \"We'd been blaming the sales team for slow follow-up. Turns out most people never finished the form.\" "
        "Priya is willing to do a case study and has verbal clearance from her VP. Written release not yet on file."
    ),
}

soql = "SELECT Id, Account.Name FROM Opportunity WHERE StageName = 'Closed Won'"
for rec in sf.query(soql):
    name = rec["Account"]["Name"]
    if name not in NOTES:
        print("skip", name)
        continue
    r = requests.patch(
        f"{sf._instance}/services/data/v{sf.api}/sobjects/Opportunity/{rec['Id']}",
        headers={"Authorization": f"Bearer {sf._token}", "Content-Type": "application/json"},
        json={"Win_Notes__c": NOTES[name]},
        timeout=30,
    )
    r.raise_for_status()
    print("updated", name, r.status_code)
