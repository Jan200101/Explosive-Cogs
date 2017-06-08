import discord
from discord.ext import commands
from cogs.utils import checks
from cogs.utils.chat_formatting import box,  pagify, escape_mass_mentions
from random import choice, randint
import datetime

class EmbedNotification:
    """Makes the bot say things for in embeds"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True, aliases=['embedm'])
    @checks.admin_or_permissions(administrator=True)
    async def embednotification(self, ctx, text: str, color: str='000000',):
        """Says Something as the bot without any trace of the message author in a colored embed"""

        if ctx.message.server.me.bot: # Check if user is a bot. If the user is bot there is no need to check for this
            try:
                await self.bot.delete_message(ctx.message)
            except:
                await self.bot.send_message(ctx.message.author, 'I will stop embedding because I could not delete your message in {}'.format(ctx.message.channel.mention))
                return

        color = color[:6]
        color = color.replace("#", "")
        color = color.replace("0x", "")
        color = int(color, 16)

        randnum = randint(1, 10) # Generating a random number for a empty embed
        empty = u"\u2063"
        emptyrand = empty * randnum

        data = discord.Embed(description=str(
            text), colour=discord.Colour(value=color))

        try:
            await self.bot.say(emptyrand, embed=data)
        except:
            await self.bot.send_message(ctx.message.author,"I need the `Embed links` permission on `{}` to the embeded message".format(ctx.message.server))


def setup(bot):
    bot.add_cog(EmbedNotification(bot))
