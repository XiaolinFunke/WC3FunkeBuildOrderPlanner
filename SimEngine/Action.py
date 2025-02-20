from enum import Enum, auto
from SimEngine.Worker import WorkerTask
from SimEngine.Trigger import Trigger
from pydoc import locate

class ActionType(Enum):
    BuildUnit = auto()
    BuildStructure = auto()
    Shop = auto()
    WorkerMovement = auto()
    BuildUpgrade = auto()

class Action:
    def __init__(self, name, goldCost, lumberCost, trigger, duration, requiredTimelineType, travelTime, actionID, interruptable = False):
        self.mName = name
        self.mGoldCost = goldCost
        self.mLumberCost = lumberCost
        #What triggers us to do this action (amount of gold, lumber, etc.)
        self.mTrigger = trigger
        #Start time starts at the beginning of the travel time 
        #In simtime
        self.mStartTime = -1
        #Duration does not include travel time - So full duration is duration + travel time
        #If action has infinite duration, will be None
        self.mDuration = duration
        #Travel time takes place at the very beginning of the action (start time)
        self.mTravelTime = travelTime
        self.mRequiredTimelineType = requiredTimelineType
        self.mActionID = actionID
        #Some actions, such as mining actions, are interruptable, and can be overwritten by other actions
        self.mInterruptable = interruptable
        #List of events
        self.mAssociatedEvents = []

        #Some Actions shouldn't be shown to the user and shouldn't make a timeline 'Active'
        self.mIsInvisibleToUser = False

    #TODO: Any fancy way we could mark variables as ones that should be serialized rather than having to specify here?
    #Pare down to only relevant fields for JSON encoding and get as dict
    #@param isOnTimeline - If True, include stuff like start time and duration (needed for when we're printing the Timelines as JSON, but not for ordered action list)
    def getAsDictForSerialization(self, isOnTimeline = True):
        dict = {
            'actionType' : self.__class__.__name__,
            'trigger' : self.mTrigger.getAsDictForSerialization(),
            'actionID' : self.mActionID
        }
        #Many common variables aren't used by all sub-classes. Don't bother serializing them if they aren't used (are set to None)
        if self.mName != None: dict['name'] = self.mName
        if self.mDuration != None: dict['duration'] = self.mDuration
        if self.mTravelTime != None: dict['travelTime'] = self.mTravelTime

        #The info we need to know about is different depending on whether we've already placed it on a timeline or have yet to
        if isOnTimeline:
            dict['startTime'] = self.mStartTime
        else:
            if self.mGoldCost != None: dict['goldCost'] = self.mGoldCost
            if self.mLumberCost != None: dict['lumberCost'] = self.mLumberCost
            dict['requiredTimelineType'] = self.mRequiredTimelineType

        return dict

    #Used to deserialize JSON (after converting the JSON to dict)
    #This base class method just gets action arguments that are common to all actions and then determines which sub-class method to call
    @staticmethod
    def getActionFromDict(actionDict):
        #See https://stackoverflow.com/questions/11775460/lexical-cast-from-string-to-type - locate is used to find the type
        actionType = locate('SimEngine.Action.' + actionDict['actionType'])

        trigger = Trigger.getTriggerFromDict(actionDict['trigger'])

        #Use get instead of operator [], since these may not exist for all subclasses and we don't want a KeyError
        name = actionDict.get('name')
        goldCost = actionDict.get('goldCost')
        lumberCost = actionDict.get('lumberCost')
        actionID = actionDict.get('actionID')
        duration = actionDict.get('duration')
        travelTime = actionDict.get('travelTime')
        requiredTimelineType = actionDict.get('requiredTimelineType')
        
        action = actionType.getActionFromDict(actionDict, trigger, name, goldCost, lumberCost, duration, requiredTimelineType, actionID, travelTime)

        return action

    def setCostToFree(self):
        self.mGoldCost = 0
        self.mLumberCost = 0

    def getTrigger(self):
        return self.mTrigger

    def payForAction(self, currentResources):
        if self.mGoldCost: currentResources.deductGold(self.mGoldCost)
        if self.mLumberCost: currentResources.deductLumber(self.mLumberCost)

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

    #Gets the associated event, but if its a recurring event, it gets the newest recurrence
    def getNewestAssociatedEvent(self):
        assEvent = self.getAssociatedEvent()
        while True:
            nextEvent = assEvent.mNextRecurredEvent
            if nextEvent:
                assEvent = nextEvent
            else:
                break
        return assEvent

    def getAssociatedEvents(self):
        return self.mAssociatedEvents
    
    def getRequiredTimelineType(self):
        return self.mRequiredTimelineType

    def getEndTime(self):
        travelTime = self.mTravelTime
        if not self.mTravelTime:
            travelTime = 0
        return self.mStartTime + self.mDuration + travelTime

    #Return the percent of this action that has been completed, based on the simtime (between 0 and 100). Returns -1 if the action has not begun yet
    #Does not include travel time as part of the action being completed
    def getPercentComplete(self, currSimTime):
        #If action hasn't started yet (excluding any potential travel time), return -1
        if currSimTime < self.getEndTime() - self.mDuration:
            return -1

        #Use time left / end time rather than the time used / start time, since we want to exclude the travel time
        #For example, a BuildStructure action that has been going for 5s because the worker has been walking for 5s is still a 0% complete action
        timeLeft = self.getEndTime() - currSimTime
        percentLeftToComplete = (timeLeft / self.mDuration) * 100

        #Bound between 0 and 100
        currentPercentComplete = min(100.0, max(0.0, 100.0 - percentLeftToComplete))

        return currentPercentComplete

    def __str__(self):
        duration = self.mDuration
        if self.mDuration == None:
            duration = 0
        name = self.mName
        if self.mName == None:
            name = "Unnamed"
        travelTime = self.mTravelTime
        if self.mTravelTime == None:
            travelTime = 0
        if self.mStartTime == -1:
            scheduleStr = "(Unscheduled)"
        else:
            scheduleStr = "(" + str(travelTime + self.getStartTime()) + " - " + str(travelTime + self.getStartTime() + duration) + ")"
        
        return "Action: \"" + self.__class__.__name__ + "\" : " + name + " " + scheduleStr + " - " + str(len(self.mAssociatedEvents)) + " events"

    def __repr__(self):
        return self.__str__()

