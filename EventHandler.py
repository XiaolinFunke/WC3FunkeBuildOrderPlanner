class EventHandler:
    def __init__(self):
        #Simtime -> list of functions to execute at that time
        self.mEvents = {}
        self.mNextEventID = 0

    def registerEvent(self, eventSimTime, event):
        print("EVent handler register event")
        if eventSimTime not in self.mEvents:
            self.mEvents[eventSimTime] = [event]
        else:
            self.mEvents[eventSimTime].append(event)

    def executeEvents(self, simTime):
        if simTime in self.mEvents:
            for event in self.mEvents[simTime]:
                event.execute()
                if event.doesRecur():
                    self.registerEvent(simTime + event.getRecurPeriodSimTime(), event)

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
    def __init__(self, eventFunction, recurPeriodSimtime, eventID, eventName = ""):
        self.mFunction = eventFunction
        #A recur period of 0 indicates it does not recur
        self.mRecurPeriodSimTime = recurPeriodSimtime
        self.mEventName = eventName
        self.mEventID = eventID

    def __str__(self):
        return "Event:\"" + self.mEventName + "\" - addr " + hex(id(self))

    def __repr__(self):
        return "Event:\"" + self.mEventName + "\" - addr " + hex(id(self))
    
    def getEventID(self):
        return self.mEventID

    def getEventName(self):
        return self.mEventName

    def getRecurPeriodSimTime(self):
        return self.mRecurPeriodSimTime

    def doesRecur(self):
        return self.mRecurPeriodSimTime > 0

    def execute(self):
        if not self.mFunction:
            print("Attempted to execute a function that was None. Event name was", self.mEventName, "and event ID was", self.mEventID)
            return
        self.mFunction()