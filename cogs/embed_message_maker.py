import random
import nextcord

class MessageMaker():
    def __init__(self):
        self.dice ={"one": "<:rolled1:1002256566717784074>", "two":"<:rolled2:1002256636066418818>", "three":"<:rolled3:1002256664692535407>", "four": "<:rolled4:1002256500607156264> ", "five": "<:rolled5:1002263017708343336> ", "six":"<:rolled6:1002263045034229870> ", "seven": "<:rolled7:1002263065963802704> ", "eight": "<:rolled8:1002263085597343874> ", "nine": "<:rolled9:1002263106682110013> ", "ten": "<:rolled10:1002264540924358768> "}
        self.sucess_emoji = ["<a:shantaebellydance:988687326865678406>", "<a:642799476159021076:898518266127986699>", "<:makismug:874651051888902154>", "<a:spinme:880561162184458311>", "<:ClaraSmile:680219668010500099>"]
        self.fail_emoji = ["<a:nervous:853663350939844618>", "<:bonerkira:925625435566534656>", "<:StarfireRaven:827046653738614824>", "<:GAH:380834608348135424>", "<:Edward_endless_barrel:346650686085398530>"]
        self.botch_emoji = ["<:laugh:927812319394803762>", "<a:sadcry:885214718711709756>", "<:ventiheh:885209971971751946>", "<a:bounce:895362491218034809>", "<:Tensaided_angry:715947045449629748> "]
        self.link_footer = "Support Like A Hoss Solutions"
        self.footer_text = "Your support matters | [Patreon](https://www.patreon.com/LikeAHoss) |  [Ko-fi](https://ko-fi.com/Like_a_Hoss)"
        self.true_footer = "If you enjoy this Bot please consider donnating to encourage further development."
        self.link_social = "https://ko-fi.com/Like_a_Hoss"
    
    def diceReader(self, results):
        message = " "
        for dice in results:
            if dice == 1:
                message += self.dice["one"]
                message += " "
            if dice == 2:
                message += self.dice["two"]
                message += " "
            if dice == 3:
                message += self.dice["three"]
                message += " "
            if dice == 4:
                message += self.dice["four"]
                message += " "
            if dice == 5:
                message += self.dice["five"]
                message += " "
            if dice == 6:
                message += self.dice["six"]
                message += " "
            if dice == 7:
                message += self.dice["seven"]
                message += " "
            if dice == 8:
                message += self.dice["eight"]
                message += " "
            if dice == 9:
                message += self.dice["nine"]
                message += " "
            if dice == 10:
                message += self.dice["ten"]
                message += " "
        return message
    
    def sucess(self, interaction:nextcord.Interaction, results, sux, bonuses, difficulty):
            dice = self.diceReader(results)
            embed_response = nextcord.Embed(color=0x00ff55,title="SUCCESS", url = self.link_social, description=dice)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name="Successes", value=f"You had {sux} successes",inline=True)
            embed_response.add_field(name="difficulty", value=f"difficulty of {difficulty}", inline=True)
            embed_response.add_field(name="bonuses", value=bonuses, inline=False)
            embed_response.add_field(name = self.link_footer, value=self.footer_text)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
            
    
    def fail(self, interaction:nextcord.Interaction, results, sux, bonuses, difficulty):
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
    
    def botch(self, interaction:nextcord.Interaction, results, sux, bonuses, difficulty):
        dice = self.diceReader(results)
        embed_response = nextcord.Embed(color=0xcc6600,title="Botch", url = self.link_social, description=dice)
        embed_response.set_author(name= interaction.user.name)
        embed_response.add_field(name="Botched", value="I can't help it if you suck at this",inline=False)
        embed_response.add_field(name="Successes", value=f"you had {sux} successes", inline=True)
        embed_response.add_field(name="difficulty", value=f"difficulty of {difficulty}", inline=True)
        embed_response.add_field(name="bonuses", value=bonuses, inline=False)
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
    