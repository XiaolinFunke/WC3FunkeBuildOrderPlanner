from SimEngine.BuildOrder import BuildOrder
from SimEngine.SimulationConstants import WorkerTask

from enum import Enum
import json

class SimulationEngine:
    def __init__(self):
        self.mTeamBuildOrders = []
        self.testEnum = WorkerTask.GOLD

    #For solo builds, only 1 race will be in list, for 2v2, will be 2, etc.
    def newBuildOrder(self, raceList):
        self.mTeamBuildOrders = []
        for race in raceList:
            self.mTeamBuildOrders.append(BuildOrder(race))

    def loadState(self):
        pass

    def getState(self):
        return json.dumps(self.mTeamBuildOrders, default=todict, sort_keys=True, indent=2)

    def saveStateToFile(self, filePath):
        with open(filePath, "w") as outputFile:
            outputFile.write(self.getState())

    def getTeamBuildOrders(self):
        return self.mTeamBuildOrders

#Recursively convert an object to a dictionary, to be used by the json serializer when it hits unfamiliar types
#Code source (some additions made by me): https://stackoverflow.com/questions/1036409/recursively-convert-python-object-graph-to-dictionary
def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif isinstance(obj, Enum):
        #obj.value if want the integer instead
        return obj.name
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey)) 
            for key, value in obj.__dict__.items() 
            if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj