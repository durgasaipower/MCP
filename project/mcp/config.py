"""Configuration loaded from environment variables."""

import os


class Config:
    # S3
    S3_BUCKET = os.getenv("S3_BUCKET", "docs-mcp-content")
    S3_DOCS_PREFIX = os.getenv("S3_DOCS_PREFIX", "documents/")
    S3_INDEX_KEY = os.getenv("S3_INDEX_KEY", "documents/index.json")

    # Vector DB
    VECTOR_DB_HOST = os.getenv("VECTOR_DB_HOST", "localhost")
    VECTOR_DB_PORT = int(os.getenv("VECTOR_DB_PORT", "5432"))
    VECTOR_DB_NAME = os.getenv("VECTOR_DB_NAME", "docs_mcp")
    VECTOR_DB_USER = os.getenv("VECTOR_DB_USER", "postgres")
    VECTOR_DB_PASSWORD = os.getenv("VECTOR_DB_PASSWORD", "password")

    # Embeddings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))

    # Auth
    UPLOAD_API_KEY = os.getenv("UPLOAD_API_KEY", "change-me-in-production")
