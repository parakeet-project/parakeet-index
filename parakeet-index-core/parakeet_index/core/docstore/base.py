from abc import abstractmethod

from parakeet_index.core.components import BaseComponent


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
    def upsert(self, doc_id: str, doc_hash: str, text: str) -> None:
        """
        Insert or update a document record.

        The DocStore holds only root (parent) documents — never chunks.
        Chunks are stored in the vector store with a ``parent_doc_id`` field
        pointing back to the root document.

        Args:
            doc_id: Unique Id of the document.
            doc_hash: SHA256 hash of the document text content.
            text: Full text content (enables incremental re-chunking in the future).
        """

    @abstractmethod
    def get_all(self) -> list[dict]:
        """
        Return all records without text content (lightweight for dedup/delete).

        Returns:
            List of dicts with keys: doc_id, doc_hash.
        """

    @abstractmethod
    def delete(self, doc_ids: list[str]) -> None:
        """
        Delete records by document Id.

        Args:
            doc_ids: List of document Ids to delete.
        """

    @abstractmethod
    def exists_hashes(self, hashes: list[str]) -> set[str]:
        """
        Return the subset of the given hashes that already exist in the store.

        Used for deduplication: only hashes returned by this method indicate
        documents already indexed. The query is performed against an index on
        doc_hash for efficiency.

        Args:
            hashes: List of SHA256 hashes to check.

        Returns:
            Set of hashes from the input that are already present in the store.
        """

    @abstractmethod
    def get_by_doc_id(self, doc_id: str) -> dict | None:
        """
        Return a single document record by Id, including text.

        Used for incremental re-chunking: fetch the stored text of a root
        document to re-chunk it after a content change.

        Args:
            doc_id: Id of the document to retrieve.

        Returns:
            Dict with keys doc_id, doc_hash, text, or None if not found.
        """
