from .converter import to_member, to_role, to_text_channel
from .utils import embed


_all__ = [
    'command_outline',
    'command_usage',
    'command_help'
]

def command_outline(cmd, ctx=None, highlight_begin=None,
                        highlight_end=None, prefix=None):
    if prefix is None:
        prefix = ctx.prefix

    if ctx is None:
        args = []
        kwargs = {}
    else:
        args = ctx.args
        kwargs = ctx.kwargs

    if highlight_end is None:
        highlight_end = highlight_begin

    def format_arg_value(arg_value):
        if arg_value.startswith('<@!') and arg_value.endswith('>'):
            try:
                m = to_member(fuzzy=False).convert(ctx, arg_name)
                arg_name = f"@{m.nick or m.name}"
            except ArgumentError:
                pass

        return arg_value

    def highlight_arg(arg_value, idx):
        if idx == highlight_begin:
            arg_value = f"``**__``{arg_value}"
        if idx == highlight_end:
            arg_value = f"{arg_value}``__**``"

        return arg_value

    def format_arg(val, idx, bracket=True, kwarg_name=None):
        if isinstance(idx, str):
            val = f"{('--' if len(idx) > 1 else '-')}{idx} {val}"
            arg = cmd.kwargs[idx]
        else:
            arg = cmd.args[idx]

        if bracket:
            val = bracket_arg(arg, val)

        return " " + highlight_arg(format_arg_value(val), idx)

    outline = f"``{prefix}{cmd.name}"
    for i in range(len(args)):
        if i > len(cmd.args):
            break

        outline += format_arg(args[i], i, bracket=False)

    for i in range(len(args), len(cmd.args)):
        outline += format_arg(cmd.args[i].name, i)

    for _, kwarg in cmd.kwargs.items():
        if kwarg.name in kwargs:
            outline += format_arg(kwargs[kwarg.name],
                                    kwarg.name, bracket=False)
        else:
            outline += format_arg(kwarg.doc[0], kwarg.name)

    if outline[-1] == '`':
        return outline[0:-2]
    else:
        return outline + "``"

def command_usage(cmd, ctx):
    s = ""

    for _, kw in cmd.kwargs.items():
        prefix = "--" if len(kw.name) > 1 else "-"

        if isinstance(kw.doc, tuple):
            s += f"\n`({prefix}{kw.name} ({kw.doc[0]}))`: {kw.doc[1]}"
        else:
            s += f"\n`({prefix}{kw.name})`: {kw.doc}"

    return command_outline(cmd, prefix=ctx.prefix) + "\n\n" + (
            "\n".join(f"`{bracket_arg(arg, arg.name)}`: {arg.doc}"
                      for arg in cmd.args)
        ) + "\n" + s

def command_help(cmd, ctx):
    e = embed(
        title=f"Command ─ {cmd.name}",
        description=cmd.doc
    )

    e.add_field(
        name="Usage",
        value=command_usage(cmd, ctx),
        inline=False
    )

    if len(cmd.aliases) > 0:
        e.add_field(
            name="Aliases",
            value=" ".join(f"`{a}`" for a in cmd.aliases),
            inline=False
        )

    return e

def bracket_arg(arg, val):
    brackets = "()" if arg.optional else "[]"
    return f"{brackets[0]}{val}{brackets[1]}"
