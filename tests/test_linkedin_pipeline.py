import json
from datetime import UTC, datetime

import httpx
import pytest

from agentic_gtm.database import FileStore
from agentic_gtm.workflows.linkedin_engagers import normalize
from agentic_gtm.workflows.linkedin_pipeline import (
    classify_roster,
    collect_stage,
    export_review_sheet,
    plan_collection,
    reconcile_seen,
)

COMPANY = "https://www.linkedin.com/company/synthetic-company"
FOUNDER = "https://www.linkedin.com/in/synthetic-founder"
EMPLOYEE = "https://www.linkedin.com/in/synthetic-employee"
POST = "https://www.linkedin.com/feed/update/urn:li:activity:1234567890123456789/"


def spec(stage, items, **kwargs):
    endpoints = {
        "discovery": ["post-search"],
        "employees": ["profile-search"],
        "posts": ["company-posts", "profile-posts"],
        "engagement": ["post-reactions", "post-comments"],
        "profiles": ["profile"],
        "companies": ["company"],
    }[stage]
    return {
        "stage": stage,
        "client_id": "synthetic",
        "account_scope": "fixture-account",
        "items": items,
        "max_pages": 3,
        "max_calls": 12,
        "max_records": 100,
        "budget_microusd": 1200,
        "prices_microusd": dict.fromkeys(endpoints, 100),
        "price_basis": "synthetic test",
        **kwargs,
    }


def response(elements, page=1, total=1, token=None):
    return httpx.Response(
        200,
        json={
            "status": 200,
            "elements": elements,
            "pagination": {"pageNumber": page, "totalPages": total, "paginationToken": token},
        },
    )


def test_discovery_preserves_voices_and_does_not_stop_at_old_pinned_posts(tmp_path):
    sources = [
        {"kind": "company", "url": COMPANY, "approved": True},
        {"kind": "founder", "url": FOUNDER, "approved": True},
        {
            "kind": "employee",
            "url": EMPLOYEE,
            "approved": True,
            "membership": "core",
            "membership_evidence": "synthetic reviewed current role",
        },
    ]
    accepted = plan_collection(
        spec(
            "posts",
            sources,
            published_since="2026-08-01T00:00:00Z",
            published_until="2026-09-01T00:00:00Z",
        ),
        tmp_path / "posts",
    )
    requests = []

    def handler(request):
        requests.append(request)
        page = int(request.url.params["page"])
        if page == 1:
            return response(
                [{"linkedinUrl": POST, "postedAt": {"timestamp": 1000000000000}}],
                page,
                2,
                "PageCaseToken",
            )
        assert request.url.params["paginationToken"] == "PageCaseToken"
        stamp = datetime(2026, 8, 20, tzinfo=UTC).timestamp() * 1000
        return response([{"linkedinUrl": POST, "postedAt": {"timestamp": stamp}}], page, 2)

    with httpx.Client(
        base_url="https://api.harvestapi.io", transport=httpx.MockTransport(handler)
    ) as client:
        state = collect_stage(
            tmp_path / "posts", accepted["sha256"], FileStore(tmp_path / "store"), client
        )
    assert state["complete"] and state["requests"] == 6
    assert requests[0].url.params["profile"] == FOUNDER
    posts = json.loads((tmp_path / "posts/posts.json").read_text())
    assert len(posts) == 1 and len(posts[0]["sources"]) == 3


def test_engagement_cache_across_runs_and_seen_provenance(tmp_path):
    items = [
        {
            "url": POST,
            "sources": [{"kind": "founder", "url": FOUNDER}, {"kind": "company", "url": COMPANY}],
            "published_at": "2026-08-20T00:00:00Z",
        }
    ]
    store, calls = FileStore(tmp_path / "store"), []

    def handler(request):
        calls.append(request)
        return response(
            [
                {
                    "id": "reaction" if request.url.path.endswith("reactions") else "comment",
                    "actor": {
                        "id": "prospect",
                        "name": "Synthetic Person",
                        "linkedinUrl": "https://www.linkedin.com/in/synthetic-prospect",
                    },
                }
            ]
        )

    with httpx.Client(
        base_url="https://api.harvestapi.io", transport=httpx.MockTransport(handler)
    ) as client:
        for index in (1, 2):
            run = tmp_path / f"run{index}"
            accepted = plan_collection(spec("engagement", items), run)
            state = collect_stage(run, accepted["sha256"], store, client)
            assert state["requests"] == (2 if index == 1 else 0)
            assert normalize(run)["people"] == 1
            fresh = reconcile_seen(run, tmp_path / "seen/seen.json")
            assert fresh["new_events"] == (2 if index == 1 else 0)
            assert reconcile_seen(run, tmp_path / "seen/seen.json") == fresh
    assert len(calls) == 2
    people = json.loads((tmp_path / "run2/people.json").read_text())
    assert people[0]["num_sources"] == 2
    assert people[0]["source_kinds"] == ["company", "founder"]


