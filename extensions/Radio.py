import discord
from discord.ext import commands, tasks
import json
import os
import time

class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_check.start()
        self.empty_channels = {}
        self.stay_connected = False

    # Load
    def load_radio_data(self):
        if not os.path.exists('radio_data.json'):
            with open('radio_data.json', 'w') as f:
                json.dump({}, f, indent=4)
        with open('radio_data.json', 'r') as f:
            return json.load(f)

    # Save
    def save_radio_data(self, data):
        with open('radio_data.json', 'w') as f:
            json.dump(data, f, indent=4)

    # Setup server data
    def initialize_server_data(self, server_id):
        radio_data = self.load_radio_data()
        if server_id not in radio_data:
            radio_data[server_id] = {"stations": {}, "last_user": None}
            self.save_radio_data(radio_data)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        server_id = str(guild.id)
        self.initialize_server_data(server_id)
        print(f"Initialized data for server: {server_id}")

    @commands.slash_command(name='radio', description='Select a radio from the list and play it automatically')
    async def select_radio(self, ctx):
        if not ctx.guild:
            return

        server_id = str(ctx.guild.id)
        self.initialize_server_data(server_id)
        radio_data = self.load_radio_data()
        stations = radio_data[server_id]['stations']

        if not stations:
            await ctx.respond("You haven't added any radios yet...")
            return

        if ctx.author.voice:
            voice_client = ctx.guild.voice_client
            if not voice_client:
                channel = ctx.author.voice.channel
                await channel.connect()
                voice_client = ctx.guild.voice_client
        else:
            await ctx.respond("Oops... You must be in a voice channel.")
            return

        options = [
            discord.SelectOption(label=station, description=f"Listen {station} ❱ Plays: {stations[station]['play_count']}")
            for station in stations
        ]
        select = discord.ui.Select(placeholder="Select a radio station", options=options)

        async def callback(interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("❗ Only the user who initiated the order can select the radio.", ephemeral=True)
                return

            selected_station_name = select.values[0]
            selected_station = stations[selected_station_name]
            station_url = selected_station['url']

            if voice_client.is_playing():
                voice_client.stop()

            try:
                voice_client.play(discord.FFmpegPCMAudio(station_url), after=lambda e: print(f'Finished playing: {e}'))
            except Exception as e:
                await ctx.respond(f"❗ An error occurred while playing: {e}")
                return

            voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
            voice_client.source.volume = 0.5

            stations[selected_station_name]['play_count'] += 1
            radio_data[server_id]['last_user'] = ctx.author.id
            self.save_radio_data(radio_data)

            await interaction.response.send_message(f"Now you listen {selected_station_name} ❱ Plays: {stations[selected_station_name]['play_count']}", ephemeral=True)
            await interaction.message.delete()

        select.callback = callback
        view = discord.ui.View()
        view.add_item(select)
        await ctx.respond("Select your favorite radio:", view=view)

    @commands.slash_command(name='addradio', description='Add a new radio station (admins only)')
    async def add_radio(self, ctx, name: str, url: str):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("🔒 You are not allowed to add radio stations.")
            return
        
        server_id = str(ctx.guild.id)
        self.initialize_server_data(server_id)
        radio_data = self.load_radio_data()
        stations = radio_data[server_id]['stations']

        if len(stations) >= 20:
            await ctx.respond("❗ You have reached the limit of 20 radio stations. You must delete a station before adding another.")
            return

        radio_data[server_id]['stations'][name] = {
            "url": url,
            "play_count": 0
        }
        self.save_radio_data(radio_data)

        await ctx.respond(f"Radio station '{name}' has been added successfully")

    # Remove a radio station
    @commands.slash_command(name='removeradio', description='Delete a radio station (admins only)')
    async def remove_radio(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("🔒 You are not allowed to delete radio stations.")
            return
        
        server_id = str(ctx.guild.id)
        self.initialize_server_data(server_id)
        radio_data = self.load_radio_data()
        stations = radio_data[server_id]['stations']

        if not stations:
            await ctx.respond("There are no radio stations to delete.")
            return

        options = [discord.SelectOption(label=station, description=f"Delete {station}") for station in stations]
        select = discord.ui.Select(placeholder="Select a radio station to delete", options=options)

        async def callback(interaction):
            selected_station_name = select.values[0]
            del radio_data[server_id]['stations'][selected_station_name]
            self.save_radio_data(radio_data)

            await interaction.response.send_message(f"Radio station '{selected_station_name}' has been deleted successfully", ephemeral=True)
            await interaction.message.delete()

        select.callback = callback
        view = discord.ui.View()
        view.add_item(select)
        await ctx.respond("Select the radio station you want to delete:", view=view)

    @commands.slash_command(name='playradio', description='Play a radio using a direct link')
    async def play_radio_link(self, ctx, url: str):
        if ctx.author.voice:
            voice_client = ctx.guild.voice_client
            if not voice_client:
                channel = ctx.author.voice.channel
                await channel.connect()
                voice_client = ctx.guild.voice_client
        else:
            await ctx.respond("You must be in a voice channel.")
            return
        
        if voice_client.is_playing():
            voice_client.stop()

        try:
            voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e: print(f'Finished playing: {e}'))
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
            voice_client.source.volume = 0.5
        except Exception as e:
            await ctx.respond(f"Error rendering: {e}")
            return

        await ctx.respond(f"Now playing from: {url}")

    @commands.slash_command(name='stop', description='Stops radio playback and disconnects the bot')
    async def stop(self, ctx):
        if not ctx.guild:
            await ctx.respond("This command can only be used in a server.")
            return

        voice_client = ctx.guild.voice_client
        server_id = str(ctx.guild.id)
        radio_data = self.load_radio_data()

        if radio_data[server_id].get('last_user') != ctx.author.id:
            await ctx.respond("Only the user who turned the radio on can turn it off.")
            return

        if ctx.author.voice:
            if voice_client:
                if voice_client.is_playing():
                    voice_client.stop()
                await voice_client.disconnect()
                await ctx.respond("Radio playback has been stopped and the bot has been disconnected.")
            else:
                await ctx.respond("Radio is not playing at this time.")
        else:
            await ctx.respond("You must be in a voice channel to stop playing the radio.")
    
    @commands.slash_command(name='24-7', description='Enable/disable 24/7 mode (bot will not log out)')
    async def stay_connected_24_7(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("🔒 Only administrators can use this command.")
            return
        
        self.stay_connected = not self.stay_connected
        status = "activated" if self.stay_connected else "disabled"
        await ctx.respond(f"24/7 mode was {status}. The bot will not disconnect from the voice channel." if self.stay_connected else "The bot will disconnect from the voice channel if there are no members.")

    @tasks.loop(seconds=10)
    async def voice_check(self):
        for guild in self.bot.guilds:
            voice_client = guild.voice_client
            if voice_client and len(voice_client.channel.members) == 1: 
                if guild.id not in self.empty_channels:
                    self.empty_channels[guild.id] = time.time()
                elif time.time() - self.empty_channels[guild.id] > 10:
                    await voice_client.disconnect()
                    self.empty_channels.pop(guild.id)
            else:
                if guild.id in self.empty_channels:
                    self.empty_channels.pop(guild.id)

    @voice_check.before_loop
    async def before_voice_check(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Radio(bot))
