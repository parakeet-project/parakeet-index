from abc import abstractmethod

from parakeet_index.core.components import BaseComponent
from parakeet_index.core.document import Document


class BaseDocStore(BaseComponent):
    """Abstract base class defining the interface for document store."""

    model_config = {
        "arbitrary_types_allowed": True,
        "validate_assignment": True,
        "validate_default": True,
    }

    @classmethod
    def class_name(cls) -> str:
        return "BaseDocStore"

    @abstractmethod
    def upsert_documents(self, documents: list[Document]) -> None:
        """
        Insert or update document records.

        Args:
            documents: List of root documents to insert or update, keyed by
                their ``id_``. Existing records with a matching Id are
                overwritten.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the upsert_documents() method"
        )

    @abstractmethod
    def list_documents(self) -> list[Document]:
        """
        Return all documents currently stored, including text.

        Returns:
            List of documents.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the list_documents() method"
        )

    @abstractmethod
    def delete_documents(self, ids: list[str]) -> None:
        """
        Delete records by document Id.

        Args:
            ids: List of document Ids to delete.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the delete_documents() method"
        )

    @abstractmethod
    def get_document_hash(self, doc_id: str) -> str | None:
        """
        Get the stored hash for a single document, if it exists.

        Used for incremental change detection: compare the returned hash
        against a newly computed one to decide whether a document needs
        re-chunking, without fetching its full text.

        Args:
            doc_id: Id of the document to look up.

        Returns:
            The stored SHA256 hash, or None if the document is not indexed.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the get_document_hash() method"
        )

    @abstractmethod
    def get_document(self, doc_id: str) -> Document | None:
        """
        Return a single document record by Id, including text.

        Used for incremental re-chunking: fetch the stored text of a root
        document to re-chunk it after a content change.

        Args:
            doc_id: Id of the document to retrieve.

        Returns:
            The document, or None if not found.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the get_document() method"
        )
