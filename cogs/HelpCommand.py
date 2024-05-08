from discord.ext import commands
import discord

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="help", description="Displays help information for all commands.")
    @commands.has_permissions(administrator=True)
    async def help_command(self, ctx):
        embed = discord.Embed(title="Commands", description="Shows every command the bot got.", color=discord.Color.blue())
        embed.add_field(name="Feedback", value="Type '!feedback' to send a message with the feedback menu.", inline=False)
        embed.add_field(name="Free Games on Epic", value="Sends the new free games on epic when they release. Type '!now' to see the current free games.", inline=False)
        embed.add_field(name="Moderation", value="You can see the moderation commands by typing '/'. Commands include: /kick, /ban, /mute, /warn.", inline=False)
        embed.add_field(name="Role Notifications", value="Type '!roles' to send the notifications menu.", inline=False)
        embed.add_field(name="Role assignment", value="Type '!RolePick' to send the Role assignment Buttons.", inline=False)
        embed.add_field(name="Show all roles", value="Type '!role' to send the button which shows your roles.", inline=False)
        embed.add_field(name="Steam game info", value="Type '/gameinfo [game]' to send information about a steam game.", inline=False)
        embed.add_field(name="Support Tickets", value="Type '!support' to send the support menu.", inline=False)
        embed.add_field(name="Music", value="Music Commands are /play {song/Youtube video}, /pause, /resume, /stop, /remove {0, 1, 2..}, /queue, /skip, /clear {stops music and clears the queue}", inline=False)
        embed.add_field(name="Giveaway", value="Type /Giveaway {time} {winners(amount)} {prize} to create a giveaway. /giveawayreroll {message_id} {winners} (rerolls new winner/s)", inline=False)
        embed.add_field(name="Chat AI", value="Type /chat and enter any message or question the bot should answer.", inline=False)

        await ctx.respond(embed=embed, ephemeral=True)

    @help_command.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("You do not have permission to use this command.", ephemeral=True)
        else:
            await ctx.respond("An error occurred while executing the command.", ephemeral=True)


def setup(bot):
    bot.add_cog(HelpCommand(bot))
