class DocStrategy:
    """
    Document deduplication strategies, based on comparing document hashes
    against the configured ``doc_store``. Require a ``doc_store`` to be set.
    Otherwise deduplication is skipped regardless of the strategy chosen.
    """

    DEDUPLICATE_OFF = "deduplicate_off"
    """Always index every document, never checking the doc_store."""

    INCREMENTAL = "incremental"
    """Index only new or changed documents; preserve everything already indexed."""

    FULL = "full"
    """Index only new or changed documents, and delete indexed documents that are no longer in the current batch."""
