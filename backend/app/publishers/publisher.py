from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PublishExecutionInput:
    project_id: int
    publish_intent_id: int
    publication_record_id: int
    target_platform: str
    title: str
    caption: str


@dataclass(frozen=True)
class PublishExecutionResult:
    provider_name: str
    external_publication_id: str | None
    publication_status: str
    error_message: str | None = None


class PublisherProvider(Protocol):
    provider_name: str
    provider_version: str

    def execute(self, input: PublishExecutionInput) -> PublishExecutionResult:
        ...
