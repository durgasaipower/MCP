"""S3 operations for reading/writing documentation files."""

import json
import boto3
from config import Config


s3 = boto3.client("s3")


def upload_file(content: bytes, path: str, content_type: str = "text/markdown") -> str:
    """Upload a file to S3. Returns the S3 key."""
    key = f"{Config.S3_DOCS_PREFIX}{path.lstrip('/')}"
    s3.put_object(
        Bucket=Config.S3_BUCKET,
        Key=key,
        Body=content,
        ContentType=content_type,
    )
    return key


def read_file(path: str) -> str:
    """Read a file from S3 by its virtual path."""
    key = f"{Config.S3_DOCS_PREFIX}{path.lstrip('/')}"
    response = s3.get_object(Bucket=Config.S3_BUCKET, Key=key)
    return response["Body"].read().decode("utf-8")


def list_files(prefix: str = "") -> list[dict]:
    """List all files under a prefix."""
    full_prefix = f"{Config.S3_DOCS_PREFIX}{prefix.lstrip('/')}"
    paginator = s3.get_paginator("list_objects_v2")
    files = []
    for page in paginator.paginate(Bucket=Config.S3_BUCKET, Prefix=full_prefix):
        for obj in page.get("Contents", []):
            # Convert S3 key back to virtual path
            virtual_path = "/" + obj["Key"].removeprefix(Config.S3_DOCS_PREFIX)
            files.append({
                "path": virtual_path,
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
            })
    return files


def get_index() -> dict:
    """Read the index.json file."""
    try:
        response = s3.get_object(Bucket=Config.S3_BUCKET, Key=Config.S3_INDEX_KEY)
        return json.loads(response["Body"].read().decode("utf-8"))
    except s3.exceptions.NoSuchKey:
        return {"files": [], "total_files": 0}


def update_index(path: str, title: str, size: int):
    """Add or update a file entry in index.json."""
    index = get_index()

    # Remove existing entry for this path
    index["files"] = [f for f in index["files"] if f["path"] != path]

    # Add new entry
    index["files"].append({"path": path, "title": title, "size": size})
    index["total_files"] = len(index["files"])

    # Write back
    s3.put_object(
        Bucket=Config.S3_BUCKET,
        Key=Config.S3_INDEX_KEY,
        Body=json.dumps(index, indent=2).encode("utf-8"),
        ContentType="application/json",
    )
