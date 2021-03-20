import car
import config


bot = car.Bot()

for module in (
    'modules.core',
    'modules.bot_admin',
    'modules.bot_info',
    'modules.guilds',
    'modules.test_module',
    'modules.utility',
    'modules.moderation',
    'modules.typing',
    'modules.pinboard'
):
    bot.load_module(module)

bot.run(config.TOKEN)
