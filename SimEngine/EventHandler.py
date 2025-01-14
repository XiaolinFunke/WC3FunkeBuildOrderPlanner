from SimEngine.EventGroup import EventGroup

class EventHandler:
    def __init__(self):
        #Simtime -> list of (event, eventGroup) pairs
        self.mEvents = {}
        self.mNextEventID = 0

        #The Event ID of the last event executed
        self.mLastEventExecuted = -1
        #The last simtime we have executed events for (only updated if there were actually events to execute at that time, not just if we tried to execute)
        self.mLastSimTimeExecuted = -1

        #For Debugging Only
        #String Events IDs of all the events executed in order - put an 'R' in front of any that were executed in reverse
        self.mEventsExecutedInOrder = []

    def getNumberOfEvents(self):
        num = 0
        for simTime in self.mEvents:
            for event in self.mEvents[simTime]:
                num += 1
        return num

    def printEventsExecutedInOrder(self):
        if len(self.mEventsExecutedInOrder) == 0:
            print("No events executed")
            return

        print("Events executed: ", end='')
        print(self.mEventsExecutedInOrder[0], end='')
        for i in range(1, len(self.mEventsExecutedInOrder)):
            print(", " + self.mEventsExecutedInOrder[i], end='')
        print()

    #Register an event to be executed at a particular simTime
    #If the event is in an EventGroup, that should also be registered
    def registerEvent(self, event, eventGroup = None):
        if event.getEventTime() not in self.mEvents:
            self.mEvents[event.getEventTime()] = [ (event, eventGroup) ]
        else:
            self.mEvents[event.getEventTime()].append( (event, eventGroup) )
        
    #Return True if we have no non-recurring events at or past the simtime passed in
    def containsOnlyRecurringEvents(self, simTime):
        #Look through all the events
        for eventSimTime in self.mEvents:
            #Only look at events in the future
            if eventSimTime < simTime: 
                continue

            for event, eventGroup in self.mEvents[eventSimTime]:
                if not event.doesRecur():
                    return False
        return True

    def registerEvents(self, events):
        for event in events:
            self.registerEvent(event)

    #Execution times are inclusive
    def executeEventsInRange(self, startSimTime, endSimTime):
        for simTime in range(startSimTime, endSimTime + 1):
            self.executeEvents(simTime)

    #Execute the reverse events, in reverse order. False otherwise
    def reverseEvents(self, simTime):
        if simTime not in self.mEvents:
            return

        executeRemainingEvents = True
        #If we have already executed at this simtime, we only want to reverse the remaining events (this event and the ones before it)
        if simTime == self.mLastSimTimeExecuted:
            executeRemainingEvents = False

        #Use index and while loop so that we also execute any events that may be added to this list
        #by the events we are executing
        i = len(self.mEvents[simTime]) - 1
        while i >= 0:
            event, eventGroup = self.mEvents[simTime][i]
            if executeRemainingEvents:
                self._reverseEvent(event, eventGroup)
            #This event was the last one we executed, so we should start executing the events for this simtime from here on
            elif event.getEventID() == self.mLastEventExecuted:
                executeRemainingEvents = True
                #Start the execution at this event, since we're going in reverse
                continue
            i -= 1
        #Search back for the last executed event to reset the variables that track the last executed event
        for time in range(simTime - 1, -1, -1):
            #Search from (simTime - 1) to 0 for an event
            if time in self.mEvents and len(self.mEvents[time]) != 0:
                self.mLastSimTimeExecuted = time
                numEvents = len(self.mEvents[time])
                self.mLastEventExecuted = self.mEvents[time][numEvents - 1][0].getEventID()
                break
        else: #No break
            #No event found, just unset them
            self.mLastSimTimeExecuted = -1
            self.mLastEventExecuted = -1

    def _reverseEvent(self, event, eventGroup):
        if not event.mIsDisabled:
            self.mEventsExecutedInOrder.append('R' + str(event.getEventID()))
            event.reverse()
            if eventGroup != None and eventGroup.doesRecur():
                if event.doesRecur():
                    print("Error: cannot have an event that recurs within an event group that recurs. Will ignore the individual event's recurrence and recur only the group")
                elif eventGroup.isLastEventInGroup(event.getEventID()):
                    eventGroup.mNextRecurredEventGroup.mPrevRecurredEventGroup = None
                    #Remove the events in the recurred event group
                    for event in eventGroup.mNextRecurredEventGroup.mOrderedEventList:
                        self.unRegisterEvent(event.getEventTime(), event.getEventID())
                    eventGroup.mNextRecurredEventGroup = None
            elif event.doesRecur():
                #If this event recurs, unregister its recurrence, so the recurrence doesn't get doubled when we simulate forward again
                #Remove the next recurring event from the chain of recurring events
                event.mNextRecurredEvent.mPrevRecurredEvent = None
                self.unRegisterEvent(event.mNextRecurredEvent.getEventTime(), event.mNextRecurredEvent.getEventID())
                event.mNextRecurredEvent = None

        #Even if this event is disabled, we still want to check if it has spawned or disabled any other events
        #because it may be disabled due to being delayed 
        #Unregister any events that this event spawned by being delayed
        for spawnedEvent in event.mDelaySpawnedEvents:
            self.unRegisterEvent(spawnedEvent.getEventTime(), spawnedEvent.getEventID())
        event.mDelaySpawnedEvents = []

        #Undo any events that this event disabled by being delayed
        for disabledEvent in event.mDelayDisabledEvents:
            disabledEvent.mIsDisabled = False
        event.mDelayDisabledEvents = []

    def executeEvents(self, simTime):
        if simTime not in self.mEvents:
            return

        executeRemainingEvents = True
        #If we have already executed at this simtime, we only want to execute the remaining events (the events after the last event we've executed)
        if simTime == self.mLastSimTimeExecuted:
            executeRemainingEvents = False

        #Use index and while loop so that we also execute any events that may be added to this list
        #by the events we are executing
        i = 0
        eventsForTime = self.mEvents[simTime]
        while i < len(eventsForTime):
            event, eventGroup = eventsForTime[i]
            if executeRemainingEvents:
                self._executeEvent(event, eventGroup)
            #This event was the last one we executed, so we should start executing the events for this simtime from here on
            elif event.getEventID() == self.mLastEventExecuted:
                executeRemainingEvents = True
            i += 1
        self.mLastSimTimeExecuted = simTime

    def _executeEvent(self, event, eventGroup):
        if event.mIsDisabled:
            return

        self.mEventsExecutedInOrder.append(str(event.getEventID()))
        amtDelayedSimTime = event.execute()
        self.mLastEventExecuted = event.getEventID()
        #Events will return a simTime delay number if they could not be executed and need to be delayed
        if amtDelayedSimTime:
            #Re-register the event for the new time, along with remaining events in its event group, if it has any
            self._delayEvent(event, amtDelayedSimTime, eventGroup)
            return

        #Handle recurrence
        if eventGroup != None and eventGroup.doesRecur():
            if event.doesRecur():
                print("Error: cannot have an event that recurs within an event group that recurs. Will ignore the individual event's recurrence and recur only the group")
            elif eventGroup.isLastEventInGroup(event.getEventID()):
                newEventIDs = []
                for i in range(eventGroup.size()):
                    newEventIDs.append(self.getNewEventID())
                newEventGroup = eventGroup.recur(newEventIDs)
                for newEvent in newEventGroup.mOrderedEventList:
                    self.registerEvent(newEvent, newEventGroup)
        elif event.doesRecur():
            newEvent = event.recur(self.getNewEventID())
            self.registerEvent(newEvent)

    #Reschedule an event by an amount given by amtToDelaySimTime
    #Any other events in the event group will also be rescheduled
    #The original events will still exist, they will just be disabled -- this is to make executing in reverse easier
    def _delayEvent(self, event, amtToDelaySimTime, eventGroup = None):
        if eventGroup:
            #This event is a part of an event group, so the other events in the group should be delayed along with this one
            eventsToDelay = eventGroup.mOrderedEventList
        else:
            eventsToDelay = [ event ]

        newEventsInOrder = []
        #Disable any new events that are based on events we have already executed
        #They need to exist for recurrence purposes, but they've already been executed
        #The old events will be the inverse of this -- we'll keep any we've already executed enabled and disable the rest
        disableOldEvents = False
        for eventToDelay in eventsToDelay:
            #Don't unregister the event, since we will need that to still be in place for when we execute backward
            newEvent = eventToDelay.delay(self.getNewEventID(), amtToDelaySimTime)
            newEventsInOrder.append(newEvent)

            #Once we get to the events we haven't executed yet, we should start disabling the old events and stop disabling the new ones
            if eventToDelay.getEventID() == event.getEventID():
                disableOldEvents = True
            if disableOldEvents:
                #Only disable if it isn't already disabled, otherwise we will enable it when going in reverse when it shouldn't be enabled
                if not eventToDelay.mIsDisabled:
                    eventToDelay.mIsDisabled = True
                    event.mDelayDisabledEvents.append(eventToDelay)
            else:
                newEvent.mIsDisabled = True

        event.mDelaySpawnedEvents = newEventsInOrder

        newEventGroup = None
        if eventGroup:
            newEventGroup = EventGroup(newEventsInOrder, eventGroup.mRecurrenceGapSimTime)

        for newEvent in newEventsInOrder:
            self.registerEvent(newEvent, newEventGroup)

    #Reschedule an event by an amount given by amtToDelaySimTime
    #Will only reschedule this event, does not affect other events in the group
    def rescheduleEvent(self, event, amtToDelaySimTime, eventGroup = None):
        self.unRegisterEvent(event.getEventTime(), event.getEventID())
        event.setEventTime(event.getEventTime() + amtToDelaySimTime)
        self.registerEvent(event, eventGroup)

    #Returns the unregistered event, in case we want to reschedule it
    #If no event matches, return None
    def unRegisterEvent(self, eventSimTime, eventID):
        eventsForTime = self.mEvents[eventSimTime]
        for i in range(len(eventsForTime)):
            event, eventGroup = eventsForTime[i]
            if event.getEventID() == eventID:
                return eventsForTime.pop(i)
        return None

    def printScheduledEvents(self):
        #Print events sorted by simtime
        print("Scheduled events:")
        for eventSimTime in self.mEvents:
            for event, eventGroup in self.mEvents[eventSimTime]:
                print("simTime", eventSimTime, ":", event, " - ", eventGroup)
        return True

    def getNewEventID(self):
        eventID = self.mNextEventID
        self.mNextEventID += 1
        return eventID