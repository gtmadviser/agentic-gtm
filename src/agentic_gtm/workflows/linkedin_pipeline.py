"""Harvest voices -> posts -> engagement, with bounded, separately accepted stages."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4

import httpx
from filelock import FileLock
from pydantic import BaseModel, ConfigDict, Field

from ..config import credential, load_settings
from ..database import open_store
from ..enrichment import PaidCalls, PaidRun, fingerprint
from ..safety.artifacts import ignore_artifacts, private_run_directory
from ..safety.checkpoints import verify_review
from .linkedin_engagers import (
    BASE_URL,
    USER_AGENT,
    event_identity,
    linkedin_url,
    load_plan,
    normalize,
    post_url,
    read_json,
    write_json,
)
from .qualification import qualify

ENDPOINTS = {
    "discovery": {"post-search"},
    "employees": {"profile-search"},
    "posts": {"company-posts", "profile-posts"},
    "engagement": {"post-reactions", "post-comments"},
    "profiles": {"profile"},
    "companies": {"company"},
}

# Stages whose items are keyword queries rather than LinkedIn URLs.
QUERY_STAGES = {"discovery"}


def company_url(value: str) -> str:
    if "/company/" not in value:
        raise ValueError("Expected a LinkedIn company URL")
    checked = linkedin_url(value.replace("/company/", "/in/", 1), "profile")
    return checked.replace("/in/", "/company/", 1)


class CollectionSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stage: Literal["discovery", "employees", "posts", "engagement", "profiles", "companies"]
    client_id: str = Field(min_length=1)
    account_scope: str = Field(min_length=1)
    items: list[dict] = Field(min_length=1, max_length=1000)
    max_pages: int = Field(ge=1, le=100)
    max_calls: int = Field(ge=1, le=10000)
    max_records: int = Field(ge=1, le=100000)
    budget_microusd: int = Field(ge=1)
    prices_microusd: dict[str, int]
    price_basis: str = Field(min_length=1)
    cache_ttl_seconds: int = Field(default=3600, ge=1, le=604800)
    published_since: datetime | None = None
    published_until: datetime | None = None
    checkpoint: dict | None = None

    def checked(self):
        expected = ENDPOINTS[self.stage]
        if self.stage == "posts":
            expected = {
                "company-posts" if row.get("kind") == "company" else "profile-posts"
                for row in self.items
            }
        if set(self.prices_microusd) != expected:
            raise ValueError(
                f"Provide upper-bound prices for exactly these endpoints: {sorted(expected)}"
            )
        if any(type(price) is not int or price <= 0 for price in self.prices_microusd.values()):
            raise ValueError("Endpoint prices must be positive integers in micro-USD")
        if self.stage in ("posts", "discovery"):
            if not self.published_since or not self.published_until:
                raise ValueError(
                    "Post discovery requires explicit published_since and published_until"
                )
            if not self.published_since.tzinfo or not self.published_until.tzinfo:
                raise ValueError("Post window must include a timezone")
            if self.published_since >= self.published_until:
                raise ValueError("Post window must be increasing")
        seen = set()
        for row in self.items:
            if self.stage in QUERY_STAGES:
                query = (row.get("query") or "").strip()
                if not query:
                    raise ValueError("Discovery items need a non-empty query")
                row["query"] = query
                # post-search is fuzzy and matches unrelated senses of a word, so its
                # output is a review queue, never an approved source list.
                if row.get("approved") is True:
                    raise ValueError(
                        "Discovery output must be reviewed after collection; "
                        "do not pre-approve a search query"
                    )
                if query in seen:
                    raise ValueError("Duplicate discovery query; merge them before planning")
                seen.add(query)
                continue
            if self.stage in ("employees", "companies"):
                row["url"] = company_url(row["url"])
            elif self.stage == "profiles":
                row["url"] = linkedin_url(row["url"], "profile")
            elif self.stage == "engagement":
                row["url"] = post_url(row["url"])
                if not row.get("sources"):
                    raise ValueError("Every selected post must retain its source voices")
            else:
                if row.get("kind") not in ("company", "founder", "employee"):
                    raise ValueError("A voice must be company, founder or employee")
                row["url"] = (
                    company_url(row["url"])
                    if row["kind"] == "company"
                    else linkedin_url(row["url"], "profile")
                )
                if row.get("approved") is not True:
                    raise ValueError("Post sources require an explicitly reviewed roster")
                if row["kind"] == "employee" and row.get("membership") not in (
                    "core",
                    "core_multi",
                    "reviewed_exception",
                ):
                    raise ValueError(
                        "Employee sources require current-role evidence or a reviewed exception"
                    )
                if row["kind"] == "employee" and not row.get("membership_evidence"):
                    raise ValueError("Employee sources require membership_evidence")
            if row["url"] in seen:
                raise ValueError("Duplicate input URL; merge its provenance before planning")
            seen.add(row["url"])
        return self


def plan_collection(spec: dict, out: Path) -> dict:
    accepted = CollectionSpec.model_validate(spec).checked().model_dump(mode="json")
    payload = {"version": 2, "run_id": str(uuid4()), **accepted}
    if payload["stage"] == "engagement":
        payload["posts"] = [row["url"] for row in payload["items"]]
    private_run_directory(out)
    with FileLock(str(out / ".lock"), timeout=1):
        if (out / "plan.json").exists():
            raise ValueError("Run already exists; review its immutable plan or use a new directory")
        plan = {"payload": payload, "sha256": fingerprint(payload)}
        write_json(out / "plan.json", plan)
    return {
        "sha256": plan["sha256"],
        "stage": accepted["stage"],
        "items": len(accepted["items"]),
        "max_calls": accepted["max_calls"],
        "budget_microusd": accepted["budget_microusd"],
        "paid_calls": 0,
    }


def validate_response(data):
    if (
        not isinstance(data, dict)
        or str(data.get("status")) not in ("200", "success")
        or data.get("error")
    ):
        raise ValueError("Harvest returned an unsuccessful response")
    if not isinstance(data.get("elements"), list) and not isinstance(data.get("element"), dict):
        raise ValueError("Harvest response has no elements or element")


def collect_stage(
    run: Path, approval: str, store, client=None, workspace: Path | None = None
) -> dict:
    with FileLock(str(run / ".lock"), timeout=1):
        plan = load_plan(run)
        if plan["sha256"] != approval or plan["payload"].get("version") != 2:
            raise ValueError("Pass the exact reviewed version-2 plan hash")
        payload = plan["payload"]
        spec = CollectionSpec.model_validate(
            {k: v for k, v in payload.items() if k not in ("version", "run_id", "posts")}
        ).checked()
        if spec.checkpoint:
            verify_review(
                workspace or Path.cwd(),
                spec.checkpoint["record"],
                spec.checkpoint["accepted_hash"],
                spec.checkpoint["recipe_version"],
            )
        paid = PaidCalls(
            store,
            PaidRun(
                run_id=payload["run_id"],
                client_id=spec.client_id,
                account_scope=spec.account_scope,
                provider="harvest",
                plan_hash=approval,
                max_calls=spec.max_calls,
                budget_microusd=spec.budget_microusd,
                prices_microusd=spec.prices_microusd,
                price_basis=spec.price_basis,
            ),
        )
        own_client = client is None
        if own_client:
            client = httpx.Client(
                base_url=BASE_URL,
                headers={"X-API-Key": credential("HARVEST_API_KEY"), "User-Agent": USER_AGENT},
                timeout=60,
                follow_redirects=False,
            )
        pages = run / "pages"
        pages.mkdir(exist_ok=True)
        rows, quarantined, coverage = {}, [], []
        # max_records is budgeted per (source, endpoint) so that a high-volume endpoint
        # cannot starve a co-requested one. Reactions page at 100/page and comments at
        # 100/page: a shared counter let reactions consume the whole cap and leave the
        # higher-signal comments with zero pages.
        records: dict[tuple[str, str], int] = {}
        total_records = 0
        state = {
            "plan_hash": approval,
            "complete": False,
            "coverage": coverage,
            "stage": spec.stage,
            "replies_complete": False,
        }

        def fetch(endpoint, params):
            request_key = fingerprint([endpoint, params])
            path = pages / (request_key + ".json")
            if path.exists():
                saved = read_json(path)
                if saved.get("plan_hash") != approval:
                    raise ValueError("Local response belongs to another plan")
                return saved

            def request():
                response = client.get("/linkedin/" + endpoint, params=params)
                response.raise_for_status()
                return response.json()

            result = paid.call(
                endpoint,
                params,
                request,
                schema_version="harvest-2026-09-09",
                ttl_seconds=spec.cache_ttl_seconds,
                validate=validate_response,
            )
            saved = {
                "plan_hash": approval,
                "endpoint": endpoint,
                "params": params,
                "observed_at": result["observed_at"],
                "response": result["response"],
                "post_url": params.get("post"),
                "page": params.get("page", 1),
            }
            write_json(path, saved)
            return saved

        items = spec.items
        if spec.stage == "posts":
            items = sorted(
                items,
                key=lambda row: (
                    row.get("priority", {"founder": 0, "company": 1, "employee": 2}[row["kind"]]),
                    row["url"],
                ),
            )
        try:
            for item in items:
                if spec.stage == "discovery":
                    jobs = [("post-search", {"search": item["query"]})]
                elif spec.stage == "employees":
                    jobs = [("profile-search", {"currentCompany": item["url"]})]
                elif spec.stage == "posts":
                    jobs = (
                        [("company-posts", {"company": item["url"]})]
                        if item["kind"] == "company"
                        else [("profile-posts", {"profile": item["url"]})]
                    )
                elif spec.stage == "engagement":
                    jobs = [
                        ("post-reactions", {"post": item["url"]}),
                        ("post-comments", {"post": item["url"], "sortBy": "date"}),
                    ]
                elif spec.stage == "profiles":
                    jobs = [("profile", {"url": item["url"], "main": "true"})]
                else:
                    jobs = [("company", {"url": item["url"]})]
                source_key = item["query"] if spec.stage in QUERY_STAGES else item["url"]
                for endpoint, query in jobs:
                    status = {
                        "source_url": source_key,
                        "endpoint": endpoint,
                        "complete": False,
                        "pages": 0,
                    }
                    coverage.append(status)
                    budget_key = (source_key, endpoint)
                    records.setdefault(budget_key, 0)
                    page, token, signatures = 1, None, set()
                    while page <= spec.max_pages and records[budget_key] < spec.max_records:
                        params = {**query}
                        if spec.stage not in ("profiles", "companies"):
                            params["page"] = page
                        if token:
                            params["paginationToken"] = token
                        saved = fetch(endpoint, params)
                        data = saved["response"]
                        status["pages"] += 1
                        if spec.stage in ("profiles", "companies"):
                            rows[item["url"]] = {
                                **item,
                                "profile" if spec.stage == "profiles" else "company": data.get(
                                    "element", {}
                                ),
                                "observed_at": saved["observed_at"],
                            }
                            records[budget_key] += 1
                            total_records += 1
                            status["complete"] = True
                            break
                        elements = data.get("elements")
                        if not isinstance(elements, list):
                            raise ValueError("Paged endpoint did not return elements")
                        signature = fingerprint(elements)
                        if elements and signature in signatures:
                            raise ValueError("Repeated provider page; collection is incomplete")
                        signatures.add(signature)
                        for row in elements:
                            if records[budget_key] >= spec.max_records:
                                break
                            records[budget_key] += 1
                            total_records += 1
                            if spec.stage == "discovery":
                                stamp = (row.get("postedAt") or {}).get("timestamp")
                                if (
                                    not isinstance(stamp, (float, int))
                                    or isinstance(stamp, bool)
                                    or stamp <= 0
                                ):
                                    quarantined.append(
                                        {
                                            "reason": "missing_post_date",
                                            "source_query": item["query"],
                                            "record": row,
                                        }
                                    )
                                    continue
                                published = datetime.fromtimestamp(stamp / 1000, UTC)
                                if not spec.published_since <= published < spec.published_until:
                                    continue
                                try:
                                    url = post_url(row["linkedinUrl"])
                                except (KeyError, ValueError):
                                    quarantined.append(
                                        {
                                            "reason": "invalid_post_url",
                                            "source_query": item["query"],
                                            "record": row,
                                        }
                                    )
                                    continue
                                author = row.get("author") or {}
                                reactions = row.get("engagement", {}).get("reactions") or []
                                candidate = rows.setdefault(
                                    url,
                                    {
                                        "url": url,
                                        "published_at": published.isoformat(),
                                        "author_name": author.get("name"),
                                        "author_url": author.get("linkedinUrl"),
                                        "author_headline": author.get("position"),
                                        "author_type": (
                                            "company"
                                            if "/company/" in (author.get("linkedinUrl") or "")
                                            else "person"
                                        ),
                                        "reactions": sum(
                                            int(entry.get("count") or 0)
                                            for entry in reactions
                                            if isinstance(entry, dict)
                                        ),
                                        "comments": int(
                                            row.get("engagement", {}).get("comments") or 0
                                        ),
                                        "is_repost": bool(row.get("repost") or row.get("repostId")),
                                        "queries": [],
                                        # A fuzzy search hit is a candidate, never a source.
                                        # Review, then feed selected rows to the engagement
                                        # stage with explicit sources.
                                        "approved": False,
                                    },
                                )
                                if item["query"] not in candidate["queries"]:
                                    candidate["queries"].append(item["query"])
                            elif spec.stage == "posts":
                                stamp = (row.get("postedAt") or {}).get("timestamp")
                                if (
                                    not isinstance(stamp, (float, int))
                                    or isinstance(stamp, bool)
                                    or stamp <= 0
                                ):
                                    quarantined.append(
                                        {
                                            "reason": "missing_post_date",
                                            "source_url": item["url"],
                                            "record": row,
                                        }
                                    )
                                    continue
                                published = datetime.fromtimestamp(stamp / 1000, UTC)
                                if not spec.published_since <= published < spec.published_until:
                                    continue
                                url = post_url(row["linkedinUrl"])
                                post = rows.setdefault(
                                    url,
                                    {
                                        "url": url,
                                        "published_at": published.isoformat(),
                                        "sources": [],
                                        "is_repost": bool(row.get("repost") or row.get("repostId")),
                                    },
                                )
                                source = {
                                    "kind": item["kind"],
                                    "url": item["url"],
                                    "source_id": item.get("source_id", item["url"]),
                                }
                                if source not in post["sources"]:
                                    post["sources"].append(source)
                            elif spec.stage == "employees":
                                try:
                                    url = linkedin_url(row.get("linkedinUrl", ""), "profile")
                                    if row.get("name", "").lower() == "linkedin member":
                                        raise ValueError("Anonymous profile")
                                except ValueError:
                                    quarantined.append(
                                        {"reason": "missing_identity", "record": row}
                                    )
                                    continue
                                rows[url] = {
                                    "url": url,
                                    "provider_id": row.get("id"),
                                    "name": row.get("name"),
                                    "headline": row.get("position"),
                                    "company_url": item["url"],
                                    "membership": "review",
                                    "approved": False,
                                    "observed_at": saved["observed_at"],
                                }
                        pagination = data.get("pagination") or {}
                        if (
                            "totalPages" not in pagination
                            or int(pagination.get("pageNumber", page)) != page
                        ):
                            raise ValueError(
                                "Missing or inconsistent pagination; cannot claim completeness"
                            )
                        total = int(pagination["totalPages"])
                        if total < 0:
                            raise ValueError("Invalid pagination total")
                        if page >= total and records[budget_key] < spec.max_records:
                            status["complete"] = True
                            break
                        token = pagination.get("paginationToken")
                        page += 1
                    if not status["complete"]:
                        status["reason"] = (
                            "record_cap" if records[budget_key] >= spec.max_records else "page_cap"
                        )
            state["complete"] = all(row["complete"] for row in coverage)
        except Exception:
            state["stop_reason"] = "provider_or_budget_error; inspect ledger before resuming"
            raise
        finally:
            summary = paid.summary()
            state.update(
                requests=summary["requests"],
                reserved_microusd=summary["reserved_microusd"],
                cost_source="accepted_upper_bound",
                records_collected=total_records,
                max_records_per_source_endpoint=spec.max_records,
            )
            write_json(run / "state.json", state)
            if spec.stage != "engagement":
                collected = list(rows.values())
                if spec.stage == "discovery":
                    # Highest-reach candidates first so a reviewer reads the posts that
                    # actually carried the announcement before the long fuzzy tail.
                    collected.sort(
                        key=lambda row: (
                            -row.get("reactions", 0),
                            -row.get("comments", 0),
                            row["url"],
                        )
                    )
                write_json(run / f"{spec.stage}.json", collected)
            write_json(run / "discovery-quarantine.json", quarantined)
            if own_client:
                client.close()
        return state


def classify_roster(employees: list[dict], profiles: list[dict], company: str) -> list[dict]:
    target = company_url(company)
    indexed = {linkedin_url(row["url"], "profile"): row for row in profiles}
    result = []
    for employee in employees:
        row = {**employee, "membership": "review", "approved": False, "kind": "employee"}
        profile_row = indexed.get(row["url"], {})
        roles = profile_row.get("profile", {}).get("currentPosition")
        if isinstance(roles, list) and roles:
            matches, unknown_company = [], False
            for role in roles:
                try:
                    matches.append(company_url(role.get("companyLinkedinUrl", "")) == target)
                except ValueError:
                    matches.append(False)
                    unknown_company = True
            if len(roles) == 1 and matches[0]:
                row["membership"] = "core"
            elif not any(matches) and not unknown_company:
                row["membership"] = "not_current"
            # Multiple current roles remain review; array order does not prove primary work.
            row["membership_evidence"] = {
                "source_url": row["url"],
                "observed_at": profile_row.get("observed_at"),
                "current_roles": roles,
            }
        row["recommended"] = row["membership"] == "core"
        result.append(row)
    return result


def reconcile_seen(run: Path, ledger_path: Path) -> dict:
    events = read_json(run / "events.json")
    client_id = load_plan(run)["payload"].get("client_id")
    if not client_id:
        raise ValueError("Reconciliation requires a client-scoped version-2 run")
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ignore_artifacts(ledger_path, ledger_path.with_suffix(".tmp"), Path(str(ledger_path) + ".lock"))
    with FileLock(str(ledger_path) + ".lock", timeout=10):
        ledger = (
            read_json(ledger_path)
            if ledger_path.exists()
            else {"client_id": client_id, "events": {}}
        )
        if ledger["client_id"] != client_id:
            raise ValueError("Seen ledger belongs to another client")
        aliases = ledger.setdefault("aliases", {})

        def root(value):
            aliases.setdefault(value, value)
            if aliases[value] != value:
                aliases[value] = root(aliases[value])
            return aliases[value]

        people = read_json(run / "people.json")
        for person in people:
            keys = [person["person_id"]] + [
                value if value.startswith("https://") else "harvest:" + value
                for value in person["identity_aliases"]
            ]
            roots = {root(key) for key in keys}
            canonical = min(roots, key=lambda key: (not key.startswith("harvest:"), key))
            for key in roots:
                aliases[key] = canonical
        # Reindex old evidence when a newly verified alias supplies a stable provider ID.
        reindexed = {}
        for prior in ledger["events"].values():
            prior["person_id"] = root(prior["person_id"])
            prior["event_id"] = event_identity(prior)
            existing = reindexed.get(prior["event_id"])
            if existing:
                prior["first_seen_at"] = min(existing["first_seen_at"], prior["first_seen_at"])
                prior["observed_at"] = max(existing["observed_at"], prior["observed_at"])
            reindexed[prior["event_id"]] = prior
        ledger["events"] = reindexed
        fresh = []
        for event in events:
            event["person_id"] = root(event["person_id"])
            event["event_id"] = event_identity(event)
            prior = ledger["events"].get(event["event_id"])
            if prior:
                event["first_seen_at"] = min(prior["first_seen_at"], event["first_seen_at"])
                event["observed_at"] = max(prior["observed_at"], event["observed_at"])
            else:
                fresh.append(event)
            ledger["events"][event["event_id"]] = event
        fresh_path = run / "new-events.json"
        previous_fresh = read_json(fresh_path) if fresh_path.exists() else []
        fresh_by_id = {}
        for event in previous_fresh + fresh:
            event["person_id"] = root(event["person_id"])
            event["event_id"] = event_identity(event)
            fresh_by_id[event["event_id"]] = ledger["events"].get(event["event_id"], event)
        write_json(fresh_path, list(fresh_by_id.values()))
        write_json(ledger_path, ledger)
        write_json(run / "events.json", events)
    return {
        "new_events": len(read_json(fresh_path)),
        "seen_events": len(ledger["events"]),
        "paid_calls": 0,
    }


def export_review_sheet(run: Path, out: Path, qualified: Path | None = None) -> dict:
    """Join people + events into one review-ready row per person.

    people.csv flattens every interaction to the bare word "reaction" and carries no
    comment text, so it cannot be reviewed or handed on as a deliverable. This keeps the
    reaction type, the per-post detail and the verbatim comment, resolves the current
    role, and leaves the judgment columns blank: the rubric decides route, a human writes
    the rationale. Nothing here invents a reason a lead is a fit.
    """
    people = read_json(run / "people.json")
    events = read_json(run / "events.json")
    verdicts = {}
    if qualified:
        for row in read_json(qualified):
            key = row.get("person_id") or row.get("profile_url")
            if key:
                verdicts[key] = row
    by_person: dict[str, list[dict]] = {}
    for event in events:
        by_person.setdefault(event["person_id"], []).append(event)
    rows = []
    for person in people:
        mine = sorted(
            by_person.get(person["person_id"], []),
            key=lambda event: (event.get("post_url") or "", event.get("type") or ""),
        )
        detail, comments = [], []
        for event in mine:
            label = event.get("reaction_type") or event.get("type") or "unknown"
            detail.append(f"{label.lower()} on {event.get('post_url')}")
            text = (event.get("comment") or "").strip()
            if text:
                comments.append(" ".join(text.split()))
        roles = person.get("current_roles") or []
        role = roles[0] if isinstance(roles, list) and roles else {}
        verdict = verdicts.get(person["person_id"], {})
        rows.append(
            {
                "name": person.get("name"),
                "current_title": role.get("position") or "",
                "current_company": role.get("companyName") or "",
                "current_company_url": role.get("companyLinkedinUrl") or "",
                "headline": person.get("headline") or "",
                "profile_url": person.get("profile_url"),
                "num_posts": len(person.get("source_posts") or []),
                "num_comments": len(comments),
                "interactions": "; ".join(detail),
                "comments_verbatim": " || ".join(comments),
                "source_kinds": ", ".join(person.get("source_kinds") or []),
                "is_internal": person.get("is_internal", False),
                "role_verified": bool(role),
                "route": verdict.get("route", ""),
                "company_fit": verdict.get("company_fit", ""),
                "persona_fit": verdict.get("persona_fit", ""),
                # Deliberately blank: a human writes these after reading the evidence.
                "tier": "",
                "why_person": "",
                "why_company": "",
                "next_step": "",
            }
        )
    rows.sort(key=lambda row: (-row["num_comments"], -row["num_posts"], row["name"] or ""))
    ignore_artifacts(out)
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["name"])
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: (
                        "'" + value
                        if isinstance(value, str)
                        and value.startswith(("=", "+", "-", "@", "\t", "\r"))
                        else value
                    )
                    for key, value in row.items()
                }
            )
    return {
        "rows": len(rows),
        "with_comments": sum(row["num_comments"] > 0 for row in rows),
        "role_verified": sum(row["role_verified"] for row in rows),
        "internal_excluded": sum(row["is_internal"] for row in rows),
        "out": str(out),
        "paid_calls": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan")
    plan.add_argument("--spec", type=Path, required=True)
    plan.add_argument("--items", type=Path, help="Snapshot selected rows from a prior stage")
    plan.add_argument("--out", type=Path, required=True)
    plan.add_argument("--checkpoint", type=Path)
    plan.add_argument("--accepted-hash")
    plan.add_argument("--recipe-version")
    plan.add_argument("--workspace", type=Path, default=Path("."))
    fetch = commands.add_parser("fetch")
    fetch.add_argument("--run", type=Path, required=True)
    fetch.add_argument("--approve", required=True)
    fetch.add_argument("--config", type=Path, default=Path("gtm.yaml"))
    normal = commands.add_parser("normalize")
    normal.add_argument("--run", type=Path, required=True)
    normal.add_argument("--profiles", type=Path)
    normal.add_argument("--internal-roster", type=Path)
    roster = commands.add_parser("roster")
    roster.add_argument("--employees", type=Path, required=True)
    roster.add_argument("--profiles", type=Path, required=True)
    roster.add_argument("--company", required=True)
    roster.add_argument("--out", type=Path, required=True)
    seen = commands.add_parser("reconcile")
    seen.add_argument("--run", type=Path, required=True)
    seen.add_argument("--ledger", type=Path, required=True)
    qualification = commands.add_parser(
        "qualify", help="Apply an evidence rubric and relationship guards offline"
    )
    qualification.add_argument("--people", type=Path, required=True)
    qualification.add_argument("--rubric", type=Path, required=True)
    qualification.add_argument("--out", type=Path, required=True)
    sheet = commands.add_parser(
        "export", help="Join people + events into a review-ready CSV deliverable"
    )
    sheet.add_argument("--run", type=Path, required=True)
    sheet.add_argument("--out", type=Path, required=True)
    sheet.add_argument(
        "--qualified", type=Path, help="Optional qualify output to merge routes from"
    )
    args = parser.parse_args()
    try:
        if args.command == "plan":
            spec = read_json(args.spec)
            if args.items:
                spec["items"] = read_json(args.items)
            if args.checkpoint:
                record = read_json(args.checkpoint)
                verify_review(args.workspace, record, args.accepted_hash, args.recipe_version)
                spec["checkpoint"] = {
                    "record": record,
                    "accepted_hash": args.accepted_hash,
                    "recipe_version": args.recipe_version,
                }
            result = plan_collection(spec, args.out)
        elif args.command == "fetch":
            if load_plan(args.run)["sha256"] != args.approve:
                raise ValueError("Pass the exact reviewed plan hash")
            settings = load_settings(args.config)
            result = collect_stage(
                args.run,
                args.approve,
                open_store(settings, quiet=True),
                workspace=settings.workspace_root,
            )
        elif args.command == "normalize":
            result = normalize(args.run, args.profiles, args.internal_roster)
        elif args.command == "export":
            result = export_review_sheet(args.run, args.out, args.qualified)
        elif args.command == "roster":
            rows = classify_roster(
                read_json(args.employees), read_json(args.profiles), args.company
            )
            ignore_artifacts(args.out, args.out.with_suffix(".tmp"))
            write_json(args.out, rows)
            result = {
                "people": len(rows),
                "recommended": sum(row["recommended"] for row in rows),
                "paid_calls": 0,
            }
        elif args.command == "qualify":
            rubric = read_json(args.rubric)
            rows = [qualify(row, rubric) for row in read_json(args.people)]
            ignore_artifacts(args.out, args.out.with_suffix(".tmp"))
            write_json(args.out, rows)
            result = {
                "people": len(rows),
                "outreach_drafts": sum(row["route"] == "outreach_draft" for row in rows),
                "paid_calls": 0,
            }
        else:
            result = reconcile_seen(args.run, args.ledger)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, RuntimeError, httpx.HTTPError) as exc:
        message = (
            "Harvest request failed; inspect local state and ledger"
            if isinstance(exc, httpx.HTTPError)
            else str(exc)
        )
        parser.exit(1, message + "\n")


if __name__ == "__main__":
    main()
