import aiomediawiki.exceptions as wiki_error
from discord.ext import commands
import traceback as tb


class EH(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return

        em_dict = {
            commands.ExtensionNotFound: "The extension was not found.",
            commands.ExtensionAlreadyLoaded: "The extension is already loaded.",
            commands.NoEntryPointError: "The extension does not have a setup function.",
            commands.ExtensionFailed: "The extension or its setup function had an execution error.",
            commands.ExtensionNotLoaded: "That extension is not loaded.",

            commands.UserInputError: "Hmm... Something you entered wasn't quite right. Try `help [command]`.",
            commands.NotOwner: "Only the owner of the bot can use this command.",
            commands.NoPrivateMessage: "This command can't be used outside of a server.",

            wiki_error.MissingPage: "No results found :("
        }

        for e in em_dict:
            if isinstance(error, e):
                await ctx.send(em_dict[e])
                return

        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"Please stop clattering through my internals. "
                                  f"Cooldown: `{round(error.retry_after, 2)}s`",
                                  delete_after=4)

        if isinstance(error, commands.CheckFailure):
            if hasattr(ctx, "custom_check_fail"):
                msg = ctx.custom_check_fail
            else:
                msg = "The requirements to run this command were not satisfied."
            await ctx.send(msg)
            return

        await ctx.send("Whoops, something went wrong. Developer has been notified.", delete_after=10)
        error_string = f"command: {ctx.command}\n```{''.join(tb.format_exception(type(error), error, error.__traceback__))}```"
        await (await self.bot.application_info()).owner.send(error_string)


def setup(bot):
    bot.add_cog(EH(bot))
