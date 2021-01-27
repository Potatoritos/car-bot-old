import discord
import inspect
import asyncio
import importlib
from .cog import Cog
from .command import Command, CommandList
from .listener import Listener, ListenerList
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

        self.commands = CommandList()
        self.listeners = ListenerList()
        self.cogs = {}

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

            if name not in self.cogs:
                self.cogs[name] = []

            cog = obj(self)
            self.cogs[name].append(cog)
            self.add_cog(cog)

    def unload_module(self, name):
        for cog in self.cogs[name]:
            self.remove_cog(cog)

        del self.cogs[name]
        del self.modules[name]

    def reload_module(self, name):
        module = self.modules[name]
        importlib.reload(module)

        self.unload_module(name)
        self.load_module(name)

    async def process_message(self, msg):
        if msg.author.bot:
            return

        prefix = 'c.' # TODO: retrieve prefix from guild settings
        if not msg.content.startswith(prefix):
            return

        command_name = msg.content[len(prefix):].split(' ')[0]

        try:
            command = self.commands[command_name]
        except ValueError:
            return

        content = msg.content[len(prefix) + len(command_name) + 1:]

        ctx = Context(msg, prefix, content, self)

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

