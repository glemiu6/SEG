import sqlite3

from evidence_graph.storage.cache import SQLiteCache


def test_cache_round_trip_and_canonical_key(tmp_path):
    cache = SQLiteCache(tmp_path / "cache.sqlite3")
    cache.set("test", {"b": 2, "a": 1}, {"result": True})
    assert cache.get("test", {"a": 1, "b": 2}) == {"result": True}


def test_cache_namespaces_do_not_collide(tmp_path):
    cache = SQLiteCache(tmp_path / "cache.sqlite3")
    cache.set("one", {"input": 1}, "first")
    cache.set("two", {"input": 1}, "second")
    assert cache.get("one", {"input": 1}) == "first"
    assert cache.get("two", {"input": 1}) == "second"


def test_expired_entry_is_deleted(tmp_path):
    cache = SQLiteCache(tmp_path / "cache.sqlite3")
    inputs = {"input": 1}
    cache.set("test", inputs, "value", ttl_seconds=-1)
    assert cache.get("test", inputs) is None
    with sqlite3.connect(cache.path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM cache_entries").fetchone()[0] == 0
