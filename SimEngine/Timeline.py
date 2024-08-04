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
        #For wisps/acolytes, cycle starts as soon as the worker is on the mine/tree ands end when they get the resource
        self.mLumberCycleTimeSec = lumberCycleTimeSec
        self.mLumberGainPerCycle = lumberGainPerCycle
        self.mGoldCycleTimeSec = goldCycleTimeSec
        self.mGoldGainPerCycle = goldGainPerCycle

        self.mTimeAtCurrentTaskSec = 0
        self.mProductiveTimeAtCurrentTaskSec = 0

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

    def changeTask(self, goldMineTimeline, currSimTime, newTask):
        if self.mCurrentTask == newTask:
            return

        if self.mCurrentTask == WorkerTask.GOLD:
            goldMineTimeline.removeWorkerFromMine(currSimTime)
        elif self.mCurrentTask == WorkerTask.LUMBER:
            #Lumber action is associated with an event to gain lumber. Remove that event here now that this worker is doing something else
            gainLumberEvent = self.getCurrOrPrevAction(currSimTime).getAssociatedEvent()
            self.mEventHandler.unRegisterEvent(gainLumberEvent.getEventTime(), gainLumberEvent.getEventID())

        self.mCurrentTask = newTask

    def getCurrentTask(self):
        return self.mCurrentTask

    def sendWorkerToMine(self, action, goldMineTimeline, currSimTime):
        self.changeTask(goldMineTimeline, currSimTime, WorkerTask.GOLD)
        #For example, a unit could be building a building, which would be an uninteruptable task (for elf and orc at least)
        enterMineEvent = Event.getModifyWorkersInMineEvent(goldMineTimeline, currSimTime + action.mTravelTime, "Enter mine", self.mEventHandler.getNewEventID())
        action.setAssociatedEvents([enterMineEvent])
        if not self.addAction(action):
            print("Failed to add go to mine action to timeline")
            return False

        self.mEventHandler.registerEvent(enterMineEvent)
        return True

    def sendWorkerToLumber(self, action, goldMineTimeline, currSimTime, currentResources):
        self.changeTask(goldMineTimeline, currSimTime, WorkerTask.LUMBER)
        gainLumberEvent = Event.getModifyResourceCountEvent(currentResources, currSimTime + action.mTravelTime + (self.mLumberCycleTimeSec * SECONDS_TO_SIMTIME), "Gain 5 lumber", 
                                                            self.mEventHandler.getNewEventID(), 0, self.mLumberGainPerCycle, 0, 0, self.mLumberCycleTimeSec * SECONDS_TO_SIMTIME)
        action.setAssociatedEvents([gainLumberEvent])

        if not self.addAction(action):
            print("Failed to add go to lumber action to timeline")
            return False

        self.mEventHandler.registerEvent(gainLumberEvent)
        return True

    #Return True if successful, False otherwise
    def buildStructure(self, action, inactiveTimelines, getNextTimelineIDFunc, currentResources, goldMineTimeline):
        newTimelineEvent = Timeline.getNewTimelineEvent( inactiveTimelines, action.mStartTime + action.mTravelTime + action.mDuration, action.mName, getNextTimelineIDFunc(), 
                                                        "Create timeline for " + action.mName, self.mEventHandler.getNewEventID(), self.mEventHandler )
        events = [ newTimelineEvent ]

        increaseFoodMaxEvent = Event.getModifyResourceCountEvent(currentResources, action.mStartTime + action.mTravelTime + action.mDuration, "Add max food for " + action.mName, 
                                                            self.mEventHandler.getNewEventID(), 0, 0, 0, action.mFoodProvided)

        if action.mFoodProvided != 0:
            events.append(increaseFoodMaxEvent)

        self.mEventHandler.registerEvents(events)

        action.setAssociatedEvents(events)
        self.addAction(action, currentResources)
        self.changeTask(goldMineTimeline, action.mStartTime, WorkerTask.CONSTRUCTING)

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

