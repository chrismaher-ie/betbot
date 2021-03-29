# bot.py
import os
import discord

from datetime import datetime
from dateutil.parser import parse
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

bot.sandwich_id = 326471661928972299

# When person connects to the voice channel
@bot.event
async def on_voice_state_update(member, before, after):
    
    if (not after.channel): # ignore users leaving a channel
        return
    if (before.channel): 
        if (after.channel.name == before.channel.name): # ignore users already in the channel
            return

    if (after.channel.name == 'General'):


        channel = discord.utils.get(member.guild.text_channels, name='bot-commands')

        await channel.send(f"{member.name} just joined #General, I'm watching you")

# Bot commands
@bot.command(name='new_round', help = 'Start new round of betting for his arrival time.')
async def new_round(ctx, proposed_time):

    
    proposed_time_parsed = parse(proposed_time)
    proposed_time_formatted = proposed_time_parsed.strftime("%H:%M:%S")

    round_start_time = datetime.now().strftime("%H:%M:%S")

    await ctx.send(
        f"""New Round.
        \nThe sandwich has stated his time of arrival to be {proposed_time_formatted}.
        \nCurrent time: {round_start_time}."""
    )

    vc = discord.utils.get(ctx.guild.voice_channels, name='General')
    members = '\n - '.join([member.name for member in vc.members])
    await ctx.send(f"Users in voice chat: \n {members}")


bot.run(TOKEN)
