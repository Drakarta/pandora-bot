from dotenv import load_dotenv
import time

import os
import discord
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="~", intents=intents, case_insensitive=False)

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"Loaded {filename}")
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
        print(f"Logged in as {self.user}")

bot = Bot()

bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="with my box."))

@bot.command()
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync(guild=None)
    await ctx.send('Command tree synced.')

@bot.command()
@commands.is_owner()
async def reload(ctx):
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                bot.unload_extension(cog_name)
            except commands.ExtensionNotLoaded:
                pass
            finally:
                await bot.load_extension(cog_name)
                print(f"Reloaded {filename}")
    await ctx.send('Cogs reloaded.')

bot.run(os.getenv("DISCORD_TOKEN"))