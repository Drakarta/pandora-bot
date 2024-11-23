from dotenv import load_dotenv

import os
import discord
from discord import app_commands
from discord.ext import commands

load_dotenv()


class VoiceChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.create_vc_channel_id = int(os.getenv("CREATE_VC_CHANNEL"))
        self.active_vc_category_id = int(os.getenv("ACTIVE_VC_CATEGORY"))
        self.vc_owner_role_id = int(os.getenv("VC_OWNER_ROLE"))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if (
            after.channel is not None
            and after.channel.id == self.create_vc_channel_id
            and not member.bot
        ):
            new_channel = await member.guild.create_voice_channel(
                f"{member.name}'s channel",
                category=discord.Object(id=self.active_vc_category_id),
            )
            await member.add_roles(member.guild.get_role(self.vc_owner_role_id))
            await member.move_to(new_channel)
        if (
            before.channel is not None
            and before.channel.id
            not in [self.create_vc_channel_id, before.channel.guild.afk_channel]
            and before.channel.category_id == self.active_vc_category_id
        ):
            if member.guild.get_role(self.vc_owner_role_id) in member.roles:
                await member.remove_roles(member.guild.get_role(self.vc_owner_role_id))
                if len(before.channel.members) != 0:
                    await before.channel.members[0].add_roles(
                        member.guild.get_role(self.vc_owner_role_id)
                    )
                    return
            if len(before.channel.members) == 0:
                await before.channel.delete()

    @app_commands.command(name="channel", description="Create a voice channel.")
    @app_commands.describe(
        name="Change the name of the channel.",
        limit="The user limit of the channel. 0 = unlimited",
        lock="Lock the channel.",
        whitelist="Whitelist a user to the channel when locked.",
        promote="Promote a user to VC Owner.",
    )
    async def channel(
        self,
        interaction: discord.Interaction,
        name: str = None,
        limit: app_commands.Range[int, 0, 99] = None,
        lock: bool = None,
        whitelist: discord.User = None,
        promote: discord.User = None,
    ) -> None:
        channel = interaction.user.voice.channel
        if channel is None:
            await interaction.response.send_message(
                "You must be in a voice channel to use this command", ephemeral=True
            )
            return
        if promote is not None:
            if promote.voice.channel != channel:
                await interaction.response.send_message(
                    "The user must be in the channel to be promoted.", ephemeral=True
                )
                return
            await promote.add_roles(interaction.guild.get_role(self.vc_owner_role_id))
            await interaction.user.remove_roles(
                interaction.guild.get_role(self.vc_owner_role_id)
            )
            try:
                await interaction.response.send_message(
                    f"{promote.mention} has been promoted to VC Owner."
                )
            except discord.InteractionResponded:
                await interaction.followup.send(
                    f"{promote.mention} has been promoted to VC Owner."
                )
        if lock is not None:
            await channel.set_permissions(
                interaction.guild.default_role, connect=not lock
            )
        if whitelist is not None:
            await channel.set_permissions(whitelist, connect=True)
            try:
                await interaction.response.send_message(
                    f"{whitelist.mention} has been whitelisted."
                )
            except discord.InteractionResponded:
                await interaction.followup.send(
                    f"{whitelist.mention} has been whitelisted."
                )
        if name is not None or limit is not None:
            if name is None:
                name = channel.name
            if limit is None:
                limit = channel.user_limit
            await channel.edit(name=name, user_limit=limit)
        try:
            await interaction.followup.send("Channel has been updated", ephemeral=True)
        except discord.InteractionResponded:
            await interaction.response.send_message(
                "Channel has been updated", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(VoiceChannel(bot))
