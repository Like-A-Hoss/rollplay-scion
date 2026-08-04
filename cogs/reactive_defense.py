import json
import re
import uuid
import nextcord
from nextcord import Interaction

import cogs.dice as dice
import cogs.embed_message_maker as embed_message_maker
from .reactive_json import _read_state, _write_state, _delete_state, _set_status
from .reactive_embeds import _get_state_embed


class HeroTypeSelect(nextcord.ui.Select):
    def __init__(self, state_id: str):
        options = [
            nextcord.SelectOption(label="Origin", value="Origin"),
            nextcord.SelectOption(label="Hero", value="Hero"),
            nextcord.SelectOption(label="Demigod", value="Demigod"),
            nextcord.SelectOption(label="God", value="God"),
        ]
        super().__init__(placeholder="Choose Hero Type", min_values=1, max_values=1, options=options, custom_id=f"hero_type_{state_id}")
        self.state_id = state_id

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        roll_info = data.get("roll_info", {})
        roll_info["hero_type"] = self.values[0]
        data["roll_info"] = roll_info
        _write_state(self.state_id, data)
        await interaction.response.edit_message(embed=_get_state_embed(data, "Reflexive Defense Configuration"), view=ReflexiveConfigView(self.state_id))


class ScaleSelect(nextcord.ui.Select):
    def __init__(self, state_id: str):
        options = [nextcord.SelectOption(label=str(i), value=str(i)) for i in range(7)]
        super().__init__(placeholder="Choose Scale", min_values=1, max_values=1, options=options, custom_id=f"scale_{state_id}")
        self.state_id = state_id

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        roll_info = data.get("roll_info", {})
        roll_info["scale"] = int(self.values[0])
        data["roll_info"] = roll_info
        _write_state(self.state_id, data)
        await interaction.response.edit_message(embed=_get_state_embed(data, "Reflexive Defense Configuration"), view=ReflexiveConfigView(self.state_id))


class ReflexiveRollModal(nextcord.ui.Modal):
    def __init__(self, state_id: str):
        super().__init__("Reflexive Defense Roll")
        self.state_id = state_id
        self.add_item(nextcord.ui.TextInput(label="Dice pool (int)", placeholder="e.g. 3", required=True))
        self.add_item(nextcord.ui.TextInput(label="Enhancement (int)", placeholder="e.g. 0", required=True))
        self.add_item(nextcord.ui.TextInput(label="Again (int)", placeholder="10", required=False))

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        roll_info = data.get("roll_info", {})
        try:
            dice_pool = int(self.children[0].value)
        except Exception:
            await interaction.response.send_message("Invalid dice pool", ephemeral=True)
            return
        try:
            enhancement = int(self.children[1].value)
        except Exception:
            enhancement = 0
        try:
            again = int(self.children[2].value) if self.children[2].value else 10
        except Exception:
            again = 10

        hero_type = roll_info.get("hero_type", "Hero")
        scale = roll_info.get("scale", 0)
        roll_info.update({"dice_pool": dice_pool, "enhancement": enhancement, "again": again, "hero_type": hero_type, "scale": scale})
        data["roll_info"] = roll_info

        tn = 8 if hero_type in {"Origin", "Hero"} else 7
        scion = dice.ScionDice(
            dice_pool=dice_pool,
            enhancement=enhancement,
            hero_type=hero_type,
            scale=scale,
            difficulty=0,
            tn=tn,
            again=again,
        )
        results = scion.roll()
        exploded = scion.check_explode(results)
        successes = scion.count_successes(results, exploded)
        botch = scion.check_botch(results, exploded, successes)

        data["defense_roll"] = {
            "dice_pool": dice_pool,
            "enhancement": enhancement,
            "hero_type": hero_type,
            "scale": scale,
            "again": again,
            "results": results,
            "exploded": exploded,
            "successes": successes,
            "botch": botch,
        }
        data["stunt_choice"] = None
        data["defense_spent"] = None
        _write_state(self.state_id, data)
        _set_status(self.state_id, "collecting_reflexive_stunt")

        await interaction.response.edit_message(embed=_get_state_embed(data, "Choose a Reflexive Stunt"), view=ReflexiveStuntView(self.state_id))


