import random

class ScionDice():
    def __init__(self, dice_pool:int, enhancement:int, scale_type:str, scale:int, difficulty:int, tn:int, again:int):
        self.dice_pool = dice_pool
        self.enhancement = enhancement
        self.scale_type = scale_type
        self.scale = scale
        self.difficulty = difficulty
        self.tn = tn
        self.again = again
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

    def roll(self):
        #Rolls the number of dice set and records them to display back
        #set up dice roller
        results:list = []
        for _ in range(self.dice_pool):
            results.append(random.randint(1,10))
        return results

    def count_successes(self, results:list):
        successes = 0
        for die in results:
            if die >= self.again:
                successes += 1
            elif die >= self.tn:
                successes += 1
        if successes >= 1:
            successes += self.enhancement

        return successes

    def check_botch(self, results:list, successes:int):
        botch = False
        for die in results:
            if die == 1:
                botch = True
        if successes >= 1:
            botch = False
        return botch

    def check_explode(self, results:list):
        exploded_results = []
        for die in results:
            current_die = die
            exploded_results.append(current_die)
            while current_die >= self.again:
                current_die = random.randint(1, 10)
                exploded_results.append(current_die)
        results[:] = exploded_results
        return results

    

