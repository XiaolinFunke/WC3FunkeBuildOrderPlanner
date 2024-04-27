import unittest

from SimEngine.EventHandler import EventHandler, Event

class TestEventHandler(unittest.TestCase):
    def testRegisterAndExecuteEvent(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment():
            self.testInt += 1

        event = Event(eventFunction = lambda: increment(), eventTime = 10,recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event=event)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 1)

    def testRegisterAndExecuteAllEventsInRange(self):
        eventHandler = EventHandler() 

        self.testInt1 = 0
        self.testInt2 = 0
        def increment1():
            self.testInt1 += 1

        def increment2():
            self.testInt2 += 1

        event1 = Event(eventFunction = lambda: increment1(), eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event2 = Event(eventFunction = lambda: increment2(), eventTime = 20, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

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
        self.assertEqual(self.testInt1, 2)
        self.assertEqual(self.testInt2, 1)

    def testUnregisterEvent(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment():
            self.testInt += 1

        eventSimTime = 10
        event = Event(eventFunction = lambda: increment(), eventTime = eventSimTime, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event)
        eventHandler.unRegisterEvent(eventSimTime=eventSimTime, eventID=event.getEventID())

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEventsInRange(0, 10)
        self.assertEqual(self.testInt, 0)

    def testEventRecurrence(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment():
            self.testInt += 1

        event = Event(eventFunction = lambda: increment(), eventTime = 10, recurPeriodSimtime = 10, eventID = eventHandler.getNewEventID())

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
        def increment():
            self.testInt += 1

        recurPeriodSimtime = 10.1
        event = Event(eventFunction = lambda: increment(), eventTime = 10, recurPeriodSimtime = recurPeriodSimtime, eventID = eventHandler.getNewEventID())

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
        def increment():
            self.testInt += 1

        recurPeriodSimtime = 1.2
        event = Event(eventFunction = lambda: increment(), eventTime = 1.4, recurPeriodSimtime = recurPeriodSimtime, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event)

        #If we don't take into account the event time's error, we'd increment at time 1, 2, and 3
        #If we do, we should increment at time 1, 3 and 4
        #Real would be time 1.4, 2.6, 3.8
        simTime = 2
        eventHandler.executeEventsInRange(0, simTime)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEventsInRange(simTime, 3)
        self.assertEqual(self.testInt, 2)

    def testUnregisterRecurringEvent(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        def increment():
            self.testInt += 1

        event = Event(eventFunction = lambda: increment(), eventTime = 10, recurPeriodSimtime = 10, eventID = eventHandler.getNewEventID())

        eventHandler.registerEvent(event)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEventsInRange(0, 10)
        self.assertEqual(self.testInt, 1)

        eventHandler.unRegisterEvent(eventSimTime=20, eventID=event.getEventID())
        eventHandler.executeEventsInRange(11, 20)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEventsInRange(21, 30)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEventsInRange(31,40)
        self.assertEqual(self.testInt, 1)

    def testGetNewEventID(self):
        eventHandler = EventHandler() 

        self.assertEqual(eventHandler.getNewEventID(), 0)
        self.assertEqual(eventHandler.getNewEventID(), 1)
        self.assertEqual(eventHandler.getNewEventID(), 2)
        self.assertEqual(eventHandler.getNewEventID(), 3)
        self.assertEqual(eventHandler.getNewEventID(), 4)
        

if __name__ == "__main__":
    unittest.main()