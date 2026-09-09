"""Grade saved skill outputs or run deterministic qualification guards. No model/API calls."""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime
from pathlib import Path

from agentic_gtm.enrichment import fingerprint
from agentic_gtm.workflows.qualification import qualify

ROOT = Path(__file__).resolve().parents[1] / "evals/linkedin-engager-outreach"


def merge(base, patch):
    result = copy.deepcopy(base)
    for key, value in patch.items():
        result[key] = merge(result.get(key, {}), value) if isinstance(value, dict) else value
    return result


def cases():
    fixture = json.loads((ROOT / "fixtures.json").read_text())
    return fixture, [
        (case["id"], merge(fixture["base_person"], case["overrides"])) for case in fixture["cases"]
    ]


def grade(outputs):
    expected = json.loads((ROOT / "expected.json").read_text())
    failures = []
    for case, assertions in expected.items():
        actual = outputs.get(case, {})
        for key, value in assertions.items():
            if actual.get(key) != value:
                failures.append(
                    {"case": case, "field": key, "expected": value, "actual": actual.get(key)}
                )
    unexpected = sorted(set(outputs) - set(expected))
    if unexpected:
        failures.append({"unexpected_cases": unexpected})
    failed_cases = {failure.get("case") for failure in failures}
    return {
        "cases": len(expected),
        "passed": len(expected) - len(failed_cases - {None}),
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results", type=Path, help="Saved case-id -> structured output JSON from an agent run"
    )
    parser.add_argument(
        "--metadata", type=Path, help="Saved skill commit, model ID, settings and run timestamp"
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    fixture, inputs = cases()
    if args.results:
        if not args.metadata:
            parser.error("Agent runs require --metadata with revision/model/settings provenance")
        metadata = json.loads(args.metadata.read_text())
        if not all(metadata.get(key) for key in ("skill_commit", "model", "settings", "run_at")):
            parser.error("Incomplete run provenance")
        outputs = json.loads(args.results.read_text())
        mode = "saved_agent_outputs"
    else:
        outputs = {
            case: qualify(
                row,
                fixture["rubric"],
                now=datetime.fromisoformat(fixture["now"].replace("Z", "+00:00")),
            )
            for case, row in inputs
        }
        mode, metadata = "deterministic_guards", {}
    result = {
        "mode": mode,
        "fixture_hash": fingerprint(fixture),
        "metadata": metadata,
        **grade(outputs),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["failures"]))


if __name__ == "__main__":
    main()
