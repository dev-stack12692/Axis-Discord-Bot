import aiohttp
import datetime
import discord
from discord.ext import commands
from axis.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from axis.utils.database import add_filtered_word, remove_filtered_word, get_filtered_words, get_log_channel, set_link_ban, get_link_ban, set_automod, get_automod

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ai_warn_state = {}
        self.ai_enabled = False
        self.ai_ban_enabled = False

    async def classify_message(self, text: str) -> dict:
        if not OPENROUTER_API_KEY:
            return {"action": "SAFE", "reason": "no key"}
        url = "https://openrouter.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        prompt = (
            "You are a moderation assistant. Classify the message as SAFE, WARN, TIMEOUT, or BAN. "
            "Answer as a JSON object with keys action and reason.\n"
            f"Message: {text}"
        )
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 120,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=30) as resp:
                    data = await resp.json()
            if resp.status != 200:
                return {"action": "SAFE", "reason": "api_error"}
            text_out = data.get("choices", [])[0].get("message", {}).get("content", "")
            # Try parse JSON from model output
            import json
            try:
                parsed = json.loads(text_out.strip())
                action = parsed.get("action", "SAFE").upper()
                reason = parsed.get("reason", "AI moderation")
                return {"action": action, "reason": reason}
            except Exception:
                lowered = text_out.lower()
                if "ban" in lowered:
                    return {"action": "BAN", "reason": "AI content analysis"}
                if "timeout" in lowered:
                    return {"action": "TIMEOUT", "reason": "AI content analysis"}
                if "warn" in lowered:
                    return {"action": "WARN", "reason": "AI content analysis"}
                return {"action": "SAFE", "reason": "AI safe"}
        except Exception:
            return {"action": "SAFE", "reason": "api_fail"}

    @commands.hybrid_command(name="aimode", description="Enable or disable AI moderation mode")
    @commands.has_permissions(manage_guild=True)
    async def aimode(self, ctx: commands.Context, enabled: bool):
        self.ai_enabled = enabled
        await ctx.reply(f"🤖 AI moderation mode {'enabled' if enabled else 'disabled'}.")

    @commands.hybrid_command(name="aiban", description="Enable or disable AI auto-ban behavior")
    @commands.has_permissions(manage_guild=True)
    async def aiban(self, ctx: commands.Context, enabled: bool):
        self.ai_ban_enabled = enabled
        await ctx.reply(f"🛡️ AI ban mode {'enabled' if enabled else 'disabled'}.")

    @commands.hybrid_command(name="ban", description="Ban a member from the server")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await ctx.reply(f"🚫 {member} has been banned. Reason: {reason}")
        await self.log_action(ctx.guild, f"{member} was banned by {ctx.author}. Reason: {reason}")

    @commands.hybrid_command(name="warn", description="Warn a member for rule violations")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        await ctx.reply(f"⚠️ {member.mention} has been warned. Reason: {reason}")
        await self.log_action(ctx.guild, f"{member} was warned by {ctx.author}. Reason: {reason}")

    @commands.hybrid_command(name="timeout", description="Timeout a member for the given duration")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx: commands.Context, member: discord.Member, duration: int, *, reason: str = "No reason"):
        try:
            await member.timeout_for(datetime.timedelta(seconds=duration), reason=reason)
            await ctx.reply(f"⏱️ {member.mention} was timed out for {duration} seconds.")
            await self.log_action(ctx.guild, f"{member} timed out for {duration}s by {ctx.author}. Reason: {reason}")
        except Exception as exc:
            await ctx.reply(f"Could not timeout user: {exc}")

    @commands.hybrid_command(name="addfilter", description="Add a word to the server filter list")
    @commands.has_permissions(manage_messages=True)
    async def add_filter(self, ctx: commands.Context, *, word: str):
        add_filtered_word(ctx.guild.id, word)
        await ctx.reply(f"✅ Added word filter: `{word}`")

    @commands.hybrid_command(name="removefilter", description="Remove a word from the filter list")
    @commands.has_permissions(manage_messages=True)
    async def remove_filter(self, ctx: commands.Context, *, word: str):
        remove_filtered_word(ctx.guild.id, word)
        await ctx.reply(f"✅ Removed word filter: `{word}`")

    @commands.hybrid_command(name="unban", description="Unban a user by ID")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_id: int):
        user = await self.bot.fetch_user(user_id)
        try:
            await ctx.guild.unban(user)
            await ctx.reply(f"✅ Unbanned {user}")
            await self.log_action(ctx.guild, f"{user} was unbanned by {ctx.author}.")
        except Exception as exc:
            await ctx.reply(f"Could not unban user: {exc}")

    @commands.hybrid_command(name="clear", description="Clear a number of messages from the channel")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int = 5):
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.reply(f"🧹 Deleted {len(deleted)} message(s).", delete_after=7)

    @commands.hybrid_command(name="filterlist", description="List all filtered words for this server")
    async def filter_list(self, ctx: commands.Context):
        words = get_filtered_words(ctx.guild.id)
        if not words:
            return await ctx.reply("No filtered words set.")
        await ctx.reply("Filtered words: `" + ", ".join(words) + "`")

    @commands.hybrid_command(name="lockdown", description="Lock all text channels for @everyone")
    @commands.has_permissions(manage_guild=True)
    async def lockdown(self, ctx: commands.Context):
        for channel in ctx.guild.text_channels:
            perms = channel.overwrites_for(ctx.guild.default_role)
            perms.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
        await ctx.reply("🔒 Server is now in lockdown (text channels locked).")

    @commands.hybrid_command(name="linkban", description="Enable or disable link bans automatically")
    @commands.has_permissions(manage_guild=True)
    async def link_ban(self, ctx: commands.Context, enabled: bool):
        set_link_ban(ctx.guild.id, enabled)
        status = "enabled" if enabled else "disabled"
        await ctx.reply(f"🔗 Link ban {status}.")

    @commands.hybrid_command(name="automod", description="Turn automod on or off for the server")
    @commands.has_permissions(manage_guild=True)
    async def automod(self, ctx: commands.Context, enabled: bool):
        set_automod(ctx.guild.id, enabled)
        status = "enabled" if enabled else "disabled"
        await ctx.reply(f"🤖 Automod {status}.")

    @commands.hybrid_command(name="giveaway", description="Start a giveaway with duration and prize")
    @commands.has_permissions(manage_guild=True)
    async def giveaway(self, ctx: commands.Context, duration: int, *, prize: str):
        embed = discord.Embed(title="🎉 Giveaway Started", description=prize, color=0xFFD700)
        embed.add_field(name="Ends in", value=f"{duration} seconds", inline=False)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")
        await ctx.reply("Giveaway started! React with 🎉")
        await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=duration))
        msg = await ctx.channel.fetch_message(msg.id)
        winners = []
        participants = 0
        for reaction in msg.reactions:
            if str(reaction.emoji) == "🎉":
                async for user in reaction.users():
                    if not user.bot:
                        winners.append(user)
                participants = len([u for u in await reaction.users().flatten() if not u.bot])
        if winners:
            winner = winners[0]
            await ctx.send(f"🎉 Giveaway complete! Winner: {winner.mention} | Participants: {participants}")
        else:
            await ctx.send(f"No participants for giveaway. Participants: {participants}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # AI auto moderation
        if self.ai_enabled and get_automod(message.guild.id):
            result = await self.classify_message(message.content)
            action = result.get("action", "SAFE")
            reason = result.get("reason", "AI moderation")
            if action in ["WARN", "TIMEOUT", "BAN"]:
                user_key = (message.guild.id, message.author.id)
                if action == "WARN":
                    count = self.ai_warn_state.get(user_key, 0) + 1
                    self.ai_warn_state[user_key] = count
                    await message.channel.send(f"⚠️ {message.author.mention}, AI Moderation Warning #{count}: {reason}")
                    if count >= 3:
                        try:
                            await message.author.timeout_for(datetime.timedelta(minutes=10), reason="3 AI warnings")
                            await message.channel.send(f"⛔ {message.author.mention} has been timed out for 10 minutes after 3 warnings.")
                            self.ai_warn_state[user_key] = 0
                        except Exception:
                            pass
                elif action == "TIMEOUT":
                    try:
                        await message.author.timeout_for(datetime.timedelta(minutes=10), reason=reason)
                        await message.channel.send(f"⛔ {message.author.mention} has been timed out for 10 minutes ({reason}).")
                    except Exception:
                        pass
                elif action == "BAN":
                    if self.ai_ban_enabled:
                        try:
                            await message.author.ban(reason=reason)
                            await message.channel.send(f"🔨 {message.author.mention} has been banned by AI moderation: {reason}")
                        except Exception:
                            pass
                    else:
                        await message.channel.send(f"⚠️ {message.author.mention}: AI detected severe violation but auto-ban is disabled. Moderator review required.")
                    try:
                        await message.delete()
                    except Exception:
                        pass
                try:
                    await message.delete()
                except Exception:
                    pass
                return

        # Link ban / automod
        automod_enabled = get_automod(message.guild.id)
        if automod_enabled and ("http://" in message.content.lower() or "https://" in message.content.lower()):
            if not message.author.guild_permissions.manage_guild:
                if get_link_ban(message.guild.id):
                    try:
                        await message.author.ban(reason="Link ban by Axis automod")
                        await message.channel.send(f"🚫 {message.author.mention} was banned for posting a link.")
                    except Exception:
                        pass
                    return
                else:
                    try:
                        await message.delete()
                        await message.channel.send(f"🔗 Link detected and deleted from {message.author.mention}.")
                    except discord.Forbidden:
                        pass

        words = get_filtered_words(message.guild.id)
        lowered = message.content.lower()
        matched = [w for w in words if w in lowered]
        if matched:
            try:
                await message.delete()
                await message.channel.send(f"🚫 Word filter block: {message.author.mention}")
                await self.log_action(message.guild, f"Deleted message by {message.author} containing {', '.join(matched)}")
            except discord.Forbidden:
                pass

        await self.bot.process_commands(message)

    async def log_action(self, guild: discord.Guild, message: str):
        channel_id = get_log_channel(guild.id)
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(message)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
