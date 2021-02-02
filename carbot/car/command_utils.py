from .converter import to_member, to_role, to_text_channel
from .utils import embed


_all__ = [
    'command_outline',
    'command_help',
    'bracket_arg'
]

async def command_outline(cmd, ctx, index=-1, index_to=None, use_args=True):
    if index_to is None:
        index_to = index

    if use_args:
        args = ctx.args
    else:
        args = []

    async def format_arg(arg_name, idx):
        if idx != index and idx != index_to:
            if arg_name.startswith('<@!') and arg_name.endswith('>'):
                try:
                    m = await to_member(fuzzy=False).convert(ctx, arg_name)
                    arg_name = f"@{m.nick or m.name}"
                except ArgumentError:
                    pass

            if idx-1 == index_to:
                return " " + arg_name

            return " " + arg_name

        if idx == index:
            arg_name = "``**__``" + arg_name
        if idx == index_to:
            arg_name = arg_name + "``__**``"

        return " " + arg_name

    outline = f"``{ctx.prefix}{cmd.name}"
    for i in range(len(args)):
        if i > len(cmd.args):
            break

        outline += await format_arg(args[i], i)

    for i in range(len(args), len(cmd.args)):
        outline += await format_arg(bracket_arg(cmd.args[i]), i)

    if outline[-1] == '`':
        return outline[0:-2]
    else:
        return outline + "``"

async def command_help(cmd, ctx):
    e = embed(
        title=f"Command ─ {cmd.name}",
        description=cmd.doc
    )

    e.add_field(
        name="Usage",
        value=await command_outline(cmd, ctx, use_args=False) + "\n\n"
            + "\n".join(f"`{bracket_arg(arg)}`: {arg.doc}"
                        for arg in cmd.args),
        inline=False
    )

    if len(cmd.kwargs) > 0:
        s = ""

        for _, kw in cmd.kwargs.items():
            if len(kw.name) > 1:
                prefix = "--"
            else:
                prefix = "-"

            if isinstance(kw.doc, tuple):
                s += f"\n`{prefix}{kw.name} <{kw.doc[0]}>`: {kw.doc[1]}"
            else:
                s += f"\n`{prefix}{kw.name}`: {kw.doc}"

        e.add_field(name="Optional Parameters", value=s, inline=False)

    if len(cmd.aliases) > 0:
        e.add_field(
            name="Aliases",
            value=" ".join(f"`{a}`" for a in cmd.aliases),
            inline=False
        )

    return e

def bracket_arg(arg):
    if arg.optional:
        return f"({arg.name})"
    else:
        return f"[{arg.name}]"
