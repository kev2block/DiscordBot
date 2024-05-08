import discord
from discord.ext import commands
from discord.ui import Button, View


class Notifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.setup_persistent_views())

    async def setup_persistent_views(self):
        await self.bot.wait_until_ready()
        self.bot.add_view(SettingsView())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def roles(self, ctx):
        role1 = ctx.guild.get_role(PUT_ROLE_HERE)
        role2 = ctx.guild.get_role(PUT_ROLE_HERE)
        role3 = ctx.guild.get_role(PUT_ROLE_HERE)
        embed = discord.Embed(title="Youtube and Game Update Pings",
                              description='Here, you can enable or disable ping notifications for new YouTube videos or game updates. Simply click on the :bell: button below this message!',
                              colour=discord.Colour.blurple(), color=0x00ff00)
        embed.add_field(name="",
                        value=f"> {role1.mention} -> General News\n"
                              f"> {role2.mention} -> Game Updates\n"
                              f"> {role3.mention} -> Social Media Posts",
                        inline=False)

        await ctx.send(embed=embed, view=SettingsView())

    @roles.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            print("No permissions to run this command.")



class SettingsView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SettingsButton(custom_id="settings_button"))



class SettingsButton(Button):
    def __init__(self, custom_id):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="🔔Settings",
            custom_id=custom_id
        )

    async def callback(self, interaction: discord.Interaction):
        role_id_generalnews = 'SAME_ROLE_AS_ROLE1'
        role_id_gameupdates = 'SAME_ROLE_AS_ROLE2'
        role_id_socialmedia = 'SAME_ROLE_AS_ROLE3'

        youtube_button = RoleButton(role_id_generalnews, "General News", discord.ButtonStyle.red, custom_id="youtube_button")
        twitch_button = RoleButton(role_id_gameupdates, "Game Updates", discord.ButtonStyle.red, custom_id="twitch_button")
        update_button = RoleButton(role_id_socialmedia, "Social Media", discord.ButtonStyle.red, custom_id="update_button")

        if any(role.id == int(role_id_generalnews) for role in interaction.user.roles):
            youtube_button.style = discord.ButtonStyle.green
        if any(role.id == int(role_id_gameupdates) for role in interaction.user.roles):
            twitch_button.style = discord.ButtonStyle.green
        if any(role.id == int(role_id_socialmedia) for role in interaction.user.roles):
            update_button.style = discord.ButtonStyle.green

        view = View()
        view.add_item(youtube_button)
        view.add_item(twitch_button)
        view.add_item(update_button)

        embed = discord.Embed(title="",
                              description='Click on the respective button below this message to enable or disable notifications.',
                              colour=discord.Colour.blurple(), color=0x00ff00)
        embed.add_field(name="",
                        value="> :red_square: -> Notifications are disabled\n"
                              "> :green_square: -> Notifications are enabled",
                        inline=False)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class RoleButton(Button):
    def __init__(self, role_id, label, style, custom_id):
        super().__init__(
            style=style,
            label=label,
            custom_id=custom_id
        )
        self.role_id = role_id


    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(int(self.role_id))
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            self.style = discord.ButtonStyle.red
        else:
            await interaction.user.add_roles(role)
            self.style = discord.ButtonStyle.green

        await interaction.response.edit_message(view=self.view)

def setup(bot):
    bot.add_cog(Notifications(bot))