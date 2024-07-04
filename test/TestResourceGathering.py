import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.SimulationConstants import Race, SECONDS_TO_SIMTIME, STARTING_GOLD, STARTING_LUMBER
from SimEngine.Worker import WorkerTask, Worker
from SimEngine.Trigger import Trigger, TriggerType
from SimEngine.Action import WorkerMovementAction, BuildUnitAction

#Checks the gold amount at the specified time BUT also
#checks the simtime right before that time, to ensure that the gold was achieved at exactly that time
#That way, we can't be off by even 1 simtime unit and still have the test pass
def testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, testClass):
    testResourceAmountPrecise(timeSec,expectedGoldAmount, buildOrder.getCurrentResources().getCurrentGold, buildOrder, testClass )

def testLumberAmountPrecise(timeSec, expectedLumberAmount, buildOrder, testClass):
    testResourceAmountPrecise(timeSec,expectedLumberAmount, buildOrder.getCurrentResources().getCurrentLumber, buildOrder, testClass )

def testResourceAmountPrecise(timeSec, expectedResourceAmount, currentResourceFunc, buildOrder, testClass):
    simTime = round(timeSec * SECONDS_TO_SIMTIME)

    #First, simulate to just before the time of interest. That way, we can double-check that the gold amount we want is
    #only achieved right on the time we expect
    justBeforeSimTime = simTime - 1
    buildOrder.simulate(justBeforeSimTime)
    testClass.assertLess(currentResourceFunc(), expectedResourceAmount, "Actual resource amount was not less than expected at the time step directly before")

    #Now, simulate to the time of interest
    buildOrder.simulate(simTime)
    testClass.assertEqual(currentResourceFunc(), expectedResourceAmount, "Actual resource amount did not match expected")

