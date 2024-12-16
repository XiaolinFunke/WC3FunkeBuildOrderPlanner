from copy import copy

class Event:
    def __init__(self, eventFunction, reverseFunction, eventTime, recurPeriodSimtime, eventID, eventName = ""):
        self.mCurrRecurrenceError = 0
        self.setEventTime(eventTime)

        self.mFunction = eventFunction
        #This function should undo what the mFunction does, for when we need to simulate backward
        self.mReverseFunction = reverseFunction

        self.setRecurPeriodSimTime(recurPeriodSimtime)
        #If this event has recurred, this will point to the previous and next event in the chain of recurring events
        self.mPrevRecurredEvent = None
        self.mNextRecurredEvent = None
        self.mEventName = eventName
        self.mEventID = eventID

    #Convenience method for getting an event that modifies our current resources and can be reversed
    @staticmethod
    def getModifyResourceCountEvent(currentResources, simTime, eventName, eventID, goldChange, lumberChange, foodChange, foodMaxChange, recurPeriodSimTime = 0):
        def eventFunc():
            currentResources.modifyResources(goldChange, lumberChange, foodChange, foodMaxChange)
        def reverseFunc():
            currentResources.modifyResources(goldChange * -1, lumberChange * -1, foodChange * -1, foodMaxChange * -1)

        event = Event(eventFunction = eventFunc, reverseFunction = reverseFunc, eventTime=simTime, recurPeriodSimtime = recurPeriodSimTime, 
                      eventName = eventName, eventID = eventID)
        return event

    #Convenience method for getting an event that modifies the number of workers in the mine and can be reversed
    @staticmethod
    def getModifyWorkersInMineEvent(goldMineTimeline, simTime, eventName, eventID):
        #Must use defined funcs instead of lamdbas so that the event function returns None
        def eventFunc():
            goldMineTimeline.addWorkerToMine(simTime)
        def reverseFunc():
            goldMineTimeline.removeWorkerFromMine(simTime)
        event = Event(eventFunction = eventFunc, reverseFunction = reverseFunc, eventTime=simTime, recurPeriodSimtime = 0, 
                      eventName = eventName, eventID = eventID)
        return event

    def __str__(self):
        return "Event:\"" + self.mEventName + "\" - ID " + str(self.mEventID)

    def __repr__(self):
        return self.__str__()
    
    def getEventID(self):
        return self.mEventID

    def getEventName(self):
        return self.mEventName

    #Return a new event with a new time based on this event's recur period
    #@param eventID - The event ID of the new event resulting from this recurrence
    def recur(self, eventID):
        if self.doesRecur():
            newEvent = copy(self)

            newEvent.mEventID = eventID

            newEvent.mCurrRecurrenceError += newEvent.mErrorPerRecurrence
            newEvent.mEventTime += newEvent.mRecurPeriodSimTime
            #Adjust for the build-up of recurrence error
            #Adjust at 0.5 instead of 1, so that we are always within half a step rather than being able to be off by almost a full step
            if newEvent.mCurrRecurrenceError >= 0.5:
                newEvent.mEventTime -= 1
                newEvent.mCurrRecurrenceError -= 1
            elif newEvent.mCurrRecurrenceError <= -0.5:
                newEvent.mEventTime += 1
                newEvent.mCurrRecurrenceError += 1
            #Create the chain of recurring events
            newEvent.mPrevRecurredEvent = self
            self.mNextRecurredEvent = newEvent
            return newEvent
        else:
            print("Error: Tried to recur an event that doesn't recur")
            return None

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

    def getMostRecentRecurrence(self):
        if self.doesRecur == False:
            return None
        
        mostRecentRecurrence = self
        while True:
            if mostRecentRecurrence.mNextRecurredEvent == None:
                return mostRecentRecurrence
            else:
                mostRecentRecurrence = mostRecentRecurrence.mNextRecurredEvent

    #Execute the reverse event
    def reverse(self):
        if not self.mReverseFunction:
            print("Attempted to execute a reverse function that was None. Event name was", self.mEventName, "and event ID was", self.mEventID)
            return
        self.mReverseFunction()

    #Execute the function associated with this event
    #@return If the event could not be executed, and must be delayed, return the amount of simTime to delay the event for
    #If event does not have to be delayed, return None
    def execute(self):
        if not self.mFunction:
            print("Attempted to execute a function that was None. Event name was", self.mEventName, "and event ID was", self.mEventID)
            return
        return self.mFunction()