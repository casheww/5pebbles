from aiomediawiki import MediaWiki
import aiosqlite
from datetime import datetime
import discord
from discord.ext import commands
import json
import os
from src.context import CustomContext


class Pebbles(commands.Bot):
    def __init__(self, version):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=self.get_prefix,
                         case_insensitive=True,
                         intents=intents,
                         description="A bot that interacts with the Rain World wiki. "
                                     "Written by casheww with discord.py and jucacrispim/aiomediawiki.")

        self.db = None
        self.default_command_prefix = "rwiki "
        self.log_ids = [675626519451795458]
        self.prefix_dict = {}
        self.start_time = datetime.now()
        self.version = version
        self.wiki = MediaWiki(url="https://rainworld.miraheze.org/w/api.php")


    async def startup(self):
        print("wait_until_ready...")
        await self.wait_until_ready()
        print("setting up")

        self.db = await aiosqlite.connect("prefixes.db")

        for data in await self.fetch_all_guild_data():
            self.prefix_dict[data[0]] = data[1]

        print("prefix dict populated")

        for log_id in self.log_ids:
            await (self.get_channel(log_id)).send("bot started")
        print("setup done")


    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CustomContext)


    async def get_prefix(self, message):
        if message.guild and message.guild.id in self.prefix_dict.keys():
            return self.prefix_dict[message.guild.id]

        return self.default_command_prefix


    # prefix database methods:

    async def fetch_all_guild_data(self):
        async with self.db.cursor() as c:
            await c.execute("SELECT * FROM PREFIXES")
            return await c.fetchall()
    
    async def fetch_guild_prefix(self, guild_id: int) -> str:
        async with self.db.cursor() as c:
            await c.execute("SELECT prefix FROM PREFIXES WHERE guildID=?;", [guild_id])
            return await c.fetchall()

    async def set_guild_prefix(self, guild_id: int, prefix: str):
        self.prefix_dict[guild_id] = prefix

        existing_prefix = await self.fetch_guild_prefix(guild_id)
        
        async with self.db.cursor() as c:
            if not existing_prefix:
                await c.execute("INSERT INTO PREFIXES VALUES (?, ?);", [guild_id, prefix])
            else:
                await c.execute("UPDATE PREFIXES SET prefix=? WHERE guildID=?;", [prefix, guild_id])
        
        await self.db.commit()

    async def drop_guild(self, guild_id: int):
        if not await self.fetch_guild_prefix(guild_id):
            return

        del self.prefix_dict[guild_id]
        
        async with self.db.cursor() as c:
            await c.execute("DELETE FROM PREFIXES WHERE guildID=?;", [guild_id])
        await self.db.commit()
