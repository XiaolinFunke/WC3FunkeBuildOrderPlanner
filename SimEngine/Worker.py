from enum import Enum, auto

class Worker(Enum):
    #Note: These names must be spelled exactly like this to match the liquipedia data for when we build units that happen to be workers
    Wisp = auto() 
    Acolyte = auto()
    Peasant = auto()
    Peon = auto()
    Ghoul = auto()

def isUnitWorker(unitName):
    for workerName in Worker:
        if unitName == workerName.name:
            return True

    return False

class WorkerTask(Enum):
    GOLD = auto()
    LUMBER = auto()
    CONSTRUCTING = auto()
    ROAMING = auto()
    IN_PRODUCTION = auto()
    IDLE = auto()