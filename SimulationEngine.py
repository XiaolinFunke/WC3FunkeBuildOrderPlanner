from enum import Enum, auto

from SimulationConstants import Race, SECONDS_TO_SIMTIME

from BuildOrder import BuildOrder

class SimulationEngine:
    def __init__(self):
        self.mBuildOrder = None

    def printScheduledEvents(self):
        self.mBuildOrder.getEventHandler().printScheduledEvents()

    def newBuildOrder(self, race):
        self.mBuildOrder = BuildOrder(race)

    #Will simulate up to specified simtime
    def simulate(self, untilSimTime):
        self.mBuildOrder.simulate(untilSimTime)

    def sendWorkerToMine(self, timelineID, simTime, travelTime):
        self.mBuildOrder.sendWorkerToMine(timelineID, simTime, travelTime)

def main():
    simEngine = SimulationEngine()
    simEngine.newBuildOrder(Race.NIGHT_ELF)
    simEngine.sendWorkerToMine(timelineID=0, simTime=0, travelTime=1 * SECONDS_TO_SIMTIME)
    simEngine.sendWorkerToMine(timelineID=1, simTime=0, travelTime=1.2 * SECONDS_TO_SIMTIME)
    simEngine.sendWorkerToMine(timelineID=2, simTime=0, travelTime =1.5 * SECONDS_TO_SIMTIME)
    simEngine.sendWorkerToMine(timelineID=3, simTime=0, travelTime=1.8 * SECONDS_TO_SIMTIME)
    simEngine.sendWorkerToMine(timelineID=4, simTime=0, travelTime=2 * SECONDS_TO_SIMTIME)

    for i in range(1, 121):
        simEngine.simulate(i * SECONDS_TO_SIMTIME)
        print("Time:", i, "seconds")
        simEngine.mBuildOrder.getCurrentResources().print()

    simEngine.printScheduledEvents()


if __name__ == "__main__":
    main()