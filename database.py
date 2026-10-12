import hashlib
import hmac
import json
import sqlite3

DB = "data.db"


def connect():
    return sqlite3.connect(DB)


def password_digest(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def setup():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                balance INTEGER NOT NULL DEFAULT 500,
                name TEXT NOT NULL DEFAULT '',
                infrastructure TEXT NOT NULL DEFAULT '{}'
            )
        """)

        columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(player)").fetchall()
        }
        if "name" not in columns:
            conn.execute(
                "ALTER TABLE player ADD COLUMN name TEXT NOT NULL DEFAULT ''"
            )
        if "infrastructure" not in columns:
            conn.execute(
                "ALTER TABLE player ADD COLUMN infrastructure "
                "TEXT NOT NULL DEFAULT '{}'"
            )


def create_player(username, password):
    with connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO player (username, password) VALUES (?, ?)",
            (username, password_digest(password))
        )


def authenticate(username, password):
    with connect() as conn:
        row = conn.execute(
            "SELECT password FROM player WHERE username = ?", (username,)
        ).fetchone()

    if row is None:
        return False

    return hmac.compare_digest(row[0], password_digest(password))


def load_player(username):
    with connect() as conn:
        row = conn.execute(
            "SELECT username, balance, name, infrastructure "
            "FROM player WHERE username = ?",
            (username,)
        ).fetchone()

    if row is None:
        return None

    infrastructure = json.loads(row[3] or "{}")
    if not isinstance(infrastructure, dict):
        raise ValueError("Player infrastructure must be a JSON object.")

    return {
        "username": row[0],
        "balance": row[1],
        "name": row[2],
        "infrastructure": infrastructure,
    }


def save_player(username, balance, name, infrastructure):
    with connect() as conn:
        conn.execute(
            "UPDATE player SET balance = ?, name = ?, infrastructure = ? "
            "WHERE username = ?",
            (
                balance,
                name,
                json.dumps(infrastructure, sort_keys=True),
                username,
            ),
        )


if __name__ == "__main__":
    setup()