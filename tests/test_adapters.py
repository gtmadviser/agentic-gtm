import base64
import json

import httpx

from agentic_gtm.adapters.ai_ark import AIArkAdapter
from agentic_gtm.adapters.blitz import BlitzAdapter
from agentic_gtm.adapters.instantly import InstantlyAdapter
from agentic_gtm.adapters.lemlist import LemlistAdapter
from agentic_gtm.contracts import CampaignDraft
from agentic_gtm.safety import make_plan


def response(request: httpx.Request, payload, status: int = 200) -> httpx.Response:
    return httpx.Response(status, json=payload, request=request)


def test_sourcing_adapters_normalize_to_same_contact_contract() -> None:
    def ai_ark_handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-token"] == "test"
        return response(
            request,
            {
                "content": [
                    {
                        "id": "person-1",
                        "fullName": "Ada Example",
                        "title": "Founder",
                        "linkedinUrl": "https://linkedin.com/in/ada-example",
                    }
                ],
                "totalPages": 1,
            },
        )

    def blitz_handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-api-key"] == "test"
        return response(
            request,
            {
                "results": [
                    {
                        "id": "person-1",
                        "full_name": "Ada Example",
                        "linkedin_url": "https://linkedin.com/in/ada-example",
                        "experiences": [{"job_is_current": True, "job_title": "Founder"}],
                    }
                ]
            },
        )

    ai_ark = AIArkAdapter(token="test", transport=httpx.MockTransport(ai_ark_handler))
    blitz = BlitzAdapter(token="test", transport=httpx.MockTransport(blitz_handler))
    left = ai_ark.search_contacts({}, 1)[0]
    right = blitz.search_contacts({}, 1)[0]
    assert (left.full_name, left.title, str(left.linkedin_url)) == (
        right.full_name,
        right.title,
        str(right.linkedin_url),
    )


def test_lemlist_apply_creates_and_verifies_paused_campaign() -> None:
    events = []

    def handler(request: httpx.Request) -> httpx.Response:
        expected = "Basic " + base64.b64encode(b":test").decode()
        assert request.headers["authorization"] == expected
        events.append((request.method, request.url.path))
        if request.method == "POST" and request.url.path.endswith("/campaigns"):
            body = json.loads(request.content)
            assert body == {"name": "Safe draft", "timezone": "Europe/Berlin"}
            return response(
                request,
                {"_id": "campaign-1", "sequenceId": "sequence-1", "state": "running"},
            )
        if request.method == "POST" and request.url.path.endswith("/pause"):
            return response(request, {"_id": "campaign-1", "state": "paused"})
        if request.method == "POST" and request.url.path.endswith("/steps"):
            body = json.loads(request.content)
            assert body["type"] == "email"
            assert body["message"] == "Body text"
            assert body["subject"] == "hello"
            assert body["delayType"] == "within"
            return response(request, {"_id": "step-1"})
        return response(request, {"_id": "campaign-1", "state": "paused"})

    adapter = LemlistAdapter(token="test", transport=httpx.MockTransport(handler))
    draft = CampaignDraft(
        name="Safe draft",
        provider="lemlist",
        audience_query={},
        steps=[{"day": 0, "channel": "email", "subject": "hello", "body": "Body text"}],
        status="paused",
    )
    plan = make_plan(
        "campaign.create_paused",
        "lemlist",
        [str(draft.id)],
        adapter.plan_campaign(draft),
        "Create paused campaign",
    )
    result = adapter.apply_campaign(plan)
    assert result.verified is False
    assert "manual configuration" in result.message
    assert result.provider_ids == ["campaign-1"]
    assert events == [
        ("POST", "/api/campaigns"),
        ("POST", "/api/campaigns/campaign-1/pause"),
        ("POST", "/api/sequences/sequence-1/steps"),
        ("GET", "/api/campaigns/campaign-1"),
    ]


def test_instantly_apply_uses_non_active_status() -> None:
    events = []

    def handler(request: httpx.Request) -> httpx.Response:
        events.append((request.method, request.url.path))
        assert request.headers["user-agent"].startswith("agentic-gtm/")
        if request.method == "POST" and request.url.path.endswith("/campaigns"):
            body = json.loads(request.content)
            assert body["name"] == "Safe draft"
            schedule = body["campaign_schedule"]["schedules"][0]
            assert schedule["timezone"] == "Europe/Berlin"
            assert schedule["timing"] == {"from": "08:00", "to": "17:00"}
            assert schedule["days"] == {
                "0": False,
                "1": True,
                "2": True,
                "3": True,
                "4": True,
                "5": True,
                "6": False,
            }
            return response(request, {"id": "campaign-2", "status": 1})
        if request.method == "POST" and request.url.path.endswith("/pause"):
            return response(request, {"id": "campaign-2", "status": 2})
        if request.method == "PATCH":
            body = json.loads(request.content)
            assert body == {
                "sequences": [
                    {
                        "steps": [
                            {
                                "type": "email",
                                "delay": 0,
                                "variants": [{"subject": "hello", "body": "Body text"}],
                            }
                        ]
                    }
                ]
            }
            return response(request, {"id": "campaign-2", "status": 2})
        return response(request, {"id": "campaign-2", "status": 2})

    adapter = InstantlyAdapter(token="test", transport=httpx.MockTransport(handler))
    draft = CampaignDraft(
        name="Safe draft",
        provider="instantly",
        audience_query={},
        steps=[{"day": 0, "channel": "email", "subject": "hello", "body": "Body text"}],
        status="paused",
    )
    plan = make_plan(
        "campaign.create_paused",
        "instantly",
        [str(draft.id)],
        adapter.plan_campaign(draft),
        "Create draft campaign",
    )
    assert adapter.apply_campaign(plan).verified is True
    assert events == [
        ("POST", "/api/v2/campaigns"),
        ("POST", "/api/v2/campaigns/campaign-2/pause"),
        ("PATCH", "/api/v2/campaigns/campaign-2"),
        ("GET", "/api/v2/campaigns/campaign-2"),
    ]


def test_instantly_pulls_campaign_metrics() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/campaigns/analytics")
        return response(
            request,
            [
                {
                    "campaign_id": "campaign-2",
                    "campaign_name": "Synthetic",
                    "emails_sent_count": 400,
                    "bounced_count": 4,
                    "reply_count": 12,
                    "total_opportunities": 3,
                }
            ],
        )

    adapter = InstantlyAdapter(token="test", transport=httpx.MockTransport(handler))
    rows = adapter.pull_campaign_metrics()
    assert len(rows) == 1
    assert rows[0].sent == 400
    assert rows[0].effective_delivered == 396
    assert rows[0].opportunities == 3
    assert rows[0].source == "instantly.analytics"


def test_lemlist_rejects_unknown_channel() -> None:
    import pytest

    from agentic_gtm.adapters.base import AdapterError
    from agentic_gtm.adapters.lemlist.adapter import lemlist_step

    assert lemlist_step({"channel": "linkedin_invite", "day": 2, "body": "hi"})["type"] == (
        "linkedinInvite"
    )
    with pytest.raises(AdapterError):
        lemlist_step({"channel": "carrier_pigeon"})
