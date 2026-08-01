import random
import nextcord

class MessageMaker(self):
    def __init__(self):
        self.dice_to_9 ={"one": "<:rolled1:1002256566717784074>", "two":"<:rolled2:1002256636066418818>", "three":"<:rolled3:1002256664692535407>", "four": "<:rolled4:1002256500607156264> ", "five": "<:rolled5:1002263017708343336> ", "six":"<:rolled6:1002263045034229870> ", "seven-bad": "<:rolled7fail:1533221453758202046 ", "seven-good": "<:rolled7:1002263065963802704> ", "eight": "<:rolled8:1002263085597343874> ", "nine": "<:rolled9:1002263106682110013> ", "ten": "<:rolled10:1002264540924358768> "}
        self.dice_10=["<:kami:1533221773720686714>", "<:Manitou:1533221860932718672>", "<:aesir:1533221551481032714>", "<:annuna:1533221575594217583>", "<:apu:1533221601418412274>", "<:atua:1533221625321754634>", "<:balahala:1533221651078975698>", "<:bogovi:1533221675146019059>", "<:devas:1533221705982546204>", "<:ilhm:1533221733358632980>", "<:kuh:1533221807736492072>", "<:loa:1533221833862676762>", "<:nemetondevos:1533221895523274893>", "<:netjer:1533221921695600650>", "<:orisha:1533221957506568212>", "<:palas:1533222023084380320>", "<:shen:1533222050884358285>", "<:tengri:1533222101329121320>", "<:teotl:1533222133696565531>", "<:theoi:1533222166370320545>", "<tuatha:1533222200398708777>", "<:yazata:1533222227028480134>, <:zemi:1533222276852617376>"]
        self.link_footer = "Support Like A Hoss Solutions"
        self.footer_text = "Your support matters | [Patreon](https://www.patreon.com/LikeAHoss) |  [Ko-fi](https://ko-fi.com/Like_a_Hoss)"
        self.true_footer = "If you enjoy this Bot please consider donnating to encourage further development."
        self.link_social = "https://ko-fi.com/Like_a_Hoss"
        self.sucess_message = ["You rolled well, good job!", "Nice roll, you got this!", "You rolled well, keep it up!", "You rolled well, good job!", "Nice roll, you got this!", "You rolled well, great work!", "Feel free to praise me for this roll, I deserve it!", "You rolled well, good job!", "Nice roll, you got this!", "You rolled well, keep it up!", "You rolled well, good job!", "Nice roll, you got this!", "You rolled well, great work!", "Feel free to praise me for this roll, I deserve it!"]
        self.fail_message = ["You rolled poorly, better luck next time!", "Don't blame me for your bad luck!", "Have you considered that maybe you just suck at this?", "You rolled poorly, better luck next time!", "You rolled poorly, better luck next time!", "Don't blame me for your bad luck!", "Have you considered that maybe you just suck at this?",  "Don't blame me for your bad luck!", "Have you considered that maybe you just suck at this?", "<:sweatdrop: 853663350939844618>"]
        self.
    
    def diceReader(self, results):
        message = " "
        for dice in results:
            if dice == 1:
                message += self.dice_to_9["one"]
                message += " "
            if dice == 2:
                message += self.dice_to_9["two"]
                message += " "
            if dice == 3:
                message += self.dice_to_9["three"]
                message += " "
            if dice == 4:
                message += self.dice_to_9["four"]
                message += " "
            if dice == 5:
                message += self.dice_to_9["five"]
                message += " "
            if dice == 6:
                message += self.dice_to_9["six"]
                message += " "
            if dice == 7:
                if self.hero_type == "God" or self.hero_type == "Demigod":
                    message += self.dice_to_9["seven-good"]
                    message += " "
                else:
                    message += self.dice_to_9["seven-bad"]
                    message += " "
            if dice == 8:
                message += self.dice_to_9["eight"]
                message += " "
            if dice == 9:
                message += self.dice_to_9["nine"]
                message += " "
            if dice == 10:
                message += self.dice_10[random.randint(0, len(self.dice_10) - 1)]
                message += " "
        return message
    
    def sucess_dramatic(self, interaction:nextcord.Interaction, results, exploded_results, sux, enhancement, scale, difficulty):
            dice = self.diceReader(results)
            exploded_dice = self.diceReader(exploded_results)
            embed_response = nextcord.Embed(color=0x00ff55,title="SUCCESS", url = self.link_social, description="rolled dice: " + dice + "\n" + "exploded dice: " + exploded_dice)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name="Successes", value=f"You had {sux} successes",inline=True)
            embed_response.add_field(name="success message", value=f"{random.choice(self.sucess_message)}", inline=False)
            embed_response.add_field(name="difficulty", value=f"difficulty of {difficulty}", inline=True)
            embed_response.add_field(name="enhancement", value=f"enhancement of {enhancement}", inline=True)
            embed_response.add_field(name="scale", value=f"scale factor of {scale}", inline=True)
            embed_response.add_field(name = self.link_footer, value=self.footer_text)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
            
    
    def fail_dramatic(self, interaction:nextcord.Interaction, results, sux, bonuses, difficulty):
        dice = self.diceReader(results)
        embed_response = nextcord.Embed(color=0xcc0000,title="Fail", url = self.link_social, description=dice)
        embed_response.set_author(name= interaction.user.name)
        embed_response.add_field(name="Failure", value="You Can't Blame me for this!",inline=False)
        embed_response.add_field(name="Successes", value=f"you had {sux} successes", inline=True)
        embed_response.add_field(name="difficulty", value=f"difficulty of {difficulty}", inline=True)
        embed_response.add_field(name="bonuses", value=bonuses, inline=False)
        embed_response.add_field(name = self.link_footer, value=self.footer_text)
        embed_response.set_footer(text = self.true_footer)
        return embed_response
    
    def botch_dramatic(self, interaction:nextcord.Interaction, results, sux, difficulty):
        dice = self.diceReader(results)
        embed_response = nextcord.Embed(color=0xcc6600,title="Botch", url = self.link_social, description=dice)
        embed_response.set_author(name= interaction.user.name)
        embed_response.add_field(name="Botched", value="I can't help it if you suck at this",inline=False)
        embed_response.add_field(name="Successes", value=f"you had {sux} successes", inline=True)
        embed_response.add_field(name="difficulty", value=f"difficulty of {difficulty}", inline=True)
        embed_response.add_field(name = self.link_footer, value=self.footer_text)
        embed_response.set_footer(text = self.true_footer)
        return embed_response

    def initative(self, interaction:nextcord.Interaction, results, bonuses, initative):
        #emoji = random.choice(self.sucess_emoji)
        dice = self.diceReader(results)
        embed_response = nextcord.Embed(color=0x1a1aff,title="Initative", url = self.link_social, description=dice)
        embed_response.set_author(name= interaction.user.name)
        embed_response.add_field(name="Initative", value=f"Your Initative is {initative}",inline=False)
        embed_response.add_field(name="bonuses", value=bonuses, inline=False)
        embed_response.add_field(name = self.link_footer, value=self.footer_text)
        embed_response.set_footer(text = self.true_footer)
