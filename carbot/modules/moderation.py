import discord
import car


class Moderation(car.Cog):
    def __init__(self, bot):
        super().__init__(
            bot=bot,
            global_category="Moderation",
            global_checks=[car.guild_must_be_id(495327409487478785)]
        )

    @car.listener
    async def on_message(self, msg):
        if msg.guild.id != 495327409487478785:
            return

    @car.command()
    @car.requires_permissions(manage_roles=True)
    async def role(
        self, ctx,
        member: car.to_member(),
        role: car.to_role(),
        *,
        a: "When specified, only adds roles" = False,
        r: "When specified, only removes roles" = False
    ):
        """
        Toggles (Adds/removes) a role from a user
        """
        if ctx.author.top_role <= role:
            raise car.CommandError("You aren't allowed to edit this role!")

        if a and r:
            raise car.CommandError("Parameters `-a` and `-r` can't be both both active!")

        try:
            if a or ((not r) and role not in member.roles):
                await member.add_roles(role)
                desc = f"Added {role.mention} to {member.mention}"
            else:
                await member.remove_roles(role)
                desc = f"Removed {role.mention} from {member.mention}"
        except discord.errors.Forbidden:
            raise car.CommandError("I don't have permission to edit this role!")

        await ctx.send(embed=car.embed(description=desc))
