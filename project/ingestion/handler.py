"""
Lambda handler: Triggered by S3 PutObject event.
Downloads the file, chunks it, embeds it, and upserts into vector DB.
"""

import json
import boto3
from chunker import chunk_document
from parser import parse_file

# Reuse imports from mcp services (shared logic)
import sys
sys.path.insert(0, "/opt/python")  # Lambda layer path

from openai import OpenAI
import psycopg2
import os


# Config from environment
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_HOST = os.getenv("VECTOR_DB_HOST")
DB_PORT = int(os.getenv("VECTOR_DB_PORT", "5432"))
DB_NAME = os.getenv("VECTOR_DB_NAME", "docs_mcp")
DB_USER = os.getenv("VECTOR_DB_USER")
DB_PASSWORD = os.getenv("VECTOR_DB_PASSWORD")
DOCS_PREFIX = os.getenv("S3_DOCS_PREFIX", "documents/")

s3 = boto3.client("s3")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def handler(event, context):
    """Lambda entry point. Triggered by S3 event."""
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        # Skip index.json updates
        if key.endswith("index.json"):
            print(f"Skipping index.json: {key}")
            continue

        print(f"Processing: s3://{bucket}/{key}")

        # 1. Download file
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read().decode("utf-8")
        source_path = "/" + key.removeprefix(DOCS_PREFIX)

        # 2. Parse file
        title, text = parse_file(content, key)

        # 3. Chunk
        chunks = chunk_document(text, source_path=source_path, title=title)
        print(f"  Created {len(chunks)} chunks")

        # 4. Generate embeddings
        texts = [c["text"] for c in chunks]
        embeddings = _embed_batch(texts)

        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i]

        # 5. Upsert into vector DB
        _upsert_chunks(source_path, chunks)
        print(f"  Upserted {len(chunks)} chunks for {source_path}")

    return {"statusCode": 200, "body": "OK"}


def _embed_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings in batches of 100."""
    all_embeddings = []
    for i in range(0, len(texts), 100):
        batch = texts[i:i + 100]
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        all_embeddings.extend([item.embedding for item in response.data])
    return all_embeddings


def _upsert_chunks(source_path: str, chunks: list[dict]):
    """Delete old chunks and insert new ones."""
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM doc_chunks WHERE source_path = %s", (source_path,))
            for chunk in chunks:
                cur.execute(
                    """
                    INSERT INTO doc_chunks (embedding, text, source_path, title, heading, chunk_index)
                    VALUES (%s::vector, %s, %s, %s, %s, %s)
                    """,
                    (
                        chunk["embedding"],
                        chunk["text"],
                        chunk["source_path"],
                        chunk["title"],
                        chunk["heading"],
                        chunk["chunk_index"],
                    ),
                )
            conn.commit()
    finally:
        conn.close()
