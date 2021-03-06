import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from dateutil.parser import parse # Remove before finishing
import discord

from fauna.fauna_base import *
import fauna.functions as f

class Round:
    _ns_to_min_factor = 60_000_000

    def __init__(self, member, command_channel, start_time, proposed_time):

        self.member: discord.Member = member
        self.command_channel: discord.channel.TextChannel = command_channel 

        self.start_time: np.datetime64 = start_time
        self.proposed_time: np.datetime64 = proposed_time

        self.ref: Ref = self._get_ref(member.name, start_time, proposed_time)

        self.bets = []
        self.arrival_time: np.datetime64 = None

    def _get_ref(self, member_name, start_time, proposed_time):
        return client.query(f.new_round(member_name, start_time, proposed_time))

    def __str__(self):
        return f"""Person of Interest: {self.member.name}
        Round Start Time: {self.start_time}
        Proposed Arrival Time: {self.proposed_time}
        Arrival Time: {self.arrival_time if self.arrival_time else "Hasn't arrived"}"""

    def end_round(self):
        """End the round, setting the arrival time as the current time, getting each bet's
        winnings, updating the player and bet objects accordingly, creating a new trial
        balance object, and then pushing data to database.

        Returns:
            Discord embeded message with the results from the round
        """

        # No players bet -> end round
        if len(self.bets) == 0:
            return discord.Embed(
                Title="Ended!", 
                description="The current round has ended but no bets were made, Boo!",
                inline=False, 
                color=0x0000ff
            )
            # TODO: set round state in db to closed

        self.arrival_time = np.datetime64(datetime.now())

        bet_data = np.array([(bet.stake, bet.time_bet)
            for bet in self.bets
        ])

        stakes = bet_data[:,0]
        times_bet = bet_data[:,1].astype(np.datetime64) # Prevent dumb coercion

        # Keeps order of bets so can map seamlessly.
        players = [bet.player_ for bet in self.bets]

        distances = self.calc_distances(times_bet, self.arrival_time)
        winnings = self.calc_winnings(distances, stakes)

        for i in range(len(winnings)):
            # Add new money to player's account.
            players[i].money += winnings[i]

            # Add the winnings to each bet object.
            self.bets[i].winnings = winnings[i]

        # Make a new trial balances for each player.
        trial_balances = [TrialBalance(player, player.money, self.arrival_time) for player in players]

        client.query(f.push(self.ref, self.arrival_time, players, self.bets, trial_balances))


        #temporary for testing
        #calculate time
        timedelta = self.calc_sandwichness()
        if timedelta > 0:
            result_msg = f"{self.member.name} is early by {timedelta} minutes! Congrats!"
        elif timedelta < 0:
            timedelta *= -1
            result_msg = f"{self.member.name} is late by {timedelta} minutes! Boo!"
        elif timedelta == 0:
            result_msg = f"{self.member.name} is on time!"

        embedVar = discord.Embed(title="Round Ended", description=f"Member {self.member} has arrived", color=0x00ff00)
        embedVar.add_field(name="Promised time", value=self.proposed_time.item().strftime("%H:%M:%S"), inline=True)
        embedVar.add_field(name="Current time", value=self.arrival_time.item().strftime("%H:%M:%S"), inline=True)
        embedVar.add_field(name="Result", value=result_msg, inline=False)
        embedVar.add_field(name="Bets", value="List of Player Bets:", inline=True)
        for bet in self.bets:
            time = bet.time_bet.item().strftime("%H:%M:%S")
            embedVar.add_field(name=bet.player_.name, value=f"Guess: {time}, Winnings: {bet.winnings}, Money: {bet.player_.money}", inline=False)
        #TODO: add bet information to embed
        return embedVar

    def cancel_round(self):
        # TODO: set round state in db to closed
        return

    def add_bet(self, player, time_bet, stake):
        """Add a bet object to the round's list of bets. 
        Also call the players add_bet method to add it to their list of bets.

        Args:
            player (Player): The player object to which the bet correponds.
            time_bet (datetime64): The date and time at which the bet was made.
            stake (int): Amount of Jambux bet.
        """
        bet = Bet(self, player, time_bet, stake)

        self.bets.append(bet)

    def list_bets(self):
        """List the bets of the round.
        
        Returns:
            str: A string containing each bet's description.
        """
        bet_descriptions = [bet.__str__() for bet in self.bets]
        return "\n".join(bet_descriptions)

    def list_players(self):
        """List the players of the round by getting the player associated with each bet.
        
        Returns:
            str: A string containing each player's description.
        """
        player_descriptions = [bet.player_.__str__() for bet in self.bets]
        return "\n".join(player_descriptions)
 
    def calc_sandwichness(self):
        """Get difference between when member says they will arrive vs when they actually do 
        in seconds. Not used in calculations, but probably helpful function for Chris.

        Returns:
            ndarray[float]: Distance member's arrival time is away from proposed time, in minutes.            
        """
        return ((self.proposed_time - self.arrival_time) / self._ns_to_min_factor).astype(int)

    def calc_distances(self, times_bet, comparative_time):
        """Calculate the distances (in minutes) each time bet is from the comparative time 
        (usually the arrival time).

        Args:
            times_bet (ndarray[datetime64]): Times bet by each player.
            comparative_time (datetime64): Time to compute distance against.

        Returns:
            ndarray[float]: Distance each players bet is away from comparative time, in minutes.
        """
        return abs((comparative_time - times_bet).astype(int) / self._ns_to_min_factor)

    def score_func(self, distances):
        """The score function used for calculating each bets/player's score for that round. 

        Args:
            distances (ndarray[timedelta64]): The distances the times bet are away from 
                the arrival time.
        
        Returns:
            ndarray[float]: The unnormalized scores for each player.
        """
        if not isinstance(distances, np.ndarray):
            distances = np.array(distances)
            
        return 8/(distances + 2)

    def calc_scores(self, distances):
        """Use the score function to calculate the scores from the distances. 
        Subtracts score of mean to normalize.

        Args:
            distances (ndarray[float]): The distances the times bet are away from 
                the arrival time.

        Returns:
            ndarray[float]: The final scores for each player.
        """
        print(f"Distances: {distances}")
        scores_unnormalized = self.score_func(distances)
        print(f"Unnorm_scores: {scores_unnormalized}")
        average_score = scores_unnormalized.mean()
        print(f"Avg unnorm score: {average_score}")
        return np.around(scores_unnormalized - average_score, decimals=3)

    def calc_winnings(self, distances, stakes):
        """Calculate total winnings from the distances and the stakes.

        Args:
            distances (ndarray[float]): The distances the times bet are away from 
                the arrival time.
            stakes (ndarray[timedelta64]): The stakes (amount of money) bet.

        Returns:
            ndarray[float]: The final winnings for each player.
        """
        scores = self.calc_scores(distances)
        print(f"Scores: {scores}")
        winnings = stakes * scores

        return winnings 

