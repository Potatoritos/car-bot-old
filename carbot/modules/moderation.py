import discord
import car
import random
import asyncio


class Moderation(car.Cog):
    def __init__(self, bot):
        super().__init__(
            bot=bot,
            global_category="Moderation",
            global_checks=[car.guild_must_be_id(495327409487478785)]
        )

    @car.listener
    async def on_message_edit(self, bef, aft):
        if bef.guild.id != 495327409487478785:
            return
        if bef.author.bot:
            return
        # TODO: handle len(bef) + len(aft) > 2000
        c = discord.utils.get(bef.guild.text_channels, id=631182593718484992)
        e = car.embed(description=(
            f"[[Jump]]({bef.jump_url}) {bef.author.mention} in"
            f"{bef.channel.mention}"
        ))
        e.set_author(name="Message Delete",
                     icon_url=bef.author.avatar_url)
        if len(bef.content) > 0:
            e.add_field(name="Before", value=bef.content)
        if len(aft.content) > 0:
            e.add_field(name="After", value=aft.content)
        await c.send(embed=e)

    @car.listener
    async def on_message_delete(self, msg):
        if msg.guild.id != 495327409487478785:
            return
        if msg.author.bot:
            return
        #TODO: handle len(msg) + len(embed and stuff) > 2000
        c = discord.utils.get(msg.guild.text_channels, id=631182593718484992)
        e = car.embed(description=(
            f"{msg.author.mention} in {msg.channel.mention}"
        ))
        e.set_author(name="Message Delete",
                     icon_url=msg.author.avatar_url)
        if len(msg.content) > 0:
            e.add_field(name="Content", value=msg.content)
        await c.send(embed=e)

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
            raise car.CommandError(f"You aren't allowed to edit this role!")

        if a and r:
            raise car.CommandError(
                "Parameters `-a` and `-r` can't be both both active!"
            )

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

    @car.command()
    @car.requires_permissions(manage_roles=True)
    async def ban(self, ctx, member: car.to_member()):
        """
        Adds the banned role to someone
        """
        cmd = self.bot.commands['role']
        role = discord.utils.get(ctx.guild.roles, id=525044579800711170)
        ctx2 = car.copy_ctx(ctx, silent=True)
        await cmd.exec(ctx2, [member, role], {'a': True})

        emoji = random.choice([':flushed:'*3, ':moyai:'*2, ':monkey:',
                               ':gorilla:', ':orangutan:',
                               '<:blobangery:808087859965853726>',
                               '<:grimace:716692825777111100>'])
        e = car.embed(
            description=(
                f":rotating_light: {member.mention} has been BANNED "
                f"from the Wab Server!!!! {emoji}"
            )
        )
        await ctx.send(embed=e)

    @car.command()
    @car.requires_permissions(manage_roles=True)
    async def unban(self, ctx, member: car.to_member()):
        """
        Removes the banned role to someone
        """
        cmd = self.bot.commands['role']
        role = discord.utils.get(ctx.guild.roles, id=525044579800711170)
        ctx2 = car.copy_ctx(ctx, silent=True)
        await cmd.exec(ctx2, [member, role], {'r': True})

        emoji = random.choice(['<:troled:787494917320474624>',
                               '<:grimace:716692825777111100>',
                               '<:individual:811309916429353010>',
                               '<:nigersaurus2:722278862079131731>'])
        e = car.embed(
            description=(
                f":rotating_light: {member.mention} has been unbanned {emoji}"
            )
        )
        await ctx.send(embed=e)

    @car.command()
    @car.requires_permissions(manage_roles=True)
    async def mute(self, ctx, member: car.to_member()):
        """
        Adds the muted role to someone
        """
        cmd = self.bot.commands['role']
        role = discord.utils.get(ctx.guild.roles, id=536552924583821313)
        ctx2 = car.copy_ctx(ctx, silent=True)
        await cmd.exec(ctx2, [member, role], {'a': True})
        e = car.embed(description=f":rotating_light: {member} has been muted")

    @car.command()
    @car.requires_permissions(manage_messages=True)
    async def clearchat(self, ctx):
        """
        Clears the chat
        """
        await ctx.send("\n"*100 + "__ __")
        await ctx.reply("Chat cleared!")

    @car.command()
    @car.requires_permissions(manage_messages=True)
    async def purge(self, ctx, amount: car.to_int(lower=1, upper=500)):
        """
        Deletes messages
        """
        deleted = await ctx.channel.purge(limit=amount+1)

        e = car.embed(description=(
            f":rotating_light: Deleted **{len(deleted)}** messages."
        ))
        e.set_footer(text="This message will disappear in 5 seconds.")
        results = await ctx.send(embed=e)
        await asyncio.sleep(5)
        await results.delete()

