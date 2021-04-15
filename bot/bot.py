# bot.py
import os
import discord
import numpy as np

from game import Round, Player

from datetime import datetime
from dateutil.parser import parse
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='-', intents=intents)

# bot.sandwich_id = 326471661928972299

bot.rounds = {}


# When person connects to the voice channel
@bot.event
async def on_voice_state_update(member, before, after):
    #TODO: logic below is not robust and only suitable for testing, fix to handle more cases
    if before.channel is None and after.channel is not None:
        
        if after.channel.guild.id in bot.rounds: #check if this guild is running a round
            round = bot.rounds[member.guild.id]
            
            if after.channel.name == 'General': #change vaule to a variable attibute of round if after.channel.name == round.voice_channel:
            
                if member.id == round.member: #player has arrived and round is over
                    
                    #TODO: change to round member function                    
                    result_embed = round.end_round()
                    await round.command_channel.send(embed=result_embed)

                    del bot.rounds[member.guild.id]

# Bot commands
@bot.command(name='new_round', help = 'Start new round of betting for the member\'s arrival time.')
async def new_round(ctx, member: discord.Member, proposed_time):
    #TODO: except if member is already in vc

    proposed_time = np.datetime64(parse(proposed_time))
    proposed_time_str = proposed_time.item().strftime("%H:%M:%S")
    
    start_time = np.datetime64(datetime.now())
    start_time_str = start_time.item().strftime("%H:%M:%S")
    
    if ctx.guild.id in bot.rounds:
        await ctx.send(embed=discord.Embed(Title="Error", description="Sorry! A round is already in progress.", color=0xff0000))
        return
    print("making new round")
    bot.rounds[ctx.guild.id] = Round(member.id, start_time, proposed_time, ctx.channel)
    print("made new round")
    embedVar = discord.Embed(title="New Round", description=f"Member {member.name} is being timed!", color=0x0000ff)
    embedVar.add_field(name="Promised time", value=proposed_time_str, inline=False)
    embedVar.add_field(name="Current time", value=start_time_str, inline=False)

    await ctx.send(embed=embedVar)
    return


@bot.command(name='cancel_round', help = 'Cancel current round of betting.')
async def cancel_round(ctx):
    if ctx.guild.id in bot.rounds:
        bot.rounds[ctx.guild.id].cancel_round()
        del bot.rounds[ctx.guild.id]
        await ctx.send(embed=discord.Embed(Title="Cancelled!", description="The current round has been cancelled.",inline=False, color=0x0000ff))
    else:
        await ctx.send(embed=discord.Embed(Title="Error", description="Sorry! There is no round in progress to cancel.", color=0xff0000))

@bot.command(name='finish_round', help = 'Manually end current round of betting.')
async def finish_round(ctx):
    if ctx.guild.id in bot.rounds:
        
        
        result_embed = bot.rounds[ctx.guild.id].end_round()

        await ctx.send(embed=result_embed)

        del bot.rounds[ctx.guild.id]

@bot.command(name='bet', help = 'Place a bet in the current round')
async def bet(ctx, time, stake=10):
    stake = float(stake)

    
    time = np.datetime64(parse(time))
    time_str = time.item().strftime("%H:%M:%S")

    # There is no round -> no bet can be made
    if ctx.guild.id not in bot.rounds:

        await ctx.send(embed=discord.Embed(Title="Error", description="Sorry! There is no round in progress to bet on.", color=0xff0000))
        return

    # Player has already bet -> not bet can be made TODO: edit bet functionality 
    if any(bet.player_.discord_id == ctx.message.author.id for bet in bot.rounds[ctx.guild.id]):
        await ctx.send(embed=discord.Embed(Title="Error", description="Sorry! There is no round in progress to bet on.", color=0xff0000))

    # There is a round & player has not yet bet -> place bet

    bot.rounds[ctx.guild.id].add_bet(ctx.message.author.id,time,stake)
    await ctx.send(embed=discord.Embed(Title="BET!", description=f"{ctx.message.author.name} has predicted {time_str} betting {stake} coins" ,inline=True, color=0x0000ff))

@bot.command(name='list_bets', help = 'Check the bets in the current round')
async def list_bets(ctx):

    if ctx.guild.id not in bot.rounds:

        await ctx.send(embed=discord.Embed(Title="Error", description="Sorry! There is no round in progress to check.", color=0xff0000))
        return

    round = bot.rounds[ctx.guild.id]

    embedVar = discord.Embed(title="Bets", description=f"The Following users have placed a bet", color=0x0000ff)
    for bet in round.bets:
        time = bet.time_bet.strftime("%H:%M:%S")
        embedVar.add_field(name=bet.player_.player_name, value=f"{bet.stake} coins on {time}", inline=False)

    await ctx.send(embed=embedVar)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        arg = error.param.name
        await ctx.send(f"The previous command is missing parameter:\n -> {arg} <-")

bot.run(TOKEN)
