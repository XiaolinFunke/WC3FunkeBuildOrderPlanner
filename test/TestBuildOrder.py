import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.SimulationConstants import Race, Trigger, TriggerType, UnitType, StructureType, WorkerTask
from SimEngine.Timeline import Timeline 
from SimEngine.TimelineTypeEnum import TimelineType
from SimEngine.Action import BuildUnitAction, BuildStructureAction

class TestBuildOrder(unittest.TestCase):
    def testFindMatchingTimeline(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        inactiveAltarTimeline = Timeline(TimelineType.ALTAR_OF_ELDERS, 0, buildOrder.mEventHandler)
        buildOrder.mInactiveTimelines.append(inactiveAltarTimeline)
        self.assertEqual(buildOrder._findMatchingTimeline(TimelineType.ALTAR_OF_ELDERS), inactiveAltarTimeline)

        activeAltarTimeline = Timeline(TimelineType.ALTAR_OF_ELDERS, 1, buildOrder.mEventHandler)
        buildOrder.mActiveTimelines.append(activeAltarTimeline)
        #Should find active one first
        self.assertEqual(buildOrder._findMatchingTimeline(TimelineType.ALTAR_OF_ELDERS), activeAltarTimeline)

        inactiveLoreTimeline = Timeline(TimelineType.ANCIENT_OF_LORE, 2, buildOrder.mEventHandler)
        buildOrder.mInactiveTimelines.append(inactiveLoreTimeline)
        self.assertEqual(buildOrder._findMatchingTimeline(TimelineType.ANCIENT_OF_LORE), inactiveLoreTimeline)

        #Can get specific timeline if multiple of same type by using ID
        self.assertEqual(buildOrder._findMatchingTimeline(TimelineType.ALTAR_OF_ELDERS, 0), inactiveAltarTimeline)
        self.assertEqual(buildOrder._findMatchingTimeline(TimelineType.ALTAR_OF_ELDERS, 1), activeAltarTimeline)
        self.assertEqual(buildOrder._findMatchingTimeline(TimelineType.ANCIENT_OF_LORE, 2), inactiveLoreTimeline)

        #If ID and TimelineType don't match, should return none
        self.assertEqual(buildOrder._findMatchingTimeline(TimelineType.ANCIENT_OF_LORE, 0), None)

    def testFindAllMatchingTimelines(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        inactiveAltarTimeline = Timeline(TimelineType.ALTAR_OF_ELDERS, 0, buildOrder.mEventHandler)
        buildOrder.mInactiveTimelines.append(inactiveAltarTimeline)
        self.assertEqual(len(buildOrder.findAllMatchingTimelines(TimelineType.ALTAR_OF_ELDERS)), 1)

        activeAltarTimeline = Timeline(TimelineType.ALTAR_OF_ELDERS, 1, buildOrder.mEventHandler)
        buildOrder.mActiveTimelines.append(activeAltarTimeline)
        self.assertEqual(len(buildOrder.findAllMatchingTimelines(TimelineType.ALTAR_OF_ELDERS)), 2)

        inactiveLoreTimeline = Timeline(TimelineType.ANCIENT_OF_LORE, 2, buildOrder.mEventHandler)
        buildOrder.mInactiveTimelines.append(inactiveLoreTimeline)
        self.assertEqual(len(buildOrder.findAllMatchingTimelines(TimelineType.ANCIENT_OF_LORE)), 1)
        self.assertEqual(len(buildOrder.findAllMatchingTimelines(TimelineType.ALTAR_OF_ELDERS)), 2)

    def testStartingResources(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        currentResources = buildOrder.getCurrentResources()
        self.assertEqual(currentResources.mCurrentGold, 500)
        self.assertEqual(currentResources.mCurrentLumber, 150)

    #Test that we can execute actions from an ordered list
    def testSimulateOrderedActionList(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        orderedActionList = []

        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), UnitType.WISP))
        orderedActionList.append(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, StructureType.ALTAR_OF_ELDERS))
        orderedActionList.append(BuildStructureAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, StructureType.MOON_WELL))

        #Should be no cost, since it's the first hero
        orderedActionList.append(BuildUnitAction(Trigger(TriggerType.ASAP), UnitType.DEMON_HUNTER))

        self.assertEqual(buildOrder.simulateOrderedActionList(orderedActionList), True) 