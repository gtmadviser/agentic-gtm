import json

import pytest

from agentic_gtm.safety.checkpoints import review_record, verify_review
from agentic_gtm.starter import health, upgrade_plan
from agentic_gtm.workspace import initialize_workspace


def test_local_artifacts_preserve_workspace_ignore_rules(tmp_path):
    import subprocess

    from agentic_gtm.safety.artifacts import ignore_artifacts, private_run_directory

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text(".env\n!important.json\n")
    artifact = tmp_path / "review [one].json"
    ignore_artifacts(artifact, artifact.with_suffix(".tmp"))
    assert (tmp_path / ".gitignore").read_text().startswith(".env\n!important.json\n")
    result = subprocess.run(
        ["git", "check-ignore", "--", artifact.name], cwd=tmp_path, capture_output=True
    )
    assert result.returncode == 0
    assert subprocess.run(
        ["git", "check-ignore", "--", "new-code.py"], cwd=tmp_path, capture_output=True
    ).returncode == 1
    with pytest.raises(ValueError, match="dedicated"):
        private_run_directory(tmp_path)


def test_starter_upgrade_preserves_customizations(tmp_path):
    workspace, candidate = tmp_path / "workspace", tmp_path / "candidate"
    initialize_workspace(workspace)
    initialize_workspace(candidate)
    assert health(workspace)["managed"] and not health(workspace)["files"]
    (workspace / "context/company.md").write_text("Client-authored context")
    (candidate / "context/company.md").write_text("New generated context")
    from agentic_gtm.starter import digest

    manifest = json.loads((candidate / ".generated.json").read_text())
    manifest["files"]["context/company.md"] = digest(candidate / "context/company.md")
    (candidate / ".generated.json").write_text(json.dumps(manifest))
    plan = upgrade_plan(workspace, candidate)
    assert plan["changes"][0]["status"] == "conflict" and plan["applied"] is False
    initialize_workspace(workspace)
    assert (workspace / "context/company.md").read_text() == "Client-authored context"


def test_sample_acceptance_invalidates_on_input_or_version_change(tmp_path):
    (tmp_path / "sample.json").write_text('{"synthetic": true}')
    record = review_record(tmp_path, ["sample.json"], "recipe-1", "Synthetic reviewer")
    verify_review(tmp_path, record, record["sha256"], "recipe-1")
    with pytest.raises(ValueError, match="changed"):
        verify_review(tmp_path, record, record["sha256"], "recipe-2")
    (tmp_path / "sample.json").write_text('{"synthetic": false}')
    with pytest.raises(ValueError, match="changed"):
        verify_review(tmp_path, record, record["sha256"], "recipe-1")


def test_manifest_paths_cannot_escape_workspace(tmp_path):
    (tmp_path / ".generated.json").write_text(
        json.dumps({"source_version": "1", "files": {"../outside": "hash"}})
    )
    with pytest.raises(ValueError, match="outside"):
        health(tmp_path)
