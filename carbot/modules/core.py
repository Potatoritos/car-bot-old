import car
import sys
import os
import discord
from collections import deque


class Core(car.Cog):
    def __init__(self, bot):
        super().__init__(bot)

    @car.listener
    async def on_message(self, msg):
        await self.bot.process_message(msg)

    @car.listener
    async def on_message_edit(self, before, after):
        await self.bot.process_message(after)

    @car.listener
    async def on_ready(self):
        print("ready!")
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name="car"))

