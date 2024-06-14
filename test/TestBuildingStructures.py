import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.TimelineTypeEnum import TimelineType
from SimEngine.SimulationConstants import Race, STARTING_GOLD, STARTING_LUMBER, STARTING_FOOD, STARTING_FOOD_MAX_MAP, SECONDS_TO_SIMTIME, WorkerTask
from Test.TestUtilities import buildStructureAndTestResources

class TestBuildingStructures(unittest.TestCase):
    def testCreateAltarOfElders(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        buildStructureAndTestResources(self, buildOrder, 0, WorkerTask.IDLE, 180, 50, 0, 60 * SECONDS_TO_SIMTIME, False)

    def testCreateMoonWell(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        timeToBuildSec = 50
        foodProvided = 10
        buildStructureAndTestResources(self, buildOrder, 0, WorkerTask.IDLE, 180, 40, foodProvided, timeToBuildSec * SECONDS_TO_SIMTIME, False)
        buildOrder.simulate(buildOrder.getCurrentSimTime() + timeToBuildSec * SECONDS_TO_SIMTIME)
        self.assertEqual(buildOrder.getCurrentResources().getCurrentFoodMax(), STARTING_FOOD_MAX_MAP[Race.NIGHT_ELF] + foodProvided)