from datetime import datetime as dt
from discord.ext import commands
from main import Pebbles


class ServerTools(commands.Cog):
    def __init__(self, bot: Pebbles):
        self.bot = bot


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.drop_guild(guild.id)


    @commands.command(description="Resets ALL the data stored by the bot about the guild. "
                                  "Use with caution.",
                      brief="Administrator permission required.")
    @commands.has_guild_permissions(administrator=True)
    async def reset_guild_data(self, ctx):
        await self.bot.drop_guild(ctx.guild.id)
        await ctx.send('Guild data has been reset.')


    @commands.command(description="Set a custom command prefix for this guild. "
                                  "To add trailing whitespace, enter the new prefix "
                                  "as in-line code, e.g. \\`rain \\`",
                      brief="Manage Server permission required.")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_prefix(self, ctx, *, prefix: str = ""):
        if prefix == "" or len(prefix) > 10:
            return await ctx.send("Please enter a custom command prefix. E.g.: `set_prefix \\`!\\``. "
                           "Prefix length must be 10 characters or fewer.")

        prefix = prefix.strip("`")
        await self.bot.set_guild_prefix(ctx.guild.id, prefix)
        await ctx.send(f"Prefix set to: `{prefix}`")


def setup(bot):
    bot.add_cog(ServerTools(bot))
