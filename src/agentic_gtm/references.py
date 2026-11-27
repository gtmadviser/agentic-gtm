"""Slack mentions and provider deep links for stakeholder messages.

Every Slack message the engine posts or drafts must tag the person who has to act
with a real Slack mention and link every campaign it names straight to the
provider UI. This module turns the readable placeholders an author writes into
Slack markup:

    @Max                         -> <@U012ABC>        (team roster in gtm.yaml)
    [[lemlist:cam_123|Name]]     -> <https://app.lemlist.com/...|Name>

A name that cannot be resolved stays as plain text and is reported, so the
operator can fix it before applying the plan.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

DEFAULT_LINK_TEMPLATES = {
    # Verify once per workspace by opening a campaign in the lemlist UI.
    "lemlist_campaign": "https://app.lemlist.com/teams/{team_id}/campaigns-v2/{campaign_id}",
    "instantly_campaign": "https://app.instantly.ai/app/campaign/{campaign_id}/analytics",
    "hubspot_deal": "https://app.hubspot.com/contacts/{portal_id}/record/0-3/{deal_id}",
}

PROVIDER_TOKEN = re.compile(r"\[\[(?P<provider>[a-z]+):(?P<id>[A-Za-z0-9_-]+)\|(?P<label>[^\]]+)\]\]")


def slack_link(url: str, label: str) -> str:
    """Slack mrkdwn link. `|` and `>` in labels would break the markup."""
    clean = label.replace("|", "/").replace(">", "").replace("<", "")
    return f"<{url}|{clean}>"


def team_roster(settings: Any) -> list[dict[str, Any]]:
    roster = getattr(settings, "team", None)
    if roster is None and isinstance(settings, dict):
        roster = settings.get("team")
    return [member for member in (roster or []) if isinstance(member, dict)]


def _aliases(member: dict[str, Any]) -> list[str]:
    names = [member.get("short"), member.get("name"), *(member.get("aliases") or [])]
    return sorted({str(n).strip() for n in names if n and str(n).strip()}, key=len, reverse=True)


def resolve_mentions(
    text: str,
    roster: list[dict[str, Any]],
    lookup: Callable[[str], str | None] | None = None,
) -> tuple[str, list[str]]:
    """Replace `@Alias` of roster members with `<@USER_ID>`.

    The user ID comes from `slack_user_id` in the roster, else from `lookup(email)`.
    Returns the new text and the aliases that were mentioned but not resolved.
    """
    unresolved: list[str] = []
    for member in roster:
        aliases = _aliases(member)
        if not aliases:
            continue
        pattern = re.compile(r"(?<![\w<])@(" + "|".join(re.escape(a) for a in aliases) + r")(?![\w-])")
        if not pattern.search(text):
            continue
        user_id = member.get("slack_user_id") or None
        if not user_id and lookup and member.get("email"):
            user_id = lookup(str(member["email"]))
            if user_id:
                member["slack_user_id"] = user_id
        if user_id:
            text = pattern.sub(f"<@{user_id}>", text)
        else:
            unresolved.append(aliases[-1])
    return text, unresolved


def resolve_provider_links(
    text: str,
    templates: dict[str, str] | None = None,
    context: dict[str, str] | None = None,
) -> tuple[str, list[str]]:
    """Replace `[[lemlist:cam_x|Label]]` with a Slack link to the provider UI."""
    merged = {**DEFAULT_LINK_TEMPLATES, **(templates or {})}
    ctx = dict(context or {})
    unresolved: list[str] = []

    def repl(match: re.Match[str]) -> str:
        provider, ident, label = match.group("provider"), match.group("id"), match.group("label")
        template = merged.get(f"{provider}_campaign") or merged.get(provider)
        if not template:
            unresolved.append(match.group(0))
            return label
        try:
            url = template.format(campaign_id=ident, deal_id=ident, **ctx)
        except KeyError:
            unresolved.append(match.group(0))
            return label
        return slack_link(url, label)

    return PROVIDER_TOKEN.sub(repl, text), unresolved
