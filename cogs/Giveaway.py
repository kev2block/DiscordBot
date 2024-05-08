import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
import random
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo



def load_entrants(filename):
    try:
        with open(filename, 'r') as file:
            data = file.read()
            if not data:
                print("JSON file is empty, initializing an empty dictionary.")
                return {}
            return json.loads(data)
    except FileNotFoundError:
        print("JSON file not found, creating a new one.")
        with open(filename, 'w') as file:
            file.write("{}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}

def save_entrants(filename, entrants):
    serializable_entrants = {
        k: {
            "channel_id": v["channel_id"],
            "message_id": v["message_id"],
            "prize": v["prize"],
            "winners_count": v["winners_count"],
            "entrants": list(v["entrants"]),
            "end_time": v["end_time"],
            "host": v["host"],
            "has_ended": v["has_ended"]
        } for k, v in entrants.items()
    }
    try:
        with open(filename, "w") as file:
            json.dump(serializable_entrants, file, indent=4)
    except IOError as e:
        print(f"Failed to save entrants: {e}")



class GiveawayButton(Button):
    def __init__(self, label, giveaway_cog):
        super().__init__(style=discord.ButtonStyle.green, label=label, custom_id=f"{label.lower().replace(' ', '_')}")
        self.giveaway_cog = giveaway_cog

    async def callback(self, interaction):
        await self.giveaway_cog.join_giveaway_callback(interaction)

class GiveawayView(View):
    def __init__(self, giveaway_cog, message_id):
        super().__init__(timeout=None)
        self.add_item(GiveawayButton("Join Giveaway", giveaway_cog))
        self.message_id = message_id

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaways = {}
        self.entrants_file = "names.json"
        self.entrants = load_entrants(self.entrants_file)
        self.bot.loop.create_task(self.setup_persistent_views())

    async def set_giveaway_view(self, message_id):
        data = self.giveaways.get(message_id)
        channel_id = data.get("channel_id")
        channel = self.bot.get_channel(channel_id)
        if channel:
            try:
                message = await channel.fetch_message(message_id)
                view = GiveawayView(self, message_id)
                await message.edit(view=view)
                self.bot.add_view(view, message_id=message_id)
            except discord.NotFound:
                print(f"Message {message_id} not found in channel {channel_id}")

    async def setup_persistent_views(self):
        await self.bot.wait_until_ready()
        self.giveaways = load_entrants(self.entrants_file)
        current_time = datetime.now(ZoneInfo("UTC")).timestamp()
        for message_id, data in self.giveaways.items():
            channel_id = data.get("channel_id")
            if not channel_id or data.get("has_ended", False):
                continue
            end_time = data.get("end_time", 0)
            remaining_time = end_time - current_time
            if remaining_time <= 0:
                await self.end_giveaway(message_id)
            else:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    try:
                        message = await channel.fetch_message(message_id)
                        view = GiveawayView(self, message_id)
                        await message.edit(view=view)
                        self.bot.add_view(view, message_id=message_id)
                        self.bot.loop.create_task(self.update_giveaway_message(message_id))
                        self.bot.loop.create_task(self.end_giveaway_after_duration(message_id, remaining_time))
                    except discord.NotFound:
                        continue

    async def end_giveaway_after_duration(self, message_id, duration):
        await asyncio.sleep(duration)
        await self.end_giveaway(message_id)

    async def setup_giveaway(self, interaction, duration, winners, prize):
        current_time = datetime.now(ZoneInfo("UTC"))
        end_time = current_time + timedelta(seconds=duration)
        unix_timestamp = int(end_time.timestamp())

        embed = discord.Embed(
            title="🎉 Giveaway! 🎉",
            description=f"**Prize:** {prize}\n**Winners:** {winners}\n\n**Ends:** <t:{unix_timestamp}:R>",
            color=discord.Color.green()
        )
        embed.add_field(name="Hosted by", value=interaction.user.mention, inline=False)
        embed.add_field(name="Entries", value="0", inline=False)

        message = await interaction.channel.send(embed=embed)
        message_id = str(message.id)
        view = GiveawayView(self, message_id)
        await message.edit(view=view)

        self.giveaways[message_id] = {
            "channel_id": interaction.channel.id,
            "message_id": message_id,
            "prize": prize,
            "winners_count": winners,
            "entrants": [],
            "end_time": int(end_time.timestamp()),
            "host": interaction.user.mention,
            "has_ended": False
        }
        save_entrants(self.entrants_file, self.giveaways)

        self.bot.loop.create_task(self.end_giveaway_after_duration(message_id, duration))
        self.bot.loop.create_task(self.update_giveaway_message(message_id))

    async def check_giveaway_end_times(self):
        while True:
            current_time = datetime.now(ZoneInfo("UTC")).timestamp()
            for message_id, giveaway in list(self.giveaways.items()):
                if not giveaway["has_ended"] and current_time >= giveaway["end_time"]:
                    await self.end_giveaway(message_id)
            await asyncio.sleep(1)

    async def join_giveaway_callback(self, interaction):
        message_id = str(interaction.message.id)
        if message_id in self.giveaways:
            giveaway = self.giveaways[message_id]
            user_id = str(interaction.user.id)
            if user_id in giveaway["entrants"]:
                await interaction.response.send_message("You are already in the giveaway!", ephemeral=True)
            else:
                giveaway["entrants"].append(user_id)
                save_entrants(self.entrants_file, self.giveaways)
                await interaction.response.send_message("You have joined the giveaway!", ephemeral=True)
        else:
            await interaction.response.send_message("No active giveaway found for this message.", ephemeral=True)

    async def update_giveaway_message(self, message_id):
        while message_id in self.giveaways and not self.giveaways[message_id]["has_ended"]:
            giveaway = self.giveaways[message_id]
            channel = self.bot.get_channel(giveaway["channel_id"])
            if channel:
                try:
                    message = await channel.fetch_message(message_id)
                    entrants_count = len(giveaway["entrants"])
                    embed = message.embeds[0]
                    embed.set_field_at(1, name="Entries", value=str(entrants_count), inline=False)
                    await message.edit(embed=embed)
                    await asyncio.sleep(5)
                except discord.NotFound:
                    print(f"Message with ID {message_id} not found in channel. Stopping updates.")
                    break
            else:
                print("Channel not found. Stopping updates.")
                break


    async def end_giveaway(self, message_id):
        giveaway = self.giveaways.get(message_id)
        if giveaway and not giveaway["has_ended"]:
            giveaway["has_ended"] = True
            ended_time = datetime.now(ZoneInfo("UTC"))
            now_unix_timestamp = int(ended_time.timestamp())

            channel_id = giveaway["channel_id"]
            channel = self.bot.get_channel(channel_id)
            if not channel:
                print(f"Channel with ID {channel_id} not found.")
                return

            try:
                message = await channel.fetch_message(message_id)
            except discord.NotFound:
                print(f"Message with ID {message_id} not found in channel {channel_id}.")
                return

            entrants_list = list(giveaway["entrants"])
            embed = discord.Embed(
                title="🎉 Giveaway Ended! 🎉",
                description=f"**Prize:** {giveaway['prize']}\n\n**Ended:** <t:{now_unix_timestamp}:R>",
                color=discord.Color.red()
            )
            embed.add_field(name="Entries", value=str(len(entrants_list)), inline=False)

            if len(giveaway['entrants']) >= giveaway['winners_count']:
                winners = random.sample(giveaway['entrants'], giveaway['winners_count'])
                winners_mentions = ', '.join(f'<@{winner}>' for winner in winners)
                embed.add_field(name="Winner(s)", value=winners_mentions, inline=False)
                await message.edit(embed=embed, view=None)
                await message.channel.send(f"Congratulations {winners_mentions}! You won the **{giveaway['prize']}**!")
            else:
                embed.add_field(name="Winner(s)", value="Not enough participants for a valid draw!", inline=False)
                await message.edit(embed=embed, view=None)

            save_entrants(self.entrants_file, self.giveaways)

    async def reroll_giveaway(self, message_id: str, num_winners: int):
        giveaway = self.giveaways.get(message_id)
        if not giveaway:
            print("No giveaway found with the provided message ID.")
            return

        if not giveaway.get("has_ended", False):
            print("Giveaway is still active, please end it before rerolling.")
            return

        channel_id = giveaway["channel_id"]
        channel = self.bot.get_channel(channel_id)
        if not channel:
            print("Channel not found.")
            return

        try:
            message = await channel.fetch_message(giveaway["message_id"])
        except discord.NotFound:
            print("Message not found in channel.")
            return

        entrants_list = list(giveaway["entrants"])
        if len(entrants_list) < num_winners:
            print("Not enough participants to reroll winners.")
            return

        winners = random.sample(entrants_list, num_winners)
        winners_mentions = ', '.join(f'<@{winner}>' for winner in winners)

        embed = message.embeds[0]
        for i, field in enumerate(embed.fields):
            if field.name == "Winner(s)":
                embed.set_field_at(i, name="Winner(s)", value=winners_mentions, inline=False)
                break
        await message.edit(embed=embed)
        await channel.send(f"New giveaway winner(s) rolled: {winners_mentions}")

    @commands.slash_command(name="giveaway")
    @commands.has_permissions(administrator=True)
    async def start_giveaway(self, ctx, time: int, winners: int, prize: str):
        await ctx.defer(ephemeral=True)
        await self.setup_giveaway(ctx, time, winners, prize)

    @commands.slash_command(name="giveawayreroll")
    @commands.has_permissions(administrator=True)
    async def reroll_giveaway_command(self, ctx, message_id: str, winners: int):
        await ctx.defer(ephemeral=True)
        if message_id in self.giveaways:
            await self.reroll_giveaway(message_id, winners)
            await ctx.respond(f"Giveaway with message ID {message_id} has been rerolled with {winners} winners updated!", ephemeral=True)
        else:
            await ctx.respond(f"No giveaway found with message ID {message_id}. Please ensure it is correct.", ephemeral=True)


@commands.Cog.listener()
async def on_ready(self):
    print("Bot is ready. Setting up tasks for giveaway checks and views...")
    await self.setup_persistent_views()
    self.bot.loop.create_task(self.check_giveaway_end_times())




def setup(bot):
    bot.add_cog(Giveaway(bot))
