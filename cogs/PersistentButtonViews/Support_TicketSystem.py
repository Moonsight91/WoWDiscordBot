import discord
from discord.ext import commands
from discord import ui


class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets = {}  # Dictionary to keep track of users who have created tickets

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} has connected to Discord!")

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if isinstance(interaction, discord.Interaction) and interaction.type == discord.InteractionType.component:
            if interaction.data["custom_id"] == "createticket":
                await self.create_ticket(interaction)

    async def create_ticket(self, interaction):
        user_id = interaction.user.id
        if user_id in self.tickets:
            await interaction.response.send_message("You've already created a ticket.", ephemeral=True)
            return

        guild = self.bot.get_guild(interaction.guild_id)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel_name = f"ticket-{interaction.user.name}"  # Using user's name for the channel name
        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

        # Add user to the tickets dictionary to track the created ticket
        self.tickets[user_id] = channel.id

        # Send a message to the user with an invite to the new channel
        embed_user = discord.Embed(
            title="Ticket Created",
            description=f"Your ticket has been created in {channel.mention}. Support will be with you shortly.",
            color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed_user, ephemeral=True)

        # Send an embed message to the ticket channel
        embed_channel = discord.Embed(
            title="New Ticket",
            description=f"Welcome to your support ticket channel, {interaction.user.mention}. Support will be with you shortly.",
            color=discord.Color.blurple())
        await channel.send(embed=embed_channel)

    @commands.command()
    async def support(self, ctx):
        embed = discord.Embed(
            title="Contact Support",
            description="Click the button below to create a support ticket.",
            color=discord.Color.blurple())
        embed.set_image(url="https://www.linearity.io/blog/content/images/2023/06/60a591db17d4bbc1d2065eb2_Untitled--1-.png")
        view = SupportView()
        await ctx.send(embed=embed, view=view)


class SupportView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Set timeout to None to make the view persistent

    @ui.button(label="Create Ticket", style=discord.ButtonStyle.blurple, custom_id="createticket")
    async def create_ticket_button(self, button: ui.Button, interaction: discord.Interaction):
        pass


async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
