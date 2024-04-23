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