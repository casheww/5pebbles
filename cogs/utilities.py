import datetime
import discord
from discord.ext import commands
from main import Pebbles
import platform


class Utilities(commands.Cog):
    def __init__(self, bot: Pebbles):
        self.bot = bot

    @commands.command(description="Returns the latency of the bot.")
    async def ping(self, ctx):
        await ctx.send(f"Pong! Bot latency: `{round(self.bot.latency * 1000)}ms`")


    @commands.command(description="Returns the uptime of the bot.")
    async def uptime(self, ctx):
        await ctx.send(f"Tick tock! Bot uptime: `{datetime.datetime.now() - self.bot.start_time}`")


    @commands.command(description="Returns bot info.")
    async def info(self, ctx):

        embed = discord.Embed(description=self.bot.description, colour=ctx.colour)
        embed.set_author(name=str(self.bot.user), url="https://www.github.com/casheww/kahu")
        embed.add_field(name="Users", value=str(len(self.bot.users)))
        embed.add_field(name="Guilds", value=str(len(self.bot.guilds)))
        embed.add_field(name="Support Guild", value="[Join here](https://discord.gg/qK5JkSG)")
        embed.add_field(name="\u200B", value=f"**Bot version**: {self.bot.version}\n"
                                             f"**Python**: {platform.python_version()} | "
                                             f"**discord.py**: {discord.__version__}")
        await ctx.send(embed=embed)


    @commands.command(description="Clears messages from the bot in the current channel. "
                                  "`limit` is the number of messages to check for bot authorship.",
                      brief="Manage Messages permission required.")
    @commands.has_permissions(manage_messages=True)
    async def clean(self, ctx, limit: int = 25):
        def check(m):
            return self.bot.user.id == m.author.id
        await ctx.channel.purge(limit=limit, check=check, bulk=False)


def setup(bot):
    bot.add_cog(Utilities(bot))
