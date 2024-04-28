from SimEngine.BuildOrder import BuildOrder

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
        self.simulate(simTime)
        self.mBuildOrder.sendWorkerToMine(timelineID, travelTime)

    def sendWorkerToLumber(self, timelineID, simTime, travelTime):
        self.simulate(simTime)
        self.mBuildOrder.sendWorkerToLumber(timelineID, travelTime)