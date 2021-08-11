import discord
import car
import random
import asyncio
from collections import deque
import time
import re


class Moderation(car.Cog):
    def __init__(self, bot):
        super().__init__(
            bot=bot,
            global_category="Moderation",
            global_checks=[car.guild_must_be_id(495327409487478785)]
        )
        self.vc_prev_msg = None
        self.vc_prev_msg_uid = None
        self.vc_prev_msg_cnt = 0

        self.vc_cnt = {}
        self.vc_dq = deque()

    @car.listener
    async def on_message(self, msg):
        if msg.guild is None:
            return
        if msg.guild.id != 495327409487478785:
            return

        if msg.channel.id == 818615295068733500:
            self.vc_prev_msg_cnt += 1

    @car.listener
    async def on_voice_state_update(self, member, bef, aft):
        if member.guild.id != 495327409487478785:
            return
        if member.bot or bef.channel == aft.channel:
            return

        if aft.channel is None:
            status = "◀—"
            channel = bef.channel
        else:
            status = "—▶"
            channel = aft.channel

        status_msg = f"`{status}` <#{channel.id}>"

        while len(self.vc_dq) and time.monotonic() - self.vc_dq[0][0] > 15:
            action = self.vc_dq.popleft()
            self.vc_cnt[action[1]] -= 1
            
        if member.id not in self.vc_cnt:
            self.vc_cnt[member.id] = 0
        self.vc_cnt[member.id] += 1
        self.vc_dq.append((time.monotonic(), member.id))

        if self.vc_cnt[member.id] > 5:
            return

        if self.vc_prev_msg is not None and self.vc_prev_msg_cnt <= 1 \
                and member.id == self.vc_prev_msg_uid:
            prev = self.vc_prev_msg.embeds[0]
            e = car.embed(description=f"{prev.description}\n{status_msg}")
            e.set_author(name=prev.author.name, icon_url=prev.author.icon_url)
            await self.vc_prev_msg.edit(embed=e)
        else:
            e = car.embed(description=status_msg)
            e.set_author(name=member.name,
                            icon_url=member.avatar_url_as(size=32))
            log_channel = discord.utils.get(member.guild.text_channels,
                                            id=818615295068733500)
            self.vc_prev_msg_cnt = 0
            msg = await log_channel.send(embed=e)
            self.vc_prev_msg = msg
            self.vc_prev_msg_uid = member.id
    
    @car.listener
    async def on_message_edit(self, bef, aft):
        if bef.guild.id != 495327409487478785:
            return
        if bef.author.bot or bef.content == aft.content:
            return
        # TODO: handle len(bef) + len(aft) > 2000
        c = discord.utils.get(bef.guild.text_channels, id=631182593718484992)
        e = car.embed(description=(
            f"[[Jump]]({bef.jump_url}) {bef.author.mention} in"
            f"{bef.channel.mention}"
        ))
        e.set_author(name="Message Edit",
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

    @car.listener
    async def on_reaction_add(self, reaction, user):
        try:
            if reaction.id != "":
                side = 0
            elif reaction.id != "":
                side = 1
            else:
                return
        except AttributeError:
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

        e = car.embed(
            description=f":rotating_light: {member.mention} has been muted"
        )
        await ctx.send(embed=e)

    @car.command()
    @car.requires_permissions(manage_roles=True)
    async def unmute(self, ctx, member: car.to_member()):
        """
        Removes the muted role from someone
        """
        cmd = self.bot.commands['role']
        role = discord.utils.get(ctx.guild.roles, id=536552924583821313)
        ctx2 = car.copy_ctx(ctx, silent=True)
        await cmd.exec(ctx2, [member, role], {'r': True})

        e = car.embed(
            description=f":rotating_light: {member.mention} has been unmuted"
        )
        await ctx.send(embed=e)

    @car.command()
    @car.requires_permissions(manage_messages=True)
    async def clearchat(self, ctx):
        """
        Clears the chat
        """
        await ctx.send("Clearing chat..." + "\n"*200 + "** **")
        e = car.embed(description=":rotating_light: Chat cleared!")
        e.set_footer(text="This message will disappear in 5 seconds.")
        m = await ctx.send(embed=e)
        await asyncio.sleep(5)
        await m.delete()

    @car.command()
    @car.requires_permissions(manage_messages=True)
    async def purge(
        self, ctx,
        amount: car.to_int(lower=1, upper=500) // (
            "the amount of messages to consider"
        ),
        *,
        e: "When specified, excludes instead of includes" = False,
        b: "When specified, only includes bots" = False,
        u: ("colon seperated members", "The members to include") = None,
        r: ("regex", "Includes messages that match a regex") = None
    ):
        """
        Deletes messages

        **Examples**
        `purge 100 -b`
        Purge the last 100 messages, only including bots

        `purge 200 -eb`
        Purge the last 100 messages, excluding bots

        `purge 10 -u member1`
        Purge the last 10 messages, only including messages by member1

        `purge 30 -ebu member1:member2:member3`
        Purge the last 30 messages, excluding bots and the specified members
        """
        conv = car.to_member()
        if u is None:
            members = set()
        else:
            members = {conv.convert(ctx, m) for m in u.split(':')}

        def check(msg):
            if (b and msg.author.bot) or (u and msg.author in members) \
                    or (r and re.match(r, msg.content, re.DOTALL)):
                return not e
            return e

        if not e and not b and u is None and r is None:
            deleted = await ctx.channel.purge(limit=amount+1)
        else:
            deleted = await ctx.channel.purge(limit=amount+1, check=check)

        e = car.embed(description=(
            f":rotating_light: Deleted **{len(deleted)}** messages."
        ))
        e.set_footer(text="This message will disappear in 5 seconds.")
        results = await ctx.send(embed=e)
        await asyncio.sleep(5)
        await results.delete()

