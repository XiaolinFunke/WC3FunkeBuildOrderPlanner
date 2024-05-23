import copy

from SimEngine.SimulationConstants import Race, UnitType, UNIT_STATS_MAP, STARTING_GOLD, STARTING_LUMBER, STARTING_FOOD, STARTING_FOOD_MAX_MAP, SECONDS_TO_SIMTIME, STRUCTURE_STATS_MAP, TriggerType, Trigger
from SimEngine.BuildOrder import CurrentResources
from SimEngine.Action import BuildStructureAction, BuildUnitAction

#Builds a unit and tests that the resources are spent properly
def buildUnitAndTestResources(testClass, buildOrder, unitType):
    prevResources = copy.deepcopy(buildOrder.getCurrentResources()) 

    action = BuildUnitAction(Trigger(TriggerType.ASAP), unitType)
    testClass.assertEqual(True, buildOrder.simulateAction(action))

    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentGold(), prevResources.getCurrentGold() - UNIT_STATS_MAP[unitType].mGoldCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentLumber(), prevResources.getCurrentLumber() - UNIT_STATS_MAP[unitType].mLumberCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFood(), prevResources.getCurrentFood() + UNIT_STATS_MAP[unitType].mFoodCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFoodMax(), prevResources.getCurrentFoodMax())

#Builds a hero and tests that the resources are spent properly
def buildHeroAndTestResources(testClass, buildOrder, unitType):
    prevResources = copy.deepcopy(buildOrder.getCurrentResources()) 

    action = BuildUnitAction(Trigger(TriggerType.ASAP), unitType)
    testClass.assertEqual(True, buildOrder.simulateAction(action))

    #First hero is free, for others we should check that resources are properly spent
    if buildOrder.mHeroesBuilt != 1:
        testClass.assertEqual(buildOrder.getCurrentResources().getCurrentGold(), prevResources.getCurrentGold() - UNIT_STATS_MAP[unitType].mGoldCost)
        testClass.assertEqual(buildOrder.getCurrentResources().getCurrentLumber(), prevResources.getCurrentLumber() - UNIT_STATS_MAP[unitType].mLumberCost)
    else:
        testClass.assertEqual(buildOrder.getCurrentResources().getCurrentGold(), prevResources.getCurrentGold())
        testClass.assertEqual(buildOrder.getCurrentResources().getCurrentLumber(), prevResources.getCurrentLumber())
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFood(), prevResources.getCurrentFood() + UNIT_STATS_MAP[unitType].mFoodCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFoodMax(), prevResources.getCurrentFoodMax())

#Builds a structure and tests that the resources are spent properly
def buildStructureAndTestResources(testClass, buildOrder, structureType, travelTime, workerTask):
    prevResources = copy.deepcopy(buildOrder.getCurrentResources()) 

    action = BuildStructureAction(travelTime, Trigger(TriggerType.ASAP), workerTask, structureType)
    testClass.assertEqual(True, buildOrder.simulateAction(action))

    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentGold(), prevResources.getCurrentGold() - STRUCTURE_STATS_MAP[structureType].mGoldCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentLumber(), prevResources.getCurrentLumber() - STRUCTURE_STATS_MAP[structureType].mLumberCost)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFood(), prevResources.getCurrentFood())

    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFoodMax(), prevResources.getCurrentFoodMax())
    buildOrder.simulate(buildOrder.getCurrSimTime() + STRUCTURE_STATS_MAP[structureType].mTimeToBuildSec * SECONDS_TO_SIMTIME)
    testClass.assertEqual(buildOrder.getCurrentResources().getCurrentFoodMax(), prevResources.getCurrentFoodMax() + STRUCTURE_STATS_MAP[structureType].mFoodProvided)