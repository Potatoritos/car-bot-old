from .command_utils import command_outline
from .parse_args import parse_args
from .utils import embed


__all__ = [
    'Context'
]

class Context(object):
    def __init__(self, msg, prefix, content, bot):
        self.msg = msg
        self.prefix = prefix
        self.content = content
        self.bot = bot

        self.args, self.kwargs = parse_args(content)

        self.guild = msg.guild
        self.channel = msg.channel
        self.author = msg.author

        self.command = None

    async def send(self, text=None, filter_pings=True, *args, **kwargs):
        if filter_pings and text is not None:
            text = str(text).replace('@', '@​')

        return await self.channel.send(text, *args, **kwargs)

    async def send_error(self, msg, index=None, index_to=None, footer=None):
        if index is None:
            e = embed(description=f":x: {msg}")

            return await self.channel.send(embed=e)

        else:
            outline = command_outline(self.command, self, index, index_to)
            e = embed(description=f":x: {outline}\n\n{msg}")

            if footer is not None:
                e.set_footer(text=footer)

            return await self.channel.send(embed=e)

    async def confirm(self, text):
        pass

