from SimEngine.SimulationConstants import Race, SECONDS_TO_SIMTIME
from SimEngine.SimulationEngine import SimulationEngine

def main():
    simEngine = SimulationEngine()
    simEngine.newBuildOrder([Race.NIGHT_ELF])

    for i in range(1, 121):
        simEngine.simulate(i * SECONDS_TO_SIMTIME)
        print("Time:", i, "seconds")
        simEngine.mBuildOrder.getCurrentResources().print()

    simEngine.printScheduledEvents()


if __name__ == "__main__":
    main()