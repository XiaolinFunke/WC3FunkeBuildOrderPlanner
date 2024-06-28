from enum import Enum, auto

SECONDS_TO_SIMTIME = 10 #simtime is in deciseconds
SIMTIME_TO_SECONDS = 1/SECONDS_TO_SIMTIME #simtime is in deciseconds

TIMELINE_TYPE_GOLD_MINE = "Gold Mine"

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

#TODO: Move Trigger out of this file
class Trigger():
    def __init__(self, triggerType, triggerValue = None):
        self.mTriggerType = triggerType
        #Not used for ASAP trigger type
        #Integer for other types, except NEXT_WORKER, for which its a string designating the worker type
        self.mValue = triggerValue

    #Used for deserializing JSON
    @staticmethod
    def getTriggerFromDict(triggerDict):
        triggerType = TriggerType[triggerDict['triggerType']]

        #Use get instead of [] because it will return None if there is no trigger value
        triggerValue = triggerDict.get('value')
        triggerObj = Trigger(triggerType, triggerValue)

        return triggerObj

    #Get as dict for JSON encoding
    def getAsDictForSerialization(self):
        dict = {
            'triggerType' : self.mTriggerType.name,
        }
        if self.mValue != None:
            dict['value'] = self.mValue

        return dict

class TriggerType(Enum):
    ASAP = auto()
    GOLD_AMOUNT = auto()
    LUMBER_AMOUNT = auto()
    FOOD_AMOUNT = auto()
    NEXT_WORKER_BUILT = auto()
    PERCENT_OF_ONGOING_ACTION = auto()