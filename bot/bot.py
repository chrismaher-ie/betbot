# bot.py
import os
import discord

from datetime import datetime
from dateutil.parser import parse
from discord.ext import commands
from dotenv import load_dotenv
from game import Game

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

bot.sandwich_id = 326471661928972299

bot.games = {}

# When person connects to the voice channel
@bot.event
async def on_voice_state_update(member, before, after):
    
    if before.channel is None and after.channel is not None:
        if after.channel.name == 'General':
            
            if member.guild.id in bot.games:
                
                game = bot.games[member.guild.id]
                if member == game.member:
                    #player has arrived and game is over

                    #calculate time
                    
                    timedelta = (game.proposedtime - datetime.now()).total_seconds()

                    if timedelta > 0:
                        result_msg = f"{member.name} is early by {int(timedelta / 60)} minutes and {int(timedelta % 60)} seconds! Congrats!"
                    elif timedelta < 0:
                        timedelta *= -1
                        result_msg = f"{member.name} is late by {int(timedelta / 60)} minutes and {int(timedelta % 60)} seconds! Boo!"
                    elif timedelta == 0:
                        result_msg = f"{member.name} is exactly on time!"


                    #setup embed


                    embedVar = discord.Embed(title="Round Ended", description=f"Member {member.name} has arrived", color=0x00ff00)
                    embedVar.add_field(name="Promised time", value=game.proposedtime.strftime("%H:%M:%S"), inline=False)
                    embedVar.add_field(name="Current time", value=datetime.now().strftime("%H:%M:%S"), inline=False)
                    embedVar.add_field(name="Result", value=result_msg, inline=False)
                    



                    await game.command_channel.send(embed=embedVar)



# Bot commands
@bot.command(name='new_round', help = 'Start new round of betting for his arrival time.')
async def new_round(ctx, member: discord.Member, proposed_time):
    #TODO: except if member is already in vc

    proposed_time_parsed = parse(proposed_time)
    proposed_time_formatted = proposed_time_parsed.strftime("%H:%M:%S")


    round_start_time = datetime.now().strftime("%H:%M:%S")

    
    if ctx.guild.id in bot.games:
        await ctx.send("Sorry! A round is already in progress")
        return
    else: 
        bot.games[ctx.guild.id] = Game(member, datetime.now(), proposed_time_parsed, ctx.channel)

    
    
    embedVar = discord.Embed(title="New Round", description=f"Member {member.name} is being timed!", color=0x00ff00)
    embedVar.add_field(name="Promised time", value=proposed_time_formatted, inline=False)
    embedVar.add_field(name="Current time", value=round_start_time, inline=False)



    await ctx.send(embed=embedVar)


# TODO: restore as a check memebers command 
    # vc = discord.utils.get(ctx.guild.voice_channels, name='General')
    # members = '\n - '.join([member.name for member in vc.members])
    # await ctx.send(f"Users in voice chat: \n {members}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        arg = error.param.name
        await ctx.send(f"the previous command is missing parameter: {arg}")

bot.run(TOKEN)
