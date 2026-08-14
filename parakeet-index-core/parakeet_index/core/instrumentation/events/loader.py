from parakeet_index.core.document import Document
from parakeet_index_instrumentation.events import BaseEvent


class LoaderStartEvent(BaseEvent):
    """
    LoaderStartEvent.

    Args:
        config_dict (dict): Retrieval model.
    """

    config_dict: dict

    @classmethod
    def class_name(cls) -> str:
        return "LoaderStartEvent"


class LoaderEndEvent(BaseEvent):
    """
    LoaderEndEvent.

    Args:
        documents (Document): List of documents.
    """

    documents: list[Document]

    @classmethod
    def class_name(cls) -> str:
        return "LoaderEndEvent"
