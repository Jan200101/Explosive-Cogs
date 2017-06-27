import discord
from discord.ext import commands
from cogs.utils import checks
from cogs.utils.chat_formatting import box,  pagify, escape_mass_mentions
from random import choice, randint
import datetime

class EmbedNotification:
    """Make announcements in embeds"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True, aliases=['embedm'])
    @checks.admin_or_permissions(administrator=True)
    async def embednotification(self, ctx, text: str, color: str='000000', *, ignore_deletion=False, normaltext:str=None):
        """Send a embed useful for announcements"""

        if ctx.message.server.me.bot: # Check if user is a bot. If the user is bot there is no need to check for this
            try:
                await self.bot.delete_message(ctx.message)
            except:
                if not ignore_deletion:
                    await self.bot.send_message(ctx.message.author, 'I need the `Embed links` permission on `{}` to delete your message before it gets embeded.\n'
                                                                    'This is done to ensure the bots embed is in the same position your command was in.'.format(ctx.message.channel.mention))
                    return
        else:
            try:
                await self.bot.delete_message(ctx.message)
            except:
                await self.bot.send_message(ctx.message.server.get_member(self.bot.settings.owner), 'Your selfbot/This userbot is able to be used by others.\nThis is breaking Discords TOS and can be punished by them.\nThis messagte was send my embednotification.py')
                return

        color = color[:6]
        color = color.replace("#", "")
        color = color.replace("0x", "")
        color = int(color, 16)

        if not normaltext:
            normaltext = u"\u2063" * randint(1, 10) # Generating a random number for a empty embed

        data = discord.Embed(description=str(text), colour=discord.Colour(value=color))

        try:
            await self.bot.say(normaltext, embed=data)
        except:
            await self.bot.send_message(ctx.message.author, "I need the `Embed links` permission on `{}` to embed your message".format(ctx.message.server))

    @commands.command(hidden=True, pass_context=True, no_pm=True)
    @checks.is_owner()
    async def embedsay(self, ctx, *, text: str):
        """The good old embedsay from Sentry-Cogs brought into embednotification.
        This Version has all features from embedsayadmin for normal and selfbots
        and it does not face the same restrictions as embednotifications."""

        colour = ''.join([choice('0123456789ABCDEF') for x in range(5)])
        colour = int(colour, 16)
        await ctx.invoke(self.embednotification, text=text, color=str(colour), ignore_deletion=True)

def setup(bot):
    bot.add_cog(EmbedNotification(bot))