class BuildUnitAction(Action):
    def __init__(self, trigger, name, goldCost, lumberCost, foodCost, duration, actionID, requiredTimelineType):
        super().__init__(name, goldCost, lumberCost, trigger, duration, requiredTimelineType, None, actionID, False)
        self.mFoodCost = foodCost

    def payForAction(self, currentResources):
        super().payForAction(currentResources)
        currentResources.increaseFoodUsed(self.mFoodCost)

    def getActionType(self):
        return ActionType.BuildUnit

    def getAsDictForSerialization(self, isOnTimeline = True):
        dict = super().getAsDictForSerialization(isOnTimeline)

        if not isOnTimeline:
            dict['foodCost'] = self.mFoodCost

        return dict

    #Used to deserialize JSON (after converting the JSON to dict)
    @staticmethod
    def getActionFromDict(actionDict, trigger, name, goldCost, lumberCost, duration, requiredTimelineType, actionID, travelTime):
        foodCost = int(actionDict['foodCost'])

        action = BuildUnitAction(trigger, name, goldCost, lumberCost, foodCost, duration, actionID, requiredTimelineType)

        return action

class BuildStructureAction(Action):
    def __init__(self, travelTime, trigger, currentWorkerTask, name, goldCost, lumberCost, foodProvided, duration, requiredTimelineType, actionID, consumesWorker = False, isInterruptable = False):
        super().__init__(name, goldCost, lumberCost, trigger, duration, requiredTimelineType, travelTime, actionID, isInterruptable)
        self.mFoodProvided = foodProvided
        self.mConsumesWorker = consumesWorker
        self.mCurrentWorkerTask = currentWorkerTask

    def payForAction(self, currentResources):
        super().payForAction(currentResources)
        if self.mConsumesWorker:
            currentResources.decreaseFoodUsedByOne()
        #Don't increase max food by food provided, since that only happens when a building is complete, not paid for

    def getActionType(self):
        return ActionType.BuildStructure

    def getAsDictForSerialization(self, isOnTimeline = True):
        dict = super().getAsDictForSerialization(isOnTimeline)
        
        dict['currentWorkerTask'] = self.mCurrentWorkerTask.name

        if not isOnTimeline:
            dict['foodProvided'] = self.mFoodProvided
            dict['consumesWorker'] = self.mConsumesWorker

        return dict

    #Used to deserialize JSON (after converting the JSON to dict)
    @staticmethod
    def getActionFromDict(actionDict, trigger, name, goldCost, lumberCost, duration, requiredTimelineType, actionID, travelTime):
        currentWorkerTask = WorkerTask[actionDict['currentWorkerTask']]
        foodProvided = int(actionDict['foodProvided'])
        consumesWorker = bool(actionDict['consumesWorker'])
        action = BuildStructureAction(travelTime, trigger, currentWorkerTask, name, goldCost, lumberCost, foodProvided, duration, requiredTimelineType, actionID, consumesWorker, False)

        return action

