from discord.ext import commands
import aiohttp
from os import listdir
from __main__ import set_cog
from .utils.checks import is_owner

__author__ = 'Sentry#4141'

class DragDrop:
    """Drag a cog into discord and get it running"""

    def __init__(self, bot):
        self.bot = bot

    @is_owner()
    @commands.command(pass_context=True)
    async def drop(self, ctx):

        await self.bot.say('Drop a cog into Discord')
        msg = await self.bot.wait_for_message(author=ctx.message.author,
                                              channel=ctx.message.channel,
                                              check=lambda m: any(m.attachments),
                                              timeout=15)
        if msg is None:
            await self.bot.say('No cog recieved')
        elif msg.attachments[0]['filename'].endswith('.py'):
            if msg.attachments[0]['filename'] in listdir('cogs'):
                await self.bot.say(msg.attachments[0]['filename'][:-3] + ' is already installed.\nOverwrite it? (yes/no)')
                answer = await self.bot.wait_for_message(timeout=15, author=ctx.message.author)
                if answer is None:
                    await self.bot.say('Keeping old cog.')
                    return
                elif answer.content.lower().strip() == "no":
                    await self.bot.say('Keeping old cog.')
                    return

            gateway = msg.attachments[0]['url']
            payload = {}
            payload['limit'] = 1
            headers = {'user-agent': 'Python-Red-cog/2.0'}

            session = aiohttp.ClientSession()
            async with session.get(gateway, params=payload, headers=headers) as r:
                cog = await r.read()
                with open('cogs/' + msg.attachments[0]['filename'],  "w+b") as f:
                    f.write(cog)
                    await self.bot.say(msg.attachments[0]['filename'][:-3] + ' installed')
            session.close()

            await self.bot.say("Load it now? (yes/no)")
            cog = msg.attachments[0]['filename'][:-3]
            answer = await self.bot.wait_for_message(timeout=15, author=ctx.message.author)

            if answer is None:
                await self.bot.say("Ok then, you can load it with"
                                   " `{}load {}`".format(ctx.prefix, cog))
            elif answer.content.lower().strip() == "yes":
                set_cog("cogs." + cog, True)
                owner = self.bot.get_cog('Owner')
                await owner.load.callback(owner, cog_name=cog)
            else:
                await self.bot.say("Ok then, you can load it with"
                                   " `{}load {}`".format(ctx.prefix, cog))


            #ctx.invoke('load', cog_name=msg.attachments[0]['filename'])

        else:
            await self.bot.say('File is not a valid cog')

def setup(bot):
    bot.add_cog(DragDrop(bot))
