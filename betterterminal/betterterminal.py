from subprocess import Popen, CalledProcessError, PIPE, STDOUT
from re import sub
from os.path import exists
from os import makedirs, getcwd, chdir, listdir, popen as ospopen
from getpass import getuser
from platform import uname, python_version
from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import dataIO

__author__ = 'Sentry#4141'

class BetterTerminal:
    """Repl like Terminal in discord"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json('data/betterterminal/settings.json')
        self.prefix = self.settings['prefix']
        self.cc = self.settings['cc']
        self.os = self.settings['os']
        self.cos = self.settings['cos']
        self.enabled = self.settings['enabled']
        self.sessions = {}


    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def cmddebug(self, ctx):
        """This command is for debugging only"""
        try:
            commithash = ospopen('git rev-parse --verify HEAD').read()[:7]
        except:
            commithash = 'None'

        text = str('```'
                   'Bot Information\n\n'
                   'Bot name:           {}\n'
                   'Bot displayname:    {}\n\n'
                   'Operating System:   {}\n'
                   'OS Version:         {}\n'
                   'Archetecture:       {}\n\n'
                   'Python Version:     {}\n'
                   'Commit              {}\n'
                   '```'.format(ctx.message.server.me.name,
                                ctx.message.server.me.display_name,
                                uname()[0], uname()[3], uname()[4],
                                python_version(), commithash)
                  )




        result = []
        in_text = text
        shorten_by = 12
        page_length = 2000
        num_mentions = text.count("@here") + text.count("@everyone")
        shorten_by += num_mentions
        page_length -= shorten_by
        while len(in_text) > page_length:
            closest_delim = max([in_text.rfind(d, 0, page_length)
                                 for d in ["\n"]])
            closest_delim = closest_delim if closest_delim != -1 else page_length
            to_send = in_text[:closest_delim].replace(
                "@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
            result.append(to_send)
            in_text = in_text[closest_delim:]

        result.append(in_text.replace(
            "@everyone", "@\u200beveryone").replace("@here", "@\u200bhere"))

        for page in result:
            await self.bot.say(page)

    @commands.group(pass_context=True, hidden=True)
    @checks.is_owner()
    async def system(self, ctx):
        """Returns system infromation"""
        await self.bot.say('{} is running on {} {} using {}'
                           ''.format(ctx.message.server.me.display_name,
                                     uname()[0], uname()[2], python_version()))

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def cmd(self, ctx):
        """Starts up the prompt"""
        if ctx.message.channel.id in self.sessions:
            await self.bot.say('Already running a Terminal session '
                               'in this channel. Exit it with `exit()` or `quit`')
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

        self.sessions.update({ctx.message.channel.id:ctx.message.author.id})
        await self.bot.say('Enter commands after {} to execute them.'
                           ' `exit()` or `quit` to exit.'.format(self.prefix.replace("`", "\\`")))

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def cmdsettings(self, ctx):
        """Settings for BetterTerminal"""
        if ctx.invoked_subcommand is None:
            pages = self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await self.bot.send_message(ctx.message.channel, page)

    @cmdsettings.group(name="customcom", pass_context=True)
    @checks.is_owner()
    async def _cc(self, ctx):
        """Custom commands for BetterTerminal"""
        await self.bot.say('This feature is WIP')
        """
        if ctx.invoked_subcommand is None:
            pages = self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await self.bot.send_message(ctx.message.channel, page)
                """

    @cmdsettings.command(name="os", pass_context=True)
    @checks.is_owner()
    async def _os(self, ctx, os: str = None):
        """Set the prompt type of BetterTerminal to emulate another Operatingsystem.
        these 'emulations' arent 100% accurate on other Operatingsystems"""

        if os is None:
            pages = self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await self.bot.send_message(ctx.message.channel, page)
            if self.cos == 'default':
                await self.bot.say('```\nCurrent prompt type: {}[{}] ```\n'.format(self.cos, uname()[0].lower()))
            else:
                await self.bot.say('```\nCurrent prompt type: {} ```\n'.format(self.cos))
            return

        if not os.lower() in self.os:
            await self.bot.say('Invalid prompt type.\nThe following once are valid:\n\n{}'.format(", ".join(self.os)))
            return

        os = os.lower()

        if os == 'default':
            os = uname()[0].lower()

        self.cos = os
        self.settings['cos'] = os
        dataIO.save_json('data/betterterminal/settings.json', self.settings)
        await self.bot.say('Changed prompt type to {} '.format(self.cos.replace("`", "\\`")))

    @cmdsettings.command(name="prefix", pass_context=True)
    @checks.is_owner()
    async def _prefix(self, ctx, prefix: str = None):
        """Set the prefix for the Terminal"""

        if prefix is None:
            pages = self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await self.bot.send_message(ctx.message.channel, page)
            await self.bot.say('```\nCurrent prefix: {} ```\n'.format(self.prefix))
            return

        self.prefix = prefix
        self.settings['prefix'] = prefix
        dataIO.save_json('data/betterterminal/settings.json', self.settings)
        await self.bot.say('Changed prefix to {} '.format(self.prefix.replace("`", "\\`")))

    async def on_message(self, message): # This is where the magic starts

        if message.channel.id in self.sessions and self.enabled and message.author.id == self.bot.settings.owner: # I REPEAT DO NOT DELETE

            #TODO:
            #  Whitelist & Blacklists that cant be modified by the bot

            if not dataIO.is_valid_json("data/betterterminal/settings.json"):
                check_folder()
                check_file()
                self.settings = dataIO.load_json('data/betterterminal/settings.json')
                self.prefix = self.settings['prefix']
                self.cc = self.settings['cc']
                self.os = self.settings['os']
                self.cos = self.settings['cos']
                self.enabled = self.settings['enabled']

            if message.content.startswith(self.prefix) or message.content.startswith('debugprefixcmd'):
                if message.content.startswith(self.prefix):
                    command = message.content[len(self.prefix):]
                else:
                    command = message.content[len('debugprefixcmd'):]
                # check if the message starts with the command prefix

                if message.attachments:
                    command += ' ' + message.attachments[0]['url']

                if not command: # if you have entered nothing it will just ignore
                    return

                if command in self.cc:
                    if self.cc[command][uname()[0].lower()]:
                        command = self.cc[command][uname()[0].lower()]
                    else:
                        command = self.cc[command]['linux']

                if command == 'exit()' or command == 'quit':  # commands used for quiting cmd, same as for repl
                    await self.bot.send_message(message.channel, 'Exiting.')
                    self.sessions.pop(message.channel.id)
                    return
                elif commands == 'exit':
                    await self.bot.send_message(message.channel, "")
                if command.lower().find("apt-get install") != -1 and command.lower().find("-y") == -1:
                    command = "{} -y".format(command) # forces apt-get to not ask for a prompt

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
                        output = Popen(command, shell=True, stdout=PIPE,
                                       stderr=STDOUT).communicate()[0]
                        error = False
                    except CalledProcessError as err:
                        output = err.output
                        error = True

                    shell = output.decode('utf_8')

                if shell == "" and not error:
                    return

                shell = sub('/bin/sh: .: ', '', shell)
                if "\n" in shell[:-2]:
                    shell = '\n' + shell

                if self.cos == 'default':
                    cos = uname()[0].lower()
                else:
                    cos = self.cos

                if cos in self.os:
                    path = getcwd()
                    username = getuser()
                    system = uname()[1]
                    user = self.os[cos].format(
                        user=username, system=system, path=path)
                else:
                    path = getcwd()
                    username = getuser()
                    system = uname()[1]
                    user = self.os['linux'].format(user=username, system=system, path=path)

                result = []
                in_text = text = user + shell
                shorten_by = 12
                page_length = 2000
                num_mentions = text.count("@here") + text.count("@everyone")
                shorten_by += num_mentions
                page_length -= shorten_by
                while len(in_text) > page_length:
                    closest_delim = max([in_text.rfind(d, 0, page_length)
                                         for d in ["\n"]])
                    closest_delim = closest_delim if closest_delim != -1 else page_length
                    to_send = in_text[:closest_delim].replace(
                        "@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
                    result.append(to_send)
                    in_text = in_text[closest_delim:]

                result.append(in_text.replace(
                    "@everyone", "@\u200beveryone").replace("@here", "@\u200bhere"))

                #result = list(pagify(user + shell, shorten_by=12))

                for num, output in enumerate(result):
                    if num % 1 == 0 and num != 0:

                        note = await self.bot.send_message(message.channel,
                                                           'There are still {} pages left.\n'
                                                           'Type `more` to continue.'
                                                           ''.format(len(result) - (num+1)))

                        msg = await self.bot.wait_for_message(check=lambda m:
                                                              m.channel == message.channel and
                                                              m.author == message.author and
                                                              m.content == 'more',
                                                              timeout=10)
                        try:
                            await self.bot.delete_message(note)
                        except:
                            pass

                        if msg is None:
                            return
                        else:
                            if output:
                                await self.bot.send_message(message.channel,
                                                            '```Bash\n{}```'.format(output))
                    else:
                        if output:
                            await self.bot.send_message(message.channel,
                                                        '```Bash\n{}```'.format(output))



def check_folder():
    if not exists("data/betterterminal"):
        print("[Terminal]Creating data/betterterminal folder...")
        makedirs("data/betterterminal")

def check_file():
    jdict = {
        "prefix":">",
        "cc":{'test' : {'linux':'printf "Hello.\n'
                                'This is a custom command made using the magic of python."',
                        'windows':'echo Hello. '
                                  'This is a custom command made using the magic of python.'}
             },
        "os":{
            'windows':'{path}>',
            'linux':'{user}@{system}:{path} $ '
            },
        "cos":"default",
        "enabled":True
        }

    if not dataIO.is_valid_json("data/betterterminal/settings.json"):
        print("[BetterTerminal]Creating default settings.json...")
        dataIO.save_json("data/betterterminal/settings.json", jdict)

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(BetterTerminal(bot))
