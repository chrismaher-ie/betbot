import random
import numpy as np

def score_func(distances):
    if not isinstance(distances, np.ndarray):
        distances = np.array(distances)

    n = distances.size
    avg_distance = distances.mean() 

    return (avg_distance - distances)/avg_distance if (avg_distance != 0) else np.ones(n)

    # # Get boolean array indicating if element is max
    # is_max = winnings == winnings.max()
    # num_winners = is_max.sum()

    # # Give bonus for winner; take from 'losers'
    # winnings = (is_max * (winnings + ((n - num_winners)/num_winners))) + (~is_max * (winnings - 1))

def pog_score_fun(distances):
    return np.around(score_func(distances) - score_func(distances.mean()), decimals=3)

def get_winnings(distances, bets):
    if not isinstance(distances, np.ndarray):
        distances = np.array(distances) 

    if not isinstance(bets, np.ndarray):
        bets = np.array(bets) 

    scores = pog_score_fun(distances)
    winnings = bets * scores

    return winnings

class Game:

    def __init__(self, min_players = 1, max_players = 10, starting_money = 50, money_delta = 10):

        self.num_players = random.randrange(min_players, max_players)

        money = np.random.randint(
            starting_money - money_delta, 
            starting_money + money_delta,
            size=self.num_players
        )

        self.players = [Player(i, money[i]) for i in range(self.num_players)]

        self.new_total_money = np.sum(money)

        self.old_total_money = self.new_total_money

        self.sum_changes = 0
        self.rounds_simulated = 0

    def __str__(self):
       
        return f"""
        Number of players: {self.num_players}
        Prior total money: {self.old_total_money}
        Current total money: {self.new_total_money}
        Change: {self.new_total_money - self.old_total_money}
        Total Avg Change: {self.sum_changes/self.rounds_simulated if self.rounds_simulated != 0 else 0}
        """

    def print_players(self):
        
        return "\n".join((player.__str__() for player in self.players))


    def simulate_round(self, guess_delta=10, bet_ave=11, bet_delta=9):
        self.old_total_money = self.new_total_money
        self.rounds_simulated += 1
        
        n = self.num_players
        
        guesses = np.random.randint(guess_delta, size=n)

        bets = np.random.randint(
                bet_ave - bet_delta, 
                bet_ave + bet_delta,
            size=n
        )

        profits = get_winnings(guesses, bets)

        old_money = np.fromiter((self.players[i].money for i in range(n)), float)
        new_money = old_money + profits

        self.new_total_money = new_money.sum()

        for i in range(n):
            self.players[i].last_guess = guesses[i]
            self.players[i].bet = bets[i]
            self.players[i].money = new_money[i]

        self.sum_changes += (self.new_total_money - self.old_total_money)

        return None

    
class Player:

    def __init__(self, id, money):
        self.id = id
        self.money = money
        self.last_guess = 0
        self.bet = 0

    def __str__(self):
        return f"Player{self.id} has {self.money} coins"


if __name__== "__main__":

    game = Game(min_players = 1, max_players=10, starting_money=50, money_delta=10)

    print(game.print_players())
    print(game)

    while True:

        input("hit enter for new round")
        
        game.simulate_round()

        print(game.print_players())
        print(game)

