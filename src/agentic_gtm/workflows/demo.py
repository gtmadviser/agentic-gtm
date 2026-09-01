"""No-key, wholly fictional acceptance workflow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..contracts import CampaignDraft, Experiment
from ..safety import make_plan


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
            {"day": 0, "channel": "email", "subject": "A specific operating question"},
            {"day": 4, "channel": "email", "subject": "Re: A specific operating question"},
        ],
        schedule={"timezone": "Europe/Berlin"},
        status="paused",
    )
    campaign_payload = {
        "desired_state": "paused",
        "campaign": {
            "name": draft.name,
            "schedule": draft.schedule,
            "steps": draft.steps,
        },
    }
    plan = make_plan(
        "campaign.create_paused",
        "lemlist",
        ["synthetic-audience"],
        campaign_payload,
        "Create one fictional campaign in paused state",
    )
    report = """# Synthetic weekly GTM review

## What changed

- A working ICP was drafted from fictional evidence.
- One experiment was preregistered; execution has not started.
- A paused campaign action plan was created but not applied.

## Risks

- Channel preference remains unknown.
- The sample is synthetic and must not be treated as company evidence.

## Next actions

- Demo Operator — review the hypothesis and denominator.
- Demo Operator — reject or explicitly apply a real plan only after connecting owned systems.
"""
    _write_json(output / "icp.json", icp)
    _write_json(output / "experiment.json", experiment.model_dump(mode="json"))
    _write_json(output / "campaign-plan.json", plan.model_dump(mode="json"))
    (output / "weekly-review.md").write_text(report, encoding="utf-8")
    return {
        "mode": "demo",
        "synthetic": True,
        "output": str(output),
        "artifacts": [
            "icp.json",
            "experiment.json",
            "campaign-plan.json",
            "weekly-review.md",
        ],
        "campaign_status": "paused",
        "external_writes": 0,
    }
