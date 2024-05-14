from enum import Enum, auto

# Each building that can make units/upgrades has its own timeline
# There are also timelines for constructing buildings, shops to buy/sell items and tavern
class TimelineType(Enum):
    #NEUTRAL
    WORKER = auto()
    TAVERN = auto()
    GOBLIN_MERCHANT = auto()
    GOLD_MINE = auto()
    #HUMAN
    #Represents all tiers of the town hall
    TOWN_HALL = auto()
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
    ANCIENT_OF_WAR = auto()
    HUNTERS_HALL = auto()
    ALTAR_OF_ELDERS = auto()
    ANCIENT_OF_LORE = auto()
    ANCIENT_OF_WIND = auto()
    CHIMAERA_ROOST = auto()
    ANCIENT_OF_WONDERS = auto()