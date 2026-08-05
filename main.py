try:
    import audioop  # type: ignore
except ModuleNotFoundError:
    import audioop_lts as audioop  # type: ignore

import nextcord
from nextcord.ext import commands
import traceback

from cogs import scaleByFactor
from settings import SECRET_KEY as SECRET_KEY
from settings import TESTING_SERVER as testingServerID
from settings import REACTIVE_DEFENSE_LOG_CHANNEL as reactiveDefenseLogChannel
from cogs.reactive_json import _read_state, _delete_state, _set_status
import cogs.dice as dice
import cogs.embed_message_maker as embed_message_maker
import cogs.reactive_defense as reactive_defense


intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True


client = commands.Bot(intents=intents)

HERO_LEVEL_CHOICES = ["Origin", "Hero", "Demigod", "God", "God Feat of Scale"]
SCALE_CHOICES = [0, 1, 2, 3, 4, 5, 6]
HERO_TYPE_DESCRIPTION = "Choose the hero type, or antagonist power level"


def hero_level_option(description: str = HERO_TYPE_DESCRIPTION):
    return nextcord.SlashOption(
        name="hero_type",
        description=description,
        choices=HERO_LEVEL_CHOICES,
    )


def scale_option():
    return nextcord.SlashOption(
        name="scale",
        description="Choose the difference in scale for the action",
        choices=SCALE_CHOICES,
    )


def get_tn(hero_type: str) -> int:
    if hero_type in {"Origin", "Hero"}:
        return 8
    elif hero_type in {"Demigod", "God"}:
        return 7
    elif hero_type == "God Feat of Scale":
        return 6
    else:
        raise ValueError(f"Invalid hero type: {hero_type}")


async def _send_debug_channel_message(message: str):
    if not reactiveDefenseLogChannel:
        return
    try:
        channel_id = int(reactiveDefenseLogChannel)
    except (TypeError, ValueError):
        return

    channel = client.get_channel(channel_id)
    if channel is None:
        try:
            channel = await client.fetch_channel(channel_id)
        except Exception:
            return

    try:
        await channel.send(message[:1900])
    except Exception:
        return

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
        await _send_debug_channel_message(
            f"[startup] Synced slash commands to guild: {guild.name} ({guild.id})"
        )
    except Exception as exc:
        print(f"Failed to sync slash commands for guild {guild.name} ({guild.id}): {exc}")
        await _send_debug_channel_message(
            "\n".join(
                [
                    "[startup_error] command sync failed",
                    f"guild={guild.name} ({guild.id})",
                    f"error={exc}",
                ]
            )
        )


@client.event
async def on_application_command_error(interaction: nextcord.Interaction, error: Exception):
    command_name = "unknown"
    try:
        command_name = interaction.application_command.qualified_name
    except Exception:
        pass

    trace = traceback.format_exc()
    await _send_debug_channel_message(
        "\n".join(
            [
                "[slash_error]",
                f"command={command_name}",
                f"user={interaction.user}",
                f"error={error}",
                f"trace={trace[:1400]}",
            ]
        )
    )

    try:
        if not interaction.response.is_done():
            await interaction.response.send_message("Something went wrong while processing this command.", ephemeral=True)
    except Exception:
        pass

@client.slash_command(name="dramatic_roll", description="Rolls a number of dice, adds in the enhancement and scale modifiers, then subtracts difficulty.")
async def dramatic_roll(
    interaction: nextcord.Interaction,
    dice_pool: int,
    enhancement: int,
    hero_type: str = hero_level_option(),
    scale: int = scale_option(),
    difficulty: int = 1,
    again: int = 10,
):
    tn = get_tn(hero_type)

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
                exploded_results=exploded_results,
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
    hero_type: str = hero_level_option(),
    scale: int = scale_option(),
    difficulty: int = 1,
    again: int = 10,
):
    tn = get_tn(hero_type)

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
                exploded_results=exploded_results,
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
    hero_type: str = hero_level_option(),
    scale: int = scale_option(),
    again: int = 10,
):
    tn = get_tn(hero_type)

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
            exploded_results=exploded_results,
            bonuses=bonuses,
            initiative=successes
        )
    await interaction.response.send_message(embed=embed_response)
    
@client.slash_command(name="attack_antagonist", description="For use when attacking an antagonist.")
async def attack_antagonist(
    interaction: nextcord.Interaction,
    dice_pool: int,
    enhancement: int,
    defense: int = nextcord.SlashOption(
        name="defense",
        description="The defense value of the antagonist being attacked.",
        required=True
    ),
    hero_type: str = hero_level_option(),
    scale: int = scale_option(),
    again: int = 10,
):
    tn = get_tn(hero_type)

    scion_dice = dice.ScionDice(
        dice_pool=dice_pool,
        enhancement=enhancement,
        hero_type=hero_type,
        scale=scale,
        difficulty=defense,
        tn=tn,
        again=again,
    )
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
            exploded_results=exploded_results,
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
                exploded_results=exploded_results,
                sux=successes,
                success="botch",
                bonuses="No bonuses applied",
                defense=defense
            )
        else:
            embed_response = message_maker.attack(
                interaction=interaction,
                results=results,
                exploded_results = exploded_results,
                sux=successes,
                success="failure",
                bonuses=f"Enhancement Bonus: +{enhancement}\nScale Bonus: +{scaleByFactor.dramatic_scale(scale)}extra successes",
                defense=defense
            )
    await interaction.response.send_message(embed=embed_response)


