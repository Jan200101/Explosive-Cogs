from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
from cogs.utils.chat_formatting import box
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
        self.settings = dataIO.load_json('data/betterterminal/settings.json') # Initial load of values making sure they are read right when the cog loads
        self.prefix = self.settings['prefix']
        self.cc = self.settings['cc']
        self.os = self.settings['os']
        self.enabled = self.settings['enabled']
        self.sessions = []

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def cmd(self, ctx):

        if ctx.message.channel.id in self.sessions:
            await self.bot.say('Already running a BetterTerminal session in this channel. Exit it with `quit`')
            return

        # Rereading the values that were already read in __init__ to ensure its always up to date
        try:
            self.settings = dataIO.load_json('data/betterterminal/settings.json')
        except:
            # Pretend its the worst case and reset the settings
            check_folder()
            check_file()
            self.settings = dataIO.load_json('data/betterterminal/settings.json')

        self.prefix = self.settings['prefix']
        self.cc = self.settings['cc']
        self.os = self.settings['os']

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

        if self.bot.user.id != message.author.id:
            return

        if message.channel.id in self.sessions and self.enabled: # Check if the current channel is the one cmd got started in

            #TODO:
            #  Whitelist & Blacklists that cant be modified by red

            def check(m):
                if m.content.strip().lower() == "more":
                    return True

            if not self.prefix: # Making little 1337 Hax0rs not fuck this command up
                check_folder()
                check_file()

            if message.content.startswith(self.prefix) or message.content.startswith('debugprefixcmd'):
                command = message.content.split(self.prefix)[1]
                # check if the message starts with the command prefix

                if not command: # if you have entered nothing it will just ignore
                    return


                if command == 'exit()':  # commands used for quiting cmd, same as for repl
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
                        if path in listdir() or path.startswith('/'):
                            shell = 'cd: {}: Permission denied'.format(path)
                        else:
                            shell = 'cd: {}: No such file or directory'.format(path)
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

                result = []
                in_text = text = user + shell
                shorten_by = 12
                page_length=2000
                num_mentions = text.count("@here") + text.count("@everyone")
                shorten_by += num_mentions
                page_length -= shorten_by
                while len(in_text) > page_length:
                    closest_delim = max([in_text.rfind(d, 0, page_length)
                                         for d in ["\n"]])
                    closest_delim = closest_delim if closest_delim != -1 else page_length
                    to_send = in_text[:closest_delim].replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
                    result.append(to_send)
                    in_text = in_text[closest_delim:]

                result.append(in_text.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere"))

                #result = list(pagify(user + shell, shorten_by=12))

                for x, output in enumerate(result):
                    if x % 2 == 0 and x != 0:
                        # TODO
                        #  Change it up to a reaction based system like repl
                        #  change up certain things. For example making a print template in the settings print character number not page number

                        note = await self.bot.send_message(message.channel, 'There are still {} pages left.\nType `more` to continue.'.format(len(result) - (x+1)))
                        msg = await self.bot.wait_for_message(author=message.author,
                                                      channel=message.channel,
                                                      check=check,
                                                      timeout=12)
                        if msg == None:
                            try:
                                await self.bot.delete_message(note)
                            except:
                                pass
                            finally:
                                break

                    await self.bot.send_message(message.channel, box(output, 'Bash'))



def check_folder():
    if not exists("data/betterterminal"):
        print("[Terminal]Creating data/betterterminal folder...")
        makedirs("data/betterterminal")

def check_file():
    jdict = {
        "prefix":">",
        "cc":{'test' : 'printf "Hello.\nThis is a custom command made using the magic of ~~unicorn poop~~ python.\nLook into /data/BetterTerminal"'},
        "os":{
            'windows':'{path}>',
            'linux':'{user}@{system}:{path} $ '
            },
        "enabled":True
        }

    if not dataIO.is_valid_json("data/betterterminal/settings.json"):
        print("[BetterTerminal]Creating default settings.json...")
        dataIO.save_json("data/betterterminal/settings.json", jdict)

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(BetterTerminal(bot))
