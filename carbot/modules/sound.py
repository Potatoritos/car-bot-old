import car
import discord
from aiogtts import aiogTTS
import os
import sqlite3


class Sound(car.Cog):
    def __init__(self, bot):
        super().__init__(
            bot=bot,
            global_category="Sound"
        )
        self.volume = {}

        cur = self.bot.conn.cursor()
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS sfxlist (
                        name TEXT PRIMARY KEY,
                        path TEXT,
                        category TEXT
                    )
                    ''')

    def get_sound(self, name):
        cur = self.bot.conn.cursor()
        cur.execute('SELECT * FROM sfxlist WHERE name = ?', (name,))
        fetch = cur.fetchone()
        if fetch is None:
            raise car.CommandError("This sound doesn't exist!")
        return fetch

    def get_vc(self, ctx):
        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if vc is None or not vc.is_connected():
            raise car.CommandError("I'm not in a voice channel!")
        if vc.channel != ctx.author.voice.channel:
            raise car.CommandError("You must be in my voice channel!")
        return vc

    @car.command()
    async def sfxstop(self, ctx):
        """
        Stops the currently playing sound
        """
        self.get_vc(ctx).stop()

    @car.command()
    async def sfxpause(self, ctx):
        """
        Pauses the currently playing sound
        """
        self.get_vc(ctx).pause()

    @car.command()
    async def sfxresume(self, ctx):
        """
        Resumes the currently playing sound
        """
        self.get_vc(ctx).resume()

    @car.command(aliases=["vcjoin"])
    async def sfxjoin(self, ctx):
        """
        Joins your voice channel
        """
        vc = ctx.author.voice
        if vc is None:
            raise car.CommandError("You must be in a voice channel!")
        await vc.channel.connect()
        await ctx.reply("Joined the voice channel")

    @car.command(aliases=["vcleave"])
    async def sfxleave(self, ctx):
        """
        Leaves the voice channel
        """
        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        print(vc)
        if vc is None:
            raise car.CommandError("I'm not in a voice channel!")
        await vc.disconnect()
        await ctx.reply("Left the voice channel")

    @car.command()
    async def sfx(
        self, ctx,
        sound: "The sound effect to play",
        *,
        v: car.to_int(lower=0, upper=200) // (
            "volume",
            "Plays the sound effect at volume (number between 1 and 200)%"
        ) = 100
    ):
        """
        Plays a sound effect in a voice channel
        """
        if ctx.author.voice is None:
            raise car.CommandError("You must be in a voice channel!")

        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if vc is None or not vc.is_connected():
            vc = await ctx.author.voice.channel.connect()
        if vc.channel != ctx.author.voice.channel:
            raise car.CommandError("You must be in my voice channel!")

        if vc.is_playing():
            vc.stop()

        sound = self.get_sound(sound)
        try:
            vc.play(discord.FFmpegPCMAudio(sound[1]))
            vc.source = discord.PCMVolumeTransformer(vc.source, volume=v*0.01)
        except IOError:
            raise car.CommandError("This sound effect is broken!")

    @car.command()
    async def sfxlist(self, ctx):
        """
        Displays a list of all sound effects
        """
        cur = self.bot.conn.cursor()
        cur.execute('SELECT * FROM sfxlist')
        fetch = cur.fetchall()
        categories = {}
        for sound in fetch:
            if sound[2] not in categories:
                categories[sound[2]] = []
            categories[sound[2]].append(sound[0])

        e = car.embed(title="Sound Effect List")

        for k, v in categories.items():
            e.add_field(name=k, value=' '.join(f"`{n}`" for n in v),
                        inline=False)

        if len(categories) == 0:
            e.description = "*No sound effects found*"

        await ctx.send(embed=e)

    @car.command()
    @car.trusted_only()
    async def sfxadd(
        self, ctx,
        name: "the sound effect's name",
        category: "the sound effect's category" = "Uncategorized"
    ):
        """
        Adds a sound effect
        """
        if len(ctx.msg.attachments) == 0:
            raise car.CommandError("You must attach a sound file!")

        attach = ctx.msg.attachments[0]
        filetype = attach.filename.split('.')[-1]
        path = f'./sfx/{name}.{filetype}'
        if os.path.exists(path):
            raise car.CommandError(f"`{path}` already exists!")

        cur = self.bot.conn.cursor()
        try:
            cur.execute('INSERT INTO sfxlist VALUES (?, ?, ?)',
                        (name, path, category))
        except sqlite3.IntegrityError:
            raise car.Commanderror(f"An sfx with this name already exists!")

        await attach.save(path)
        self.bot.conn.commit()

        await ctx.reply(
            f"sfx added: name `{name}`, path `{path}`, "
            f"category `{category}`"
        )

    @car.command(aliases=["sfxdel", "sfxdelete"])
    @car.trusted_only()
    async def sfxremove(
        self, ctx,
        name: "the sound effect to delete",
        *,
        k: "If specified, does not delete any files"
    ):
        """
        Removes a sound effect
        """
        sound = self.get_sound(name)
        cur = self.bot.conn.cursor()
        cur.execute("DELETE FROM sfxlist WHERE name = ?", (name,))
        self.bot.conn.commit()

        if not k:
            try:
                os.remove(sound[1])
            except FileNotFoundError:
                pass

        await ctx.reply(f"removed `{sound}`")

    @car.command()
    @car.trusted_only()
    async def sfxmanuadd(
        self, ctx,
        name: "the sound effect's name",
        path: "the sound effect's path",
        category: "the sound effect's category"
    ):
        """
        Manually add a sound effect
        """
        cur = self.bot.conn.cursor()
        cur.execute('INSERT INTO sfxlist VALUES (?, ?, ?)',
                    (name, path, category))
        self.bot.conn.commit()
        await ctx.reply(
            f"sfx added: name `{name}`, path `{path}`, category `{category}`"
        )

    @car.command()
    async def tts(
        self, ctx,
        text: "the text to convert to speech",
        *,
        # d: (
            # "Returns the audio file and doesn't play it in a voice channel"
        # ) = False,
        l: (
            "language_code", "Changes the language of the TTS voice"
        ) = 'en-ca',
        s: "Slows down the speech playback rate" = False,
    ):
        """
        Converts text to speech, then plays it in a voice channel
        """
        if l not in LANGUAGES:
            raise car.CommandError((
                "Invalid language! use `ttslanguages` to view all languages"
            ))

        if ctx.author.voice is None:
            raise car.CommandError("You must be in a voice channel!")

        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if vc is None or not vc.is_connected():
            vc = await ctx.author.voice.channel.connect()

        generating = await ctx.reply("Generating TTS...")
        aiogtts = aiogTTS()
        await aiogtts.save(text, f"tts_{ctx.guild.id}.mp3", lang=l, slow=s)

        if vc.is_playing():
            vc.stop()

        vc.play(discord.FFmpegPCMAudio(f"tts_{ctx.guild.id}.mp3"))
        await generating.delete()

    @car.command(aliases=["ttslang", "ttslangs"])
    async def ttslanguages(self, ctx):
        """
        Displays all languages available for `tts`
        """
        await ctx.author.send(LANGUAGES_LIST)

LANGUAGES = {
    'af', 'ar', 'bn', 'bs', 'ca', 'cs', 'en-au', 'en-ca', 'en-gb', 'en-ie',
    'en-in', 'en-ng', 'en-nz', 'en-ph', 'en-tz', 'en-uk', 'en-us', 'en-za',
    'en', 'eo', 'es-es', 'es-us', 'es', 'et', 'fi', 'fr-ca', 'fr-fr', 'fr',
    'gu', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'jw', 'km', 'kn',
    'ko', 'la', 'lv', 'mk', 'ml', 'mr', 'my', 'ne', 'nl', 'no', 'pl', 'pt-br',
    'pt-pt', 'pt', 'ro', 'ru', 'si', 'sk', 'sq', 'sr', 'su', 'sv', 'sw', 'ta',
    'te', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh-cn', 'zh-tw'
}

LANGUAGES_LIST = """```
af:    Afrikaans
ar:    Arabic
bn:    Bengali
bs:    Bosnian
ca:    Catalan
cs:    Czech
en-au: English (Australia)
en-ca: English (Canada)
en-gb: English (UK)
en-gh: English (Ghana)
en-ie: English (Ireland)
en-in: English (India)
en-ng: English (Nigeria)
en-nz: English (New Zealand)
en-ph: English (Philippines)
en-tz: English (Tanzania)
en-uk: English (UK)
en-us: English (US)
en-za: English (South Africa)
en:    English
eo:    Esperanto
es-es: Spanish (Spain)
es-us: Spanish (United States)
es:    Spanish
et:    Estonian
fi:    Finnish
fr-ca: French (Canada)
fr-fr: French (France)
fr:    French
gu:    Gujarati
hi:    Hindi
hr:    Croatian
hu:    Hungarian
hy:    Armenian
id:    Indonesian
is:    Icelandic
it:    Italian
ja:    Japanese
jw:    Javanese
km:    Khmer
kn:    Kannada
ko:    Korean
la:    Latin
lv:    Latvian
mk:    Macedonian
ml:    Malayalam
mr:    Marathi
my:    Myanmar (Burmese)
ne:    Nepali
nl:    Dutch
no:    Norwegian
pl:    Polish
pt-br: Portuguese (Brazil)
pt-pt: Portuguese (Portugal)
pt:    Portuguese
ro:    Romanian
ru:    Russian
si:    Sinhala
sk:    Slovak
sq:    Albanian
sr:    Serbian
su:    Sundanese
sv:    Swedish
sw:    Swahili
ta:    Tamil
te:    Telugu
th:    Thai
tl:    Filipino
tr:    Turkish
uk:    Ukrainian
ur:    Urdu
vi:    Vietnamese
zh-cn: Chinese (Mandarin/China)
zh-tw: Chinese (Mandarin/Taiwan)```
"""

