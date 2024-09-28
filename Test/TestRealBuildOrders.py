import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.ResourceBank import ResourceBank
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

        #First gold gained at 2.625 seconds
        #With 4 wisps, we will gain 10 more every 1.25 seconds
        executeStandardElfStart(buildOrder, actionIDHandler, 4)

        #Queue first wisp
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        #Time shouldn't have advanced yet
        self.assertEqual(buildOrder.getCurrentSimTime(), 0)

        #0th wisp -- Altar
        altarActionID = actionIDHandler.getNextID()
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(8 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Altar of Elders", 
                                              180, 50, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, altarActionID, False)))
        #Time should not advance yet
        self.assertEqual(buildOrder.getCurrentSimTime(), 0)

        #1st wisp -- moon well
        moonWellActionID = actionIDHandler.getNextID()
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, "Moon Well", 
                                                    180, 40, 10, 50 * SECONDS_TO_SIMTIME, Worker.Wisp.name, moonWellActionID, False)))
        #Time should advance until the time the first wisp is built
        self.assertEqual(buildOrder.getCurrentSimTime(), 14 * SECONDS_TO_SIMTIME)

        #Queue 2nd wisp
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        self.assertEqual(buildOrder.getCurrentSimTime(), 14 * SECONDS_TO_SIMTIME)

        #2nd wisp -- gold
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(1.5 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, WorkerTask.GOLD, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(buildOrder.getCurrentSimTime(), 28 * SECONDS_TO_SIMTIME)

        #Queue 3rd wisp
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        self.assertEqual(buildOrder.getCurrentSimTime(), 28 * SECONDS_TO_SIMTIME)

        #3rd wisp -- lumber
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(buildOrder.getCurrentSimTime(), 42 * SECONDS_TO_SIMTIME)

        #Queue 4th wisp
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        self.assertEqual(buildOrder.getCurrentSimTime(), 42 * SECONDS_TO_SIMTIME)

        #4th wisp -- lumber
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(buildOrder.getCurrentSimTime(), 56 * SECONDS_TO_SIMTIME)

        #5th wisp start
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        self.assertEqual(buildOrder.getCurrentSimTime(), 56 * SECONDS_TO_SIMTIME)

        #Moon well wisp to lumber when done
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.PERCENT_OF_ONGOING_ACTION, 100, moonWellActionID), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(buildOrder.getCurrentSimTime(), 66 * SECONDS_TO_SIMTIME)

        #@Altar -- build hero
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), "Keeper of the Grove", 0, 0, 5, 55 * SECONDS_TO_SIMTIME, 8, "Altar of Elders")))
        self.assertEqual(buildOrder.getCurrentSimTime(), 68 * SECONDS_TO_SIMTIME)

        #Altar wisp to lumber when done
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.PERCENT_OF_ONGOING_ACTION, 100, altarActionID), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(buildOrder.getCurrentSimTime(), 68 * SECONDS_TO_SIMTIME)

        #5th wisp to lumber
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(buildOrder.getCurrentSimTime(), 70 * SECONDS_TO_SIMTIME)

        #Queue 6th wisp
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        self.assertEqual(buildOrder.getCurrentSimTime(), 70 * SECONDS_TO_SIMTIME)

        #6th wisp -- lumber
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(buildOrder.getCurrentSimTime(), 84 * SECONDS_TO_SIMTIME)

        #Queue 7th wisp
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        self.assertEqual(buildOrder.getCurrentSimTime(), 84 * SECONDS_TO_SIMTIME)

        #@160 lumber, build AoW and HH
        #Lumber wisps start mining at 44s, 58s, 68s, 70s, 72s, 86s, 100s, 114s, 128s
        #We already have 60 lumber leftover from start, so we need to gather 100
        #If they gather 5 lumber every 8 seconds, that means we will get to 160 lumber at 96s
        #We will make the trigger 155 lumber, since we will have that at 94s, just before the 2s travel time (the trigger is when the wisp STARTS the action, before travel time)
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(2 * SECONDS_TO_SIMTIME, Trigger(TriggerType.LUMBER_AMOUNT, 155), WorkerTask.LUMBER, "Hunter's Hall", 210, 100, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)))
        self.assertEqual(buildOrder.getCurrentSimTime(), 94 * SECONDS_TO_SIMTIME)
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(2 * SECONDS_TO_SIMTIME, Trigger(TriggerType.LUMBER_AMOUNT, 155), WorkerTask.LUMBER, "Ancient of War", 150, 60, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), True)))
        self.assertEqual(buildOrder.getCurrentSimTime(), 94 * SECONDS_TO_SIMTIME)

        #7th wisp to lumber
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(buildOrder.getCurrentSimTime(), 98 * SECONDS_TO_SIMTIME)

        #Queue 8th wisp -- lumber
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        self.assertEqual(buildOrder.getCurrentSimTime(), 98 * SECONDS_TO_SIMTIME)

        #8th wisp -- lumber
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(buildOrder.getCurrentSimTime(), 112 * SECONDS_TO_SIMTIME)

        #9th wisp -- start
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        self.assertEqual(buildOrder.getCurrentSimTime(), 112 * SECONDS_TO_SIMTIME)

        #@60 lumber -- 2nd AoW
        #Really triggering at 50 lumber to account for travel time
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.LUMBER_AMOUNT, 50), WorkerTask.LUMBER, "Ancient of War", 150, 60, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), True)))
        self.assertEqual(buildOrder.getCurrentSimTime(), 114 * SECONDS_TO_SIMTIME)
        
        #9th wisp to lumber
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, WorkerTask.LUMBER, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(buildOrder.getCurrentSimTime(), 126 * SECONDS_TO_SIMTIME)

        #@40 lumber -- 2nd well
        #Really triggering at 35 lumber to account for travel time
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.LUMBER_AMOUNT, 35), WorkerTask.LUMBER, "Moon Well", 
                                                    180, 40, 10, 50 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)))
        self.assertEqual(buildOrder.getCurrentSimTime(), 128 * SECONDS_TO_SIMTIME)

        #Should have the money for these 3 hunts as soon as they are able to be produced
        #@AoW -- 1st Hunt
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), "Huntress", 195, 20, 3, 30 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Ancient of War")))
        self.assertEqual(buildOrder.getCurrentSimTime(), 156 * SECONDS_TO_SIMTIME)

        #@2nd Aow -- 2nd Hunt
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), "Huntress", 195, 20, 3, 30 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Ancient of War")))
        self.assertEqual(buildOrder.getCurrentSimTime(), 176 * SECONDS_TO_SIMTIME)

        #@1st Hunt -- 3rd Hunt
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), "Huntress", 195, 20, 3, 30 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Ancient of War")))
        self.assertEqual(buildOrder.getCurrentSimTime(), 186 * SECONDS_TO_SIMTIME)