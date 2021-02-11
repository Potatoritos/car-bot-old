import car
import time
import os
import psutil
from datetime import datetime


class BotInfo(car.Cog):
    def __init__(self, bot):
        super().__init__(bot, global_category="Bot")

    @car.command()
    async def help(self, ctx, command: car.to_command() = None):
        """
        Displays the usage of a command
        Lists all commands if `[command]` is not specified
        """
        if command is not None:
            await ctx.send(embed=car.command_help(command, ctx))
            return

        e = car.embed(
            title="Command List",
            description=(
                f"Use ``{ctx.prefix}syntax`` for help on how to use the bot\n"
                f"Use ``{ctx.prefix}help [command]`` to view command usage\n"
            )
        )

        commands = {}

        for cmd in self.bot.commands:

            if cmd.category == "Hidden":
                continue

            if cmd.category not in commands:
                commands[cmd.category] = []

            commands[cmd.category].append(cmd.name)

        for category in commands:
            e.add_field(
                name=category,
                value=" ".join([f"`{cmd}`" for cmd in commands[category]]),
                inline=False
            )

        await ctx.send(embed=e)
        return

    @car.command()
    async def ping(self, ctx):
        """
        Displays latency
        """
        p = f":heart: {int(self.bot.latency*1000)}ms"
        e = car.embed(description=p)

        bef = time.monotonic()
        msg = await ctx.send("Pong!", embed=e)

        delta = time.monotonic() - bef
        p += f"\n:envelope: {int(delta*1000)}ms"

        await msg.edit(embed=car.embed(description=p))

    @car.command()
    async def info(self, ctx):
        """
        Displays bot info
        """
        process = psutil.Process(os.getpid())
        e = car.embed()
        mem = f"{round(process.memory_info().rss/(1024**2), 1)} MB"
        e.add_field(name="Memory usage", value=mem)

        await ctx.send(embed=e)

    @car.command()
    async def syntax(self, ctx):
        """
        Displays syntax help
        """
        e = car.embed()

        e.add_field(name="Using commands", value=(
            f"To use a command, type my prefix (`{ctx.prefix}`), and then "
            "the command name. Commands can be triggered by sending and "
            "editing messages."
        ), inline=False)

        e.add_field(name="Parameters", value=(
            "When viewing command help, you will see something like this: \n"
            f"``{ctx.prefix}command_name [param1] [param2] (param3)``\n\n"
            "The text enclosed in brackets (`[]` and `()`) are parameters. "
            "Parameters enclosed in `[]` are required, while parameters "
            "enclosed in `()` are optional. To set the value of these "
            "parameters, type the parameters after the command name, "
            f"all seperated by spaces. For example:\n``{ctx.prefix}"
            "command_name value_for_param1 value_for_param2``"
        ), inline=False)

        e.add_field(name="Spaces in parameters", value=(
            "Parameters are seperated by spaces. To include spaces in a "
            "parameter, surround it with double quotes (`\"\"`). This is not "
            "required if you are changing the last parameter. For example:\n"
            f"``{ctx.prefix}command_name \"value for param 1\" value for "
            "param 2``"
        ), inline=False)

        e.add_field(name="Double quotes in parameters", value=(
            "To include double quotes in a quoted parameter, "
            "put a backslash (`\`) before the internal quotes. (Because of "
            "markdown, you technically have to put two backslashes before "
            "the quotes; one of these backslashes should be greyed out, and "
            "the other should not be greyed out)"

        ), inline=False)

        e.add_field(name="Optional parameters", value=(
            "To specify optional parameters, type `--name value`, where "
            "`name` is the name of the optional parameter, a space, and "
            "`value` is the value the parameter (this is not always "
            "required). To have spaces in optional parameters, surround the "
            "value with double quotes. You can specify multiple "
            "single-letter optional parameters by typing `-abcde...` where "
            "each letter is some optional argument."
        ), inline=False)

        await ctx.send(embed=e)

