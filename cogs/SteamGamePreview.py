import os
import discord
from discord.ext import commands
import requests
from fuzzywuzzy import process
from rapidfuzz import process, fuzz



API_KEY = os.getenv('STEAM_API_KEY')
game_list_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
game_list_response = requests.get(game_list_url)
all_games = game_list_response.json()['applist']['apps'] if game_list_response.status_code == 200 else []


class SteamGamePreview(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Retrieve information about a Steam game by name.")
    async def gameinfo(self, ctx, *, game_name: str):
        await ctx.defer(ephemeral=True)
        games_dict = {game['name']: game['appid'] for game in all_games}
        best_match = process.extractOne(game_name, games_dict.keys(), scorer=fuzz.WRatio, score_cutoff=70)
        if best_match:
            matched_game_name = best_match[0]
            appid = games_dict[matched_game_name]
            url = f"https://store.steampowered.com/api/appdetails?appids={appid}&filters=basic,release_date,price_overview,metacritic,categories,genres,developers"
            response = requests.get(url)
            data = response.json()

            if str(appid) in data and data[str(appid)]['success']:
                game_data = data[str(appid)]['data']
                title = game_data.get('name', 'No title available')
                steam_url = f"https://store.steampowered.com/app/{appid}"
                embed = discord.Embed(title=title, url=steam_url, description=game_data.get('short_description', 'No description available'), color=discord.Color.blue())
                embed.add_field(name="Price", value=game_data.get('price_overview', {}).get('final_formatted', 'Free or N/A'), inline=False)
                embed.add_field(name="Developer", value=", ".join(game_data.get('developers', ['Unknown'])), inline=False)
                embed.add_field(name="Tags", value=", ".join([tag['description'] for tag in game_data.get('genres', [])[:3]]), inline=False)
                embed.add_field(name="Release Date", value=game_data.get('release_date', {}).get('date', 'No release date available'), inline=False)
                embed.set_thumbnail(url=game_data.get('header_image', ''))
                await ctx.respond(embed=embed, ephemeral=True)
            else:
                await ctx.followup.send("Game details could not be retrieved. Please try a different name.", ephemeral=True)
        else:
            await ctx.followup.send("No matching game found. Please check the spelling and try again.", ephemeral=True)




def setup(bot):
    bot.add_cog(SteamGamePreview(bot))

