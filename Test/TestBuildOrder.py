import unittest

from copy import copy

from SimEngine.BuildOrder import BuildOrder
from SimEngine.ResourceBank import ResourceBank
from SimEngine.SimulationConstants import Race, SECONDS_TO_SIMTIME
from SimEngine.Worker import Worker, WorkerTask
from SimEngine.Trigger import Trigger, TriggerType
from SimEngine.Timeline import Timeline 
from SimEngine.Action import BuildUnitAction, BuildStructureAction, WorkerMovementAction, ShopAction
from Test.UniqueIDHandler import UniqueIDHandler

class TestBuildOrder(unittest.TestCase):
    def testFindMatchingTimeline(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        timelineType = "Altar of Elders"
        inactiveAltarTimeline = Timeline(timelineType, 0, buildOrder.mEventHandler)
        buildOrder.mInactiveTimelines.append(inactiveAltarTimeline)
        self.assertEqual(buildOrder._findMatchingTimeline(timelineType), inactiveAltarTimeline)

        activeAltarTimeline = Timeline(timelineType, 1, buildOrder.mEventHandler)
        buildOrder.mActiveTimelines.append(activeAltarTimeline)
        #Should find active one first
        self.assertEqual(buildOrder._findMatchingTimeline(timelineType), activeAltarTimeline)

        timelineTypeLore = "Ancient of Lore"
        inactiveLoreTimeline = Timeline(timelineTypeLore, 2, buildOrder.mEventHandler)
        buildOrder.mInactiveTimelines.append(inactiveLoreTimeline)
        self.assertEqual(buildOrder._findMatchingTimeline(timelineTypeLore), inactiveLoreTimeline)

        #Can get specific timeline if multiple of same type by using ID
        self.assertEqual(buildOrder._findMatchingTimeline(timelineType, 0), inactiveAltarTimeline)
        self.assertEqual(buildOrder._findMatchingTimeline(timelineType, 1), activeAltarTimeline)
        self.assertEqual(buildOrder._findMatchingTimeline(timelineTypeLore, 2), inactiveLoreTimeline)

        #If ID and TimelineType don't match, should return none
        self.assertEqual(buildOrder._findMatchingTimeline(timelineTypeLore, 0), None)

    def testFindAllMatchingTimelines(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        timelineType = "Altar of Elders"
        inactiveAltarTimeline = Timeline(timelineType, 0, buildOrder.mEventHandler)
        buildOrder.mInactiveTimelines.append(inactiveAltarTimeline)
        self.assertEqual(len(buildOrder.findAllMatchingTimelines(timelineType)), 1)

        activeAltarTimeline = Timeline(timelineType, 1, buildOrder.mEventHandler)
        buildOrder.mActiveTimelines.append(activeAltarTimeline)
        self.assertEqual(len(buildOrder.findAllMatchingTimelines(timelineType)), 2)

        timelineTypeLore = "Ancient of Lore"
        inactiveLoreTimeline = Timeline(timelineTypeLore, 2, buildOrder.mEventHandler)
        buildOrder.mInactiveTimelines.append(inactiveLoreTimeline)
        self.assertEqual(len(buildOrder.findAllMatchingTimelines(timelineTypeLore)), 1)
        self.assertEqual(len(buildOrder.findAllMatchingTimelines(timelineType)), 2)

    def testStartingResources(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        currentResources = buildOrder.getCurrentResources()
        self.assertEqual(currentResources.mCurrentGold, 500)
        self.assertEqual(currentResources.mCurrentLumber, 150)

    #Test that we can execute actions from an ordered list
    def testSimulateOrderedActionList(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        orderedActionList = []

        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, 0, "Tree of Life"))
        orderedActionList.append(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Altar of Elders", 180, 50, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, 1))
        orderedActionList.append(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Moon Well", 180, 40, 10, 50 * SECONDS_TO_SIMTIME, Worker.Wisp.name, 2))

        #Should be no cost, since it's the first hero
        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), "Demon Hunter", 0, 0, 5, 55 * SECONDS_TO_SIMTIME, 3, "Altar of Elders"))

        self.assertEqual(buildOrder.simulateOrderedActionList(orderedActionList), True) 

    #Tests that we properly detect if we will never have enough resources for an action, and fail instead of infinitely looping
    def testFailIfNeverEnoughResources(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        orderedActionList = []

        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, 0, "Tree of Life"))
        orderedActionList.append(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Altar of Elders", 180, 50, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, 1))
        orderedActionList.append(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Moon Well", 180, 40, 10, 50 * SECONDS_TO_SIMTIME, Worker.Wisp.name, 2))

        #We only start with 500 gold, so this moon well should be too expensive, and we have no wisps on gold, so we will never be able to afford it
        orderedActionList.append(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Moon Well", 180, 40, 10, 50 * SECONDS_TO_SIMTIME, Worker.Wisp.name, 3))
        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, 0, "Tree of Life"))

        self.assertEqual(buildOrder.simulateOrderedActionList(orderedActionList), False) 

    #Tests that we properly detect if we will never have the timeline for an action, and fail instead of infinitely looping
    def testFailIfTimelineNeverExists(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        orderedActionList = []

        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), "Demon Hunter", 0, 0, 5, 55 * SECONDS_TO_SIMTIME, 3, "Altar of Elders"))

        self.assertEqual(buildOrder.simulateOrderedActionList(orderedActionList), False) 

    #Tests that we properly detect if we will never have a new worker for an action, and fail instead of infinitely looping
    def testFailIfWorkerNeverMade(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        orderedActionList = []

        orderedActionList.append(WorkerMovementAction(0, Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, WorkerTask.GOLD, Worker.Wisp.name, 0))

        self.assertEqual(buildOrder.simulateOrderedActionList(orderedActionList), False) 

    #Tests that we properly detect that we will never have the resources for an action, even if we have the resources now, but won't by the time the travel time is over
    def testFailIfWontHaveResourcesByTravelTimeAndNeverWill(self):
        actionIDHandler = UniqueIDHandler()
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Try to build two buildings that both have travel time and cost 400 gold. We have 500 gold, so we will think we can afford them initially, but won't be able to by the end of the travel time
        #And since we aren't mining, we never will have the resources.
        #We should just fail instead of infinite looping
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(5 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Fake Building", 
                                                    400, 40, 10, 100 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)))

        self.assertEqual(False, buildOrder.simulateAction(BuildStructureAction(int(5 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Fake Building", 
                                                    400, 40, 10, 100 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)))


    #Test that we will wait until we have the food available for an action
    def testWaitForFoodAvailable(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        orderedActionList = []

        #Add a bunch of wisps for 0 gold, so we will run out of food before gold
        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 0, 0, 1, 14 * SECONDS_TO_SIMTIME, 0, "Tree of Life"))
        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 0, 0, 1, 14 * SECONDS_TO_SIMTIME, 0, "Tree of Life"))
        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 0, 0, 1, 14 * SECONDS_TO_SIMTIME, 0, "Tree of Life"))
        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 0, 0, 1, 14 * SECONDS_TO_SIMTIME, 0, "Tree of Life"))
        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 0, 0, 1, 14 * SECONDS_TO_SIMTIME, 0, "Tree of Life"))

        orderedActionList.append(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Moon Well", 180, 40, 10, 50 * SECONDS_TO_SIMTIME, Worker.Wisp.name, 2))
        #This shouldn't fail, but instead wait until the moon well is done
        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, 0, "Tree of Life"))

        self.assertEqual(buildOrder.simulateOrderedActionList(orderedActionList), True) 

    #Test that we will add an action to a timeline that does not yet exist, if it will the first timeline to be able to handle the action once the timeline exists
    def testScheduleOnTimelineThatDoesntExistYet(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        orderedActionList = []

        ancientOfWarStr = "Ancient of War"
        orderedActionList.append(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, ancientOfWarStr, 150, 60, 0, 60 * SECONDS_TO_SIMTIME, "Wisp", 0, True))
        orderedActionList.append(BuildStructureAction(10, Trigger(TriggerType.ASAP), WorkerTask.IDLE, ancientOfWarStr, 150, 60, 0, 60 * SECONDS_TO_SIMTIME, "Wisp", 0, True))
        #Build two archers - pretend they cost no gold/lumber so we will have enough
        #The second archer should be built at the second AoW
        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), "Archer", 0, 0, 2, 20 * SECONDS_TO_SIMTIME, 0, "Ancient of War"))
        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), "Archer", 0, 0, 2, 20 * SECONDS_TO_SIMTIME, 0, "Ancient of War"))

        self.assertEqual(buildOrder.simulateOrderedActionList(orderedActionList), True) 

        activeTimelines = buildOrder.getActiveTimelines()

        #Check that both AoW timelines have 1 action on them
        for timeline in activeTimelines:
            if timeline.mTimelineType == ancientOfWarStr:
                self.assertEqual(len(timeline.mActions), 1)

    #Test that we properly handle a travel time of zero for an action that could have a non-zero travel time
    def testTravelTimeOfZero(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        self.assertEqual(buildOrder.simulateAction(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Altar of Elders", 180, 50, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, 1)), True)

    #Test that resources aren't lost for building a structure or buying an item until AFTER the travel time, since a skilled player will not tie up the resources until it's necessary (unless it's a case where it doesn't matter)
    def testResourceSpendingWithTravelTime(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        startingResources = copy(buildOrder.getCurrentResources())
        wellStr = "Moon Well"

        #Starting resources: 500/150
        self.assertEqual(buildOrder.simulateAction(BuildStructureAction(5 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, wellStr, 180, 40, 0, 50 * SECONDS_TO_SIMTIME, "Wisp", 0)), True) 
        #Sim time should not advance, so we can queue another action while we wait for the travel time to be done
        #Resources should also not be spent yet
        self.assertEqual(buildOrder.getCurrentSimTime(), 0)
        self.assertEqual(buildOrder.getCurrentResources(), startingResources)

        self.assertEqual(buildOrder.simulateAction(BuildStructureAction(5 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, wellStr, 180, 40, 0, 50 * SECONDS_TO_SIMTIME, "Wisp", 1)), True) 
        self.assertEqual(buildOrder.getCurrentSimTime(), 0)
        self.assertEqual(buildOrder.getCurrentResources(), startingResources)

        #Two wells cost 360/80. So at time 5 seconds we should have 140/70 resources left, only accounting for those
        #Sell TP
        self.assertEqual(buildOrder.simulateAction(ShopAction("Scroll of Town Portal", -195, Trigger(TriggerType.ASAP), "Goblin Merchant", 5 * SECONDS_TO_SIMTIME, 2)), True)
        self.assertEqual(buildOrder.getCurrentSimTime(), 0)
        self.assertEqual(buildOrder.getCurrentResources(), startingResources)

        #However, if we won't have enough resources by the end of the travel time, the action start time should be pushed back until we will have resources by the end of the travel time
        self.assertEqual(buildOrder.simulateAction(WorkerMovementAction(5 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 3)), True)

        #Now, at time 5 seconds we should have 335/70 resources left
        #We should have enough gold for this, but are short 30 lumber
        #We have one worker mining (5 lumber every 8 seconds, starting at second 5), so we should have the required amount of lumber by time 53s
        #Travel time to build it is 7 seconds, so the start time should actually be pushed back to 46s, NOT 53s 
        self.assertEqual(buildOrder.simulateAction(BuildStructureAction(7 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Hunter's Hall", 210, 100, 0, 60 * SECONDS_TO_SIMTIME, "Wisp", 1)), True) 
        self.assertEqual(buildOrder.getCurrentSimTime(), 46 * SECONDS_TO_SIMTIME)

    #Test that the travel time works properly with the NEXT_WORKER_BUILT trigger. We don't want the travel time to start before the worker is actually finished, assuming we are building with that worker (won't necessarily be the case, but usually it will be, and we don't really know)
    #It should also work if we don't yet have enough resources -- it should just be pushed back slightly
    def testTravelTimeNextWorkerTrigger(self):
        actionIDHandler = UniqueIDHandler()
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Send all 5 wisps to gold immediately
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(0 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(0 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(0 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(0 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, actionIDHandler.getNextID())))
        self.assertEqual(True, buildOrder.simulateAction(WorkerMovementAction(0 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, actionIDHandler.getNextID())))

        #Queue wisp
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))

        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(8 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, "Altar of Elders", 
                                              180, 50, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)))
        #Time should be at the time the wisp was finished building, not before
        self.assertEqual(buildOrder.getCurrentSimTime(), 14 * SECONDS_TO_SIMTIME)

        #Queue 2nd wisp
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))

        #We start with 500 gold, spend 180 + 60 + 60 on Altar + 2 wisp, so 200 left
        #Then, we have mined with 5 wisps for 28 seconds = 280. So should have 480 gold
        #Attempt to build a fake building that costs 580 gold - shouldn't be able to build it for another 10 seconds
        #Travel time is 5 seconds, so time should be 33 seconds rather than 38
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(5 * SECONDS_TO_SIMTIME), Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, "Fake Building", 
                                              580, 0, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)))
        self.assertEqual(buildOrder.getCurrentSimTime(), 33 * SECONDS_TO_SIMTIME)

    def testActionCompletionPercentageTrigger(self):
        actionIDHandler = UniqueIDHandler()
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Add a bunch of resources so we don't run out (greedisgood)
        buildOrder.mCurrentResources = buildOrder.mCurrentResources + ResourceBank(Race.NIGHT_ELF, 1000, 1000, 0)

        #Queue first wisp
        actionIDWispBuild = actionIDHandler.getNextID()
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDWispBuild, "Tree of Life")))
        #Time shouldn't have advanced yet
        self.assertEqual(buildOrder.getCurrentSimTime(), 0)

        #Queue altar when wisp is halfway done
        actionIDAltarBuild = actionIDHandler.getNextID()
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(8 * SECONDS_TO_SIMTIME), Trigger(TriggerType.PERCENT_OF_ONGOING_ACTION, 50, actionIDWispBuild), WorkerTask.IDLE, "Altar of Elders", 
                                              180, 50, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDAltarBuild, False)))
        #Time should be at 7 seconds, since that's halfway to the wisp being built (and the travel time doesn't affect the current time)
        self.assertEqual(buildOrder.getCurrentSimTime(), 7 * SECONDS_TO_SIMTIME)

        #Queue 2nd wisp when altar is 10% done
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.PERCENT_OF_ONGOING_ACTION, 10, actionIDAltarBuild), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        #Altar actually starts building at 15 seconds, due to the travel time. So it will by 10% done at 21 seconds
        self.assertEqual(buildOrder.getCurrentSimTime(), 21 * SECONDS_TO_SIMTIME)

        #Build moon well when altar is 100% complete
        actionIDMoonWellBuild = actionIDHandler.getNextID()
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.PERCENT_OF_ONGOING_ACTION, 100, actionIDAltarBuild), WorkerTask.IN_PRODUCTION, "Moon Well", 
                                                    180, 40, 10, 50 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDMoonWellBuild, False)))
        #Altar should be done at 75 seconds
        self.assertEqual(buildOrder.getCurrentSimTime(), 75 * SECONDS_TO_SIMTIME)

        #Build wisp when moon well is 0% complete -- this should mean it builds at the same time the well actually starts (after travel time)
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.PERCENT_OF_ONGOING_ACTION, 0, actionIDMoonWellBuild), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDHandler.getNextID(), "Tree of Life")))
        #Altar actually starts building at 15 seconds, due to the travel time. So it will by 10% done at 21 seconds
        self.assertEqual(buildOrder.getCurrentSimTime(), 77 * SECONDS_TO_SIMTIME)

    #Test that we can have an action completion trigger for a decimal percentage, and that it works whether that percentage ends on an integer simtime or not
    def testActionCompletionTriggerDecimalPercentage(self):
        actionIDHandler = UniqueIDHandler()
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Add a bunch of resources so we don't run out (greedisgood)
        buildOrder.mCurrentResources = buildOrder.mCurrentResources + ResourceBank(Race.NIGHT_ELF, 1000, 1000, 0)

        #Build fake building that takes 100 seconds
        actionIDBuild = actionIDHandler.getNextID()
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(0 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Fake Building", 
                                                    180, 40, 10, 100 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDBuild, False)))

        #Should be at exactly 895 sim-seconds
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.PERCENT_OF_ONGOING_ACTION, 89.5, actionIDBuild), WorkerTask.IDLE, "Fake Building2", 
                                                    180, 40, 10, 50 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)))
        self.assertEqual(buildOrder.getCurrentSimTime(), 89.5 * SECONDS_TO_SIMTIME)

        #Should be at 895.3 sim-seconds, which means it should actually trigger at 896
        self.assertEqual(True, buildOrder.simulateAction(BuildStructureAction(int(2 * SECONDS_TO_SIMTIME), Trigger(TriggerType.PERCENT_OF_ONGOING_ACTION, 89.53, actionIDBuild), WorkerTask.IDLE, "Fake Building2", 
                                                    180, 40, 10, 50 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)))
        self.assertEqual(buildOrder.getCurrentSimTime(), 89.6 * SECONDS_TO_SIMTIME)


    #Test that it fails if you specify a non-existent action ID
    def testActionCompletionPercentageTriggerBadActionID(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Add a bunch of resources so we don't run out (greedisgood)
        buildOrder.mCurrentResources = buildOrder.mCurrentResources + ResourceBank(Race.NIGHT_ELF, 1000, 1000, 0)

        #Action ID is nonexistent
        badActionID = 100
        self.assertEqual(False, buildOrder.simulateAction(BuildStructureAction(int(8 * SECONDS_TO_SIMTIME), Trigger(TriggerType.PERCENT_OF_ONGOING_ACTION, 50, badActionID), WorkerTask.IDLE, "Altar of Elders", 
                                              180, 50, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, 0, False)))

    #Test that it fails if you specify a percentage that is not between 0 and 100
    def testActionCompletionPercentageTriggerBadPercentage(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Queue first wisp
        actionIDWispBuild = 0
        self.assertEqual(True, buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, actionIDWispBuild, "Tree of Life")))
        #Time shouldn't have advanced yet
        self.assertEqual(buildOrder.getCurrentSimTime(), 0)

        #Queue altar when wisp is halfway done
        actionIDAltarBuild = 1
        self.assertEqual(False, buildOrder.simulateAction(BuildStructureAction(int(8 * SECONDS_TO_SIMTIME), Trigger(TriggerType.PERCENT_OF_ONGOING_ACTION, -1, actionIDWispBuild), WorkerTask.IDLE, "Altar of Elders", 
                                              180, 50, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDAltarBuild, False)))

        self.assertEqual(False, buildOrder.simulateAction(BuildStructureAction(int(8 * SECONDS_TO_SIMTIME), Trigger(TriggerType.PERCENT_OF_ONGOING_ACTION, 110, actionIDWispBuild), WorkerTask.IDLE, "Altar of Elders", 
                                              180, 50, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDAltarBuild, False)))

        self.assertEqual(False, buildOrder.simulateAction(BuildStructureAction(int(8 * SECONDS_TO_SIMTIME), Trigger(TriggerType.PERCENT_OF_ONGOING_ACTION, -100, actionIDWispBuild), WorkerTask.IDLE, "Altar of Elders", 
                                              180, 50, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDAltarBuild, False)))




