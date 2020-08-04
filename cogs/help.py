import discord
from discord.ext import commands


hidden_cogs = ['Dev', 'EH', 'StatH', 'Help', 'Jishaku']


class CustomHelp(commands.HelpCommand):


    @staticmethod
    def plural_command(number: int):
        return "command" if number == 1 else "commands"


    @staticmethod
    def get_cog(cog_list, cog_name):
        """ Finds cog name in its own case from any casing.
            Just makes it easier for users to get help
            This originally-cased name is send to bot.get_cog() later. """
        for c in cog_list:
            if cog_name.lower() == c.lower():
                return c
        return None


    async def send_bot_help(self, mapping):

        ctx = self.context
        bot = ctx.bot
        destination = self.get_destination()

        try:
            desc = bot.description.replace("*", bot.get_user(bot.owner_id).mention)
        except AttributeError:
            desc = bot.description.replace("*", (await bot.fetch_user(444857307843657739)).mention)

        e = discord.Embed(colour=ctx.colour,
                          title=f"{bot.user.name} -- Bot help",
                          description=desc)

        for cog in mapping:
            if cog and cog.qualified_name not in hidden_cogs:
                cog_size = len(mapping[cog])

                for command in mapping[cog]:
                    if command.hidden:
                        cog_size -= 1

                e.add_field(name=f"{cog.qualified_name}", value=f"{cog_size} {self.plural_command(cog_size)}")

        e.set_footer(text="Try `help [category]` for a list of the category's commands.")

        await destination.send(embed=e)


    async def send_cog_help(self, cog):

        destination = self.get_destination()
        if cog.qualified_name in hidden_cogs:
            return await commands.HelpCommand.send_error_message(self,
                                                                 f'No command called "{cog.qualified_name}" found.')

        ctx = self.context

        e = discord.Embed(colour=ctx.colour,
                          title=cog.qualified_name,
                          description="*(category)*")

        cmd_list = await commands.HelpCommand.filter_commands(self, cog.get_commands())
        for command in cmd_list:
            e.add_field(name=f"{command.qualified_name}", value=f"{command.description.split('.')[0]}.")

        e.set_footer(text="Try `help [command/group]` for a more details.")

        await destination.send(embed=e)


    async def send_command_help(self, command):

        ctx = self.context
        destination = self.get_destination()

        if not command.parent:
            sig = [command.name, command.signature]
        else:
            sig = [command.full_parent_name, command.name, command.signature]

        e = discord.Embed(colour=ctx.colour,
                          title=command.qualified_name,
                          description=f"*(command)*\n{command.description}")
        e.add_field(name="Syntax", value=f"`{self.clean_prefix}{' '.join(sig)}`", inline=False)

        if command.brief:
            e.add_field(name="User conditions", value=f"{command.brief}", inline=False)

        if command.aliases:
            e.set_footer(text=f"Aliases: [{', '.join([a for a in command.aliases])}]")

        await destination.send(embed=e)


    async def send_group_help(self, group):

        ctx = self.context
        destination = self.get_destination()

        e = discord.Embed(colour=ctx.colour,
                          title=group.qualified_name,
                          description=f"*(command group)*\n{group.description}")
        e.add_field(name="User conditions", value=f"{group.brief}", inline=False)
        e.add_field(name="Subcommands", value=f"`{'`, `'.join([c.qualified_name for c in group.commands])}`",
                    inline=False)

        if group.aliases:
            e.set_footer(text=f"Aliases: [{', '.join([a for a in group.aliases])}]")

        await destination.send(embed=e)


    async def command_callback(self, ctx, *, command=None):
        """ Mostly the same as the original, but modified to use
            custom get_cog for case-insensitivity in cog searching.
            For that reason please excuse the bot/bot naming inconsistency."""

        await self.prepare_help_command(ctx, command)
        bot = ctx.bot

        if command is None:
            mapping = self.get_bot_mapping()
            return await self.send_bot_help(mapping)

        cog_name = self.get_cog(bot.cogs, command)
        if cog_name is not None:
            cog = bot.get_cog(cog_name)
            return await self.send_cog_help(cog)

        maybe_coro = discord.utils.maybe_coroutine

        keys = command.split(' ')
        cmd = bot.all_commands.get(keys[0])
        if cmd is None or cmd.hidden:
            string = await maybe_coro(self.command_not_found, self.remove_mentions(keys[0]))
            return await self.send_error_message(string)

        for key in keys[1:]:
            try:
                found = cmd.all_commands.get(key)
            except AttributeError:
                cmd_name = self.remove_mentions(key)
                return await commands.HelpCommand.send_error_message(self, f"No matches found.")
            else:
                if found is None:
                    cmd_name = self.remove_mentions(key)
                    return await commands.HelpCommand.send_error_message(self,
                                                                         f"No matches found.")
                cmd = found

        if isinstance(cmd, commands.Group):
            return await self.send_group_help(cmd)
        else:
            return await self.send_command_help(cmd)


    async def send_error_message(self, error):
        await self.get_destination().send(error)


class Help(commands.Cog):
    def __init__(self, bot):
        bot.help_command = CustomHelp()
        bot.help_command.cog = self


def setup(bot):
    bot.add_cog(Help(bot))
