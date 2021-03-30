import numpy as np
import datetime

class Player:
    def __init__(self, discord_id, time_bet, stake):
        self.discord_id = discord_id
        self.time_bet = time_bet
        self.stake = stake
        self.money = 100 # Pull value from database?

    def __str__(self):
        return f"""
        Player: {self.discord_id}
        Money: {self.money}
        Time Bet: {self.time_bet}
        Stake: {self.stake}
        """

class Round:
    micro_second_factor = 1_000_000

    def __init__(self, member, start_time, proposed_time, command_channel):
        self.member = member
        self.start_time = np.datetime64(start_time)
        self.proposed_time = np.datetime64(proposed_time)
        self.command_channel = channel 

        self.players = []
        self.arrival_time = np.datetime64()

    def list_players(self):
        return "\n".join((player.__str__() for player in self.players))

    def end_round(self):
        self.arrival_time = np.datetime64(datetime.now())

        stakes = np.array[self.players[i].stake for i in range(len(self.players))]

        distances = calculate_distances(self.arrival_time)

        winnings = get_winnings(distances, stakes)

        for i in range(len(self.players)):
            self.players[i].money = new_money[i]
 
    def calculate_sandwichness(self):
        # Get difference between when member says they will arrive vs when they actually do
        # in seconds.
        return (self.proposed_time - self.arrival_time).astype(int) / micro_second_factor

    def calculate_distances(self, comparative_time):
        times_bet = np.array([self.players[i].time_bet for i in range(n)])

        return abs((comparative_time - times_bet).astype(int) / micro_second_factor)

    def score_func(self, distances):
        if not isinstance(distances, np.ndarray):
            distances = np.array(distances)
            
        avg_distance = distances.mean() 

        return (avg_distance - distances)/avg_distance \
            if (avg_distance != 0) \
            else np.ones(n)

    def get_scores(self, distances):
        return np.around(score_func(distances) - score_func(distances.mean()), decimals=3)

    def get_winnings(self, distances, stakes):
        scores = pog_score_fun(distances)
        winnings = stakes * scores

        return winnings