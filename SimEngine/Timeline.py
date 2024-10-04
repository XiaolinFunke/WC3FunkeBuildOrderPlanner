from SimEngine.SimulationConstants import Race, SECONDS_TO_SIMTIME, GOLD_MINED_PER_TRIP, TIME_TO_MINE_GOLD_BASE_SEC
from SimEngine.Worker import WorkerTask, isUnitWorker, Worker
from SimEngine.Event import Event
from SimEngine.Action import AutomaticAction

# Represents a single timeline on the planner. For example, the production queue of a barracks, or blacksmith, etc.
class Timeline:
    def __init__(self, timelineType, timelineID, eventHandler):
        self.mActions = []
        self.mTimelineType = timelineType
        self.mTimelineID = timelineID
        self.mEventHandler = eventHandler

    #Convenience method for getting an event that adds a new timeline and can be reversed
    @staticmethod
    def getNewTimelineEvent(inactiveTimelines, simTime, timelineName, timelineID, eventName, eventID, eventHandler):
        def removeTimeline(id):
            for i in range(len(inactiveTimelines)):
                if inactiveTimelines[i].getTimelineID() == id:
                    inactiveTimelines.pop(i)
                    return

        getNewTimelineFunc = lambda: Timeline(timelineName, timelineID, eventHandler)
        if isUnitWorker(timelineName):
            getNewTimelineFunc = lambda: WorkerTimeline.getNewWorkerTimeline(timelineName, timelineID, eventHandler)
                    
        event = Event(eventFunction = lambda: inactiveTimelines.append(getNewTimelineFunc()), 
                        reverseFunction = lambda: removeTimeline(timelineID),
                      eventTime=simTime, recurPeriodSimtime=0, eventID=eventID, eventName=eventName)

        return event

    def getTimelineType(self):
        return self.mTimelineType

    def getTimelineID(self):
        return self.mTimelineID

    def getNumActions(self):
        return len(self.mActions)

    #Returns the next action based on the sim time
    #Return None if no actions >= that sim time
    def getNextAction(self, simTime):
        #Actions are assumed to be in time-order
        for i in range(len(self.mActions)):
            if self.mActions[i].getStartTime() >= simTime:
                return self.mActions[i]
        #No next action found
        return None

    #Get the current action if there is one. If not, get the previous one
    def getCurrOrPrevAction(self, simTime):
        currAction = self.getCurrentAction(simTime)
        if currAction:
            return currAction
        else:
            return self.getPrevAction(simTime)

    #Returns the previous action based on the sim time
    #Return None if no actions < that sim time
    #Note that, unlike getNextAction, an action with a sim time of exactly simTime passed in doesn't count as the prev action
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

    #Return only an action whose simtime matches exactly. Otherwise return None
    def getCurrentAction(self, simTime):
        #Actions are assumed to be in time-order
        for i in range(len(self.mActions)):
            if self.mActions[i].getStartTime() == simTime:
                return self.mActions[i]
            elif self.mActions[i].getStartTime() > simTime:
                return None
        #No current action found
        return None

    #Add the action to the timeline, if it doesn't conflict with the Action that starts before it
    #Any actions with start times after this one will be removed from the Timeline as well
    #If currentResources is not passed in, Action will be assumed to not affect current resources
    #Returns False and won't add if overlaps with the Action before it in the Timeline
    def addAction(self, newAction, currentResources = None):
        i = self.findProperSpotForAction(newAction.getStartTime()) 
        prevActionEndTime = self.mActions[i-1].mStartTime + self.mActions[i-1].mDuration if i != 0 and self.mActions[i-1].mDuration else 0
        if newAction.getStartTime() < prevActionEndTime:
            print("Action failed to add to timeline. Its start time is", newAction.getStartTime())
            return False
        else:
            self.mActions.insert(i, newAction)
            #Remove all Actions after this new one, since we will have to recalculate all of those anyway
            #and we want to ensure the list still has no overlapping
            self.mActions = self.mActions[:i + 1]
            if currentResources:
                newAction.payForAction(currentResources)
            self.mIsActive = True
            return True

    #Return the simtime when the given Action could be scheduled on this timeline
    #If no overlap with an earlier action, will return the simTime of the Action.
    #However, if it would overlap with an earlier Action, will return a later time when it can actually be scheduled
    def getNextPossibleTimeForAction(self, actionStartTime):
        i = self.findProperSpotForAction(actionStartTime)
        prevActionEndTime = self.mActions[i-1].mStartTime + self.mActions[i-1].mDuration if i != 0 and self.mActions[i-1].mDuration else 0
        newStartTime = max(actionStartTime, prevActionEndTime)
        return newStartTime

    #Returns the index of where the Action would be inserted (assuming they are in time-order and no overlapping)
    #Ignore any Actions currently scheduled after the start time of the new action, since earlier
    #actions get priority over later ones (if we're inserting an action, everything after that will need to be re-simulated anyway)
    def findProperSpotForAction(self, actionStartTime):
        #TODO: This search is O=n complexity. Since these are sorted, could do as well as O=log(n) if performance is an issue
        #Increment loop an additional time because we can insert before all elements or after all, as well as in between
        #Loop and check if new action can be inserted BEFORE the action we're looking at
        for i in range(len(self.mActions) + 1):
            #We've reached the end or new action starts before existing action - must insert here
            if i == len(self.mActions) or actionStartTime < self.mActions[i].mStartTime:
                return i

    def getAsDictForSerialization(self):
        dict = {
            'timelineType' : self.mTimelineType,
            'timelineID' : self.mTimelineID,
            'actions' : []
        }

        for action in self.mActions:
            actionDict = action.getAsDictForSerialization()
            #Actions that don't concern the user will return None here and won't be serialized
            if actionDict != None:
                dict['actions'].append(actionDict)

        return dict

    def printTimeline(self):
        print(self.mTimelineType, "Timeline (ID:", str(self.mTimelineID), "):", self.mActions)

    def __str__(self):
        return "Timeline: " + self.mTimelineType + " (ID:" + str(self.mTimelineID) + ")"

    def __repr__(self):
        return self.__str__()

