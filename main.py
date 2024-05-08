import discord
from discord.ext import commands
import os

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, debug_guilds=[GUILD_ID], help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user} logged in.')


initial_extensions = [
     'cogs.Feedback',
     'cogs.ShowAllRoles',
     'cogs.Moderation',
     'cogs.Notifications',
     'cogs.YoutubeAnounce',
     'cogs.ThreadManager',
     'cogs.SupportTicket',
     'cogs.RolePicker',
     'cogs.FreeGames',
     'cogs.SteamGamePreview',
     'cogs.HelpCommand',
     'cogs.Giveaway',
     'cogs.music_cog',
     'cogs.AiHelper'
]

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run("TOKEN")
