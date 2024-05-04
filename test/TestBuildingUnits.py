import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.Timeline import TimelineType
from SimEngine.SimulationConstants import Race, UnitType, UNIT_STATS_MAP, STARTING_GOLD, STARTING_LUMBER, STARTING_FOOD, STARTING_FOOD_MAX_MAP, SECONDS_TO_SIMTIME

def buildUnitAndTestResources(testClass, buildOrder, unitType, prevFoodMax, prevGold = STARTING_GOLD, prevLumber = STARTING_LUMBER, prevFood = STARTING_FOOD):
    testClass.assertEqual(True, buildOrder.buildUnit(unitType))

    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentGold(), prevGold - UNIT_STATS_MAP[unitType].mGoldCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentLumber(), prevLumber - UNIT_STATS_MAP[unitType].mLumberCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFood(), prevFood + UNIT_STATS_MAP[unitType].mFoodCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFoodMax(), prevFoodMax)

class TestBuildingUnits(unittest.TestCase):
    def testCreateWisp(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        buildUnitAndTestResources(self, buildOrder, UnitType.WISP, STARTING_FOOD_MAX_MAP[Race.NIGHT_ELF])

        #Should be 5 workers before this one is made
        self.assertEqual(len(buildOrder.findAllMatchingTimelines(timelineType=TimelineType.WORKER)), 5)
        buildOrder.simulate(UNIT_STATS_MAP[UnitType.WISP].mTimeToBuildSec * SECONDS_TO_SIMTIME)
        #Now should be 6 worker timelines
        self.assertEqual(len(buildOrder.findAllMatchingTimelines(timelineType=TimelineType.WORKER)), 6)