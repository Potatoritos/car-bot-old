import car
import sys
import os


class Core(car.Cog):
    def __init__(self, bot):
        super().__init__(bot)

    @car.listener
    async def on_message(self, msg):
        # if msg.author.id != 153240776216805376:
            # return
        await self.bot.process_message(msg)

    @car.listener
    async def on_message_edit(self, before, after):
        # if before.author.id != 153240776216805376:
            # return
        await self.bot.process_message(after)

    @car.listener
    async def on_ready(self):
        print("ready!")

