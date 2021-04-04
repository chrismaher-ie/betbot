import json

import numpy as np

from datetime import datetime
from dateutil.parser import parse

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# with open("schema.gql") as f:
#     scehma_str = f.read()

# transport=RequestsHTTPTransport(
#     url='https://graphql.fauna.com/graphql/',
#     use_json=True,
#     headers={
#         "Content-type": "application/json",
#     },
#     verify=False,
#     retries=3
# )

# client = Client(
#     transport=transport,
#     schema=scehma_str
# )

class TrialBalance:
    def __init__(self, player_obj, amount, date_time):
        self.player = player_obj
        self.amount = amount
        self.date_time = np.datetime64(date_time)

    def __str__(self):
        return f"Player {self.player.name} had {self.amount} Jambux at {self.date_time}"

    def repr_JSON(self):
        return dict(
            amount=self.amount, 
            date_time=datetime.strftime(self.date_time.item(), "%Y-%m-%dT%H:%M:%SZ")
        )

class Bet:
    def __init__(self, round_obj, player_obj, time_bet, stake):
        self.round = round_obj
        self.player = player_obj
        self.time_bet = np.datetime64(time_bet)
        self.stake = stake

        self.winnings = float()
    
    def __str__(self):
        return f"""
        Discord ID: {self.player.discord_id}
        Time Bet: {self.time_bet}
        Stake Bet: {self.stake}
        """

    def repr_JSON(self):
        return dict(
            time_bet = datetime.strftime(self.time_bet.item(), "%Y-%m-%dT%H:%M:%SZ"),
            stake = self.stake,
            winnings = self.winnings
        )

    def set_winnings(self, winnings):
        """Set the winnings earned from this particular bet.

        Args:
            winnings (float): The amount of Jambux won from this bet.
        """
        self.winnings = winnings

class Player:
    def __init__(self, discord_id, player_name, money = 100):
        self.discord_id = discord_id # Discord ID
        self.player_name = player_name
        self.money = money

        self.bets = []
        self.trial_balances = []

    def __str__(self):
        return f"""
        Discord ID: {self.discord_id}
        Name: {self.player_name}
        Current Money: {self.money}
        """

    def repr_JSON(self):
        return dict(
            discord_id = self.discord_id,
            player_name = self.player_name,
            money = self.money,
            bets = self.bets,
            trial_balances = self.trial_balances
        )

    @classmethod
    def new_player(cls, message_author):
        discord_id = message_author.id
        player_name = message_author.name

        # Pull data from Fauna based on discord_id index.
        
        if exists_in_db:
            return player_obj_from_db
        else:
            return cls(discord_id, player_name)

    def add_bet(self, bet):
        """Add a Bet object to the player's list of bets.
        
        Args:
            bet (Bet): The bet object to add to the player's list of bets.
        """
        self.bets.append(bet)

    def add_trial_balance(self, trial_balance):
        """Add a TrialBalance object to the player's list of trial balances.
        
        Args:
            trial_balance (TrialBalance): The trial balance object to add to the player's list of trial balances.
        """
        self.trial_balances.append(trial_balance)

