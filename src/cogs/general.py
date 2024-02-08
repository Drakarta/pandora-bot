from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands

load_dotenv()


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"Pong! ``{round(self.bot.latency * 1000)}ms``"
        )


async def setup(bot):
    await bot.add_cog(General(bot))
