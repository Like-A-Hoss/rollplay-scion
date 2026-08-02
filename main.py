try:
    import audioop  # type: ignore
except ModuleNotFoundError:
    import audioop_lts as audioop  # type: ignore

import nextcord
from nextcord.ext import commands

from settings import SECRET_KEY as SECRET_KEY
from settings import TESTING_SERVER as testingServerID
import cogs.dice as dice
import cogs.embed_message_maker as message_maker


intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True


client = commands.Bot(intents=intents)

@client.event
async def on_ready():
    print("Hello Papa!\n")

    try:
        guild_id = int(testingServerID)
    except (TypeError, ValueError):
        print(f"Invalid TESTING_SERVER value: {testingServerID}")
        return
    if guild_id is None:
        print("TESTING_SERVER environment variable is not set.")
    print (f"Using guild ID: {guild_id}")
    
    guild = client.get_guild(guild_id)
    if guild is None:
        print(f"Could not find guild with ID {guild_id}")
        print("Guilds currently available to this bot:")
        for available_guild in client.guilds:
            print(f"- {available_guild.id}: {available_guild.name}")
        return

    channel = next((c for c in guild.text_channels if c.name == "general"), None)
    if channel is None:
        channel = guild.system_channel

    if channel is not None:
        await channel.send("Hello Papa!\n")

    try:
        await client.sync_application_commands(guild_id=guild_id)
        print(f"Synced slash commands to guild: {guild.name} ({guild.id})")
    except Exception as exc:
        print(f"Failed to sync slash commands for guild {guild.name} ({guild.id}): {exc}")

@client.slash_command(name="dramatic_roll", description="Rolls a number of dice, adds in the enhancement and scale modifiers, then subtracts difficulty.")
async def dramatic_roll(
    interaction: nextcord.Interaction,
    dice_pool: int,
    enhancement: int,
    hero_type: str = nextcord.SlashOption(
        name="hero_type",
        description="Choose the hero type",
        choices=["Origin", "Hero", "Demigod", "God"],
    ),
    scale: int = nextcord.SlashOption(
        name="scale",
        description="Choose the difference in scale for the action",
        choices=[0, 1, 2, 3, 4, 5, 6],
    ),
    difficulty: int = 1,
    again: int = 10,
):
    tn = 8 if hero_type in {"Origin", "Hero"} else 7

    scion_dice = dice.ScionDice(
        dice_pool=dice_pool,
        enhancement=enhancement,
        hero_type=hero_type,
        scale=scale,
        difficulty=difficulty,
        tn=tn,
        again=again,
    )

    results = scion_dice.roll()
    exploded_results = scion_dice.check_explode(results)
    successes = scion_dice.count_successes(results, exploded_results)
    

    await interaction.response.send_message(
        f"Rolling {dice_pool} dice with hero type {hero_type}.\n"
        f"TN: {tn}\n"
        f"Initial roll: {results}\n"
        f"Exploded results: {exploded_results}\n"
        f"Successes: {successes}\n"
    )


client.run(SECRET_KEY)