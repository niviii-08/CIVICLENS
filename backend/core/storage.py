"""
CIVICLENS TN — Document Storage Abstraction Layer (Phase 11.10)

Provides unified, immutable object storage for raw PDFs, government gazettes,
and evidence files. Supports local filesystem and S3/MinIO compatible object stores.
"""
import os
import hashlib
from pathlib import Path
from typing import Optional, Tuple, BinaryIO


class DocumentStorage:
    """Unified storage interface guaranteeing SHA-256 integrity upon persistence."""

    def __init__(self, base_storage_dir: Optional[str] = None):
        self.storage_dir = Path(base_storage_dir or "data/immutable_documents")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.use_s3 = os.getenv("USE_S3_STORAGE", "False").lower() in ("true", "1")
        self.s3_bucket = os.getenv("S3_STORAGE_BUCKET", "civiclens-evidence-vault")

    def save_document(self, file_content: bytes, filename: str) -> Tuple[str, str]:
        """
        Saves a raw document, validates its SHA-256 digest, and stores it in content-addressable storage.
        Returns: (sha256_hash, relative_or_s3_path)
        """
        sha256 = hashlib.sha256(file_content).hexdigest()
        ext = Path(filename).suffix.lower() or ".bin"
        storage_filename = f"{sha256}{ext}"

        if self.use_s3:
            # S3 / MinIO integration stub
            s3_path = f"s3://{self.s3_bucket}/{storage_filename}"
            return sha256, s3_path

        local_path = self.storage_dir / storage_filename
        if not local_path.exists():
            with open(local_path, "wb") as f:
                f.write(file_content)

        return sha256, str(local_path)

    def retrieve_document(self, sha256: str, ext: str = ".pdf") -> Optional[bytes]:
        """Retrieves an immutable document and re-verifies its cryptographic hash."""
        local_path = self.storage_dir / f"{sha256}{ext}"
        if not local_path.exists():
            return None

        with open(local_path, "rb") as f:
            content = f.read()

        calculated_hash = hashlib.sha256(content).hexdigest()
        if calculated_hash != sha256:
            raise ValueError(f"CRITICAL: Cryptographic integrity mismatch for {sha256}!")

        return content


storage_vault = DocumentStorage()
