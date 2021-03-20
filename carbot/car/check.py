import types
import config
from .exception import CheckError


__all__ = [
    'check',
    'requires_permissions',
    'public_channels_only',
    'bot_owner_only',
    'guild_must_be_id',
    'trusted_only'
]

def check(condition):
    def decorator(func):
        if isinstance(func, types.FunctionType):
            if not hasattr(func, '_command_checks'):
                func._command_checks = []

            func._command_checks.append(condition)

        else:
            func.checks.append(condition)
        return func
    return decorator

def requires_permissions(**permissions):
    def condition(ctx):
        perms = ctx.channel.permissions_for(ctx.author)
        missing = [
            p for p, v in permissions.items() if getattr(perms, p) != v
        ]
        if missing:
            raise CheckError("You aren't allowed to use this command!")

    return check(condition)

def public_channels_only():
    def condition(ctx):
        if ctx.msg.guild is None:
            raise CheckError("This command can only be used in servers!")
    return check(condition)

def bot_owner_only():
    def condition(ctx):
        if ctx.msg.author.id != config.OWNER_ID:
            raise CheckError("You aren't allowed to use this command!")
    return check(condition)

def guild_must_be_id(*ids):
    def condition(ctx):
        if ctx.guild is None:
            raise CheckError()

        if len(ids) == 1 and isinstance(ids[0], set):
            if ctx.guild.id not in ids[0]:
                raise CheckError()

        elif ctx.guild.id not in ids:
            raise CheckError()

    return check(condition)

def trusted_only():
    def condition(ctx):
        if ctx.msg.author.id not in ctx.bot.cogs['BotAdmin'].trusted \
                and ctx.msg.author.id != config.OWNER_ID:
            raise CheckError("You aren't allowed to use this command!")
    return check(condition)