class DefenseSpendModal(nextcord.ui.Modal):
    def __init__(self, state_id: str, max_successes: int):
        super().__init__("Spend Defense Successes")
        self.state_id = state_id
        self.max_successes = max_successes
        self.add_item(nextcord.ui.TextInput(label=f"Successes to spend on defense (0-{max_successes})", required=True))

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        try:
            spend = int(self.children[0].value)
        except Exception:
            await interaction.response.send_message("Invalid number", ephemeral=True)
            return
        if spend < 0 or spend > self.max_successes:
            await interaction.response.send_message(f"Enter a value between 0 and {self.max_successes}", ephemeral=True)
            return

        data["stunt_choice"] = "defense"
        data["defense_spent"] = spend
        _write_state(self.state_id, data)
        _set_status(self.state_id, "collecting_armor_values")

        await interaction.response.edit_message(embed=_get_state_embed(data, "Set Armor and Resolve"), view=ArmorResolveView(self.state_id))


class DiveCoverModal(nextcord.ui.Modal):
    def __init__(self, state_id: str, max_successes: int):
        super().__init__("Dive for Cover")
        self.state_id = state_id
        self.max_successes = max_successes
        self.add_item(nextcord.ui.TextInput(label="Cover type (expendable/light/heavy/full)", required=True))
        self.add_item(nextcord.ui.TextInput(label=f"Successes to keep after cover (0-{max_successes - 1})", required=True))
        self.add_item(nextcord.ui.TextInput(label="Cover damage already taken (optional)", required=False))

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        if data.get("attack", {}).get("attack_type", "Melee") != "Ranged":
            await interaction.response.send_message("Dive for cover is only available against ranged attacks.", ephemeral=True)
            return

        try:
            cover_type = self.children[0].value.strip().lower()
            if cover_type not in {"expendable", "light", "heavy", "full"}:
                raise ValueError
        except Exception:
            await interaction.response.send_message("Enter a valid cover type: expendable, light, heavy, or full.", ephemeral=True)
            return

        try:
            keep = int(self.children[1].value)
        except Exception:
            await interaction.response.send_message("Invalid defense amount", ephemeral=True)
            return

        if keep < 0 or keep > self.max_successes - 1:
            await interaction.response.send_message(f"Enter a defense amount between 0 and {max(0, self.max_successes - 1)}", ephemeral=True)
            return

        try:
            damage_taken = int(self.children[2].value) if self.children[2].value else 0
        except Exception:
            damage_taken = 0

        cover_values = {"expendable": 1, "light": 4, "heavy": 10, "full": 10}
        data["stunt_choice"] = "dive_for_cover"
        data["defense_spent"] = keep
        data["cover_type"] = cover_type
        data["cover_hard_armor"] = cover_values[cover_type]
        data["cover_damage_taken"] = damage_taken
        _write_state(self.state_id, data)
        _set_status(self.state_id, "collecting_armor_values")

        await interaction.response.edit_message(embed=_get_state_embed(data, "Set Armor and Resolve"), view=ArmorResolveView(self.state_id))


class RollAwayModal(nextcord.ui.Modal):
    def __init__(self, state_id: str):
        super().__init__("Roll Away")
        self.state_id = state_id
        self.add_item(nextcord.ui.TextInput(label="Type YES to confirm Roll Away", required=True))

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        if self.children[0].value.strip().lower() != "yes":
            await interaction.response.send_message("Roll Away cancelled.", ephemeral=True)
            return

        data["stunt_choice"] = "roll_away"
        data["defense_spent"] = 0
        _write_state(self.state_id, data)
        _set_status(self.state_id, "collecting_armor_values")

        await interaction.response.edit_message(embed=_get_state_embed(data, "Set Armor and Resolve"), view=ArmorResolveView(self.state_id))