@dataclass
class Player:
    ref: Ref = field(init=False, repr=False)
    discord_id: int
    name: str
    money: float = field(init=False)
    bets: list = field(init=False, repr=False)
    trial_balances: list = field(init=False, repr=False)

    def __post_init__(self):
        resp = client.query(f.get_or_create_player(
            self.discord_id,
            self.name
        ))

        self.ref = resp['ref']
        self.money = resp['data']['money']

    def __str__(self):
        return f"""Discord ID: {self.discord_id}
        Name: {self.name}
        Current Money: {self.money}"""

@dataclass
class TrialBalance:
    player_: Player
    amount: float
    date_time: np.datetime64

@dataclass
class Bet:
    round_: Round
    player_: Player
    time_bet: np.datetime64
    stake: float
    winnings: float = field(init=False, repr=False)
    
    def __str__(self):
        return f"""Discord ID: {self.player_.discord_id}
        Time Bet: {self.time_bet}
        Stake Bet: {self.stake}"""

if __name__ == "__main__":
    p1 = Player(999, "chris")
    print(p1.ref)
    p2 = Player(000, "brian")
    print(p2)
    x = Round(123, np.datetime64(datetime.now()), np.datetime64(parse("21:00:00")), "general")
    x.add_bet(p1, np.datetime64(parse("22:20:00")), 100)
    x.add_bet(p2, np.datetime64(parse("21:20:00")), 100)
    x.end_round()