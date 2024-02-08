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
        name="The name of the role. Example: My Role",
    )
    async def custom_role(
        self, interaction: discord.Interaction, colour: str = None, name: str = None
    ) -> None:
        if colour and (not colour.startswith("#") or len(colour) != 7):
            await interaction.response.send_message(
                "Invalid colour format. Please provide a valid hex colour (e.g., #FFFFFF)."
            )
            return

        try:
            con = sqlite3.connect("./database.sqlite")
            cur = con.cursor()
            cur.execute(
                "SELECT role_id FROM user WHERE user_id = ?", (interaction.user.id,)
            )
            role_id = cur.fetchone()
            if not role_id:
                cur.execute(
                    "INSERT INTO user(user_id) VALUES(?)", (interaction.user.id,)
                )
                con.commit()
                role_id = cur.lastrowid
            else:
                role_id = role_id[0]

            role = interaction.guild.get_role(role_id)
            if not role:
                name = name or f"{interaction.user.name}'s Role"
                colour = (
                    discord.Colour(int(colour.lstrip("#"), 16))
                    if colour
                    else discord.Colour.default()
                )
                role = await interaction.guild.create_role(name=name, colour=colour)
                position = (
                    interaction.guild.get_role(
                        int(os.getenv("CUSTOM_ROLE_POSITION"))
                    ).position
                    - 1
                )
                await role.edit(position=position)
                cur.execute(
                    "UPDATE user SET role_id = ? WHERE user_id = ?",
                    (role.id, interaction.user.id),
                )
                con.commit()
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    "Role created successfully.", ephemeral=True
                )
            else:
                name = name or role.name
                colour = (
                    discord.Colour(int(colour.lstrip("#"), 16))
                    if colour
                    else role.colour
                )
                await role.edit(name=name, colour=colour)
                await interaction.response.send_message(
                    "Role updated successfully.", ephemeral=True
                )
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred: {e}", ephemeral=True
            )
        finally:
            if con:
                con.close()

    class RoleColourMenu(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.color_roles = {
                "Red": {
                    "id": 1205189540067938405,
                    "emoji": "<:ant_honey:1201179745119916103>",
                },
                "Orange": {
                    "id": 1205230488537669692,
                    "emoji": "<:ant_honey:1201179745119916103>",
                },
                "Yellow": {
                    "id": 1205223532208857160,
                    "emoji": "<:ant_honey:1201179745119916103>",
                },
                "Green": {
                    "id": 1205228398734086194,
                    "emoji": "<:ant_honey:1201179745119916103>",
                },
                "Aqua": {
                    "id": 1205228768168382494,
                    "emoji": "<:ant_honey:1201179745119916103>",
                },
                "Blue": {
                    "id": 1205229138005327924,
                    "emoji": "<:ant_honey:1201179745119916103>",
                },
                "Pink": {
                    "id": 1205229403903107212,
                    "emoji": "<:ant_honey:1201179745119916103>",
                },
                "Purple": {
                    "id": 1205229751539605514,
                    "emoji": "<:ant_honey:1201179745119916103>",
                },
            }
            options = [
                discord.SelectOption(
                    label=role,
                    value=str(data["id"]),
                    emoji=data["emoji"],
                )
                for role, data in self.color_roles.items()
            ]
            self.menu = discord.ui.Select(
                custom_id="colour_role",
                placeholder="Select a colour role.",
                min_values=1,
                max_values=1,
                options=options,
            )
            self.menu.callback = self.callback
            self.add_item(self.menu)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            assert (
                interaction.data is not None and "custom_id" in interaction.data
            ), "Invalid interaction data"
            selected_role_id = int(interaction.data["values"][0])
            selected_role = interaction.guild.get_role(selected_role_id)
            if selected_role:
                roles_to_remove = [
                    interaction.guild.get_role(int(data["id"]))
                    for role, data in self.color_roles.items()
                ]
                await interaction.user.remove_roles(*roles_to_remove)
                await interaction.user.add_roles(selected_role)
                await interaction.followup.send(
                    f"Role {interaction.guild.get_role(selected_role_id).name} selected.",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    "Failed to find the selected role. Please try again.",
                    ephemeral=True,
                )

    @commands.command()
    async def menu(self, ctx):
        await ctx.send("Select a colour role.", view=self.RoleColourMenu())

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.RoleColourMenu())


async def setup(bot):
    await bot.add_cog(CustomRole(bot))
