class Action:
    def __init__(self, goldCost, lumberCost, travelTime, startTime, duration, requiredTimelineType, events, actionName, isExecutedASAP = False, interruptable = False):
        self.mGoldCost = goldCost
        self.mLumberCost = lumberCost
        #Start time starts at the beginning of the travel time 
        #In simtime
        self.mStartTime = startTime
        #Travel time takes place at the very beginning of the action (start time)
        self.mTravelTime = travelTime
        #Duration does not include travel time - So full duration is duration + travel time
        self.mDuration = duration
        self.mRequiredTimelineType = requiredTimelineType
        self.mActionName = actionName
        #Some actions, such as mining actions, are interruptable, and can be overwritten by other actions
        self.mInterruptable = interruptable
        #If True, we will execute this action as soon as possible after the previous one
        self.mIsExecutedASAP = isExecutedASAP
        #List of events
        self.mAssociatedEvents = events

    def payForAction(self, currentResources, isFree):
        if not isFree:
            currentResources.deductGold(self.mGoldCost)
            currentResources.deductLumber(self.mLumberCost)

    def setStartTime(self, startTime):
        self.mStartTime = startTime

    def getStartTime(self):
        return self.mStartTime

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

    def __str__(self):
        return "Action:\"" + self.mActionName + "(" + str(self.getStartTime()) + " - " + str(self.getStartTime() + self.mDuration) + ") - " + str(len(self.mAssociatedEvents)) + " events"

    def __repr__(self):
        return self.__str__()

class BuildUnitAction(Action):
    def __init__(self, goldCost, lumberCost, foodCost, startTime, duration, requiredTimelineType, events, actionName):
        super().__init__(goldCost, lumberCost, 0, startTime, duration, requiredTimelineType, events, actionName, True, False)
        self.mFoodCost = foodCost

    def payForAction(self, currentResources, isFree = False):
        super().payForAction(currentResources, isFree)
        currentResources.increaseFoodUsed(self.mFoodCost)

class BuildStructureAction(Action):
    def __init__(self, goldCost, lumberCost, foodProvided, travelTime, startTime, duration, requiredTimelineType, events, actionName, isInterruptable, consumesWorker):
        super().__init__(goldCost, lumberCost, travelTime, startTime, duration, requiredTimelineType, events, actionName, False, isInterruptable)
        #TODO: Are some of these Action members even really necessary to track? Like, won't food provided really just be handled by the associated event?
        self.mFoodProvided = foodProvided
        self.mConsumesWorker = consumesWorker

    def payForAction(self, currentResources, isFree = False):
        super().payForAction(currentResources, isFree)
        if self.mConsumesWorker:
            currentResources.decreaseFoodUsedByOne()
        #Don't increase max food by food provided, since that only happens when a building is complete, not paid for

class ShopAction(Action):
    def __init__(self, goldCost, startTime, requiredTimelineType, events, actionName):
        super().__init__(goldCost, 0, 0, startTime, 0, requiredTimelineType, events, actionName, True, False)

class WorkerMovementAction(Action):
    def __init__(self, travelTime, startTime, requiredTimelineType, events, actionName):
        super().__init__(0, 0, travelTime, startTime, 0, requiredTimelineType, events, actionName, False, True)