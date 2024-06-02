from SimEngine.BuildOrder import BuildOrder
from SimEngine.SimulationConstants import WorkerTask

from enum import Enum
import json

class SimulationEngine:
    def __init__(self):
        self.mTeamBuildOrders = []

    #For solo builds, only 1 race will be in list, for 2v2, will be 2, etc.
    def newBuildOrder(self, raceList):
        self.mTeamBuildOrders = []
        for race in raceList:
            self.mTeamBuildOrders.append(BuildOrder(race))

    #Takes JSON of ordered action list for team build orders and simulate from scratch
    def loadStateFromActionLists(self, stateJSON):
        pass

    #Returns the JSON of the current build order states as timelines
    def getJSONStateAsTimelines(self):
        list = [] 
        for buildOrder in self.mTeamBuildOrders:
            list.append(buildOrder.getSimTimeAndTimelinesAsDictForSerialization())

        return json.dumps(list, indent = 2)

    #Returns the JSON of the current build order states as action lists
    def getJSONStateAsActionLists(self):
        list = [] 
        for buildOrder in self.mTeamBuildOrders:
            list.append(buildOrder.getRaceAndActionListAsDictForSerialization())

        return json.dumps(list, indent = 2)

    def getTeamBuildOrders(self):
        return self.mTeamBuildOrders