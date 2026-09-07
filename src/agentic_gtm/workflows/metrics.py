"""Campaign metric maths shared by imports, syncs, and reviews.

Rates are computed here and only here so every report uses the same
denominators. The KPI hierarchy is: opportunities per 1k sent, meetings per
1k, positive replies per 1k, positive reply rate, reply rate. Opens are not a
metric and are not stored.
"""

from __future__ import annotations

import contextlib
import csv
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..contracts import CampaignMetrics

CSV_COLUMNS = [
    "provider",
    "campaign",
    "campaign_id",
    "kind",
    "unit",
    "variant",
    "window_start",
    "window_end",
    "sent",
    "delivered",
    "bounced",
    "replied",
    "positive_replies",
    "meetings",
    "opportunities",
]

BOUNCE_PAUSE_THRESHOLD = 0.02
POSITIVE_REPLY_GOOD = 0.01
POSITIVE_REPLY_GREAT = 0.02


def certainty(sent: int) -> str:
    if sent < 200:
        return "too_early"
    if sent < 500:
        return "directional"
    if sent < 2000:
        return "usable"
    return "solid"


def _parse_datetime(value: str) -> datetime:
    text = value.strip()
    if not text:
        raise ValueError("window_start and window_end are required (ISO date or datetime)")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def parse_metrics_csv(path: Path, default_provider: str = "import") -> list[CampaignMetrics]:
    rows: list[CampaignMetrics] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [
            column for column in ("campaign", "sent") if column not in (reader.fieldnames or [])
        ]
        if missing:
            raise ValueError(f"metrics CSV is missing required columns: {', '.join(missing)}")
        for line_number, raw in enumerate(reader, start=2):

            def number(key: str, row: dict[str, str] = raw) -> int | None:
                value = (row.get(key) or "").strip()
                return int(value) if value else (0 if key == "bounced" else None)

            delivered_raw = (raw.get("delivered") or "").strip()
            try:
                rows.append(
                    CampaignMetrics(
                        provider=(raw.get("provider") or default_provider).strip(),
                        campaign=raw["campaign"].strip(),
                        campaign_id=raw.get("campaign_id") or raw["campaign"].strip(),
                        kind=raw.get("kind") or "interval",
                        unit=raw.get("unit") or "email",
                        variant=(raw.get("variant") or "").strip(),
                        window_start=_parse_datetime(raw.get("window_start") or ""),
                        window_end=_parse_datetime(raw.get("window_end") or ""),
                        sent=number("sent"),
                        delivered=int(delivered_raw) if delivered_raw else None,
                        bounced=number("bounced"),
                        replied=number("replied"),
                        positive_replies=number("positive_replies"),
                        meetings=number("meetings"),
                        opportunities=number("opportunities"),
                        source="import",
                    )
                )
            except (KeyError, ValueError) as exc:
                raise ValueError(f"metrics CSV line {line_number}: {exc}") from exc
    return rows


def rates(
    sent: int,
    delivered: int,
    bounced: int,
    replied: int,
    positive: int,
    meetings: int,
    opportunities: int,
) -> dict[str, float | None]:
    def ratio(numerator: int, denominator: int) -> float | None:
        return round(numerator / denominator, 4) if denominator and numerator is not None else None

    def per_1k(numerator: int) -> float | None:
        return round(numerator / sent * 1000, 2) if sent and numerator is not None else None

    return {
        "bounce_rate": ratio(bounced, sent),
        "reply_rate": ratio(replied, delivered),
        "positive_reply_rate": ratio(positive, delivered),
        "positive_per_1k_sent": per_1k(positive),
        "meetings_per_1k_sent": per_1k(meetings),
        "opportunities_per_1k_sent": per_1k(opportunities),
    }