class Round:
    _ns_to_min_factor = 60_000_000

    def __init__(self, member, start_time, proposed_time, command_channel):
        self.member = member
        self.start_time = np.datetime64(start_time)
        self.proposed_time = np.datetime64(proposed_time)
        self.command_channel = command_channel 

        self.bets = []

        self.arrival_time = np.datetime64()

    def __str__(self):
        return f"""
        Round ID: {self.round_id}
        Person of Interest: {self.member}
        Round Start Time: {self.start_time}
        Proposed Arrival Time: {self.proposed_time}
        Arrival Time: {"Not arrived" if self.arrival_time.isnull() else self.arrival_time}
        """

    def repr_JSON(self):
        return dict(
            member = self.member,
            start_time = datetime.strftime(self.start_time.item(), "%Y-%m-%dT%H:%M:%SZ"),
            proposed_time = datetime.strftime(self.proposed_time.item(), "%Y-%m-%dT%H:%M:%SZ"),
            command_channel = self.command_channel,
            arrival_time = datetime.strftime(self.arrival_time.item(), "%Y-%m-%dT%H:%M:%SZ"),
            bets = self.bets
        )

    @classmethod
    def new_round(cls, member, start_time, proposed_time, command_channel):
        return cls(member, start_time, proposed_time, command_channel)

    def end_round(self):
        """End the round, setting the arrival time as the current time, getting each bet's
        winnings, updating the player and bet objects accordingly, creating a new trial
        balance object, and then pushing data to database.

        Returns:
            None: Chris, to decide if something should be returned.
        """
        self.arrival_time = np.datetime64(datetime.now())

        bet_data = np.array([(self.bets[i].stake, self.bets[i].time_bet)
            for i in range(len(self.bets))
        ])

        stakes = bet_data[:,0]
        times_bet = bet_data[:,1].astype(np.datetime64) # Prevent dumb coercion

        # Keeps order of bets so can map seamlessly.
        players = [self.bets[i].player for i in range(len(self.bets))]

        distances = self.calc_distances(times_bet, self.arrival_time)
        winnings = self.calc_winnings(distances, stakes)

        for i in range(len(winnings)):
            # Add new money to player's account.
            players[i].money += winnings[i]

            # Make a new trial balance for the player.
            trial_balance = TrialBalance(players[i], players[i].money, self.arrival_time)

            # Add the new trial balance to the player.
            players[i].add_trial_balance(trial_balance)

            # Add the winnings to each bet object.
            self.bets[i].set_winnings(winnings[i])

        self.upload()

        # Return something? For Chris to decide...
        return None

    def upload(self):
        """Run GQL query/mutation to upload round object along with its bets, 
        each bet's player, and each player's latest trial balance.
        """
        return f'''
        member: "{self.member}"
        start_time: "{self.start_time}"
        proposed_time: "{self.proposed_time}"
        command_channel: "{self.command_channel}"
        arrival_time: "{self.arrival_time}"
        bets: {{
            create: {[self.bets[i].upload() for i in range(len(bets))]}
        }}
        '''

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
        player.add_bet(bet)

    def list_bets(self):
        """List the bets of the round.
        
        Returns:
            str: A string containing each bet's description.
        """
        bet_descriptions = [self.bets[i].__str__() for i in range(len(bets))]
        return "\n".join(bet_descriptions)

    def list_players(self):
        """List the players of the round by getting the player associated with each bet.
        
        Returns:
            str: A string containing each player's description.
        """
        player_descriptions = [bets[i].player.__str__() for i in range(len(bets))]
        return "\n".join(players)
 
    def calc_sandwichness(self):
        """Get difference between when member says they will arrive vs when they actually do 
        in seconds. Not used in calculations, but probably helpful function for Chris.

        Returns:
            ndarray[float]: Distance member's arrival time is away from proposed time, in minutes.            
        """
        return (self.proposed_time - self.arrival_time).astype(int) / self._ns_to_min_factor

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
            
        avg_distance = distances.mean() 

        return (avg_distance - distances)/avg_distance \
            if (avg_distance != 0) \
            else np.zeros(len(distances))

    def calc_scores(self, distances):
        """Use the score function to calculate the scores from the distances. 
        Subtracts score of mean to normalize.

        Args:
            distances (ndarray[timedelta64]): The distances the times bet are away from 
                the arrival time.

        Returns:
            ndarray[float]: The final scores for each player.
        """
        return np.around(self.score_func(distances) - self.score_func(distances.mean()), decimals=3)

    def calc_winnings(self, distances, stakes):
        """Calculate total winnings from the distances and the stakes.

        Args:
            distances (ndarray[timedelta64]): The distances the times bet are away from 
                the arrival time.
            stakes (ndarray[timedelta64]): The stakes (amount of money) bet.

        Returns:
            ndarray[float]: The final winnings for each player.
        """
        scores = self.calc_scores(distances)
        winnings = stakes * scores

        return winnings 

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'repr_JSON'):
            return obj.repr_JSON()
        else:
            return json.JSONEncoder.default(self, obj)

if __name__ == "__main__":
    rnd = Round.new_round("ham", parse("22:30:00"), parse("23:00:00"), "general")
    player1 = Player("bd3dowling", "ben")
    player2 = Player("cmaher", "chris")
    rnd.add_bet(player1, parse("23:10:00"), 10)
    rnd.add_bet(player2, parse("23:20:00"), 15)
    print(rnd.upload())