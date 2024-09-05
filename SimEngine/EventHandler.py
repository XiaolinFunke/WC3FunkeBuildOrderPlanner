from SimEngine.Timeline import WorkerTimeline, Timeline

class EventHandler:
    def __init__(self):
        #Simtime -> list of events (functions to execute at that time)
        self.mEvents = {}
        self.mNextEventID = 0

        #The Event ID of the last event executed
        self.mLastEventExecuted = -1
        #The last simtime we have executed events for (only updated if there were actually events to execute at that time, not just if we tried to execute)
        self.mLastSimTimeExecuted = -1

        #For Debugging Only
        #String Events IDs of all the events executed in order - put an 'R' in front of any that were executed in reverse
        self.mEventsExecutedInOrder = []

    def printEventsExecutedInOrder(self):
        if len(self.mEventsExecutedInOrder) == 0:
            print("No events executed")
            return

        print("Events executed: ", end='')
        print(self.mEventsExecutedInOrder[0], end='')
        for i in range(1, len(self.mEventsExecutedInOrder)):
            print(", " + self.mEventsExecutedInOrder[i], end='')
        print()

    def registerEvent(self, event):
        if event.getEventTime() not in self.mEvents:
            self.mEvents[event.getEventTime()] = [event]
        else:
            self.mEvents[event.getEventTime()].append(event)
        
    #Return True if we have no non-recurring events at or past the simtime passed in
    def containsOnlyRecurringEvents(self, simTime):
        #Look through all the events
        for eventSimTime in self.mEvents:
            #Only look at events in the future
            if eventSimTime < simTime: 
                continue

            for event in self.mEvents[eventSimTime]:
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
            event = self.mEvents[simTime][i]
            if executeRemainingEvents:
                self.mEventsExecutedInOrder.append('R' + str(event.getEventID()))
                event.reverse()
                #If this event recurs, unregister its recurrence, so the recurrence doesn't get doubled when we simulate forward again
                if event.doesRecur():
                    #Remove the next recurring event from the chain of recurring events
                    event.mNextRecurredEvent.mPrevRecurredEvent = None
                    self.unRegisterEvent(event.mNextRecurredEvent.getEventTime(), event.mNextRecurredEvent.getEventID())
                    event.mNextRecurredEvent = None
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
                self.mLastEventExecuted = self.mEvents[time][numEvents - 1].getEventID()
                break
        else: #No break
            #No event found, just unset them
            self.mLastSimTimeExecuted = -1
            self.mLastEventExecuted = -1

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
        while i < len(self.mEvents[simTime]):
            event = self.mEvents[simTime][i]
            if executeRemainingEvents:
                self.mEventsExecutedInOrder.append(str(event.getEventID()))
                event.execute()
                self.mLastEventExecuted = event.getEventID()
                if event.doesRecur():
                    newEvent = event.recur(self.getNewEventID())
                    self.registerEvent(newEvent)
            #This event was the last one we executed, so we should start executing the events for this simtime from here on
            elif event.getEventID() == self.mLastEventExecuted:
                executeRemainingEvents = True
            i += 1
        self.mLastSimTimeExecuted = simTime

    #Returns the unregistered event, in case we want to reschedule it
    #If no event matches, return None
    def unRegisterEvent(self, eventSimTime, eventID):
        eventsForTime = self.mEvents[eventSimTime]
        for i in range(len(eventsForTime)):
            if eventsForTime[i].getEventID() == eventID:
                return eventsForTime.pop(i)
        return None

    def printScheduledEvents(self):
        #Print events sorted by simtime
        print("Scheduled events:")
        for simTime, events in sorted(self.mEvents.items(), key=lambda x: x[0]):
            print("simTime", simTime, ":", events)

    def getNewEventID(self):
        eventID = self.mNextEventID
        self.mNextEventID += 1
        return eventID