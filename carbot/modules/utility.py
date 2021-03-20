import car
import random
from googletrans import Translator


class Utility(car.Cog):
    def __init__(self, bot):
        super().__init__(bot, global_category="Utility")

    @car.command(aliases=["avatar"])
    async def pfp(self, ctx, member: car.to_member()):
        """
        Displays someone's profile picture (and provides download links)
        """
        links = [
            (f"[[.{form}]]({member.avatar_url_as(format=form)} "
             f"\"Link to .{form}\")")
            for form in ('webp', 'png', 'jpg')
        ]

        if member.is_avatar_animated():
            links.append(f"[[.gif]]({member.avatar_url} \"Link to .gif\") ")

        link = ' '.join(links)
        e = car.embed(description=f"{member.mention}'s avatar\n{link}")
        e.set_image(url=member.avatar_url)

        await ctx.send(embed=e)

    @car.command(aliases=["emote"])
    async def emoji(self, ctx, emoji: car.to_emoji()):
        """
        Displays a server emoji (and provides download links)
        """
        links = [
            f"[[.{form}]]({emoji.url_as(format=form)} \"Link to .{form}\")"
            for form in ('webp', 'png', 'jpg')
        ]
        if emoji.animated:
            links.append(f"[[.gif]]({emoji.url} \"Link to .gif\") ")

        embed = car.embed(description=f":{emoji.name}:\n{' '.join(links)}")
        embed.set_image(url=emoji.url)

        await ctx.send(embed=embed)

    @car.command()
    async def rand(
        self, ctx,
        a: car.to_float() // (
            "Selects a random number between 1 and a inclusive (if `b` is "
            "not specified). Default: 100"
        ) = 100,
        b: car.to_float() // (
            "If specified, selects a random number between a and b inclusive"
        ) = None,
        *,
        u: ("Selects a floating point number instead of an integer") = False,
        r: car.to_int() // (
            "amount", "... rounded to `(amount)` decimal places"
        ) = False
    ):
        """
        Selects a random number between a range
        """

        if b is None:
            range_ = (1, a)
        else:
            range_ = (min(a, b), max(a, b))

        if u:
            n = random.uniform(*range_)
            if r:
                n = round(n,r)
        else:
            n = random.randint(*range_)

        await ctx.send(embed=car.embed(description=f":game_die: `{n}`"))

    @car.command()
    async def choose(
        self, ctx,
        choices: "Space seperated choices",
        *,
        k: car.to_int(lower=1, upper=100) // (
            "The amount of choices to select (with replacement). Default: 1"
        ) = 1,
        w: (
            "Comma seperated integers; the weights of the respective choices"
        ) = None
    ):
        """
        Selects random choices from a list of choices
        """
        choices = choices.split(' ')

        if w is not None:
            weights = []
            w = w.split(',')

            if len(w) != len(choices):
                raise car.CommandError(
                    "The number of weights must match the number of choices!"
                )

            for weight in w:
                try:
                    weights.append(car.to_int().convert(ctx, weight))
                except car.ArgumentError as e:
                    raise car.CommandError(
                        "The weights must be comma seperated integers!"
                    )

        else:
            weights = None

        selected = ' '.join(
            f"``{car.zwsp(c,'`')}``"
            for c in random.choices(choices, weights, k=k)
        )

        if len(selected) > 1950:
            raise car.CommandError("I can't fit this in a single message!")

        await ctx.send(embed=car.embed(description=f":game_die: {selected}"))

    @car.command()
    async def cat(
        self, ctx,
        message: car.to_message() // (
            "The message. If left blank, the most recent message with a "
            "text file attachment will be selected."
        ) = None,
        *,
        a: car.to_int() // (
            "n", "selects the `(n)`th attachment in `(message)`"
        ) = 1,
        m: car.to_int() // (
            "n", "specifies to select the `(n)`th last message with an "
            "attachment, if `(message)` is not specified"
        ) = 1,
    ):
        """
        **WIP-not working yet!**
        Displays the contents of a text file.
        """
        await ctx.send("wip")