class ArmorModal(nextcord.ui.Modal):
    def __init__(self, state_id: str):
        super().__init__("Armor Values")
        self.state_id = state_id
        self.add_item(nextcord.ui.TextInput(label="Soft armor (int)", required=False))
        self.add_item(nextcord.ui.TextInput(label="Hard armor (int)", required=False))

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        try:
            soft = int(self.children[0].value) if self.children[0].value else 0
        except Exception:
            soft = 0
        try:
            hard = int(self.children[1].value) if self.children[1].value else 0
        except Exception:
            hard = 0

        data["armor"] = {"soft": soft, "hard": hard}
        _write_state(self.state_id, data)
        _set_status(self.state_id, "ready_to_resolve")

        await interaction.response.edit_message(embed=_get_state_embed(data, "Ready to Resolve Attack"), view=ArmorResolveView(self.state_id))


class FullDefenseModal(nextcord.ui.Modal):
    def __init__(self, state_id: str):
        super().__init__("Full Defense Details")
        self.state_id = state_id
        self.add_item(nextcord.ui.TextInput(label="Defense value (int)", required=True))
        self.add_item(nextcord.ui.TextInput(label="Defensive stunts taken", required=False))
        self.add_item(nextcord.ui.TextInput(label="Cover damage taken (optional)", required=False))

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        try:
            defense_value = int(self.children[0].value)
        except Exception:
            await interaction.response.send_message("Invalid defense value", ephemeral=True)
            return
        stunts = self.children[1].value or ""
        try:
            cover_damage = int(self.children[2].value) if self.children[2].value else 0
        except Exception:
            cover_damage = 0

        data["context"] = "full_defense"
        data["manual_defense"] = defense_value
        data["manual_stunts"] = stunts
        data["cover_damage_taken"] = cover_damage
        _write_state(self.state_id, data)
        _set_status(self.state_id, "collecting_armor_values")

        await interaction.response.edit_message(embed=_get_state_embed(data, "Set Armor and Resolve"), view=ArmorResolveView(self.state_id))


