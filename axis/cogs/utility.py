import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="developer", description="Show bot developer and feature information")
    async def developer(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Axis Bot Developers",
            description="Main Lead: Swapnendu\nPowered by Core AI Infrastructure",
            color=0x00FF00,
        )
        embed.add_field(name="Bot Name", value="Axis", inline=False)
        embed.add_field(name="Features", value="Advanced moderation, AFK, word filter, security locks, logs, prefix manager", inline=False)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="axishelp", aliases=["bothelp"], description="Show the Axis bot help menu")
    async def help_command(self, ctx: commands.Context):
        prefix = "!"
        if ctx.guild:
            from axis.utils.database import get_prefix_guild
            prefix = get_prefix_guild(ctx.guild.id)
        embed = discord.Embed(
            title="Axis Bot Help",
            description="Advanced moderation & security bot commands",
            color=0x7289DA,
        )
        embed.add_field(name="Moderation", value=f"`{prefix}ban @user reason`, `{prefix}unban user_id`, `{prefix}warn @user reason`, `{prefix}timeout @user seconds reason`, `{prefix}clear amount`", inline=False)
        embed.add_field(name="Word Filter", value=f"`{prefix}addfilter word`, `{prefix}removefilter word`, `{prefix}filterlist`", inline=False)
        embed.add_field(name="Security", value=f"`{prefix}lock`, `{prefix}unlock`, `{prefix}lockdown`, `{prefix}liftlockdown`", inline=False)
        embed.add_field(name="Utility", value=f"`{prefix}afk reason`, `{prefix}setprefix newprefix`, `{prefix}setlog #channel`, `{prefix}developer`", inline=False)
        embed.set_footer(text="Use slash or prefix commands (prefix can be changed per server)")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="ping", description="Check bot latency")
    async def ping(self, ctx: commands.Context):
        await ctx.reply(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")

    @commands.hybrid_command(name="announce", description="Send an announcement embed in a channel")
    @commands.has_permissions(manage_guild=True)
    async def announce(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str):
        embed = discord.Embed(title="📢 Announcement", description=message, color=0xFFA500)
        embed.set_footer(text=f"Announced by {ctx.author}")
        await channel.send(embed=embed)
        await ctx.reply(f"✅ Announcement sent to {channel.mention}")

    @commands.hybrid_command(name="alert", description="Send an alert embed in a channel")
    @commands.has_permissions(manage_guild=True)
    async def alert(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str):
        embed = discord.Embed(title="🚨 Alert", description=message, color=0xFF0000)
        embed.set_footer(text="Axis Alert System")
        await channel.send(embed=embed)
        await ctx.reply(f"✅ Alert posted in {channel.mention}")

    @commands.hybrid_command(name="dashboard", description="Show server dashboard stats")
    async def dashboard(self, ctx: commands.Context):
        guild = ctx.guild
        if not guild:
            return await ctx.reply("This command works only in servers.")
        embed = discord.Embed(title="📊 Axis Dashboard", color=0x00BFFF)
        embed.add_field(name="Server", value=guild.name, inline=False)
        embed.add_field(name="Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Text channels", value=str(len(guild.text_channels)), inline=True)
        embed.add_field(name="Boosts", value=str(guild.premium_subscription_count), inline=True)
        embed.add_field(name="Bot Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="smart", description="Ask the smart AI moderation helper")
    async def smart_ai(self, ctx: commands.Context, *, prompt: str):
        answer = """Smart AI: I can help moderate your server, manage giveaways, and respond quickly. Use `/axishelp` to see commands."""
        await ctx.reply(f"🤖 Smart AI response for: `{prompt}`\n{answer}")

    @commands.hybrid_command(name="invite", description="Get bot invite URL")
    async def invite(self, ctx: commands.Context):
        invite_url = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"
        await ctx.reply(f"Invite Axis to your server: {invite_url}")

    @commands.hybrid_command(name="support", description="Get support server link")
    async def support(self, ctx: commands.Context):
        await ctx.reply("Join support: https://discord.gg/axis-bot")

    @commands.hybrid_command(name="uptime", description="Show bot uptime status")
    async def uptime(self, ctx: commands.Context):
        await ctx.reply("Bot is online and running.")

    @commands.hybrid_command(name="botinfo")
    async def botinfo(self, ctx: commands.Context):
        embed = discord.Embed(title="Axis Bot", description="Advanced moderation and security bot", color=0x5865F2)
        embed.add_field(name="Owner", value="Swapnendu", inline=True)
        embed.add_field(name="Library", value="discord.py", inline=True)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="rank")
    async def rank(self, ctx: commands.Context):
        await ctx.reply("🏆 Axis Ranking: You're the server hero! Keep moderating.")

    @commands.hybrid_command(name="feedback")
    async def feedback(self, ctx: commands.Context, *, message: str):
        await ctx.guild.text_channels[0].send(f"📩 Feedback from {ctx.author}: {message}")
        await ctx.reply("✅ Feedback sent.")

    @commands.hybrid_command(name="team")
    async def team(self, ctx: commands.Context):
        embed = discord.Embed(title="Axis Team", description="Lead: Swapnendu | AI: Core Infrastructure", color=0x00FF00)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="stats")
    async def stats(self, ctx: commands.Context):
        await ctx.reply(f"📈 Stats: {len(self.bot.guilds)} servers, {len(self.bot.users)} users.")

    @commands.hybrid_command(name="supporters")
    async def supporters(self, ctx: commands.Context):
        await ctx.reply("⭐ Supporters: Swapnendu, Axis Team, Core AI Infrastructure")

    @commands.hybrid_command(name="echo")
    async def echo(self, ctx: commands.Context, *, message: str):
        await ctx.reply(message)

    @commands.hybrid_command(name="servericon")
    async def server_icon(self, ctx: commands.Context):
        await ctx.reply(ctx.guild.icon.url if ctx.guild.icon else "No icon")

    @commands.hybrid_command(name="rule")
    async def rule(self, ctx: commands.Context, *, content: str):
        await ctx.reply(embed=discord.Embed(title="Server Rule", description=content, color=0xFFD700))

    @commands.hybrid_command(name="banner")
    async def banner(self, ctx: commands.Context):
        await ctx.reply("https://i.imgur.com/axis-banner.png")

    @commands.hybrid_command(name="invitebot")
    async def invite_bot(self, ctx: commands.Context):
        await ctx.reply("https://discord.com/oauth2/authorize?...")

    @commands.hybrid_command(name="credits")
    async def credits(self, ctx: commands.Context):
        await ctx.reply("Axis Bot by Swapnendu with Core AI infrastructure.")


async def setup(bot):
    await bot.add_cog(Utility(bot))