class WorkerTimeline(Timeline):
    def __init__(self, timelineType, timelineID, eventHandler, lumberCycleTimeSec, lumberGainPerCycle, goldCycleTimeSec, goldGainPerCycle):
        super().__init__(timelineType, timelineID, eventHandler)
        self.mCurrentTask = WorkerTask.IDLE
        #For most workers, the cycle starts at the town hall with no resource and ends at the town hall when they drop off the resource
        #For wisps/acolytes, cycle starts as soon as the worker is on the mine/tree and ends when they get the resource
        self.mLumberCycleTimeSec = lumberCycleTimeSec
        self.mLumberGainPerCycle = lumberGainPerCycle
        self.mGoldCycleTimeSec = goldCycleTimeSec
        self.mGoldGainPerCycle = goldGainPerCycle

        self.mTimeAtCurrentTaskSec = 0
        self.mProductiveTimeAtCurrentTaskSec = 0

        #If this worker is on gold or lumber, it will have a reference to that gold mine or tree copse timeline here
        #Otherwise, this will be None
        self.mCurrentResourceSourceTimeline = None

    @staticmethod
    def getNewWorkerTimeline(workerName, timelineID, eventHandler):
        if not isUnitWorker(workerName):
            print("Tried to get new worker timeline for unit that isn't a worker!")
            return None
        
        if workerName == Worker.Acolyte.name:
            return AcolyteTimeline(timelineID, eventHandler)
        elif workerName == Worker.Ghoul.name:
            return GhoulTimeline(timelineID, eventHandler)
        elif workerName == Worker.Peasant.name:
            return PeasantTimeline(timelineID, eventHandler)
        elif workerName == Worker.Peon.name:
            return PeonTimeline(timelineID, eventHandler)
        elif workerName == Worker.Wisp.name:
            return WispTimeline(timelineID, eventHandler)

    #Convenience method for getting an event that changes a worker's task and can be reversed
    #If task is being changed to gold or lumber, need to pass in that resource source timeline as well
    def getChangeTaskEvent(self, newTask, simTime, eventName, eventID, resourceSourceTimeline = None):
        originalTask = self.mCurrentTask
        event = Event(eventFunction = lambda: self.changeTask(simTime, newTask, resourceSourceTimeline), 
                        reverseFunction = lambda: self.changeTask(simTime, originalTask, self.mCurrentResourceSourceTimeline),
                      eventTime=simTime, recurPeriodSimtime = 0, eventName = eventName, eventID = eventID)
        return event

    #Mark worker as working on a new task
    #Also, if the worker is currently on a resource, remove them from that resource
    def changeTask(self, currSimTime, newTask, resourceSourceTimeline = None):
        if self.mCurrentTask == newTask:
            return

        if self.mCurrentTask == WorkerTask.GOLD or self.mCurrentTask == WorkerTask.LUMBER:
            if not self.mCurrentResourceSourceTimeline:
                print("Worker must move off of gold or lumber, but doesn't have a reference to any gold mine or copse of trees timeline!")
                return

        #Move off of current resource, if we were on one
        if self.mCurrentTask == WorkerTask.GOLD:
            self.mCurrentResourceSourceTimeline.removeWorkerFromMine(currSimTime)
        elif self.mCurrentTask == WorkerTask.LUMBER:
            #Lumber action is associated with an event to gain lumber. Remove that event here now that this worker is doing something else
            #TODO: We should adjust something on the copse of trees here as well
            gainLumberEvent = self.getCurrOrPrevAction(currSimTime).getNewestAssociatedEvent()
            self.mEventHandler.unRegisterEvent(gainLumberEvent.getEventTime(), gainLumberEvent.getEventID())

        #Mark worker as working on new task
        self.mCurrentTask = newTask
        if newTask == WorkerTask.GOLD or newTask == WorkerTask.LUMBER:
            if not resourceSourceTimeline:
                print("Worker was told to go to gold or lumber, but no gold mine or copse of trees timeline reference was passed in!")
                return
            else:
                self.mCurrentResourceSourceTimeline = resourceSourceTimeline

    def getCurrentTask(self):
        return self.mCurrentTask

    def sendWorkerToMine(self, action, currSimTime, goldMineTimeline):
        self.changeTask(currSimTime, WorkerTask.GOLD, goldMineTimeline)
        #For example, a unit could be building a building, which would be an uninteruptable task (for elf and orc at least)
        enterMineEvent = Event.getModifyWorkersInMineEvent(goldMineTimeline, currSimTime + action.mTravelTime, "Enter mine", self.mEventHandler.getNewEventID())
        action.setAssociatedEvents([enterMineEvent])
        if not self.addAction(action):
            print("Failed to add go to mine action to timeline")
            return False

        self.mEventHandler.registerEvent(enterMineEvent)
        return True

    def sendWorkerToLumber(self, action, currSimTime, copseOfTreesTimeline):
        self.changeTask(currSimTime, WorkerTask.LUMBER, copseOfTreesTimeline)
        #TODO: This should be handled by the Copse of Trees Timeline like we do for Gold Mine timeline
        gainLumberEvent = Event.getModifyResourceCountEvent(copseOfTreesTimeline.mCurrentResources, currSimTime + action.mTravelTime + (self.mLumberCycleTimeSec * SECONDS_TO_SIMTIME), "Gain 5 lumber", 
                                                            self.mEventHandler.getNewEventID(), 0, self.mLumberGainPerCycle, 0, 0, self.mLumberCycleTimeSec * SECONDS_TO_SIMTIME)
        action.setAssociatedEvents([gainLumberEvent])

        if not self.addAction(action):
            print("Failed to add go to lumber action to timeline")
            return False

        self.mEventHandler.registerEvent(gainLumberEvent)
        return True

    #Return True if successful, False otherwise
    def buildStructure(self, action, inactiveTimelines, getNextTimelineIDFunc, currentResources):
        newTimelineEvent = Timeline.getNewTimelineEvent( inactiveTimelines, action.mStartTime + action.mTravelTime + action.mDuration, action.mName, getNextTimelineIDFunc(), 
                                                        "Create timeline for " + action.mName, self.mEventHandler.getNewEventID(), self.mEventHandler )
        setWorkerIdleEvent = self.getChangeTaskEvent( WorkerTask.IDLE, action.mStartTime + action.mTravelTime + action.mDuration, "Worker finished building " + action.mName, self.mEventHandler.getNewEventID() )
        events = [ newTimelineEvent, setWorkerIdleEvent ]

        increaseFoodMaxEvent = Event.getModifyResourceCountEvent(currentResources, action.mStartTime + action.mTravelTime + action.mDuration, "Add max food for " + action.mName, 
                                                            self.mEventHandler.getNewEventID(), 0, 0, 0, action.mFoodProvided)

        if action.mFoodProvided != 0:
            events.append(increaseFoodMaxEvent)

        self.mEventHandler.registerEvents(events)

        action.setAssociatedEvents(events)

        #Must change task before adding action, since moving off of gold or lumber will assume the last action on the timeline is the gain 
        # gold or lumber action that it can grab the +gold or +lumber event from
        #TODO: Make this more elegant / less error prone?
        self.changeTask(action.mStartTime, WorkerTask.CONSTRUCTING)
        self.addAction(action)

        return True

    def printTimeline(self):
        print(self.mTimelineType, "Timeline (ID:", str(self.mTimelineID), "):", self.mCurrentTask, self.mActions)

