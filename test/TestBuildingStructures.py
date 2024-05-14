import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.TimelineTypeEnum import TimelineType
from SimEngine.SimulationConstants import Race, STRUCTURE_STATS_MAP, STARTING_GOLD, STARTING_LUMBER, STARTING_FOOD, STARTING_FOOD_MAX_MAP, SECONDS_TO_SIMTIME, StructureType, WorkerTask
from Test.TestUtilities import buildStructureAndTestResources

class TestBuildingStructures(unittest.TestCase):
    def testCreateAltarOfElders(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Send a worker to gold so we can grab it to build the structure
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=TimelineType.WORKER)
        buildOrder.sendWorkerToMine(timelineID=workerTimelines[0].getTimelineID(), travelTime=0)

        buildStructureAndTestResources(self, buildOrder, StructureType.ALTAR_OF_ELDERS, 0, WorkerTask.GOLD)

    def testCreateMoonWell(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Send a worker to gold so we can grab it to build the structure
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=TimelineType.WORKER)
        buildOrder.sendWorkerToMine(timelineID=workerTimelines[0].getTimelineID(), travelTime=0)

        buildStructureAndTestResources(self, buildOrder, StructureType.MOON_WELL, 0, WorkerTask.GOLD)