@client.slash_command(name="attack_player",  description="For use when attacking a player.", guild_ids=[int(testingServerID)]
)
async def attack_player(
    interaction: nextcord.Interaction,
    antagonist_name: str,
    character_name: str,
    player: nextcord.Member,
    attacker_dice_pool: int,
    enhancement: int,
    rollaway_cost: int = nextcord.SlashOption(
        name="rollaway_cost",
        description="Enter the roll away cost (attacker Composure or Defense)",
        required=True,
    ),
    attacker_hero_type: str = hero_level_option("Choose the antagonist's level of power"),
    attack_type: str = nextcord.SlashOption(
        name="attack_type",
        description="Choose the attack type",
        choices=["Melee", "Ranged"],
    ),
    scale: int = scale_option(),
    again: int = 10,
):
    tn = get_tn(attacker_hero_type)
    attack_params = {
        "dice_pool": attacker_dice_pool,
        "enhancement": enhancement,
        "hero_type": attacker_hero_type,
        "scale": scale,
        "difficulty": 0,
        "tn": tn,
        "again": again,
    }

    state_id = await reactive_defense.start_defense(
        interaction,
        antagonist_name,
        character_name,
        player,
        attack_params,
        attack_type,
        rollaway_cost,
    )
    await _send_debug_channel_message(
        f"[attack_player] created reactive defense state: {state_id}"
    )


@client.slash_command(
    name="resolve_player_attack",
    description="Resolve a queued player attack after defender finalizes their defense.",
    guild_ids=[int(testingServerID)],
)
async def resolve_player_attack(
    interaction: nextcord.Interaction,
    state_id: str = nextcord.SlashOption(
        name="state_id",
        description="Reactive defense state id to resolve",
        required=True,
    ),
):
    state = _read_state(state_id)
    if not state:
        await interaction.response.send_message("No state found for that ID.", ephemeral=True)
        return

    status = state.get("status")
    if status != "defense_ready":
        await interaction.response.send_message(
            f"State is not ready yet (current status: {status}).",
            ephemeral=True,
        )
        return

    attack = state.get("attack") or {}
    attack_params = attack.get("attack_params", {})
    if not attack_params:
        await interaction.response.send_message("Attack data missing from state.", ephemeral=True)
        return

    scion_dice = dice.ScionDice(
        dice_pool=int(attack_params.get("dice_pool", 0) or 0),
        enhancement=int(attack_params.get("enhancement", 0) or 0),
        hero_type=attack_params.get("hero_type", "Hero"),
        scale=int(attack_params.get("scale", 0) or 0),
        difficulty=0,
        tn=int(attack_params.get("tn", 8) or 8),
        again=int(attack_params.get("again", 10) or 10),
    )
    results = scion_dice.roll()
    exploded_results = scion_dice.check_explode(results)
    attack_successes = scion_dice.count_successes(results, exploded_results)
    botched = scion_dice.check_botch(results, exploded_results, attack_successes)

    defense_successes = int(state.get("defense_roll", {}).get("successes", 0) or 0)
    context = state.get("context", "reflexive")
    stunt_choice = state.get("stunt_choice")
    defense_spent = int(state.get("defense_spent", 0) or 0)
    if context == "full_defense":
        defense_spent = int(state.get("manual_defense", 0) or 0)

    armor = state.get("armor", {})
    soft = int(armor.get("soft", 0) or 0)
    hard = int(armor.get("hard", 0) or 0)
    hard += int(state.get("cover_hard_armor", 0) or 0)
    rollaway_cost = int(attack.get("attack_cost", 0) or 0)

    remaining = attack_successes
    if botched:
        result_type = "botch"
    elif stunt_choice == "roll_away":
        if defense_successes >= rollaway_cost:
            remaining = 0
            result_type = "success"
        else:
            remaining = max(0, attack_successes - rollaway_cost)
            result_type = "failure" if remaining == 0 else "success"
    else:
        remaining = max(0, attack_successes - defense_spent)
        if remaining > 0:
            remaining = max(0, remaining - hard)
            remaining = max(0, remaining - soft)
        result_type = "success" if remaining > 0 else "failure"

    message_maker = embed_message_maker.MessageMaker(hero_type=attack_params.get("hero_type", "Hero"))
    if botched:
        embed_response = message_maker.attack(
            interaction=interaction,
            results=results,
            exploded_results=exploded_results,
            sux=attack_successes,
            success="botch",
            bonuses="No bonuses applied",
            defense=defense_spent,
        )
    elif result_type == "success":
        embed_response = message_maker.attack(
            interaction=interaction,
            results=results,
            exploded_results=exploded_results,
            sux=remaining,
            success="success",
            bonuses=f"Enhancement Bonus: +{attack_params.get('enhancement', 0)}\nScale Bonus: +{attack_params.get('scale', 0)}",
            defense=defense_spent,
        )
    else:
        embed_response = message_maker.attack(
            interaction=interaction,
            results=results,
            exploded_results=exploded_results,
            sux=0,
            success="failure",
            bonuses=f"Enhancement Bonus: +{attack_params.get('enhancement', 0)}\nScale Bonus: +{attack_params.get('scale', 0)}",
            defense=defense_spent,
        )

    channel_id = attack.get("channel_id")
    channel = client.get_channel(channel_id) if channel_id else interaction.channel
    if channel:
        await channel.send(embed=embed_response)
        await interaction.response.send_message("Attack resolved and posted.", ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed_response)

    _set_status(state_id, "attack_resolved")
    _delete_state(state_id)
    

@client.slash_command(name="help", description="Provides information about the bot and its commands.")
async def hep_command(interaction):
    message_maker = embed_message_maker.MessageMaker(hero_type="Origin")
    embed_response = message_maker.help_embed()
    
    await interaction.response.send_message(embed=embed_response, ephemeral=True)

client.run(SECRET_KEY)