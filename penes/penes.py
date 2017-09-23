import discord
from discord.ext import commands
import random
import hashlib

class Penes:
    """Like Penis but using Hash"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def penes(self, user : discord.Member):
        """Detects the users internet penis length\nEvery Willy will be huge and unrealistic"""
        pl = 0
        for x in str(int(hashlib.sha1(user.id.encode('utf-8')).hexdigest(), 16) % (10 ** 8)):
            pl += int(x)
        pl -= len(user.id)
        p = "8" + "="*pl + "D"
        await self.bot.say("Size: " + p)

def setup(bot):
    bot.add_cog(Penes(bot))
