import numpy as np
from datetime import datetime

class Player:
    def __init__(self, discord_id, time_bet, stake):
        self.discord_id = discord_id
        self.time_bet = np.datetime64(time_bet)
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
    # TODO: Privatize some of the functions
    micro_second_factor = 1_000_000

    def __init__(self, member, start_time, proposed_time, command_channel):
        self.member = member
        self.start_time = np.datetime64(start_time)
        self.proposed_time = np.datetime64(proposed_time)
        self.command_channel = command_channel 

        self.players = []
        self.arrival_time = np.datetime64()

    def list_players(self):
        return "\n".join((player.__str__() for player in self.players))

    def end_round(self):
        self.arrival_time = np.datetime64(datetime.now())

        player_data = np.array([
            (self.players[i].stake, self.players[i].money, self.players[i].time_bet)
            for i in range(len(self.players))
        ])

        # Can't remember if this is how numpy arrays work.
        # It absolutely isn't...
        # But above avoids mutliple iterations
        stakes = player_data[0]
        old_money = player_data[1]
        times_bet = player_data[2]

        distances = calc_distances(times_bet, self.arrival_time)
        winnings = get_winnings(distances, stakes)
        new_money = old_money + winnings

        for i in range(len(self.players)):
            self.players[i].money = new_money[i]

        # Post to database?

        # Return something? For Chris todo...
        return None
 
    def calc_sandwichness(self):
        # Get difference between when member says they will arrive vs when they actually do
        # in seconds.
        # Not used in calculations, but probably helpful function for Chris.
        return (self.proposed_time - self.arrival_time).astype(int) / micro_second_factor

    def calc_distances(self, times_bet, comparative_time):
        return abs((comparative_time - times_bet).astype(int) / micro_second_factor)

    def score_func(self, distances):
        if not isinstance(distances, np.ndarray):
            distances = np.array(distances)
            
        avg_distance = distances.mean() 

        return (avg_distance - distances)/avg_distance \
            if (avg_distance != 0) \
            else np.ones(n)

    def calc_scores(self, distances):
        return np.around(score_func(distances) - score_func(distances.mean()), decimals=3)

    def calc_winnings(self, distances, stakes):
        scores = pog_score_fun(distances)
        winnings = stakes * scores

        return winnings
