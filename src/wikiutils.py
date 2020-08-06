import aiohttp
from aiomediawiki import exceptions as wiki_errors
from bs4 import BeautifulSoup
import discord


async def get_page_refs(bot, limit, query):
    pages = []
    page_dict = {}
    page_number = 1
    async for page in await bot.wiki.search(query, limit=limit):
        pages.append(f"{page_number}. [{page.title}]({page.url})")
        page_dict[str(page_number)] = page.pageid
        page_number += 1

    if not pages:
        raise wiki_errors.MissingPage

    return "\n".join(pages), page_dict


async def parse_page(url):
    async with aiohttp.ClientSession() as client:
        async with client.get(url) as r:
            r = await r.text()

    return BeautifulSoup(r, features="html.parser")


def get_page_thumbnail(parsed: BeautifulSoup):
    img = parsed.find("img", attrs={"class": "thumbimage"})
    if img:
        return img.get("src")


async def get_creature_stats(parsed: BeautifulSoup):
    """ This was painful. """
    source_stats_tables = parsed.find_all("table", attrs={"class": "infoboxtable"})
    source_stats_tables = [x.find("tbody") for x in source_stats_tables]

    stats_blocks = []
    for t in source_stats_tables:
        stat_block = {}
        rows = t.find_all("tr")

        stat_block["Name"] = rows[0].text.strip("\n\"")

        for i in range(3, 6):
            try:
                parts = rows[i].text.split("\n")
                stat_block[parts[1]] = parts[2]
            except (IndexError, KeyError):
                pass
        stats_blocks.append(stat_block)

    return stats_blocks


class RWPageEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(kwargs=kwargs)

    async def rw_format(self, page):
        self.set_author(name=page.title, url=page.url)

        if len(page.summary) < 640:
            self.description = page.summary
        else:
            self.description = f"{page.summary[:640]}\n..."

        thumbnail_url = get_page_thumbnail(await parse_page(page.url))
        if thumbnail_url:
            self.set_thumbnail(url=thumbnail_url)

        if page.categories:
            self.set_footer(text=f"Categories: {', '.join(page.categories)}")