import random

class Exalted_Dice():
    def __init__(self, dice_pool:int, willpower:bool, excelence:int, stunt:bool):
        self.dice_pool = dice_pool
        self.willpower = willpower
        self.excelence = excelence
        self.stunt = stunt
    #Set up the value modifiers
    def set_attribute(self, numb:int):
        self.dice_pool = numb
    
    def get_attribute(self):
        return self.dice_pool
    
    def set_excelence(self, numb:int):
        self.excelence = numb
    
    def get_excelence(self):
        return self.excelence

    def set_willpower(self, value:bool):
        self.willpower = value
    
    def get_willpower(self):
        return self.willpower

    def set_stunt(self, value:bool):
        self.stunt = value
    def get_stunt(self):
        return self.stunt

    def basic_roll(self):
        #Rolls the number of dice set and records them to display back
        #Sets stunt number
        stunt_value = 0
        if self.stunt == True:
            stunt_value += 2
        #else:
        #    stunt_value = 0
        #
        end_dice_pool = self.dice_pool + self.excelence + stunt_value
        #set up dice roller
        results = []
        for _ in range(end_dice_pool):
            results.append(random.randint(1,10))
        return results

    
    def roll_withering_damage(self, raw, soak):
        #
        dice_pool = raw - soak
        #set up dice roller
        if dice_pool < 1:
            dice_pool = 1
        results = []
        for _ in range(dice_pool):
            results.append(random.randint(1,10))
        return results

    """def roll_decisive_attach(self, defence ):
        if self.stunt >= 1:
            stunt_value = 2
        else:
            stunt_value = 0
        #
        dice_pool = (self.attribute + self.ability + self.excelence + stunt_value) - defence
        #set up dice roller
        if dice_pool >= 1:
            results = []
            for _ in range(dice_pool):
                results.append(random.randint(1,10))
            return results
        else:
            dice_pool = 1
            results = []
            for _ in range(dice_pool):
                results.append(random.randint(1,10))
            return results """

    def count_successes(self, results, dub:int, tn:int =7):
        successes = 0
        for die in results:
            if dub == 10:
                if die == 10:
                    successes += 2
                elif die >= tn:
                    successes += 1
            else:
                if die >= dub:
                    successes += 2
                elif die < dub and die >= tn:
                    successes += 1
        if self.willpower == True:
            successes += 1
#        if self.stunt > 1:
#            successes += 1            
        return successes

    def check_botch(self, results):
        botch = False
        for die in results:
            if die == 1:
                botch = True
        sux = self.count_successes(results)
        if sux >= 1:
            botch = False
        return botch

    def check_explode(self, results:list, value:int):
        added_dice =0
        added_results =[]
        for die in results:
            if die == value:
                added_dice += 1
        for _ in range(added_dice):
            added_die = random.randint(1,10)
            if added_die == value:
                added_dice += 1
            added_results.append(added_die)
        for die in added_results:
            results.append(die)

    def check_reroll_all(self, results:list, value:int):
        #rerolls dice until no more of that number appear.
        rerolls = []  #Creates empty list to store rerolled values.
        done = False
        for die in results:
            if die == value:
                done = False
                while done == False:
                    new_die = (random.randint(1,10))
                    if new_die != value:
                        done = True
                        rerolls.append(new_die)
        return rerolls

            
    
    def check_reroll_once(self, results:list, value:int):
        #rerolls dice of a certain value once
        rerolls = []
        for die in results:
            if die <= value:
                rerolls.append(random.randint(1,10))

