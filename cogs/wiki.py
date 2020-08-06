import aiomediawiki.exceptions as wiki_error
import asyncio
import discord
from discord.ext import commands
from main import Pebbles
from src import wikiutils
from typing import Optional


class RainWorldWiki(commands.Cog):
    def __init__(self, bot: Pebbles):
        self.bot = bot


    @commands.command(description="Searches the wiki for results.")
    async def search(self, ctx, limit: Optional[int], *, query):
        if len(query) > 40:
            return await ctx.send("Max. query length is 40 characters.")
        if limit is not None and limit not in range(1, 11):
            return await ctx.send("Search limit must be between 1 and 10 inclusive.")

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
                await r.rw_format(page)

                await ctx.send(embed=r)

        except asyncio.TimeoutError:
            pass



    @commands.command(description="Searches the wiki for results. "
                                  "The first result is returned in detail.")
    async def page(self, ctx, *, query):
        if len(query) > 40:
            return await ctx.send("Max. query length is 40 characters.")

        r = wikiutils.RWPageEmbed(colour=0x2b2233)

        try:
            page = await self.bot.wiki.get_page(query.title())

        except wiki_error.MissingPage:
            r.description = "Page not found :(\nMaybe you want one of these:"
            r.add_field(name=f"Search for {query}:", value=(await wikiutils.get_page_refs(self.bot, 5, query))[0])
            return await ctx.send(embed=r)

        await r.rw_format(page)

        await ctx.send(embed=r)


    @commands.command(description="Tries to find a matching creature from the wiki "
                                  "and return any stats provided.",
                      aliases=["c"])
    async def creature(self, ctx, *, query):
        if len(query) > 40:
            return await ctx.send("Max. query length is 40 characters.")

        r = discord.Embed(colour=0x2b2233)

        try:
            page = await self.bot.wiki.get_page(query.title())
            if "Creatures" not in page.categories:
                return await ctx.send("That page exists, but it's not a creature.")

        except wiki_error.MissingPage:
            return await ctx.send("That page doesn't exist.")

        r.set_author(name=page.title, url=page.url)

        parsed = await wikiutils.parse_page(page.url)

        stats_blocks = await wikiutils.get_creature_stats(parsed)
        for block in stats_blocks:
            for k in block.keys():
                r.add_field(name=k, value=block[k])
            r.add_field(name="\u200B", value="\u200B", inline=False)

        thumbnail_url = wikiutils.get_page_thumbnail(parsed)
        if thumbnail_url:
            r.set_thumbnail(url=thumbnail_url)

        await ctx.send(embed=r)



def setup(bot):
    bot.add_cog(RainWorldWiki(bot))
