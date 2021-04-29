import discord
from .exception import ArgumentError
from .utils import fuzzy_match


__all__ = [
    'Converter',
    'to_int',
    'to_float',
    'to_member',
    'to_text_channel',
    'to_role',
    'to_message',
    'to_command',
    'to_emoji'
]

class Converter(object):
    def __init__(self, func, doc=None):
        self.convert = func
        self.doc = doc

    def __floordiv__(self, doc):
        self.doc = doc
        return self

def check_is_between(obj, lower, upper):
    if lower is not None and upper is not None:
        if not lower <= obj <= upper:
            raise ArgumentError(f"This must be between {lower} and {upper}!")

    elif lower is None and upper is not None and obj > upper:
        raise ArgumentError(f"This must be at most {upper}!")

    elif lower is not None and upper is None and obj < lower:
        raise ArgumentError(f"This must be at least {upper}!")

def to_int(lower=None, upper=None):
    def converter(ctx, obj):
        try:
            obj = int(obj)
        except ValueError:
            raise ArgumentError("This parameter must be an integer!")

        check_is_between(obj, lower, upper)

        return obj

    return Converter(converter, "an integer")

def to_float(*, lower=None, upper=None):
    def converter(ctx, obj):
        spl = obj.split('/')

        if len(spl) == 2:
            try:
                obj = float(spl[0]) / float(spl[1])
            except (ValueError, ZeroDivisionError):
                raise ArgumentError("{{arg}} is not a valid fraction!")

        try:
            obj = float(obj)
        except ValueError:
            raise ArgumentError("This parameter must be a number!")

        check_is_between(obj, lower, upper)

        return obj

    return Converter(converter, "a number")

def match_by_args(to_match, against, *, amount, prompt, key):
    if isinstance(amount, int):
        return fuzzy_match(to_match, against, amount, key)
    if prompt:
        return fuzzy_match(to_match, against, 5, key)[0][0]
        # TODO: implement name disambiguation
    else:
        return fuzzy_match(to_match, against, 5, key)[0][0]

def to_member(*, fuzzy=True, prompt=True, amount=None):
    def converter(ctx, obj):
        # Get ID from obj if obj is a mention
        if obj[-1] == '>':
            if obj.startswith('<@!'):
                obj = obj[3:-1]
            elif obj.startswith('<@'):
                obj = obj[2:-1]

        try:
            # Get member if obj is an ID
            m = discord.utils.get(ctx.guild.members, id=int(obj))
            if m is not None:
                return m

        except ValueError:
            pass

        discrim = None

        # Check if obj specifies a discriminator
        if len(obj) > 5 and obj[-5] == '#':
            try:
                int(obj[-4:])
                discrim = obj[-4:]
            except ValueError:
                pass

        if fuzzy:
            if discrim is None:
                members = ctx.guild.members
            else:
                members = [
                    m for m in ctx.guild.members if m.discriminator == discrim
                ]

            return match_by_args(obj, members, amount=amount,
                                 prompt=prompt, key=lambda m: m.name.lower())

        kwargs = {'name':obj}
        if discrim is not None:
            kwargs['discriminator'] = discrim

        m = discord.utils.get(ctx.guild.members, **kwargs)

        if m is not None:
            return m

        raise ArgumentError("I can't find this member!")

    return Converter(converter, "a member")

def to_text_channel(*, fuzzy=True, prompt=True, amount=None):
    def converter(ctx, obj):
        if obj.startswith('<#') and obj[-1] == '>':
            obj = obj[2:-1]

        try:
            c = discord.utils.get(ctx.guild.text_channels, id=int(obj))
            if c is not None:
                return c
        except ValueError:
            pass

        if fuzzy:
            return match_by_args(obj, ctx.guild.text_channels, amount=amount,
                                 prompt=prompt, key=lambda x: x.name.lower())

        raise ArgumentError("I can't find this text channel!")

    return Converter(converter, "a text channel")

def to_role(*, fuzzy=True, prompt=True, amount=None):
    def converter(ctx, obj):
        if obj.startswith('<@&') and obj[-1] == '>':
            obj = obj[3:-1]

        try:
            r = discord.utils.get(ctx.guild.roles, id=int(obj))
            if c is not None:
                return c
        except ValueError:
            pass

        if fuzzy:
            return match_by_args(obj, ctx.guild.roles, amount=amount,
                                 prompt=prompt, key=lambda m: m.name.lower())

        raise ArgumentError("I can't find this role!")

    return Converter(converter, "a role")

def to_message():
    async def converter(ctx, obj):
        obj = obj.split('/')[-1]
        try:
            msg = await ctx.channel.fetch_message(int(obj))
        except (ValueError, discord.NotFound):
            raise ArgumentError("I can't find this message!")
        except discord.Forbidden:
            raise ArgumentError("I don't have the permissions required to"
                                "fetch this message!")
        except discord.HTTPException:
            raise ArgumentError("Message fetching failed!")

        return msg

    return Converter(converter, "a message")

def to_command():
    def converter(ctx, obj):
        command = ctx.bot.commands.get(obj)

        if command is None:
            raise ArgumentError("I can't find this command!")

        return command

    return Converter(converter, "a command")

def to_emoji(*, allow_unicode_emojis=False, to_id=False):
    def converter(ctx, obj):
        # doesn't actually check if obj is an emoji (obj can be any character)
        if len(obj) == 1 and allow_unicode_emojis:
            return obj

        if obj.startswith('<:') and obj.endswith('>'):
            try:
                obj = int(obj.split(':')[-1][:-1])
            except ValueError:
                pass

        try:
            e = discord.utils.get(ctx.guild.emojis, id=int(obj))
            if e is not None:
                return e
        except ValueError:
            pass

        e = discord.utils.get(ctx.guild.emojis, name=obj)
        if e is not None:
            return e

        f = fuzzy_match(
            obj, ctx.guild.emojis, 1, lambda x: x.name.lower()
        )[0][0]

        if to_id:
            return f.id
        else:
            return f

    return Converter(converter, "an emoji")

