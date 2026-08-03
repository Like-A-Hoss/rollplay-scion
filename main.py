try:
    import audioop  # type: ignore
except ModuleNotFoundError:
    import audioop_lts as audioop  # type: ignore

import nextcord
from nextcord.ext import commands

from cogs import scaleByFactor
from settings import SECRET_KEY as SECRET_KEY
from settings import TESTING_SERVER as testingServerID
import cogs.dice as dice
import cogs.embed_message_maker as embed_message_maker
import cogs.reactive_defense as reactive_defense


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
    message_maker = embed_message_maker.MessageMaker(hero_type=hero_type)
    botched = scion_dice.check_botch(results, exploded_results, successes)
    successes -= difficulty
    if successes > 0:
        embed_response = message_maker.sucess_dramatic(
            interaction=interaction,
            results=results,
            exploded_results=exploded_results,
            sux=successes,
            enhancement=enhancement,
            scale=scale,
            difficulty=difficulty,
        )
    else:
        if botched:
            embed_response = message_maker.botch_dramatic(
                interaction=interaction,
                results=results,
                sux=successes,
                difficulty=difficulty,
            )
        else:
            embed_response = message_maker.fail_dramatic(
                interaction=interaction,
                results=results,
                sux=successes,
                enhancement=enhancement,
                scale=scale,
                difficulty=difficulty,
            )
    

    await interaction.response.send_message(embed=embed_response)
        
        
@client.slash_command(name="narrative_roll", description="Rolls a number of dice, adds in the enhancement and scale modifiers, then subtracts difficulty.")
async def narrative_roll(
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
    successes = scion_dice.count_narrative_successes(results, exploded_results)
    botched = scion_dice.check_botch(results, exploded_results, successes)
    successes -= difficulty
    message_maker = embed_message_maker.MessageMaker(hero_type=hero_type)
    if successes > 0:
        embed_response = message_maker.sucess_narrative(
            interaction=interaction,
            results=results,
            exploded_results=exploded_results,
            sux=successes,
            enhancement=enhancement,
            scale=scale,
            difficulty=difficulty,
        )
    else:
        if botched:
            embed_response = message_maker.botch_dramatic(
                interaction=interaction,
                results=results,
                sux=successes,
                difficulty=difficulty,
            )
        else:
            embed_response = message_maker.fail_dramatic(
                interaction=interaction,
                results=results,
                sux=successes,
                enhancement=enhancement,
                scale=scale,
                difficulty=difficulty,
            )
    

    await interaction.response.send_message(embed=embed_response)
    
@client.slash_command(name="initiative_roll", description="Rolls a number of dice, adds in the enhancement and scale modifiers and generates slots.")
async def initiative_roll(
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
        choices=[0, 1, 2, 3, 4, 5, 6]
    ),
    again: int = 10,
):
    tn = 8 if hero_type in {"Origin", "Hero"} else 7

    scion_dice = dice.ScionDice(
        dice_pool=dice_pool,
        enhancement=enhancement,
        hero_type=hero_type,
        scale=scale,
        difficulty=0,
        tn=tn,
        again=again,
    )

    results = scion_dice.roll()
    exploded_results = scion_dice.check_explode(results)
    successes = scion_dice.count_successes(results, exploded_results)
    botched = scion_dice.check_botch(results, exploded_results, successes)
    message_maker = embed_message_maker.MessageMaker(hero_type=hero_type)
    
    bonuses = f"Enhancement Bonus: {enhancement}\nScale Bonus: {scaleByFactor.dramatic_scale(scale)}"
    
    embed_response = message_maker.initiative(
            interaction=interaction,
            results=results,
            bonuses=bonuses,
            initiative=successes
        )
    await interaction.response.send_message(embed=embed_response)
    
