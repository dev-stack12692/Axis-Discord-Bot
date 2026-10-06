# Axis Discord Bot - Design

## Purpose

Axis is a Discord server management bot for moderation, channel security,
support tickets, and everyday utilities. This document describes the current
code structure and separates planned improvements from existing behavior.

## Tech stack

- Python with `discord.py` for Discord events and hybrid commands.
- `aiohttp` for optional OpenRouter moderation requests.
- SQLite for per-server settings and word filters.
- Environment variables and local configuration files for credentials.

## Architecture

`axis/main.py` creates the bot, loads the modules in `axis/cogs/`, starts the
Discord connection, and syncs slash commands when the bot is ready.
`axis/config.py` resolves the server prefix and loads the bot token.
`axis/utils/database.py` owns the SQLite connection and settings helpers.

Each cog groups related commands and event listeners:

| Cog | Responsibility | Example commands |
| --- | --- | --- |
| Moderation | Member actions, message filters, optional AI moderation, giveaways | `ban`, `unban`, `warn`, `timeout`, `clear`, `automod`, `aimode`, `aiban`, `giveaway` |
| Security | Channel messaging permissions | `lock`, `unlock` |
| Tickets | Private support channels and access management | `ticket`, `close`, `add`, `remove` |
| Logs | Configure the moderation log destination | `setlog`, `showlog` |
| Prefix | Per-server prefix configuration | `setprefix`, `showprefix` |
| AFK | Away status and mention notices | `afk` |
| Utility | Help, latency, server information, announcements | `axishelp`, `ping`, `dashboard`, `announce`, `alert` |

Commands use `@commands.hybrid_command`, so they are registered for prefix
and slash usage. The default prefix is `!`; servers can set their own.

## Event flow

1. Discord delivers a command interaction or message event.
2. The command framework checks declared member permissions before running
   restricted commands, such as banning members or managing channels.
3. Message listeners handle AFK notices and moderation. The moderation
   listener skips bot messages and direct messages.
4. When enabled, AI moderation sends message text to OpenRouter and reads an
   action and reason. Local moderation also checks links and filtered words.
5. The bot performs the Discord action, replies where needed, and writes
   supported moderation actions to the configured log channel.

AI mode and AI auto-ban start disabled. Link handling can delete links or ban
members according to server options. Word filters are checked separately from
the automod toggle in the current implementation.

## State and persistence

`axis/axis_data.db` stores three tables:

- `guild_settings`: server ID, command prefix, and log channel ID.
- `word_filters`: filtered words keyed by server ID.
- `guild_options`: link-ban and automod switches keyed by server ID.

AFK status, AI warning counts, and AI mode switches are held in memory and
reset after a restart. AI mode switches currently apply to the whole bot,
not an individual server. Ticket access is represented by Discord channel
permission overwrites.

## Safety and reliability goals

The following are proposed improvements, not claims that they are implemented:

- Keep credentials outside source control and exclude runtime database files.
- Use only the Discord intents and bot permissions each feature needs.
- Add per-server AI settings, request limits, and moderator review before
  severe AI-driven actions. Explain that AI mode sends message text to an
  external service.
- Validate model responses against a fixed action list; malformed replies
  should not trigger punishment.
- Centralize prefix-command dispatch so multiple message listeners cannot
  run the same command more than once.
- Add clear error handling for missing permissions, unavailable channels,
  API failures, and incompatible Discord library calls.
- Persist long-running jobs where needed, and select giveaway winners fairly.

## Validation plan

Use a test server to check prefix and slash commands, permission denials,
server-specific settings, ticket visibility, log delivery, and restart
behavior. Test AI moderation with mocked safe, invalid, and failed responses
before enabling it for real members. This design draft does not change or
verify the running bot.
