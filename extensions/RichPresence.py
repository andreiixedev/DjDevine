import discord
from discord.ext import commands, tasks
import time

class RichPresenceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_activity_time = time.time()
        self.presence_started = False 
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.presence_started:
            self.update_presence.start()
            self.presence_started = True 

    @tasks.loop(seconds=10)
    async def update_presence(self):
        try:
            current_time = time.time()
            voice_channel = None

            for guild in self.bot.guilds:
                if guild.voice_client and guild.voice_client.is_connected():
                    voice_channel = guild.voice_client.channel
                    break

            if voice_channel and len(voice_channel.members) > 1: 
                listeners_count = len(voice_channel.members) - 1
                activity = discord.Activity(
                    type=discord.ActivityType.listening,
                    name=f"︱{listeners_count}︱listen〢/help"
                )
                status = discord.Status.online
            else:
                activity = discord.Activity(
                    type=discord.ActivityType.playing,
                    name="/help"
                )
                status = discord.Status.idle 

            await self.bot.change_presence(activity=activity, status=status)

        except Exception as e:
            print(f"Error updating presence: {e}")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.last_activity_time = time.time()

    def cog_unload(self):
        self.update_presence.cancel()

def setup(bot):
    bot.add_cog(RichPresenceCog(bot))
