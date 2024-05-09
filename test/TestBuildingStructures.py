import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.Timeline import TimelineType
from SimEngine.SimulationConstants import Race, STRUCTURE_STATS_MAP, STARTING_GOLD, STARTING_LUMBER, STARTING_FOOD, STARTING_FOOD_MAX_MAP, SECONDS_TO_SIMTIME, StructureType, WorkerTask

def buildStructureAndTestResources(testClass, buildOrder, structureType, travelTime, workerTask, prevFoodMax, prevGold = STARTING_GOLD, prevLumber = STARTING_LUMBER, prevFood = STARTING_FOOD):
    testClass.assertEqual(True, buildOrder.buildStructure(structureType, travelTime, workerTask))

    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentGold(), prevGold - STRUCTURE_STATS_MAP[structureType].mGoldCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentLumber(), prevLumber - STRUCTURE_STATS_MAP[structureType].mLumberCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFood(), prevFood)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFoodMax(), prevFoodMax + STRUCTURE_STATS_MAP[structureType].mFoodProvided)

class TestBuildingStructures(unittest.TestCase):
    def testCreateAltarOfElders(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Send a worker to gold so we can grab it to build the structure
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=TimelineType.WORKER)
        buildOrder.sendWorkerToMine(timelineID=workerTimelines[0].getTimelineID(), travelTime=0)

        buildStructureAndTestResources(self, buildOrder, StructureType.ALTAR_OF_ELDERS, 0, WorkerTask.GOLD, buildOrder.getCurrentResources().getCurrentFoodMax())