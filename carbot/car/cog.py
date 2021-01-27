import inspect
from .command import Command
from .listener import Listener

__all__ = [
    'Cog'
]

class Cog(object):
    def __init__(self, bot, global_checks=[], global_category=None):
        self.bot = bot
        self.global_checks = global_checks
        self.global_category = global_category
        self.commands = []
        self.listeners = []

        for _, obj in inspect.getmembers(self):
            if isinstance(obj, Command):
                if obj.category is None:
                    obj.category = self.global_category

                for command_check in self.global_checks:
                    command_check(obj)

                obj.category = obj.category or self.global_category

                obj.parent = self

                self.commands.append(obj)

            elif isinstance(obj, Listener):
                obj.parent = self

                self.listeners.append(obj)

