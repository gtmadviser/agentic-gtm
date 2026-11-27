import json

import httpx

from agentic_gtm.adapters.lemlist import LemlistAdapter
from agentic_gtm.adapters.slack.adapter import SlackAdapter
from agentic_gtm.references import resolve_mentions, resolve_provider_links

ROSTER = [
    {"name": "Maximilian Muster", "short": "Max", "email": "max@example.com"},
    {"name": "Andrea Beispiel", "short": "Andi", "email": "andi@example.com", "slack_user_id": "U0ANDI"},
]


def test_mentions_use_roster_id_or_lookup_and_report_unresolved() -> None:
    text, unresolved = resolve_mentions(
        "Hi @Max, bitte mit @Andi klären. @Maximilian bleibt Text.", [dict(m) for m in ROSTER],
        lambda email: "U0MAX" if email == "max@example.com" else None,
    )
    assert text == "Hi <@U0MAX>, bitte mit <@U0ANDI> klären. @Maximilian bleibt Text."
    assert unresolved == []
    text, unresolved = resolve_mentions("Hi @Max", [dict(ROSTER[0])], lambda email: None)
    assert text == "Hi @Max"
    assert unresolved == ["Max"]


def test_provider_links_render_as_slack_links() -> None:
    text, unresolved = resolve_provider_links(
        "Kampagne [[lemlist:cam_1|Vorstand | Sie]] ist pausiert.", None, {"team_id": "tea_1"}
    )
    assert text == (
        "Kampagne <https://app.lemlist.com/teams/tea_1/campaigns-v2/cam_1|Vorstand / Sie> ist pausiert."
    )
    assert unresolved == []
    text, unresolved = resolve_provider_links("[[lemlist:cam_1|X]]", None, {})
    assert text == "X" and unresolved == ["[[lemlist:cam_1|X]]"]


def test_lemlist_campaign_url_uses_team_id() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/team"
        return httpx.Response(200, json={"_id": "tea_9"}, request=request)

    adapter = LemlistAdapter(token="t", transport=httpx.MockTransport(handler))
    assert adapter.campaign_url("cam_5") == "https://app.lemlist.com/teams/tea_9/campaigns-v2/cam_5"


def test_slack_lookup_user_id() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/users.lookupByEmail"
        assert request.url.params["email"] == "max@example.com"
        return httpx.Response(200, content=json.dumps({"ok": True, "user": {"id": "U0MAX"}}), request=request)

    adapter = SlackAdapter(token="xoxb-test", transport=httpx.MockTransport(handler))
    assert adapter.lookup_user_id("max@example.com") == "U0MAX"
