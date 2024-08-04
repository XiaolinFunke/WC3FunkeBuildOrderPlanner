import unittest

from copy import copy

from SimEngine.BuildOrder import BuildOrder
from SimEngine.SimulationConstants import Race, SECONDS_TO_SIMTIME
from SimEngine.Worker import Worker, WorkerTask
from SimEngine.Trigger import Trigger, TriggerType
from SimEngine.Timeline import Timeline 
from SimEngine.Action import BuildUnitAction, BuildStructureAction, WorkerMovementAction, ShopAction

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

    #Test that resources aren't lost for building a structure or buying an item until AFTER the travel time, since a skilled player will not tie up the resources until it's necessary (unless it's a case where it doesn't matter)
    def testResourceSpendingWithTravelTime(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        startingResources = copy(buildOrder.getCurrentResources)
        wellStr = "Moon Well"

        #Starting resources: 500/150
        self.assertEqual(buildOrder.simulateAction(BuildStructureAction(5 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, wellStr, 180, 40, 0, 50 * SECONDS_TO_SIMTIME, "Wisp", 0)), True) 
        #Sim time should not advance, so we can queue another action while we wait for the travel time to be done
        #Resources should also not be spent yet
        self.assertEqual(buildOrder.getCurrentSimTime(), 0)
        self.assertEqual(buildOrder.getCurrentResources, startingResources)

        self.assertEqual(buildOrder.simulateAction(BuildStructureAction(5 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, wellStr, 180, 40, 0, 50 * SECONDS_TO_SIMTIME, "Wisp", 1)), True) 
        self.assertEqual(buildOrder.getCurrentSimTime(), 0)
        self.assertEqual(buildOrder.getCurrentResources, startingResources)

        #Two wells cost 360/80. So at time 5 seconds we should have 140/70 resources left
        #Sell TP
        self.assertEqual(buildOrder.simulateAction(ShopAction("Scroll of Town Portal", -195, Trigger(TriggerType.ASAP), "Goblin Merchant", 5 * SECONDS_TO_SIMTIME, 2)), True)
        self.assertEqual(buildOrder.getCurrentSimTime(), 0)
        self.assertEqual(buildOrder.getCurrentResources, startingResources)

        #However, if we won't have enough resources by the end of the travel time, the action start time should be pushed back until we will have resources by the end of the travel time
        self.assertEqual(buildOrder.simulateAction(WorkerMovementAction(5 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 3)), True)

        print(buildOrder.getCurrentResources())
        #Now, at time 5 seconds we should have 335/70 resources left
        #We should have enough gold for this, but are short 30 lumber
        #We have one worker mining (5 lumber every 8 seconds, starting at second 5), so we should have the required amount of lumber by time 53s
        #Travel time to build it is 7 seconds, so the start time should actually be pushed back to 46s, NOT 53s 
        self.assertEqual(buildOrder.simulateAction(BuildStructureAction(7 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Hunter's Hall", 210, 100, 0, 60 * SECONDS_TO_SIMTIME, "Wisp", 1)), True) 
        self.assertEqual(buildOrder.getCurrentSimTime(), 46 * SECONDS_TO_SIMTIME)

    #TODO: Add test that shows travel time is properly handled for a worker that's IN_PRODUCTION as well... because it can't start the travel time until it's actually built -- Some idle time will also need to be added if we don't have enough resources in that case


