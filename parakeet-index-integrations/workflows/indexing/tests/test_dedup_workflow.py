import hashlib
from pathlib import Path

import pytest
from parakeet_index.core.document import Document
from parakeet_index.core.embeddings import BaseEmbedding
from parakeet_index.core.text_chunkers import TokenTextChunker
from parakeet_index.docstore.sqlite import SQLiteDocStore
from parakeet_index.loaders.file import PdfLoader
from parakeet_index.vector_stores.chroma import ChromaVectorStore
from parakeet_index.workflows.indexing import DocumentIngestionWorkflow
from parakeet_index.workflows.indexing.enums import DocStrategy

PDF_PATH = Path(__file__).parents[4] / "faq_banking_test.pdf"


class FakeEmbedding(BaseEmbedding):
    """Deterministic, local, hash-based embedding — no model download or network call."""

    model_name: str = "fake-embedding"
    dimensions: int = 8

    def _get_text_embeddings(self, input: str | list[str]) -> list[list[float]]:
        texts = [input] if isinstance(input, str) else input
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [b / 255 for b in digest[: self.dimensions]]


def load_documents() -> list[Document]:
    """Load the sample PDF. PdfLoader assigns a stable id_ per page (source + page number)."""
    return PdfLoader(input_file=str(PDF_PATH)).load_data()


def build_workflow(
    doc_store: SQLiteDocStore,
    vector_store: ChromaVectorStore,
    doc_strategy: str = DocStrategy.INCREMENTAL,
) -> DocumentIngestionWorkflow:
    return DocumentIngestionWorkflow(
        transformers=[
            TokenTextChunker(chunk_size=200, chunk_overlap=20),
            FakeEmbedding(),
        ],
        doc_strategy=doc_strategy,
        vector_store=vector_store,
        doc_store=doc_store,
    )


@pytest.fixture
def doc_store(tmp_path) -> SQLiteDocStore:
    return SQLiteDocStore(db_path=str(tmp_path / "docstore.db"))


@pytest.fixture
def vector_store() -> ChromaVectorStore:
    # No collection_name -> ChromaVectorStore auto-generates a unique one,
    # so each test gets an isolated in-memory collection.
    return ChromaVectorStore(embed_model=FakeEmbedding())


@pytest.mark.asyncio
async def test_first_run_indexes_all_pages(doc_store, vector_store):
    workflow = build_workflow(doc_store, vector_store)

    result = await workflow.run(documents=load_documents())

    assert len(result.result) > 0
    assert len(vector_store.get_all_documents()) == len(result.result)
    assert len(doc_store.list_documents()) == len(load_documents())


@pytest.mark.asyncio
async def test_incremental_strategy_skips_unchanged_documents_on_rerun(
    doc_store, vector_store
):
    workflow = build_workflow(doc_store, vector_store, DocStrategy.INCREMENTAL)

    first_run = await workflow.run(documents=load_documents())
    assert len(first_run.result) > 0

    second_run = await workflow.run(documents=load_documents())

    assert len(second_run.result) == 0
    # Nothing new was written to the vector store on the second run.
    assert len(vector_store.get_all_documents()) == len(first_run.result)


@pytest.mark.asyncio
async def test_incremental_strategy_reindexes_changed_document(doc_store, vector_store):
    workflow = build_workflow(doc_store, vector_store, DocStrategy.INCREMENTAL)

    documents = load_documents()
    first_run = await workflow.run(documents=documents)
    assert len(first_run.result) > 0

    changed_documents = load_documents()
    changed_documents[0].text = changed_documents[0].text + " extra content"

    second_run = await workflow.run(documents=changed_documents)

    # Only the changed page should have been re-chunked and re-indexed.
    assert 0 < len(second_run.result) < len(first_run.result)
    stored_hash = doc_store.get_document_hash(changed_documents[0].id_)
    assert stored_hash == changed_documents[0].hash


@pytest.mark.asyncio
async def test_deduplicate_off_reindexes_every_run(doc_store, vector_store):
    workflow = build_workflow(doc_store, vector_store, DocStrategy.DEDUPLICATE_OFF)

    first_run = await workflow.run(documents=load_documents())
    second_run = await workflow.run(documents=load_documents())

    assert len(first_run.result) > 0
    assert len(second_run.result) == len(first_run.result)


@pytest.mark.asyncio
async def test_full_strategy_deletes_documents_missing_from_batch(
    doc_store, vector_store
):
    workflow = build_workflow(doc_store, vector_store, DocStrategy.FULL)

    all_documents = load_documents()
    await workflow.run(documents=all_documents)
    assert len(doc_store.list_documents()) == len(all_documents)

    remaining_documents = [doc for doc in load_documents() if doc.id_ != all_documents[0].id_]
    await workflow.run(documents=remaining_documents)

    indexed_ids = {doc.id_ for doc in doc_store.list_documents()}
    assert all_documents[0].id_ not in indexed_ids
    assert len(indexed_ids) == len(remaining_documents)
