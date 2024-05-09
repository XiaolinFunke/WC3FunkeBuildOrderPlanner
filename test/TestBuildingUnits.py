import unittest
import math

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

        #Should be 5 workers to start
        self.assertEqual(len(buildOrder.findAllMatchingTimelines(timelineType=TimelineType.WORKER)), 5)

        simTime = 0
        #This is number of wisps we can build by resources, but food will be the limit first
        #numWorkersCanBuild = math.floor(STARTING_GOLD / UNIT_STATS_MAP[UnitType.WISP].mGoldCost)
        numWorkersCanBuild = 5
        currentGold = STARTING_GOLD
        currentFood = STARTING_FOOD
        for i in range(numWorkersCanBuild):
            buildUnitAndTestResources(self, buildOrder, UnitType.WISP, STARTING_FOOD_MAX_MAP[Race.NIGHT_ELF], currentGold, STARTING_LUMBER, currentFood)

            currentGold -= UNIT_STATS_MAP[UnitType.WISP].mGoldCost
            currentFood += UNIT_STATS_MAP[UnitType.WISP].mFoodCost
            simTime += UNIT_STATS_MAP[UnitType.WISP].mTimeToBuildSec * SECONDS_TO_SIMTIME
            buildOrder.simulate(simTime)
            #Now should be one more worker timeline
            self.assertEqual(len(buildOrder.findAllMatchingTimelines(timelineType=TimelineType.WORKER)), 6 + i)

        #TODO: Re-enable this check once we are checking that we will eventually be able to afford the worker, or it will loop infinitely
        #Now we should be out of food to build workers
        #self.assertEqual(False, buildOrder.buildUnit(UnitType.WISP))
