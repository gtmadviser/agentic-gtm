"""AI Ark people search normalized into public contracts."""

from __future__ import annotations

from typing import Any

from ...config import credential
from ...contracts import Account, Contact
from ...contracts.dedupe import deduplicate, normalized_domain, normalized_linkedin
from ..base import APIClient, ProviderAdapter


def _dig(record: dict[str, Any], *paths: str) -> Any:
    for path in paths:
        current: Any = record
        for part in path.split("."):
            if isinstance(current, list) and part.isdigit():
                current = current[int(part)] if int(part) < len(current) else None
            elif isinstance(current, dict):
                current = current.get(part)
            else:
                current = None
            if current is None:
                break
        if current not in (None, "", []):
            return current
    return None


class AIArkAdapter(ProviderAdapter):
    name = "ai_ark"
    capabilities = frozenset({"search_accounts", "search_contacts"})

    def __init__(self, token: str | None = None, **client_kwargs: Any) -> None:
        token = token or credential("AI_ARK_API_KEY")
        self.api = APIClient(
            "https://api.ai-ark.com/api/developer-portal",
            {"X-TOKEN": token, "Content-Type": "application/json"},
            **client_kwargs,
        )

    def _people(self, query: dict[str, Any], limit: int) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        page = 0
        while len(records) < limit:
            response = self.api.request(
                "POST", "/v1/people", json={**query, "page": page, "size": min(100, limit)}
            )
            batch = response.get("content") or []
            records.extend(batch)
            page += 1
            if not batch or page >= int(response.get("totalPages") or page):
                break
        return records[:limit]

    def search_contacts(self, query: dict[str, Any], limit: int = 25) -> list[Contact]:
        self.require("search_contacts")
        contacts = []
        for index, row in enumerate(self._people(query, limit)):
            linkedin = _dig(row, "linkedinUrl", "linkedin_url", "socialLinks.linkedin")
            contacts.append(
                Contact(
                    provider=self.name,
                    provider_id=str(_dig(row, "id", "personId") or f"result-{index}"),
                    full_name=str(_dig(row, "fullName", "full_name", "name") or "Unnamed contact"),
                    title=_dig(row, "title", "jobTitle", "headline", "currentTitle"),
                    email=_dig(row, "email", "workEmail", "emails.0"),
                    linkedin_url=linkedin or None,
                    attributes={"provenance": "AI Ark people search"},
                )
            )
        return deduplicate(contacts, lambda item: normalized_linkedin(str(item.linkedin_url or "")))

    def search_accounts(self, query: dict[str, Any], limit: int = 25) -> list[Account]:
        self.require("search_accounts")
        accounts = []
        for index, row in enumerate(self._people(query, limit)):
            domain = _dig(
                row,
                "companyDomain",
                "company.domain",
                "company.website",
                "currentCompany.domain",
            )
            accounts.append(
                Account(
                    provider=self.name,
                    provider_id=str(_dig(row, "companyId", "company.id") or f"result-{index}"),
                    name=str(
                        _dig(row, "companyName", "company.name", "currentCompany.name")
                        or "Unnamed account"
                    ),
                    domain=normalized_domain(str(domain or "")) or None,
                    attributes={"provenance": "AI Ark people search"},
                )
            )
        return deduplicate(accounts, lambda item: normalized_domain(item.domain))
