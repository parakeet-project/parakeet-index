from typing import Any

from parakeet_index.core.document import Document


def doc_to_metadata_dict(document: Document) -> dict[str, Any]:
    """
    Build the metadata dict to persist alongside a document in a vector store.

    Merges the document's own metadata with reserved tracking fields (currently
    just ref_doc_id) needed to recover the parent/child relationship after
    storage. Reserved keys are omitted when unset, since most vector store
    backends (e.g. Chroma) reject None as a metadata value.

    Args:
        document: The document (typically a chunk) being persisted.

    Returns:
        A flat metadata dict safe to hand to a vector store backend.
    """
    metadata = {**document.metadata}

    if document.ref_doc_id is not None:
        metadata["ref_doc_id"] = document.ref_doc_id

    return metadata
