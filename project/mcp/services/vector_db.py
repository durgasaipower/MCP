"""Vector database operations (pgvector implementation)."""

import psycopg2
from psycopg2.extras import execute_values
from config import Config
from services.embeddings import generate_embedding


def get_connection():
    """Get a database connection."""
    return psycopg2.connect(
        host=Config.VECTOR_DB_HOST,
        port=Config.VECTOR_DB_PORT,
        dbname=Config.VECTOR_DB_NAME,
        user=Config.VECTOR_DB_USER,
        password=Config.VECTOR_DB_PASSWORD,
    )


def search(query: str, top_k: int = 5) -> list[dict]:
    """Semantic search: embed query and find similar chunks."""
    query_embedding = generate_embedding(query)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, text, source_path, title, heading, chunk_index,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM doc_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (query_embedding, query_embedding, top_k),
            )
            rows = cur.fetchall()
            return [
                {
                    "id": str(row[0]),
                    "text": row[1],
                    "source_path": row[2],
                    "title": row[3],
                    "heading": row[4],
                    "chunk_index": row[5],
                    "similarity": float(row[6]),
                }
                for row in rows
            ]
    finally:
        conn.close()


def upsert_chunks(source_path: str, chunks: list[dict]):
    """Replace all chunks for a source_path with new ones."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Delete existing chunks for this source
            cur.execute(
                "DELETE FROM doc_chunks WHERE source_path = %s",
                (source_path,),
            )

            # Insert new chunks
            if chunks:
                execute_values(
                    cur,
                    """
                    INSERT INTO doc_chunks
                        (embedding, text, source_path, title, heading, chunk_index)
                    VALUES %s
                    """,
                    [
                        (
                            chunk["embedding"],
                            chunk["text"],
                            chunk["source_path"],
                            chunk["title"],
                            chunk["heading"],
                            chunk["chunk_index"],
                        )
                        for chunk in chunks
                    ],
                )
            conn.commit()
    finally:
        conn.close()


def init_db():
    """Create the doc_chunks table if it doesn't exist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS doc_chunks (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    embedding vector(1536),
                    text TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    title TEXT,
                    heading TEXT,
                    chunk_index INTEGER,
                    uploaded_at TIMESTAMP DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_doc_chunks_embedding
                ON doc_chunks USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
                """
            )
            conn.commit()
    finally:
        conn.close()
