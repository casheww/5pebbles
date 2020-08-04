import discord
from discord.ext import commands


class CustomContext(commands.Context):
    @property
    def colour(self):
        if self.guild:
            return self.guild.me.colour
        return discord.Colour(0x9886b4)
