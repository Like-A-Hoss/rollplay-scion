import random

class Scion_Dice():
    def __init__(self, dice_pool:int, enhancement:int = 0, scale:int = 0, difficulty:int =1):
        self.dice_pool = dice_pool
        self.enhancement = enhancement
        self.scale = scale
        self.difficulty = difficulty
    #Set up the value modifiers
    def set_pool(self, numb:int):
        self.dice_pool = numb
    
    def get_pool(self):
        return self.dice_pool
    
    def set_enhancement(self, numb:int):
        self.enhancement = numb
    
    def get_enhancement(self):
        return self.enhancement

    def set_scale(self, numb:int):
        self.scale = numb

    def get_scale(self):
        return self.scale

    def set_difficulty(self, numb:int):
        self.difficulty = numb

    def get_difficulty(self):
        return self.difficulty

    def basic_roll(self):
        #Rolls the number of dice set and records them to display back
        #set up dice roller
        results = []
        for _ in range(self.dice_pool):
            results.append(random.randint(1,10))
        return results

    def count_successes(self, results,  tn:int =7):
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

