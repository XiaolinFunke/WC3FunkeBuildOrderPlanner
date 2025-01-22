from SimEngine.SimulationConstants import SECONDS_TO_SIMTIME
from SimEngine.Worker import WorkerTask, isUnitWorker, Worker
from SimEngine.Event import Event
from SimEngine.EventGroup import EventGroup

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
                    
        def eventFunc():
            inactiveTimelines.append(getNewTimelineFunc())
        def reverseFunc():
            removeTimeline(timelineID)
        event = Event(eventFunction = eventFunc, reverseFunction = reverseFunc, eventTime=simTime, recurPeriodSimtime=0, 
                      eventID=eventID, eventName=eventName)

        return event

    def getTimelineType(self):
        return self.mTimelineType

    def getTimelineID(self):
        return self.mTimelineID

    def getNumActions(self):
        return len(self.mActions)

    #Remove an action from the timeline by action ID
    #@return the Action removed
    def removeAction(self, actionID):
        for i in range(len(self.mActions)):
            if self.mActions[i].mActionID == actionID:
                return self.mActions.pop(i)

    #Returns the latest action on the Timeline
    #Return None if no actions on Timeline
    def getLatestAction(self):
        return self.mActions[-1]

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

        #Amount of resources the worker has on it, and whether it's gold or lumber
        self.mAmtResourcesCarried = 0
        self.mIsCarryingGold = True
        #TODO: Ghoul should have 20, wisp and acolyte 0
        self.mMaxAmtCarried = 10

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

    #Convenience method for getting an event that adds a resource to a Worker and can be reversed
    @staticmethod
    def getAddResourceToWorkerEvent(workerTimeline, isResourceGold, amtToAdd, simTime, eventName, eventID):
        def eventFunc():
            workerTimeline.addResource(isResourceGold, amtToAdd)
        def reverseFunc():
            workerTimeline.removeResources(isResourceGold, amtToAdd)
        event = Event(eventFunction = eventFunc, reverseFunction = reverseFunc, eventTime=simTime, recurPeriodSimtime=0, 
                      eventID=eventID, eventName=eventName)

        return event

    #TODO: Do these methods actually need to be static?
    #Convenience method for getting an event that returns the resources from a Worker to the overall resources and can be reversed
    @staticmethod
    def getReturnResourcesFromWorkerEvent(workerTimeline, isResourceGold, amtToReturn, currentResources, simTime, eventName, eventID):
        def eventFunc():
            workerTimeline.returnResources(currentResources, amtToReturn, isResourceGold)
        def reverseFunc():
            #Add the resource back to the worker from our resource totals
            workerTimeline.addResource(isResourceGold, amtToReturn)
            if isResourceGold:
                currentResources.deductGold(amtToReturn)
            else:
                currentResources.deductLumber(amtToReturn)
        event = Event(eventFunction = eventFunc, reverseFunction = reverseFunc, eventTime=simTime, recurPeriodSimtime=0, 
                      eventID=eventID, eventName=eventName)

        return event

    #addResource - Add a resource to the worker
    #@param isResourceGold - True if resource is gold, false if lumber
    #@param amtToAdd - How much to add to the worker
    #Return True if successful
    def addResource(self, isResourceGold, amtToAdd):
        #TODO: Some workers can only carry some resources, or none at all. Should check that here
        #Should also check the max amount

        if self.mIsCarryingGold == isResourceGold and self.mAmtResourcesCarried >= self.mMaxAmtCarried:
            print("Tried to add resource to worker that is already at capacity for that resource. isGold is", isResourceGold)
            return False

        #Worker is not at full capacity, so we can add these resources
        if self.mIsCarryingGold == isResourceGold:
            self.mAmtResourcesCarried = min(self.mAmtResourcesCarried + amtToAdd, self.mMaxAmtCarried)
        else:
            #Worker had the other resource on it or no resource at all, so we just overwrite with the new resource
            self.mAmtResourcesCarried = amtToAdd
            self.mIsCarryingGold = isResourceGold
        return True

    def removeResource(self, isResourceGold, amtToRemove):
        if self.mIsCarryingGold != isResourceGold:
            print("Tried to remove resources from worker when it isn't carrying any of that resource. isResourceGold is", isResourceGold)
            return False
        
        if amtToRemove > self.mAmtResourcesCarried:
            print("Tried to remove more resources from worker than it is actually carrying. Tried to remove", amtToRemove, "when it only carried", self.mAmtResourcesCarried)
            return False
        
        self.mAmtResourcesCarried -= amtToRemove
        return True

    #Add the resources on this worker to the total resources
    #@param currentResources - The current resource totals
    #@param amtToReturn - (Optional) If None, ignore. Otherwise, ensure this is the amount being returned and error if not
    #@param isResourceGold - (Optional) If None, ignore. Otherwise, ensure this is the resource being returned and error if not
    #@return True if successful, False otherwise
    def returnResources(self, currentResources, amtToReturn = None, isResourceGold = None):
        if self.mAmtResourcesCarried == 0:
            print("Tried to return resources on a worker that has no resources")
            return False
        if amtToReturn and self.mAmtResourcesCarried != amtToReturn:
            print("Tried to return resources on a worker, but it is carrying", self.mAmtResourcesCarried, "and we are expecting to return", amtToReturn)
            return False
        if isResourceGold and isResourceGold != self.mIsCarryingGold:
            print("Tried to return resources on a worker, but it is ", self.mIsCarryingGold, "that it is carrying gold, and we are expecting it to be", isResourceGold)
            return False

        goldChange = 0
        lumberChange = 0
        if self.mIsCarryingGold:
            goldChange = self.mAmtResourcesCarried
        else:
            lumberChange = self.mAmtResourcesCarried

        currentResources.modifyResources(goldChange, lumberChange)
        self.mAmtResourcesCarried = 0

    #Convenience method for getting an event that changes a worker's task and can be reversed
    #If task is being changed to gold or lumber, need to pass in that resource source timeline as well
    def getChangeTaskEvent(self, newTask, simTime, eventName, eventID, resourceSourceTimeline = None):
        originalTask = self.mCurrentTask
        def eventFunc():
            self.changeTask(simTime, newTask, resourceSourceTimeline)
        def reverseFunc():
            self.changeTask(simTime, originalTask, self.mCurrentResourceSourceTimeline)
        event = Event(eventFunction = eventFunc, reverseFunction = reverseFunc, eventTime=simTime, recurPeriodSimtime = 0, 
                      eventName = eventName, eventID = eventID)
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

    #TODO: This is a WorkerTimeline, so probably don't need to specify "Worker" in the function name
    def sendWorkerToMine(self, action, currSimTime, goldMineTimeline):
        self.changeTask(currSimTime, WorkerTask.GOLD, goldMineTimeline)

        miningEvents, miningEventGroup = self._getGoldMiningEvents(action, currSimTime, goldMineTimeline)

        action.setAssociatedEvents([miningEvents])
        if not self.addAction(action):
            print("Failed to add go to mine action to timeline")
            return False

        for miningEvent in miningEvents:
            self.mEventHandler.registerEvent(miningEvent, miningEventGroup)
        return True

    #Get the events associated with gold mining - will be overridden depending on the worker type to get the appropraite event(s)
    #@return [events], eventGroup
    #eventGroup may be None if events only contains 1 event
    def _getGoldMiningEvents(self, action, currSimTime, goldMineTimeline):
        #Must be implemented by derived classes
        print("Error: getGoldMiningEvents is not implemented for this class")

    def _getGoldMiningEventsElfUD(self, action, currSimTime, goldMineTimeline):
        enterMineStartTime = currSimTime + action.mTravelTime
        enterMineEvent = Event.getModifyWorkersInMineEvent(goldMineTimeline, enterMineStartTime, "Enter mine", self.mEventHandler.getNewEventID())

        miningEvents = [enterMineEvent]

        return miningEvents, None

    def _getGoldMiningEventsOrcHu(self, action, currSimTime, goldMineTimeline):
        GOLD_MINED_PER_TRIP = 10
        #Amount of time worker will stay in mine getting the gold, for Hu and Orc
        TIME_IN_MINE_SEC = 1
        enterMineStartTime = currSimTime + action.mTravelTime
        enterMineEvent = Event.getModifyWorkersInMineEvent(goldMineTimeline, enterMineStartTime, "Enter mine", self.mEventHandler.getNewEventID())
        exitMineStartTime = enterMineStartTime + (TIME_IN_MINE_SEC * SECONDS_TO_SIMTIME)
        exitMineEvent = WorkerTimeline.getAddResourceToWorkerEvent(self, True, GOLD_MINED_PER_TRIP, exitMineStartTime, "Exit mine", self.mEventHandler.getNewEventID())
        returnGoldStartTime = exitMineStartTime + goldMineTimeline.mTimeToWalkToMine
        returnGoldEvent = WorkerTimeline.getReturnResourcesFromWorkerEvent(self, True, GOLD_MINED_PER_TRIP, goldMineTimeline.mCurrentResources, returnGoldStartTime, "Return gold", self.mEventHandler.getNewEventID())

        miningEvents = [enterMineEvent, exitMineEvent, returnGoldEvent]
        miningEventGroup = EventGroup(miningEvents, goldMineTimeline.mTimeToWalkToMine)

        return miningEvents, miningEventGroup

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

    def _getGoldMiningEvents(self, action, currSimTime, goldMineTimeline):
        return super()._getGoldMiningEventsElfUD(action, currSimTime, goldMineTimeline)