def test_employee_review_is_required_and_multiple_roles_are_not_assumed_primary(tmp_path):
    people = [{"url": EMPLOYEE}]
    profiles = [
        {
            "url": EMPLOYEE,
            "observed_at": "2026-09-09T00:00:00Z",
            "profile": {
                "currentPosition": [
                    {"companyLinkedinUrl": COMPANY},
                    {"companyLinkedinUrl": "https://www.linkedin.com/company/synthetic-investor"},
                ]
            },
        }
    ]
    reviewed = classify_roster(people, profiles, COMPANY)
    assert reviewed[0]["membership"] == "review" and not reviewed[0]["approved"]
    with pytest.raises(ValueError, match="reviewed roster"):
        plan_collection(
            spec(
                "posts",
                reviewed,
                prices_microusd={"profile-posts": 100},
                published_since="2026-08-01T00:00:00Z",
                published_until="2026-09-01T00:00:00Z",
            ),
            tmp_path / "invalid",
        )
    profiles[0]["profile"]["currentPosition"] = [{"companyLinkedinUrl": COMPANY}]
    assert classify_roster(people, profiles, COMPANY)[0]["membership"] == "core"


def test_budget_stop_persists_partial_state(tmp_path):
    accepted = plan_collection(
        spec(
            "engagement",
            [{"url": POST, "sources": [{"kind": "company", "url": COMPANY}]}],
            budget_microusd=100,
        ),
        tmp_path / "run",
    )
    with (
        httpx.Client(
            base_url="https://api.harvestapi.io",
            transport=httpx.MockTransport(lambda request: response([])),
        ) as client,
        pytest.raises(ValueError, match="spend ceiling"),
    ):
        collect_stage(tmp_path / "run", accepted["sha256"], FileStore(tmp_path / "store"), client)
    state = json.loads((tmp_path / "run/state.json").read_text())
    assert state["complete"] is False and state["reserved_microusd"] == 100


def test_resolved_alias_does_not_create_a_new_seen_reaction(tmp_path):
    from agentic_gtm.workflows.linkedin_engagers import write_json

    opaque = "https://www.linkedin.com/in/ACoSynthetic"
    public = "https://www.linkedin.com/in/synthetic-person"
    item = {"url": POST, "sources": [{"kind": "founder", "url": FOUNDER}]}
    for index in (1, 2):
        run = tmp_path / f"alias-{index}"
        accepted = plan_collection(spec("engagement", [item]), run)
        (run / "pages").mkdir()
        actor = {"linkedinUrl": opaque, "name": "Synthetic person"}
        if index == 2:
            actor.update(id="stable-person", linkedinUrl=public)
        write_json(
            run / "pages/one.json",
            {
                "post_url": POST,
                "endpoint": "post-reactions",
                "plan_hash": accepted["sha256"],
                "observed_at": f"2026-09-0{index}T00:00:00+00:00",
                "response": {"elements": [{"id": f"changing-reaction-{index}", "actor": actor}]},
            },
        )
        profiles = tmp_path / "profiles.json"
        write_json(
            profiles,
            [
                {
                    "url": opaque,
                    "profile": {
                        "id": "stable-person",
                        "publicIdentifier": "synthetic-person",
                        "currentPosition": [],
                    },
                }
            ],
        )
        normalize(run, profiles if index == 2 else None)
        result = reconcile_seen(run, tmp_path / "seen/seen.json")
        assert result["new_events"] == (1 if index == 1 else 0)
    people = json.loads((run / "people.json").read_text())
    assert people[0]["profile_url"] == public
    ledger = json.loads((tmp_path / "seen/seen.json").read_text())
    assert len(ledger["events"]) == 1
    assert next(iter(ledger["events"].values()))["first_seen_at"].startswith("2026-09-01")


def discovered_post(url, stamp, author, reactions=0, comments=0):
    return {
        "linkedinUrl": url,
        "postedAt": {"timestamp": stamp},
        "author": {"name": author, "linkedinUrl": "https://www.linkedin.com/in/" + author},
        "engagement": {"reactions": [{"type": "LIKE", "count": reactions}], "comments": comments},
    }


