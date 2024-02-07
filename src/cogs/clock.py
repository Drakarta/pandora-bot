from dotenv import load_dotenv

import os
from discord.ext import commands, tasks
import asyncio
import pytz
import datetime

load_dotenv()

zone = pytz.timezone("Europe/Amsterdam")

class Clock(commands.Cog, name="Clock"):
    def __init__(self, bot):
        self.bot = bot
        self.clock.start()

    @tasks.loop(seconds=600)
    async def clock(self):
        channel = await self.bot.fetch_channel(int(os.getenv("CLOCK_CHANNEL")))
        x = str((int(datetime.datetime.now(tz=zone).strftime('%M')) // 10) * 10)
        y = "{:0>2}".format(x)
        await channel.edit(name=f"Time: {datetime.datetime.now(tz=zone).strftime('%H')}:{y} [{datetime.datetime.now(tz=zone).tzname()}]")
    
    @clock.before_loop
    async def before_clock(self):   
        await self.bot.wait_until_ready()
        channel = await self.bot.fetch_channel(int(os.getenv("CLOCK_CHANNEL")))
        x = str((int(datetime.datetime.now(tz=zone).strftime('%M')) // 10) * 10)
        y = "{:0>2}".format(x)
        await channel.edit(name=f"Time: {datetime.datetime.now(tz=zone).strftime('%H')}:{y} [{datetime.datetime.now(tz=zone).tzname()}]")
        await asyncio.sleep((((((int(datetime.datetime.now().strftime('%M')) // 10) * 10) + 10) - int(datetime.datetime.now().strftime('%M'))) * 60) - int(datetime.datetime.now().strftime('%S')))

async def setup(bot):
    await bot.add_cog(Clock(bot))