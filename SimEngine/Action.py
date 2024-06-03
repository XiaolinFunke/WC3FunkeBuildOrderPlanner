from enum import Enum, auto
from SimEngine.SimulationConstants import UNIT_STATS_MAP, STRUCTURE_STATS_MAP, ITEM_STATS_MAP, UPGRADE_STATS_MAP, SECONDS_TO_SIMTIME, Trigger, UnitType, StructureType, WorkerTask, ItemType, UpgradeType
from SimEngine.TimelineTypeEnum import TimelineType
from pydoc import locate

class ActionType(Enum):
    BuildUnit = auto()
    BuildStructure = auto()
    Shop = auto()
    WorkerMovement = auto()
    BuildUpgrade = auto()

class Action:
    def __init__(self, goldCost, lumberCost, travelTime, trigger, duration, requiredTimelineType, interruptable = False, actionNote = ""):
        #TODO: Don't necessarily need to set gold and lumber, etc. on this, since we have unitType, sctructureType, etc. Could just grab those values when we pay for the action
        self.mGoldCost = goldCost
        self.mLumberCost = lumberCost
        #What triggers us to do this action (amount of gold, lumber, etc.)
        self.mTrigger = trigger
        #Start time starts at the beginning of the travel time 
        #In simtime
        self.mStartTime = -1 #Set to -1 so we know this is unscheduled as of yet
        #Travel time takes place at the very beginning of the action (start time)
        self.mTravelTime = travelTime
        #Duration does not include travel time - So full duration is duration + travel time
        self.mDuration = duration
        self.mRequiredTimelineType = requiredTimelineType
        self.mActionNote = actionNote
        #Some actions, such as mining actions, are interruptable, and can be overwritten by other actions
        self.mInterruptable = interruptable
        #List of events
        self.mAssociatedEvents = []

        #Some Actions shouldn't be shown to the user and shouldn't make a timeline 'Active'
        self.mIsInvisibleToUser = False

        #If True, simulate up to when the action would need to be taken, but don't actually execute it
        #Just used for testing at the moment
        self.mDontExecute = False

    #TODO: Any fancy way we could mark variables as ones that should be serialized rather than having to specify here?
    #Pare down to only relevant fields for JSON encoding and get as dict
    #@param isOnTimeline - If True, include stuff like start time and duration (needed for when we're printing the Timelines as JSON, but not for ordered action list)
    def getAsDictForSerialization(self, isOnTimeline = True):
        dict = {
            'mType' : self.__class__.__name__,
            'mTrigger' : self.mTrigger.getAsDictForSerialization(),
            'mTravelTime' : self.mTravelTime,
            'mActionNote' : self.mActionNote
        }

        if isOnTimeline:
            dict['mStartTime'] = self.mStartTime
            dict['mDuration'] = self.mDuration

        return dict

    #Used to deserialize JSON (after converting the JSON to dict)
    #This base class method just gets action arguments that are common to all actions and then determines which sub-class method to call
    @staticmethod
    def getActionFromDict(actionDict):
        #See https://stackoverflow.com/questions/11775460/lexical-cast-from-string-to-type - locate is used to find the type
        actionType = locate('SimEngine.Action.' + actionDict['mType'])

        trigger = Trigger.getTriggerFromDict(actionDict['mTrigger'])
        actionNote = actionDict['mActionNote']
        action = actionType.getActionFromDict(actionDict, trigger, actionNote)

        return action

    def setCostToFree(self):
        self.mGoldCost = 0
        self.mLumberCost = 0

    def getTrigger(self):
        return self.mTrigger

    def payForAction(self, currentResources):
        currentResources.deductGold(self.mGoldCost)
        currentResources.deductLumber(self.mLumberCost)

    def setStartTime(self, startTime):
        self.mStartTime = startTime

    def getStartTime(self):
        return self.mStartTime

    def setAssociatedEvents(self, events):
        self.mAssociatedEvents = events

    #If there is only one event, get it. Otherwise return None
    def getAssociatedEvent(self):
        if len(self.mAssociatedEvents) == 1:
            return self.mAssociatedEvents[0]
        print("Tried to get associated event, but there were", len(self.mAssociatedEvents), "associated events")
        return None

    def getAssociatedEvents(self):
        return self.mAssociatedEvents
    
    def getRequiredTimelineType(self):
        return self.mRequiredTimelineType

    def getActionTypeStr(self):
        return ""

    def __str__(self):
        return "Action:\"" + self.__class__.__name__ + " : " + self.getActionTypeStr() + " (" + str(self.getStartTime()) + " - " + str(self.getStartTime() + self.mDuration) + ") - " + str(len(self.mAssociatedEvents)) + " events"

    def __repr__(self):
        return self.__str__()

