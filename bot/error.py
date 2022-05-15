from discord.ext import commands


class UserInputWarning(commands.CommandError):
    __match_args__ = ("message",)

    def __init__(self, message: str):
        self.message: str = message
        super().__init__(message=message)
