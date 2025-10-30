import unittest

from SimEngine.EventHandler import EventHandler
from SimEngine.Event import Event

class TestEventHandler(unittest.TestCase):
    def testRegisterAndExecuteEvent(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment(currSimTime):
            self.testInt += 1

        event = Event(eventFunction = increment, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event=event)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 1)

    def testRegisterAndExecuteAllEventsInRange(self):
        eventHandler = EventHandler() 

        self.testInt1 = 0
        self.testInt2 = 0
        def increment1(currSimTime):
            self.testInt1 += 1

        def increment2(currSimTime):
            self.testInt2 += 1

        event1 = Event(eventFunction = increment1, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event2 = Event(eventFunction = increment2, reverseFunction = None, eventTime = 20, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event1)
        eventHandler.registerEvent(event2)

        self.assertEqual(self.testInt1, 0)
        self.assertEqual(self.testInt2, 0)
        eventHandler.executeEventsInRange(0, 9)
        self.assertEqual(self.testInt1, 0)
        self.assertEqual(self.testInt2, 0)
        eventHandler.executeEventsInRange(10, 19)
        self.assertEqual(self.testInt1, 1)
        self.assertEqual(self.testInt2, 0)
        eventHandler.executeEventsInRange(10, 20)
        self.assertEqual(self.testInt1, 1)
        self.assertEqual(self.testInt2, 1)

    def testDelayEvent(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        self.delaySimTime = 10
        def incrementOrDelay(currSimTime):
            if self.delaySimTime != 0:
                return self.delaySimTime
            self.testInt += 1
            return 0

        event = Event(eventFunction = incrementOrDelay, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event=event)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(10)
        #Should be delayed rather than executed
        self.assertEqual(self.testInt, 0)

        self.delaySimTime = 2
        eventHandler.executeEvents(20)
        #Should be delayed again
        self.assertEqual(self.testInt, 0)

        self.delaySimTime = 0
        eventHandler.executeEvents(22)
        #Should finally be executed
        self.assertEqual(self.testInt, 1)

    def testUnregisterEvent(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment(currSimTime):
            self.testInt += 1

        eventSimTime = 10
        event = Event(eventFunction = increment, reverseFunction = None, eventTime = eventSimTime, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event)
        eventHandler.unRegisterEvent(eventSimTime=eventSimTime, eventID=event.getEventID())

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEventsInRange(0, 10)
        self.assertEqual(self.testInt, 0)

    def testEventRecurrence(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment(currSimTime):
            self.testInt += 1

        event = Event(eventFunction = increment, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 10, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEventsInRange(0, 10)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEventsInRange(11, 20)
        self.assertEqual(self.testInt, 2)
        eventHandler.executeEventsInRange(21, 29)
        self.assertEqual(self.testInt, 2)
        eventHandler.executeEventsInRange(30, 30)
        self.assertEqual(self.testInt, 3)
        eventHandler.executeEventsInRange(31,40)
        self.assertEqual(self.testInt, 4)

    #Recurring events with non-integer simtime periods should not accumulate error over time. We should always be within half a simtime step of correct
    def testEventRecurrenceNonInteger(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment(currSimTime):
            self.testInt += 1

        recurPeriodSimtime = 10.1
        event = Event(eventFunction = increment, reverseFunction = None, eventTime = 10, recurPeriodSimtime = recurPeriodSimtime, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event)

        #If we lose 0.1 simtime steps each recurrence (each recurrence if faster by that amount), we would be off by 
        #0.1 * (simTime / 10.1) simTime steps (divide by 10 again to get how far integer is off)
        simTime = 10100
        eventHandler.executeEventsInRange(0, simTime)
        numIncrements = round(simTime / recurPeriodSimtime)
        self.assertEqual(self.testInt, numIncrements)

    #If a recurring event has a start time that is a non-integer, that initial error should also be taken into account
    def testEventRecurrenceNonIntegerStartTime(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment(currSimTime):
            self.testInt += 1

        recurPeriodSimtime = 1.2
        event = Event(eventFunction = increment, reverseFunction = None, eventTime = 1.4, recurPeriodSimtime = recurPeriodSimtime, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event)

        #If we don't take into account the event time's error, we'd increment at time 1, 2, and 3
        #If we do, we should increment at time 1, 3 and 4
        #Real would be time 1.4, 2.6, 3.8
        eventHandler.executeEventsInRange(0, 2)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEventsInRange(2, 3)
        self.assertEqual(self.testInt, 2)
        eventHandler.executeEventsInRange(3, 4)
        self.assertEqual(self.testInt, 3)

    def testUnregisterRecurringEvent(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment(currSimTime):
            self.testInt += 1

        event = Event(eventFunction = increment, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 10, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEventsInRange(0, 10)
        self.assertEqual(self.testInt, 1)

        #The original event will be unregistered, but it has already recurred, so that event won't be unregistered
        eventHandler.unRegisterEvent(eventSimTime=20, eventID=event.getEventID())
        eventHandler.executeEventsInRange(11, 20)
        self.assertEqual(self.testInt, 2)
        eventHandler.executeEventsInRange(21, 30)
        self.assertEqual(self.testInt, 3)
        eventHandler.executeEventsInRange(31,40)
        self.assertEqual(self.testInt, 4)

    def testGetNewEventID(self):
        eventHandler = EventHandler() 

        self.assertEqual(eventHandler.getNewEventID(), 0)
        self.assertEqual(eventHandler.getNewEventID(), 1)
        self.assertEqual(eventHandler.getNewEventID(), 2)
        self.assertEqual(eventHandler.getNewEventID(), 3)
        self.assertEqual(eventHandler.getNewEventID(), 4)

    #If the same time is executed twice in a row, the event handler should only execute the new events that have been
    #added for that time since the previous execution
    #Test that ONLY the new events are executed
    def testExecuteSameTimeAgain(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment(currSimTime):
            self.testInt += 1
        event = Event(eventFunction = increment, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEventsInRange(0, 10)
        self.assertEqual(self.testInt, 1)

        self.testInt2 = 0
        def increment2(currSimTime):
            self.testInt2 += 1
        event2 = Event(eventFunction = increment2, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event3 = Event(eventFunction = increment2, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        eventHandler.registerEvent(event2)
        eventHandler.registerEvent(event3)

        #Should only execute the new events
        eventHandler.executeEventsInRange(10, 20)
        self.assertEqual(self.testInt, 1)
        self.assertEqual(self.testInt2, 2)

    #Some events may add other events. If an event adds another event to the currently executing event list for a given simTime, that event should be executed as well
    def testEventAddsAnotherEventToOwnList(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment(currSimTime):
            self.testInt += 1
        def triggerEventFunc(currSimTime):
            eventHandler.registerEvent(incrementEvent)
        incrementEvent = Event(eventFunction = increment, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        triggerEvent = Event(eventFunction = triggerEventFunc, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(triggerEvent)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEventsInRange(0, 10)
        #Increment event wasn't in list of events when the events for time 10 are executed, but it will get added as we execute, so it should be executed as well
        self.assertEqual(self.testInt, 1)

    #Test reversing a single one-time event
    def testReverseEvent(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment(currSimTime):
            self.testInt += 1
        def decrement(currSimTime):
            self.testInt -= 1
        incrementEvent = Event(eventFunction = increment, reverseFunction = decrement, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(incrementEvent)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 1)
        eventHandler.reverseEvents(10)
        self.assertEqual(self.testInt, 0)

        #Do it again to make sure we can execute and reverse multiple times
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 1)
        eventHandler.reverseEvents(10)
        self.assertEqual(self.testInt, 0)

    #Test reversing a recurring event
    def testReverseRecurringEvent(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment(currSimTime):
            self.testInt += 1
        def decrement(currSimTime):
            self.testInt -= 1
        incrementEvent = Event(eventFunction = increment, reverseFunction = decrement, eventTime = 10, recurPeriodSimtime = 5, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(incrementEvent)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 1)
        eventHandler.reverseEvents(10)
        self.assertEqual(self.testInt, 0)

        #The event should have recurred, so now let's make sure the reversal undid that recurrence and we only get one recurring event still when we simulate forward
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEvents(15)
        self.assertEqual(self.testInt, 2)

        #Do it again to make sure we can execute and reverse multiple times and all is as expected
        eventHandler.reverseEvents(15)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEvents(15)
        self.assertEqual(self.testInt, 2)
        eventHandler.executeEvents(20)
        self.assertEqual(self.testInt, 3)

        #Now, test that if we UNREGISTER the ORIGINAL event, after reversing everything, there will be no more events registered
        eventHandler.reverseEvents(20)
        self.assertEqual(self.testInt, 2)
        eventHandler.reverseEvents(15)
        self.assertEqual(self.testInt, 1)
        eventHandler.reverseEvents(10)
        self.assertEqual(self.testInt, 0)

        eventHandler.unRegisterEvent(incrementEvent.getEventTime(), incrementEvent.getEventID())
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(15)
        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(20)
        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(25)
        self.assertEqual(self.testInt, 0)

    #Test that reversing works properly even if the event was delayed originally
    #It should be reversed back to the previous time
    def testReverseDelayedEvent(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        self.delaySimTime = 10
        def incrementOrDelay(currSimTime):
            if self.delaySimTime != 0:
                return self.delaySimTime
            self.testInt += 1
            return 0
        def decrement(currSimTime):
            self.testInt -= 1
        incrementEvent = Event(eventFunction = incrementOrDelay, reverseFunction = decrement, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(incrementEvent)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(10)
        #Event should be delayed
        self.assertEqual(self.testInt, 0)

        eventHandler.executeEvents(20)
        #Event should be delayed again
        self.assertEqual(self.testInt, 0)

        self.delaySimTime = 0
        eventHandler.executeEvents(30)
        self.assertEqual(self.testInt, 1)
        eventHandler.reverseEvents(30)
        self.assertEqual(self.testInt, 0)

        #Now that we have reversed the event at 20, the event at 30 should no longer exist, since it was spawned by the event at 20
        eventHandler.reverseEvents(20)
        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(30)
        self.assertEqual(self.testInt, 0)

        #The event at 20 should be successful now, rather than being delayed, so the event at 30 should still not exist after this is executed
        eventHandler.executeEvents(20)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEvents(30)
        self.assertEqual(self.testInt, 1)

        #Now, we can reverse the event at 10 and test the same thing again
        eventHandler.reverseEvents(20)
        self.assertEqual(self.testInt, 0)
        eventHandler.reverseEvents(10)
        self.assertEqual(self.testInt, 0)
        #Event at 20 shouldn't exist anymore
        eventHandler.executeEvents(20)
        self.assertEqual(self.testInt, 0)

        #The event at 10 should be successful now, rather than being delayed, so the event at 20 should still not exist after this is executed
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEvents(20)
        self.assertEqual(self.testInt, 1)
        eventHandler.reverseEvents(10)
        self.assertEqual(self.testInt, 0)