class BuildUnitAction(Action):
    def __init__(self, trigger, unitType, actionNote = ""):
        unitStats = UNIT_STATS_MAP[unitType]
        super().__init__(unitStats.mGoldCost, unitStats.mLumberCost, 0, trigger, unitStats.mTimeToBuildSec * SECONDS_TO_SIMTIME, unitStats.mRequiredTimelineType, False, actionNote)
        self.mFoodCost = unitStats.mFoodCost
        self.mUnitType = unitType

    def getActionTypeStr(self):
        return str(self.mUnitType)

    def payForAction(self, currentResources):
        super().payForAction(currentResources)
        currentResources.increaseFoodUsed(self.mFoodCost)

    def getActionType(self):
        return ActionType.BuildUnit

    def getAsDictForSerialization(self, isOnTimeline = True):
        dict = super().getAsDictForSerialization(isOnTimeline)
        dict['mUnitType'] = self.mUnitType.name

        return dict

    #Used to deserialize JSON (after converting the JSON to dict)
    @staticmethod
    def getActionFromDict(actionDict, trigger, actionNote):
        #TODO: We aren't using travel time here (and in other places). Should we also not bother to serialize that to avoid confusion? (Since it's always 0)
        unitType = UnitType[actionDict['mUnitType']]
        action = BuildUnitAction(trigger, unitType, actionNote)

        return action

class BuildStructureAction(Action):
    def __init__(self, travelTime, trigger, currentWorkerTask, structureType, isInterruptable = False, consumesWorker = False, actionNote = ""):
        structureStats = STRUCTURE_STATS_MAP[structureType]
        super().__init__(structureStats.mGoldCost, structureStats.mLumberCost, travelTime, trigger, structureStats.mTimeToBuildSec * SECONDS_TO_SIMTIME, TimelineType.WORKER, isInterruptable, actionNote)
        #TODO: Are some of these Action members even really necessary to track? Like, won't food provided really just be handled by the associated event?
        #TODO: Shouldn't need to pass isInteruruptable or consumesWorker, we can get that from the structure type
        self.mFoodProvided = structureStats.mFoodProvided
        self.mConsumesWorker = consumesWorker
        self.mCurrentWorkerTask = currentWorkerTask
        self.mStructureType = structureType

    def getActionTypeStr(self):
        return str(self.mStructureType)

    def payForAction(self, currentResources):
        super().payForAction(currentResources)
        if self.mConsumesWorker:
            currentResources.decreaseFoodUsedByOne()
        #Don't increase max food by food provided, since that only happens when a building is complete, not paid for

    def getActionType(self):
        return ActionType.BuildStructure

    def getAsDictForSerialization(self, isOnTimeline = True):
        dict = super().getAsDictForSerialization(isOnTimeline)
        dict['mCurrentWorkerTask'] = self.mCurrentWorkerTask.name
        dict['mStructureType'] = self.mStructureType.name

        return dict

    #Used to deserialize JSON (after converting the JSON to dict)
    @staticmethod
    def getActionFromDict(actionDict, trigger, actionNote):
        travelTime = int(actionDict['mTravelTime'])
        currentWorkerTask = WorkerTask[actionDict['mCurrentWorkerTask']]
        structureType = StructureType[actionDict['mStructureType']]
        action = BuildStructureAction(travelTime, trigger, currentWorkerTask, structureType, False, False, actionNote)

        return action

