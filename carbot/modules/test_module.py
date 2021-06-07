import discord
import car
import random

class TestModule(car.Cog):
    def __init__(self, bot):
        super().__init__(bot, global_category="Hidden")
        self.last_msg = {}
        self.responses = []

    def markov_text(text):
        resp = {}
        spl = text.split(' ')
        for i in range(len(spl)-1):
            if spl[i] not in resp:
                resp[spl[i]] = []
            resp[spl[i]].append(spl[i+1])
        return resp

    def gen(resp, min_length):
        length = 0
        words = []
        while length < min_length:
            return 

    @car.listener
    async def on_message(self, msg):
        if msg.guild.id != 495327409487478785 or msg.author.bot:
            return
        if msg.channel.id not in (
                495327409487478787,
                629034237022044170,
                57579341361879449
            ):
            return

        if msg.channel.id in self.last_msg:
            self.responses.append(
                (self.last_msg[msg.channel.id].content, msg.content)
            )

        self.last_msg[msg.channel.id] = msg


