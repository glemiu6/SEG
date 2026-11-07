"""Small SQLite-backed cache shared by network and local-model clients."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any


class CacheError(RuntimeError):
    """Raised when the persistent cache cannot be read or written."""


class SQLiteCache:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self._connect() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        namespace TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        created_at INTEGER NOT NULL,
                        expires_at INTEGER,
                        PRIMARY KEY (namespace, key)
                    )
                    """
                )
                connection.execute(
                    "CREATE INDEX IF NOT EXISTS cache_expiry ON cache_entries(expires_at)"
                )
        except (OSError, sqlite3.Error) as exc:
            raise CacheError(f"Could not initialize cache at {self.path}: {exc}") from exc

    def get(self, namespace: str, inputs: Any) -> Any | None:
        key = self.make_key(inputs)
        now = int(time.time())
        try:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT value, expires_at FROM cache_entries WHERE namespace = ? AND key = ?",
                    (namespace, key),
                ).fetchone()
                if row is None:
                    return None
                value, expires_at = row
                if expires_at is not None and expires_at <= now:
                    connection.execute(
                        "DELETE FROM cache_entries WHERE namespace = ? AND key = ?",
                        (namespace, key),
                    )
                    return None
                return json.loads(value)
        except (sqlite3.Error, json.JSONDecodeError) as exc:
            raise CacheError(f"Could not read cache at {self.path}: {exc}") from exc

    def set(
        self,
        namespace: str,
        inputs: Any,
        value: Any,
        ttl_seconds: int | None = None,
    ) -> None:
        now = int(time.time())
        expires_at = now + ttl_seconds if ttl_seconds is not None else None
        try:
            encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO cache_entries(namespace, key, value, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(namespace, key) DO UPDATE SET
                        value = excluded.value,
                        created_at = excluded.created_at,
                        expires_at = excluded.expires_at
                    """,
                    (namespace, self.make_key(inputs), encoded, now, expires_at),
                )
        except (TypeError, sqlite3.Error) as exc:
            raise CacheError(f"Could not write cache at {self.path}: {exc}") from exc

    @staticmethod
    def make_key(inputs: Any) -> str:
        canonical = json.dumps(
            inputs, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=10)
