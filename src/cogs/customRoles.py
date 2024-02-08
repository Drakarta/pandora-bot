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

    @app_commands.command(name="role", description="Create and update a custom role.")
    @app_commands.describe(
        colour="The colour of the role in hex format. Example: #FFFFFF", 
        name="The name of the role. Example: My Role"
    )
    async def custom_role(self, interaction: discord.Interaction, colour: str = None, name: str = None) -> None:
        if colour and (not colour.startswith("#") or len(colour) != 7):
            await interaction.response.send_message("Invalid colour format. Please provide a valid hex colour (e.g., #FFFFFF).")
            return

        try:
            con = sqlite3.connect("./database.sqlite")
            cur = con.cursor()
            cur.execute("SELECT role_id FROM user WHERE user_id = ?", (interaction.user.id,))
            role_id = cur.fetchone()
            if not role_id:
                cur.execute("INSERT INTO user(user_id) VALUES(?)", (interaction.user.id,))
                con.commit()
                role_id = cur.lastrowid
            else:
                role_id = role_id[0]

            role = interaction.guild.get_role(role_id)
            if not role:
                name = name or f"{interaction.user.name}'s Role"
                colour = discord.Colour(int(colour.lstrip("#"), 16)) if colour else discord.Colour.default()
                role = await interaction.guild.create_role(name=name, colour=colour)
                position = interaction.guild.get_role(int(os.getenv("CUSTOM_ROLE_POSITION"))).position - 1
                await role.edit(position=position)
                cur.execute("UPDATE user SET role_id = ? WHERE user_id = ?", (role.id, interaction.user.id))
                con.commit()
                await interaction.user.add_roles(role)
                await interaction.response.send_message("Role created successfully.")
            else:
                name = name or role.name
                colour = discord.Colour(int(colour.lstrip("#"), 16)) if colour else role.colour
                await role.edit(name=name, colour=colour)
                await interaction.response.send_message("Role updated successfully.")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}")
        finally:
            if con:
                con.close()

async def setup(bot):
    await bot.add_cog(CustomRole(bot))