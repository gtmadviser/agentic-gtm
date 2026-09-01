"""HubSpot inspection and normalized CRM pulls."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ...config import credential
from ...contracts import Account, Contact, Opportunity
from ..base import APIClient, ProviderAdapter


class HubSpotAdapter(ProviderAdapter):
    name = "hubspot"
    capabilities = frozenset({"inspect", "pull"})

    def __init__(self, token: str | None = None, **client_kwargs: Any) -> None:
        token = token or credential("HUBSPOT_ACCESS_TOKEN")
        self.api = APIClient(
            "https://api.hubapi.com",
            {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            **client_kwargs,
        )

    def inspect(self) -> dict[str, Any]:
        self.require("inspect")
        return {
            "provider": self.name,
            "properties": {
                object_type: self.api.request("GET", f"/crm/v3/properties/{object_type}").get(
                    "results", []
                )
                for object_type in ("companies", "contacts", "deals")
            },
            "pipelines": self.api.request("GET", "/crm/v3/pipelines/deals").get("results", []),
            "requires_field_map_confirmation": True,
        }

    def _search(self, object_type: str, properties: list[str]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        after: str | None = None
        while True:
            body: dict[str, Any] = {"limit": 100, "properties": properties}
            if after:
                body["after"] = after
            page = self.api.request("POST", f"/crm/v3/objects/{object_type}/search", json=body)
            results.extend(page.get("results", []))
            after = ((page.get("paging") or {}).get("next") or {}).get("after")
            if not after:
                return results

    def pull(self, field_map: dict[str, str]) -> dict[str, list[Any]]:
        self.require("pull")
        if not field_map:
            raise ValueError("HubSpot pull requires a human-confirmed field map in gtm.yaml")
        company_props = ["name", "domain", "industry", "numberofemployees"]
        contact_props = ["firstname", "lastname", "jobtitle", "email", "hs_linkedin_url"]
        deal_props = ["dealname", "dealstage", "amount", "closedate", "hs_is_closed_won"]
        raw_accounts = self._search("companies", company_props)
        raw_contacts = self._search("contacts", contact_props)
        raw_deals = self._search("deals", deal_props)
        accounts = [self._account(row) for row in raw_accounts]
        contacts = [self._contact(row) for row in raw_contacts]
        opportunities = [self._opportunity(row) for row in raw_deals]
        return {"accounts": accounts, "contacts": contacts, "opportunities": opportunities}

    def _account(self, row: dict[str, Any]) -> Account:
        props = row.get("properties") or {}
        employees = props.get("numberofemployees")
        return Account(
            provider=self.name,
            provider_id=str(row["id"]),
            name=props.get("name") or "Unnamed account",
            domain=props.get("domain"),
            industry=props.get("industry"),
            employee_count=int(employees) if str(employees or "").isdigit() else None,
            attributes={"archived": row.get("archived", False)},
        )

    def _contact(self, row: dict[str, Any]) -> Contact:
        props = row.get("properties") or {}
        name = " ".join(filter(None, [props.get("firstname"), props.get("lastname")])).strip()
        return Contact(
            provider=self.name,
            provider_id=str(row["id"]),
            full_name=name or props.get("email") or "Unnamed contact",
            title=props.get("jobtitle"),
            email=props.get("email"),
            linkedin_url=props.get("hs_linkedin_url") or None,
        )

    def _opportunity(self, row: dict[str, Any]) -> Opportunity:
        props = row.get("properties") or {}
        is_won = str(props.get("hs_is_closed_won", "")).lower() == "true"
        stage = props.get("dealstage") or "unknown"
        status = "won" if is_won else ("lost" if "lost" in stage.lower() else "open")
        close_date = props.get("closedate")
        parsed_close = None
        if close_date:
            parsed_close = datetime.fromisoformat(close_date.replace("Z", "+00:00")).astimezone(UTC)
        amount = props.get("amount")
        return Opportunity(
            provider=self.name,
            provider_id=str(row["id"]),
            name=props.get("dealname") or "Unnamed opportunity",
            stage=stage,
            status=status,
            amount=float(amount) if amount not in (None, "") else None,
            close_date=parsed_close,
        )
