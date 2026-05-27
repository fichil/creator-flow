from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class MetricsSnapshotInput:
    project_id: int
    publish_intent_id: int
    publication_record_id: int
    target_platform: str
    provider_name: str
    publication_status: str


@dataclass(frozen=True)
class MetricsSnapshotResult:
    source: str
    views: int | None
    likes: int | None
    comments: int | None
    shares: int | None
    favorites: int | None
    average_watch_time_seconds: float | None
    completion_rate: float | None
    provider_payload_summary: str


class MetricsProvider(Protocol):
    provider_name: str
    provider_version: str

    def collect(self, input: MetricsSnapshotInput) -> MetricsSnapshotResult:
        ...
