from parakeet_index.core.document import DocumentWithScore
from parakeet_index_instrumentation.events import BaseEvent


class RetrievalStartEvent(BaseEvent):
    """
    RetrievalStartEvent.

    Args:
        query: (str) The query string to search for similar documents.
        config_dict (dict): Retrieval model.
    """

    query: str
    config_dict: dict

    @classmethod
    def class_name(cls) -> str:
        return "RetrievalStartEvent"


class RetrievalEndEvent(BaseEvent):
    """
    RetrievalEndEvent.

    Args:
        documents (list[DocumentWithScore]): List of documents with scores.
    """

    documents: list[DocumentWithScore]

    @classmethod
    def class_name(cls) -> str:
        return "RetrievalEndEvent"
