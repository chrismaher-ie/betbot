from fauna.fauna_base import *

def push(round_ref, arrival_time, players, bets, trial_balances):
    return q.do(
        add_arrival_time_to_round(round_ref, arrival_time),
        new_bets(round_ref, bets),
        update_players(players),
        new_trial_balances(players)
    )

def add_arrival_time_to_round(round_ref, arrival_time):
    return q.update(
        round_ref,
        {
            "data": {
                "arrival_time": str(arrival_time)
            }
        }
    )

def new_round(member, start_time, proposed_time, command_channel):
    return q.select(
        ['ref'],
        q.create(
            q.collection('rounds'),
            {
                "data": {
                    "member": member,
                    "start_time": str(start_time),
                    "proposed_time": str(proposed_time),
                    "command_channel": command_channel
                }
            }
        )
    )
    
# UPDATE ROUND; WITH ARRIVAL TIME

def new_bets(round_ref, bets):
    bets_values = [
        [str(bet.time_bet), bet.stake, bet.winnings, bet.player_.ref]
        for bet in bets
    ]
    return q.map_(
        q.lambda_(
            ["time_bet", "stake", "winnings", "player_ref"],
            new_bet(
                q.var("time_bet"), 
                q.var("stake"), 
                q.var("winnings"), 
                q.var("player_ref"), 
                round_ref
            )
        ),
        bets_values
    )

def new_bet(time_bet, stake, winnings, player_ref, round_ref):
    return q.create(
        q.collection('bets'),
        {
            "data": {
                "time_bet": str(time_bet),
                "stake": stake,
                "winnings": winnings,
                "player": player_ref,
                "round": round_ref
            }
        }
    )

def new_trial_balances(players):
    players_values = [[player.ref, player.money] for player in players]
    return q.map_(
        q.lambda_(
            ["player_ref", "amount"],
            new_trial_balance(
                q.var("player_ref"),
                q.var("amount")
            )
        ),
        players_values
    )

def new_trial_balance(player_ref, amount):
    return q.create(
        q.collection('trial_balances'),
        {
            "data": {
                "player": player_ref,
                "amount": amount,
                "date_time": q.now() # Can remove since _ts is a thing.
            }
        }
    )

def update_players(players):
    players_values = [
        [player.discord_id, player.player_name, player.money] 
        for player in players
    ]
    return q.map_(
        q.lambda_(
            ["discord_id", "player_name", "money"],
            create_or_update_player(
                q.var("discord_id"),
                q.var("player_name"),
                q.var("money")
            )
        ),
        players_values
    )

def create_or_update_player(discord_id, player_name, money):
    return q.let(
        {
            "match": q.match(
                q.index('players_by_discord_id'),
                discord_id
            )
        },
        q.if_(
            q.exists(q.var("match")),
            q.select(
                ['ref'], 
                q.update(
                    q.select(['ref'], q.get(q.var("match"))),
                    {
                        "data": {
                            "player_name": player_name,
                            "money": money
                        }
                    }
                )
            ),
            q.select(
                ['ref'],
                q.create(
                    q.collection('players'),
                    {
                        "data": {
                            "discord_id": discord_id,
                            "player_name": player_name,
                            "money": money
                        }
                    }
                )
            )
        )
    )