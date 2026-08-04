import nextcord


def _get_state_embed(state: dict, title: str):
    embed = nextcord.Embed(title=title, color=0x1a1aff)
    embed.add_field(name="Attacker", value=state.get("attacker", "Unknown"), inline=True)
    embed.add_field(name="Target", value=state.get("character_name", "Unknown"), inline=True)
    embed.add_field(name="Status", value=state.get("status", "Unknown"), inline=False)

    attack = state.get("attack", {})
    attack_params = attack.get("attack_params", {})
    attack_type = attack.get("attack_type", attack_params.get("attack_type", "Unknown"))
    attack_cost = attack.get("attack_cost", attack.get("attack_cost", "Unknown"))
    embed.add_field(name="Attack Type", value=attack_type, inline=True)
    embed.add_field(name="Roll Away Cost", value=str(attack_cost), inline=True)

    roll_info = state.get("roll_info")
    if roll_info:
        embed.add_field(name="Hero Type", value=roll_info.get("hero_type", "Hero"), inline=True)
        embed.add_field(name="Scale", value=str(roll_info.get("scale", 0)), inline=True)
        embed.add_field(name="Dice Pool", value=str(roll_info.get("dice_pool", "?")), inline=True)

    defense_roll = state.get("defense_roll")
    if defense_roll:
        embed.add_field(name="Defense Successes", value=str(defense_roll.get("successes", 0)), inline=True)
        embed.add_field(name="Botch", value=str(defense_roll.get("botch", False)), inline=True)

    stunt_choice = state.get("stunt_choice")
    if stunt_choice:
        embed.add_field(name="Stunt", value=stunt_choice.replace("_", " ").title(), inline=False)

    armor = state.get("armor")
    if armor:
        embed.add_field(name="Armor", value=f"Soft: {armor.get('soft',0)}, Hard: {armor.get('hard',0)}", inline=False)

    return embed
