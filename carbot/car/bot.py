import discord
import inspect
import asyncio
import importlib
import sqlite3
from .cog import Cog
from .command import Command, CommandList
from .listener import Listener, ListenerList
from .guild_settings import GuildSettingsList
from .exception import ArgumentError
from .context import Context


__all__ = [
    'Bot'
]

class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents().default()
        intents.members = True
        super().__init__(intents=intents)

        self.conn = sqlite3.connect('car.db')

        self.commands = CommandList()
        self.listeners = ListenerList()
        self.guild_settings = GuildSettingsList(self.conn)

        self.cogs = {}
        self.module_cogs = {}
        self.modules = {}

    def add_cog(self, cog):
        for command in cog.commands:
            self.commands.add(command)

        for listener in cog.listeners:
            self.listeners.add(listener)

    def remove_cog(self, cog):
        for command in cog.commands:
            self.commands.remove(command)

        for listener in cog.listeners:
            self.listeners.remove(listener)

    def load_module(self, name):
        module = importlib.import_module(name)
        self.modules[name] = module

        for _, obj in inspect.getmembers(module):
            if not hasattr(obj, 'mro') or not obj.mro()[1] is Cog:
                continue

            if name not in self.module_cogs:
                self.module_cogs[name] = []

            cog = obj(self)
            self.module_cogs[name].append(cog);
            self.cogs[type(cog).__name__] = cog
            self.add_cog(cog)

    def unload_module(self, name):
        for cog in self.module_cogs[name]:
            self.remove_cog(cog)

        del self.module_cogs[name]
        del self.modules[name]

    def reload_module(self, name):
        module = self.modules[name]
        importlib.reload(module)

        self.unload_module(name)
        self.load_module(name)

    async def process_message(self, msg):
        if msg.author.bot:
            return

        prefix = self.guild_settings[msg.guild.id].prefix
        if not msg.content.startswith(prefix):
            return

        command_name = msg.content[len(prefix):].split(' ')[0]
        try:
            command = self.commands[command_name]
        except KeyError:
            return

        content = msg.content[len(prefix)+len(command_name)+1:]
        ctx = Context(msg=msg, bot=self, prefix=prefix, content=content)
        await command.run(ctx)

    def command(self, **kwargs):
        def decorator(func):
            self.commands.add(Command(func, **kwargs))
        return decorator

    def listener(self, func):
        self.listeners.add(Listener(func))

    def dispatch(self, event, *args, **kwargs):
        # This function is called by discord.Client whenever an event occurs
        self.listeners.run('on_' + event, *args, **kwargs)
        super().dispatch(event, *args, **kwargs)