def summarize(metrics: list[CampaignMetrics]) -> dict[str, Any]:
    series = defaultdict(list)
    units = {row.unit for row in metrics}
    if len(units) > 1:
        raise ValueError("Metric units differ; review email, contact and account counts separately")
    for row in metrics:
        series[(row.provider, row.campaign_id, row.variant)].append(row)
    groups, names = {}, {}
    for key, observations in series.items():
        kinds = {row.kind for row in observations}
        if len(kinds) != 1:
            raise ValueError("Do not mix lifetime snapshots and intervals for the same campaign")
        observations.sort(key=lambda row: (row.window_end, row.observed_at))
        names[key] = observations[-1].campaign
        if observations[-1].kind == "cumulative":
            # A second sync is a newer observation, never additional sends.
            observations = observations[-1:]
        else:
            observations.sort(key=lambda row: row.window_start)
            for previous, current in zip(observations, observations[1:], strict=False):
                if current.window_start < previous.window_end:
                    raise ValueError("Metric intervals overlap; use disjoint half-open windows")
        bucket = dict(sent=0, delivered=0, bounced=0, replied=0, positive=0, meetings=0, opps=0)
        for row in observations:
            for field, value in {
                "sent": row.sent,
                "delivered": row.effective_delivered,
                "bounced": row.bounced,
                "replied": row.replied,
                "positive": row.positive_replies,
                "meetings": row.meetings,
                "opps": row.opportunities,
            }.items():
                bucket[field] = (
                    bucket[field] + value
                    if bucket[field] is not None and value is not None
                    else None
                )
        groups[key] = bucket

    rows = []
    totals = dict(sent=0, delivered=0, bounced=0, replied=0, positive=0, meetings=0, opps=0)
    for (provider, campaign_id, variant), bucket in sorted(groups.items()):
        campaign = names[(provider, campaign_id, variant)]
        for key in totals:
            totals[key] = (
                totals[key] + bucket[key]
                if totals[key] is not None and bucket[key] is not None
                else None
            )
        computed = rates(
            bucket["sent"],
            bucket["delivered"],
            bucket["bounced"],
            bucket["replied"],
            bucket["positive"],
            bucket["meetings"],
            bucket["opps"],
        )
        flags = []
        if computed["bounce_rate"] is not None and computed["bounce_rate"] > BOUNCE_PAUSE_THRESHOLD:
            flags.append("bounce_above_2pct_pause")
        if (
            bucket["sent"] >= 500
            and bucket["replied"] is not None
            and bucket["replied"] >= 20
            and bucket["opps"] == 0
            and bucket["meetings"] == 0
        ):
            flags.append("reply_vanity_trap")
        if computed["positive_reply_rate"] is not None and bucket["sent"] >= 200:
            if computed["positive_reply_rate"] >= POSITIVE_REPLY_GREAT:
                flags.append("positive_reply_great")
            elif computed["positive_reply_rate"] >= POSITIVE_REPLY_GOOD:
                flags.append("positive_reply_good")
        rows.append(
            {
                "provider": provider,
                "campaign": campaign,
                "campaign_id": campaign_id,
                "variant": variant,
                **bucket,
                **computed,
                "certainty": certainty(bucket["sent"]),
                "flags": flags,
            }
        )
    total_rates = rates(
        totals["sent"],
        totals["delivered"],
        totals["bounced"],
        totals["replied"],
        totals["positive"],
        totals["meetings"],
        totals["opps"],
    )
    ranked = sorted(
        (
            row
            for row in rows
            if row["certainty"] != "too_early"
            and all(row[field] is not None for field in ("opps", "meetings", "positive"))
        ),
        key=lambda row: (
            -(row["opportunities_per_1k_sent"] or 0),
            -(row["meetings_per_1k_sent"] or 0),
            -(row["positive_per_1k_sent"] or 0),
        ),
    )
    return {
        "scope": "Latest lifetime snapshot per cumulative series; all non-overlapping imported intervals",
        "unit": next(iter(units), "email"),
        "campaigns": rows,
        "totals": {**totals, **total_rates, "certainty": certainty(totals["sent"])},
        "ranking": [
            f"{row['campaign']}{' / ' + row['variant'] if row['variant'] else ''}" for row in ranked
        ],
        "kpi_hierarchy": [
            "opportunities_per_1k_sent",
            "meetings_per_1k_sent",
            "positive_per_1k_sent",
            "positive_reply_rate",
            "reply_rate",
        ],
    }


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.2f}%"


