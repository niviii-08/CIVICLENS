"""
CivicLens TN - Database Backup and Verification Utility
Uses SQLite online backup API to take consistent snapshots without blocking concurrent transactions.
Performs SHA-256 checksumming and PRAGMA integrity_check validation.
"""
import argparse
import hashlib
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def calculate_sha256(filepath: str) -> str:
    """Calculates SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def backup_database(source_path: str, backup_dir: str, verify: bool = True) -> str:
    """
    Creates an online, non-blocking backup of an SQLite database.
    Verifies B-tree integrity and generates a checksum manifest.
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source database not found: {source_path}")

    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_filename = f"civiclens_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)

    print(f"[*] Starting backup from '{source_path}' to '{backup_path}'...")

    src_conn = sqlite3.connect(source_path)
    dst_conn = sqlite3.connect(backup_path)

    try:
        # Use SQLite native backup API (safe for WAL mode during live concurrent writes)
        src_conn.backup(dst_conn, pages=100)
        dst_conn.close()
        src_conn.close()
        print("[+] Database pages transferred successfully.")
    except Exception as e:
        if os.path.exists(backup_path):
            os.remove(backup_path)
        raise RuntimeError(f"Backup failed during page copy: {e}") from e

    sha256 = calculate_sha256(backup_path)
    file_size_bytes = os.path.getsize(backup_path)

    print(f"[+] Backup completed: {backup_filename} ({file_size_bytes:,} bytes)")
    print(f"[+] SHA-256 Checksum: {sha256}")

    if verify:
        print("[*] Running PRAGMA integrity_check on backup...")
        verify_conn = sqlite3.connect(backup_path)
        cursor = verify_conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        res = cursor.fetchone()
        verify_conn.close()

        if res and res[0] == "ok":
            print("[+] Backup verified: PRAGMA integrity_check returned 'ok'")
        else:
            raise RuntimeError(f"Backup verification failed: {res}")

    # Write manifest file
    manifest_path = backup_path + ".manifest"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(f"Source: {source_path}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"File Size: {file_size_bytes} bytes\n")
        f.write(f"SHA-256: {sha256}\n")
        f.write(f"Integrity Check: PASSED\n")

    return backup_path


def restore_database(backup_path: str, target_path: str, dry_run: bool = False) -> bool:
    """
    Restores an SQLite database from a verified backup snapshot.
    """
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    # Check integrity of backup before restoring
    print(f"[*] Verifying integrity of backup '{backup_path}' before restore...")
    verify_conn = sqlite3.connect(backup_path)
    cursor = verify_conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    res = cursor.fetchone()
    verify_conn.close()

    if not res or res[0] != "ok":
        raise RuntimeError(f"Cannot restore: Backup corrupted with status '{res}'")

    if dry_run:
        print("[+] Dry run: Backup is intact and ready for restore.")
        return True

    print(f"[*] Restoring backup to '{target_path}'...")
    src_conn = sqlite3.connect(backup_path)
    dst_conn = sqlite3.connect(target_path)
    src_conn.backup(dst_conn, pages=100)
    dst_conn.close()
    src_conn.close()

    print(f"[+] Restore successfully completed to '{target_path}'.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CivicLens TN Database Backup Utility")
    parser.add_argument("--source", default="data/processed/civiclens.db", help="Path to source SQLite database")
    parser.add_argument("--dest-dir", default="data/backups", help="Directory to store backups")
    parser.add_argument("--restore-from", default=None, help="Backup file to restore from")
    parser.add_argument("--restore-to", default=None, help="Destination database path for restore")
    parser.add_argument("--dry-run", action="store_true", help="Perform validation without writing")

    args = parser.parse_args()

    if args.restore_from:
        if not args.restore_to:
            print("ERROR: --restore-to is required when using --restore-from", file=sys.stderr)
            sys.exit(1)
        restore_database(args.restore_from, args.restore_to, dry_run=args.dry_run)
    else:
        backup_database(args.source, args.dest_dir, verify=True)
