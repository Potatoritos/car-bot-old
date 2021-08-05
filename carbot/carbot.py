import car
import config


bot = car.Bot()

for module in (
    'modules.core',
    'modules.bot_admin',
    'modules.bot_info',
    'modules.guilds',
    'modules.utility',
    'modules.moderation',
    'modules.typing',
    'modules.pinboard',
    'modules.sound',
    'modules.simulation'
):
    bot.load_module(module)

bot.run(config.TOKEN)
