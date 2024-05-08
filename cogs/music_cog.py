from discord.ext import commands
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import asyncio
import discord

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'source_address': '0.0.0.0'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = None
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)

    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return {'source': item, 'title': title}
        search = VideosSearch(item, limit=1)
        return {'source': search.result()["result"][0]["link"], 'title': search.result()["result"][0]["title"]}

    async def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)
            data = await asyncio.to_thread(self.ytdl.extract_info, m_url, download=False)
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, **self.FFMPEG_OPTIONS), after=lambda e: self.bot.loop.create_task(self.play_next()))

    async def play_music(self, ctx):
        if not self.music_queue:
            self.is_playing = False
            return
        self.is_playing = True
        m_url = self.music_queue[0][0]['source']
        if self.vc is None or not self.vc.is_connected():
            self.vc = await self.music_queue[0][1].connect()
            if self.vc is None:
                await ctx.send("Could not connect to the voice channel")
                return
        self.music_queue.pop(0)
        data = await asyncio.to_thread(self.ytdl.extract_info, m_url, download=False)
        song = data['url']
        self.vc.play(discord.FFmpegPCMAudio(song, **self.FFMPEG_OPTIONS), after=lambda e: self.bot.loop.create_task(self.play_next()))

    @commands.slash_command(name="play", description="Plays a selected song from youtube")
    async def play(self, ctx, *, query: str):
        await ctx.defer(
            ephemeral=True)
        try:
            voice_channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.followup.send("You need to connect to a voice channel first!")
            return
        if self.is_paused:
            self.vc.resume()
            await ctx.followup.send("Resuming the paused song.")
        else:
            song = self.search_yt(query)
            if isinstance(song, bool):
                await ctx.followup.send(
                    "Could not download the song. Incorrect format, try another keyword. This could be due to playlist or a livestream format.")
            else:
                await ctx.followup.send(f"**'{song['title']}'** added to the queue")
                self.music_queue.append([song, voice_channel])
                if not self.is_playing:
                    await self.play_music(ctx)

    @commands.slash_command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx):
        await ctx.defer(ephemeral=True)
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
            await ctx.followup.send('Paused.')

    @commands.slash_command(name="resume", aliases=["r"], help="Resumes playing the current song")
    async def resume(self, ctx):
        await ctx.defer(ephemeral=True)
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()
            await ctx.followup.send('Resumed.')

    @commands.slash_command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        await ctx.defer(ephemeral=True)
        if self.vc and self.vc.is_playing():
            self.vc.stop()
            await self.play_music(ctx)
            await ctx.followup.send('Skipped the track..')

    @commands.slash_command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        await ctx.defer(ephemeral=True)
        retval = ""
        for i, song in enumerate(self.music_queue):
            retval += f"#{i+1} - {song[0]['title']}\n"
        if retval:
            await ctx.send(f"Current queue:\n{retval}")
        else:
            await ctx.send("No music in queue")

    @commands.slash_command(name="clearq", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clearq(self, ctx):
        await ctx.defer(ephemeral=True)
        if self.vc and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        self.is_playing = False
        self.is_paused = False
        await ctx.send("Music queue cleared")
        await ctx.followup.send('Cleared the queue')

    @commands.slash_command(name="stop", aliases=["disconnect", "leave", "d"], help="Disconnects the bot from the voice channel")
    async def stop(self, ctx):
        await ctx.defer(ephemeral=True)
        self.is_playing = False
        self.is_paused = False
        if self.vc:
            await self.vc.disconnect()
            await ctx.followup.send('Stopped playing music.')

    @commands.slash_command(name="remove", help="Removes the specified song from the queue")
    async def remove(self, ctx, index: int):
        await ctx.defer(ephemeral=True)
        if 0 <= index < len(self.music_queue):
            removed = self.music_queue.pop(index)
            await ctx.send(f"Removed **{removed[0]['title']}** from the queue.")
            await ctx.followup.send(f"Removed **{removed[0]['title']}** from the queue.")
        else:
            await ctx.send("Invalid index.")


def setup(bot):
    bot.add_cog(music_cog(bot))
