"""Thin Salesforce REST client using the OAuth client credentials flow."""
import os
import time
from urllib.parse import quote

import requests


class SalesforceClient:
    def __init__(self) -> None:
        self.domain = os.environ["SF_DOMAIN"].rstrip("/")
        self.client_id = os.environ["SF_CLIENT_ID"]
        self.client_secret = os.environ["SF_CLIENT_SECRET"]
        self.api = os.environ.get("SF_API_VERSION", "62.0")
        self._token: str | None = None
        self._instance: str | None = None
        self._expires_at: float = 0

    def _auth(self) -> None:
        if self._token and time.time() < self._expires_at:
            return
        r = requests.post(
            f"{self.domain}/services/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=30,
        )
        r.raise_for_status()
        body = r.json()
        self._token = body["access_token"]
        self._instance = body["instance_url"].rstrip("/")
        # Tokens from this flow last ~2h by default. Refresh well before that.
        self._expires_at = time.time() + 90 * 60

    def query(self, soql: str) -> list[dict]:
        self._auth()
        r = requests.get(
            f"{self._instance}/services/data/v{self.api}/query",
            headers={"Authorization": f"Bearer {self._token}"},
            params={"q": soql},
            timeout=30,
        )
        if r.status_code == 401:
            self._token = None
            self._auth()
            r = requests.get(
                f"{self._instance}/services/data/v{self.api}/query",
                headers={"Authorization": f"Bearer {self._token}"},
                params={"q": soql},
                timeout=30,
            )
        r.raise_for_status()
        return r.json().get("records", [])


def soql_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")
