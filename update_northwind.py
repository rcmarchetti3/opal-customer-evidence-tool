"""One-off: make Northwind's approval status explicit in the win notes."""
import requests
from dotenv import load_dotenv
from sf_client import SalesforceClient

load_dotenv()
sf = SalesforceClient()
sf._auth()

OPP_ID = "006fj00000LtIhlAAF"
notes = (
    "Northwind's marketing team was running 40+ landing page variants by hand across three regions. "
    "Pilot on their cardiology product line cut time-to-launch for a campaign page from 11 days to 2. "
    "Q2 conversion on the pilot pages was up 23% vs control. Champion: Dana Whitfield, VP Digital Marketing. "
    "Dana agreed to a public case study and signed our customer reference release on July 8, 2026. "
    "Cleared for external use of the Northwind name and logo."
)
r = requests.patch(
    f"{sf._instance}/services/data/v{sf.api}/sobjects/Opportunity/{OPP_ID}",
    headers={"Authorization": f"Bearer {sf._token}", "Content-Type": "application/json"},
    json={"Win_Notes__c": notes},
    timeout=30,
)
r.raise_for_status()
print("updated", OPP_ID, r.status_code)