def test_post_search_finds_third_party_posts_the_roster_cannot_reach(tmp_path):
    """A funding post is carried by investors and press, not only by the roster voices."""
    window = {
        "published_since": "2026-09-01T00:00:00Z",
        "published_until": "2026-09-11T00:00:00Z",
    }
    inside = int(datetime(2026, 9, 3, tzinfo=UTC).timestamp() * 1000)
    outside = int(datetime(2026, 8, 1, tzinfo=UTC).timestamp() * 1000)
    store = FileStore(tmp_path / "store")

    def handler(request):
        assert request.url.params["search"] == "synthetic seed round"
        return response(
            [
                discovered_post(POST, inside, "investor-vc", reactions=12, comments=3),
                # Fuzzy search also returns an unrelated sense of the keyword.
                discovered_post(
                    "https://www.linkedin.com/feed/update/urn:li:activity:2222222222222222222/",
                    inside,
                    "unrelated-agriculture",
                    reactions=400,
                ),
                # Out of window, must be dropped.
                discovered_post(
                    "https://www.linkedin.com/feed/update/urn:li:activity:3333333333333333333/",
                    outside,
                    "old-post",
                    reactions=999,
                ),
            ]
        )

    run = tmp_path / "discovery"
    accepted = plan_collection(
        spec("discovery", [{"query": "synthetic seed round"}], **window), run
    )
    with httpx.Client(
        base_url="https://api.harvestapi.io", transport=httpx.MockTransport(handler)
    ) as client:
        collect_stage(run, accepted["sha256"], store, client)
    rows = json.loads((run / "discovery.json").read_text())
    assert [row["author_name"] for row in rows] == ["unrelated-agriculture", "investor-vc"]
    assert all(row["approved"] is False for row in rows), "candidates must stay unreviewed"
    assert rows[1]["url"] == POST and rows[1]["queries"] == ["synthetic seed round"]


def test_discovery_output_cannot_be_pre_approved_or_skip_review(tmp_path):
    window = {
        "published_since": "2026-09-01T00:00:00Z",
        "published_until": "2026-09-11T00:00:00Z",
    }
    with pytest.raises(ValueError, match="do not pre-approve"):
        plan_collection(
            spec("discovery", [{"query": "synthetic", "approved": True}], **window),
            tmp_path / "a",
        )
    with pytest.raises(ValueError, match="non-empty query"):
        plan_collection(spec("discovery", [{"query": "   "}], **window), tmp_path / "b")
    # A discovered post still needs reviewed source voices before engagement spend.
    with pytest.raises(ValueError, match="source voices"):
        plan_collection(spec("engagement", [{"url": POST}]), tmp_path / "c")


def test_record_cap_is_per_endpoint_so_reactions_cannot_starve_comments(tmp_path):
    """A shared counter let reactions consume the cap and leave comments zero pages."""
    items = [{"url": POST, "sources": [{"kind": "founder", "url": FOUNDER}]}]
    store = FileStore(tmp_path / "store")

    def handler(request):
        reactions = request.url.path.endswith("reactions")
        # Reactions return a full page; comments return one row.
        elements = [
            {
                "id": f"{'reaction' if reactions else 'comment'}-{index}",
                "actor": {
                    "id": f"person-{index}",
                    "name": f"Person {index}",
                    "linkedinUrl": f"https://www.linkedin.com/in/person-{index}",
                },
                **({} if reactions else {"commentary": "Congrats"}),
            }
            for index in range(10 if reactions else 1)
        ]
        return response(elements)

    run = tmp_path / "run"
    accepted = plan_collection(spec("engagement", items, max_records=10), run)
    with httpx.Client(
        base_url="https://api.harvestapi.io", transport=httpx.MockTransport(handler)
    ) as client:
        state = collect_stage(run, accepted["sha256"], store, client)
    pages = {row["endpoint"]: row["pages"] for row in state["coverage"]}
    assert pages["post-reactions"] == 1
    assert pages["post-comments"] == 1, "comments must still be fetched under the same cap"
    # normalize budgets the cap the same way, so the commenter survives.
    normalize(run)
    events = json.loads((run / "events.json").read_text())
    assert any(event["type"] == "comment" for event in events)


def test_export_keeps_reaction_type_and_comment_text_and_leaves_judgment_blank(tmp_path):
    items = [{"url": POST, "sources": [{"kind": "founder", "url": FOUNDER}]}]
    store = FileStore(tmp_path / "store")

    def handler(request):
        reactions = request.url.path.endswith("reactions")
        actor = {
            "id": "prospect",
            "name": "Synthetic Buyer",
            "position": "Bid Manager",
            "linkedinUrl": "https://www.linkedin.com/in/synthetic-prospect",
        }
        element = {"id": "r1" if reactions else "c1", "actor": actor}
        if reactions:
            element["reactionType"] = "INTEREST"
        else:
            element["commentary"] = "We spend weeks on every tender"
        return response([element])

    run = tmp_path / "run"
    accepted = plan_collection(spec("engagement", items), run)
    with httpx.Client(
        base_url="https://api.harvestapi.io", transport=httpx.MockTransport(handler)
    ) as client:
        collect_stage(run, accepted["sha256"], store, client)
    normalize(run)
    out = tmp_path / "review.csv"
    result = export_review_sheet(run, out)
    assert result["rows"] == 1 and result["with_comments"] == 1
    text = out.read_text()
    assert "INTEREST".lower() in text, "rare reaction types must survive into the sheet"
    assert "We spend weeks on every tender" in text
    header = text.splitlines()[0].split(",")
    for column in ("tier", "why_person", "why_company", "next_step"):
        assert column in header
    row = text.splitlines()[1]
    assert row.endswith(",,,,"), "judgment columns stay blank for a human to fill"
