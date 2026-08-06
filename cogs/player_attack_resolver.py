import nextcord

import cogs.dice as dice
import cogs.embed_message_maker as embed_message_maker
from .reactive_json import _read_state, _delete_state, _set_status


async def resolve_player_attack_state(
    client: nextcord.Client,
    interaction: nextcord.Interaction,
    state_id: str,
) -> tuple[bool, str]:
    state = _read_state(state_id)
    if not state:
        return False, "No state found for that ID."

    status = state.get("status")
    if status != "defense_ready":
        return False, f"Defender is not ready yet (current status: {status})."

    attack = state.get("attack") or {}
    attack_params = attack.get("attack_params", {})
    if not attack_params:
        return False, "Attack data missing from state."

    scion_dice = dice.ScionDice(
        dice_pool=int(attack_params.get("dice_pool", 0) or 0),
        enhancement=int(attack_params.get("enhancement", 0) or 0),
        hero_type=attack_params.get("hero_type", "Hero"),
        scale=int(attack_params.get("scale", 0) or 0),
        difficulty=int(state.get("final_defense", 1) or 1),
        tn=int(attack_params.get("tn", 8) or 8),
        again=int(attack_params.get("again", 10) or 10),
    )

    results = scion_dice.roll()
    exploded_results = scion_dice.check_explode(results)
    attack_successes = scion_dice.count_successes(results, exploded_results)
    botched = scion_dice.check_botch(results, exploded_results, attack_successes)

    final_defense = int(state.get("final_defense", 1) or 1)
    remaining = attack_successes
    if botched:
        result_type = "botch"
    else:
        remaining -= final_defense
        if remaining > 0:
            result_type = "success"
        else:
            result_type = "failure"

    message_maker = embed_message_maker.MessageMaker(hero_type=attack_params.get("hero_type", "Hero"))
    if botched:
        embed_response = message_maker.attack_player_fail(
            character=state.get("character_name", "Unknown"),
            interaction=interaction,
            results=results,
            exploded_results=exploded_results,
            sux=attack_successes,
            success="botch",
            bonuses="No bonuses applied",
            defense=final_defense,
        )
    elif result_type == "success":
        embed_response = message_maker.attack_player_success(
            interaction=interaction,
            results=results,
            exploded_results=exploded_results,
            sux=remaining,
            success="success",
            bonuses=f"Enhancement Bonus: +{attack_params.get('enhancement', 0)}\\nScale Bonus: +{attack_params.get('scale', 0)}",
            defense=final_defense,
            stunt_choice=state.get("stunt_choice"),
            armor=state.get("armor", {}),
            character=state.get("character_name", "Unknown"),
        )
    else:
        embed_response = message_maker.attack_player_fail(
            character=state.get("character_name", "Unknown"),
            interaction=interaction,
            results=results,
            exploded_results=exploded_results,
            sux=0,
            success="failure",
            bonuses=f"Enhancement Bonus: +{attack_params.get('enhancement', 0)}\\nScale Bonus: +{attack_params.get('scale', 0)}",
            defense=final_defense,
        )

    channel_id = attack.get("channel_id")
    channel = client.get_channel(channel_id) if channel_id else interaction.channel
    if channel:
        await channel.send(embed=embed_response)
    else:
        return False, "Could not find the target channel to post the resolved attack."

    _set_status(state_id, "attack_resolved")
    _delete_state(state_id)
    return True, "Attack resolved and posted."
