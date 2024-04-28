class EventHandler:
    def __init__(self):
        #Simtime -> list of functions to execute at that time
        self.mEvents = {}
        self.mNextEventID = 0
        #The Event ID of the last event executed
        self.mLastEventExecuted = -1
        #The last simtime we have executed. Note that this is updated even if no events were registered for that simtime
        self.mLastSimTimeExecuted = -1

    def registerEvent(self, event):
        if event.getEventTime() not in self.mEvents:
            self.mEvents[event.getEventTime()] = [event]
        else:
            self.mEvents[event.getEventTime()].append(event)

    #Execution times are inclusive
    def executeEventsInRange(self, startSimTime, endSimTime):
        for simTime in range(startSimTime, endSimTime + 1):
            self.executeEvents(simTime)

    def executeEvents(self, simTime):
        if simTime not in self.mEvents:
            self.mLastSimTimeExecuted = simTime
            return

        executeRemainingEvents = True
        #If we have already executed at this simtime, we only want to execute the remaining events
        if simTime == self.mLastSimTimeExecuted:
            executeRemainingEvents = False

        #Use index and while loop so that we also execute any events that may be added to this list
        #by the events we are executing
        i = 0
        while i < len(self.mEvents[simTime]):
            event = self.mEvents[simTime][i]
            if executeRemainingEvents:
                event.execute()
                self.mLastEventExecuted = event.getEventID()
                if event.doesRecur():
                    event.recur()
                    self.registerEvent(event)
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
        for simTime, events in sorted(self.mEvents.items(), key=lambda x: x[0]):
            print("simTime", simTime, ":", events)

    def getNewEventID(self):
        eventID = self.mNextEventID
        self.mNextEventID += 1
        return eventID

class Event:
    def __init__(self, eventFunction, eventTime, recurPeriodSimtime, eventID, eventName = ""):
        self.mCurrRecurrenceError = 0
        self.setEventTime(eventTime)

        self.mFunction = eventFunction

        self.setRecurPeriodSimTime(recurPeriodSimtime)
        self.mEventName = eventName
        self.mEventID = eventID

    def __str__(self):
        return "Event:\"" + self.mEventName + "\" - addr " + hex(id(self))

    def __repr__(self):
        return self.__str__()
    
    def getEventID(self):
        return self.mEventID

    def getEventName(self):
        return self.mEventName

    #Change this event's time based on its recur period
    def recur(self):
        if self.doesRecur():
            self.mCurrRecurrenceError += self.mErrorPerRecurrence
            self.mEventTime += self.mRecurPeriodSimTime
            #Adjust for the build-up of recurrence error
            #Adjust at 0.5 instead of 1, so that we are always within half a step rather than being able to be off by almost a full step
            if self.mCurrRecurrenceError >= 0.5:
                self.mEventTime -= 1
                self.mCurrRecurrenceError -= 1
            elif self.mCurrRecurrenceError <= -0.5:
                self.mEventTime += 1
                self.mCurrRecurrenceError += 1

    #Automatically rounded (note, python3 uses banker's rounding to avoid bias)
    def setEventTime(self, newEventTime):
        roundedTime = round(newEventTime)
        error = roundedTime - newEventTime
        self.mEventTime = roundedTime
        self.mCurrRecurrenceError = error

    #Get the time this event is scheduled for
    def getEventTime(self):
        return self.mEventTime

    #Get the time this event WOULD BE scheduled for, if we could simulate
    #perfectly accurately
    def getTrueTime(self):
        return self.mEventTime - self.mCurrRecurrenceError

    def getTrueRecurPeriodSimTime(self):
        return self.mRecurPeriodSimTime - self.mErrorPerRecurrence

    def getRecurPeriodSimTime(self):
        return self.mRecurPeriodSimTime

    def setRecurPeriodSimTime(self, recurPeriodSimtime):
        #A recur period of 0 indicates it does not recur
        self.mRecurPeriodSimTime = round(recurPeriodSimtime)
        #For recurring events that don't have an integer sim time period, some error will occur
        #We should track this error to ensure it doesn't build up over time
        self.mErrorPerRecurrence = self.mRecurPeriodSimTime - recurPeriodSimtime

    def doesRecur(self):
        return self.mRecurPeriodSimTime > 0

    def execute(self):
        if not self.mFunction:
            print("Attempted to execute a function that was None. Event name was", self.mEventName, "and event ID was", self.mEventID)
            return
        self.mFunction()