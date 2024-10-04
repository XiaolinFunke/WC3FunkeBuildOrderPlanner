from SimEngine.SimulationConstants import Race, TIME_TO_MINE_GOLD_BASE_SEC, SECONDS_TO_SIMTIME
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
        self.mNumWorkersInMine = 0
        self.mRace = race
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