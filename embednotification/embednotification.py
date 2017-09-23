from random import choice, randint
from discord.ext import commands
from discord import Colour, errors, Embed
from cogs.utils import checks

class EmbedNotification:
    """Make announcements in embeds"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True, aliases=['embedm'])
    @checks.admin_or_permissions(administrator=True)
    async def embednotification(self, ctx, text: str, color: str = '000000'):
        """Send a embed useful for announcements"""

        try:
            await self.bot.delete_message(ctx.message)
        except errors.Forbidden:
            if ctx.message.server.me.bot:
                dest = ctx.message.author
                msg = ('I need the `Manage Messages` permission on `{}` '
                       'to delete your message before it gets embeded.\n'
                       'This is done to ensure the bots embed is in '
                       'the same position your command was in.'
                      ).format(ctx.message.channel.name)
            else:
                dest = ctx.message.channel
                msg = ('Your selfbot/This userbot is '
                       'able to be used by others.\n'
                       'This is breaking Discord\'s TOS and '
                       'can be punished by them.\n'
                       'This message was sent by embednotification.py')

            await self.bot.send_message(dest, msg)
            return

        try:
            color = color.replace("#", "").replace("0x", "")[:6]
            color = int(color, 16)
        except ValueError:
            color = '000000'

        normaltext = u"\u2063" * randint(1, 10) # Generating a random amount of nothing

        data = Embed(description=str(text), colour=Colour(value=color))

        try:
            await self.bot.say(normaltext, embed=data)
        except errors.Forbidden:
            await self.bot.send_message(ctx.message.author,
                                        "I need the `Embed links` permission on `{}`"
                                        "to embed your message"
                                        "".format(ctx.message.server))

    @commands.command(hidden=True, pass_context=True, no_pm=True)
    async def embedsay(self, ctx, *, text: str):
        """The good old embedsay from Sentry-Cogs brought into embednotification.
        This Version has all features from embedsayadmin for normal and selfbots
        and it does not face the same restrictions as embednotifications."""

        try:
            await self.bot.delete_message(ctx.message)
        except errors.Forbidden:
            if ctx.message.server.me.bot:
                dest = ctx.message.author
                msg = ('I need the `Manage Messages` permission on `{}` '
                       'to delete your message before it gets embeded.\n'
                       'This is done to ensure the bots embed is in '
                       'the same position your command was in.'
                      ).format(ctx.message.channel.name)
            else:
                dest = ctx.message.channel
                msg = ('Your selfbot/This userbot is '
                       'able to be used by others.\n'
                       'This is breaking Discord\'s TOS and '
                       'can be punished by them.\n'
                       'This message was sent by embednotification.py')

            await self.bot.send_message(dest, msg)
            return

        normaltext = u"\u2063" * randint(1, 10) # Generating a random amount of nothing

        colour = int(''.join([choice('0123456789ABCDEF') for x in range(5)]), 16)
        data = Embed(description=str(text), colour=Colour(value=colour))
        if ctx.message.server.me.bot:
            data.set_author(name=ctx.message.author.display_name)

        try:
            await self.bot.say(normaltext, embed=data)
        except errors.Forbidden:
            await self.bot.send_message(ctx.message.author,
                                        "I need the `Embed links` permission on `{}`"
                                        " to embed your message".format(ctx.message.server))

def setup(bot):
    bot.add_cog(EmbedNotification(bot))
