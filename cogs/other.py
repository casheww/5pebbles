import discord
from discord.ext import commands
import functools
from io import BytesIO
import os
from PIL import Image
import re


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def gen_rwtext_image(text: str):
        available_letters = [fp[:1] for fp in os.listdir("./assets")]
        img = Image.new("RGBA", (70 * len(text), 60), (1, 0, 0, 0))
        buffer = BytesIO()
        img.save(buffer, "png")

        proceeding_width = 0
        for i in range(len(text)):
            buffer.seek(0)
            img = Image.open(buffer)
            char = text[i]

            if char in available_letters:
                char_img = Image.open(f"./assets/{char}.png")
                if char == "t":
                    box = (proceeding_width - 5, 0)
                else:
                    box = (proceeding_width, 0)
                img.paste(char_img, box)

                proceeding_width += char_img.width + 10
                if char in ["f", "l", "r"]:
                    proceeding_width -= 2
                elif char in ["m", "w", "x"]:
                    proceeding_width -= 5

            elif char == " ":
                char_img = Image.new("RGBA", (25, 60), (1, 0, 0, 0))
                box = (proceeding_width, 0)
                img.paste(char_img, box)

                proceeding_width += char_img.width

            else:
                raise FileNotFoundError(text[i])

            buffer.seek(0)
            img.save(buffer, "png")

        buffer.seek(0)
        img = Image.open(buffer)
        img = img.crop((0, 0, proceeding_width, 60))
        buffer.seek(0)
        img.save(buffer, "png")
        buffer.seek(0)
        return buffer

    @staticmethod
    async def rwtext_check(ctx):
        if ctx.guild and ctx.guild.id == 291184728944410624:
            if 366341475522576386 not in [r.id for r in ctx.author.roles] \
                    and ctx.author.id != 444857307843657739:
                return False
        return True

    @commands.check(rwtext_check)
    @commands.command(description="Generates a Rain World style region title from text.")
    async def rwtext(self, ctx, *, text):
        await ctx.trigger_typing()
        # strip mid whitespace
        text = re.sub(r"\s+", " ", text)

        try:
            func = functools.partial(self.gen_rwtext_image, text.lower())
            buffer = await self.bot.loop.run_in_executor(None, func)
        except FileNotFoundError as e:
            return await ctx.send(f"The following character could not be converted: `{e.args[0]}`")

        await ctx.send(file=discord.File(buffer, f"{text[:6]}.png"))


def setup(bot):
    bot.add_cog(Misc(bot))
