import discord
from discord.ext import commands
from axis.utils.database import set_log_channel, get_log_channel

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="setlog", description="Set the log channel for moderation logs")
    @commands.has_permissions(manage_guild=True)
    async def set_log(self, ctx: commands.Context, channel: discord.TextChannel):
        set_log_channel(ctx.guild.id, channel.id)
        await ctx.reply(f"✅ Log channel set to {channel.mention}")

    @commands.hybrid_command(name="showlog", description="Show the currently configured log channel")
    async def show_log(self, ctx: commands.Context):
        channel_id = get_log_channel(ctx.guild.id)
        if not channel_id:
            return await ctx.reply("No log channel set. Use `/setlog #channel`.")
        channel = ctx.guild.get_channel(channel_id)
        if not channel:
            return await ctx.reply("The log channel is invalid. Please set it again.")
        await ctx.reply(f"Current log channel is: {channel.mention}")


async def setup(bot):
    await bot.add_cog(Logs(bot))
