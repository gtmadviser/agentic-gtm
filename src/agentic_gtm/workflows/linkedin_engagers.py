"""Bounded Harvest post collection and offline normalization. MIT licensed."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit

import httpx
from filelock import FileLock

from ..safety.artifacts import private_run_directory

BASE_URL = "https://api.harvestapi.io"
USER_AGENT = "Mozilla/5.0 (compatible; AgenticGTM/1.0; +https://github.com/gtmadviser/agentic-gtm)"


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def linkedin_url(value, kind):
    parsed = urlsplit(value)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not (host == "linkedin.com" or host.endswith(".linkedin.com")):
        raise ValueError("Expected an HTTPS LinkedIn URL")
    if parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("Unexpected URL credentials or port")
    path = unquote(parsed.path).rstrip("/")
    if kind == "profile":
        if not re.fullmatch(r"/in/[^/]+", path):
            raise ValueError("Not a person profile")
        return "https://www.linkedin.com" + path
    match = re.search(r"(?:urn:li:|[-/])(activity|ugcPost|share)[:-](\d+)", path)
    if not match or not path.startswith(("/feed/update/", "/posts/")):
        raise ValueError("Expected a LinkedIn post URL containing its post ID")
    return f"https://www.linkedin.com/feed/update/urn:li:{match[1]}:{match[2]}/"


def post_url(value):
    if re.fullmatch(r"urn:li:(activity|ugcPost|share):\d+", value):
        return "https://www.linkedin.com/feed/update/" + value + "/"
    return linkedin_url(value, "post")


def event_identity(event):
    discriminator = "" if event["type"] == "reaction" else event.get("provider_event_id") or event.get("comment") or ""
    return digest([event["person_id"], event["post_url"], event["type"], discriminator])


def create_plan(out, posts, max_pages, max_calls):
    if not 1 <= max_pages <= 100 or not 1 <= max_calls <= 1000:
        raise ValueError("Use 1..100 pages and 1..1000 requests per approved run")
    posts = sorted({post_url(post) for post in posts})
    if not posts:
        raise ValueError("At least one explicit post is required")
    private_run_directory(out)
    with FileLock(str(out / ".lock"), timeout=1):
        if (out / "plan.json").exists():
            raise ValueError("Run already exists; use its cached plan or a new run directory")
        payload = {"version": 1, "posts": posts, "max_pages": max_pages, "max_calls": max_calls}
        plan = {"payload": payload, "sha256": digest(payload)}
        write_json(out / "plan.json", plan)
    return {**plan, "maximum_requests": min(len(posts) * 2 * max_pages, max_calls), "paid_calls": 0}


def load_plan(run):
    plan = read_json(run / "plan.json")
    if digest(plan["payload"]) != plan["sha256"]:
        raise ValueError("Plan changed; create and review a new plan")
    return plan


def collect(run, approval, client=None):
    with FileLock(str(run / ".lock"), timeout=1):
        plan = load_plan(run)
        if approval != plan["sha256"]:
            raise ValueError("Pass the exact reviewed plan hash with --approve")
        policy = plan["payload"]
        state_path = run / "state.json"
        state = (
            read_json(state_path)
            if state_path.exists()
            else {
                "plan_hash": approval,
                "requests": 0,
                "pending": None,
            }
        )
        if state["plan_hash"] != approval:
            raise ValueError("State belongs to another plan")
        cache = run / "pages"
        cache.mkdir(exist_ok=True)
        pending = state.get("pending")
        if pending and not (cache / (pending + ".json")).exists():
            raise ValueError(
                "Previous request is uncertain. Reconcile provider usage before a newly approved run."
            )
        state["pending"] = None
        own_client = client is None
        if own_client:
            key = os.environ.get("HARVEST_API_KEY", "").strip()
            if not key:
                raise ValueError("HARVEST_API_KEY is missing from this process environment")
            client = httpx.Client(
                base_url=BASE_URL,
                headers={
                    "X-API-Key": key,
                    "User-Agent": USER_AGENT,
                },
                timeout=60,
                follow_redirects=False,
            )
        coverage = []
        try:
            for post in policy["posts"]:
                for endpoint in ("post-reactions", "post-comments"):
                    page, token, complete = 1, None, False
                    fingerprints = set()
                    while page <= policy["max_pages"]:
                        key = digest([post, endpoint, page])
                        path = cache / (key + ".json")
                        if path.exists():
                            saved = read_json(path)
                        else:
                            if state["requests"] >= policy["max_calls"]:
                                break
                            state.update(requests=state["requests"] + 1, pending=key)
                            write_json(state_path, state)
                            params = {"post": post, "page": page}
                            if endpoint == "post-comments":
                                params["sortBy"] = "date"
                            if token:
                                params["paginationToken"] = token
                            try:
                                response = client.get("/linkedin/" + endpoint, params=params)
                                response.raise_for_status()
                                data = response.json()
                                if str(data.get("status")) not in ("200", "success") or data.get(
                                    "error"
                                ):
                                    raise ValueError("Provider returned an unsuccessful response")
                                if not isinstance(data.get("elements"), list):
                                    raise ValueError("Provider response has no elements array")
                            except (httpx.HTTPError, ValueError) as exc:
                                raise ValueError(
                                    "Harvest request failed; reserved usage retained, no automatic retry"
                                ) from exc
                            saved = {
                                "post_url": post,
                                "endpoint": endpoint,
                                "page": page,
                                "observed_at": datetime.now(UTC).isoformat(),
                                "response": data,
                            }
                            write_json(path, saved)
                            state["pending"] = None
                            write_json(state_path, state)
                        data = saved["response"]
                        fingerprint = digest(data["elements"])
                        if fingerprint in fingerprints and data["elements"]:
                            raise ValueError("Provider repeated a page; collection is incomplete")
                        fingerprints.add(fingerprint)
                        pagination = data.get("pagination") or {}
                        if "totalPages" not in pagination:
                            raise ValueError(
                                "Missing pagination metadata; cannot claim complete collection"
                            )
                        if int(pagination.get("pageNumber", page)) != page:
                            raise ValueError(
                                "Provider returned the wrong page; collection is incomplete"
                            )
                        total_pages = int(pagination["totalPages"])
                        if total_pages < 0:
                            raise ValueError("Invalid totalPages")
                        if page >= total_pages:
                            complete = True
                            break
                        token = pagination.get("paginationToken")
                        page += 1
                    coverage.append({"post_url": post, "endpoint": endpoint, "complete": complete})
            state["coverage"] = coverage
            state["complete"] = all(item["complete"] for item in coverage)
            state["replies_complete"] = False
            write_json(state_path, state)
            return state
        finally:
            if own_client:
                client.close()


def normalize(run, profiles_path=None, internal_roster=None):
    with FileLock(str(run / ".lock"), timeout=1):
        plan = load_plan(run)
        records, rejected = [], []
        aliases = {}
        metadata = {item["url"]: item for item in plan["payload"].get("items", [])}
        profiles = read_json(profiles_path) if profiles_path else []
        internal = {row["url"] for row in read_json(internal_roster)} if internal_roster else set()
        for item in metadata.values():
            internal.update(source["url"] for source in item.get("sources", []) if source.get("kind") in ("founder", "employee"))

        def root(key):
            aliases.setdefault(key, key)
            if aliases[key] != key:
                aliases[key] = root(aliases[key])
            return aliases[key]

        def flatten(items, kind):
            for item in items:
                yield item, kind
                replies = item.get("replies") or []
                if isinstance(replies, dict):
                    replies = replies.get("elements", [])
                yield from flatten(replies, "reply")

        for profile in profiles:
            raw = profile.get("profile", {})
            values = [profile.get("url"), raw.get("linkedinUrl")]
            if raw.get("publicIdentifier"):
                values.append("https://www.linkedin.com/in/" + raw["publicIdentifier"])
            keys = []
            if raw.get("id"):
                keys.append("harvest:" + str(raw["id"]))
            for value in values:
                if value:
                    keys.append(linkedin_url(value, "profile"))
            for key in keys[1:]:
                aliases[root(key)] = root(keys[0])

        # max_records is budgeted per (post, endpoint), matching how collect_stage spends
        # it. A shared counter here would discard records the fetch stage legitimately
        # paid for, silently dropping commenters behind high-volume reactions.
        cap = plan["payload"].get("max_records", float("inf"))
        counts: dict[tuple[str, str], int] = {}
        record_count = 0
        capped = False
        for path in sorted((run / "pages").glob("*.json")):
            page = read_json(path)
            if page["post_url"] not in plan["payload"]["posts"]:
                raise ValueError("Cached page is outside the approved post list")
            kind = "reaction" if page["endpoint"] == "post-reactions" else "comment"
            budget_key = (page["post_url"], page["endpoint"])
            counts.setdefault(budget_key, 0)
            for item, event_kind in flatten(page["response"]["elements"], kind):
                if counts[budget_key] >= cap:
                    capped = True
                    break
                counts[budget_key] += 1
                record_count += 1
                actor = item.get("actor") or {}
                if actor.get("author") is True:
                    continue
                raw_url = actor.get("linkedinUrl") or ""
                if "/company/" in raw_url:
                    continue
                try:
                    url = linkedin_url(raw_url, "profile") if raw_url else ""
                except ValueError:
                    rejected.append({"reason": "invalid_profile_url", "actor": actor})
                    continue
                person_id = str(actor.get("id") or "")
                if not person_id and not url:
                    rejected.append({"reason": "missing_identity", "actor": actor})
                    continue
                if str(actor.get("name", "")).lower() == "linkedin member":
                    rejected.append({"reason": "anonymous_profile", "actor": actor})
                    continue
                keys = (["harvest:" + person_id] if person_id else []) + ([url] if url else [])
                for key in keys[1:]:
                    aliases[root(key)] = root(keys[0])
                records.append((keys[0], actor, url, item, event_kind, page))
        people, events = {}, {}
        resolved = {root(profile["url"]): profile for profile in profiles}
        for key, actor, url, item, kind, page in records:
            profile_row = resolved.get(root(key), {})
            profile = profile_row.get("profile", {})
            resolved_url = profile.get("linkedinUrl")
            if not resolved_url and profile.get("publicIdentifier"):
                resolved_url = "https://www.linkedin.com/in/" + profile["publicIdentifier"]
            if resolved_url:
                resolved_url = linkedin_url(resolved_url, "profile")
            person = people.setdefault(
                root(key),
                {
                    "person_id": root(key),
                    "name": actor.get("name") or "",
                    "profile_url": resolved_url or url,
                    "headline": actor.get("position") or "",
                    "source_posts": set(),
                    "interactions": set(),
                    "identity_aliases": set(),
                    "source_voices": set(),
                    "source_kinds": set(),
                    "is_internal": False,
                    "current_roles": profile.get("currentPosition") or [],
                },
            )
            person["source_posts"].add(page["post_url"])
            person["interactions"].add(kind)
            sources = metadata.get(page["post_url"], {}).get("sources", [])
            person["source_voices"].update(source["url"] for source in sources)
            person["source_kinds"].update(source["kind"] for source in sources)
            person["is_internal"] = person["is_internal"] or any(root(value) == root(key) for value in internal)
            person["identity_aliases"].update(
                value for value in [url, resolved_url, profile_row.get("url"), str(actor.get("id") or ""), str(profile.get("id") or "")] if value
            )
            observed = page["observed_at"]
            event = {
                "person_id": root(key),
                "post_url": page["post_url"],
                "type": kind,
                "reaction_type": item.get("reactionType"),
                "comment": item.get("commentary"),
                "engaged_at": item.get("createdAtTimestamp"),
                "first_seen_at": observed,
                "observed_at": observed,
                "sources": sources,
                "post_published_at": metadata.get(page["post_url"], {}).get("published_at"),
                "provider_event_id": item.get("id"),
            }
            event_id = event_identity(event)
            event["event_id"] = event_id
            if event_id in events:
                event["first_seen_at"] = min(events[event_id]["first_seen_at"], observed)
                event["observed_at"] = max(events[event_id]["observed_at"], observed)
            events[event_id] = event
        rows = []
        for person in sorted(people.values(), key=lambda row: row["person_id"]):
            person["num_sources"] = len(person["source_voices"])
            rows.append(
                {
                    key: sorted(value) if isinstance(value, set) else value
                    for key, value in person.items()
                }
            )
        write_json(run / "events.json", sorted(events.values(), key=lambda row: row["event_id"]))
        write_json(run / "people.json", rows)
        write_json(run / "quarantine.json", rejected)
        with (run / "people.csv").open("w", encoding="utf-8", newline="") as handle:
            columns = [
                "person_id",
                "name",
                "profile_url",
                "headline",
                "source_posts",
                "interactions",
                "identity_aliases",
                "source_voices",
                "source_kinds",
                "num_sources",
                "is_internal",
                "current_roles",
            ]
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                # Prevent spreadsheet formulas; JSON remains the lossless representation.
                writer.writerow(
                    {
                        key: (
                            "'" + value
                            if isinstance(value, str)
                            and value.startswith(("=", "+", "-", "@", "\t", "\r"))
                            else json.dumps(value)
                            if isinstance(value, list)
                            else value
                        )
                        for key, value in row.items()
                    }
                )
        state = read_json(run / "state.json") if (run / "state.json").exists() else {}
        return {
            "people": len(rows),
            "events": len(events),
            "quarantined": len(rejected),
            "collection_complete": state.get("complete", False) and not capped,
            "replies_complete": False,
            "paid_calls": 0,
            "raw_data": "local_only",
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="Offline, bounded collection plan")
    plan.add_argument("--post", action="append", required=True)
    plan.add_argument("--max-pages", type=int, required=True)
    plan.add_argument("--max-calls", type=int, required=True)
    plan.add_argument("--out", type=Path, required=True)
    fetch = commands.add_parser("fetch", help="Apply an approved paid collection plan")
    fetch.add_argument("--run", type=Path, required=True)
    fetch.add_argument("--approve", required=True)
    normal = commands.add_parser("normalize", help="Offline deduplication of cached pages")
    normal.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "plan":
            result = create_plan(args.out, args.post, args.max_pages, args.max_calls)
        elif args.command == "fetch":
            result = collect(args.run, args.approve)
        else:
            result = normalize(args.run)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
