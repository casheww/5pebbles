from discord.ext import commands
import json
import os
from rw_wiki_bot import Pebbles


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
