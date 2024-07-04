from enum import Enum, auto

SECONDS_TO_SIMTIME = 10 #simtime is in deciseconds
SIMTIME_TO_SECONDS = 1/SECONDS_TO_SIMTIME #simtime is in deciseconds

TIMELINE_TYPE_GOLD_MINE = "Gold Mine"

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