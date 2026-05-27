from app.publishers.publisher import PublishExecutionInput, PublishExecutionResult


class FakePublisherProvider:
    provider_name = "fake_publisher"
    provider_version = "0.1"

    def execute(self, input: PublishExecutionInput) -> PublishExecutionResult:
        return PublishExecutionResult(
            provider_name=self.provider_name,
            external_publication_id=f"fake-publication-{input.publication_record_id}",
            publication_status="succeeded",
            error_message=None,
        )
