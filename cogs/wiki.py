import aiomediawiki.exceptions as wiki_errors
from discord.ext import commands, flags
from main import Pebbles
from src import wikiutils
from typing import Optional


class RainWorldWiki(commands.Cog):
    def __init__(self, bot: Pebbles):
        self.bot = bot


    @commands.command(description="Clears the bot's wiki cache.")
    @commands.check_any(commands.has_role(291207293905928193), commands.is_owner())
    async def clear_cache(self, ctx):
        self.bot.wiki.cache.clean()
        await ctx.send("cache cleared!")


    @commands.command(description="Searches the wiki for results.",
                      aliases=["s"])
    async def search(self, ctx, limit: Optional[int], *, query):
        if len(query) > 40:
            return await ctx.send("Max. query length is 40 characters.")
        if limit is not None and limit not in range(1, 11):
            return await ctx.send("Search limit must be between 1 and 10 inclusive.")

        await ctx.trigger_typing()

        limit = limit if limit is not None else 5
        await wikiutils.result_selector(ctx, limit, query, wikiutils.PageType.SearchResult)


    @commands.command(description="Searches the wiki for results. "
                                  "The first result is returned in detail.",
                      aliases=["p"])
    async def page(self, ctx, *, query: str):
        if len(query) > 40:
            return await ctx.send("Max. query length is 40 characters.")

        await ctx.trigger_typing()

        try:
            if query.lower().startswith("looks to the moon"):
                query = query.lower().replace("looks to the moon", "Looks to the Moon")
            else:
                query = query.title()

            r = wikiutils.RWPageEmbed(colour=0x2b2233)
            page = await self.bot.wiki.get_page(query)
            await r.format(page)
            await ctx.send(embed=r)

        except wiki_errors.MissingPage:
            await wikiutils.result_selector(ctx, 5, query, wikiutils.PageType.Page)


    @commands.command(description="Provides creature stats from the wiki.",
                      aliases=["c"])
    async def creature(self, ctx, *, query):
        if len(query) > 40:
            return await ctx.send("Max. query length is 40 characters.")

        await ctx.trigger_typing()

        try:
            if query.lower() in ["lttm", "looks to the moon"]:
                query = "Looks to the Moon (character)"
            else:
                query = query.title()

            page = await self.bot.wiki.get_page(query)

            if "Creatures" not in page.categories:
                raise wiki_errors.MissingPage

            r = wikiutils.RWCreatureEmbed(colour=0x2b2233)
            await r.format(page)
            await ctx.send(embed=r)

        except wiki_errors.MissingPage:
            await wikiutils.result_selector(ctx, 5, query, wikiutils.PageType.Creature)


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

        try:
            found = False
            if query.lower() == "su":
                query = "Outskirts"
                found = True
            elif query.lower() == "sh":
                query = "Shaded Citadel"
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

            r = wikiutils.RWRegionEmbed(colour=0x33132d)
            page = await self.bot.wiki.get_page(query)
            await r.r_format(page, threat_toggle)
            await ctx.send(embed=r)

        except wiki_errors.MissingPage:
            await wikiutils.result_selector(ctx, 5, query, wikiutils.PageType.Region, threats=threat_toggle)


def setup(bot):
    bot.add_cog(RainWorldWiki(bot))
