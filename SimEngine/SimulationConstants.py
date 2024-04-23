from enum import Enum, auto

SECONDS_TO_SIMTIME = 10 #simtime is in deciseconds
SIMTIME_TO_SECONDS = 1/SECONDS_TO_SIMTIME #simtime is in deciseconds

STARTING_GOLD = 500
STARTING_LUMBER = 150

GOLD_MINED_PER_TRIP = 10
#Time to mine for 1 worker
TIME_TO_MINE_GOLD_BASE_SEC = 5

class Race(Enum):
    HUMAN = auto()
    ORC = auto()
    NIGHT_ELF = auto()
    UNDEAD = auto()

class WorkerTask(Enum):
    GOLD = auto(),
    LUMBER = auto(),
    CONSTRUCTING = auto(),
    ROAMING = auto()

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