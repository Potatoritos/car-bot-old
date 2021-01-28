import inspect
import discord
from .exception import CheckError, ArgumentError, CommandError
from .converter import Converter, to_member #, to_channel
from .command_utils import bracket_arg


__all__ = [
    'Argument',
    'Command',
    'CommandList',
    'command',
]

class Argument(object):
    def __init__(self, name, converter=None, optional=False):
        self.name = name
        self.optional = optional

        if type(converter) in (str, tuple) or converter is None:
            self.converter = None
            self.doc = converter

        else:
            self.converter = converter
            self.doc = converter.doc

class Command(object):
    def __init__(self, func, **kwargs):
        self.func = func
        self.parent = None

        self.name = kwargs.get('name', func.__name__)
        self.aliases = kwargs.get('aliases', [])
        self.category = kwargs.get('category')
        self.checks = kwargs.get('checks', [])
        self.aliases = kwargs.get('aliases', [])

        self.doc = inspect.getdoc(func) or "*(No description provided)*"

        if hasattr(func, '_command_checks'):
            for check in func._command_checks:
                self.checks.append(check)

        conv = Converter(lambda ctx, arg: arg, "test")

        # Account for 'self' argument
        if len(func.__code__.co_varnames) > 1 \
                and func.__code__.co_varnames[1] == 'ctx':
            offset = 2
        else:
            offset = 1

        # Get argument names,
        # their converters (from annotations),
        # and whether they are optional (whether they have a default value)
        self.args = [
            Argument(
                func.__code__.co_varnames[i],
                func.__annotations__.get(func.__code__.co_varnames[i], conv),
                func.__code__.co_argcount - i <= len(func.__defaults__ or ())
            )
            for i in range(offset, func.__code__.co_argcount)
        ]
        self.kwargs = {
            func.__code__.co_varnames[i] : Argument(
                func.__code__.co_varnames[i],
                func.__annotations__.get(func.__code__.co_varnames[i], conv),
                True
            )
            for i in range(func.__code__.co_argcount,
                           func.__code__.co_argcount \
                           + func.__code__.co_kwonlyargcount)
        }

        self.req_args_length = len([a for a in self.args if not a.optional])

    def run_checks(self, ctx):
        # Determine if a context satisfies all command checks
        # If checks fail, CheckError will be raised
        for command_check in self.checks:
            command_check(ctx)

    async def run(self, ctx, run_checks=True):
        try:
            await self._run(ctx, run_checks)

        except ArgumentError as e:
            await ctx.send_error(e.error_msg, e.index)

        except CommandError as e:
            await ctx.send_error(e.error_msg)

    async def _run(self, ctx, run_checks=True):
        ctx.command = self

        if run_checks:
            try:
                self.run_checks(ctx)
            except CheckError as e:
                await ctx.send_error(e.error_msg)
                return

        # Connect the context args that go past the amount of command args
        args = ctx.args[:max(0, len(self.args)-1)]

        if len(ctx.args) >= len(self.args) and len(ctx.args) > 0:
            args.append(' '.join(ctx.args[len(self.args)-1:]))

        ctx.args = args

        # Send error message if there are missing arguments
        if len(ctx.args) < self.req_args_length:
            missing = "I am missing the highlighted arguments!\n\n" \
                + "\n".join([
                    f"`{bracket_arg(self.args[i])}`: {self.args[i].doc}"
                    for i in range(len(ctx.args), len(self.args))
                ])

            optional = "\n\nOptional parameters"

            await ctx.send_error(missing, len(ctx.args), self.req_args_length-1)
            return

        # Convert all arguments with their respective converters
        conv_args = []
        conv_kwargs = {}

        for i in range(len(ctx.args)):
            try:
                if self.args[i].converter is None:
                    conv_args.append(args[i])
                else:
                    c = await self.args[i].converter.convert(ctx, args[i])
                    conv_args.append(c)

            except ArgumentError as e:
                raise ArgumentError(e.error_msg, i)

        for _, kwarg in self.kwargs.items():
            if kwarg.name not in ctx.kwargs:
                continue

            try:
                if kwarg.converter is None:
                    conv_kwargs[kwarg.name] = ctx.kwargs[kwarg.name]
                else:
                    c = await kwarg.converter.convert(ctx, ctx.kwargs[kwarg.name])
                    conv_kwargs[kwarg.name] = c

            except ArgumentError as e:
                raise ArgumentError(e.error_msg, kwarg.name)

        await self.exec(ctx, conv_args, conv_kwargs)

    async def exec(self, ctx, args, kwargs):
        # Execute the command func with converted args
        if self.parent is not None:
            await self.func(self.parent, ctx, *args, **kwargs)
        else:
            await self.func(ctx, *args, **kwargs)

class CommandList(object):
    def __init__(self):
        self._commands = {}
        self._aliases = {}

        self._iter_list = []
        self._iter_idx = 0
        self._edited = False

    def __len__(self):
        return len(self._commands)

    def __contains__(self, key):
        return (key in self._commands) or (key in self._aliases)

    def __getitem__(self, key):
        if key in self._commands:
            return self._commands[key]

        return self._commands[self._aliases[key]]

    def __iter__(self):
        self._iter_idx = -1

        if self._edited:
            self._iter_list = list(self._commands.values())
            self._iter_list.sort(key=lambda x: x.name)
            self._edited = False

        return self

    def __next__(self):
        self._iter_idx += 1

        if self._iter_idx >= len(self._iter_list):
            raise StopIteration

        return self._iter_list[self._iter_idx]

    def add(self, command):
        self._commands[command.name] = command

        for alias in command.aliases:
            self.set_alias(alias, command.name)

        self._edited = True

    def remove(self, command):
        for alias in command.aliases:
            del self._aliases[alias]

        del self._commands[command.name]

        self._edited = True

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def set_alias(self, alias, command_name):
        self._aliases[alias] = command_name

def command(**kwargs):
    def decorator(func):
        return Command(func, **kwargs)
    return decorator

