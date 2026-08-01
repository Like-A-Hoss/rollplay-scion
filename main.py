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
import cogs.scaleByFactor as scaleByFactor


intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

init_list = []

client = commands.Bot(intents=intents)

@client.event
async def on_ready():
    print("Hello Papa!\n")

    guild = client.get_guild(int(testingServerID))
    if guild is None:
        print(f"Could not find guild with ID {testingServerID}")
        print("Guilds currently available to this bot:")
        for available_guild in client.guilds:
            print(f"- {available_guild.id}: {available_guild.name}")
        return

    channel = next((c for c in guild.text_channels if c.name == "general"), None)
    if channel is None:
        channel = guild.system_channel

    if channel is not None:
        await channel.send("Hello Papa!\n")

    await client.clear_guild_commands(guild)
@client.slash_command(name="dramaticRoll", description="Rolls a number of dice, adds in the enhancement and scale modifiers, then subtracts difficulty.")
async def dramatic_roll(
    interaction: nextcord.Interaction,
    dice_pool: int,
    enhancement: int = 0,
    hero_type: str = nextcord.SlashOption(
        name="hero_type",
        description="Choose the hero type",
        choices=[
            nextcord.OptionChoice(name="Origin", value="Origin"),
            nextcord.OptionChoice(name="Hero", value="Hero"),
            nextcord.OptionChoice(name="Demigod", value="Demigod"),
            nextcord.OptionChoice(name="God", value="God"),
        ],
    ),
    scale: int = nextcord.SlashOption(
        name="scale",
        description="Choose the difference in scale of the action",
        choices=[
            nextcord.OptionChoice(name="0 - Normal", value=0),
            nextcord.OptionChoice(name="1 - Elite", value=1),
            nextcord.OptionChoice(name="2 - Supernatural", value=2),
            nextcord.OptionChoice(name="3 - Incredible", value=3),
            nextcord.OptionChoice(name="4 - Godlike", value=4),
            nextcord.OptionChoice(name="5 - Supernal", value=5),
            nextcord.OptionChoice(name="6 - Titanic", value=6),
        ],
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
    successes = scion_dice.count_successes(results,exploded_results)
    

    await interaction.response.send_message(
        f"Rolling {dice_pool} dice with hero type {hero_type}.\n"
        f"TN: {tn}\n"
        f"Initial roll: {results}\n"
        f"Exploded results: {exploded_results}\n"
        f"Successes: {successes}\n"
        f"Final result: {final_result}"
    )


client.run(SECRET_KEY)