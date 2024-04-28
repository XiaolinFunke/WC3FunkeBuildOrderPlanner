import unittest

from SimEngine.BuildOrder import BuildOrder
from SimEngine.SimulationConstants import Race, SECONDS_TO_SIMTIME, STARTING_GOLD, STARTING_LUMBER
from SimEngine.Timeline import TimelineType

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

        #All workers mine immediately
        #TODO: This is acting like we only have one wisp if they all have the same simtime and travel time
        buildOrder.sendWorkerToMine(timelineID=0, travelTime=0)
        buildOrder.sendWorkerToMine(timelineID=1, travelTime=0)
        buildOrder.sendWorkerToMine(timelineID=2, travelTime=0)
        buildOrder.sendWorkerToMine(timelineID=3, travelTime=0)
        buildOrder.sendWorkerToMine(timelineID=4, travelTime=0)

        timeSec = 3600
        expectedGoldAmount = STARTING_GOLD + (timeSec * 10)

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    def testElfGoldMiningStartRealistic(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Workers mine in a staggered fashion. More realistic
        buildOrder.sendWorkerToMine(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=1, travelTime=1.2 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=2, travelTime=1.5 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=3, travelTime=1.8 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=4, travelTime=2 * SECONDS_TO_SIMTIME)

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

        buildOrder.sendWorkerToMine(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)

        #3601 so it's a multiple of 5 + 1, meaning we should gain gold right at that time
        timeSec = 3601
        expectedGoldAmount = STARTING_GOLD + ((timeSec - 1) / 5 * 10)

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    def testElfGoldMiningTwoWorkersSimple(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        buildOrder.sendWorkerToMine(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=1, travelTime=1 * SECONDS_TO_SIMTIME)

        #3601 so it's a multiple of 5 + 1, meaning we should gain gold right at that time
        timeSec = 3601
        expectedGoldAmount = STARTING_GOLD + ((timeSec - 1) * 2 / 5 * 10)

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    def testElfGoldMiningThreeWorkersSimple(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        buildOrder.sendWorkerToMine(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=1, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=2, travelTime=1 * SECONDS_TO_SIMTIME)

        #3601 so it's a multiple of 5 + 1, meaning we should gain gold right at that time
        timeSec = 3601
        expectedGoldAmount = STARTING_GOLD + ((timeSec - 1) * 3 / 5 * 10)

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    def testElfGoldMiningFourWorkersSimple(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        buildOrder.sendWorkerToMine(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=1, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=2, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=3, travelTime=1 * SECONDS_TO_SIMTIME)

        #3601 so it's a multiple of 5 + 1, meaning we should gain gold right at that time
        timeSec = 3601
        expectedGoldAmount = STARTING_GOLD + ((timeSec - 1) * 4 / 5 * 10)

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    #Test that no progress is kept if we remove all of the wisps from the mine
    def testElfGoldMiningNoProgressKept(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        buildOrder.sendWorkerToMine(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=1, travelTime=1 * SECONDS_TO_SIMTIME)

        #4 wisp-seconds of mining has been done, which is not enough to gain 10 gold
        buildOrder.simulate(3 * SECONDS_TO_SIMTIME)
        buildOrder.removeWorkerFromMine()
        buildOrder.removeWorkerFromMine()

        #Progress toward the 10 gold should have been reset, so we won't gain any here either
        buildOrder.simulate(4 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.simulate(7 * SECONDS_TO_SIMTIME)
        buildOrder.removeWorkerFromMine()

        #Progress toward the 10 gold should have been reset, so we won't gain any here either
        buildOrder.simulate(8 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=1, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=2, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=3, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.simulate(10 * SECONDS_TO_SIMTIME)
        buildOrder.removeWorkerFromMine()
        buildOrder.removeWorkerFromMine()
        buildOrder.removeWorkerFromMine()
        buildOrder.removeWorkerFromMine()

        buildOrder.simulate(11 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        #Don't remove worker here, so we should finally gain our first 10 gold at 17 seconds

        timeSec = 17
        expectedGoldAmount = STARTING_GOLD + 10

        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    #Test that partial progress toward next gold is tracked correctly as we add an remove in a complex fashion
    def testElfGoldMiningPartialProgressWithRemovingAndAdding(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Add one worker and have it get 10 gold
        buildOrder.sendWorkerToMine(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        timeSec = 6
        expectedGoldAmount = STARTING_GOLD + 10
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

        #Add a second worker for 1s and then remove it. Ensure the next 10 gold is at the right time
        buildOrder.simulate(6 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=1, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.simulate(8 * SECONDS_TO_SIMTIME)
        buildOrder.removeWorkerFromMine()
        timeSec = 10
        expectedGoldAmount += 10
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

        #Add 2 workers (3 total)
        buildOrder.sendWorkerToMine(timelineID=1, travelTime=0)
        buildOrder.sendWorkerToMine(timelineID=2, travelTime=1 * SECONDS_TO_SIMTIME)
        timeSec = 12
        expectedGoldAmount += 10
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

        #Remove 1 (2 left)
        buildOrder.simulate(13 * SECONDS_TO_SIMTIME)
        buildOrder.removeWorkerFromMine()
        timeSec = 14
        expectedGoldAmount += 10
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

        #Add 3 more back in in a staggered fashion (5 total)
        #2.2 wisp-seconds toward 10 gold
        buildOrder.sendWorkerToMine(timelineID=2, travelTime=1.1 * SECONDS_TO_SIMTIME)
        #0.6 more wisp-seconds (2.8 total)
        buildOrder.sendWorkerToMine(timelineID=3, travelTime=1.3 * SECONDS_TO_SIMTIME)
        #1.2 more wisp-seconds (4.0 total)
        buildOrder.sendWorkerToMine(timelineID=4, travelTime=1.6 * SECONDS_TO_SIMTIME)
        #1.0 more wisp-seconds needed. so 1.0 /5 = 0.2 seconds more
        timeSec = 15.8
        expectedGoldAmount += 10
        testGoldAmountPrecise(timeSec, expectedGoldAmount, buildOrder, self)

    #Test that rounding errors don't accumulate while mining gold
    def testElfGoldMiningRounding(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        buildOrder.sendWorkerToMine(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToMine(timelineID=1, travelTime=1 * SECONDS_TO_SIMTIME)
        #0.4 wisp-seconds
        buildOrder.sendWorkerToMine(timelineID=2, travelTime=1.2 * SECONDS_TO_SIMTIME)
        #0.3 wisp-seconds (0.7 total)
        buildOrder.sendWorkerToMine(timelineID=3, travelTime=1.3 * SECONDS_TO_SIMTIME)
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

    @unittest.skip("Re-enable when individual wisps are targeted by commands")
    def testElfLumberMiningNoProgressKept(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        buildOrder.sendWorkerToLumber(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        #7 seconds of mining has been done, which is not enough to gain 5 lumber
        buildOrder.removeWorkerFromLumber(simTime=8)

        buildOrder.simulate(10 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToLumber(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        #5 seconds of mining has been done, which is not enough to gain 5 lumber
        buildOrder.simulate(16 * SECONDS_TO_SIMTIME)
        buildOrder.removeWorkerFromLumber(simTime=16)

        buildOrder.simulate(18 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToLumber(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        #First 5 lumber should be mined at 26 seconds

        timeSec = 26
        expectedLumberAmount = STARTING_LUMBER + 5

        testLumberAmountPrecise(timeSec, expectedLumberAmount, buildOrder, self)

    def testElfLumberMiningFourWorkersSimple(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Workers all start mining at the exact same time
        buildOrder.sendWorkerToLumber(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToLumber(timelineID=1, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToLumber(timelineID=2, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToLumber(timelineID=3, travelTime=1 * SECONDS_TO_SIMTIME)

        #3601 because it's 1 + a multiple of 8, so we should get lumber at that time
        timeSec = 3601
        expectedLumberAmount = STARTING_LUMBER + (5 * 4 * (timeSec - 1)/ 8)

        testLumberAmountPrecise(timeSec, expectedLumberAmount, buildOrder, self)

    def testElfLumberMiningFiveWorkersRealistic(self):
        buildOrder = BuildOrder(Race.NIGHT_ELF)

        #Worker mining is staggered
        buildOrder.sendWorkerToLumber(timelineID=0, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.simulate(1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToLumber(timelineID=1, travelTime=1 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToLumber(timelineID=2, travelTime=2 * SECONDS_TO_SIMTIME)
        buildOrder.simulate(2 * SECONDS_TO_SIMTIME)
        buildOrder.sendWorkerToLumber(timelineID=3, travelTime=2 * SECONDS_TO_SIMTIME)

        #3601 because it's 1 + a multiple of 8, so we should get lumber at that time from the first worker
        timeSec = 3601
        #Subtract 15 because not all the wisps have gotten their lumber yet
        expectedLumberAmount = STARTING_LUMBER + (5 * 4 * (timeSec - 1) / 8) - 15
        testLumberAmountPrecise(timeSec, expectedLumberAmount, buildOrder, self)
        #Other 3 wisps should get their lumber 1 second later than the previous
        testLumberAmountPrecise(timeSec + 1, expectedLumberAmount + 5, buildOrder, self)
        testLumberAmountPrecise(timeSec + 2, expectedLumberAmount + 10, buildOrder, self)
        testLumberAmountPrecise(timeSec + 3, expectedLumberAmount + 15, buildOrder, self)


