import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.SimulationConstants import Race, STARTING_GOLD, STARTING_LUMBER
from SimEngine.Timeline import Timeline, TimelineType, Action, BuildUnitAction

class TestBuildOrder(unittest.TestCase):
    def testFindMatchingTimeline(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        inactiveAltarTimeline = Timeline(TimelineType.ALTAR_OF_ELDERS, 0, buildOrder.mEventHandler)
        buildOrder.mInactiveTimelines.append(inactiveAltarTimeline)
        self.assertEqual(buildOrder.findMatchingTimeline(TimelineType.ALTAR_OF_ELDERS), inactiveAltarTimeline)

        activeAltarTimeline = Timeline(TimelineType.ALTAR_OF_ELDERS, 1, buildOrder.mEventHandler)
        buildOrder.mActiveTimelines.append(activeAltarTimeline)
        #Should find active one first
        self.assertEqual(buildOrder.findMatchingTimeline(TimelineType.ALTAR_OF_ELDERS), activeAltarTimeline)

        inactiveLoreTimeline = Timeline(TimelineType.ANCIENT_OF_LORE, 2, buildOrder.mEventHandler)
        buildOrder.mInactiveTimelines.append(inactiveLoreTimeline)
        self.assertEqual(buildOrder.findMatchingTimeline(TimelineType.ANCIENT_OF_LORE), inactiveLoreTimeline)

        #Can get specific timeline if multiple of same type by using ID
        self.assertEqual(buildOrder.findMatchingTimeline(TimelineType.ALTAR_OF_ELDERS, 0), inactiveAltarTimeline)
        self.assertEqual(buildOrder.findMatchingTimeline(TimelineType.ALTAR_OF_ELDERS, 1), activeAltarTimeline)
        self.assertEqual(buildOrder.findMatchingTimeline(TimelineType.ANCIENT_OF_LORE, 2), inactiveLoreTimeline)

        #If ID and TimelineType don't match, should return none
        self.assertEqual(buildOrder.findMatchingTimeline(TimelineType.ANCIENT_OF_LORE, 0), None)

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

    def testAddActionToMatchingTimeline(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        inactiveAltarTimeline = Timeline(TimelineType.ALTAR_OF_ELDERS, 0, buildOrder.mEventHandler)
        buildOrder.mInactiveTimelines.append(inactiveAltarTimeline)
        self.assertEqual(buildOrder.findMatchingTimeline(TimelineType.ALTAR_OF_ELDERS), inactiveAltarTimeline)

        action = BuildUnitAction(goldCost=0, lumberCost=0, foodCost=0, startTime=10, duration=0, requiredTimelineType=TimelineType.ALTAR_OF_ELDERS, events=[], actionName="Test action")
        self.assertEqual(buildOrder.addActionToMatchingTimeline(action), True)

        self.assertEqual(inactiveAltarTimeline.getNextAction(0), action)

        #Should fail if timeline type doesn't exist
        badAction = BuildUnitAction(goldCost=0, lumberCost=0, foodCost=0, startTime=10, duration=0, requiredTimelineType=TimelineType.ANCIENT_OF_LORE, events=[], actionName="Test action")
        self.assertEqual(buildOrder.addActionToMatchingTimeline(badAction), False)

    def testStartingResources(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        currentResources = buildOrder.getCurrentResources()
        self.assertEqual(currentResources.mCurrentGold, 500)
        self.assertEqual(currentResources.mCurrentLumber, 150)