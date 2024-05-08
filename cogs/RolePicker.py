import discord
from discord.ext import commands
from discord.ui import Button, View

ROLE_MAPPINGS = {
    "🟢": "Green",
    "🔵": "Blue",
    "🔴": "Red",
    "🟣": "Purple",
    "🟡": "Yellow"
}

role_ids = {
    "Green": YOUR_ROLE_ID,
    "Blue": YOUR_ROLE_ID,
    "Red": YOUR_ROLE_ID,
    "Purple": YOUR_ROLE_ID,
    "Yellow": YOUR_ROLE_ID
}

class RolePicker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.setup_persistent_views())

    async def setup_persistent_views(self):
        await self.bot.wait_until_ready()
        self.bot.add_view(RolePickView())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def RolePick(self, ctx):
        embed = discord.Embed(
            title="Choose Your Color!",
            description="Click a button to select your role.",
            color=discord.Color.blue()
        )
        view = RolePickView()
        await ctx.send(embed=embed, view=view)

    @RolePick.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            print("No permissions to run this command.")


class RoleButton(Button):
    def __init__(self, label, role_name, role_id):
        super().__init__(label=label, style=discord.ButtonStyle.gray, custom_id=f"role_{role_name.lower()}")
        self.role_name = role_name
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        user_roles = interaction.user.roles
        current_color_roles = [interaction.guild.get_role(role_ids[name]) for name in ROLE_MAPPINGS.values()]
        if role in user_roles:
            await interaction.user.remove_roles(role)
            response_message = f"Removed role: {self.role_name}"
        else:
            roles_to_remove = [r for r in current_color_roles if r in user_roles]
            await interaction.user.remove_roles(*roles_to_remove, reason="Ensuring unique color role")
            await interaction.user.add_roles(role, reason="Adding new color role")
            response_message = f"Added role: {self.role_name}"
        await interaction.response.send_message(response_message, ephemeral=True)

class RolePickView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for emoji, role_name in ROLE_MAPPINGS.items():
            self.add_item(RoleButton(emoji, role_name, role_ids[role_name]))

def setup(bot):
    bot.add_cog(RolePicker(bot))
