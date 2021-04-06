from fauna_base import *

# Delete indexes
client.query(q.delete(q.index("players_by_discord_id")))

# Delete collections