import discord
from discord.ext import commands, tasks
import scrapetube

class YoutubeAnounce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = {
            "Youtube Name": "https://youtube.com/@name",
        }
        self.discord_channel_id = DISCORD_CHANNEL_ID
        self.videos = {}
        self.check_videos_loop.start()

    @tasks.loop(minutes=1)
    async def check_videos_loop(self):
        discord_channel = self.bot.get_channel(self.discord_channel_id)
        if discord_channel is None:
            print("Channel not found.")
            return

        #print("Checking for new videos...")
        for channel_name, channel_url in self.channels.items():
            #print(f"Checking channel {channel_name}")
            try:
                videos = scrapetube.get_channel(channel_url=channel_url, limit=5)
                video_ids = [video["videoId"] for video in videos]

                if self.videos.get(channel_name) is None:
                    self.videos[channel_name] = video_ids
                    continue

                for video_id in video_ids:
                    if video_id not in self.videos[channel_name]:
                        url = f"https://youtu.be/{video_id}"
                        await discord_channel.send(f"**{channel_name}** has uploaded a new video\n\n{url}")
                        print(f"New video found for channel {channel_name}: {url}")

                self.videos[channel_name] = video_ids
            except Exception as e:
                print(f"Error fetching channel {channel_name}: {e}")

    @check_videos_loop.before_loop
    async def before_check_videos_loop(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(YoutubeAnounce(bot))
