import car


class Utility(car.Cog):
    def __init__(self, bot):
        super().__init__(bot, global_category="Utility")

    @car.command(aliases=["avatar"])
    async def pfp(self, ctx, member: car.to_member()):
        """
        Displays someone's profile picture
        """
        link = ""
        if member.is_avatar_animated():
            link += f"[[.gif]]({member.avatar_url} \"Link to .gif\") "

        as_webp = member.avatar_url_as(format='webp')
        as_png = member.avatar_url_as(format='png')

        link += f"[[.webp]]({as_webp} \"Link to .webp\") "
        link += f"[[.png]]({as_png} \"Link to .png\") "

        e = car.embed(description=f"{member.mention}'s avatar\n{link}")
        e.set_image(url=member.avatar_url)

        await ctx.send(embed=e)

    @car.command()
    async def cat(
        self, ctx,
        message: car.to_message() // (
            "The message. If left blank, the most recent message with a "
            "text file attachment will be selected."
        ) = None
    ):
        """
        Displays the contents of a text file.
        The contents will be formatted in a code block if the name of the file is not message.txt.
        """
        pass

