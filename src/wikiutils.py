import aiohttp
from aiomediawiki import exceptions as wiki_errors
from aiomediawiki.page import MediaWikiPage
import asyncio
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
import enum


class PageType(enum.Enum):
    Page = 1
    Creature = 2
    Region = 3
    SearchResult = 4


categories = {
    PageType.Page: None,
    PageType.Creature: "Creatures",
    PageType.Region: "Regions",
    PageType.SearchResult: None
}

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
    "Outskirts": ["outskirts"],     # 'su' code is special case bc of overlap w subterranean name - check in wiki.py
    "The Exterior": ["uw", "exterior", "the exterior"],
    "The Leg": ["the leg", "leg"],
    "The Wall": ["the wall", "wall"],
    "The Underhang": ["the underhang", "underhang", "uh"]
}


async def result_selector(ctx: commands.Context, limit: int, query: str, page_type: PageType, *, threats=False):
    pages_str, page_dict = await get_page_refs(ctx.bot, limit, query, page_type=page_type)

    embed = discord.Embed(colour=0x180d1f)

    if page_type is PageType.SearchResult:
        embed.add_field(name="Search", value=pages_str)

    else:
        embed.description = "Page not found :(\nMaybe you want one of these:"
        embed.add_field(name=f"Search for {query}:", value=pages_str)

    embed.set_footer(text="Reply with a number to correct to the corresponding page.")
    await ctx.send(embed=embed)

    page = await page_from_choice(ctx, page_dict)
    if not page:
        return

    p_type_map = {
        PageType.Page: RWPageEmbed,
        PageType.Creature: RWCreatureEmbed,
        PageType.Region: RWRegionEmbed,
        PageType.SearchResult: RWPageEmbed,
    }
    embed = p_type_map[page_type](colour=0x2b2233)

    if isinstance(embed, RWRegionEmbed):
        await embed.r_format(page, threats)
    else:
        await embed.format(page)

        if page_type is PageType.SearchResult:
            if "Regions" in page.categories:
                embed = RWRegionEmbed(colour=0x2b2233)
                await embed.r_format(page, threats)

            elif "Creatures" in page.categories:
                creature_stats = await creature_special_ask(ctx)
                if creature_stats:
                    embed = RWCreatureEmbed(colour=0x2b2233)
                    await embed.format(page)

    await ctx.send(embed=embed)


async def page_from_choice(ctx: commands.Context, page_dict):
    def check(m):
        return m.channel == ctx.channel and m.author.id == ctx.author.id

    try:
        reply = await ctx.bot.wait_for("message", check=check, timeout=30)

        if reply.content in page_dict.keys():
            return await ctx.bot.wiki.get_page(pageid=page_dict[reply.content])

    except asyncio.TimeoutError:
        pass


async def creature_special_ask(ctx: commands.Context):
    await ctx.send("Do you want the creature stats?\n"
                   "If no, the page summary will be returned instead.")

    def check(m):
        return m.channel == ctx.channel and m.author.id == ctx.author.id and \
            m.content.lower() in ["y", "yes", "n", "no"]


    answer = await ctx.bot.wait_for("message", check=check, timeout=30)
    if answer.content.lower() in ["y", "yes"]:
        return True
    return False


async def get_page_refs(bot, limit, query, *, page_type: PageType):
    pages = []
    page_dict = {}
    page_number = 1
    async for page in await bot.wiki.search(query, limit=limit):
        if categories[page_type] is None or categories[page_type] in page.categories:
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
    img = parsed.find("a", attrs={"class": "image"})
    if img:
        src = img.next_element["src"]
        try:
            src = "/".join(src.split("/")[:-4])
        except KeyError:
            pass
        return src


def get_region_map(parsed: BeautifulSoup):
    """ thanks Henpemaz """
    try:
        img = parsed.find("span", attrs={"id": "Map"}).parent.next_sibling.next_sibling.find("img")
    except AttributeError:
        img = parsed.find("img", attrs={"class": "thumbimage"})
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


class RWBaseEmbed(discord.Embed):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour

    def add_hyperlink(self, url):
        hyper = f"\n\n[View this page]({url})"
        if len(self.fields) == 0:
            self.description += hyper
        else:
            f_name = self.fields[-1].name
            f_value = self.fields[-1].value
            self.remove_field(-1)
            self.add_field(name=f_name,
                           value=f_value+hyper)

    async def format(self, page):
        ...


class RWPageEmbed(RWBaseEmbed):
    def __init__(self, colour):
        super().__init__(colour)

    async def format(self, page):
        self.set_author(name=page.title, url=page.url)

        if len(page.summary) < 640:
            self.description = page.summary
        else:
            self.description = f"{page.summary[:600]}\n..."

        thumbnail_url = get_page_thumbnail(await parse_page(page.url))
        if thumbnail_url:
            self.set_thumbnail(url=thumbnail_url)

        if page.categories:
            self.set_footer(text=f"Categories: {', '.join(page.categories)}")

        self.add_hyperlink(page.url)


class RWCreatureEmbed(RWBaseEmbed):
    def __init__(self, colour):
        super().__init__(colour)

    async def format(self, page):
        self.set_author(name=page.title, url=page.url)
        parsed = await parse_page(page.url)

        if page.title == "Lizards":
            self.description = "There are many different types of lizards in Rain World. " \
                            "To see their stats, be specific: e.g. `creature green lizard`!"

        else:
            stats_blocks = get_creature_stats(parsed)

            if stats_blocks:
                for block in stats_blocks:
                    for k in block.keys():
                        self.add_field(name=k, value=block[k])

            else:
                if page.title == "Five Pebbles (character)":
                    self.description = "Ah, that's me."
                elif page.title == "Looks to the Moon (character)":
                    self.description = "Looks to the Moon... her state is considerably worse than mine."
                else:
                    self.description = "No data was found for this creature..."

        thumbnail_url = get_page_thumbnail(parsed)
        if thumbnail_url:
            self.set_thumbnail(url=thumbnail_url)
        self.add_hyperlink(page.url)


class RWRegionEmbed(RWBaseEmbed):
    def __init__(self, colour):
        super().__init__(colour)

    async def r_format(self, page, threat_toggle: bool):
        self.set_author(name=page.title, url=page.url)
        parsed = await parse_page(page.url)

        self.description = f"{page.summary.split('.')[0]}."

        if threat_toggle:
            threat_dict = get_region_threats(parsed)
            self.format_threats(threat_dict)
        else:
            self.set_footer(text="Add `-t` to your command call to see the region's threats.")

        img_url = get_region_map(parsed)
        if img_url:
            self.set_image(url=img_url)

        self.add_hyperlink(page.url)

    def format_threats(self, threats):
        for level in threats.keys():
            self.add_field(name=level,
                           value='\n'.join([f"- `{t}`" for t in threats[level]]),
                           inline=False)
