import copy

from SimEngine.SimulationConstants import TriggerType, Trigger
from SimEngine.Action import BuildStructureAction, BuildUnitAction

#Builds a unit and tests that the resources are spent properly
def buildUnitAndTestResources(testClass, buildOrder, goldCost, lumberCost, foodCost, duration, requiredTimelineType):
    action = BuildUnitAction(Trigger(TriggerType.ASAP), "", goldCost, lumberCost, foodCost, duration, requiredTimelineType)
    #Mark as not executing, so we simulate right up until when we would do that action but don't actually do it
    #This way, we know what the resources are just before the action
    action.mDontExecute = True
    #Should return False because we aren't actually executing the action
    testClass.assertEqual(False, buildOrder.simulateAction(action))
    prevResources = copy.deepcopy(buildOrder.getCurrentResources()) 

    action.mDontExecute = False
    testClass.assertEqual(True, buildOrder.simulateAction(action))

    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentGold(), prevResources.getCurrentGold() - goldCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentLumber(), prevResources.getCurrentLumber() - lumberCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFood(), prevResources.getCurrentFood() + foodCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFoodMax(), prevResources.getCurrentFoodMax())

#Builds a structure and tests that the resources are spent properly
def buildStructureAndTestResources(testClass, buildOrder, travelTime, workerTask, goldCost, lumberCost, foodProvided, duration, requiredTimelineType, consumesWorker):
    #Mark as not executing, so we simulate right up until when we would do that action but don't actually do it
    #This way, we nkow what the resources are just before the action
    action = BuildStructureAction(travelTime, Trigger(TriggerType.ASAP), workerTask, "", goldCost, lumberCost, foodProvided, duration, requiredTimelineType, consumesWorker)
    action.mDontExecute = True

    testClass.assertEqual(False, buildOrder.simulateAction(action))
    prevResources = copy.deepcopy(buildOrder.getCurrentResources()) 

    action.mDontExecute = False
    testClass.assertEqual(True, buildOrder.simulateAction(action))

    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentGold(), prevResources.getCurrentGold() - goldCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentLumber(), prevResources.getCurrentLumber() - lumberCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFood(), prevResources.getCurrentFood())

    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFoodMax(), prevResources.getCurrentFoodMax())
    #Can't test that it provides the correct amount of food here, since it won't provide taht until it's done and we don't want to simulate forward in this function in case we need to do other stuff first