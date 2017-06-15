from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
from cogs.utils.chat_formatting import pagify, box
from subprocess import Popen, CalledProcessError, PIPE, STDOUT
from os.path import expanduser, exists
from os import makedirs, getcwd, chdir, listdir
from getpass import getuser
from platform import uname
from re import sub

class BetterTerminal:
    """Repl like Terminal in discord"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json('data/betterterminal/settings.json')
        self.prefix = self.settings['prefix']
        self.cc = self.settings['cc']
        self.os = self.settings['os']
        self.sessions = []

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def cmd(self, ctx):

        if ctx.message.channel.id in self.sessions:
            await self.bot.say('Already running a BetterTerminal session in this channel. Exit it with `quit`')
            return

        self.sessions.append(ctx.message.channel.id)
        await self.bot.say('Enter commands after {} to execute them. `exit()` or `quit` to exit.'.format(self.prefix.replace("`", "\\`")))


    @commands.group(pass_context=True)
    @checks.is_owner()
    async def cmdsettings(self, ctx):
        """Settings for BetterTerminal"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @cmdsettings.command(name="prefix", pass_context=True)
    async def _prefix(self, ctx, prefix:str):
        """Set the prefix for the Terminal"""

        self.prefix = prefix
        self.settings['prefix'] = self.prefix
        dataIO.save_json('data/betterterminal/settings.json', self.settings)
        await self.bot.say('Changed prefix to {} '.format(self.prefix.replace("`", "\\`")))

    async def on_message(self, message): # This is where the magic starts

        if message.channel.id in self.sessions: # Check if the current channel is the one cmd got started in

            #TODO:
            #  Whitelist & Blacklists


            if not self.prefix: # Making little 1337 Hax0rs not fuck this command up
                check_folder()
                check_file()

            if message.content.startswith(self.prefix) and message.author.id == self.bot.settings.owner:
                command = message.content.split(self.prefix)[1]
                # check if the message starts with the command prefix and if the bot owner is writing

                if not command: # if you have entered nothing it will just ignore
                    return


                if command == 'exit()' or command == 'quit':  # commands used for quiting cmd, same as for repl
                    await self.bot.send_message(message.channel, 'Exiting.')
                    self.sessions.remove(message.channel.id)
                    return

                if command.lower().find("apt-get install") != -1 and command.lower().find("-y") == -1:
                    command = "{} -y".format(command) # forces apt-get to not ask for a prompt

                if command in self.cc:
                    command = self.cc[command]

                if command.startswith('cd ') and command.split('cd ')[1]:
                    path = command.split('cd ')[1]
                    try:
                        chdir(path)
                        return
                    except:
                        if command.split('cd ')[1] in listdir():
                            shell = 'cd: {}: Permission denied'.format(command.split('cd ')[1])
                        else:
                            shell = 'cd: {}: No such file or directory'.format(command.split('cd ')[1])
                else:
                    try:
                        output = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT).communicate()[0] # This is what proccesses the commands and returns their output
                        error = False
                    except CalledProcessError as e:
                        output = e.output
                        error = True

                    shell = output.decode('utf_8')

                if shell == "" and not error: # check if the previous run command is giving output and is not a error
                    return

                shell = sub('/bin/sh: .: ', '', shell)
                if "\n" in shell[:-2]:
                    shell = '\n' + shell

                os = uname()[0].lower()

                if os.lower() in self.os:
                    path = getcwd()
                    username = getuser()
                    system = uname()[1]
                    user = self.os[os.lower()].format(user=username, system=system, path=path)
                else:
                    path = getcwd()
                    username = getuser()
                    system = uname()[1]
                    user = self.os['linux'].format(user=username, system=system, path=path)

                for page in pagify(user + shell, shorten_by=12):
                    await self.bot.send_message(message.channel, box(page, 'Bash'))


def check_folder():
    if not exists("data/betterterminal"):
        print("[Terminal]Creating data/betterterminal folder...")
        makedirs("data/betterterminal")


def check_file():
    jdict = {
        "prefix":">",
        "cc":{'test':'printf "Hello.\nThis is a custom command made using the magic of ~~unicorn poop~~ python.\nLook into /data/BetterTerminal'},
        "os":{
            'windows':'{path}>',
            'linux':'{user}@{system}:{path} $ '
            }
        }

    if not dataIO.is_valid_json("data/betterterminal/settings.json"):
        print("[BetterTerminal]Creating default settings.json...")
        dataIO.save_json("data/betterterminal/settings.json", jdict)


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(BetterTerminal(bot))
