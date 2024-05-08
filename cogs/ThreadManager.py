import discord
from discord.ext import commands
import asyncio


TARGET_CHANNEL_ID = CHANNEL_ID

class ThreadManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or not message.content.strip():
            return

        if message.channel.id == TARGET_CHANNEL_ID:
            thread_name = message.content.strip()[:100]
            if not thread_name:
                thread_name = "Unknown thread"

#            try:
#                thread = await message.create_thread(name=thread_name, auto_archive_duration=60)
#                print(f"Thread '{thread.name}' got created.")

#                await asyncio.sleep(86400)

#                await thread.delete()
#                print(f"Thread '{thread.name}' got deleted.")
#            except discord.errors.HTTPException as e:
#                print(f"Error: {e}")

def setup(bot):
    bot.add_cog(ThreadManager(bot))