class TestResourceGathering(unittest.TestCase):
    def testElfGoldMiningStartSimple(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        #All workers mine immediately
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 3, workerTimelines[2].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 4, workerTimelines[3].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 5, workerTimelines[4].getTimelineID()))

        timeSec = 3600
        expectedGoldAmount = STARTING_GOLD + (timeSec * 10)

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    def testElfGoldMiningStartRealistic(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        #Workers mine in a staggered fashion. More realistic
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1.2 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1.5 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 3, workerTimelines[2].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1.8 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 4, workerTimelines[3].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(2 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 5, workerTimelines[4].getTimelineID()))

        #It takes 5 wisp-seconds to make 10 gold
        #1 second of no money (0 progress to 10 gold)
        #0.2 seconds of single wisp (0.2 wisp-seconds progress to 10 gold)
        #then 0.3 seconds of 2 wisps (0.6 wisp-seconds progress to 10 gold)
        #then 0.3 seconds of 3 wisps (0.9 wisp-seconds progress to 10 gold)
        #then 0.2 seconds of 4 wisps (0.8 wisp-seconds progress to 10 gold)
        #then 5 wisps for rest
        #So, at 2 seconds, we have 5 wisps in mine and have mined for 2.5 wisp-seconds - that's halfway to 10 gold
        #That should mean our first 10 gold will come in half the time it would have if we just started mining with all 5 wisps right at 2s
        #So, first 10 gold should be at 2.5s instead of 3s

        #Do half-second so we are right on the time we would get 10 gold
        timeSec = 3600.5
        #Subtract 1.5 from time, since we get our first gold at 2.5s instead of 1s
        expectedGoldAmount = STARTING_GOLD + (timeSec - 1.5) * 10

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    def testElfGoldMiningOneWorkerSimple(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))

        #3601 so it's a multiple of 5 + 1, meaning we should gain gold right at that time
        timeSec = 3601
        expectedGoldAmount = STARTING_GOLD + ((timeSec - 1) / 5 * 10)

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    def testElfGoldMiningTwoWorkersSimple(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))

        #3601 so it's a multiple of 5 + 1, meaning we should gain gold right at that time
        timeSec = 3601
        expectedGoldAmount = STARTING_GOLD + ((timeSec - 1) * 2 / 5 * 10)

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    def testElfGoldMiningThreeWorkersSimple(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 3, workerTimelines[2].getTimelineID()))

        #3601 so it's a multiple of 5 + 1, meaning we should gain gold right at that time
        timeSec = 3601
        expectedGoldAmount = STARTING_GOLD + ((timeSec - 1) * 3 / 5 * 10)

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    def testElfGoldMiningFourWorkersSimple(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 3, workerTimelines[2].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 4, workerTimelines[3].getTimelineID()))

        #3601 so it's a multiple of 5 + 1, meaning we should gain gold right at that time
        timeSec = 3601
        expectedGoldAmount = STARTING_GOLD + ((timeSec - 1) * 4 / 5 * 10)

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    #Test that no progress is kept if we remove all of the wisps from the mine
    def testElfGoldMiningNoProgressKept(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))

        #4 wisp-seconds of mining has been done, which is not enough to gain 10 gold
        buildOrder.simulate(3 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.GOLD, WorkerTask.LUMBER, Worker.Wisp.name, 3, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.GOLD, WorkerTask.LUMBER, Worker.Wisp.name, 4, workerTimelines[1].getTimelineID()))

        #Progress toward the 10 gold should have been reset, so we won't gain any here either
        buildOrder.simulate(4 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.LUMBER, WorkerTask.GOLD, Worker.Wisp.name, 5, workerTimelines[0].getTimelineID()))
        buildOrder.simulate(7 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.GOLD, WorkerTask.LUMBER, Worker.Wisp.name, 6, workerTimelines[0].getTimelineID()))

        #Progress toward the 10 gold should have been reset, so we won't gain any here either
        buildOrder.simulate(8 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.LUMBER, WorkerTask.GOLD, Worker.Wisp.name, 7, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.LUMBER, WorkerTask.GOLD, Worker.Wisp.name, 8, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 9, workerTimelines[2].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 10, workerTimelines[3].getTimelineID()))
        buildOrder.simulate(10 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.GOLD, WorkerTask.LUMBER, Worker.Wisp.name, 11, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.GOLD, WorkerTask.LUMBER, Worker.Wisp.name, 12, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.GOLD, WorkerTask.LUMBER, Worker.Wisp.name, 13, workerTimelines[2].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.GOLD, WorkerTask.LUMBER, Worker.Wisp.name, 14, workerTimelines[3].getTimelineID()))

        buildOrder.simulate(11 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.LUMBER, WorkerTask.GOLD, Worker.Wisp.name, 15, workerTimelines[0].getTimelineID()))
        #Don't remove worker here, so we should finally gain our first 10 gold at 17 seconds

        timeSec = 17
        expectedGoldAmount = STARTING_GOLD + 10

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    #Test that partial progress toward next gold is tracked correctly as we add an remove in a complex fashion
    def testElfGoldMiningPartialProgressWithRemovingAndAdding(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        #Add one worker and have it get 10 gold
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        timeSec = 6
        expectedGoldAmount = STARTING_GOLD + 10
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

        #Add a second worker for 1s and then remove it. Ensure the next 10 gold is at the right time
        buildOrder.simulate(6 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))
        buildOrder.simulate(8 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.GOLD, WorkerTask.LUMBER, Worker.Wisp.name, 3, workerTimelines[1].getTimelineID()))
        timeSec = 10
        expectedGoldAmount += 10
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

        #Add 2 workers (3 total)
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.LUMBER, WorkerTask.GOLD, Worker.Wisp.name, 4, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 5, workerTimelines[2].getTimelineID()))
        timeSec = 12
        expectedGoldAmount += 10
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

        #Remove 1 (2 left)
        buildOrder.simulate(13 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.GOLD, WorkerTask.LUMBER, Worker.Wisp.name, 6, workerTimelines[2].getTimelineID()))
        timeSec = 14
        expectedGoldAmount += 10
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

        #Add 3 more back in in a staggered fashion (5 total)
        #2.2 wisp-seconds toward 10 gold
        buildOrder.simulateAction(WorkerMovementAction(1.1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.LUMBER, WorkerTask.GOLD, Worker.Wisp.name, 7, workerTimelines[2].getTimelineID()))
        #0.6 more wisp-seconds (2.8 total)
        buildOrder.simulateAction(WorkerMovementAction(1.3 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 8, workerTimelines[3].getTimelineID()))
        #1.2 more wisp-seconds (4.0 total)
        buildOrder.simulateAction(WorkerMovementAction(1.6 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 9, workerTimelines[4].getTimelineID()))
        #1.0 more wisp-seconds needed. so 1.0 /5 = 0.2 seconds more
        timeSec = 15.8
        expectedGoldAmount += 10
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    #Test that rounding errors don't accumulate while mining gold
    def testElfGoldMiningRounding(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))
        #0.4 wisp-seconds
        buildOrder.simulateAction(WorkerMovementAction(1.2 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 3, workerTimelines[2].getTimelineID()))
        #0.3 wisp-seconds (0.7 total)
        buildOrder.simulateAction(WorkerMovementAction(1.3 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 4, workerTimelines[3].getTimelineID()))
        #4.3 wisp-seconds remaining until next 10 gold
        #Time-wise, should be 4.3 / 4 seconds = 1.075 seconds from now, at time 1.375s
        #If our simuilation steps are only 10th of a second, we can't accurately simulate that
        #If we round to 1.1 seconds, we'll have an error of 0.025 seconds
        #So, every 4 times we round, we will accumulate 10th of a second of error
        #We should be handling this in the sim engine so that this error does not keep accumulating

        #First 10 gold is at 1.375s. Each subsequent gold should be at 1.25s (5/4) intervals
        #So, we should also gain 10 gold at time 3601.375
        #Since our steps are in 10ths of a second, we should be gaining that 10 gold either at 3601.3 or 3601.4 if we aren't accumulating error
        timeSec = 3601.4
        expectedGoldAmount = STARTING_GOLD + ((timeSec - 1.4) * 4 / 5 * 10)

        buildOrder.simulate(round((timeSec - 0.1) * SECONDS_TO_SIMTIME))

        #We should not be more than 1 sim time step off of accurate
        #At one step earlier, we should be either correct already, or short 10 gold
        self.assertTrue(buildOrder.getCurrentResources().mCurrentGold == expectedGoldAmount or buildOrder.getCurrentResources().mCurrentGold == expectedGoldAmount - 10, 
                        "Current gold is " + str(buildOrder.getCurrentResources().mCurrentGold) + ", but expected " + str(expectedGoldAmount) + " or " + str(expectedGoldAmount - 10))
        buildOrder.simulate(round(timeSec * SECONDS_TO_SIMTIME))
        #At the later step, we should have the correct amount of gold
        self.assertEqual( buildOrder.getCurrentResources().mCurrentGold, expectedGoldAmount )

    def testElfLumberMiningNoProgressKept(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        #7 seconds of mining has been done, which is not enough to gain 5 lumber
        buildOrder.simulate(7 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.LUMBER, WorkerTask.GOLD, Worker.Wisp.name, 2, workerTimelines[0].getTimelineID()))

        buildOrder.simulate(10 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.GOLD, WorkerTask.LUMBER, Worker.Wisp.name, 3, workerTimelines[0].getTimelineID()))

        #5 seconds of mining has been done, which is not enough to gain 5 lumber
        buildOrder.simulate(16 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.LUMBER, WorkerTask.GOLD, Worker.Wisp.name, 4, workerTimelines[0].getTimelineID()))

        buildOrder.simulate(18 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.GOLD, WorkerTask.LUMBER, Worker.Wisp.name, 5, workerTimelines[0].getTimelineID()))

        #First 5 lumber should be mined at 27 seconds
        timeSec = 27
        expectedLumberAmount = STARTING_LUMBER + 5

        testLumberAmountPrecise(timeSec, expectedLumberAmount, buildOrder, self)

    def testElfLumberMiningFourWorkersSimple(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        #Workers all start mining at the exact same time
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 3, workerTimelines[2].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(1 * SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 4, workerTimelines[3].getTimelineID()))

        #3601 because it's 1 + a multiple of 8, so we should get lumber at that time
        timeSec = 3601
        expectedLumberAmount = STARTING_LUMBER + (5 * 4 * (timeSec - 1)/ 8)

        testLumberAmountPrecise(timeSec, expectedLumberAmount, buildOrder, self)

    def testElfLumberMiningFiveWorkersRealistic(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        #Worker mining is staggered
        buildOrder.simulateAction(WorkerMovementAction(1*SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        buildOrder.simulate(1 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(1*SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(2*SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 3, workerTimelines[2].getTimelineID()))
        buildOrder.simulate(2 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(WorkerMovementAction(2*SECONDS_TO_SIMTIME, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 4, workerTimelines[3].getTimelineID()))

        #3601 because it's 1 + a multiple of 8, so we should get lumber at that time from the first worker
        timeSec = 3601
        #Subtract 15 because not all the wisps have gotten their lumber yet
        expectedLumberAmount = STARTING_LUMBER + (5 * 4 * (timeSec - 1) / 8) - 15
        testLumberAmountPrecise(timeSec, expectedLumberAmount, buildOrder, self)
        #Other 3 wisps should get their lumber 1 second later than the previous
        testLumberAmountPrecise(timeSec + 1, expectedLumberAmount + 5, buildOrder, self)
        testLumberAmountPrecise(timeSec + 2, expectedLumberAmount + 10, buildOrder, self)
        testLumberAmountPrecise(timeSec + 3, expectedLumberAmount + 15, buildOrder, self)

    def testElfMiningWithNewWisp(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        #All workers mine immediately
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 3, workerTimelines[2].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 4, workerTimelines[3].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 5, workerTimelines[4].getTimelineID()))

        buildOrder.simulate(1 * SECONDS_TO_SIMTIME)
        buildOrder.simulateAction(BuildUnitAction(Trigger(TriggerType.ASAP), Worker.Wisp.name, 60, 0, 1, 14 * SECONDS_TO_SIMTIME, 6, Worker.Wisp.name))

        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.NEXT_WORKER_BUILT, Worker.Wisp.name), WorkerTask.IN_PRODUCTION, WorkerTask.GOLD, Worker.Wisp.name, 7))

        #New worker should come out at 15 seconds and start mining gold
        #So, we have 4 workers mining for 15 seconds (120 gold)
        #And then 5 workers mining for the rest
        timeSec = 3600
        wispGoldCost = 60
        expectedGoldAmount = (STARTING_GOLD - wispGoldCost) + 120 + ((timeSec - 15) * 10)
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    def testElfSwitchingWorkerLumberToGold(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        #All workers mine immediately
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 3, workerTimelines[2].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 4, workerTimelines[3].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 5, workerTimelines[4].getTimelineID()))

        buildOrder.simulate(5 * SECONDS_TO_SIMTIME)
        #After 5 seconds, move the lumber worker to gold
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.LUMBER, WorkerTask.GOLD, Worker.Wisp.name, 6, workerTimelines[4].getTimelineID()))

        #We have 4 workers mining for 5 seconds (40 gold)
        #And then 5 workers mining for the rest
        timeSec = 3600
        expectedGoldAmount = STARTING_GOLD + 40 + ((timeSec - 5) * 10)
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)
        #We shouldn't have been on lumber long enough to gain any
        self.assertEqual(buildOrder.getCurrentResources().getCurrentLumber(), STARTING_LUMBER, "Actual lumber amount did not match expected")

    def testElfSwitchingWorkerGoldToLumber(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)
        workerTimelines = buildOrder.findAllMatchingTimelines(timelineType=Worker.Wisp.name)

        #All workers mine immediately
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 1, workerTimelines[0].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 2, workerTimelines[1].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 3, workerTimelines[2].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.GOLD, Worker.Wisp.name, 4, workerTimelines[3].getTimelineID()))
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.IDLE, WorkerTask.LUMBER, Worker.Wisp.name, 5, workerTimelines[4].getTimelineID()))

        buildOrder.simulate(15 * SECONDS_TO_SIMTIME)
        #After 15 seconds, move a gold worker to lumber
        buildOrder.simulateAction(WorkerMovementAction(0, Trigger(TriggerType.ASAP), WorkerTask.GOLD, WorkerTask.LUMBER, Worker.Wisp.name, 6, workerTimelines[3].getTimelineID()))

        #We have 4 workers mining for 15 seconds (120 gold)
        #And then 3 workers mining for the rest
        timeSec = 3600
        expectedGoldAmount = STARTING_GOLD + 120 + ((timeSec - 15) * (3/5) * 10)
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

        #We have 1 worker lumbering for 15 seconds (5 lumber, 5 more at 16 seconds, 24 seconds, etc.)
        #And then we add a second for the rest (first 5 lumber at 23 seconds)
        #so, at 24 seconds we have +20 lumber. Will have 10 more at 32 seconds, 10 more every 8 seconds
        timeSec = 7200
        expectedLumberAmount = STARTING_LUMBER + 20 + ((timeSec - 24) / 8 * 10)
        testLumberAmountPrecise(timeSec, expectedLumberAmount, buildOrder, self)
