from abc import abstractmethod

from parakeet_index.core.components import TransformerComponent
from parakeet_index.core.document import Document
from parakeet_index.core.instrumentation import DispatcherSpanMixin, get_dispatcher
from parakeet_index.core.instrumentation.events.text_chunker import (
    TextChunkerEndEvent,
    TextChunkerStartEvent,
)

dispatcher = get_dispatcher(__name__)


class BaseTextChunker(TransformerComponent, DispatcherSpanMixin):
    """Abstract base class defining the interface for text chunker."""

    model_config = {
        "arbitrary_types_allowed": True,
        "validate_assignment": True,
        "validate_default": True,
    }

    @classmethod
    def class_name(cls) -> str:
        return "BaseTextChunker"

    @abstractmethod
    def _get_text_chunks(self, text: str) -> list[str]:
        """Split a single string of text into smaller chunks."""

    @dispatcher.span
    def get_text_chunks(self, text: str) -> list[str]:
        """
        Split a single string of text into smaller chunks.

        Args:
            text (str): Input text to split.
        """
        config_dict = self.to_dict(exclude={"api_key"})
        dispatcher.event(
            TextChunkerStartEvent(
                config_dict=config_dict,
            )
        )

        chunks = self._get_text_chunks(text)

        dispatcher.event(
            TextChunkerEndEvent(
                chunks=chunks,
            )
        )
        return chunks

    @dispatcher.span
    def get_document_chunks(self, documents: list[Document]) -> list[Document]:
        """
        Split a list of documents into smaller document chunks.

        Args:
            documents (list[Document]): Documents to split.
        """
        config_dict = self.to_dict(exclude={"api_key"})
        dispatcher.event(
            TextChunkerStartEvent(
                config_dict=config_dict,
            )
        )
        chunked_documents = []

        for document in documents:
            texts = self._get_text_chunks(document.get_content())
            metadata = {**document.metadata}

            for text in texts:
                chunked_documents.append(
                    Document(
                        text=text,
                        metadata=metadata,
                        ref_doc_id=document.id_,
                    ),
                )

        dispatcher.event(
            TextChunkerEndEvent(
                chunks=chunked_documents,
            )
        )
        return chunked_documents

    def __call__(self, documents: list[Document]) -> list[Document]:
        return self.get_document_chunks(documents)
