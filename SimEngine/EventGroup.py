from copy import copy

#Define an ordered group of events that will be temporally locked relative to each other, meaning:
#If one event is pushed forward or backward in time, the future events in the group will be as well
#The whole group can (and must, if recurrence is desired) also be recurred as one, recurring each individual event within it
#This is useful for events that are tied to each other, like gathering and returning gold from the mine
class EventGroup:
    def __init__(self, orderedEventList, recurrenceGapSimTime = 0):
        self.mOrderedEventList = orderedEventList

        #The amount of time between the last event of the event group, before the first event of the recurred event group
        #A gap of 1 would mean the first event of the next group starts on the very next simTime
        #A recurrence gap of 0 means it doesn't recur
        self.mRecurrenceGapSimTime = recurrenceGapSimTime

        #If this event group has recurred, this will point to the previous and next event in the chain of recurring event groups
        self.mPrevRecurredEventGroup = None
        self.mNextRecurredEventGroup = None

    #Get all events in the event group after the event with the ID that is passed in
    def getRemainingEvents(self, eventID):
        for i in range(len(self.mOrderedEventList)):
            if self.mOrderedEventList[i].getEventID() == eventID:
                return self.mOrderedEventList[i+1:]
        print("Error: getRemainingEvents called for event with ID ", eventID, " but no event with that ID exists in the event group")
        return None

    def doesRecur(self):
        return self.mRecurrenceGapSimTime > 0

    #Return a new event group with new events that have recurred and have new times based on the recurrence gap
    def recur(self):
        if self.doesRecur() and len(self.mOrderedEventList) > 0:
            recurredEvents = []
            #Calculate the recur period -- can change if events are moved forward or back, so must be calculated here
            recurPeriodSimTime = event[-1].getEventTime() - event[0].getEventTime() + self.mRecurrenceGapSimTime

            for event in self.mOrderedEventList:
                event.setRecurPeriodSimTime(recurPeriodSimTime)
                recurredEvents.append(event.recur())

            newEventGroup = copy(self)
            newEventGroup.mOrderedEventList = recurredEvents

            #Create the chain of recurring event groups
            newEventGroup.mPrevRecurredEventGroup = self
            self.mNextRecurredEventGroup = newEventGroup

            return newEventGroup
        else:
            print("Error: Tried to recur an event group that doesn't recur or doesn't have any events")
            return None