class WispTimeline(WorkerTimeline):
    def __init__(self, timelineID, eventHandler):
        super().__init__(timelineType = Worker.Wisp.name, timelineID = timelineID, eventHandler=eventHandler, 
                         lumberCycleTimeSec = 8, lumberGainPerCycle = 5, goldCycleTimeSec = 5, goldGainPerCycle = 10)

class AcolyteTimeline(WorkerTimeline):
    def __init__(self, timelineID, eventHandler):
        super().__init__(timelineType = Worker.Acolyte.name, timelineID = timelineID, eventHandler=eventHandler, 
                         lumberCycleTimeSec = None, lumberGainPerCycle = None, goldCycleTimeSec = 5, goldGainPerCycle = 10)

class GhoulTimeline(WorkerTimeline):
    def __init__(self, timelineID, eventHandler):
        super().__init__(timelineType = Worker.Ghoul.name, timelineID = timelineID, eventHandler=eventHandler, 
                         lumberCycleTimeSec = None, lumberGainPerCycle = 20, goldCycleTimeSec = None, goldGainPerCycle = None)

class PeasantTimeline(WorkerTimeline):
    def __init__(self, timelineID, eventHandler):
        super().__init__(timelineType = Worker.Peasant.name, timelineID = timelineID, eventHandler=eventHandler, 
                         lumberCycleTimeSec = None, lumberGainPerCycle = 10, goldCycleTimeSec = None, goldGainPerCycle = 10)

class PeonTimeline(WorkerTimeline):
    def __init__(self, timelineID, eventHandler):
        super().__init__(timelineType = Worker.Peon.name, timelineID = timelineID, eventHandler=eventHandler, 
                         lumberCycleTimeSec = None, lumberGainPerCycle = 10, goldCycleTimeSec = None, goldGainPerCycle = 10)