class ShopAction(Action):
    def __init__(self, trigger, itemType, isBeingSold, actionNote = ""):
        itemStats = ITEM_STATS_MAP[itemType]
        super().__init__(itemStats.mGoldCost, 0, 0, trigger, 0, itemStats.requiredTimelineType, True, False, actionNote)
        self.mItemType = itemType
        #If True, we are selling the item, if False, buying it
        self.mIsBeingSold = isBeingSold

    def getActionTypeStr(self):
        return str(self.mItemType)

    def getActionType(self):
        return ActionType.Shop

    def getAsDictForSerialization(self, isOnTimeline = True):
        dict = super().getAsDictForSerialization(isOnTimeline)
        dict['mItemType'] = self.mItemType.name
        dict['mIsBeingSold'] = self.mIsBeingSold

        return dict

    #Used to deserialize JSON (after converting the JSON to dict)
    @staticmethod
    def getActionFromDict(actionDict, trigger, actionNote):
        itemType = ItemType[actionDict['mItemType']]
        isBeingSold = bool(actionDict['mIsBeingSold'])
        action = ShopAction(trigger, itemType, isBeingSold, actionNote)

        return action

class WorkerMovementAction(Action):
    def __init__(self, travelTime, trigger, currentWorkerTask, desiredWorkerTask, workerTimelineID = None, actionNote = ""):
        super().__init__(0, 0, travelTime, trigger, 0, TimelineType.WORKER, True, actionNote)
        self.mCurrentWorkerTask = currentWorkerTask
        self.mDesiredWorkerTask = desiredWorkerTask
        self.mWorkerTimelineID = workerTimelineID

    def getActionTypeStr(self):
        return "to" + str(self.mDesiredWorkerTask)

    def getActionType(self):
        return ActionType.WorkerMovement

    def getAsDictForSerialization(self, isOnTimeline = True):
        dict = super().getAsDictForSerialization(isOnTimeline)
        dict['mCurrentWorkerTask'] = self.mCurrentWorkerTask.name
        dict['mDesiredWorkerTask'] = self.mDesiredWorkerTask.name

        if not isOnTimeline:
            dict['mWorkerTimelineID'] = self.mWorkerTimelineID

        return dict

    #Used to deserialize JSON (after converting the JSON to dict)
    @staticmethod
    def getActionFromDict(actionDict, trigger, actionNote):
        travelTime = int(actionDict['mTravelTime'])
        currentWorkerTask = WorkerTask[actionDict['mCurrentWorkerTask']]
        desiredWorkerTask = WorkerTask[actionDict['mDesiredWorkerTask']]
        strTimelineID = actionDict['mWorkerTimelineID']
        workerTimelineID = None if strTimelineID == None else int(strTimelineID)
        action =WorkerMovementAction(travelTime, trigger, currentWorkerTask, desiredWorkerTask, workerTimelineID, actionNote)

        return action

class BuildUpgradeAction(Action):
    def __init__(self, trigger, upgradeType, actionNote = ""):
        upgradeStats = UPGRADE_STATS_MAP[upgradeType]
        super().__init__(upgradeStats.mGoldCost, upgradeStats.mLumberCost, 0, trigger, upgradeStats.mTimeToBuildSec * SECONDS_TO_SIMTIME, upgradeStats.mRequiredTimelineType, False, actionNote)
        self.mUpgradeType = upgradeType

    def getActionTypeStr(self):
        return str(self.mUpgradeType)

    def getActionType(self):
        return ActionType.BuildUpgrade

    def getAsDictForSerialization(self, isOnTimeline = True):
        dict = super().getAsDictForSerialization(isOnTimeline)
        dict['mUpgradeType'] = self.mUpgradeType.name

        return dict

    #Used to deserialize JSON (after converting the JSON to dict)
    @staticmethod
    def getActionFromDict(actionDict, trigger, actionNote):
        upgradeType = UpgradeType[actionDict['mUpgradeType']]
        action = BuildUpgradeAction(trigger, upgradeType, actionNote)

        return action

#Represents an action that the user does not actually take, but is placed on the timeline by the simulation engine automatically
#For example, adding and removing a worker from a mine
class AutomaticAction(Action):
    def __init__(self, actionNote = ""):
        super().__init__(0, 0, 0, None, 0, None, False, actionNote)
        self.mIsInvisibleToUser = True

    #Automatic actions don't concern the user and won't be serialized
    def getAsDictForSerialization(self, isOnTimeline = True):
        return None

    #Automatic actions don't concern the user and won't be deserialized
    @staticmethod
    def getActionFromDict(actionDict, trigger, actionNote):
        return None