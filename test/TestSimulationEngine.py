import unittest

from SimEngine.SimulationEngine import SimulationEngine
from SimEngine.SimulationConstants import Race, WorkerTask, TimelineType, SECONDS_TO_SIMTIME, Trigger, TriggerType
from SimEngine.Action import WorkerMovementAction, BuildUnitAction, BuildStructureAction, BuildUpgradeAction, ShopAction

#Convenience method to simulate a basic night elf build order
def simulateBasicElfBuildOrder(simEngine):
    simEngine.newBuildOrder([Race.NIGHT_ELF, Race.NIGHT_ELF])

    actionList1 = []
    actionList1.append(BuildUnitAction(Trigger(TriggerType.ASAP), "Wisp", 60, 0, 1, 14 * SECONDS_TO_SIMTIME, "Tree of Life", "Build this wisp fast!"))
    actionList1.append(WorkerMovementAction(int(1 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, "Wisp"))
    actionList1.append(WorkerMovementAction(int(1.2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, "Wisp"))
    actionList1.append(WorkerMovementAction(int(1.4 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, "Wisp"))
    actionList1.append(WorkerMovementAction(int(1.6 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, "Wisp"))
    actionList1.append(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Altar of Elders", 180, 50, 0, 60 * SECONDS_TO_SIMTIME, "Wisp", False))
    actionList1.append(BuildStructureAction(int(1.5 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, "Moon Well", 180, 40, 10, 50 * SECONDS_TO_SIMTIME, "Wisp", False))
    actionList1.append(BuildStructureAction(0, Trigger(TriggerType.GOLD_AMOUNT, 300), WorkerTask.GOLD, "Hunter's Hall", 210, 100, 0, 60 * SECONDS_TO_SIMTIME, "Wisp", False))
    actionList1.append(BuildUnitAction(Trigger(TriggerType.ASAP), "Demon Hunter", 0, 0, 5, 55 * SECONDS_TO_SIMTIME, "Altar of Elders", "Skill mana burn and run to opponent's base"))
    actionList1.append(BuildUpgradeAction(Trigger(TriggerType.LUMBER_AMOUNT, 75), "Strength of the Moon", 125, 75, 60 * SECONDS_TO_SIMTIME, "Hunter's Hall"))

    actionList2 = []
    actionList2.append(BuildUnitAction(Trigger(TriggerType.ASAP), "Wisp", 60, 0, 1, 14 * SECONDS_TO_SIMTIME, "Tree of Life", "Build this wisp VERY fast!"))
    actionList2.append(WorkerMovementAction(int(1 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, "Wisp"))
    actionList2.append(WorkerMovementAction(int(1.2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, "Wisp"))
    actionList2.append(WorkerMovementAction(int(1.4 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, "Wisp"))
    actionList2.append(WorkerMovementAction(int(1.6 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, "Wisp"))
    actionList2.append(BuildUnitAction(Trigger(TriggerType.NEXT_WORKER_BUILT), "Wisp", 60, 0, 1, 14 * SECONDS_TO_SIMTIME, "Tree of Life"))
    actionList2.append(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Altar of Elders", 180, 50, 0, 60 * SECONDS_TO_SIMTIME, "Wisp", False))
    actionList2.append(BuildStructureAction(int(1.5 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, "Moon Well", 180, 40, 10, 50 * SECONDS_TO_SIMTIME, "Wisp", False))
    actionList2.append(ShopAction("Scroll of Town Portal", 325, Trigger(TriggerType.ASAP), "Goblin Merchant", 15 * SECONDS_TO_SIMTIME, True, "Sell TP to get more money for hunts"))
    actionList2.append(BuildUnitAction(Trigger(TriggerType.ASAP), "Keeper of the Grove", 0, 0, 5, 55 * SECONDS_TO_SIMTIME, "Altar of Elders", "Skill entangle and go with Demon Hunter to opponent's base"))

    simEngine.getTeamBuildOrders()[0].simulateOrderedActionList(actionList1)
    simEngine.getTeamBuildOrders()[1].simulateOrderedActionList(actionList2)

class TestSimulationEngine(unittest.TestCase):
    def testGetJSONStateAsActionLists(self):
        simEngine = SimulationEngine() 

        simulateBasicElfBuildOrder(simEngine)

        self.assertTrue(simEngine.getJSONStateAsActionLists())

    def testGetJSONStateAsTimelines(self):
        simEngine = SimulationEngine() 

        simulateBasicElfBuildOrder(simEngine)

        self.assertTrue(simEngine.getJSONStateAsTimelines())

    def testLoadStateFromJSON(self):
        simEngine = SimulationEngine() 

        #First, simulate normally
        simulateBasicElfBuildOrder(simEngine)

        #Now, save off the state in JSON to compare to later
        originalJSONTimelines = simEngine.getJSONStateAsTimelines()
        originalJSONActionList = simEngine.getJSONStateAsActionLists()

        #Load from action list JSON
        simEngine2 = SimulationEngine() 
        self.assertTrue(simEngine2.loadStateFromActionListsJSON(originalJSONActionList))

        self.assertEqual(originalJSONActionList, simEngine2.getJSONStateAsActionLists()) 
        self.assertEqual(originalJSONTimelines, simEngine2.getJSONStateAsTimelines()) 