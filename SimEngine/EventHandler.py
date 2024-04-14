class EventHandler:
    def __init__(self):
        #Simtime -> list of functions to execute at that time
        self.mEvents = {}
        self.mNextEventID = 0

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
        if simTime in self.mEvents:
            for event in self.mEvents[simTime]:
                event.execute()
                if event.doesRecur():
                    event.recur()
                    self.registerEvent(event)

    #Returns the unregistered event, in case we want to reschedule it
    #If no event matches, return None
    def unRegisterEvent(self, eventSimTime, eventID):
        eventsForTime = self.mEvents[eventSimTime]
        for i in range(len(eventsForTime)):
            if eventsForTime[i].getEventID() == eventID:
                return eventsForTime.pop(i)
        return None

    def printScheduledEvents(self):
        for simTime, events in self.mEvents.items():
            print("simTime", simTime, ":", events)

    def getNewEventID(self):
        eventID = self.mNextEventID
        self.mNextEventID += 1
        return eventID

class Event:
    def __init__(self, eventFunction, eventTime, recurPeriodSimtime, eventID, eventName = ""):
        self.mFunction = eventFunction
        #A recur period of 0 indicates it does not recur
        self.mRecurPeriodSimTime = recurPeriodSimtime
        self.mEventName = eventName
        self.mEventID = eventID
        self.mEventTime = eventTime

    def __str__(self):
        return "Event:\"" + self.mEventName + "\" - addr " + hex(id(self))

    def __repr__(self):
        return "Event:\"" + self.mEventName + "\" - addr " + hex(id(self))
    
    def getEventID(self):
        return self.mEventID

    def getEventName(self):
        return self.mEventName

    #Change this event's time based on its recur period
    def recur(self):
        if self.doesRecur():
            self.mEventTime += self.mRecurPeriodSimTime

    def setEventTime(self, newEventTime):
        self.mEventTime = newEventTime

    def getEventTime(self):
        return self.mEventTime

    def getRecurPeriodSimTime(self):
        return self.mRecurPeriodSimTime

    def doesRecur(self):
        return self.mRecurPeriodSimTime > 0

    def execute(self):
        if not self.mFunction:
            print("Attempted to execute a function that was None. Event name was", self.mEventName, "and event ID was", self.mEventID)
            return
        self.mFunction()