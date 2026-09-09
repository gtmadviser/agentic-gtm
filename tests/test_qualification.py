from datetime import datetime

from agentic_gtm.workflows.qualification import qualify
from scripts.evaluate_skills import cases, grade


def test_synthetic_relationship_and_qualification_cases():
    fixture, inputs = cases()
    outputs = {
        case: qualify(
            row,
            fixture["rubric"],
            now=datetime.fromisoformat(fixture["now"].replace("Z", "+00:00")),
        )
        for case, row in inputs
    }
    assert grade(outputs)["failures"] == []
    assert outputs["unknown-size"]["company_fit"]["status"] == "review"
    assert outputs["wrong-persona"]["company_fit"]["status"] == "fit"
    assert outputs["wrong-persona"]["persona_fit"]["status"] == "not_fit"


def test_grader_rejects_missing_cases_and_unsafe_actions():
    result = grade(
        {
            "eligible": {
                "route": "outreach_draft",
                "enrollment_ready": True,
                "external_actions": ["send"],
            }
        }
    )
    assert result["failures"]
    assert any(failure.get("field") == "external_actions" for failure in result["failures"])


def test_missing_owner_fields_and_undated_evidence_stay_unknown():
    fixture, inputs = cases()
    row = inputs[0][1]
    now = datetime.fromisoformat(fixture["now"].replace("Z", "+00:00"))
    del row["checks"]["account_owner"]
    assert qualify(row, fixture["rubric"], now=now)["route"] == "hold"
    row["checks"]["account_owner"] = None
    row["criteria"]["company_size"]["evidence"][0]["observed_at"] = "not-a-date"
    result = qualify(row, fixture["rubric"], now=now)
    assert result["company_fit"]["status"] == "review" and result["route"] == "hold"
