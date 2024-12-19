import discord
from discord.ext import commands
import psutil
import asyncio
import platform
import json
import datetime

class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    async def cog_check(self, ctx):
        return ctx.author.id == 888817795490521128  # Only show commands hoster bot (btw it's my user id)

    @commands.slash_command(name='debug', description='Afișează informații detaliate despre bot')
    async def debug(self, ctx):
        # Setup network stats
        initial_net_io = psutil.net_io_counters()
        
        # Create the embed message
        embed = discord.Embed(title="🔧 Debug Information", color=0x3498db)

        # Get server information
        server = ctx.guild
        radio_data = self.load_radio_data()
        server_id = str(server.id)
        stations = radio_data.get(server_id, {}).get('stations', {})
        embed.add_field(name="Server", value=f"{server.name}", inline=False)
        embed.add_field(name="Radio-uri Salvate", value=f"{len(stations)}", inline=False)

        if stations:
            station_list = "\n".join([f"🎵 {station}" for station in stations.keys()])
            embed.add_field(name="Stații Radio", value=station_list, inline=False)

        # Server icon as the thumbnail
        if server.icon:
            embed.set_thumbnail(url=server.icon.url)

        # Banner server if available
        if server.banner:
            embed.set_image(url=server.banner.url)  # Set the banner at the bottom of the embed

        # Send/Respond embed message
        message = await ctx.respond(embed=embed)

        start_time = asyncio.get_event_loop().time()
        duration = 30  # check for 30 seconds

        while True:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time >= duration:
                break  # Stop after 30 seconds

            # System information
            cpu_usage = psutil.cpu_percent()
            ram_usage = psutil.virtual_memory().percent
            cpu_name = platform.processor()  #CPU name (on vps probably not work)
            extensions = list(self.bot.extensions.keys())
            uptime = datetime.datetime.utcnow() - self.start_time

            # Network stats
            current_net_io = psutil.net_io_counters()
            bytes_sent = current_net_io.bytes_sent - initial_net_io.bytes_sent
            bytes_recv = current_net_io.bytes_recv - initial_net_io.bytes_recv

            # Bytes ---> MB
            sent_mb = bytes_sent / (1024 * 1024)
            recv_mb = bytes_recv / (1024 * 1024)

            # System details
            embed.description = (
                f"☢️ **CPU:"
                f"**CPU Usage:** {cpu_usage}%\n"
                f"**RAM Usage:** {ram_usage}%\n"
                f"🛠️ **Loaded Extensions:** {', '.join(extensions)}\n"
                f"📶 **Internet usage:**\n"
                f"  - Sent: {sent_mb:.2f} MB\n"
                f" - Received: {recv_mb:.2f} MB\n"
                f"⚙️ **Operating System: ** {platform.system()} {platform.release()}\n"
                f"🐍 **Python:** {platform.python_version()}\n"
                f"📚 **Discord.py:** {discord.__version__}\n"
                f"⏳ **Uptime:** {str(uptime).split('.')[0]}\n"
            )

            try:
                await message.edit(embed=embed)
            except discord.HTTPException as e:
                print(f"Failed to edit message: {e}")

            await asyncio.sleep(5)  # Update every 5 seconds

        embed.description += "\n**Check completed :D**"
        await message.edit(embed=embed)

    @commands.slash_command(name='updates', description='See the latest bot updates.') #Commands for show updates
    async def updates(self, ctx):
        updates_text = (
            "**Version 1.0.2**\n"
            "- Removing errors and fixing bugs\n"
            "\n"
        )

        embed = discord.Embed(
            title='₊˚ʚ『🆕』┋Actualizări Recente',
            description=updates_text,
            color=0x3498db,  # Custom bar embeded
        )

        embed.add_field(name="Update Date", value="18 nov 2024", inline=False)
        embed.add_field(name="Maintainer", value="<@888817795490521128>", inline=False)
        embed.set_image(url="https://i.giphy.com/mJIa7rg9VPEhzU1dyQ.webp") #Anime image UwU

        await ctx.respond(embed=embed)

    @commands.slash_command(name='shutdown', description='Bot shutdown by a Maintainer.')
    async def shutdown(self, ctx):
        if ctx.author.id == 888817795490521128: #Admin hoster ID Discord
            await ctx.respond("Shutdown...")
            await self.bot.close()
        else:
            await ctx.respond("You do not have permission to use this command.")

    def load_radio_data(self):
        # Check in database radio based of server id guild
        try:
            with open('radio_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {} 
        except json.JSONDecodeError:
            return {} 

def setup(bot):
    bot.add_cog(Debug(bot))
