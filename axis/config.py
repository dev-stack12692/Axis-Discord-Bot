import os
from pathlib import Path

from axis.utils.database import init_db, get_prefix_guild

OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


def get_prefix(bot, message):
    if message.guild:
        return get_prefix_guild(message.guild.id)
    return "!"


def load_token():
    # 1) Prefer environment variable first
    env = os.getenv("DISCORD_TOKEN")
    if env:
        return env.strip()

    # 2) Then .env file in project root
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        with env_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    if key.strip() == "DISCORD_TOKEN" and value.strip():
                        return value.strip().strip('"').strip("'")

    # 3) Fallback to token.txt for backward compatibility
    token_file = Path(__file__).resolve().parent.parent / "token.txt"
    if token_file.exists():
        with token_file.open("r", encoding="utf-8") as f:
            token = f.read().strip()
            if token:
                return token

    return None


init_db()

