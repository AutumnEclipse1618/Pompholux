import logging

import discord.utils

from app import app, ConfigReader, EmojiReader
from core.types.Config import Config
import motor.motor_asyncio
from bot.MyBot import MyBot


config_files = [
    "config/config.ini",
    "config/versions.ini",
]

emoji_file = "config/emoji.json"

if __name__ == "__main__":
    app.config = ConfigReader.read_config(Config, *config_files)

    discord.utils.setup_logging(level=logging.INFO if app.config.Debug.DEBUG else logging.CRITICAL, root=True)

    app.emoji, app.emoji_rev = EmojiReader.read_emoji(emoji_file)

    app.bot = MyBot()

    app.db_client = motor.motor_asyncio.AsyncIOMotorClient(app.config.Database.connection)

    app.bot.run(app.config.Discord.token, log_handler=None)
