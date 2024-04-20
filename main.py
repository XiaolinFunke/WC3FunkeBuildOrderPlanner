from SimEngine.SimulationConstants import Race, SECONDS_TO_SIMTIME
from SimEngine.SimulationEngine import SimulationEngine

def main():
    simEngine = SimulationEngine()
    simEngine.newBuildOrder(Race.NIGHT_ELF)
    simEngine.sendWorkerToMine(timelineID=0, simTime=0, travelTime=1 * SECONDS_TO_SIMTIME)
    simEngine.sendWorkerToMine(timelineID=1, simTime=0, travelTime=1.2 * SECONDS_TO_SIMTIME)
    simEngine.sendWorkerToMine(timelineID=2, simTime=0, travelTime =1.5 * SECONDS_TO_SIMTIME)
    simEngine.sendWorkerToMine(timelineID=3, simTime=0, travelTime=1.8 * SECONDS_TO_SIMTIME)
    simEngine.sendWorkerToMine(timelineID=4, simTime=0, travelTime=3 * SECONDS_TO_SIMTIME)

    for i in range(1, 121):
        simEngine.simulate(i * SECONDS_TO_SIMTIME)
        print("Time:", i, "seconds")
        simEngine.mBuildOrder.getCurrentResources().print()

    simEngine.printScheduledEvents()


if __name__ == "__main__":
    main()