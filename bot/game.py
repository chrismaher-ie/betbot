import numpy as np
from datetime import datetime

class Trial_Balance:
    def __init__(self, player, amount, date_time):
        self.player = player
        self.amount = amount
        self.date_time = date_time

    def __str__(self):
        return f"Player {self.player.name} had {self.amount} Jambux at {self.date_time}"

class Bet:
    def __init__(self, round_id, player, time_bet, stake):
        self.round_id = round_id
        self.player = player
        self.time_bet = time_bet
        self.stake = stake

        self.winnings = float()
    
    def __str__(self):
        return f"""
        Round ID: {self.round_id}
        Player ID: {self.player.player_id}
        Time Bet: {self.time_bet}
        Stake Bet: {self.stake}
        """

    def set_winnings(self, winnings):
        """Set the winnings earned from this particular bet.

        Args:
            winnings (float): The amount of Jambux won from this bet.
        """
        self.winnings = winnings

class Player:
    def __init__(self, player_id, player_name, money = 100):
        self.player_id = player_id
        self.name = player_name
        self.money = money

        self.bets = []

    def __str__(self):
        return f"""
        Player ID: {self.player_id}
        Name: {self.name}
        Current Money: {self.money}
        """

    @classmethod
    def new_player(cls, message_author):
        # Try pull in player from player table with player_id.
        player_id = message_author.id
        player_name = message_author.name

        if exists_in_db:
            return player_obj_from_db
        else:
            return Player(player_id, player_name)

    def add_bet(self, bet):
        """Add a bet object to the player's list of bets.
        
        Args:
            bet (Bet): The bet object to add to the player's list of bets.
        """
        self.bets.append(bet)

class Round:
    _ns_to_min_factor = 60_000_000

    def __init__(self, member, start_time, proposed_time, command_channel):
        self.member = member
        self.start_time = np.datetime64(start_time)
        self.proposed_time = np.datetime64(proposed_time)
        self.command_channel = command_channel 

        # Pull from db.
        self.round_id = 

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

    def end_round(self):
        """End the round, setting the arrival time as the current time, getting each bet's
        winnings, updating the player and bet objects accordingly, creating a new trial
        balance object, and then pushing data to database.

        Returns:
            None: Chris, to decide if something should be returned.
        """
        self.arrival_time = np.datetime64(datetime.now())

        bet_data = np.array([
            (self.bets[i].stake, self.bets[i].time_bet)
            for i in range(len(self.bets))
        ])

        # Keeps order of bets so can map seamlessly.
        players = [self.bets[i].player for i in range(len(self.bets))]

        stakes = player_data[:,0]
        times_bet = player_data[:,1]

        distances = calc_distances(times_bet, self.arrival_time)
        winnings = calc_winnings(distances, stakes)

        for i in range(len(self.winnings)):
            # Add new money to player's account.
            players[i].money += winnings[i]

            # Add the winnings to each bet object.
            self.bets[i].set_winnings(winnings[i])

        # Create TB from updated player data.
        trial_balances = [
            Trial_Balance(player, player.money, self.arrival_time) 
            for player in players
        ]

        # PUSH TO DB HERE. Handler?

        # Return something? For Chris to decide...
        return None

    def add_bet(self, player, time_bet, stake):
        """Add a bet object to the round's list of bets. 
        Also call the players add_bet method to add it to their list of bets.

        Args:
            player (Player): The player object to which the bet correponds.
            time_bet (datetime64): The date and time at which the bet was made.
            stake (int): Amount of Jambux bet.
        """
        bet = Bet(self.round_id, player, time_bet, stake)
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
        return (self.proposed_time - self.arrival_time).astype(int) / _micro_second_factor

    def calc_distances(self, times_bet, comparative_time):
        """Calculate the distances (in minutes) each time bet is from the comparative time 
        (usually the arrival time).

        Args:
            times_bet (ndarray[datetime64]): Times bet by each player.
            comparative_time (datetime64): Time to compute distance against.

        Returns:
            ndarray[float]: Distance each players bet is away from comparative time, in minutes.
        """
        return abs((comparative_time - times_bet).astype(int) / _micro_second_factor)

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
            else np.ones(len(distances))

    def calc_scores(self, distances):
        """Use the score function to calculate the scores from the distances. 
        Subtracts score of mean to normalize.

        Args:
            distances (ndarray[timedelta64]): The distances the times bet are away from 
                the arrival time.

        Returns:
            ndarray[float]: The final scores for each player.
        """
        return np.around(score_func(distances) - score_func(distances.mean()), decimals=3)

    def calc_winnings(self, distances, stakes):
        """Calculate total winnings from the distances and the stakes.

        Args:
            distances (ndarray[timedelta64]): The distances the times bet are away from 
                the arrival time.
            stakes (ndarray[timedelta64]): The stakes (amount of money) bet.

        Returns:
            ndarray[float]: The final winnings for each player.
        """
        scores = calc_scores(distances)
        winnings = stakes * scores

        return winnings

if __name__ == "__main__":
    return None