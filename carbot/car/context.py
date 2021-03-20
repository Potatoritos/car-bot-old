from .command_utils import command_outline
from .parse_args import parse_args
from .utils import embed, zwsp


__all__ = [
    'Context',
    'copy_ctx'
]

class Context(object):
    def __init__(self, *, msg, bot, prefix, content, silent=False):
        self.msg = msg
        self.prefix = prefix
        self.content = content
        self.bot = bot

        self.args, self.kwargs = parse_args(content)

        self.guild = msg.guild
        self.channel = msg.channel
        self.author = msg.author

        self.command = None

        self.silent = silent

    async def send(self, text=None, filter_pings=True, *args, **kwargs):
        if self.silent:
            return
        if filter_pings and text is not None:
            text = zwsp(str(text), '@')

        return await self.channel.send(text, *args, **kwargs)

    async def reply(self, *args, **kwargs):
        await self.send(*args, **kwargs, reference=self.msg.to_reference())

    async def send_error(self, msg, highlight_begin=None,
                            highlight_end=None, footer=None):
        if highlight_begin is None:
            e = embed(description=f":x: {msg}")
            return await self.channel.send(embed=e)
        else:
            outline = command_outline(self.command, self,
                                        highlight_begin, highlight_end)
            e = embed(description=f":x: {outline}\n\n{msg}")

            if footer is not None:
                e.set_footer(text=footer)

            return await self.channel.send(embed=e)

    async def confirm(self, text):
        pass

def copy_ctx(ctx, **kwargs):
    return Context(msg=ctx.msg, bot=ctx.bot, prefix=ctx.prefix,
                   content=ctx.content, **kwargs)