#        embed_response.add_field(name="display", value= emoji, inline=False)
        return embed_response    
    
    def attack(self, interaction:nextcord.Interaction, results, sux, success, bonuses, defense):
        if success == "success":
            #emoji = random.choice(self.sucess_emoji)
            dice = self.diceReader(results)
            embed_response = nextcord.Embed(color=0x00ff55,title="SUCCESS", url = self.link_social, description=dice)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name="Successes", value=f"You had {sux} against defense {defense}",inline=False)
            embed_response.add_field(name="bonuses", value=bonuses, inline=False)
    #        embed_response.add_field(name="display", value= emoji, inline=False)
            embed_response.add_field(name = self.link_footer, value=self.footer_text)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
        elif success == "failure":
            #emoji = random.choice(self.fail_emoji)
            dice = self.diceReader(results)
            embed_response = nextcord.Embed(color=0xcc0000,title="FAIL", url = self.link_social, description=dice)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name="Fail", value=f"You had {sux} against defense {defense}",inline=False)
            embed_response.add_field(name="bonuses", value=bonuses, inline=False)
    #        embed_response.add_field(name="display", value= emoji, inline=False)
            embed_response.add_field(name = self.link_footer, value=self.footer_text)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
        else:
            #emoji = random.choice(self.botch_emoji)
            dice = self.diceReader(results)
            embed_response = nextcord.Embed(color=0xcc6600, title="BOTCHED", url = self.link_social, description=dice)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name="Botch", value=f"You had {sux} against defense {defense}",inline=False)
            embed_response.add_field(name="bonuses", value=bonuses, inline=False)
    #        embed_response.add_field(name="display", value= emoji, inline=False)
            embed_response.add_field(name = self.link_footer, value=self.footer_text)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
    
    def withering_damage_msg(self, interaction:nextcord.Interaction, results, sux, soak, initative_gained):
        if sux > 0:
            #emoji = random.choice(self.sucess_emoji)
            dice = self.diceReader(results)
            embed_response = nextcord.Embed(color=0x00ff55,title="SUCESS", url = self.link_social, description=dice)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name="Successes", value=f"You dealt {sux} damage against a soak of {soak}",inline=False)
            embed_response.add_field(name="initative gained", value=initative_gained, inline=True)
   #         embed_response.add_field(name="display", value= emoji, inline=False)
            embed_response.add_field(name = self.link_footer, value=self.footer_text)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
        else:
            #emoji = random.choice(self.botch_emoji)
            dice = self.diceReader(results)
            embed_response = nextcord.Embed(color=0xcc6600,title="pillow fist", url = self.link_social, description=dice)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name="Barely touched them", value=f"You had {sux} against a soak of {soak}",inline=False)
            embed_response.add_field(name="initative gained", value=initative_gained, inline=True)
            #embed_response.add_field(name="enemy initative", value=initative)
    #        embed_response.add_field(name="display", value= emoji, inline=False)
            embed_response.add_field(name = self.link_footer, value=self.footer_text)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
    