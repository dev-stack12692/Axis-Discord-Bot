import sys
from pathlib import Path

import discord
from discord.ext import commands

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from axis.config import get_prefix, load_token

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Axis Bot ready as {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_guild_join(guild):
    print(f"Joined guild: {guild.name} [{guild.id}]")


async def load_all_cogs():
    cogs_folder = Path(__file__).resolve().parent / "cogs"
    for path in cogs_folder.glob("*.py"):
        if path.name.startswith("_"):
            continue
        ext = f"axis.cogs.{path.stem}"
        try:
            await bot.load_extension(ext)
            print(f"Loaded {ext}")
        except Exception as exc:
            print(f"Failed to load {ext}: {exc}")


async def main():
    await load_all_cogs()
    token = load_token()
    if not token:
        print("No bot token found. Add DISCORD_TOKEN to .env or put your token in token.txt.")
        return
    await bot.start(token)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
