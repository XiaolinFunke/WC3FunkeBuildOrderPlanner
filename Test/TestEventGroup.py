import unittest

from SimEngine.EventHandler import EventHandler
from SimEngine.Event import Event
from SimEngine.EventGroup import EventGroup

class TestEventGroup(unittest.TestCase):
    #Test that the isLastEventInGroup method works correctly
    def testIsLastEventInGroup(self):
        eventHandler = EventHandler() 
        event1 = Event(eventFunction = None, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event2 = Event(eventFunction = None, reverseFunction = None, eventTime = 15, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event3 = Event(eventFunction = None, reverseFunction = None, eventTime = 20, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventGroup = EventGroup( orderedEventList = [ event1, event2, event3 ], recurrenceGapSimTime = 0)

        self.assertFalse(eventGroup.isLastEventInGroup(event1.getEventID()))
        self.assertFalse(eventGroup.isLastEventInGroup(event2.getEventID()))
        self.assertTrue(eventGroup.isLastEventInGroup(event3.getEventID()))

    #Test that delaying an event in an event group also delays the future events in the group
    def testDelayEventGroup(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        self.delayAmount = 10
        def incrementOrDelay(currSimTime):
            if self.delayAmount != 0:
                return self.delayAmount
            self.testInt += 1
            return 0

        event1 = Event(eventFunction = incrementOrDelay, reverseFunction = None, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event2 = Event(eventFunction = incrementOrDelay, reverseFunction = None, eventTime = 15, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event3 = Event(eventFunction = incrementOrDelay, reverseFunction = None, eventTime = 20, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventGroup = EventGroup( orderedEventList = [ event1, event2, event3 ], recurrenceGapSimTime = 0)

        eventHandler.registerEvent(event=event1, eventGroup=eventGroup)
        eventHandler.registerEvent(event=event2, eventGroup=eventGroup)
        eventHandler.registerEvent(event=event3, eventGroup=eventGroup)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(10)
        #None should be executed still, since they should have been delayed by 10 simseconds
        self.assertEqual(self.testInt, 0)

        self.delayAmount = 0
        #Should be nothing at 15, since it was delayed
        eventHandler.executeEvents(15)
        eventHandler.executeEvents(20)
        #We should now be executing the first event that was delayed
        #None of the others should have been executed, since they should have been delayed with it
        self.assertEqual(self.testInt, 1)

        self.delayAmount = 2
        eventHandler.executeEvents(25)
        #The second event should have been delayed until time 25 and will be delayed further now
        self.assertEqual(self.testInt, 1)

        self.delayAmount = 0
        eventHandler.executeEvents(27)
        #The second event should have been delayed until time 27 and will be executed now
        self.assertEqual(self.testInt, 2)

        eventHandler.executeEvents(32)
        #The third event should have been delayed until time 32 and will be executed now
        self.assertEqual(self.testInt, 3)

    #Test that an event group will be recurred once the last event of the group is executed, if it is an event group that is marked for recurrence
    def testRecurEventGroup(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        self.delayAmount = 0
        def incrementOrDelay(currSimTime):
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
        #Execute all 3 events
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEvents(15)
        self.assertEqual(self.testInt, 2)
        eventHandler.executeEvents(20)
        self.assertEqual(self.testInt, 3)

        #Now, the events should have recurred and will be at 30, 35, 40 simtimes
        #Execute all 3 again
        eventHandler.executeEvents(30)
        self.assertEqual(self.testInt, 4)
        eventHandler.executeEvents(35)
        self.assertEqual(self.testInt, 5)
        eventHandler.executeEvents(40)
        self.assertEqual(self.testInt, 6)

        #Now, the events should have recurred and will be at 50, 55, 60 simtimes
        #Execute all 3 again
        eventHandler.executeEvents(50)
        self.assertEqual(self.testInt, 7)
        eventHandler.executeEvents(55)
        self.assertEqual(self.testInt, 8)
        eventHandler.executeEvents(60)
        self.assertEqual(self.testInt, 9)

    #Test that event group recurrence works properly if one of the events is delayed
    def testRecurEventGroupWithDelays(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        self.delayAmount = 0
        def incrementOrDelay(currSimTime):
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
        #Delay first event
        self.delayAmount = 10
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 0)
        self.delayAmount = 0
        #Execute all 3 events
        eventHandler.executeEvents(20)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEvents(25)
        self.assertEqual(self.testInt, 2)
        eventHandler.executeEvents(30)
        self.assertEqual(self.testInt, 3)

        #Now, the events should have recurred and will be at 40, 45, 50 simtimes, because of the 10s delay
        #Delay 2nd event this time
        eventHandler.executeEvents(40)
        self.assertEqual(self.testInt, 4)
        self.delayAmount = 20
        eventHandler.executeEvents(45)
        self.assertEqual(self.testInt, 4)
        self.delayAmount = 0
        #Now execute the remaining events
        eventHandler.executeEvents(65)
        self.assertEqual(self.testInt, 5)
        eventHandler.executeEvents(70)
        self.assertEqual(self.testInt, 6)

        #Events will be at 80, 85, 90
        #Delay the 3rd event this time
        eventHandler.executeEvents(80)
        self.assertEqual(self.testInt, 7)
        eventHandler.executeEvents(85)
        self.assertEqual(self.testInt, 8)
        self.delayAmount = 10
        eventHandler.executeEvents(90)
        self.assertEqual(self.testInt, 8)
        self.delayAmount = 0
        eventHandler.executeEvents(100)
        self.assertEqual(self.testInt, 9)

        #Despite delay on the event that will trigger the event group recurrence, the remaining events should be at 110, 115, 120
        eventHandler.executeEvents(110)
        self.assertEqual(self.testInt, 10)
        eventHandler.executeEvents(115)
        self.assertEqual(self.testInt, 11)
        eventHandler.executeEvents(120)
        self.assertEqual(self.testInt, 12)

    #Test that reversing events in an event group that have been delayed works as expected
    def testReverseDelayedEventGroup(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        self.delayAmount = 0
        def incrementOrDelay(currSimTime):
            if self.delayAmount != 0:
                return self.delayAmount
            self.testInt += 1
            return 0
        def decrement(currSimTime):
            self.testInt -= 1

        event1 = Event(eventFunction = incrementOrDelay, reverseFunction = decrement, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event2 = Event(eventFunction = incrementOrDelay, reverseFunction = decrement, eventTime = 15, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event3 = Event(eventFunction = incrementOrDelay, reverseFunction = decrement, eventTime = 20, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventGroup = EventGroup( orderedEventList = [ event1, event2, event3 ], recurrenceGapSimTime = 0)

        eventHandler.registerEvent(event=event1, eventGroup=eventGroup)
        eventHandler.registerEvent(event=event2, eventGroup=eventGroup)
        eventHandler.registerEvent(event=event3, eventGroup=eventGroup)

        self.assertEqual(self.testInt, 0)
        #Delay first event and then reverse it
        self.delayAmount = 10
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 0)
        eventHandler.reverseEvents(10)

        #Events should have gone back to normal (delayed events spawned should be removed, and disabled events re-enabled)
        self.delayAmount = 0
        #Should be able to execute and reverse again without errors despite not being delayed anymore
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 1)
        eventHandler.reverseEvents(10)
        self.assertEqual(self.testInt, 0)

        #Now can execute all 3 events normally
        eventHandler.executeEvents(10)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEvents(15)
        self.assertEqual(self.testInt, 2)
        eventHandler.executeEvents(20)
        self.assertEqual(self.testInt, 3)
        #Should be no events at these times, since those delayed events should have been removed
        eventHandler.executeEvents(25)
        self.assertEqual(self.testInt, 3)
        eventHandler.executeEvents(30)
        self.assertEqual(self.testInt, 3)

        #Reverse the last 2 events so we can see what happens if we reverse an event that was only delayed due to an event before it being delayed
        eventHandler.reverseEvents(20)
        self.assertEqual(self.testInt, 2)
        eventHandler.reverseEvents(15)
        self.assertEqual(self.testInt, 1)

        #Delay 2nd event in group
        self.delayAmount = 10
        eventHandler.executeEvents(15)
        self.assertEqual(self.testInt, 1)
        self.delayAmount = 0
        eventHandler.executeEvents(25)
        self.assertEqual(self.testInt, 2)
        eventHandler.executeEvents(30)
        self.assertEqual(self.testInt, 3)

        #Reversing the delayed events shouldn't get rid of any events
        eventHandler.reverseEvents(30)
        self.assertEqual(self.testInt, 2)
        eventHandler.executeEvents(30)
        self.assertEqual(self.testInt, 3)
        eventHandler.reverseEvents(30)
        self.assertEqual(self.testInt, 2)
        eventHandler.reverseEvents(25)
        self.assertEqual(self.testInt, 1)

        #Reversing the original 2nd event should set things back to how they were before the delay
        #There should be no event at time 30 anymore
        eventHandler.reverseEvents(15)
        self.assertEqual(self.testInt, 1)

        #These events shouldn't exist now
        eventHandler.executeEvents(25)
        self.assertEqual(self.testInt, 1)
        eventHandler.executeEvents(30)
        self.assertEqual(self.testInt, 1)

    #Test that reversing works properly with an event group that has recurred
    def testReverseRecurredEventGroup(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        self.delayAmount = 0
        def incrementOrDelay(currSimTime):
            if self.delayAmount != 0:
                return self.delayAmount
            self.testInt += 1
            return 0
        def decrement(currSimTime):
            self.testInt -= 1

        event1 = Event(eventFunction = incrementOrDelay, reverseFunction = decrement, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event2 = Event(eventFunction = incrementOrDelay, reverseFunction = decrement, eventTime = 15, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event3 = Event(eventFunction = incrementOrDelay, reverseFunction = decrement, eventTime = 20, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventGroup = EventGroup( orderedEventList = [ event1, event2, event3 ], recurrenceGapSimTime = 10)

        eventHandler.registerEvent(event=event1, eventGroup=eventGroup)
        eventHandler.registerEvent(event=event2, eventGroup=eventGroup)
        eventHandler.registerEvent(event=event3, eventGroup=eventGroup)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(10)
        eventHandler.executeEvents(15)
        eventHandler.executeEvents(20)
        self.assertEqual(self.testInt, 3)
        #Event group should recur, giving 30, 35, 40 simtimes

        #Reversing the last event in the group should undo the recurrence
        eventHandler.reverseEvents(20)
        self.assertEqual(self.testInt, 2)
        #These events shouldn't exist anymore
        eventHandler.executeEvents(30)
        eventHandler.executeEvents(35)
        eventHandler.executeEvents(40)
        self.assertEqual(self.testInt, 2)

    #Test that reversing works properly with an event group that has been delayed and then recurred
    def testReverseRecurredAndDelayedEventGroup(self):
        eventHandler = EventHandler() 

        self.testInt = 0
        self.delayAmount = 0
        def incrementOrDelay(currSimTime):
            if self.delayAmount != 0:
                return self.delayAmount
            self.testInt += 1
            return 0
        def decrement(currSimTime):
            self.testInt -= 1

        event1 = Event(eventFunction = incrementOrDelay, reverseFunction = decrement, eventTime = 10, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event2 = Event(eventFunction = incrementOrDelay, reverseFunction = decrement, eventTime = 15, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())
        event3 = Event(eventFunction = incrementOrDelay, reverseFunction = decrement, eventTime = 20, recurPeriodSimtime = 0, eventID = eventHandler.getNewEventID())

        eventGroup = EventGroup( orderedEventList = [ event1, event2, event3 ], recurrenceGapSimTime = 10)

        eventHandler.registerEvent(event=event1, eventGroup=eventGroup)
        eventHandler.registerEvent(event=event2, eventGroup=eventGroup)
        eventHandler.registerEvent(event=event3, eventGroup=eventGroup)

        self.assertEqual(self.testInt, 0)
        eventHandler.executeEvents(10)
        eventHandler.executeEvents(15)
        self.delayAmount = 10
        eventHandler.executeEvents(20)
        self.delayAmount = 0
        eventHandler.executeEvents(30)
        self.assertEqual(self.testInt, 3)
        #Event group should recur, giving 40, 45, 50 simtimes due to the delay

        #Reversing the last event in the group should undo the recurrence
        eventHandler.reverseEvents(30)
        self.assertEqual(self.testInt, 2)
        #These events shouldn't exist anymore
        eventHandler.executeEvents(40)
        eventHandler.executeEvents(45)
        eventHandler.executeEvents(50)
        self.assertEqual(self.testInt, 2)

        #Undoing this event should undo the delay
        eventHandler.reverseEvents(20)
        self.assertEqual(self.testInt, 2)
        #These events shouldn't exist anymore
        eventHandler.executeEvents(25)
        eventHandler.executeEvents(30)
        self.assertEqual(self.testInt, 2)

        #Executing this event again should now cause a recurrence at the non-delayed time
        eventHandler.executeEvents(20)
        self.assertEqual(self.testInt, 3)
        eventHandler.executeEvents(30)
        self.assertEqual(self.testInt, 4)
        eventHandler.executeEvents(35)
        self.assertEqual(self.testInt, 5)
        eventHandler.executeEvents(40)
        self.assertEqual(self.testInt, 6)