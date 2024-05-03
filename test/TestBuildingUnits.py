import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.SimulationConstants import Race, UnitType

class TestBuildingUnits(unittest.TestCase):
    def testCreateWisp(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        self.assertEqual(True, buildOrder.buildUnit(UnitType.WISP))