import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "axis_data.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id INTEGER PRIMARY KEY,
            prefix TEXT DEFAULT '!',
            log_channel_id INTEGER
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS word_filters (
            guild_id INTEGER,
            word TEXT,
            PRIMARY KEY (guild_id, word)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS guild_options (
            guild_id INTEGER PRIMARY KEY,
            link_ban INTEGER DEFAULT 0,
            automod INTEGER DEFAULT 1
        )
        """
    )
    conn.commit()
    conn.close()


def get_prefix_guild(guild_id: int):
    conn = get_connection()
    row = conn.execute("SELECT prefix FROM guild_settings WHERE guild_id = ?", (guild_id,)).fetchone()
    conn.close()
    if row and row['prefix']:
        return row['prefix']
    return '!'


def set_prefix_guild(guild_id: int, prefix: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO guild_settings (guild_id, prefix) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET prefix = excluded.prefix",
        (guild_id, prefix),
    )
    conn.commit()
    conn.close()


def get_log_channel(guild_id: int):
    conn = get_connection()
    row = conn.execute("SELECT log_channel_id FROM guild_settings WHERE guild_id = ?", (guild_id,)).fetchone()
    conn.close()
    if row and row['log_channel_id']:
        return row['log_channel_id']
    return None


def set_log_channel(guild_id: int, channel_id: int):
    conn = get_connection()
    conn.execute(
        "INSERT INTO guild_settings (guild_id, log_channel_id) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET log_channel_id = excluded.log_channel_id",
        (guild_id, channel_id),
    )
    conn.commit()
    conn.close()


def add_filtered_word(guild_id: int, word: str):
    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO word_filters (guild_id, word) VALUES (?, ?)", (guild_id, word.lower()))
    conn.commit()
    conn.close()


def set_link_ban(guild_id: int, enabled: bool):
    conn = get_connection()
    conn.execute(
        "INSERT INTO guild_options (guild_id, link_ban) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET link_ban = excluded.link_ban",
        (guild_id, 1 if enabled else 0),
    )
    conn.commit()
    conn.close()


def get_link_ban(guild_id: int):
    conn = get_connection()
    row = conn.execute("SELECT link_ban FROM guild_options WHERE guild_id = ?", (guild_id,)).fetchone()
    conn.close()
    if row:
        return bool(row['link_ban'])
    return False


def set_automod(guild_id: int, enabled: bool):
    conn = get_connection()
    conn.execute(
        "INSERT INTO guild_options (guild_id, automod) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET automod = excluded.automod",
        (guild_id, 1 if enabled else 0),
    )
    conn.commit()
    conn.close()


def get_automod(guild_id: int):
    conn = get_connection()
    row = conn.execute("SELECT automod FROM guild_options WHERE guild_id = ?", (guild_id,)).fetchone()
    conn.close()
    if row:
        return bool(row['automod'])
    return True


def remove_filtered_word(guild_id: int, word: str):
    conn = get_connection()
    conn.execute("DELETE FROM word_filters WHERE guild_id = ? AND word = ?", (guild_id, word.lower()))
    conn.commit()
    conn.close()


def get_filtered_words(guild_id: int):
    conn = get_connection()
    rows = conn.execute("SELECT word FROM word_filters WHERE guild_id = ?", (guild_id,)).fetchall()
    conn.close()
    return [row['word'] for row in rows]

