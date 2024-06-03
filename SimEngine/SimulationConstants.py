from enum import Enum, auto

from SimEngine.TimelineTypeEnum import TimelineType

SECONDS_TO_SIMTIME = 10 #simtime is in deciseconds
SIMTIME_TO_SECONDS = 1/SECONDS_TO_SIMTIME #simtime is in deciseconds

class Race(Enum):
    HUMAN = auto()
    ORC = auto()
    NIGHT_ELF = auto()
    UNDEAD = auto()

STARTING_GOLD = 500
STARTING_LUMBER = 150
STARTING_FOOD = 5
STARTING_FOOD_MAX_MAP = {
    Race.NIGHT_ELF: 10,
    Race.UNDEAD: 10,
    Race.HUMAN: 12,
    Race.ORC: 11
}

GOLD_MINED_PER_TRIP = 10
#Time to mine for 1 worker
TIME_TO_MINE_GOLD_BASE_SEC = 5

class WorkerTask(Enum):
    GOLD = auto()
    LUMBER = auto()
    CONSTRUCTING = auto()
    ROAMING = auto()
    IN_PRODUCTION = auto()
    IDLE = auto()

class StructureType(Enum):
    #HUMAN
    #Represents all tiers of the town hall
    TOWN_HALL = auto()
    FARM = auto()
    HUMAN_BARRACKS = auto()
    LUMBER_MILL = auto()
    BLACKSMITH = auto()
    ALTAR_OF_KINGS = auto()
    ARCANE_SANCTUM = auto()
    WORKSHOP = auto()
    SCOUT_TOWER = auto()
    GRYPHON_AVIARY = auto()
    ARCANE_VAULT = auto()
    #NIGHT ELF
    #Represents all tiers of the tree of life
    TREE_OF_LIFE = auto()
    #TODO: How do we handle entangle gold mine? -- kind of like an upgrade?
    ENTANGLED_GOLD_MINE = auto()
    MOON_WELL = auto()
    ANCIENT_OF_WAR = auto()
    ANCIENT_PROTECTOR = auto()
    HUNTERS_HALL = auto()
    ALTAR_OF_ELDERS = auto()
    ANCIENT_OF_LORE = auto()
    ANCIENT_OF_WIND = auto()
    CHIMAERA_ROOST = auto()
    ANCIENT_OF_WONDERS = auto()

class UnitType(Enum):
    #NEUTRAL
    NAGA_SEA_WITCH = auto()
    DARK_RANGER = auto()
    PANDAREN_BREWMASTER = auto()
    BEASTMASTER = auto()
    PIT_LORD = auto()
    GOBLIN_TINKER = auto()
    FIRELORD = auto()
    GOBLIN_ALCHEMIST = auto()
    #HUMAN
    PALADIN = auto()
    ARCHMAGE = auto()
    MOUNTAIN_KING = auto()
    BLOOD_MAGE = auto()
    PEASANT = auto()
    FOOTMAN = auto()
    KNIGHT = auto()
    PRIEST = auto()
    SORCERESS = auto()
    SPELL_BREAKER = auto()
    FLYING_MACHINE = auto()
    MORTAR_TEAM = auto()
    SIEGE_ENGINE = auto()
    GRYPHON_RIDER = auto()
    DRAGONHAWK_RIDER = auto()
    #NIGHT ELF
    DEMON_HUNTER = auto()
    KEEPER_OF_THE_GROVE = auto()
    PRIESTESS_OF_THE_MOON = auto()
    WARDEN = auto()
    WISP = auto()
    ARCHER = auto()
    HUNTRESS = auto()
    GLAIVE_THROWER = auto()
    DRYAD = auto()
    DRUID_OF_THE_CLAW = auto()
    MOUNTAIN_GIANT = auto()
    HIPPOGRYPH = auto()
    DRUID_OF_THE_TALON = auto()
    FAERIE_DRAGON = auto()
    CHIMAERA = auto()

