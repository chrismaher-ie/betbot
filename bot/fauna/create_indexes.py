from fauna_base import *

# Create index for retrieving players
client.query(
    q.create_index({
        "name": "players_by_discord_id",
        "source": q.collection("players"),
        "terms": [
            { "field": ["data", "discord_id"] }
        ],
        "unique": True
    })
)