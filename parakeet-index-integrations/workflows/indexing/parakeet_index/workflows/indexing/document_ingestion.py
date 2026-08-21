from parakeet_index.core.bridge.pydantic import BaseModel, Field
from parakeet_index.core.components import TransformerComponent
from parakeet_index.core.docstore import BaseDocStore
from parakeet_index.core.document import Document
from parakeet_index.core.loaders import BaseLoader
from parakeet_index.core.utils.validation import validate_enum
from parakeet_index.core.vector_stores import BaseVectorStore
from parakeet_index.core.workflows import Context, StartEvent, StopEvent, Workflow, step
from parakeet_index.workflows.indexing.enums import DocStrategy
from parakeet_index.workflows.indexing.events import (
    DocumentsDeduplicatedEvent,
    DocumentsLoadedEvent,
    DocumentsTransformedEvent,
)

# ============================================================================
# Workflow State
# ============================================================================


class WorkflowState(BaseModel):
    """State for document ingestion workflow."""

    input_documents: list[Document] = Field(
        default_factory=list, description="Input documents"
    )
    processed_documents: list[Document] = Field(
        default_factory=list, description="Final processed documents"
    )


# ============================================================================
# Document Ingestion Workflow
# ============================================================================


class DocumentIngestionWorkflow(Workflow):
    """
    A document ingestion workflow for processing and storing documents.

    This workflow orchestrates the document ingestion pipeline with support for:
    - Multiple document loaders (e.g., Docx, PDF, S3)
    - Multiple transformation components (e.g., chunking, embedding)
    - Deduplication strategies (requires ``doc_store`` to be configured)
    - Vector store integration

    Attributes:
        transformers (list[TransformerComponent]): Transformer components applied to input documents.
        loaders (list[BaseLoader]): Loaders for fetching documents.
        vector_store (BaseVectorStore, optional): Vector store for storing processed documents.
        doc_strategy (str, optional): Strategy for handling duplicate documents. Defaults to ``incremental``.
        doc_store (BaseDocStore, optional): Document store for deduplication index. If not provided,
            deduplication is skipped regardless of ``doc_strategy``.

    Example:
        ```python
        from parakeet_workflows.prebuilt import DocumentIngestionWorkflow

        from parakeet_index.core.text_chunkers import TokenTextChunker
        from parakeet_index.docstore.sqlite import SQLiteDocStore
        from parakeet_index.embeddings.huggingface import HuggingFaceEmbedding


        ingestion_workflow = DocumentIngestionWorkflow(
            transformers=[
                TokenTextChunker(),
                HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-small"),
            ],
            doc_store=SQLiteDocStore(db_path="./my-index.db"),
        )

        result = await ingestion_workflow.run(documents=[doc1, doc2])
        ```
    """

    def __init__(
        self,
        transformers: list[TransformerComponent],
        doc_strategy: str = DocStrategy.INCREMENTAL,
        doc_store: BaseDocStore | None = None,
        loaders: list[BaseLoader] | None = None,
        vector_store: BaseVectorStore | None = None,
    ) -> None:
        validate_enum(
            el=doc_strategy, el_name="doc_strategy", expected_enum=DocStrategy
        )

        self.transformers = transformers
        self.loaders = loaders or []
        self.vector_store = vector_store
        self.doc_strategy = doc_strategy
        self.doc_store = doc_store

    @step(when=StartEvent)
    async def load_documents(
        self, ctx: Context[WorkflowState], ev: StartEvent
    ) -> DocumentsLoadedEvent:
        """
        Load documents.

        This step collects documents from all configured loaders and
        any documents passed directly to the workflow.
        """
        input_documents = []

        documents = ev.get("documents", [])
        if documents:
            input_documents.extend(documents)

        for loader in self.loaders:
            input_documents.extend(loader.load_data())

        async with ctx.store.edit_state() as state:
            state.input_documents = input_documents

        return DocumentsLoadedEvent(documents=input_documents)

    @step(when=DocumentsLoadedEvent)
    async def deduplicate_before_transform(
        self, ctx: Context[WorkflowState], ev: DocumentsLoadedEvent
    ) -> DocumentsDeduplicatedEvent | DocumentsTransformedEvent:
        """
        Apply deduplication at parent document level before transformation.

        Parent documents that pass deduplication are immediately persisted to
        the doc_store so future runs can detect them as already indexed.
        """
        documents = ev.documents

        if (
            self.doc_store is not None
            and self.doc_strategy != DocStrategy.DEDUPLICATE_OFF
        ):
            documents = self._handle_duplicates(documents)

            # Persist accepted parent documents to the doc_store index
            if documents:
                self.doc_store.upsert_documents(documents)

            return DocumentsDeduplicatedEvent(documents=documents)
        else:
            return DocumentsTransformedEvent(documents=documents)

    @step(when=DocumentsDeduplicatedEvent)
    async def transform_documents(
        self, ctx: Context[WorkflowState], ev: DocumentsDeduplicatedEvent
    ) -> DocumentsTransformedEvent:
        """Applies all configured transformers in sequence."""
        documents = ev.documents

        if documents:
            documents = self._run_transformers(documents, self.transformers)

        return DocumentsTransformedEvent(documents=documents)

    @step(when=DocumentsTransformedEvent)
    async def save_documents(
        self, ctx: Context[WorkflowState], ev: DocumentsTransformedEvent
    ) -> StopEvent:
        """
        Finalize document processing.

        Saves transformed chunks to the vector store.
        The doc_store is NOT updated here — parent documents were already
        persisted in ``deduplicate_before_transform``.
        """
        documents = ev.documents

        if self.vector_store is not None and documents:
            self.vector_store.add_documents(documents)

        async with ctx.store.edit_state() as state:
            state.processed_documents = documents

        return StopEvent(result=documents)

    def _handle_duplicates(self, documents: list[Document]) -> list[Document]:
        if self.doc_store is None:
            return documents

        seen_hashes_in_batch: set[str] = set()
        dedup_documents: list[Document] = []

        for doc in documents:
            if doc.get_content() == "" or doc.hash in seen_hashes_in_batch:
                continue

            stored_hash = self.doc_store.get_document_hash(doc.id_)
            if stored_hash == doc.hash:
                continue

            dedup_documents.append(doc)
            seen_hashes_in_batch.add(doc.hash)

        # Handle FULL strategy — remove indexed docs not in current batch
        if self.doc_strategy == DocStrategy.FULL:
            incoming_ids = {doc.id_ for doc in documents}
            ids_to_remove = [
                indexed_doc.id_
                for indexed_doc in self.doc_store.list_documents()
                if indexed_doc.id_ not in incoming_ids
            ]

            if ids_to_remove:
                if self.vector_store is not None:
                    self.vector_store.delete_documents(ids_to_remove)
                self.doc_store.delete_documents(ids_to_remove)

        return dedup_documents

    def _run_transformers(
        self,
        documents: list[Document],
        transformers: list[TransformerComponent],
    ) -> list[Document]:
        _documents = documents.copy()

        for transformer in transformers:
            _documents = transformer(_documents)

        return _documents
