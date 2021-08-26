from aiomediawiki import MediaWiki
import aiosqlite
from datetime import datetime
import db_interface
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
                                     "Written by casheww in Python. Completely unofficial.")

        self.db = None
        self.log_id = 584971929778257930
        self.prefix_dict = {}
        self.start_time = datetime.now()
        self.version = version
        self.wiki = MediaWiki(url="https://rainworld.miraheze.org/w/api.php")


    async def get_prefix(self, message):
        default_prefix = "rain "

        if message.guild:
            try:
                return self.prefix_dict[message.guild.id]
            except (KeyError, TypeError):
                pass

        return default_prefix


    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CustomContext)


    async def on_ready(self):
        print(f"===== ON_READY =====\n"
              f"\tlogged in as:\t{self.user}\n"
              f"\tid:\t\t{self.user.id}\n"
              f"\tdt:\t\t{self.start_time}\n\n")


    async def startup(self):
        await self.wait_until_ready()

        log_ch = self.get_channel(self.log_id)

        self.db = await aiosqlite.connect("db/bot.db")

        data = await db_interface.get_all_guilds(self.db)
        for entry in data:
            try:
                prefix = json.loads(entry[1])["info"]["prefix"]
                self.prefix_dict[entry[0]] = prefix
            except KeyError:
                pass

        await log_ch.send("bot started")


if __name__ == "__main__":
    with open("_keys.json") as f:
        keys = json.load(f)
        token = keys["discord"]
        v = keys["version"]

    bot = Pebbles(version=v)
    _cd = commands.CooldownMapping.from_cooldown(3, 12, commands.BucketType.user)
    _cd_rw_guild = commands.CooldownMapping.from_cooldown(1, 15, commands.BucketType.user)

    @bot.check
    async def cooldown_check(ctx):
        if ctx.guild.id == 291184728944410624:
            bucket = _cd_rw_guild.get_bucket(ctx.message)
        else:
            bucket = _cd.get_bucket(ctx.message)

        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        return True

    bot.load_extension("jishaku")
    for ext in os.listdir("cogs"):
        if ext.endswith(".py"):
            bot.load_extension(f"cogs.{ext[:-3]}")

    bot.loop.create_task(bot.startup())

    bot.run(token)
