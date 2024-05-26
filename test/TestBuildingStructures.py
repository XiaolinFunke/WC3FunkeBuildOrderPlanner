import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.TimelineTypeEnum import TimelineType
from SimEngine.SimulationConstants import Race, STRUCTURE_STATS_MAP, STARTING_GOLD, STARTING_LUMBER, STARTING_FOOD, STARTING_FOOD_MAX_MAP, SECONDS_TO_SIMTIME, StructureType, WorkerTask
from Test.TestUtilities import buildStructureAndTestResources
from SimEngine.Action import WorkerMovementAction

class TestBuildingStructures(unittest.TestCase):
    def testCreateAltarOfElders(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        buildStructureAndTestResources(self, buildOrder, StructureType.ALTAR_OF_ELDERS, 0, WorkerTask.IDLE)

    def testCreateMoonWell(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        buildStructureAndTestResources(self, buildOrder, StructureType.MOON_WELL, 0, WorkerTask.IDLE)
        buildOrder.simulate(buildOrder.getCurrentSimTime() + (STRUCTURE_STATS_MAP[StructureType.MOON_WELL].mTimeToBuildSec * SECONDS_TO_SIMTIME))
        self.assertEqual(buildOrder.getCurrentResources().getCurrentFoodMax(), STARTING_FOOD_MAX_MAP[Race.NIGHT_ELF] + STRUCTURE_STATS_MAP[StructureType.MOON_WELL].mFoodProvided)