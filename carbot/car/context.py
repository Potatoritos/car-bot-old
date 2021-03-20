from .command_utils import command_outline
from .utils import embed, zwsp
import discord


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

        # these variables are defined in Command._run()
        self.args = None
        self.kwargs = None
        self.command = None

        self.guild = msg.guild
        self.channel = msg.channel
        self.author = msg.author

        self.silent = silent

    async def send(self, text=None, filter_pings=True, *args, **kwargs):
        if self.silent:
            return
        if filter_pings and text is not None:
            text = zwsp(str(text), '@')

        return await self.channel.send(text, *args, **kwargs)

    async def reply(self, *args, ping=False, **kwargs):
        allowed_mentions = None
        if not ping:
            allowed_mentions = discord.AllowedMentions(replied_user=False)
        return await self.send(
            *args, **kwargs,
            allowed_mentions=allowed_mentions,
            reference=self.msg.to_reference()
        )

    async def send_error(self, msg, highlight_begin=None,
                            highlight_end=None, footer=None):
        if highlight_begin is None:
            e = embed(description=f":x: {msg}")
            return await self.reply(embed=e)
        else:
            outline = command_outline(self.command, self,
                                        highlight_begin, highlight_end)
            e = embed(description=f":x: {outline}\n\n{msg}")

            if footer is not None:
                e.set_footer(text=footer)

            return await self.reply(embed=e)

    async def confirm(self, text):
        pass

def copy_ctx(ctx, **kwargs):
    return Context(msg=ctx.msg, bot=ctx.bot, prefix=ctx.prefix,
                   content=ctx.content, **kwargs)