@client.slash_command(name="attack_antagonist", description="For use when attacking an antagonist.  Antagonists have set defense values and do not roll defense dice, or get defense stunts.")
async def attack_antagonist(
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
        choices=[0, 1, 2, 3, 4, 5, 6]
    ),
    difficulty: int = 1,
    again: int = 10,
    defense: int = nextcord.SlashOption(
        name="defense",
        description="The defense value of the antagonist being attacked.",
        required=True
    )
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
    scion_dice.set_difficulty(defense)
    results = scion_dice.roll()
    exploded_results = scion_dice.check_explode(results)
    successes = scion_dice.count_successes(results, exploded_results)
    botched = scion_dice.check_botch(results, exploded_results, successes)
    successes -= defense
    message_maker = embed_message_maker.MessageMaker(hero_type=hero_type)
    if successes > 0:
        embed_response = message_maker.attack(
            interaction=interaction,
            results=results,
            sux=successes,
            success="success",
            bonuses=f"Enhancement Bonus: +{enhancement}\nScale Bonus: +{scaleByFactor.dramatic_scale(scale)}extra successes",
            defense=defense
        )
    else:
        if botched:
            embed_response = message_maker.attack(
                interaction=interaction,
                results=results,
                sux=successes,
                success="botch",
                bonuses="No bonuses applied",
                defense=defense
            )
        else:
            embed_response = message_maker.attack(
                interaction=interaction,
                results=results,
                sux=successes,
                success="fail",
                bonuses=f"Enhancement Bonus: +{enhancement}\nScale Bonus: +{scaleByFactor.dramatic_scale(scale)}extra successes",
                defense=defense
            )
    await interaction.response.send_message(embed=embed_response)    
@client.slash_command(
    name="attack_player",
    description="For use when attacking a player. The attacker provides attack info; the defender chooses defense."
)
async def attack_player(
    interaction: nextcord.Interaction,
    antagonist_name: str,
    character_name: str,
    player: nextcord.Member,
    attacker_dice_pool: int,
    enhancement: int,
    attacker_hero_type: str = nextcord.SlashOption(
        name="hero_type",
        description="Choose the antagonist's level of power",
        choices=["Origin", "Hero", "Demigod", "God"],
    ),
    attack_type: str = nextcord.SlashOption(
        name="attack_type",
        description="Choose the attack type",
        choices=["Melee", "Ranged"],
    ),
    attack_cost: int = 1,
    scale: int = nextcord.SlashOption(
        name="scale",
        description="Choose the difference in scale for the action",
        choices=[0, 1, 2, 3, 4, 5, 6],
    ),
):
    attack_state = {
        "attacker_name": antagonist_name,
        "target_name": character_name,
        "target_id": player.id,
        "attacker_dice_pool": attacker_dice_pool,
        "attacker_hero_type": attacker_hero_type,
        "attack_type": attack_type,
        "attack_cost": attack_cost,
        "attack_scale": scale,
        "enhancement": enhancement,
        "status": "Collecting Defense type",
    }

    await reactive_defense.start_defense(interaction, player, attack_state)
    
    
@client.slash_command(name="help", description="Provides information about the bot and its commands.")
async def help_command(interaction: nextcord.Interaction):
    embed_response = nextcord.Embed(
        color=0x1a1aff,
        title="Scion Dice Roller Bot Help",
        description="This bot helps you roll dice for Scion RPG, applying enhancements and scale modifiers.",
    )
    embed_response.add_field(
        name="/dramatic_roll",
        value="Rolls a number of dice, adds in the enhancement and scale modifiers, then subtracts difficulty.",
        inline=False,
    )
    embed_response.add_field(
        name="/narrative_roll",
        value="Rolls a number of dice, adds in the enhancement and scale modifiers, then subtracts difficulty.",
        inline=False,
    )
    embed_response.add_field(
        name="/initiative_roll",
        value="Rolls a number of dice, adds in the enhancement and scale modifiers and generates initiative slots.",
        inline=False,
    )
    embed_response.set_footer(text="For more information, please refer to the Scion RPG rulebook 1 Origin.")
    
    await interaction.response.send_message(embed=embed_response)

client.run(SECRET_KEY)