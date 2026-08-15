class DocStrategy:
    """
    Document de-duplication strategies work by comparing the hashes in the vector store.
    They require a vector store to be set.
    """

    DEDUPLICATE_OFF = "deduplicate_off"
    DUPLICATE_ONLY = "duplicate_only"
    DUPLICATE_AND_DELETE = "duplicate_and_delete"