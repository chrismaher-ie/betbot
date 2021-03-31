# bot.py
import os
import discord

from game import Round, Player

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

bot.games = {}

#TODO: move to game.py
def get_round_end_embed(game):
                    
    #calculate time
    timedelta = (game.proposed_time - datetime.now()).total_seconds()
    if timedelta > 0:
        result_msg = f"{game.member.name} is early by {int(timedelta / 60)} minutes and {int(timedelta % 60)} seconds! Congrats!"
    elif timedelta < 0:
        timedelta *= -1
        result_msg = f"{game.member.name} is late by {int(timedelta / 60)} minutes and {int(timedelta % 60)} seconds! Boo!"
    elif timedelta == 0:
        result_msg = f"{game.member.name} is exactly on time!"
    
    #setup embed to display results
    embedVar = discord.Embed(title="Round Ended", description=f"Member {game.member.name} has arrived", color=0x00ff00)
    embedVar.add_field(name="Promised time", value=game.proposed_time.strftime("%H:%M:%S"), inline=False)
    embedVar.add_field(name="Current time", value=datetime.now().strftime("%H:%M:%S"), inline=False)
    embedVar.add_field(name="Result", value=result_msg, inline=False)

    return embedVar


# When person connects to the voice channel
@bot.event
async def on_voice_state_update(member, before, after):
    #TODO: logic below is not robust and only suitable for testing, fix to handle more cases
    if before.channel is None and after.channel is not None:
        
        if after.channel.guild.id in bot.games: #check if this guild is running a game
            game = bot.games[member.guild.id]
            
            if after.channel.name == 'General': #change vaule to a variable attibute of Game if after.channel.name == game.voice_channel:
            
                if member == game.member: #player has arrived and game is over
                    
                    #TODO: change to game member function                    
                    embedVar = get_round_end_embed( game )
                    await game.command_channel.send(embed=embedVar)

                    del bot.games[member.guild.id]

# Bot commands
@bot.command(name='new_round', help = 'Start new round of betting for the member\'s arrival time.')
async def new_round(ctx, member: discord.Member, proposed_time):
    #TODO: except if member is already in vc

    proposed_time_parsed = parse(proposed_time)
    proposed_time_formatted = proposed_time_parsed.strftime("%H:%M:%S")
    round_start_time = datetime.now().strftime("%H:%M:%S")
    
    if ctx.guild.id in bot.games:
        await ctx.send(embed=discord.Embed(Title="Error", description="Sorry! A round is already in progress.", color=0xff0000))
    else: 

        bot.games[ctx.guild.id] = Round(member, datetime.now(), proposed_time_parsed, ctx.channel)

        embedVar = discord.Embed(title="New Round", description=f"Member {member.name} is being timed!", color=0x0000ff)
        embedVar.add_field(name="Promised time", value=proposed_time_formatted, inline=False)
        embedVar.add_field(name="Current time", value=round_start_time, inline=False)

        await ctx.send(embed=embedVar)


@bot.command(name='cancel_round', help = 'Cancel current round of betting.')
async def cancel_round(ctx):
    if ctx.guild.id in bot.games:
        del bot.games[ctx.guild.id]
        await ctx.send(embed=discord.Embed(Title="Cancelled!", description="The current round has been cancelled.",inline=False, color=0x0000ff))
    else:
        await ctx.send(embed=discord.Embed(Title="Error", description="Sorry! There is no round in progress to cancel.", color=0xff0000))

@bot.command(name='finish_round', help = 'Manually end current round of betting.')
async def finish_round(ctx):
    if ctx.guild.id in bot.games:
        embedVar = get_round_end_embed( bot.games[ctx.guild.id] )

        await ctx.send(embed=embedVar)

        del bot.games[ctx.guild.id]

@bot.command(name='bet', help = 'Place a bet in the current round')
async def bet(ctx, time, stake=10):
    stake = float(stake)
    time = parse(time)
    time_str = time.strftime("%H:%M:%S")
    if ctx.guild.id in bot.games:
        await ctx.send(embed=discord.Embed(Title="BET!", description=f"{ctx.message.author.name} has predicted {time_str} betting {stake} coins" ,inline=True, color=0x0000ff))
    else:
        await ctx.send(embed=discord.Embed(Title="Error", description="Sorry! There is no round in progress to bet on.", color=0xff0000))


# TODO: restore as a check members command or remove
    # vc = discord.utils.get(ctx.guild.voice_channels, name='General')
    # members = '\n - '.join([member.name for member in vc.members])
    # await ctx.send(f"Users in voice chat: \n {members}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        arg = error.param.name
        await ctx.send(f"The previous command is missing parameter:\n -> {arg} <-")

bot.run(TOKEN)
