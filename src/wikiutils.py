import aiohttp
from aiomediawiki import exceptions as wiki_errors
from bs4 import BeautifulSoup
import discord


region_dict = {
    "Chimney Canopy": ["cc", "chimney"],
    "Drainage System": ["ds", "drainage"],
    "Garbage Wastes": ["gw", "garbage"],
    "Industrial Complex": ["hi", "industrial"],
    "Farm Arrays": ["lf", "farm"],
    "Subterranean": ["sb", "sub"],
    "Filtration System": ["filtration"],
    "Depths": ["depths", "the depths"],
    "Shaded Citadel": ["sh", "shaded"],
    "Memory Crypts": ["mc", "memory cr"],
    "Sky Islands": ["si", "sky"],
    "Communications Array": ["communication"],
    "Shoreline": ["sl", "shoreline"],
    "Looks to the Moon (region)": ["looks", "lttm", "moon"],
    "Five Pebbles (region)": ["ss", "five", "fp", "5p"],
    "Recursive Transform Arrays": ["rta", "recursive"],
    "Unfortunate Development": ["ud", "unfortunate"],
    "Memory Conflux": ["memory co"],
    "General Systems Bus": ["gsb", "general"],
    "Outskirts": ["outskirts"],
    "The Exterior": ["uw", "exterior", "the exterior"],
    "The Leg": ["the leg", "leg"],
    "The Wall": ["the wall", "wall"],
    "The Underhang": ["the underhang", "underhang", "uh"]
}


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
        src = img["src"]
        try:
            src = "/".join(src.split("/")[:-4])
        except KeyError:
            pass
        return src


def get_region_map(parsed: BeautifulSoup):
    """ thanks Henpemaz """
    img = parsed.find("span", attrs={"id": "Map"}).parent.next_sibling.next_sibling.find("img")
    try:
        return img["src"]
    except KeyError:
        pass


def get_creature_stats(parsed: BeautifulSoup):
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


def get_region_threats(parsed: BeautifulSoup):
    paras = parsed.find_all("p")
    threats = {}

    for p in paras:
        if p.text.startswith("The following creatures"):
            level = p.text.split()[-2].title()
            threats[level] = []
            threat_list = p.next_sibling.next_sibling

            subspecies_count_to_ignore = 0

            for item in threat_list.find_all("li"):
                if subspecies_count_to_ignore > 0:
                    subspecies_count_to_ignore -= 1
                    continue

                if "\n" in item.text:
                    split = item.text.split("\n")
                    species = split[0]
                    subspecies = split[1:]
                    subspecies_count_to_ignore = len(subspecies)

                    threats[level].append(f"{species} {[s for s in subspecies]}")

                else:
                    threats[level].append(item.text)

    return threats


class RWPageEmbed(discord.Embed):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour


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


class RWRegionEmbed(discord.Embed):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour

    def format_threats(self, threats):
        for level in threats.keys():
            self.add_field(name=level,
                           value='\n'.join([f"- `{t}`" for t in threats[level]]),
                           inline=False)