class GoldMineTimeline(Timeline):
    def __init__(self, timelineType, timelineID, eventHandler, race, currentResources):
        super().__init__(timelineType, timelineID, eventHandler)
        self.mNumWorkersInMine = 0
        self.mRace = race
        self.mCurrentResources = currentResources
        if self.mRace == Race.NIGHT_ELF or self.mRace == Race.UNDEAD:
            self.mMaxWorkersInMine = 5
        else:
            self.mMaxWorkersInMine = 1

    #Sim time only needed for Undead and Elf, to bring their next +10 gold proportionally forward
    #Return False if Action failed to add, True if succeeded
    def addWorkerToMine(self, simTime):
        if self.mineIsFull():
            print("Tried to add a worker to mine when it's already full")
            return False

        if self.mRace == Race.NIGHT_ELF or self.mRace == Race.UNDEAD:
            if self.mineIsEmpty():
                #Time to mine for 1 worker (diminishes proportionally with number of workers)
                timeToMine = TIME_TO_MINE_GOLD_BASE_SEC * SECONDS_TO_SIMTIME

                #For first worker, we need to create the +10 gold event that we will use from here on out
                gainGoldEvent = Event.getModifyResourceCountEvent(self.mCurrentResources, simTime + timeToMine, "Gain 10 gold", 
                                                            self.mEventHandler.getNewEventID(), 10, 0, 0, 0, timeToMine)
                self.mEventHandler.registerEvent(gainGoldEvent)
            else:
                gainGoldEvent = self.modifyGainGoldEvent(self.getNumWorkersInMine(), self.getNumWorkersInMine() + 1, simTime)

            newWorkerInMineAction = AutomaticAction()
            newWorkerInMineAction.setStartTime(simTime)
            newWorkerInMineAction.setAssociatedEvents([gainGoldEvent])

            if not self.addAction(newAction = newWorkerInMineAction):
                print("Failed to add new worker action to mine timeline")
                return False

        self.mNumWorkersInMine += 1
        return True

    #Sim time only needed for Undead and Elf, to bring their next +10 gold proportionally forward
    #Return False if Action failed to add, True if succeeded
    def removeWorkerFromMine(self, simTime):
        if self.mineIsEmpty():
            print("Tried to remove a worker from mine when it's already empty")
            return False

        if self.mRace == Race.NIGHT_ELF or self.mRace == Race.UNDEAD:
            gainGoldEvent = self.modifyGainGoldEvent(self.getNumWorkersInMine(), self.getNumWorkersInMine() - 1, simTime)

            events = []
            #Don't bother adding a None event if the mine now has 0 workers
            if gainGoldEvent:
                events = [gainGoldEvent]
            removeWorkerFromMineAction = AutomaticAction()
            removeWorkerFromMineAction.setStartTime(simTime)
            removeWorkerFromMineAction.setAssociatedEvents(events)
            if not self.addAction(newAction = removeWorkerFromMineAction):
                print("Failed to add Remove Worker action from mine timeline")
                return False

        self.mNumWorkersInMine -= 1
        return True

    def modifyGainGoldEvent(self, oldNumWorkers, newNumWorkers, simTime):
        #Already a worker in the mine, and a +10 gold event
        #Next 10 gold gained will be proportionally faster now that we have another worker
        #Will need to bring that event forward
        #The event could also be for the current time, if multiple workers are added at exact same time (unrealistic, but happens in tests)
        prevAction = self.getCurrOrPrevAction(simTime)
        #The "New worker in mine" or "Remove worker from mine" action on the mine timeline will be associated with a gain gold event
        gainGoldEvent = prevAction.getNewestAssociatedEvent()

        if newNumWorkers != 0:
            #The new time of the +10 gold event will be proportionally sooner or later
            changeProportion = oldNumWorkers / newNumWorkers
            #Use true time so we don't accumulate error, but ensure that never gives a negative result
            goldEventNewSimTime = simTime + max(gainGoldEvent.getTrueTime() - simTime, 0) * changeProportion

            #Re-register the event at the new time
            unregisteredEvent = self.mEventHandler.unRegisterEvent(gainGoldEvent.getEventTime(), gainGoldEvent.getEventID())
            newRecurPeriod = unregisteredEvent.getTrueRecurPeriodSimTime() * changeProportion
            unregisteredEvent.setRecurPeriodSimTime(newRecurPeriod)

            unregisteredEvent.setEventTime(goldEventNewSimTime)
            self.mEventHandler.registerEvent(unregisteredEvent)
            return unregisteredEvent
        else:
            #Zero workers, so we need to remove the event altogether
            self.mEventHandler.unRegisterEvent(gainGoldEvent.getEventTime(), gainGoldEvent.getEventID())
            return None

    def mineIsFull(self):
        return self.mNumWorkersInMine == self.mMaxWorkersInMine

    def mineIsEmpty(self):
        return self.mNumWorkersInMine == 0

    def getNumWorkersInMine(self):
        return self.mNumWorkersInMine