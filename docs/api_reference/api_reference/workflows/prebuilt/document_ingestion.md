---
title: Document Ingestion

---

=== "pip"

    ```bash
    $ pip install "parakeet-workflows[prebuilt]"
    ```

=== "uv"

    ```bash
    $ uv add "parakeet-workflows[prebuilt]"
    ```

A prebuilt workflow for document ingestion that handles the complete pipeline of loading, transforming, and storing documents in a vector store.

This workflow orchestrates the document ingestion pipeline with support for:
    - Multiple document loaders (e.g., Docx, PDF, S3)
    - Multiple transformation components (e.g., chunking, embedding)
    - Deduplication strategies
    - Vector store integration

This workflow provides a streamlined approach to building document ingestion pipelines with support for custom transformers and flexible document processing strategies.

## Attributes

| Parameter        | Type                         | Description                                                                                                                                                   |
| ---------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| transformers     | `list[TransformerComponent]` | List of transformer components to apply to the documents. Transformers are applied in sequence to process and modify documents during the ingestion pipeline. |
| doc_strategy     | `DocStrategy, optional`                | Strategy for handling document processing. Defines how documents should be processed and managed throughout the workflow.                                     |
| doc_store        | `BaseDocStore, optional`     | Document store for deduplication index. If not provided, deduplication is skipped regardless of `doc_strategy`.                                                |
| loaders          | `list[BaseLoader], optional`       | Optional loader component for reading documents from various sources. If not provided, documents must be supplied directly to the workflow.                   |
| vector_store     | `BaseVectorStore, optional`  | Optional vector store for persisting processed documents. When provided, documents are automatically stored after transformation.                             |


## Example

```python
from parakeet_workflows.prebuilt import DocumentIngestionWorkflow
from parakeet_index.core.loaders import DirectoryLoader
from parakeet_index.core.text_chunkers import TokenTextChunker
from parakeet_index.docstore.sqlite import SQLiteDocStore
from parakeet_index.vector_stores.chroma import ChromaVectorStore
from parakeet_index.embeddings.huggingface import HuggingFaceEmbedding

# Initialize components
dir_loader = DirectoryLoader(input_dir="./documents")
chunker = TokenTextChunker(chunk_size=512, chunk_overlap=50)
embeddings = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = ChromaVectorStore(
    collection_name="my_documents",
    embed_model=embeddings
)

# Create ingestion workflow
workflow = DocumentIngestionWorkflow(
    transformers=[chunker],
    doc_strategy="incremental",
    doc_store=SQLiteDocStore(),
    loaders=[dir_loader],
    vector_store=vector_store
)

# Run the workflow
result = await workflow.run()
```

## Workflows

Full workflow documentation [here](https://parakeet-project.github.io/parakeet-workflows/workflows/overview/)