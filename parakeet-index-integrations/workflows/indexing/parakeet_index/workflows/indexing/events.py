from parakeet_index.core.bridge.pydantic import Field
from parakeet_index.core.document import Document
from parakeet_index.core.workflows import Event


class DocumentsLoadedEvent(Event):
    """Event when documents are loaded."""

    documents: list[Document] = Field(
        default_factory=list, description="Loaded documents"
    )


class DocumentsDeduplicatedEvent(Event):
    """Event after deduplication."""

    documents: list[Document] = Field(
        default_factory=list, description="Deduplicated documents"
    )


class DocumentsTransformedEvent(Event):
    """Event after transformation."""

    documents: list[Document] = Field(
        default_factory=list, description="Transformed documents"
    )
