import unittest

from SimEngine.Timeline import Timeline 
from SimEngine.TimelineTypeEnum import TimelineType
from SimEngine.Action import Action

class TestTimeline(unittest.TestCase):
    def testAddAction(self):
        timeline = Timeline(timelineType=TimelineType.WORKER, timelineID=0, eventHandler=None)

        action = Action(goldCost=0, lumberCost=0, travelTime=0, startTime=0, duration=10, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action), True)

    def testAddMultipleActions(self):
        timeline = Timeline(timelineType=TimelineType.WORKER, timelineID=0, eventHandler=None)

        action = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=0, duration=10, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action), True)

        action2 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=15, duration=10, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action2), True)

    #Should not be able to add an Action that overlaps with one that comes before it
    #Should be able to if it overlaps with one that comes after
    def testAddOverlappingActions(self):
        timeline = Timeline(timelineType=TimelineType.WORKER, timelineID=0, eventHandler=None)

        action = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=10, duration=10, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action), True)

        #Start time overlaps with previous action's duration
        action2 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=19, duration=5, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action2), False)

        #Would overlap with previous Action, but that one should have failed to add, so this should be OK
        action4 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=21, duration=4, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action4), True)

        #End time overlaps with first action's start time, but this Action comes first, so it will be added successfully and remove everything after it
        action4 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=5, duration=6, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action4), True)

        #That last Action added should have removed all Actions after it, so there should only be 1 Action left on Timeline
        self.assertEqual(timeline.getNumActions(), 1)

    #Should be able to add an action that starts at the time that another action ends
    def testAddNearlyOverlappingActions(self):
        timeline = Timeline(timelineType=TimelineType.WORKER, timelineID=0, eventHandler=None)

        action = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=10, duration=10, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action), True)

        #Starts when previous one ends
        action2 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=20, duration=5, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action2), True)

    def testFindProperSpotForAction(self):
        timeline = Timeline(timelineType=TimelineType.WORKER, timelineID=0, eventHandler=None)

        action = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=10, duration=2, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action), True)

        action2 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=15, duration=5, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action2), True)

        #Action at start, no overlap
        action3 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=8, duration=1, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.findProperSpotForAction(action3.getStartTime()), 0)
        #Action at start, overlaps with next Action
        action4 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=8, duration=1, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.findProperSpotForAction(action4.getStartTime()), 0)

        #Action in middle, no overlap
        action5 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=13, duration=1, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.findProperSpotForAction(action5.getStartTime()), 1)
        #Action in middle, overlaps with next Action
        action6 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=13, duration=5, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.findProperSpotForAction(action6.getStartTime()), 1)
        #Action in middle, overlaps with previous Action
        action7 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=11, duration=3, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.findProperSpotForAction(action7.getStartTime()), 1)

        #Action at end, no overlap
        action8 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=21, duration=2, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.findProperSpotForAction(action8.getStartTime()), 2)
        #Action at end, overlaps with previous Action
        action9 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=19, duration=5, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.findProperSpotForAction(action9.getStartTime()), 2)

    def testGetNextPossibleTimeForAction(self):
        timeline = Timeline(timelineType=TimelineType.WORKER, timelineID=0, eventHandler=None)

        action = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=10, duration=2, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action), True)

        action2 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=15, duration=5, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.addAction(action2), True)

        #Action at start, no overlap
        action3 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=8, duration=1, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.getNextPossibleTimeForAction(action3.getStartTime()), 8)
        #Action at start, overlaps with next Action
        action4 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=8, duration=1, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.getNextPossibleTimeForAction(action4.getStartTime()), 8)

        #Action in middle, no overlap
        action5 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=13, duration=1, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.getNextPossibleTimeForAction(action5.getStartTime()), 13)
        #Action in middle, overlaps with next Action
        action6 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=13, duration=5, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.getNextPossibleTimeForAction(action6.getStartTime()), 13)
        #Action in middle, overlaps with previous Action -- This means the next possible time will be pushed to the end of the previous Action
        action7 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=11, duration=3, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.getNextPossibleTimeForAction(action7.getStartTime()), 12)

        #Action at end, no overlap
        action8 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=21, duration=2, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.getNextPossibleTimeForAction(action8.getStartTime()), 21)
        #Action at end, overlaps with previous Action -- This means the next possible time will be pushed to the end of the previous Action
        action9 = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=19, duration=5, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        self.assertEqual(timeline.getNextPossibleTimeForAction(action9.getStartTime()), 20)

    def testGetNextAction(self):
        timeline = Timeline(timelineType=TimelineType.WORKER, timelineID=0, eventHandler=None)

        actionStartTime=10
        action = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=actionStartTime, duration=0, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        timeline.addAction(action)

        nextAction = timeline.getNextAction(actionStartTime)
        self.assertEqual(action, nextAction)

        nextAction = timeline.getNextAction(0)
        self.assertEqual(action, nextAction)

        nextAction = timeline.getNextAction(actionStartTime + 1)
        self.assertEqual(None, nextAction)

    def testGetPrevAction(self):
        timeline = Timeline(timelineType=TimelineType.WORKER, timelineID=0, eventHandler=None)

        actionStartTime=10
        action = Action(goldCost=0, lumberCost=0,travelTime=0, startTime=actionStartTime, duration=0, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        timeline.addAction(action)

        #getPrevAction doesn't return an action with start time exactly equal
        prevAction = timeline.getPrevAction(actionStartTime)
        self.assertEqual(None, prevAction)

        prevAction = timeline.getPrevAction(actionStartTime + 1)
        self.assertEqual(action, prevAction)

        prevAction = timeline.getPrevAction(0)
        self.assertEqual(None, prevAction)