def _num(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def render_outreach_review(summary: dict[str, Any], generated: datetime) -> str:
    totals = summary["totals"]
    lines = [
        "# Outreach review",
        "",
        f"Generated: {generated.isoformat()}",
        "",
        "## Totals",
        "",
        f"- Sent: {totals['sent']} (sample size tier: {totals['certainty']})",
        f"- Scope: {summary.get('scope', 'Imported windows')}; unit: {summary.get('unit', 'email')}",
        "- Sample size tiers are heuristics, not statistical confidence or permission to scale.",
        f"- Bounce rate: {_pct(totals['bounce_rate'])}",
        f"- Reply rate (of delivered): {_pct(totals['reply_rate'])}",
        f"- Positive reply rate (of delivered): {_pct(totals['positive_reply_rate'])}",
        f"- Positive replies per 1k sent: {_num(totals['positive_per_1k_sent'])}",
        f"- Meetings per 1k sent: {_num(totals['meetings_per_1k_sent'])}",
        f"- Opportunities per 1k sent: {_num(totals['opportunities_per_1k_sent'])}",
        "",
        "## Per campaign and variant",
        "",
        "| Campaign | Variant | Sent | Bounce | Reply | Positive | Pos/1k | Mtg/1k | Opp/1k | Certainty | Flags |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in summary["campaigns"]:
        lines.append(
            f"| {row['campaign']} | {row['variant'] or '-'} | {row['sent']} | "
            f"{_pct(row['bounce_rate'])} | {_pct(row['reply_rate'])} | "
            f"{_pct(row['positive_reply_rate'])} | {_num(row['positive_per_1k_sent'])} | "
            f"{_num(row['meetings_per_1k_sent'])} | {_num(row['opportunities_per_1k_sent'])} | "
            f"{row['certainty']} | {', '.join(row['flags']) or '-'} |"
        )
    lines.extend(
        [
            "",
            "## Ranking (KPI hierarchy, campaigns with enough sends only)",
            "",
        ]
    )
    lines.extend(f"{index}. {name}" for index, name in enumerate(summary["ranking"], start=1))
    if not summary["ranking"]:
        lines.append(
            "- No campaign has both 200 sends and complete outcome counts. Do not rank missing data."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Compare each campaign only against its preregistered decision rule.",
            "- A high reply rate with zero meetings or opportunities is a reply-vanity trap: stop, do not scale.",
            "- Bounce above 2% pauses the sender or campaign before anything else is discussed.",
            "",
            "## Owners and next actions",
            "",
            "- Assign one human owner and a date to each action.",
        ]
    )
    return "\n".join(lines) + "\n"


def summarize_pipeline(opportunities: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, dict[str, float]] = {
        status: {"count": 0, "amount": 0.0} for status in ("won", "lost", "open")
    }
    for row in opportunities:
        status = str(row.get("status") or "open").lower()
        if status not in buckets:
            status = "open"
        buckets[status]["count"] += 1
        amount = row.get("amount")
        with contextlib.suppress(TypeError, ValueError):
            buckets[status]["amount"] += float(amount) if amount not in (None, "") else 0.0
    closed = buckets["won"]["count"] + buckets["lost"]["count"]
    win_rate = round(buckets["won"]["count"] / closed, 4) if closed else None
    return {"pipeline": buckets, "closed": closed, "win_rate": win_rate}


def render_pipeline_review(summary: dict[str, Any], generated: datetime) -> str:
    pipeline = summary["pipeline"]
    lines = [
        "# Pipeline review",
        "",
        f"Generated: {generated.isoformat()}",
        "",
        "## Won, lost, open (kept separate)",
        "",
        "| Status | Count | Amount |",
        "|---|---:|---:|",
    ]
    for status in ("won", "lost", "open"):
        lines.append(
            f"| {status} | {int(pipeline[status]['count'])} | {pipeline[status]['amount']:.2f} |"
        )
    lines.extend(
        [
            "",
            f"- Closed deals: {summary['closed']}",
            f"- Win rate (won / closed): {_pct(summary['win_rate'])}",
            "",
            "## Interpretation",
            "",
            "- Cut won and lost by employee band, geography, industry and source before believing any ICP claim.",
            "- Do not trust a cut with fewer than 10 closed deals.",
            "",
            "## Owners and next actions",
            "",
            "- Assign one human owner and a date to each action.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_weekly_review(
    outreach: dict[str, Any],
    pipeline: dict[str, Any],
    extras: dict[str, Any],
    generated: datetime,
) -> str:
    totals = outreach["totals"]
    buckets = pipeline["pipeline"]
    lines = [
        "# Weekly GTM review",
        "",
        f"Generated: {generated.isoformat()}",
        "",
        "## Current snapshot",
        "",
        "This is a review prepared this week, not a measured week-over-week delta.",
        f"Scope: {outreach.get('scope', 'Imported windows')}",
        "",
        f"- Outreach sent in scope: {totals['sent']} (certainty: {totals['certainty']})",
        f"- Positive replies per 1k sent: {_num(totals['positive_per_1k_sent'])}",
        f"- Meetings per 1k sent: {_num(totals['meetings_per_1k_sent'])}",
        f"- Opportunities per 1k sent: {_num(totals['opportunities_per_1k_sent'])}",
        f"- Pipeline: {int(buckets['won']['count'])} won, {int(buckets['lost']['count'])} lost, "
        f"{int(buckets['open']['count'])} open (win rate {_pct(pipeline['win_rate'])})",
        f"- Experiments on file: {extras.get('experiments', 0)}; "
        f"pending action plans: {extras.get('pending_plans', 'unknown')}",
        "",
        "## Evidence",
        "",
        "- Campaign ranking by KPI hierarchy: "
        + (", ".join(outreach["ranking"]) if outreach["ranking"] else "no campaign past 200 sends"),
        "- Flags: "
        + (
            "; ".join(
                f"{row['campaign']}: {', '.join(row['flags'])}"
                for row in outreach["campaigns"]
                if row["flags"]
            )
            or "none"
        ),
        "",
        "## Decisions needed",
        "",
        "- List each decision with the evidence line it rests on and the person who decides.",
        "",
        "## Risks",
        "",
        "- Interested leads without logged meetings is a process gap, not a copy problem.",
        "- Any bounce flag above pauses the sender before other work continues.",
        "",
        "## Owners and next actions",
        "",
        "- One owner, one date per action.",
    ]
    return "\n".join(lines) + "\n"
