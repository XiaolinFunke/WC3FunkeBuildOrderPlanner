import unittest

from SimEngine.SimulationEngine import SimulationEngine
from SimEngine.SimulationConstants import Race, UnitType, StructureType, WorkerTask, TimelineType, SECONDS_TO_SIMTIME, Trigger, TriggerType, UpgradeType
from SimEngine.Action import WorkerMovementAction, BuildUnitAction, BuildStructureAction, BuildUpgradeAction

class TestSimulationEngine(unittest.TestCase):
    def testGetJSONStateAsActionLists(self):
        simEngine = SimulationEngine() 

        simEngine.newBuildOrder([Race.NIGHT_ELF, Race.NIGHT_ELF])

        actionList1 = []
        actionList1.append(BuildUnitAction(Trigger(TriggerType.ASAP), UnitType.WISP, "Build this wisp fast!"))
        actionList1.append(WorkerMovementAction(int(1 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD))
        actionList1.append(WorkerMovementAction(int(1.2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD))
        actionList1.append(WorkerMovementAction(int(1.4 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD))
        actionList1.append(WorkerMovementAction(int(1.6 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER))
        actionList1.append(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, StructureType.ALTAR_OF_ELDERS))
        actionList1.append(BuildStructureAction(int(1.5 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, StructureType.MOON_WELL))
        actionList1.append(BuildStructureAction(0, Trigger(TriggerType.GOLD_AMOUNT, 300), WorkerTask.GOLD, StructureType.HUNTERS_HALL))
        actionList1.append(BuildUnitAction(Trigger(TriggerType.ASAP), UnitType.DEMON_HUNTER, "Skill mana burn and run to opponent's base"))
        actionList1.append(BuildUpgradeAction(Trigger(TriggerType.LUMBER_AMOUNT, 100), UpgradeType.STRENGTH_OF_THE_MOON1))

        actionList2 = []
        actionList2.append(BuildUnitAction(Trigger(TriggerType.ASAP), UnitType.WISP, "Build this wisp VERY fast!"))
        actionList2.append(WorkerMovementAction(int(1 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD))
        actionList2.append(WorkerMovementAction(int(1.2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD))
        actionList2.append(WorkerMovementAction(int(1.4 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER))
        actionList2.append(WorkerMovementAction(int(1.6 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER))
        actionList2.append(BuildUnitAction(Trigger(TriggerType.NEXT_WORKER_BUILT), UnitType.WISP))
        actionList2.append(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, StructureType.ALTAR_OF_ELDERS))
        actionList2.append(BuildStructureAction(int(1.5 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, StructureType.MOON_WELL))
        actionList2.append(BuildUnitAction(Trigger(TriggerType.ASAP), UnitType.KEEPER_OF_THE_GROVE, "Skill entangle and go with Demon Hunter to opponent's base"))

        simEngine.getTeamBuildOrders()[0].simulateOrderedActionList(actionList1)
        simEngine.getTeamBuildOrders()[1].simulateOrderedActionList(actionList2)

        self.assertTrue(simEngine.getJSONStateAsActionLists())

    def testGetJSONStateAsTimelines(self):
        simEngine = SimulationEngine() 

        simEngine.newBuildOrder([Race.NIGHT_ELF, Race.NIGHT_ELF])

        actionList1 = []
        actionList1.append(BuildUnitAction(Trigger(TriggerType.ASAP), UnitType.WISP, "Build this wisp fast!"))
        actionList1.append(WorkerMovementAction(int(1 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD))
        actionList1.append(WorkerMovementAction(int(1.2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD))
        actionList1.append(WorkerMovementAction(int(1.4 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD))
        actionList1.append(WorkerMovementAction(int(1.6 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER))
        actionList1.append(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, StructureType.ALTAR_OF_ELDERS))
        actionList1.append(BuildStructureAction(int(1.5 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, StructureType.MOON_WELL))
        actionList1.append(BuildStructureAction(0, Trigger(TriggerType.GOLD_AMOUNT, 300), WorkerTask.GOLD, StructureType.HUNTERS_HALL))
        actionList1.append(BuildUnitAction(Trigger(TriggerType.ASAP), UnitType.DEMON_HUNTER, "Skill mana burn and run to opponent's base"))
        actionList1.append(BuildUpgradeAction(Trigger(TriggerType.LUMBER_AMOUNT, 100), UpgradeType.STRENGTH_OF_THE_MOON1))

        actionList2 = []
        actionList2.append(BuildUnitAction(Trigger(TriggerType.ASAP), UnitType.WISP, "Build this wisp VERY fast!"))
        actionList2.append(WorkerMovementAction(int(1 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD))
        actionList2.append(WorkerMovementAction(int(1.2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD))
        actionList2.append(WorkerMovementAction(int(1.4 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER))
        actionList2.append(WorkerMovementAction(int(1.6 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER))
        actionList2.append(BuildUnitAction(Trigger(TriggerType.NEXT_WORKER_BUILT), UnitType.WISP))
        actionList2.append(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, StructureType.ALTAR_OF_ELDERS))
        actionList2.append(BuildStructureAction(int(1.5 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, StructureType.MOON_WELL))
        actionList2.append(BuildUnitAction(Trigger(TriggerType.ASAP), UnitType.KEEPER_OF_THE_GROVE, "Skill entangle and go with Demon Hunter to opponent's base"))

        simEngine.getTeamBuildOrders()[0].simulateOrderedActionList(actionList1)
        simEngine.getTeamBuildOrders()[1].simulateOrderedActionList(actionList2)

        self.assertTrue(simEngine.getJSONStateAsTimelines())