import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.SimulationConstants import Race, SECONDS_TO_SIMTIME
from SimEngine.Trigger import Trigger, TriggerType
from SimEngine.Worker import WorkerTask, Worker
from SimEngine.Action import WorkerMovementAction, BuildStructureAction, BuildUnitAction
from Test.UniqueIDHandler import UniqueIDHandler

#Executes moving N wisps to gold realistically
#Returns the time at which the first 10 gold will be gained
def executeStandardElfStart(buildOrder, actionIDHandler, numWorkersToGold):
    #Workers mine in a staggered fashion
    #It takes 5 wisp-seconds to make 10 gold
    if numWorkersToGold == 0 or numWorkersToGold > 5:
        print("executeStandardElfStart cannot have ", numWorkersToGold, " workers specified")
        return None

    #1 second of no money (0 progress to 10 gold)
    buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, actionIDHandler.getNextID()))
    if numWorkersToGold == 1:
        return (5 + 1) * SECONDS_TO_SIMTIME

    buildOrder.simulateAction(WorkerMovementAction(1.2 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, actionIDHandler.getNextID()))
    if numWorkersToGold == 2:
        #0.2 seconds of single wisp (0.2 wisp-seconds progress to 10 gold) already done
        return (2.4 + 1.2) * SECONDS_TO_SIMTIME

    buildOrder.simulateAction(WorkerMovementAction(1.5 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, actionIDHandler.getNextID()))
    if numWorkersToGold == 3:
        #then 0.3 seconds of 2 wisps (0.6 wisp-seconds progress to 10 gold) (0.8 wisp seconds total)
        return (1.4 + 1.3) * SECONDS_TO_SIMTIME


    if numWorkersToGold == 4:
        #then 0.3 seconds of 3 wisps (0.9 wisp-seconds progress to 10 gold) (1.7 wisp seconds total)
        buildOrder.simulateAction(WorkerMovementAction(1.8 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, actionIDHandler.getNextID()))
        return round((0.825 + 1.8) * SECONDS_TO_SIMTIME)

    #then 0.2 seconds of 4 wisps (0.8 wisp-seconds progress to 10 gold) (2.5 wisp seconds total)
    buildOrder.simulateAction(WorkerMovementAction(2 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, actionIDHandler.getNextID()))
    return (0.5 + 2)

class TestRealBuildOrders(unittest.TestCase):
    def testDoubleAoWHunts(self):
        actionIDHandler = UniqueIDHandler()
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        timeOfFirstGold = executeStandardElfStart(buildOrder, actionIDHandler, 4)

        #0th wisp -- Altar
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Altar of Elders", 
                                              180, 50, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)))

        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        #1st wisp -- moon well
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, "Moon Well", 
                                                    180, 40, 10, 50 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)))

        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        #2nd wisp -- gold
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(1.5 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, WorkerTask.GOLD, Worker.Wisp.name, actionIDHandler.getNextID())))

        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        #3rd wisp -- lumber
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))

        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        #4th wisp -- lumber
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))

        #5th wisp start
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        #@Altar -- build hero
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), "Keeper of the Grove", 0, 0, 5, 55 * SECONDS_TO_SIMTIME, 8, "Altar of Elders")))
        #Altar and moon well wisps to lumber when done
        #TODO: Change to use trigger at 100% of those buildings once we have that trigger type working
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))

        #5th wisp to lumber
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))

        #6th wisp -- lumber
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))

        #7th wisp -- start
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))

        #@160 lumber, build AoW and HH
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(2 * SECONDS_TO_SIMTIME, Trigger(TriggerType.LUMBER_AMOUNT, 160), WorkerTask.LUMBER, "Hunter's Hall", 210, 100, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)))
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(2 * SECONDS_TO_SIMTIME, Trigger(TriggerType.LUMBER_AMOUNT, 160), WorkerTask.LUMBER, "Ancient of War", 150, 60, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), True)))

        #7th wisp to lumber
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))

        #8th wisp -- lumber
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))

        #9th wisp -- start
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))

        #TODO: This might be during the 8th wisp instead of 9th, was close
        #@60 lumber -- 2nd AoW
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(3 * SECONDS_TO_SIMTIME), Trigger(TriggerType.LUMBER_AMOUNT, 60), WorkerTask.LUMBER, "Ancient of War", 150, 60, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), True)))

        #9th wisp to lumber
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))

        #@40 lumber -- 2nd well
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.LUMBER_AMOUNT, 40), WorkerTask.LUMBER, "Moon Well", 
                                                    180, 40, 10, 50 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)))

        #@AoW -- 1st Hunt
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), "Huntress", 195, 20, 3, 30 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Ancient of War")))

        #@2nd Aow -- 2nd Hunt
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), "Huntress", 195, 20, 3, 30 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Ancient of War")))

        #@1st Hunt -- 3rd Hunt
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), "Huntress", 195, 20, 3, 30 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Ancient of War")))