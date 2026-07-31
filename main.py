import nextcord
from nextcord.ext import commands
from settings.py import SECRET_KEY as SECRET_KEY
from settings import TESTING_SERVER as testingServerID
import cogs.dice as dice
import cogs.embed_message_maker as message_maker



intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

init_list = []


client = commands.Bot(intents = intents)

@client.event
async def on_ready():
    print("Hello Papa!\n")
    await client.get_channel(testingServerID).send("Hello Papa!\n")
    await client.clear_guild_commands(testingServerID)


client.run(SECRET_KEY)