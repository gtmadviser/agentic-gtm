from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from agentic_gtm.contracts import CampaignDraft
from agentic_gtm.contracts.dedupe import deduplicate, normalized_domain, normalized_email
from agentic_gtm.safety import assert_plan_can_apply, make_plan, redact


def test_action_plan_hash_detects_tampering() -> None:
    plan = make_plan("slack.post_report", "slack", ["C123"], {"text": "hello"}, "Post report")
    assert plan.verify()
    tampered = plan.model_copy(update={"payload": {"text": "changed"}})
    assert not tampered.verify()
    with pytest.raises(ValueError, match="hash"):
        assert_plan_can_apply(tampered)


def test_expired_plan_is_rejected() -> None:
    plan = make_plan("slack.post_report", "slack", ["C123"], {"text": "hello"}, "Post report")
    expired = plan.model_copy(
        update={"expires_at": datetime.now(UTC) - timedelta(seconds=1)}
    ).sealed()
    with pytest.raises(ValueError, match="expired"):
        assert_plan_can_apply(expired)


def test_campaign_contract_refuses_active_status() -> None:
    with pytest.raises(ValidationError, match="paused"):
        CampaignDraft(
            name="Unsafe",
            provider="lemlist",
            audience_query={},
            steps=[],
            status="draft",
        )


def test_deduplication_normalizes_identity() -> None:
    assert normalized_domain("https://WWW.Example.com/path") == "example.com"
    assert normalized_email(" Person@Example.com ") == "person@example.com"
    assert deduplicate(["A", "a", "B"], str.lower) == ["A", "B"]


def test_redaction_is_recursive() -> None:
    value = {"api_key": "supersecretvalue", "nested": ["Bearer abcdefghijklmnopqrstuv"]}
    assert redact(value) == {"api_key": "[REDACTED]", "nested": ["Bearer [REDACTED]"]}
