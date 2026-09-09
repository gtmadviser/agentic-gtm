"""File-backed store: CSV tables plus JSON plans under `.gtm/store/`.

This is the no-database path. Records live in one CSV per table so they open in
a spreadsheet or upload to any enrichment tool. Nested values are JSON-encoded
inside the cell. Action plans and apply results are one JSON file each so the
plan hash is never touched by CSV quoting. The directory is gitignored; it holds
contacts and provider IDs and must never be committed.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
from uuid import UUID

from filelock import FileLock

from ..contracts import ActionPlan, ApplyResult
from ..safety.plans import assert_plan_can_apply
from .base import TABLES

DEFAULT_ROOT = Path(".gtm") / "store"
_JSON_PREFIX = "json:"


def _encode(value: Any) -> str:
    if value is None:
        return "json:null"
    if isinstance(value, (dict, list, bool, int, float)) or (
        isinstance(value, str) and (value == "" or value.startswith(_JSON_PREFIX))
    ):
        return _JSON_PREFIX + json.dumps(value, sort_keys=True, default=str)
    return str(value)


def _decode(value: str) -> Any:
    if value == "":
        return None  # Legacy CSV null; new empty strings are explicitly JSON encoded.
    if value.startswith(_JSON_PREFIX):
        return json.loads(value[len(_JSON_PREFIX) :])
    return value


def _matches(row: dict[str, Any], filters: dict[str, str]) -> bool:
    for key, expression in filters.items():
        if key in {"select", "limit", "order"}:
            continue
        if expression.startswith("eq."):
            if str(row.get(key, "")) != expression[3:]:
                return False
        elif expression.startswith("in."):
            wanted = expression[3:].strip("()").split(",")
            if str(row.get(key, "")) not in wanted:
                return False
    return True


class FileStore:
    backend = "files"

    def __init__(self, root: Path | str = DEFAULT_ROOT) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = FileLock(str(self.root / ".store.lock"), timeout=10)
        (self.root / "plans").mkdir(exist_ok=True)
        (self.root / "apply-results").mkdir(exist_ok=True)
        gitignore = self.root / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n", encoding="utf-8")

    # -- tables -----------------------------------------------------------------

    def _path(self, table: str) -> Path:
        if table not in TABLES:
            raise ValueError(f"Unknown table {table!r}. Known tables: {', '.join(TABLES)}")
        return self.root / f"{table}.csv"

    def _read(self, table: str) -> list[dict[str, Any]]:
        if table in {"action_plans", "apply_results"}:
            folder = "plans" if table == "action_plans" else "apply-results"
            return [
                json.loads(path.read_text(encoding="utf-8"))
                for path in sorted((self.root / folder).glob("*.json"))
            ]
        path = self._path(table)
        if not path.exists():
            return []
        with path.open(newline="", encoding="utf-8") as handle:
            return [
                {key: _decode(value) for key, value in row.items()}
                for row in csv.DictReader(handle)
            ]

    def _write(self, table: str, rows: list[dict[str, Any]]) -> None:
        path = self._path(table)
        columns: list[str] = []
        for row in rows:
            for key in row:
                if key not in columns:
                    columns.append(key)
        tmp = path.with_suffix(".csv.tmp")
        with tmp.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: _encode(row.get(key)) for key in columns})
        tmp.replace(path)

    def upsert(
        self, table: str, records: list[dict[str, Any]], on_conflict: str
    ) -> list[dict[str, Any]]:
        if not records:
            return []
        with self.lock:
            keys = [key.strip() for key in on_conflict.split(",") if key.strip()]
            existing = self._read(table)
            index = {
                tuple(str(row.get(key, "")) for key in keys): position
                for position, row in enumerate(existing)
            }
            for record in records:
                identity = tuple(str(record.get(key, "")) for key in keys)
                if identity in index:
                    previous = existing[index[identity]]
                    existing[index[identity]] = {**previous, **record}
                    if "id" not in keys and previous.get("id"):
                        existing[index[identity]]["id"] = previous["id"]
                else:
                    index[identity] = len(existing)
                    existing.append(dict(record))
            self._write(table, existing)
            return [
                existing[index[tuple(str(record.get(key, "")) for key in keys)]]
                for record in records
            ]

    def select(self, table: str, params: dict[str, str] | None = None) -> list[dict[str, Any]]:
        params = params or {}
        rows = [row for row in self._read(table) if _matches(row, params)]
        limit = params.get("limit")
        return rows[: int(limit)] if limit else rows

    # -- plans ------------------------------------------------------------------

    def _save_json(self, path: Path, content: str) -> None:
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)

    def create_plan(self, plan: ActionPlan) -> ActionPlan:
        sealed = plan.sealed()
        with self.lock:
            for row in self._read("action_plans"):
                if row["idempotency_key"] == sealed.idempotency_key:
                    return ActionPlan.model_validate(row)
            path = self.root / "plans" / f"{sealed.id}.json"
            if path.exists():
                raise ValueError("Plan ID already exists; immutable plans cannot be overwritten")
            self._save_json(path, sealed.model_dump_json(indent=2))
        return sealed

    def claim_apply(self, plan_id: UUID | str) -> ActionPlan:
        with self.lock:
            plan = self.get_plan(plan_id)
            assert_plan_can_apply(plan)
            self._save_json(
                self.root / "plans" / f"{plan.id}.json",
                plan.model_copy(update={"status": "applying"}).model_dump_json(indent=2),
            )
            return plan

    def mark_needs_review(self, plan_id: UUID | str) -> None:
        with self.lock:
            plan = self.get_plan(plan_id)
            if plan.status == "applying":
                self._save_json(
                    self.root / "plans" / f"{plan.id}.json",
                    plan.model_copy(update={"status": "needs_review"}).model_dump_json(indent=2),
                )

    def get_plan(self, plan_id: UUID | str) -> ActionPlan:
        path = self.root / "plans" / f"{plan_id}.json"
        if not path.exists():
            raise LookupError(f"Action plan {plan_id} was not found in {self.root}")
        return ActionPlan.model_validate_json(path.read_text(encoding="utf-8"))

    def record_apply(self, result: ApplyResult) -> ApplyResult:
        with self.lock:
            prior = self.applied_result(result.plan_id)
            if prior:
                return prior
            path = self.root / "apply-results" / f"{result.plan_id}.json"
            # Write the result first. A crash before the status update still prevents replay.
            self._save_json(path, result.model_dump_json(indent=2))
            plan = self.get_plan(result.plan_id)
            status = "needs_review" if result.status == "rejected" else "applied"
            self._save_json(
                self.root / "plans" / f"{plan.id}.json",
                plan.model_copy(update={"status": status}).model_dump_json(indent=2),
            )
        return result

    def applied_result(self, plan_id: UUID | str) -> ApplyResult | None:
        path = self.root / "apply-results" / f"{plan_id}.json"
        if not path.exists():
            return None
        return ApplyResult.model_validate_json(path.read_text(encoding="utf-8"))

    # -- introspection ----------------------------------------------------------

    def enrichment_rpc(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        from ..enrichment import file_operation

        path = self.root / "enrichment-state.json"
        with self.lock:
            state = json.loads(path.read_text()) if path.exists() else {}
            result = file_operation(state, operation, payload)
            if operation != "inspect":
                self._save_json(path, json.dumps(state, sort_keys=True, allow_nan=False))
            return result

    def describe(self) -> dict[str, Any]:
        counts = {table: len(self._read(table)) for table in TABLES if self._path(table).exists()}
        return {
            "backend": self.backend,
            "root": str(self.root),
            "tables": counts,
            "pending_plans": sum(row["status"] == "pending" for row in self._read("action_plans")),
        }
