import aiomediawiki.exceptions as wiki_errors
import asyncio
import discord
from discord.ext import commands, flags
from main import Pebbles
from src import wikiutils
from typing import Optional


class RainWorldWiki(commands.Cog):
    def __init__(self, bot: Pebbles):
        self.bot = bot


    @commands.command(description="Searches the wiki for results.",
                      aliases=["s"])
    async def search(self, ctx, limit: Optional[int], *, query):
        if len(query) > 40:
            return await ctx.send("Max. query length is 40 characters.")
        if limit is not None and limit not in range(1, 11):
            return await ctx.send("Search limit must be between 1 and 10 inclusive.")

        await ctx.trigger_typing()

        limit = limit if limit is not None else 5

        pages_str, page_dict = await wikiutils.get_page_refs(self.bot, limit, query)

        r = discord.Embed(colour=0x180d1f)
        r.add_field(name="Results", value=pages_str)
        r.set_footer(text="Reply with a number to get the summary of the corresponding page.")

        await ctx.send(embed=r)

        def check(m):
            return m.channel == ctx.channel and m.author.id == ctx.author.id

        try:
            reply = await self.bot.wait_for("message", check=check, timeout=30)

            if reply.content in page_dict.keys():
                page = await self.bot.wiki.get_page(pageid=page_dict[reply.content])

                r = wikiutils.RWPageEmbed(colour=0x2b2233)
                await r.format(page)

                await ctx.send(embed=r)

        except asyncio.TimeoutError:
            pass


    @commands.command(description="Searches the wiki for results. "
                                  "The first result is returned in detail.",
                      aliases=["p"])
    async def page(self, ctx, *, query: str):
        if len(query) > 40:
            return await ctx.send("Max. query length is 40 characters.")

        await ctx.trigger_typing()

        r = wikiutils.RWPageEmbed(colour=0x2b2233)

        try:
            if query.lower().startswith("looks to the moon"):
                query = query.lower().replace("looks to the moon", "Looks to the Moon")
            else:
                query = query.title()
                
            page = await self.bot.wiki.get_page(query)

        except wiki_errors.MissingPage:
            r.description = "Page not found :(\nMaybe you want one of these:"
            r.add_field(name=f"Search for {query}:", value=(await wikiutils.get_page_refs(self.bot, 5, query))[0])
            return await ctx.send(embed=r)

        await r.format(page)

        await ctx.send(embed=r)


    @commands.command(description="Provides creature stats from the wiki.",
                      aliases=["c"])
    async def creature(self, ctx, *, query):
        if len(query) > 40:
            return await ctx.send("Max. query length is 40 characters.")

        await ctx.trigger_typing()

        r = wikiutils.RWCreatureEmbed(colour=0x2b2233)

        try:
            if query.lower() in ["lttm", "looks to the moon"]:
                query = "Looks to the Moon (character)"
            else:
                query = query.title()

            page = await self.bot.wiki.get_page(query)
            if "Creatures" not in page.categories:
                raise wiki_errors.MissingPage

        except wiki_errors.MissingPage:
            r.description = "Creature page not found :(\nMaybe you want one of these:"
            r.add_field(name=f"Search for {query}:", value=(await wikiutils.get_page_refs(self.bot, 5, query))[0])
            return await ctx.send(embed=r)

        await r.format(page)

        await ctx.send(embed=r)


    @flags.add_flag("-t", action="store_true")
    @flags.add_flag("query", nargs="+")
    @flags.command(description="Provides region map and threats.",
                      aliases=["r"])
    async def region(self, ctx, **options):
        threat_toggle = options["t"]
        query = " ".join(options["query"])

        if len(query) > 40:
            return await ctx.send("Max. query length is 40 characters.")

        await ctx.trigger_typing()

        r = wikiutils.RWRegionEmbed(colour=0x33132d)

        try:
            found = False
            if query.lower() == "su":
                query = "Outskirts"
                found = True
            else:
                for region in wikiutils.region_dict.keys():
                    for alias in wikiutils.region_dict[region]:
                        if query.lower().startswith(alias):
                            query = region
                            found = True
                            break

            if not found:
                raise wiki_errors.MissingPage

        except wiki_errors.MissingPage:
            r.description = "Region page not found :(\nMaybe you want one of these:"
            r.add_field(name=f"Search for {query}:", value=(await wikiutils.get_page_refs(self.bot, 5, query))[0])
            return await ctx.send(embed=r)

        page = await self.bot.wiki.get_page(query)
        await r.r_format(page, threat_toggle)

        await ctx.send(embed=r)


def setup(bot):
    bot.add_cog(RainWorldWiki(bot))
