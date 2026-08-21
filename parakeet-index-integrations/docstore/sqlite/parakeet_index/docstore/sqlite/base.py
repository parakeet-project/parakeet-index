from datetime import datetime, timezone
from typing import Any

from parakeet_index.core.bridge.pydantic import Field, PrivateAttr
from parakeet_index.core.docstore import BaseDocStore
from parakeet_index.core.document import Document


class SQLiteDocStore(BaseDocStore):
    """
    SQLite-backed document store.

    Attributes:
        db_path (str): Path to the SQLite database file. Defaults to ``parakeet-index-docstore.db``.

    Example:
        ```python
        from parakeet_index.docstore.sqlite import SQLiteDocStore

        doc_store = SQLiteDocStore(db_path="./my-index.db")
        ```
    """

    db_path: str = Field(
        default="parakeet-index-docstore.db",
        description="Path to the SQLite database file.",
    )

    _engine: Any = PrivateAttr()
    _table: Any = PrivateAttr()

    def model_post_init(self, __context):  # noqa: PYI063
        from sqlalchemy import (
            Column,
            Index,
            MetaData,
            String,
            Table,
            Text,
            create_engine,
        )

        self._engine = create_engine(f"sqlite:///{self.db_path}")

        metadata = MetaData()
        self._table = Table(
            "parakeet_index_docstore",
            metadata,
            Column("doc_id", String, primary_key=True),
            Column("doc_hash", String, nullable=False),
            Column("text", Text, nullable=False),
            Column("created_at", String, nullable=False),
            Column("updated_at", String, nullable=False),
            Index("idx_doc_hash", "doc_hash"),
        )
        metadata.create_all(self._engine)

    @classmethod
    def class_name(cls) -> str:
        return "SQLiteDocStore"

    def upsert_documents(self, documents: list[Document]) -> None:
        """Insert or update document records."""
        if not documents:
            return

        from sqlalchemy.dialects.sqlite import insert

        now = datetime.now(timezone.utc).isoformat()

        values = [
            {
                "doc_id": doc.id_,
                "doc_hash": doc.hash,
                "text": doc.get_content(),
                "created_at": now,
                "updated_at": now,
            }
            for doc in documents
        ]

        stmt = insert(self._table)
        stmt = stmt.on_conflict_do_update(
            index_elements=["doc_id"],
            set_={
                "doc_hash": stmt.excluded.doc_hash,
                "text": stmt.excluded.text,
                "updated_at": stmt.excluded.updated_at,
            },
        )

        with self._engine.begin() as conn:
            conn.execute(stmt, values)

    def list_documents(self) -> list[Document]:
        """Return all documents currently stored, including text."""
        from sqlalchemy import select

        stmt = select(
            self._table.c.doc_id,
            self._table.c.text,
        )

        with self._engine.connect() as conn:
            rows = conn.execute(stmt).fetchall()

        return [Document(id_=row[0], text=row[1]) for row in rows]

    def delete_documents(self, ids: list[str]) -> None:
        """Delete records by document ID."""
        if not ids:
            return

        from sqlalchemy import delete

        stmt = delete(self._table).where(self._table.c.doc_id.in_(ids))

        with self._engine.begin() as conn:
            conn.execute(stmt)

    def get_document_hash(self, doc_id: str) -> str | None:
        """Get the stored hash for a single document, if it exists."""
        from sqlalchemy import select

        stmt = select(self._table.c.doc_hash).where(self._table.c.doc_id == doc_id)

        with self._engine.connect() as conn:
            row = conn.execute(stmt).fetchone()

        return row[0] if row is not None else None

    def get_document(self, doc_id: str) -> Document | None:
        """Return a single document record by Id, including text."""
        from sqlalchemy import select

        stmt = select(
            self._table.c.doc_id,
            self._table.c.text,
        ).where(self._table.c.doc_id == doc_id)

        with self._engine.connect() as conn:
            row = conn.execute(stmt).fetchone()

        if row is None:
            return None

        return Document(id_=row[0], text=row[1])