class Trigger():
    def __init__(self, triggerType, triggerAmount = None):
        self.mTriggerType = triggerType
        #Not used for ASAP and NEXT_WORKER_BUILT trigger types
        self.mValue = triggerAmount

    #Used for deserializing JSON
    @staticmethod
    def getTriggerFromDict(triggerDict):
        triggerType = TriggerType[triggerDict['mTriggerType']]

        triggerValue = None if triggerDict['mValue'] == None else int(triggerDict['mValue'])
        triggerObj = Trigger(triggerType, triggerValue)

        return triggerObj

    #Get as dict for JSON encoding
    def getAsDictForSerialization(self):
        dict = {
            'mTriggerType' : self.mTriggerType.name,
            'mValue' : self.mValue
        }
        return dict

class TriggerType(Enum):
    ASAP = auto()
    GOLD_AMOUNT = auto()
    LUMBER_AMOUNT = auto()
    FOOD_AMOUNT = auto()
    NEXT_WORKER_BUILT = auto()
    PERCENT_OF_ONGOING_ACTION = auto()

class UnitStats:
    def __init__(self, goldCost, lumberCost, foodCost, timeToBuildSec, requiredTimelineType, isHero, name):
        self.mName = name
        self.mIsHero = isHero
        self.mGoldCost = goldCost
        self.mLumberCost = lumberCost
        self.mFoodCost = foodCost
        self.mTimeToBuildSec = timeToBuildSec
        self.mRequiredTimelineType = requiredTimelineType

UNIT_STATS_MAP = {
    #Tree of life timeline represents all tiers of tree of life
    UnitType.WISP: UnitStats(goldCost = 60, lumberCost = 0, foodCost = 1, timeToBuildSec = 14, requiredTimelineType = TimelineType.TREE_OF_LIFE, isHero = False, name = "Wisp"), 
    UnitType.DEMON_HUNTER: UnitStats(goldCost = 400, lumberCost = 100, foodCost = 5, timeToBuildSec = 55, requiredTimelineType = TimelineType.ALTAR_OF_ELDERS, isHero = True, name = "Demon Hunter"),
    UnitType.KEEPER_OF_THE_GROVE: UnitStats(goldCost = 400, lumberCost = 100, foodCost = 5, timeToBuildSec = 55, requiredTimelineType = TimelineType.ALTAR_OF_ELDERS, isHero = True, name = "Keeper of the Grove")
}

class StructureStats:
    def __init__(self, name, goldCost, lumberCost, foodProvided, timeToBuildSec):
        self.mName = name
        self.mGoldCost = goldCost
        self.mLumberCost = lumberCost
        self.mFoodProvided = foodProvided
        self.mTimeToBuildSec = timeToBuildSec
    

STRUCTURE_STATS_MAP = {
    StructureType.ALTAR_OF_ELDERS: StructureStats(name = "Altar of Elders", goldCost = 180, lumberCost = 50, foodProvided = 0, timeToBuildSec = 60),
    StructureType.MOON_WELL: StructureStats(name = "Moon Well", goldCost = 180, lumberCost = 40, foodProvided = 10, timeToBuildSec = 50),
    StructureType.HUNTERS_HALL: StructureStats(name = "Hunter's Hall", goldCost = 210, lumberCost = 100, foodProvided = 0, timeToBuildSec = 60)
}

class ItemType(Enum):
    DUST_OF_APPEARANCE = auto()

ITEM_STATS_MAP = {

}

class UpgradeStats:
    def __init__(self, goldCost, lumberCost, timeToBuildSec, requiredTimelineType, name):
        self.mName = name
        self.mGoldCost = goldCost
        self.mLumberCost = lumberCost
        self.mTimeToBuildSec = timeToBuildSec
        self.mRequiredTimelineType = requiredTimelineType

class UpgradeType(Enum):
    STRENGTH_OF_THE_MOON1 = auto()

UPGRADE_STATS_MAP = {
    UpgradeType.STRENGTH_OF_THE_MOON1: UpgradeStats(goldCost = 125, lumberCost = 75, timeToBuildSec = 60, requiredTimelineType = TimelineType.HUNTERS_HALL, name = "Strength of the Moon"), 
}
