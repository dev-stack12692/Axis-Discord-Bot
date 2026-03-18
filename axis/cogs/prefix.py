from discord.ext import commands
from axis.utils.database import set_prefix_guild, get_prefix_guild

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="setprefix", description="Set the server prefix for commands")
    @commands.has_permissions(manage_guild=True)
    async def set_prefix(self, ctx: commands.Context, prefix: str):
        if len(prefix) > 5:
            return await ctx.reply("Prefix should be 5 characters or less.")
        set_prefix_guild(ctx.guild.id, prefix)
        await ctx.reply(f"✅ Prefix has been changed to: `{prefix}`")

    @commands.hybrid_command(name="showprefix", description="Show the server command prefix")
    async def show_prefix(self, ctx: commands.Context):
        prefix = get_prefix_guild(ctx.guild.id)
        await ctx.reply(f"Server prefix is: `{prefix}`")


async def setup(bot):
    await bot.add_cog(Prefix(bot))
