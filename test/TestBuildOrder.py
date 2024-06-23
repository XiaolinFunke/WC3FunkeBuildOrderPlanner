import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.SimulationConstants import Race, Trigger, TriggerType, WorkerTask, Worker, SECONDS_TO_SIMTIME
from SimEngine.Timeline import Timeline 
from SimEngine.Action import BuildUnitAction, BuildStructureAction

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

        #We only start iwth 500 gold, so this moon well should be too expensive, and we have no wisps on gold, so we will never be able to afford it
        orderedActionList.append(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, "Moon Well", 180, 40, 10, 50 * SECONDS_TO_SIMTIME, Worker.Wisp.name, 3))

        self.assertEqual(buildOrder.simulateOrderedActionList(orderedActionList), False) 

    #Test that we will wait until we have the food available for an action, if we ever will, otherwise fail
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