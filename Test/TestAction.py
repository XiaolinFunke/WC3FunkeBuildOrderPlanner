import unittest

from SimEngine.Action import BuildStructureAction
from Test.UniqueIDHandler import UniqueIDHandler
from SimEngine.SimulationConstants import SECONDS_TO_SIMTIME
from SimEngine.Worker import Worker, WorkerTask
from SimEngine.Trigger import Trigger, TriggerType

class TestAction(unittest.TestCase):
    #Test that the getPercentComplete method returns the expected percentages in various situations
    def testGetPercentComplete(self):
        actionIDHandler = UniqueIDHandler()
        action = BuildStructureAction(int(8 * SECONDS_TO_SIMTIME), Trigger(TriggerType.ASAP, Worker.Wisp.name), WorkerTask.IDLE, "Altar of Elders", 
                                              180, 50, 0, 60 * SECONDS_TO_SIMTIME, Worker.Wisp.name, actionIDHandler.getNextID(), False)
        #Set the start time to mimic it being scheduled
        action.mStartTime = 2 * SECONDS_TO_SIMTIME

        #Any time before the travel time is done should return -1 to indicate the action hasn't started yet
        self.assertEqual(action.getPercentComplete(2 * SECONDS_TO_SIMTIME), -1)
        self.assertEqual(action.getPercentComplete(7 * SECONDS_TO_SIMTIME), -1)
        self.assertEqual(action.getPercentComplete(8.5 * SECONDS_TO_SIMTIME), -1)

        #Right at start, it should be 0%
        self.assertEqual(action.getPercentComplete(10 * SECONDS_TO_SIMTIME), 0.0)

        #Any time after the action is complete should be 100%
        self.assertEqual(action.getPercentComplete(70 * SECONDS_TO_SIMTIME), 100.0)
        self.assertEqual(action.getPercentComplete(70.4 * SECONDS_TO_SIMTIME), 100.0)
        self.assertEqual(action.getPercentComplete(1000 * SECONDS_TO_SIMTIME), 100.0)

        #Check times in between 0 and 100%
        self.assertAlmostEqual(action.getPercentComplete(11 * SECONDS_TO_SIMTIME), 1.67, 2)
        self.assertEqual(action.getPercentComplete(25 * SECONDS_TO_SIMTIME), 25.0)
        self.assertAlmostEqual(action.getPercentComplete(30 * SECONDS_TO_SIMTIME), 33.33, 2)
        self.assertEqual(action.getPercentComplete(40 * SECONDS_TO_SIMTIME), 50.0)
        self.assertAlmostEqual(action.getPercentComplete(60 * SECONDS_TO_SIMTIME), 83.33, 2)