import discord


class MyModal(discord.ui.Modal):
    async def on_error(self, interaction: discord.Interaction, error: Exception):
        interaction.client.dispatch("modal_error", self, interaction, error)