class ReflexiveConfigView(nextcord.ui.View):
    def __init__(self, state_id: str):
        super().__init__(timeout=None)
        self.state_id = state_id
        self.add_item(HeroTypeSelect(state_id))
        self.add_item(ScaleSelect(state_id))

    @nextcord.ui.button(label="Enter Roll Info", style=nextcord.ButtonStyle.primary)
    async def enter_roll_info(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_modal(ReflexiveRollModal(self.state_id))


class ReflexiveStuntView(nextcord.ui.View):
    def __init__(self, state_id: str):
        super().__init__(timeout=None)
        self.state_id = state_id

    @nextcord.ui.button(label="Defense", style=nextcord.ButtonStyle.primary)
    async def defense(self, button: nextcord.ui.Button, interaction: Interaction):
        data = _read_state(self.state_id)
        successes = data.get("defense_roll", {}).get("successes", 0)
        await interaction.response.send_modal(DefenseSpendModal(self.state_id, successes))

    @nextcord.ui.button(label="Dive for Cover", style=nextcord.ButtonStyle.secondary)
    async def dive_for_cover(self, button: nextcord.ui.Button, interaction: Interaction):
        data = _read_state(self.state_id)
        if data.get("attack", {}).get("attack_type", "Melee") != "Ranged":
            await interaction.response.send_message("Dive for cover is only available against ranged attacks.", ephemeral=True)
            return
        successes = data.get("defense_roll", {}).get("successes", 0)
        if successes < 1:
            await interaction.response.send_message("You need at least 1 defense success to use Dive for Cover.", ephemeral=True)
            return
        await interaction.response.send_modal(DiveCoverModal(self.state_id, successes))

    @nextcord.ui.button(label="Roll Away", style=nextcord.ButtonStyle.secondary)
    async def roll_away(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_modal(RollAwayModal(self.state_id))


class FullDefenseView(nextcord.ui.View):
    def __init__(self, state_id: str):
        super().__init__(timeout=None)
        self.state_id = state_id

    @nextcord.ui.button(label="Enter Full Defense Details", style=nextcord.ButtonStyle.primary)
    async def enter_full_defense(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_modal(FullDefenseModal(self.state_id))


class ArmorResolveView(nextcord.ui.View):
    def __init__(self, state_id: str):
        super().__init__(timeout=None)
        self.state_id = state_id

    @nextcord.ui.button(label="Set Armor", style=nextcord.ButtonStyle.primary)
    async def set_armor(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_modal(ArmorModal(self.state_id))

    @nextcord.ui.button(label="Resolve Attack", style=nextcord.ButtonStyle.danger)
    async def resolve_attack(self, button: nextcord.ui.Button, interaction: Interaction):
        await _resolve_attack(interaction, self.state_id)


class DefenseChoiceView(nextcord.ui.View):
    def __init__(self, state_id: str):
        super().__init__(timeout=None)
        self.state_id = state_id

    @nextcord.ui.button(label="Reflexive Defense", style=nextcord.ButtonStyle.primary)
    async def reflexive_defense(self, button: nextcord.ui.Button, interaction: Interaction):
        _set_status(self.state_id, "collecting_reflexive_info")
        await interaction.response.edit_message(embed=_get_state_embed(_read_state(self.state_id), "Reflexive Defense Setup"), view=ReflexiveConfigView(self.state_id))

    @nextcord.ui.button(label="Full Defense", style=nextcord.ButtonStyle.secondary)
    async def full_defense(self, button: nextcord.ui.Button, interaction: Interaction):
        data = _read_state(self.state_id)
        data["context"] = "full_defense"
        _write_state(self.state_id, data)
        _set_status(self.state_id, "collecting_full_defense")
        await interaction.response.edit_message(embed=_get_state_embed(data, "Full Defense Setup"), view=FullDefenseView(self.state_id))


async def _resolve_attack(interaction: Interaction, state_id: str):
    data = _read_state(state_id)
    attack = data.get("attack") or {}
    if not attack:
        await interaction.response.send_message("Attack data missing.", ephemeral=True)
        return

    attack_params = attack.get("attack_params", {})
    scion = dice.ScionDice(
        dice_pool=attack_params.get("dice_pool", 0),
        enhancement=attack_params.get("enhancement", 0),
        hero_type=attack_params.get("hero_type", "Hero"),
        scale=attack_params.get("scale", 0),
        difficulty=0,
        tn=attack_params.get("tn", 8),
        again=attack_params.get("again", 10),
    )
    results = scion.roll()
    exploded = scion.check_explode(results)
    attack_successes = scion.count_successes(results, exploded)
    botch = scion.check_botch(results, exploded, attack_successes)

    defense_successes = data.get("defense_roll", {}).get("successes", 0)
    context = data.get("context", "reflexive")
    stunt_choice = data.get("stunt_choice")
    defense_spent = int(data.get("defense_spent", 0) or 0)
    if context == "full_defense":
        defense_spent = int(data.get("manual_defense", 0) or 0)

    armor = data.get("armor", {})
    soft = int(armor.get("soft", 0) or 0)
    hard = int(armor.get("hard", 0) or 0)
    cover_hard = int(data.get("cover_hard_armor", 0) or 0)
    hard += cover_hard

    roll_away_cost = int(attack.get("attack_cost", 0) or 0)
    remaining = attack_successes

    if botch:
        result_type = "botch"
    elif stunt_choice == "roll_away":
        if defense_successes >= roll_away_cost:
            remaining = 0
            result_type = "success"
        else:
            remaining = max(0, attack_successes - roll_away_cost)
            result_type = "failure" if remaining == 0 else "success"
    else:
        remaining = max(0, attack_successes - defense_spent)
        if remaining > 0:
            remaining = max(0, remaining - hard)
            remaining = max(0, remaining - soft)
        result_type = "success" if remaining > 0 else "failure"

    maker = embed_message_maker.MessageMaker(hero_type=attack_params.get("hero_type", "Hero"))

    if botch:
        embed = maker.attack(interaction=interaction, results=results, sux=attack_successes, success="botch", bonuses="", defense=defense_spent)
    elif result_type == "success":
        embed = maker.attack(
            interaction=interaction,
            results=results,
            sux=remaining,
            success="success",
            bonuses=f"Enhancement Bonus: +{attack_params.get('enhancement',0)}\nScale Bonus: +{attack_params.get('scale',0)}",
            defense=defense_spent,
        )
    else:
        embed = maker.attack(
            interaction=interaction,
            results=results,
            sux=0,
            success="fail",
            bonuses=f"Enhancement Bonus: +{attack_params.get('enhancement',0)}\nScale Bonus: +{attack_params.get('scale',0)}",
            defense=defense_spent,
        )

    channel_id = attack.get("channel_id")
    channel = interaction.client.get_channel(channel_id) if channel_id else interaction.channel
    if channel:
        await channel.send(embed=embed)
        await interaction.response.send_message("Attack resolved and posted.", ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed)

    _set_status(state_id, "attack_resolved")
    _delete_state(state_id)


async def start_defense(
    interaction: Interaction,
    antagonist_name: str,
    character_name: str,
    player: nextcord.Member,
    attack_params: dict | None,
    attack_type: str,
    attack_cost: int,
    scion_dice: dice.ScionDice | None = None,
):
    if attack_params is None and scion_dice is not None:
        attack_params = {
            "dice_pool": scion_dice.dice_pool,
            "enhancement": scion_dice.enhancement,
            "hero_type": scion_dice.hero_type,
            "scale": scion_dice.scale,
            "difficulty": scion_dice.difficulty,
            "tn": scion_dice.tn,
            "again": scion_dice.again,
        }

    if attack_params is None:
        attack_params = {}

    attack_params["attack_type"] = attack_type

    state_id = str(uuid.uuid4())
    data = {
        "attacker": interaction.user.name,
        "antagonist_name": antagonist_name,
        "character_name": character_name,
        "player_id": player.id,
        "status": "awaiting_defense_choice",
        "context": None,
        "attack": {
            "attack_params": attack_params,
            "attack_type": attack_type,
            "attack_cost": attack_cost,
            "channel_id": interaction.channel.id if interaction.channel else None,
        },
    }
    _write_state(state_id, data)

    embed = nextcord.Embed(title="Defensive Reaction", color=0x1a1aff)
    embed.add_field(name="Attacker", value=interaction.user.name, inline=True)
    embed.add_field(name="Target", value=character_name, inline=True)
    embed.add_field(name="Attack Type", value=attack_type, inline=True)
    embed.add_field(name="Roll Away Cost", value=str(attack_cost), inline=True)
    embed.add_field(name="Instructions", value="Choose Reflexive Defense or Full Defense to begin.", inline=False)

    view = DefenseChoiceView(state_id)

    # Defer the interaction response to avoid Discord "interaction failed" timeout
    try:
        await interaction.response.defer(ephemeral=True)
        deferred = True
    except Exception:
        deferred = False

    # Try to DM the player. If that fails (DMs closed), fall back to channel mention.
    sent_dm = False
    try:
        await player.send(embed=embed, view=view)
        sent_dm = True
    except Exception:
        sent_dm = False

    if sent_dm:
        msg = f"Sent defensive prompt to {player.display_name} via DM."
        if deferred:
            await interaction.followup.send(msg, ephemeral=True)
        else:
            try:
                await interaction.response.send_message(msg, ephemeral=True)
            except Exception:
                pass
    else:
        # Fallback: post in the channel and mention the player
        channel = interaction.channel
        if channel is None and interaction.guild is not None:
            channel = interaction.guild.system_channel

        if channel:
            await channel.send(f"{player.mention}", embed=embed, view=view)
            msg = f"Could not DM {player.display_name}; posted prompt in channel."
        else:
            msg = f"Could not deliver prompt to {player.display_name}."

        if deferred:
            await interaction.followup.send(msg, ephemeral=True)
        else:
            try:
                await interaction.response.send_message(msg, ephemeral=True)
            except Exception:
                pass
