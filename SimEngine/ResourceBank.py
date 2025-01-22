from SimEngine.SimulationConstants import STARTING_GOLD, STARTING_LUMBER, STARTING_FOOD, STARTING_FOOD_MAX_MAP
from SimEngine.SimulationConstants import Race

class ResourceBank:
    def __init__(self, race, startingGold=STARTING_GOLD, startingLumber=STARTING_LUMBER, startingFood=STARTING_FOOD, startingFoodMax=None):
        self.mCurrentGold = startingGold
        self.mCurrentLumber = startingLumber
        self.mCurrentFood = startingFood

        if not startingFoodMax:
            self.mCurrentFoodMax = STARTING_FOOD_MAX_MAP[race]
        else:
            self.mCurrentFoodMax = startingFoodMax

    def getAsDictForSerialization(self):
        dict = {
            'currentGold' : self.mCurrentGold,
            'currentLumber' : self.mCurrentLumber,
            'currentFood' : self.mCurrentFood,
            'currentFoodMax' : self.mCurrentFoodMax
        }

        return dict

    def modifyResources(self, goldChange, lumberChange, foodChange = 0, foodMaxChange = 0):
        self.mCurrentGold += goldChange
        self.mCurrentLumber += lumberChange
        self.mCurrentFood += foodChange
        self.mCurrentFoodMax += foodMaxChange

    def deductGold(self, amount):
        if amount > self.mCurrentGold:
            print("Tried to deduct", amount, "gold, but only have", self.mCurrentGold)
        else:
            self.mCurrentGold -= amount

    def deductLumber(self, amount):
        if amount > self.mCurrentLumber:
            print("Tried to deduct", amount, "lumber, but only have", self.mCurrentLumber)
        else:
            self.mCurrentLumber -= amount

    def increaseMaxFood(self, amount):
        self.mCurrentFoodMax += amount

    def increaseFoodUsed(self, amount):
        self.mCurrentFood += amount

    def decreaseFoodUsedByOne(self):
        if self.mCurrentFood <= 0:
            print("Tried to decrease food used by one, but food count was", self.mCurrentFood)
        else:
            self.mCurrentFood -= 1

    def getCurrentGold(self):
        return self.mCurrentGold

    def getCurrentLumber(self):
        return self.mCurrentLumber

    def getCurrentFood(self):
        return self.mCurrentFood

    def getCurrentFoodMax(self):
        return self.mCurrentFoodMax

    def haveRequiredResources(self, goldRequired, lumberRequired, foodRequired = 0):
        return self.mCurrentGold >= goldRequired and self.mCurrentLumber >= lumberRequired and self.mCurrentFood + foodRequired <= self.mCurrentFoodMax

    def __sub__(self, other):
        new = ResourceBank(Race.NIGHT_ELF, self.mCurrentGold, self.mCurrentLumber, self.mCurrentFood, self.mCurrentFoodMax)
        new.mCurrentFood -= other.mCurrentFood
        new.mCurrentGold -= other.mCurrentGold
        new.mCurrentLumber -= other.mCurrentLumber
        return new

    def __add__(self, other):
        new = ResourceBank(Race.NIGHT_ELF, self.mCurrentGold, self.mCurrentLumber, self.mCurrentFood, self.mCurrentFoodMax)
        new.mCurrentFood += other.mCurrentFood
        new.mCurrentGold += other.mCurrentGold
        new.mCurrentLumber += other.mCurrentLumber
        return new

    def __eq__(self, other):
        #Don't attempt to compare if not the same type
        if not isinstance(other, ResourceBank):
            return NotImplemented

        return self.mCurrentFood == other.mCurrentFood and self.mCurrentFoodMax == other.mCurrentFoodMax and self.mCurrentGold == other.mCurrentGold and self.mCurrentLumber == other.mCurrentLumber

    def __str__(self):
        return "| Gold:" + str(self.mCurrentGold) + " | Lumber:" + str(self.mCurrentLumber) + " | Food:" + str(self.mCurrentFood) + "/" + str(self.mCurrentFoodMax) + " |"

    def __repr__(self):
        return self.__str__()