import discord
from discord.ext import commands

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ticket", description="Create a support ticket channel")
    async def ticket(self, ctx: commands.Context, *, reason: str = "No reason provided"):
        guild = ctx.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        channel = await guild.create_text_channel(f"ticket-{ctx.author.name}", overwrites=overwrites, topic=f"Ticket for {ctx.author}")
        await channel.send(f"🎫 Ticket created by {ctx.author.mention} for: {reason}")
        await ctx.reply(f"✅ Ticket channel created: {channel.mention}")

    @commands.hybrid_command(name="close", description="Close the current ticket channel")
    @commands.has_permissions(manage_channels=True)
    async def close_ticket(self, ctx: commands.Context):
        if "ticket" not in ctx.channel.name:
            return await ctx.reply("This command can only be used in ticket channels.")
        await ctx.reply("Closing ticket in 5 seconds...")
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=5))
        await ctx.channel.delete(reason="Ticket closed")

    @commands.hybrid_command(name="add", description="Add a user to the ticket channel")
    @commands.has_permissions(manage_channels=True)
    async def add_user(self, ctx: commands.Context, user: discord.Member):
        if "ticket" not in ctx.channel.name:
            return await ctx.reply("This command can only be used in ticket channels.")
        await ctx.channel.set_permissions(user, read_messages=True, send_messages=True)
        await ctx.reply(f"Added {user.mention} to this ticket.")

    @commands.hybrid_command(name="remove", description="Remove a user from the ticket channel")
    @commands.has_permissions(manage_channels=True)
    async def remove_user(self, ctx: commands.Context, user: discord.Member):
        if "ticket" not in ctx.channel.name:
            return await ctx.reply("This command can only be used in ticket channels.")
        await ctx.channel.set_permissions(user, overwrite=None)
        await ctx.reply(f"Removed {user.mention} from this ticket.")

async def setup(bot):
    await bot.add_cog(Tickets(bot))