class AcolyteTimeline(WorkerTimeline):
    def __init__(self, timelineID, eventHandler):
        super().__init__(timelineType = Worker.Acolyte.name, timelineID = timelineID, eventHandler=eventHandler, 
                         lumberCycleTimeSec = None, lumberGainPerCycle = None, goldCycleTimeSec = 5, goldGainPerCycle = 10)

    def _getGoldMiningEvents(self, action, currSimTime, goldMineTimeline):
        return super()._getGoldMiningEventsElfUD(action, currSimTime, goldMineTimeline)

class GhoulTimeline(WorkerTimeline):
    def __init__(self, timelineID, eventHandler):
        super().__init__(timelineType = Worker.Ghoul.name, timelineID = timelineID, eventHandler=eventHandler, 
                         lumberCycleTimeSec = None, lumberGainPerCycle = 20, goldCycleTimeSec = None, goldGainPerCycle = None)

class PeasantTimeline(WorkerTimeline):
    def __init__(self, timelineID, eventHandler):
        super().__init__(timelineType = Worker.Peasant.name, timelineID = timelineID, eventHandler=eventHandler, 
                         lumberCycleTimeSec = None, lumberGainPerCycle = 10, goldCycleTimeSec = None, goldGainPerCycle = 10)

    def _getGoldMiningEvents(self, action, currSimTime, goldMineTimeline):
        return super()._getGoldMiningEventsOrcHu(action, currSimTime, goldMineTimeline)

class PeonTimeline(WorkerTimeline):
    def __init__(self, timelineID, eventHandler):
        super().__init__(timelineType = Worker.Peon.name, timelineID = timelineID, eventHandler=eventHandler, 
                         lumberCycleTimeSec = None, lumberGainPerCycle = 10, goldCycleTimeSec = None, goldGainPerCycle = 10)

    def _getGoldMiningEvents(self, action, currSimTime, goldMineTimeline):
        return super()._getGoldMiningEventsOrcHu(action, currSimTime, goldMineTimeline)