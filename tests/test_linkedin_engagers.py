"""Synthetic data only. No Harvest credits or live LinkedIn actions."""

import importlib.util
import json
from pathlib import Path

import httpx
import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills/linkedin-engager-outreach/scripts/harvest_engagers.py"
)
spec = importlib.util.spec_from_file_location("harvest_engagers", SCRIPT)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
POST = "urn:li:activity:1234567890123456789"


def actor(identity="person-a", slug="example-a", **extra):
    return {
        "id": identity,
        "name": "Example Person",
        "position": "Example Role",
        "linkedinUrl": "https://www.linkedin.com/in/" + slug,
        **extra,
    }


def test_paginated_collection_cache_and_interaction_dedup(tmp_path):
    plan = helper.create_plan(tmp_path, [POST], 3, 6)
    calls = []

    def handler(request):
        calls.append(request)
        page = int(request.url.params["page"])
        reactions = request.url.path.endswith("post-reactions")
        if reactions:
            elements = [
                {
                    "id": f"reaction-{page}",
                    "actor": actor() if page == 1 else actor("person-b", "example-b"),
                    "reactionType": "LIKE",
                }
            ]
        else:
            assert request.url.params["sortBy"] == "date"
            elements = [
                {
                    "id": "comment-1",
                    "actor": actor(),
                    "commentary": "Synthetic comment",
                    "createdAtTimestamp": 1700000000000,
                    "replies": [
                        {"id": "reply-1", "actor": actor(), "commentary": "Synthetic reply"},
                        {"actor": actor(author=True), "commentary": "Author"},
                    ],
                }
            ]
        return httpx.Response(
            200,
            json={
                "status": 200,
                "elements": elements,
                "pagination": {"pageNumber": page, "totalPages": 2 if reactions else 1},
            },
        )

    with httpx.Client(base_url=helper.BASE_URL, transport=httpx.MockTransport(handler)) as client:
        state = helper.collect(tmp_path, plan["sha256"], client)
        assert state["complete"] and state["requests"] == 3
        assert not state["replies_complete"]
        helper.collect(tmp_path, plan["sha256"], client)
    assert len(calls) == 3
    result = helper.normalize(tmp_path)
    assert result["people"] == 2 and result["events"] == 4
    events = json.loads((tmp_path / "events.json").read_text())
    assert all(event["engaged_at"] is None for event in events if event["type"] == "reaction")
    before = (tmp_path / "events.json").read_bytes()
    helper.normalize(tmp_path)
    assert before == (tmp_path / "events.json").read_bytes()
    assert (tmp_path / ".gitignore").read_text() == "*\n"


def test_budget_marks_partial_without_extra_calls(tmp_path):
    plan = helper.create_plan(tmp_path, [POST], 10, 1)
    with httpx.Client(
        base_url=helper.BASE_URL,
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200, json={"status": "200", "elements": [], "pagination": {"totalPages": 3}}
            )
        ),
    ) as client:
        state = helper.collect(tmp_path, plan["sha256"], client)
    assert state["requests"] == 1 and state["complete"] is False
    assert len(state["coverage"]) == 2


def test_uncertain_paid_request_is_reserved_and_not_retried(tmp_path):
    plan = helper.create_plan(tmp_path, [POST], 3, 6)
    attempts = []

    def timeout(request):
        attempts.append(request)
        raise httpx.ReadTimeout("synthetic timeout", request=request)

    with httpx.Client(base_url=helper.BASE_URL, transport=httpx.MockTransport(timeout)) as client:
        with pytest.raises(ValueError, match="no automatic retry"):
            helper.collect(tmp_path, plan["sha256"], client)
        with pytest.raises(ValueError, match="uncertain"):
            helper.collect(tmp_path, plan["sha256"], client)
    assert len(attempts) == 1
    assert json.loads((tmp_path / "state.json").read_text())["requests"] == 1


@pytest.mark.parametrize(
    "url",
    [
        "https://linkedin.com.evil.example/in/a",
        "http://linkedin.com/in/a",
        "https://linkedin.com/company/a",
    ],
)
def test_person_url_validation(url):
    with pytest.raises(ValueError):
        helper.linkedin_url(url, "profile")


def test_normalizer_quarantines_unknowns_and_excludes_companies_and_author(tmp_path):
    helper.create_plan(tmp_path, [POST], 1, 2)
    (tmp_path / "pages").mkdir()
    elements = [
        {"actor": actor(), "reactionType": "LIKE"},
        {"actor": actor(identity=""), "reactionType": "LIKE"},
        {"actor": {"name": "No identity"}, "reactionType": "LIKE"},
        {
            "actor": actor(linkedinUrl="https://linkedin.com/company/example"),
            "reactionType": "LIKE",
        },
        {"actor": actor(author=True), "reactionType": "LIKE"},
    ]
    helper.write_json(
        tmp_path / "pages/a.json",
        {
            "post_url": helper.post_url(POST),
            "endpoint": "post-reactions",
            "observed_at": "2026-09-06T00:00:00Z",
            "response": {"elements": elements},
        },
    )
    result = helper.normalize(tmp_path)
    assert result["people"] == 1 and result["events"] == 1 and result["quarantined"] == 1
    assert result["collection_complete"] is False


def test_tampered_plan_and_wrong_approval_stop_offline(tmp_path):
    helper.create_plan(tmp_path, [POST], 1, 2)
    with pytest.raises(ValueError, match="exact reviewed"):
        helper.collect(tmp_path, "wrong")
    plan = json.loads((tmp_path / "plan.json").read_text())
    plan["payload"]["max_calls"] = 999
    helper.write_json(tmp_path / "plan.json", plan)
    with pytest.raises(ValueError, match="Plan changed"):
        helper.load_plan(tmp_path)
