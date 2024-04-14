# Represents a single timeline on the planner. For example, the production queue of a barracks, or blacksmith, etc.
class Timeline:
    def __init__(self, timelineType, timelineID):
        self.mActions = []
        self.mTimelineType = timelineType
        self.mTimelineID = timelineID

    def getTimelineType(self):
        return self.mTimelineType

    def getTimelineID(self):
        return self.mTimelineID

    def getNextAction(self, simTime):
        #Actions are assumed to be in time-order
        for i in range(len(self.mActions)):
            if self.mActions[i].getStartTime() >= simTime:
                return self.mActions[i]
        #No next action found
        return None

    #If no actions have a simtime less that the simtime passed in, returns None
    def getPrevAction(self, simTime):
        if len(self.mActions) == 0:
            return None

        #Actions are assumed to be in time-order
        for i in range(len(self.mActions)):
            #Find next action and return the one before it
            if self.mActions[i].getStartTime() >= simTime:
                return self.mActions[i - 1] if i != 0 else None
        #No next action found, so previous action must be last action in list
        return self.mActions[len(self.mActions) - 1]

    #Return True if action was successfully added to timeline
    #False if failed (usually due to there already being an action in that timeslot)
    def addAction(self, newAction):
        #TODO: This insertion is O=n complexity. Since these are sorted, could do as well as O=log(n) if performance is an issue
        #Increment loop an additional time because we can insert before all elements or after all, as well as in between
        #Loop and check if new action can be inserted BEFORE the action we're looking at
        for i in range(len(self.mActions) + 1):
            #We've reached the end or new action ends before existing action - must insert here if possible
            if i == len(self.mActions) or ((newAction.mStartTime + newAction.mDuration) < self.mActions[i].mStartTime):
                #Check that previous action ends in time for the new action to start
                if i == 0 or ((self.mActions[i-1].mStartTime + self.mActions[i-1].mDuration) < newAction.mStartTime):
                    self.mActions.insert(i, newAction)
                    return True
        return False

class WorkerTimeline(Timeline):
    def __init__(self, timelineType, currentTask, timelineID, lumberCycleTimeSec, lumberGainPerCycle, goldCycleTimeSec, goldGainPerCycle):
        super().__init__(timelineType, timelineID)
        self.mCurrentTask = currentTask
        #For most workers, the cycle starts at the town hall with no resource and ends at the town hall when they drop off the resource
        #For wisps/acolytes, cycle starts as soon as the worker is on the mine/tree ands end when they get the resource
        self.mLumberCycleTimeSec = lumberCycleTimeSec
        self.mLumberGainPerCycle = lumberGainPerCycle
        self.mGoldCycleTimeSec = goldCycleTimeSec
        self.mGoldGainPerCycle = goldGainPerCycle

        self.mTimeAtCurrentTaskSec = 0
        self.mProductiveTimeAtCurrentTaskSec = 0

class WispTimeline(WorkerTimeline):
    def __init__(self, timelineType, currentTask, timelineID):
        super().__init__(timelineType = timelineType, currentTask = currentTask, timelineID = timelineID, lumberCycleTimeSec = 8, lumberGainPerCycle = 5, goldCycleTimeSec = 5, goldGainPerCycle = 10)

class GoldMineTimeline(Timeline):
    def __init__(self, timelineType, timelineID, maxWorkersInMine):
        super().__init__(timelineType, timelineID)
        self.mNumWorkersInMine = 0
        self.mMaxWorkersInMine = maxWorkersInMine

    def addWorkerToMine(self):
        if self.mineIsFull():
            return False
        self.mNumWorkersInMine += 1
        return True

    def removeWorkerFromMine(self):
        if self.mineIsEmpty():
            return False
        self.mNumWorkersInMine -= 1
        return True

    def mineIsFull(self):
        return self.mNumWorkersInMine == self.mMaxWorkersInMine

    def mineIsEmpty(self):
        return self.mNumWorkersInMine == 0

    def getNumWorkersInMine(self):
        return self.mNumWorkersInMine

class Action:
    def __init__(self, goldCost, lumberCost, foodCost, travelTime, startTime, duration, requiredTimelineType, events, actionName, interruptable = False):
        self.mGoldCost = goldCost
        self.mLumberCost = lumberCost
        self.mFoodCost = foodCost
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
        #List of events
        self.mAssociatedEvents = events

    def getStartTime(self):
        return self.mStartTime

    #If there is only one event, get it. Otherwise return None
    def getAssociatedEvent(self):
        if len(self.mAssociatedEvents) == 1:
            return self.mAssociatedEvents[0]
        return None

    def getAssociatedEvents(self):
        return self.mAssociatedEvents
    
    def getRequiredTimelineType(self):
        return self.mRequiredTimelineType