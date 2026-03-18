import discord
from discord.ext import commands

afk_users = {}

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="afk", description="Set your AFK message")
    async def afk(self, ctx: commands.Context, *, reason: str = "AFK"):    
        afk_users[ctx.author.id] = reason
        await ctx.reply(f"✅ {ctx.author.mention} is now AFK: {reason}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.author.id in afk_users:
            del afk_users[message.author.id]
            await message.channel.send(f"Welcome back {message.author.mention}, AFK removed.")

        for user_id, reason in list(afk_users.items()):
            if f"<@{user_id}>" in message.content or f"<@!{user_id}>" in message.content:
                await message.channel.send(f"{message.author.mention}: That user is AFK: {reason}")

        await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(AFK(bot))