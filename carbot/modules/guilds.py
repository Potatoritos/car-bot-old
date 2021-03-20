import discord
import car


class Guilds(car.Cog):
    def __init__(self, bot):
        super().__init__(
            bot,
            global_category="Server",
            global_checks=[
                car.public_channels_only(),
                car.requires_permissions(manage_guild=True)
            ]
        )

    @car.listener
    async def on_member_join(self, member):
        role = self.bot.guild_settings[member.guild.id].role_unverified
        role = discord.utils.get(member.guild.text_channels, id=role)

        if role is not None:
            await member.add_roles(role, reason="Newcomer role") # doesn't work

        greeting = self.bot.guild_settings[member.guild.id].msg_join
        channel = self.bot.guild_settings[member.guild.id].channel_joinleave
        channel = discord.utils.get(member.guild.text_channels, id=channel)

        if greeting == '' or channel is None:
            return

        await channel.send(greeting.format(
            mention=member.mention,
            username=member.name,
            discriminator=member.discriminator,
            id=member.id
        ))

    @car.listener
    async def on_member_remove(self, member):
        farewell = self.bot.guild_settings[member.guild.id].msg_leave
        channel = self.bot.guild_settings[member.guild.id].channel_joinleave
        channel = discord.utils.get(member.guild.text_channels, id=channel)

        if farewell == '' or channel is None:
            return

        await channel.send(farewell.format(
            mention=member.mention,
            username=member.name,
            discriminator=member.discriminator,
            id=member.id
        ))

    @car.command(aliases=["config", "cfg", "set"])
    async def settings(
        self, ctx,
        setting: "The name of the setting you want to change" = None,
        value: "The new value. Leave blank to reset" = None
    ):
        """
        Edits/views bot settings
        Leave `(settings)` blank to view current settings

        General:
        `prefix`: Sets the prefix of the bot (Default: c.)

        Join/leave:
        `msg_join`: Sets the join message.
        `msg_leave`: Sets the leave message.
        The following keywords in these messages will be replaced:
        `{mention}`, `{username}`, `{discriminator}`, `{id}`
        By default, there is no join/leave message.

        Channels:
        `channel_joinleave`: Sets the join/leave announcement channel

        Roles:
        `role_banned`: Sets the banned role
        `role_muted`: Sets the muted role
        `role_unverified`: Sets the role given to all newcomers
        """
        if setting is None:
            e = car.embed(title="Settings")

            for s in car.GUILD_SETTINGS:
                if s.startswith('role_'):
                    id = self.bot.guild_settings[ctx.guild.id][s]
                    role = discord.utils.get(ctx.guild.roles, id=id)
                    if role is None:
                        disp = "*(None)*"
                    else:
                        disp = role.mention

                elif s.startswith('channel_'):
                    id = self.bot.guild_settings[ctx.guild.id][s]
                    channel = discord.utils.get(ctx.guild.text_channels, id=id)
                    if channel is None:
                        disp = "*(None)*"
                    else:
                        disp = channel.mention

                else:
                    disp = self.bot.guild_settings[ctx.guild.id][s]
                    if disp == '':
                        disp = "*(None)*"

                e.add_field(name=s, value=disp, inline=False)

            await ctx.send(embed=e)
            return

        setting = setting.lower()
        if setting not in car.GUILD_SETTINGS:
            raise car.ArgumentError("Invalid setting!", 0)

        if value is None:
            e = car.embed(description=f":gear: `{setting}` has been reset")

        elif setting.startswith('role_'):
            try:
                role = car.to_role().convert(ctx, value)

            except car.ArgumentError as e:
                raise car.ArgumentError(e.error_msg, 1)

            value = role.id
            disp = role.mention
            e = car.embed(
                description=f":gear: `{setting}` has been set to {disp}"
            )

        elif setting.startswith('channel_'):
            try:
                channel = car.to_text_channel().convert(ctx, value)

            except car.ArgumentError as e:
                raise car.ArgumentError(e.error_msg, 1)

            value = channel.id
            disp = channel.mention
            e = car.embed(
                description=f":gear: `{setting}` has been set to {disp}"
            )

        else:
            e = car.embed(
                description=f":gear: `{setting}` has been set to {value}"
            )

        self.bot.guild_settings[ctx.guild.id][setting] = value

        await ctx.send(embed=e)

