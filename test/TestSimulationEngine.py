import unittest

from SimEngine.SimulationEngine import SimulationEngine
from SimEngine.SimulationConstants import Race

class TestSimulationEngine(unittest.TestCase):
    def testNewBuildOrder(self):
       simEngine = SimulationEngine() 

       simEngine.newBuildOrder(Race.NIGHT_ELF)

       #TODO: Test something meaningful here..