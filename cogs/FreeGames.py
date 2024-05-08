import discord
from discord.ext import commands, tasks
import requests
from datetime import datetime
import pytz
import os
import json



class FreeGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.epic_endpoint = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=es-ES&country=ES&allowCountries=ES"
        self.known_free_games = self.load_known_games()
        self.channel_id = 1229756652975165522
        self.fixed_urls = {"Thief": "https://store.epicgames.com/en-US/p/thief-5bb95f"}
        self.check_new_games.start()

    def cog_unload(self):
        self.check_new_games.cancel()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def now(self, ctx):
        games = self.fetch_epic_free_games()
        await self.send_free_games(ctx.channel, games, check_known=False)

    @now.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            print("No permissions to run this command.")

    @tasks.loop(minutes=60)
    async def check_new_games(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            new_games = self.fetch_epic_free_games()
            await self.send_free_games(channel, new_games)

    async def send_free_games(self, channel, games, check_known=True):
        for game in games:
            if check_known and game['title'] in self.known_free_games:
                continue
            self.known_free_games.add(game['title'])
            self.save_known_games()
            if game['url'] == "URL not found":
                description = f"**{game['title']}** - Link not available, please search in the [Epic Games Store](https://store.epicgames.com/en-US/free-games)."
            else:
                description = f"**[{game['title']}](<{game['url']}>)**"

            embed = discord.Embed(title="Free Game on Epic Games", description=description)
            embed.set_image(url=game['image'])
            embed.add_field(name="Original Price", value=f"~~€{game['original_price']}~~ ➜ Free", inline=False)
            embed.add_field(name="Open with:",
                            value=f"[EpicGames.com](<{game['url']}>) or [Epic Launcher](https://kev2block.github.io/Website/)",
                            inline=False)
            end_timestamp = int(game['end_date'].timestamp())
            embed.add_field(name="Offer ends:", value=f"<t:{end_timestamp}:R>", inline=False)
            await channel.send(embed=embed)


    def fetch_epic_free_games(self):
        try:
            response = requests.get(self.epic_endpoint)
            data = response.json()
            games = data['data']['Catalog']['searchStore']['elements']
            new_free_games = []
            for game in games:
                if game['promotions'] and game['promotions']['promotionalOffers']:
                    offers = game['promotions']['promotionalOffers'][0]['promotionalOffers']
                    if offers and offers[0]['discountSetting']['discountPercentage'] == 0:
                        start_date = datetime.strptime(offers[0]['startDate'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)
                        end_date = datetime.strptime(offers[0]['endDate'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)
                        image_url = game['keyImages'][0]['url'] if game['keyImages'] else "https://example.com/default_image.png"
                        original_price = game.get('price', {}).get('totalPrice', {}).get('fmtPrice', {}).get('originalPrice', 'N/A')
                        title = game['title']
                        url = self.fixed_urls.get(title, f"https://www.epicgames.com/store/en-US/p/{game.get('productSlug', 'None')}")
                        new_free_games.append({
                            'title': title,
                            'url': url,
                            'image': image_url,
                            'start_date': start_date,
                            'end_date': end_date,
                            'original_price': original_price
                        })
            return new_free_games
        except Exception as e:
            print(f"Failed to fetch Epic Games: {e}")
            return []

    def load_known_games(self):
        if os.path.exists('known_games.json'):
            with open('known_games.json', 'r') as file:
                return set(json.load(file))
        return set()

    def save_known_games(self):
        with open('known_games.json', 'w') as file:
            json.dump(list(self.known_free_games), file)

def setup(bot):
    bot.add_cog(FreeGames(bot))
