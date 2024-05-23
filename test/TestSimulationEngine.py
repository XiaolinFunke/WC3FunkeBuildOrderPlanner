import unittest

from SimEngine.SimulationEngine import SimulationEngine
from SimEngine.SimulationConstants import Race, UnitType, StructureType, WorkerTask, TimelineType, SECONDS_TO_SIMTIME, Trigger, TriggerType
from SimEngine.Action import WorkerMovementAction, BuildUnitAction, BuildStructureAction

class TestSimulationEngine(unittest.TestCase):
    def testGetState(self):
        simEngine = SimulationEngine() 

        simEngine.newBuildOrder([Race.NIGHT_ELF])

    def testSaveStateToFile(self):
        simEngine = SimulationEngine() 

        simEngine.newBuildOrder([Race.NIGHT_ELF])

        simEngine.saveStateToFile(r"D:\Visual Studio Code\ForFun\WC3BuildOrderPlanner\Test\TestOutput\testSaveStartingStateToFile.json")

        buildOrder = simEngine.getTeamBuildOrders()[0]

        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=TimelineType.WORKER)
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1.5 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1.5 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, workerTimelines[2].getTimelineID()))

        buildOrder.simulate(1 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), UnitType.WISP))
        buildOrder.simulate(2 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, StructureType.ALTAR_OF_ELDERS))
        buildOrder.simulate(3 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, StructureType.MOON_WELL))

        simEngine.saveStateToFile(r"D:\Visual Studio Code\ForFun\WC3BuildOrderPlanner\Test\TestOutput\testSaveBuildDemonHunterStateToFile.json")

