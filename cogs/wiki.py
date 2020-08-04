import aiomediawiki.exceptions as wiki_error
import aiohttp
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
from main import Pebbles
from typing import Optional


class RainWorldWiki(commands.Cog):
    def __init__(self, bot: Pebbles):
        self.bot = bot


    async def get_pages(self, limit, query):
        pages = []
        async for page in await self.bot.wiki.search(query, limit=limit):
            pages.append(f"[{page.title}]({page.url})")

        if not pages:
            raise wiki_error.MissingPage

        return "\n".join(pages)


    @staticmethod
    async def get_thumbnail(url):
        async with aiohttp.ClientSession() as client:
            async with client.get(url) as r:
                r = await r.text()

        img = BeautifulSoup(r, features="html.parser").find("img", attrs={"class": "thumbimage"})

        if img:
            return img.get("src")


    @commands.command(description="Searches the wiki for results.")
    async def search(self, ctx, limit: Optional[int], *, query):
        if len(query) > 40:
            return await ctx.send("Max. query length is 40 characters.")

        limit = limit if limit is not None else 5

        pages_str = await self.get_pages(limit, query)

        r = discord.Embed(colour=0x180d1f)
        r.add_field(name="Results", value=pages_str)

        await ctx.send(embed=r)


    @commands.command(description="Searches the wiki for results. "
                                  "The first result is returned in detail.")
    async def page(self, ctx, *, query):
        if len(query) > 40:
            return await ctx.send("Max. query length is 40 characters.")

        r = discord.Embed(colour=0x2b2233)

        try:
            page = await self.bot.wiki.get_page(query.title())

        except wiki_error.MissingPage:
            r.description = "Page not found :(\nMaybe you want one of these:"
            r.add_field(name=f"Search for {query}:", value=await self.get_pages(5, query))
            return await ctx.send(embed=r)

        r.set_author(name=page.title, url=page.url)

        if len(page.summary) < 640:
            r.description = page.summary
        else:
            r.description = f"{page.summary[:640]}\n..."

        thumbnail_url = await self.get_thumbnail(page.url)
        if thumbnail_url:
            r.set_thumbnail(url=thumbnail_url)

        if page.categories:
            r.set_footer(text=f"Categories: {', '.join(page.categories)}")

        await ctx.send(embed=r)


def setup(bot):
    bot.add_cog(RainWorldWiki(bot))