class ShopAction(Action):
    def __init__(self, name, goldCost, trigger, requiredTimelineType, travelTime, actionID):
        super().__init__(name, goldCost, None, trigger, None, requiredTimelineType, travelTime, actionID, False)

    def getActionType(self):
        return ActionType.Shop

    #Used to deserialize JSON (after converting the JSON to dict)
    @staticmethod
    def getActionFromDict(actionDict, trigger, name, goldCost, lumberCost, duration, requiredTimelineType, actionID, travelTime):
        action = ShopAction(name, goldCost, trigger, requiredTimelineType, travelTime, actionID)

        return action

class WorkerMovementAction(Action):
    def __init__(self, travelTime, trigger, currentWorkerTask, desiredWorkerTask, requiredTimelineType, actionID, workerTimelineID = None):
        super().__init__(None, None, None, trigger, None, requiredTimelineType, travelTime, actionID, True)
        self.mCurrentWorkerTask = currentWorkerTask
        self.mDesiredWorkerTask = desiredWorkerTask
        self.mWorkerTimelineID = workerTimelineID

    def getActionType(self):
        return ActionType.WorkerMovement

    def getAsDictForSerialization(self, isOnTimeline = True):
        dict = super().getAsDictForSerialization(isOnTimeline)
        dict['currentWorkerTask'] = self.mCurrentWorkerTask.name
        dict['desiredWorkerTask'] = self.mDesiredWorkerTask.name

        if not isOnTimeline:
            dict['workerTimelineID'] = self.mWorkerTimelineID

        return dict

    #Used to deserialize JSON (after converting the JSON to dict)
    @staticmethod
    def getActionFromDict(actionDict, trigger, name, goldCost, lumberCost, duration, requiredTimelineType, actionID, travelTime):
        currentWorkerTask = WorkerTask[actionDict['currentWorkerTask']]
        desiredWorkerTask = WorkerTask[actionDict['desiredWorkerTask']]
        strTimelineID = actionDict['workerTimelineID']
        workerTimelineID = None if strTimelineID == None else int(strTimelineID)
        action = WorkerMovementAction(travelTime, trigger, currentWorkerTask, desiredWorkerTask, requiredTimelineType, actionID, workerTimelineID)

        return action

class BuildUpgradeAction(Action):
    def __init__(self, trigger, name, goldCost, lumberCost, duration, actionID, requiredTimelineType):
        super().__init__(name, goldCost, lumberCost, trigger, duration, requiredTimelineType, None, actionID, False)

    def getActionType(self):
        return ActionType.BuildUpgrade

    #Used to deserialize JSON (after converting the JSON to dict)
    @staticmethod
    def getActionFromDict(actionDict, trigger, name, goldCost, lumberCost, duration, requiredTimelineType, actionID, travelTime):
        action = BuildUpgradeAction(trigger, name, goldCost, lumberCost, duration, actionID, requiredTimelineType)

        return action

#Represents an action that the user does not actually take, but is placed on the timeline by the simulation engine automatically
#For example, adding and removing a worker from a mine
class AutomaticAction(Action):
    def __init__(self, duration = 0):
        super().__init__(None, 0, 0, None, duration, None, None, -1, False)
        self.mIsInvisibleToUser = True

    #Automatic actions don't concern the user and won't be serialized
    def getAsDictForSerialization(self, isOnTimeline = True):
        return None

    #Automatic actions don't concern the user and won't be deserialized
    @staticmethod
    def getActionFromDict(actionDict, trigger, name, goldCost, lumberCost, duration, requiredTimelineType, actionID, travelTime):
        return None