import uuid
from abc import abstractmethod

from parakeet_index.core.bridge.pydantic import Field
from parakeet_index.core.components import BaseComponent
from parakeet_index.core.document import Document
from parakeet_index.core.instrumentation import DispatcherSpanMixin, get_dispatcher
from parakeet_index.core.instrumentation.events.loader import (
    LoaderEndEvent,
    LoaderStartEvent,
)

dispatcher = get_dispatcher(__name__)


class BaseLoader(BaseComponent, DispatcherSpanMixin):
    """Abstract base class defining the interface for document loader."""

    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "forbid",
        "validate_assignment": True,
        "validate_default": True,
    }

    @classmethod
    def class_name(cls) -> str:
        """Returns the class name of the loader."""
        return "BaseLoader"

    @abstractmethod
    def _load_data(self) -> list[Document]:
        """Loads data and returns a list of documents."""

    @dispatcher.span
    def load_data(self) -> list[Document]:
        """Loads data and returns a list of documents."""
        config_dict = self.to_dict(exclude={"api_key"})
        dispatcher.event(
            LoaderStartEvent(
                config_dict=config_dict,
            )
        )

        documents = self._load_data()

        dispatcher.event(
            LoaderEndEvent(
                documents=documents,
            )
        )
        return documents


class BaseFileLoader(BaseLoader):
    """
    Abstract base class defining the interface for file-based document loaders.

    Attributes:
        input_file (str): File path to load.
    """

    input_file: str = Field(
        ...,
        description="File path to load",
    )

    @classmethod
    def class_name(cls) -> str:
        """Returns the class name of the loader."""
        return "BaseFileLoader"

    @staticmethod
    def _stable_id(*args: str) -> str:
        """Determine a stable, deterministic id (uuid5) from identity components."""
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, ":".join(args)))
