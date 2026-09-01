"""Blitz search adapter."""

from __future__ import annotations

from typing import Any

from ...config import credential
from ...contracts import Account, Contact
from ...contracts.dedupe import deduplicate, normalized_domain, normalized_linkedin
from ..base import APIClient, ProviderAdapter


def _current_company(person: dict[str, Any]) -> dict[str, Any]:
    experiences = person.get("experiences") or []
    return next(
        (item for item in experiences if item.get("job_is_current")),
        experiences[0] if experiences else {},
    )


class BlitzAdapter(ProviderAdapter):
    name = "blitz"
    capabilities = frozenset({"inspect", "search_accounts", "search_contacts"})

    def __init__(self, token: str | None = None, **client_kwargs: Any) -> None:
        token = token or credential("BLITZAPI_API_KEY")
        self.api = APIClient(
            "https://api.blitz-api.ai/v2",
            {"x-api-key": token, "Content-Type": "application/json"},
            **client_kwargs,
        )

    def inspect(self) -> dict[str, Any]:
        return self.api.request("GET", "/account/key-info")

    def _people(self, query: dict[str, Any], limit: int) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        cursor: str | None = None
        while len(records) < limit:
            body = {**query, "max_results": min(50, limit - len(records))}
            if cursor:
                body["cursor"] = cursor
            response = self.api.request("POST", "/search/people", json=body)
            batch = response.get("results") or []
            records.extend(batch)
            cursor = response.get("cursor")
            if not cursor or not batch:
                break
        return records[:limit]

    def search_contacts(self, query: dict[str, Any], limit: int = 25) -> list[Contact]:
        self.require("search_contacts")
        contacts = []
        for index, row in enumerate(self._people(query, limit)):
            company = _current_company(row)
            contacts.append(
                Contact(
                    provider=self.name,
                    provider_id=str(row.get("id") or row.get("linkedin_url") or f"result-{index}"),
                    full_name=row.get("full_name") or "Unnamed contact",
                    title=company.get("job_title") or row.get("headline"),
                    email=row.get("email"),
                    linkedin_url=row.get("linkedin_url") or None,
                    attributes={"provenance": "Blitz people search"},
                )
            )
        return deduplicate(contacts, lambda item: normalized_linkedin(str(item.linkedin_url or "")))

    def search_accounts(self, query: dict[str, Any], limit: int = 25) -> list[Account]:
        self.require("search_accounts")
        accounts = []
        for index, row in enumerate(self._people(query, limit)):
            company = _current_company(row)
            domain = company.get("company_website") or company.get("company_domain")
            accounts.append(
                Account(
                    provider=self.name,
                    provider_id=str(company.get("company_id") or f"result-{index}"),
                    name=company.get("company_name") or "Unnamed account",
                    domain=normalized_domain(domain) or None,
                    attributes={"provenance": "Blitz people search"},
                )
            )
        return deduplicate(accounts, lambda item: normalized_domain(item.domain))
