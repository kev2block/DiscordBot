import discord
from discord.ext import commands



class SupportTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.setup_persistent_views())

    async def setup_persistent_views(self):
        await self.bot.wait_until_ready()
        self.bot.add_view(SupportView())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def support(self, ctx: commands.Context):
        view = SupportView()
        embed = discord.Embed(
            title="Questions and reports",
            description="Feel free to open tickets here for any private inquiries to the team or to report users!",
            colour=discord.Colour.green()
        )
        embed.add_field(
            name="Report user",
            value="> -Please provide the username and the [user id](<https://imgur.com/a/G9VPekI>) of the target.\n"
                  "> -Please provide evidence in the form of images or videos (unlisted youtube video).",
            inline=False
        )
        embed.add_field(
            name="Attention",
            value="> Abuse of the ticket system will result in exclusion! Please select an appropriate theme for your concern from the menu below to receive assistance.",
            inline=False
        )
        embed.add_field(
            name="",
            value="Ready? Then select a topic from the menu below to open a new ticket!",
            inline=False
        )
        await ctx.send(embed=embed, view=view)


    @support.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            print("No permissions to run this command.")




class SupportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Select(
            placeholder="Choose an option...",
            options=[
                discord.SelectOption(label="Reset Options", description="Reset your selections", emoji='🔄'),
                discord.SelectOption(label="Application", description="Apply for a moderator position", emoji='🛡️'),
                discord.SelectOption(label="Report User", description="Report a user for misconduct", emoji='🔨'),
                discord.SelectOption(label="Miscellaneous", description="Other inquiries", emoji='❔'),
            ],
            custom_id="support_select"
        ))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        select = interaction.data.get('values', [None])[0]
        if select == "Reset Options":
            await interaction.response.send_message("Options have been reset.", ephemeral=True)
        elif select == "Application":
            await interaction.response.send_message("The applications are currently closed.", ephemeral=True)
            #modal = ApplicationModal()
            #await interaction.response.send_modal(modal)
        elif select == "Report User":
            modal = ReportUserModal()
            await interaction.response.send_modal(modal)
        elif select == "Miscellaneous":
            modal = MiscellaneousModal()
            await interaction.response.send_modal(modal)
        return True


class ApplicationModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Application")
        self.add_item(discord.ui.InputText(label="Full Name"))
        self.add_item(discord.ui.InputText(label="Why do you want to be a moderator?"))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Thank you for your application!", ephemeral=True)

class ReportUserModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Report User")
        self.add_item(discord.ui.InputText(label="Username", placeholder="Enter the username of the user"))
        self.add_item(discord.ui.InputText(label="User ID", placeholder="Right-click on the user's name and copy the id"))
        self.add_item(discord.ui.InputText(label="Evidence", placeholder="In form of a image or video"))
        self.add_item(discord.ui.InputText(label="Reason", placeholder="Enter the reason for reporting", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        feedback_channel = interaction.guild.get_channel(report_channel_id)
        if feedback_channel:
            embed = discord.Embed(
                title="Report user",
                color=discord.Color.random(),
                description=f"**Username:** {self.children[0].value}\n**User id:** {self.children[1].value}\n**Evidence:** {self.children[2].value}\n**Message:** {self.children[3].value}"
            )
            await feedback_channel.send(f'{interaction.user.mention} created a report.', embed=embed)
            await interaction.response.send_message(content="Report created successfully!", ephemeral=True)
        else:
            await interaction.response.send_message(content="Error 3, Please contact a Admin or Moderator.", ephemeral=True)

report_channel_id = YOUR_CHANNEL_ID
support_channel_id = YOUR_CHANNEL_ID
moderator_role_id = YOUR_ROLE_ID

class TicketView(discord.ui.View):
    def __init__(self, user, thread):
        super().__init__(timeout=None)
        self.user = user
        self.thread = thread

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.user or interaction.user.get_role(moderator_role_id):
            await self.thread.delete()
            await interaction.response.send_message(f"Ticket {self.thread.name} has been closed.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to close this ticket.", ephemeral=True)

    @discord.ui.button(label="Ping Moderator", style=discord.ButtonStyle.primary, custom_id="ping_moderator")
    async def ping_moderator(self, button: discord.ui.Button, interaction: discord.Interaction):
        view=MiscellaneousModal
        moderator_role = interaction.guild.get_role(moderator_role_id)
        if moderator_role:
            await self.thread.send(f"{moderator_role.mention}, attention is required here!")
            button.disabled = True
            button.label = "Moderator pinged"
            await interaction.message.edit(view=self)
            await interaction.response.send_message("Moderator has been pinged.", ephemeral=True)
        else:
            await interaction.response.send_message("Moderator role not found.", ephemeral=True)


class MiscellaneousModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Miscellaneous Message")
        self.add_item(discord.ui.InputText(label="Message", placeholder="The ticket begins with this message",
                                           style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        support_channel = interaction.guild.get_channel(support_channel_id)
        if support_channel:
            thread = await support_channel.create_thread(name=f"Support Ticket: {interaction.user.display_name}",
                                                         auto_archive_duration=1440)
            if thread:
                report_channel = interaction.guild.get_channel(report_channel_id)
                if report_channel:
                    await report_channel.send(f"{interaction.user.mention} created a ticket: {thread.mention}")

                embed = discord.Embed(
                    title='New Ticket Created',
                    description=f'{self.children[0].value}',
                    color=discord.Color.blue()
                )

                ticket_view = TicketView(user=interaction.user, thread=thread)

                await thread.send(content=f"{interaction.user.mention} has initiated this ticket.", embed=embed,
                                  view=ticket_view)

                await thread.send(content="**Ping a moderator only in urgent matters**")

                await interaction.response.send_message(content=f"Your ticket has been successfully created! {thread.mention}",
                                                        ephemeral=True)
            else:
                await interaction.response.send_message(content="Failed to create a support thread.", ephemeral=True)
        else:
            await interaction.response.send_message(content="Support channel not found.", ephemeral=True)


@commands.Cog.listener()
async def on_ready(self):
    self.bot.add_view(TicketView(user=None, thread=None))

def setup(bot):
    bot.add_cog(SupportTicket(bot))
