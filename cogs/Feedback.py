import discord
from discord.ext import commands

feedback_channel_id=YOUR_CHANNEL_ID

class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.setup_persistent_views())

    async def setup_persistent_views(self):
        await self.bot.wait_until_ready()
        self.bot.add_view(MyView())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def feedback(self, ctx: commands.Context):
        view = MyView()
        embed = discord.Embed(title="Feedback", description="Click the button below to open the feedback menu.")
        await ctx.send(embed=embed, view=view)

    @feedback.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            print("No permissions to run this command.")



class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Feedback", style=discord.ButtonStyle.primary, custom_id="persistent_feedback_button")
    async def button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        modal = MyModal(title="Modal Triggered from Button")
        await interaction.response.send_modal(modal)

class MyModal(discord.ui.Modal):
    def __init__(self, title):
        super().__init__(title=title)
        self.add_item(discord.ui.InputText(label="Title", placeholder="Give your feedback a title"))
        self.add_item(discord.ui.InputText(label="Discord Username", placeholder="Enter your Discord username"))
        self.add_item(discord.ui.InputText(label="Message", placeholder="Type your message", style=discord.InputTextStyle.paragraph))

    async def callback(self, interaction: discord.Interaction):
        feedback_channel = interaction.guild.get_channel(feedback_channel_id)
        if feedback_channel:
            embed = discord.Embed(
                title="Feedback",
                color=discord.Color.random(),
                description=f"**Title:** {self.children[0].value}\n"
                            f"**Username:** {self.children[1].value}\n"
                            f"**Message:** {self.children[2].value}"
            )
            await feedback_channel.send(f"{interaction.user.mention} has submitted feedback.", embed=embed)
            await interaction.response.send_message("Feedback submitted successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("Feedback channel not found. Please contact an administrator.", ephemeral=True)

def setup(bot):
    bot.add_cog(Feedback(bot))
