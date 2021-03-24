# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# def get_guild():
#     return discord.utils.get(client.guilds, name = GUILD)


@client.event
async def on_ready():

    print(f'{client.user} is connected to the following guilds:\n')
    for guild in client.guilds:
        f'{guild.name}(id: {guild.id})\n'
    
        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members} \n\n')


@client.event
async def on_voice_state_update(member, before, after):


    if (after.channel.name == 'General'):

        channel = discord.utils.get(member.guild.text_channels, name='general')

        await channel.send(f"{member.name} just joined #General, I'm watching you")


@client.event
async def on_message(message):

    
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('#test'):
        await message.channel.send(f'I heard you! {message.author.name}')
        vc = discord.utils.get(message.guild.voice_channels, name='General')
        members = '\n - '.join([member.name for member in vc.members])
        await message.channel.send(f"users in: \n {members}")


client.run(TOKEN)
