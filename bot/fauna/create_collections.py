from fauna_base import *

# Create rounds collection
client.query(
    q.create_collection(
        {
            "name": "rounds",
            "history_days": 0
        }
    )
)

# Create bets collection
client.query(
    q.create_collection(
        {
            "name": "bets",
            "history_days": 0
        }
    )
)

# Create trial balances collection
client.query(
    q.create_collection(
        {
            "name": "trial_balances",
            "history_days": 0
        }
    )
)

# Create players collection
client.query(
    q.create_collection(
        {
            "name": "players",
            "history_days": 0
        }
    )
)