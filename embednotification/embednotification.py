from random import choice, randint
from discord.ext import commands
import discord
from cogs.utils import checks

class EmbedNotification:
    """Make announcements in embeds"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True, aliases=['embedm'])
    @checks.admin_or_permissions(administrator=True)
    async def embednotification(self, ctx, text: str, color: str = '000000'):
        """Send a embed useful for announcements"""

        if ctx.message.server.me.bot:
            try:
                await self.bot.delete_message(ctx.message)
            except:
                await self.bot.send_message(ctx.message.author,
                                            'I need the `Manage Messages` permission on `{}`'
                                            'to delete your message before it gets embeded.\n'
                                            'This is done to ensure the bots embed is in'
                                            'the same position your command was in.'
                                            ''.format(ctx.message.channel.mention))
                return
        else:
            try:
                await self.bot.delete_message(ctx.message)
            except:
                await self.bot.send_message(ctx.message.channel,
                                            'Your selfbot/This userbot is '
                                            'able to be used by others.\n'
                                            'This is breaking Discords TOS and'
                                            ' can be punished by them.\n'
                                            'This messagte was send by embednotification.py')

                return
            
        if not color.replace("#", "").replace("0x", "").isdigit():
            color = '000000'
            
        color = color.replace("#", "").replace("0x", "")[:6]
        color = int(color, 16)

        normaltext = u"\u2063" * randint(1, 10) # Generating a random number for a empty embed

        data = discord.Embed(description=str(text), colour=discord.Colour(value=color))

        try:
            await self.bot.say(normaltext, embed=data)
        except:
            await self.bot.send_message(ctx.message.author,
                                        "I need the `Embed links` permission on `{}`"
                                        "to embed your message"
                                        "".format(ctx.message.server))

    @commands.command(hidden=True, pass_context=True, no_pm=True)
    @checks.is_owner()
    async def embedsay(self, ctx, *, text: str):
        """The good old embedsay from Sentry-Cogs brought into embednotification.
        This Version has all features from embedsayadmin for normal and selfbots
        and it does not face the same restrictions as embednotifications."""

        try:
            await self.bot.delete_message(ctx.message)
        except:
            await self.bot.send_message(ctx.message.server.get_member(self.bot.settings.owner),
                                        'Your selfbot/This userbot is able to be used by others.\n'
                                        'This is breaking Discords TOS and can be punished by them.'
                                        '\nThis messagte was send my embednotification.py')
            return

        normaltext = u"\u2063" * randint(1, 10) # Generating a random number for a empty embed

        data = discord.Embed(description=str(text), colour=discord.Colour(value=int(''.join([choice('0123456789ABCDEF') for x in range(5)]), 16)))

        try:
            await self.bot.say(normaltext, embed=data)
        except:
            await self.bot.send_message(ctx.message.author,
                                        "I need the `Embed links` permission on `{}`"
                                        " to embed your message".format(ctx.message.server))

def setup(bot):
    bot.add_cog(EmbedNotification(bot))
