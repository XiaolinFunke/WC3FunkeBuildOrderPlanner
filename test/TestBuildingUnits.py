import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.TimelineTypeEnum import TimelineType
from SimEngine.SimulationConstants import Race, UnitType, UNIT_STATS_MAP, STARTING_GOLD, STARTING_LUMBER, STARTING_FOOD, STARTING_FOOD_MAX_MAP, SECONDS_TO_SIMTIME, StructureType, WorkerTask
from Test.TestUtilities import buildStructureAndTestResources, buildUnitAndTestResources, buildHeroAndTestResources

class TestBuildingUnits(unittest.TestCase):
    def testCreateWisp(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Should be 5 workers to start
        self.assertEqual(len(buildOrder.findAllMatchingTimelines(timelineType=TimelineType.WORKER)), 5)

        simTime = 0
        #This is number of wisps we can build by resources, but food will be the limit first
        #numWorkersCanBuild = math.floor(STARTING_GOLD / UNIT_STATS_MAP[UnitType.WISP].mGoldCost)
        numWorkersCanBuild = 5
        for i in range(numWorkersCanBuild):
            buildUnitAndTestResources(self, buildOrder, UnitType.WISP)

            simTime += UNIT_STATS_MAP[UnitType.WISP].mTimeToBuildSec * SECONDS_TO_SIMTIME
            buildOrder.simulate(simTime)
            #Now should be one more worker timeline
            self.assertEqual(len(buildOrder.findAllMatchingTimelines(timelineType=TimelineType.WORKER)), 6 + i)

        #TODO: Re-enable this check once we are checking that we will eventually be able to afford the worker, or it will loop infinitely
        #Now we should be out of food to build workers
        #self.assertEqual(False, buildOrder.buildUnit(UnitType.WISP))

    def testCreateDemonHunter(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        buildUnitAndTestResources(self, buildOrder, UnitType.WISP)
        buildStructureAndTestResources(self, buildOrder, StructureType.ALTAR_OF_ELDERS, 0, WorkerTask.IDLE)
        buildStructureAndTestResources(self, buildOrder, StructureType.MOON_WELL, 0, WorkerTask.IDLE)
        #80 gold

        #Should be no cost, since it's the first hero
        buildHeroAndTestResources(self, buildOrder, UnitType.DEMON_HUNTER)



