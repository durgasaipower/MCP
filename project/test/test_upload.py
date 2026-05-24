"""
Test the /upload REST endpoint.

Usage:
    python test_upload.py
"""

import requests

SERVER_URL = "http://localhost:8000"
API_KEY = "change-me-in-production"


def test_upload_file():
    """Upload a test markdown file."""
    content = """---
title: Test Document
description: A test document for the MCP server
---

# Test Document

This is a test document uploaded via the REST API.

## Section 1

Some content about authentication and authorization.

## Section 2

More content about RAG pipelines and vector search.
"""

    response = requests.post(
        f"{SERVER_URL}/upload",
        headers={"X-API-Key": API_KEY},
        files={"file": ("test-doc.md", content.encode(), "text/markdown")},
        data={"path": "/guides/test-doc.md", "title": "Test Document"},
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response


def test_upload_unauthorized():
    """Test upload with wrong API key."""
    response = requests.post(
        f"{SERVER_URL}/upload",
        headers={"X-API-Key": "wrong-key"},
        files={"file": ("test.md", b"# Test", "text/markdown")},
        data={"path": "/test.md"},
    )

    print(f"\nUnauthorized test:")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 401


def test_upload_missing_fields():
    """Test upload with missing required fields."""
    response = requests.post(
        f"{SERVER_URL}/upload",
        headers={"X-API-Key": API_KEY},
        data={},  # No file, no path
    )

    print(f"\nMissing fields test:")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Upload file")
    print("=" * 60)
    test_upload_file()

    print("\n" + "=" * 60)
    print("TEST: Unauthorized")
    print("=" * 60)
    test_upload_unauthorized()

    print("\n" + "=" * 60)
    print("TEST: Missing fields")
    print("=" * 60)
    test_upload_missing_fields()

    print("\n\nAll upload tests complete.")
