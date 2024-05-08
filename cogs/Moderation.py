import discord
from discord.ext import commands
from datetime import datetime, timedelta
import collections
from collections import defaultdict, deque
from discord.ui import Button, View, Modal, InputText
import math
import json
from discord.commands import Option
import asyncio



def load_warnings():
    try:
        with open("warnings.json", "r") as f:
            warnings = json.load(f)
            return warnings
    except FileNotFoundError:
        return {}

def save_warnings(warnings):
    with open("warnings.json", "w") as f:
        json.dump(warnings, f, indent=4)



class UnbanRequestModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Unban Request")
        self.add_item(discord.ui.InputText(label="Why should your ban be lifted?", style=discord.InputTextStyle.long))
        self.view = view

    async def callback(self, interaction: discord.Interaction):
        admin_channel = interaction.client.get_channel(Moderation.LOG_CHANNEL_ID)
        embed = discord.Embed(title="Unban Request", description=f"Request from {interaction.user.display_name} (ID: {interaction.user.id})")
        embed.add_field(name="Explanation", value=self.children[0].value[:4000], inline=False)
        view = discord.ui.View()
        view.add_item(AdminResponseButton(interaction.user.id))
        await admin_channel.send(embed=embed, view=view)
        await interaction.response.send_message("Your unban request has been sent to the admins. Please wait for a answer.", ephemeral=True)
        for item in self.view.children:
            if isinstance(item, UnbanRequestButton):
                item.disabled = True
        await interaction.message.edit(view=self.view)


class UnbanRequestView(View):
    def __init__(self, member_id):
        super().__init__(timeout=None)
        self.add_item(UnbanRequestButton(member_id))

class UnbanRequestButton(discord.ui.Button):
    def __init__(self, member_id):
        super().__init__(style=discord.ButtonStyle.primary, label="Request Unban", custom_id=f"unban_request_{member_id}")
        self.member_id = member_id

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        modal = UnbanRequestModal(view)
        await interaction.response.send_modal(modal)


class ReviewModal(discord.ui.Modal):
    def __init__(self, member_id):
        super().__init__(title="Timeout Review Request")
        self.member_id = member_id
        self.add_item(discord.ui.InputText(label="Explain why this timeout is incorrect."))

    async def callback(self, interaction: discord.Interaction):
        log_channel = interaction.client.get_channel(Moderation.LOG_CHANNEL_ID)
        embed = discord.Embed(title="Review Request", description=f'Request by: {interaction.user.display_name} (ID: {self.member_id})')
        embed.add_field(name="Explanation", value=self.children[0].value, inline=False)
        await log_channel.send(embed=embed)
        await interaction.response.send_message("Your request has been forwarded to an admin.", ephemeral=True)

class AdminResponseButton(discord.ui.Button):
    def __init__(self, user_id):
        super().__init__(style=discord.ButtonStyle.primary, label="Respond", custom_id=f"admin_respond_{user_id}")
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        modal = AdminResponseModal(self.user_id)
        await interaction.response.send_modal(modal)

class AdminResponseModal(discord.ui.Modal):
    def __init__(self, user_id):
        super().__init__(title="Respond to Unban Request")
        self.user_id = user_id
        self.add_item(discord.ui.InputText(label="Response", placeholder="Type your response here...", min_length=1, max_length=2000))

    async def callback(self, interaction: discord.Interaction):
        response_text = self.children[0].value
        user = await interaction.client.fetch_user(self.user_id)
        embed = discord.Embed(title="Admin Response", description=response_text)
        await user.send(embed=embed)
        await interaction.response.send_message("Your response has been sent to the user.", ephemeral=True)



