from app import ConfigReader
from app.MyApp import MyApp
from core.types.Config import Config
from bot.MyBot import MyBot


config_files = [
    "config/config.ini",
    "config/versions.ini",
]


if __name__ == "__main__":
    app = MyApp()

    app.config = ConfigReader.read_config(Config, *config_files)
    app.bot = app.create_component(MyBot)

    app.run()
