from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MetricsReviewSnapshot:
    captured_at: str
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    favorites: int | None = None
    average_watch_time_seconds: float | None = None
    completion_rate: float | None = None


@dataclass(frozen=True)
class MetricsReviewSummaryResult:
    source: str
    is_fake_local: bool
    summary_text: str
    highlights: str
    low_performance_signals: str
    next_observations: str
    snapshot_count: int
    metric_window_start: str | None
    metric_window_end: str | None


class FakeMetricsReviewSummaryGenerator:
    generator_name = "fake_metrics_review_summary"
    generator_version = "0.1"
    source = "fake_local"

    def generate(self, snapshots: list[MetricsReviewSnapshot]) -> MetricsReviewSummaryResult:
        ordered_snapshots = sorted(snapshots, key=lambda snapshot: snapshot.captured_at)
        if not ordered_snapshots:
            return MetricsReviewSummaryResult(
                source=self.source,
                is_fake_local=True,
                summary_text=(
                    "No fake/local metric snapshots are available yet for this PublicationRecord. "
                    "This summary is only a local review placeholder, not real platform analysis."
                ),
                highlights="No metrics highlights yet because no fake/local snapshots were found.",
                low_performance_signals="No low-performance signals yet because no fake/local snapshots were found.",
                next_observations=(
                    "Generate or import a fake/local metric snapshot before using this record for manual review."
                ),
                snapshot_count=0,
                metric_window_start=None,
                metric_window_end=None,
            )

        first = ordered_snapshots[0]
        latest = ordered_snapshots[-1]
        snapshot_count = len(ordered_snapshots)
        latest_views = _format_metric(latest.views, "views")
        latest_likes = _format_metric(latest.likes, "likes")
        latest_comments = _format_metric(latest.comments, "comments")
        latest_completion = _format_percent(latest.completion_rate)
        latest_watch_time = _format_seconds(latest.average_watch_time_seconds)

        summary_text = (
            f"Fake/local review summary based on {snapshot_count} metric snapshot(s). "
            f"Latest snapshot shows {latest_views}, {latest_likes}, {latest_comments}, "
            f"completion rate {latest_completion}, and average watch time {latest_watch_time}. "
            "Use this only as a manual review reference; it is not real platform analysis."
        )
        highlights = self._build_highlights(ordered_snapshots)
        low_performance_signals = self._build_low_performance_signals(latest)
        next_observations = self._build_next_observations(ordered_snapshots)

        return MetricsReviewSummaryResult(
            source=self.source,
            is_fake_local=True,
            summary_text=summary_text,
            highlights=highlights,
            low_performance_signals=low_performance_signals,
            next_observations=next_observations,
            snapshot_count=snapshot_count,
            metric_window_start=first.captured_at,
            metric_window_end=latest.captured_at,
        )

    def _build_highlights(self, snapshots: list[MetricsReviewSnapshot]) -> str:
        latest = snapshots[-1]
        candidates: list[tuple[str, Any]] = [
            ("views", latest.views),
            ("likes", latest.likes),
            ("comments", latest.comments),
            ("shares", latest.shares),
            ("favorites", latest.favorites),
        ]
        available = [f"{name}={value}" for name, value in candidates if value is not None]
        if latest.completion_rate is not None:
            available.append(f"completion_rate={_format_percent(latest.completion_rate)}")
        if latest.average_watch_time_seconds is not None:
            available.append(f"average_watch_time={_format_seconds(latest.average_watch_time_seconds)}")
        if not available:
            return "Snapshots exist, but no comparable metric values are available yet."

        if len(snapshots) == 1:
            return f"Latest fake/local snapshot baseline: {', '.join(available)}."

        first = snapshots[0]
        trend_notes = _build_delta_notes(first, latest)
        if trend_notes:
            return f"Latest fake/local snapshot: {', '.join(available)}. Window changes: {', '.join(trend_notes)}."
        return f"Latest fake/local snapshot: {', '.join(available)}. No numeric trend changes are available."

    def _build_low_performance_signals(self, latest: MetricsReviewSnapshot) -> str:
        signals: list[str] = []
        if latest.views is not None and latest.views < 150:
            signals.append("views below the local fake baseline of 150")
        if latest.likes is not None and latest.views not in (None, 0) and latest.likes / latest.views < 0.08:
            signals.append("like rate below 8% of fake/local views")
        if latest.comments is not None and latest.views not in (None, 0) and latest.comments / latest.views < 0.02:
            signals.append("comment rate below 2% of fake/local views")
        if latest.completion_rate is not None and latest.completion_rate < 0.5:
            signals.append("completion rate below 50%")
        if latest.average_watch_time_seconds is not None and latest.average_watch_time_seconds < 10:
            signals.append("average watch time below 10 seconds")
        if not signals:
            return "No low-performance signals were detected from the available fake/local metrics."
        return "; ".join(signals) + "."

    def _build_next_observations(self, snapshots: list[MetricsReviewSnapshot]) -> str:
        latest = snapshots[-1]
        missing = [
            name
            for name, value in [
                ("views", latest.views),
                ("likes", latest.likes),
                ("comments", latest.comments),
                ("shares", latest.shares),
                ("favorites", latest.favorites),
                ("average_watch_time_seconds", latest.average_watch_time_seconds),
                ("completion_rate", latest.completion_rate),
            ]
            if value is None
        ]
        if missing:
            return (
                "Manually review the next fake/local snapshot for missing fields: "
                f"{', '.join(missing)}. Do not auto-modify topics, scripts, or content plans."
            )
        return (
            "Compare the next fake/local snapshot against this window before making any manual content judgment. "
            "Do not auto-modify topics, scripts, or content plans."
        )


def _format_metric(value: int | None, label: str) -> str:
    if value is None:
        return f"missing {label}"
    return f"{value} {label}"


def _format_percent(value: float | None) -> str:
    if value is None:
        return "missing"
    return f"{round(value * 100, 1)}%"


def _format_seconds(value: float | None) -> str:
    if value is None:
        return "missing"
    return f"{round(value, 1)}s"


def _build_delta_notes(first: MetricsReviewSnapshot, latest: MetricsReviewSnapshot) -> list[str]:
    notes: list[str] = []
    for label, first_value, latest_value in [
        ("views", first.views, latest.views),
        ("likes", first.likes, latest.likes),
        ("comments", first.comments, latest.comments),
        ("shares", first.shares, latest.shares),
        ("favorites", first.favorites, latest.favorites),
    ]:
        if first_value is not None and latest_value is not None:
            notes.append(f"{label} {latest_value - first_value:+d}")
    if first.completion_rate is not None and latest.completion_rate is not None:
        notes.append(f"completion_rate {round((latest.completion_rate - first.completion_rate) * 100, 1):+g}pp")
    if first.average_watch_time_seconds is not None and latest.average_watch_time_seconds is not None:
        notes.append(
            "average_watch_time "
            f"{round(latest.average_watch_time_seconds - first.average_watch_time_seconds, 1):+g}s"
        )
    return notes