class Moderation(commands.Cog):
    LOG_CHANNEL_ID = REPLACE_WITH_ID
    RAPID_MESSAGE_THRESHOLD = 7
    RAPID_TIME_FRAME = 10
    REPEAT_MESSAGE_THRESHOLD = 5


    def __init__(self, bot):
        self.bot = bot
        self.message_timestamps = defaultdict(deque)
        self.message_contents = defaultdict(lambda: defaultdict(int))
        self.warnings = load_warnings()
        self.last_warned = defaultdict(lambda: datetime.min)
        self.LOG_CHANNEL_ID = REPLACE_WITH_ID

    async def log_unban_request(self, user):
        admin_channel = self.bot.get_channel(self.LOG_CHANNEL_ID)
        if not admin_channel:
            return

        embed = discord.Embed(title="Unban Request", description=f"Request from {user.display_name} (ID: {user.id})")
        view = View()
        view.add_item(AdminResponseButton(user.id))
        await admin_channel.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        await self.process_message(message)

    async def process_message(self, message):
        author_id = message.author.id
        content = message.content.strip().lower()
        current_time = datetime.utcnow()

        timestamps = self.message_timestamps[author_id]

        timestamps.append((current_time, message))

        while timestamps and (current_time - timestamps[0][0]).total_seconds() > self.RAPID_TIME_FRAME:
            timestamps.popleft()

        if len(timestamps) >= self.RAPID_MESSAGE_THRESHOLD:
            await self.handle_spam(message.author, "Rapid messaging detected (7 messages in 10 seconds).")
            timestamps.clear()

        message_counts = self.message_contents[author_id]
        message_counts[content] += 1

        if message_counts[content] >= self.REPEAT_MESSAGE_THRESHOLD:
            await self.handle_spam(message.author, f"Repeated message spamming detected: '{content}'")
            message_counts[content] = 0

    async def handle_spam(self, member, spam_content):
        member_id_str = str(member.id)
        current_time = datetime.utcnow()

        if member_id_str not in self.warnings:
            self.warnings[member_id_str] = {'count': 0, 'last_handled': current_time.isoformat()}
        if isinstance(self.warnings[member_id_str], int):
            self.warnings[member_id_str] = {'count': self.warnings[member_id_str],
                                            'last_handled': datetime.min.isoformat()}

        last_handled = datetime.fromisoformat(self.warnings[member_id_str]['last_handled'])
        if (current_time - last_handled).total_seconds() < 10:
            return

        self.warnings[member_id_str]['count'] += 1
        self.warnings[member_id_str]['last_handled'] = current_time.isoformat()
        save_warnings(self.warnings)

        total_warnings = self.warnings[member_id_str]['count']
        timeout_duration = timedelta(minutes=10)
        suspension_message = ""

        embed = discord.Embed(title="Warning Issued",
                              description=f"You have been warned for: {spam_content}\nTotal Warnings: {total_warnings}",
                              color=discord.Color.red())
        if total_warnings == 2:
            embed.add_field(name="Notice", value="If you get one more warn, you will be suspended for 3 days.")
        elif total_warnings >= 3:
            timeout_duration = timedelta(days=3)
            embed.add_field(name="Suspended",
                            value="You have been suspended for 3 days. You can request an unban if you believe this is a mistake.")
            view = UnbanRequestView(member.id)
            suspension_message = " and has been suspended for 3 days."
            self.warnings[member_id_str]['count'] = 0
            save_warnings(self.warnings)

        await member.edit(communication_disabled_until=datetime.utcnow() + timeout_duration)
        await member.send(embed=embed, view=(view if total_warnings >= 3 else None))

        log_channel = self.bot.get_channel(self.LOG_CHANNEL_ID)
        embed_log = discord.Embed(title="Spam Detection",
                                  description=f"{member.display_name} has been put in timeout for spamming.\n\n Reason: {spam_content}. \n\nTotal Warnings: {total_warnings}{suspension_message}",
                                  color=discord.Color.orange())
        await log_channel.send(embed=embed_log)

    async def button_callback(self, interaction):
        modal = ReviewModal(member_id=interaction.user.id)
        await interaction.response.send_modal(modal)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.type == discord.InteractionType.component and interaction.custom_id == "request_review":
            await self.button_callback(interaction)



    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.type == discord.InteractionType.component and interaction.custom_id == "request_review":
            await self.button_callback(interaction)

    @commands.slash_command(name="warnings", description="Display the number of warnings for a specified user.")
    @commands.has_permissions(ban_members=True)
    async def warnings(self, ctx, user: Option(discord.Member, "Select a user", required=True)):
        member_id_str = str(user.id)
        if member_id_str in self.warnings:
            warning_count = self.warnings[member_id_str].get('count', 0)
            last_handled = self.warnings[member_id_str].get('last_handled', 'N/A')
            embed = discord.Embed(title=f"Warnings for {user.display_name}",
                                  description=f"Total Warnings: **{warning_count}**\nLast Handled: **{last_handled}**",
                                  color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            await ctx.respond(f"{user.display_name} has no warnings.", ephemeral=True)


    @commands.slash_command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, reason: str = "Kein Grund angegeben"):
        await member.kick(reason=reason)
        log_channel = self.bot.get_channel(self.LOG_CHANNEL_ID)
        embed = discord.Embed(title="Kick", description=f'{ctx.author.display_name} has kicked {member.display_name} from the server.\n\n**Reason**: {reason}')
        await log_channel.send(embed=embed)
        await ctx.respond(f"{member.display_name} got kicked. Reason: {reason}", ephemeral=True)

    @commands.slash_command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason: str = "Kein Grund angegeben"):
        await member.ban(reason=reason)
        log_channel = self.bot.get_channel(self.LOG_CHANNEL_ID)
        embed = discord.Embed(title="Ban", description=f'{ctx.author.display_name} has banned {member.display_name} from the server.\n\n**Reason**: {reason}')
        await log_channel.send(embed=embed)
        await ctx.respond(f"{member.display_name} got banned. Reason: {reason}", ephemeral=True)

    @commands.slash_command()
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minutes: int, reason: str = "Kein Grund angegeben"):
        timeout_duration = timedelta(minutes=minutes)
        await member.edit(communication_disabled_until=discord.utils.utcnow() + timeout_duration, reason=reason)
        log_channel = self.bot.get_channel(self.LOG_CHANNEL_ID)
        embed = discord.Embed(title="Muted/Timeout", description=f'{ctx.author.display_name} has put {member.display_name} in timeout for {minutes} minutes.\n\n**Reason**: {reason}')
        await log_channel.send(embed=embed)
        await ctx.respond(f"{member.display_name} got muted for {minutes} minutes. Reason: {reason}", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        log_channel = self.bot.get_channel(self.LOG_CHANNEL_ID)
        embed = discord.Embed(title="Unban", description=f'{user.display_name} got unbanned.')
        await log_channel.send(embed=embed)



    @commands.slash_command(name="warn", description="Warn a user.")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, reason="No reason provided", remove: bool = False):
        if remove:
            if str(member.id) in self.warnings and self.warnings[str(member.id)] > 0:
                self.warnings[str(member.id)] -= 1
                save_warnings(self.warnings)
                await ctx.respond(f"Removed a warning from {member.display_name}. Total warnings now: {self.warnings[str(member.id)]}", ephemeral=True)
            else:
                await ctx.respond(f"{member.display_name} has no warnings to remove.", ephemeral=True)
            return

        if str(member.id) not in self.warnings:
            self.warnings[str(member.id)] = 0
        self.warnings[str(member.id)] += 1
        save_warnings(self.warnings)

        embed = discord.Embed(title="Warning", description=f"You have been warned.\n**Reason**: {reason}\n**Total Warnings**: {self.warnings[str(member.id)]}")
        if self.warnings[str(member.id)] == 2:
            embed.add_field(name="Warning", value="If you get one more warn, you will be suspended for 3 days.")
        await member.send(embed=embed)

        if self.warnings[str(member.id)] >= 3:
            await member.edit(communication_disabled_until=datetime.utcnow() + timedelta(days=3))
            await ctx.respond(f"{member.display_name} has been suspended for 3 days due to repeated infractions.", ephemeral=True)
            self.warnings[str(member.id)] = 0
            save_warnings(self.warnings)
        else:
            await ctx.respond(f"{member.display_name} has been warned for: {reason}. Total warnings: {self.warnings[str(member.id)]}", ephemeral=True)


    @commands.slash_command(name="clearr", description="Clears a specified number of messages from the channel.")
    @commands.has_permissions(manage_messages=True)
    async def clearr(self, ctx, amount: Option(int, "Enter the number of messages to delete", required=True, min_value=1, max_value=10000)):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.respond(f"Cleared {amount} messages.", ephemeral=True)

    @commands.slash_command(name="userclear", description="Clears a specified number of messages from the selected user.")
    @commands.has_permissions(manage_messages=True)
    async def userclear(self, ctx, user: discord.Member, amount: int = 5):
        if amount < 1:
            await ctx.respond("Amount must be at least 1.", ephemeral=True)
            return

        counter = 0
        async for message in ctx.channel.history(limit=200):
            if message.author == user:
                await message.delete()
                counter += 1
                if counter >= amount:
                    break

        await ctx.respond(f"Cleared {counter} messages from {user.display_name}.", ephemeral=True)



    @ban.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("You do not have permission to use this command.", ephemeral=True)
        else:
            await ctx.respond("An error occurred while executing the command.", ephemeral=True)

    @userclear.error
    async def userclear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("You do not have permission to use this command.", ephemeral=True)
        else:
            await ctx.respond(f"An error occurred: {error}", ephemeral=True)


    @kick.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("You do not have permission to use this command.", ephemeral=True)
        else:
            await ctx.respond("An error occurred while executing the command.", ephemeral=True)

    @warn.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("You do not have permission to use this command.", ephemeral=True)
        else:
            await ctx.respond("An error occurred while executing the command.", ephemeral=True)

    @mute.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("You do not have permission to use this command.", ephemeral=True)
        else:
            await ctx.respond("An error occurred while executing the command.", ephemeral=True)

    @commands.slash_command(name="userclear",
                            description="Clears a specified number of messages from the selected user.")
    @commands.has_permissions(manage_messages=True)
    async def userclear(self, ctx, user: discord.Member, amount: int = 5):
        if amount < 1:
            await ctx.respond("Amount must be at least 1.", ephemeral=True)
            return

        await ctx.defer(ephemeral=True)

        counter = 0
        try:
            async for message in ctx.channel.history(limit=200):
                if message.author == user:
                    await message.delete()
                    counter += 1
                    if counter >= amount:
                        break
        except Exception as e:
            await ctx.followup.send(f"An error occurred while deleting messages: {e}", ephemeral=True)
            return

        await ctx.followup.send(f"Cleared {counter} messages from {user.display_name}.", ephemeral=True)


def setup(bot):
    bot.add_cog(Moderation(bot))