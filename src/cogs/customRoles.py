from dotenv import load_dotenv

import sqlite3

import os
import discord
from discord import app_commands
from discord.ext import commands

load_dotenv()

class CustomRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def role_check(self, interaction: discord.Interaction) -> bool:
        for role in interaction.user.roles:
            if role.id in os.getenv("PRIVILEGED_ROLES").split(", "):
                return True
        return False

    @app_commands.command(name="role", description="Create and update a custom role.")
    @app_commands.describe(colour="The colour of the role in hex format. Example: #FFFFFF", name="The name of the role. Example: My Role")
    @app_commands.check(role_check)
    async def custom_role(self, interaction: discord.Interaction, colour: str = None, name: str = None) -> None:
        if colour is not None:
            colour = colour.replace("#", "").replace("0x", "")
            if len(colour) != 6:
                await interaction.response.send_message("Invalid colour")
                return
        con = sqlite3.connect("./database.sqlite")
        cur = con.cursor()
        cur.execute("SELECT role_id FROM user WHERE user_id = ?", (interaction.user.id,))
        result = cur.fetchone()
        if result is None:
            cur.execute("INSERT INTO user(user_id) VALUES(?)", (interaction.user.id,))
            con.commit()
        result = cur.execute("SELECT role_id FROM user WHERE user_id = ?", (interaction.user.id,))
        role_id = result.fetchone()[0]
        if result is None or interaction.guild.get_role(role_id) is None:
            if name is None:
                name = f"{interaction.user.name}'s role"
            if colour is None:
                colour = "FFFFFF"
            role = await interaction.guild.create_role(name=name, colour=discord.Colour.from_str(f"#{colour}"))
            await role.edit(position=interaction.guild.get_role(1203859877504491570).position - 1)
            cur.execute("UPDATE user SET role_id = ? WHERE user_id = ?", (role.id, interaction.user.id))
            con.commit()
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Role created")
        else:
            role = interaction.guild.get_role(role_id)
            if name is None:
                name = role.name
            if colour is None:
                colour = str(role.colour).replace("#", "")
            await role.edit(name=name, colour=discord.Colour.from_str(f"#{colour}"))
            await interaction.response.send_message("Role updated")

async def setup(bot):
    await bot.add_cog(CustomRole(bot))