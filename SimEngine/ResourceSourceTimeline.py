from SimEngine.SimulationConstants import Race, SECONDS_TO_SIMTIME
from SimEngine.Event import Event
from SimEngine.Timeline import Timeline
from SimEngine.Action import AutomaticAction

class ResourceSourceTimeline(Timeline):
    def __init__(self, timelineType, timelineID, eventHandler, currentResources):
        super().__init__(timelineType, timelineID, eventHandler)
        #Needs a reference to the current resources so it can add to them
        self.mCurrentResources = currentResources

class CopseOfTreesTimeline(ResourceSourceTimeline):
    def __init__(self, timelineType, timelineID, eventHandler, currentResources):
        super().__init__(timelineType, timelineID, eventHandler, currentResources)


class GoldMineTimeline(ResourceSourceTimeline):
    def __init__(self, timelineType, timelineID, eventHandler, race, currentResources):
        super().__init__(timelineType, timelineID, eventHandler, currentResources)
        #Only used for Elf and Undead, since their workers stay in the mine
        self.mNumWorkersInMine = 0
        self.mMaxWorkersInMine = 5

        self.mRace = race

        #TODO: This should later depend on the map
        #Amount of time it takes a peon or peasant to walk to the mine from the town hall one-way, in simtime
        self.mTimeToWalkToMine = 2 * SECONDS_TO_SIMTIME

    #Sim time only needed for Undead and Elf, to bring their next +10 gold proportionally forward
    #Return -1 if Action failed to add, 0 if succeeded without delays, and >0 if the action was added, but for a later time
    #If >0, will return the amount the action was delayed by, in SimTime. Should only happen for Human and Orc
    def addWorkerToMine(self, simTime):
        if self.mRace == Race.NIGHT_ELF or self.mRace == Race.UNDEAD:
            if self.mineIsFull():
                print("Num workers in mine", self.mNumWorkersInMine, "and max is", self.mMaxWorkersInMine)
                print("Tried to add a Night Elf or Undead worker to mine when it's already full")
                return -1
            if self.mineIsEmpty():
                #Time to mine for 1 worker (diminishes proportionally with number of workers)
                TIME_TO_MINE_GOLD_BASE_SEC = 5
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
                return -1
        
            #TODO: Make this only used for Undead and Elf
            self.mNumWorkersInMine += 1
        else:
            #No additional events needed for entering the mine - the purpose of this addWorkerToMine event that is executing this function is just to 
            #see if we need to delay due to another worker in the mine.
            #If we are delayed, all other events in the event group will be too
            newWorkerInMineAction = AutomaticAction(duration = 1 * SECONDS_TO_SIMTIME)
            #Check the next time for action, so we don't have 2 workers in the mine at the same time
            newWorkerInMineAction.setStartTime(self.getNextPossibleTimeForAction(simTime))

            if not self.addAction(newAction = newWorkerInMineAction):
                print("Failed to add new worker action to mine timeline")
                return -1

            #Return the amount we had to delay
            if newWorkerInMineAction.getStartTime() != simTime:
                return newWorkerInMineAction.getStartTime() - simTime
        return 0

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
        else:
            #Human and Orc
            #Get the "Worker in mine" automatic action added to this timeline by addWorkerToMine and remove it
            workerInMineAction = self.getLatestAction()
            self.removeAction(workerInMineAction.mActionID)

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

            #Re-register the event at the new time and set its new recur period
            self.mEventHandler.rescheduleEvent(gainGoldEvent, goldEventNewSimTime - gainGoldEvent.getEventTime())
            newRecurPeriod = gainGoldEvent.getTrueRecurPeriodSimTime() * changeProportion
            gainGoldEvent.setRecurPeriodSimTime(newRecurPeriod)

            return gainGoldEvent
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