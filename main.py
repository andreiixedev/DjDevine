import discord #<-- Discord Stuff
from discord.ext import commands #<-- Discord Commands
import asyncio

# |DISCORD INTENTS|
intents = discord.Intents.default()
intents.message_content = True #<-- Send messages
bot = commands.Bot(command_prefix='!', intents=intents)

#|COGS|
initial_extensions = ['extensions.Radio', 'extensions.Debug', 'extensions.RichPresence', 'extensions.Help'] 

if __name__ == "__main__":
    for extension in initial_extensions:
        bot.load_extension(extensions)

@bot.event
async def on_ready():
    print(f'Loaded {bot.user.name}')

bot.run('TOKEN_DISCORD')