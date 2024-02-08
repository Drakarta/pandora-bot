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
        self.channel_id = int(os.getenv("CLOCK_CHANNEL"))
        self.clock.start()

    @tasks.loop(minutes=10)
    async def clock(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"Failed to find channel with ID {self.channel_id}")
            return
        current_time = datetime.datetime.now(tz=zone)
        formatted_minutes = "{:02}".format((current_time.minute // 10) * 10)
        await channel.edit(
            name=f"Time: {current_time.strftime('%H')}:{formatted_minutes} [{current_time.tzname()}]"
        )

    @clock.before_loop
    async def before_clock(self):
        await self.bot.wait_until_ready()
        current_time = datetime.datetime.now()
        delay_seconds = (10 - (current_time.minute % 10)) * 60 - current_time.second
        await asyncio.sleep(delay_seconds)


async def setup(bot):
    await bot.add_cog(Clock(bot))
