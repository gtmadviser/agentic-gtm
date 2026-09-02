"""No-key, wholly fictional acceptance workflow."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..contracts import CampaignDraft, CampaignMetrics, Experiment
from ..safety import make_plan
from .metrics import CSV_COLUMNS, render_outreach_review, summarize


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_demo(output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    icp = {
        "status": "working",
        "declared_belief": "Small B2B software teams with a technical founder",
        "observed_evidence": [
            {
                "claim": "Three fictional wins share an engineering-led evaluation",
                "source": "synthetic CRM fixture",
                "confidence": 0.75,
            }
        ],
        "anti_icp": ["consumer applications", "teams without an accountable owner"],
        "missing_evidence": ["channel preference", "typical buying committee"],
    }
    experiment = Experiment(
        name="Technical founder signal test",
        audience="Fictional B2B software companies with 10-80 employees",
        trigger="Recently hired a first revenue leader",
        channel="email",
        hypothesis="Trigger-specific outreach earns at least 5 qualified replies per 100 delivered",
        denominator="delivered messages",
        safeguards=["suppress opt-outs", "exclude competitors", "maximum 40 new contacts per day"],
        decision_rule="Continue only if 100 delivered messages produce >=5 qualified replies",
        owner="Demo Operator",
    )
    draft = CampaignDraft(
        name="Synthetic founder signal test",
        provider="lemlist",
        audience_query={"fixture": "synthetic-company", "limit": 25},
        steps=[
            {
                "day": 0,
                "channel": "email",
                "variants": [
                    {
                        "subject": "first revenue hire",
                        "body": (
                            "Saw the revenue lead role on your careers page. Most teams your "
                            "size spend the first quarter rebuilding the list before anyone "
                            "sells. Northstar Relay keeps the handoff list current for "
                            "engineering-led teams. Worth a look at how it works?"
                        ),
                        "hypothesis": "verifiable observation opener",
                    },
                    {
                        "subject": "quarter one for a new rev lead",
                        "body": (
                            "A new revenue lead usually inherits a list nobody trusts. "
                            "Northstar Relay keeps that list current so week one is selling, "
                            "not cleaning. Should I send how a 40-person team set it up?"
                        ),
                        "hypothesis": "scenario opener",
                    },
                ],
            },
            {
                "day": 4,
                "channel": "email",
                "subject": "one more angle",
                "body": (
                    "Different angle: the list is only half of it. The other half is knowing "
                    "which accounts moved since the last export. Happy to show that part in "
                    "ten minutes, or say no and I stop here."
                ),
            },
        ],
        schedule={"timezone": "Europe/Berlin"},
        status="paused",
    )
    campaign_payload = {
        "desired_state": "paused",
        "campaign": {
            "name": draft.name,
            "schedule": draft.schedule.model_dump(mode="json"),
            "steps": [step.model_dump(mode="json") for step in draft.steps],
        },
    }
    plan = make_plan(
        "campaign.create_paused",
        "lemlist",
        ["synthetic-audience"],
        campaign_payload,
        "Create one fictional campaign in paused state",
    )
    window_start = datetime(2026, 8, 1, tzinfo=UTC)
    window_end = datetime(2026, 8, 31, tzinfo=UTC)
    metrics = [
        CampaignMetrics(
            provider="demo",
            campaign="Synthetic founder signal test",
            variant="A",
            window_start=window_start,
            window_end=window_end,
            sent=620,
            bounced=9,
            replied=31,
            positive_replies=11,
            meetings=4,
            opportunities=2,
        ),
        CampaignMetrics(
            provider="demo",
            campaign="Synthetic founder signal test",
            variant="B",
            window_start=window_start,
            window_end=window_end,
            sent=610,
            bounced=8,
            replied=44,
            positive_replies=6,
            meetings=0,
            opportunities=0,
        ),
    ]
    csv_lines = [",".join(CSV_COLUMNS)]
    for row in metrics:
        dumped = row.model_dump(mode="json")
        csv_lines.append(",".join(str(dumped.get(column) or "") for column in CSV_COLUMNS))
    report = render_outreach_review(summarize(metrics), datetime.now(UTC))
    weekly = """# Synthetic weekly GTM review

## What changed

- A working ICP was drafted from fictional evidence.
- One experiment was preregistered; execution has not started.
- A paused campaign action plan was created but not applied.
- Two fictional variants were scored; variant B shows the reply-vanity pattern.

## Risks

- Channel preference remains unknown.
- The sample is synthetic and must not be treated as company evidence.

## Next actions

- Demo Operator: review the hypothesis and denominator.
- Demo Operator: reject or explicitly apply a real plan only after connecting owned systems.
"""
    _write_json(output / "icp.json", icp)
    _write_json(output / "experiment.json", experiment.model_dump(mode="json"))
    _write_json(output / "campaign-draft.json", draft.model_dump(mode="json"))
    _write_json(output / "campaign-plan.json", plan.model_dump(mode="json"))
    (output / "metrics-sample.csv").write_text("\n".join(csv_lines) + "\n", encoding="utf-8")
    (output / "outreach-review.md").write_text(report, encoding="utf-8")
    (output / "weekly-review.md").write_text(weekly, encoding="utf-8")
    return {
        "mode": "demo",
        "synthetic": True,
        "output": str(output),
        "artifacts": [
            "icp.json",
            "experiment.json",
            "campaign-draft.json",
            "campaign-plan.json",
            "metrics-sample.csv",
            "outreach-review.md",
            "weekly-review.md",
        ],
        "campaign_status": "paused",
        "external_writes": 0,
    }
