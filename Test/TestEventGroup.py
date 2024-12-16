import unittest

from SimEngine.EventHandler import EventHandler
from SimEngine.Event import Event
from SimEngine.EventGroup import EventGroup

class TestEventGroup(unittest.TestCase):
    #Test that delaying an event in an event group also delays the future events in the group
    def testDelayEventGroup(self):
        eventHandler = EventHandler() 

        #TODO: These don't really have to be member vars do they?
        self.testInt = 0
        self.delayAmount = 10
        def incrementOrDelay():
            if self.delayAmount != 0:
                return self.delayAmount
            self.testInt += 1
            return 0

        event1 = Event(eventFunction = incrementOrDelay, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event2 = Event(eventFunction = incrementOrDelay, reverseFunction = None, eventTime = 15, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event3 = Event(eventFunction = incrementOrDelay, reverseFunction = None, eventTime = 20, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventGroup = EventGroup( orderedEventList = [ event1, event2, event3 ], recurrenceGapSimTime = 10)

        eventHandler.registerEvent(event=event1, eventGroup=eventGroup)
        eventHandler.registerEvent(event=event2, eventGroup=eventGroup)
        eventHandler.registerEvent(event=event3, eventGroup=eventGroup)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEventsInRange(0, 15)
        #None should be executed still, since they should have been delayed by 10 simseconds
        self.assertEqual(self.testInt, 0)

        self.delayAmount = 0
        eventHandler.executeEventsInRange(16, 20)
        #We should now be executing the first event that was delayed
        #None of the others should have been executed, since they should have been delayed with it
        self.assertEqual(self.testInt, 1)

        self.delayAmount = 2
        eventHandler.executeEventsInRange(21, 25)
        #The second event should have been delayed until time 25 and will be delayed further now
        self.assertEqual(self.testInt, 1)

        self.delayAmount = 0
        eventHandler.executeEventsInRange(26, 27)
        #The second event should have been delayed until time 27 and will be executed now
        self.assertEqual(self.testInt, 2)

        eventHandler.executeEventsInRange(28, 32)
        #The second event should have been delayed until time 32 and will be executed now
        self.assertEqual(self.testInt, 3)