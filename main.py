import logging

import discord.utils

from app import ConfigReader, EmojiReader
from app.MyApp import MyApp
from core.types.Config import Config
from bot.MyBot import MyBot


config_files = [
    "config/config.ini",
    "config/versions.ini",
]

emoji_file = "config/emoji.json"

if __name__ == "__main__":
    app = MyApp()

    app.config = ConfigReader.read_config(Config, *config_files)

    discord.utils.setup_logging(level=logging.INFO if app.config.Debug.DEBUG else logging.CRITICAL, root=True)

    app.emoji, app.emoji_rev = EmojiReader.read_emoji(emoji_file)
    app.bot = app.create_component(MyBot)

    app.run()
