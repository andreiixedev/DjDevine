import discord
from discord.ext import commands
import json
import os

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Load radio data
    def load_radio_data(self):
        if not os.path.exists('radio_data.json'):
            with open('radio_data.json', 'w') as f:
                json.dump({}, f, indent=4)
        with open('radio_data.json', 'r') as f:
            return json.load(f)

    # Help command for radio commands
    @commands.slash_command(name='help', description='Shows the controls for the radio station')
    async def show_help(self, ctx):
        embed = discord.Embed(
            title="Ajutor",
            description="Here is a list of commands for managing and playing radio stations.",
            color=discord.Color.blue()
        )

        embed.set_thumbnail(url="https://i.pinimg.com/originals/7f/16/0d/7f160dcfef77ff1b4b062f2083b5f1f1.gif")  # Replace with your bot logo URL
        
        embed.add_field(
            name="/radio", 
            value="Select a radio from the available list and start autoplay. 🎵", 
            inline=False
        )
        embed.add_field(
            name="/addradio [nume] [url]", 
            value="Add a new radio station (administrators only). 🔒\n", 
            inline=False
        )
        embed.add_field(
            name="/removeradio", 
            value="Delete an existing radio station (administrators only). 🔒\n", 
            inline=False
        )
        embed.add_field(
            name="/playradio [url]", 
            value="Play a radio using a direct link. 🎧\n", 
            inline=False
        )
        embed.add_field(
            name="/stop", 
            value="Stop playing the radio. ⏹️\n", 
            inline=False
        )
        embed.add_field(
            name="/24-7", 
            value="Enable or disable 24/7 mode for continuous playback. 🕒\n", 
            inline=False
        )
        embed.add_field(
            name="/stations", 
            value="Shows the radio stations available on this server. 📻\n", 
            inline=False
        )

        embed.set_footer(text="Commands are only available in servers where radio stations are added.")
        await ctx.respond(embed=embed)

    # Command to list available radio stations for the server
    @commands.slash_command(name='stations', description='Shows the radio stations available on this server')
    async def list_stations(self, ctx):
        server_id = str(ctx.guild.id)

        # Load radio data
        radio_data = self.load_radio_data()

        # Check if the server has any stations
        if server_id in radio_data and radio_data[server_id]['stations']:
            stations = radio_data[server_id]['stations']
            embed = discord.Embed(
                title="Available Radio Stations",
                description=f"Radio stations added in this server:",
                color=discord.Color.green()
            )
            
            # Add each station to the embed
            for station_name, station_info in stations.items():
                embed.add_field(
                    name=station_name,
                    value=f" URL: {station_info['url']} | Plays: {station_info['play_count']}",
                    inline=False
                )

            await ctx.respond(embed=embed)
        else:
            await ctx.respond("There are no radio stations added on this server.")

def setup(bot):
    bot.add_cog(Help(bot))
