"""Pydantic models for request/response schemas."""

from pydantic import BaseModel
from typing import Optional


class UploadRequest(BaseModel):
    path: str
    title: Optional[str] = None


class UploadResponse(BaseModel):
    status: str
    path: str
    s3_key: str
    message: str


class IndexEntry(BaseModel):
    path: str
    title: str
    size: int


class IndexFile(BaseModel):
    files: list[IndexEntry]
    total_files: int
    last_updated: Optional[str] = None
