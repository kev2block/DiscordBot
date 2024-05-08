from discord.ext import commands
import discord
from discord.ui import View, Button

class ShowAllRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.setup_persistent_views())

    async def setup_persistent_views(self):
        await self.bot.wait_until_ready()
        self.bot.add_view(RoleView(), message_id=None)

    @commands.command(name="role")
    @commands.has_permissions(administrator=True)
    async def role_command(self, ctx):
        embed = discord.Embed(title="Your Roles", description="Click on the button below to see your roles.", color=discord.Color.blue())
        view = RoleView()
        button = discord.ui.Button(label="Show Roles", style=discord.ButtonStyle.primary)

        await ctx.send(embed=embed, view=view)

    @role_command.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            print("No permissions to run this command.")


class RoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleButton())

class RoleButton(Button):
    def __init__(self):
        super().__init__(label="Show Roles", style=discord.ButtonStyle.primary, custom_id="show_roles_button")

    async def callback(self, interaction: discord.Interaction):
        roles = interaction.user.roles
        role_names = "\n".join(f"<@&{role.id}>" for role in interaction.user.roles if role.name != "@everyone")
        embed = discord.Embed(title="Your Roles:", description=role_names, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(ShowAllRoles(bot))



