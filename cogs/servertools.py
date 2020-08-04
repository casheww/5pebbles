from datetime import datetime as dt
import db_interface
from discord.ext import commands
from main import Pebbles


class ServerTools(commands.Cog):
    def __init__(self, bot: Pebbles):
        self.bot = bot


    @staticmethod
    async def guild_setup(db, guild):
        info = {'info': {'name': guild.name, 'join': str(dt.now().strftime(f'%d/%m/%Y'))}}
        await db_interface.dump_guild_data(db, guild.id, info)


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.guild_setup(self.bot.db, guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await db_interface.delete_guild(self.bot.db, guild.id)


    @commands.command(description="Resets ALL the data stored by the bot about the guild. "
                                  "Use with caution.",
                      brief="Administrator permission required.")
    @commands.has_guild_permissions(administrator=True)
    async def reset_guild_data(self, ctx):
        await self.guild_setup(self.bot.db, ctx.guild)
        await ctx.send('Guild data has been reset.')


    @commands.command(description="Set a custom command prefix for this guild.",
                      brief="Manage Server permission required.")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_prefix(self, ctx, *, prefix: str = ""):
        if prefix == "" or len(prefix) > 10:
            await ctx.send("Please enter a custom command prefix. E.g.: `set_prefix !`. "
                           "Prefix must be less than 10 characters long.")
        else:
            guild_info = await db_interface.get_guild_data(self.bot.db, ctx.guild.id)
            guild_info['info']['prefix'] = prefix
            await db_interface.dump_guild_data(self.bot.db, ctx.guild.id, guild_info)
            self.bot.prefix_dict[ctx.guild.id] = prefix

            await ctx.send(f"Prefix set to: `{prefix}`")


def setup(bot):
    bot.add_cog(ServerTools(bot))
