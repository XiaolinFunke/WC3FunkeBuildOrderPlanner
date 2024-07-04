import unittest

from SimEngine.Timeline import Timeline 
from SimEngine.Action import Action
from SimEngine.Worker import Worker
from SimEngine.Trigger import Trigger, TriggerType

class TestTimeline(unittest.TestCase):
    def testAddAction(self):
        timeline = Timeline(timelineType=Worker.Wisp.name, timelineID=0, eventHandler=None)

        action = Action(actionID=1, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=10, requiredTimelineType=Worker.Wisp.name)
        action.setStartTime(0)
        self.assertEqual(timeline.addAction(action), True)

    def testAddMultipleActions(self):
        timeline = Timeline(timelineType=Worker.Wisp.name, timelineID=0, eventHandler=None)

        action = Action(actionID=1, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=10, requiredTimelineType=Worker.Wisp.name)
        action.setStartTime(0)
        self.assertEqual(timeline.addAction(action), True)

        action2 = Action(actionID=2, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=10, requiredTimelineType=Worker.Wisp.name)
        action2.setStartTime(15)
        self.assertEqual(timeline.addAction(action2), True)

    #Should not be able to add an Action that overlaps with one that comes before it
    #Should be able to if it overlaps with one that comes after
    def testAddOverlappingActions(self):
        timeline = Timeline(timelineType=Worker.Wisp.name, timelineID=0, eventHandler=None)

        action = Action(actionID=1, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=10, requiredTimelineType=Worker.Wisp.name)
        action.setStartTime(10)
        self.assertEqual(timeline.addAction(action), True)

        #Start time overlaps with previous action's duration
        action2 = Action(actionID=2, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=5, requiredTimelineType=Worker.Wisp.name)
        action2.setStartTime(19)
        self.assertEqual(timeline.addAction(action2), False)

        #Would overlap with previous Action, but that one should have failed to add, so this should be OK
        action3 = Action(actionID=3, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=4, requiredTimelineType=Worker.Wisp.name)
        action3.setStartTime(21)
        self.assertEqual(timeline.addAction(action3), True)

        #End time overlaps with first action's start time, but this Action comes first, so it will be added successfully and remove everything after it
        action4 = Action(actionID=4, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=6, requiredTimelineType=Worker.Wisp.name)
        action4.setStartTime(5)
        self.assertEqual(timeline.addAction(action4), True)

        #That last Action added should have removed all Actions after it, so there should only be 1 Action left on Timeline
        self.assertEqual(timeline.getNumActions(), 1)

    #Should be able to add an action that starts at the time that another action ends
    def testAddNearlyOverlappingActions(self):
        timeline = Timeline(timelineType=Worker.Wisp.name, timelineID=0, eventHandler=None)

        action = Action(actionID=1, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=10, requiredTimelineType=Worker.Wisp.name)
        action.setStartTime(10)
        self.assertEqual(timeline.addAction(action), True)

        #Starts when previous one ends
        action2 = Action(actionID=2, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=5, requiredTimelineType=Worker.Wisp.name)
        action2.setStartTime(20)
        self.assertEqual(timeline.addAction(action2), True)

    def testFindProperSpotForAction(self):
        timeline = Timeline(timelineType=Worker.Wisp.name, timelineID=0, eventHandler=None)

        action = Action(actionID=1, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=2, requiredTimelineType=Worker.Wisp.name)
        action.setStartTime(10)
        self.assertEqual(timeline.addAction(action), True)

        action2 = Action(actionID=2, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=5, requiredTimelineType=Worker.Wisp.name)
        action2.setStartTime(15)
        self.assertEqual(timeline.addAction(action2), True)

        #Action at start, no overlap
        action3 = Action(actionID=3, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=1, requiredTimelineType=Worker.Wisp.name)
        action3.setStartTime(8)
        self.assertEqual(timeline.findProperSpotForAction(action3.getStartTime()), 0)
        #Action at start, overlaps with next Action
        action4 = Action(actionID=4, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=1, requiredTimelineType=Worker.Wisp.name)
        action4.setStartTime(8)
        self.assertEqual(timeline.findProperSpotForAction(action4.getStartTime()), 0)

        #Action in middle, no overlap
        action5 = Action(actionID=5, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=1, requiredTimelineType=Worker.Wisp.name)
        action5.setStartTime(13)
        self.assertEqual(timeline.findProperSpotForAction(action5.getStartTime()), 1)
        #Action in middle, overlaps with next Action
        action6 = Action(actionID=6, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=5, requiredTimelineType=Worker.Wisp.name)
        action6.setStartTime(13)
        self.assertEqual(timeline.findProperSpotForAction(action6.getStartTime()), 1)
        #Action in middle, overlaps with previous Action
        action7 = Action(actionID=7, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=3, requiredTimelineType=Worker.Wisp.name)
        action7.setStartTime(11)
        self.assertEqual(timeline.findProperSpotForAction(action7.getStartTime()), 1)

        #Action at end, no overlap
        action8 = Action(actionID=8, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=2, requiredTimelineType=Worker.Wisp.name)
        action8.setStartTime(21)
        self.assertEqual(timeline.findProperSpotForAction(action8.getStartTime()), 2)
        #Action at end, overlaps with previous Action
        action9 = Action(actionID=9, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=5, requiredTimelineType=Worker.Wisp.name)
        action9.setStartTime(19)
        self.assertEqual(timeline.findProperSpotForAction(action9.getStartTime()), 2)

    def testGetNextPossibleTimeForAction(self):
        timeline = Timeline(timelineType=Worker.Wisp.name, timelineID=0, eventHandler=None)

        action = Action(actionID=1, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=2, requiredTimelineType=Worker.Wisp.name)
        action.setStartTime(10)
        self.assertEqual(timeline.addAction(action), True)

        action2 = Action(actionID=2, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=5, requiredTimelineType=Worker.Wisp.name)
        action2.setStartTime(15)
        self.assertEqual(timeline.addAction(action2), True)

        #Action at start, no overlap
        action3 = Action(actionID=3, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=1, requiredTimelineType=Worker.Wisp.name)
        action3.setStartTime(8)
        self.assertEqual(timeline.getNextPossibleTimeForAction(action3.getStartTime()), 8)
        #Action at start, overlaps with next Action
        action4 = Action(actionID=4, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=1, requiredTimelineType=Worker.Wisp.name)
        action4.setStartTime(8)
        self.assertEqual(timeline.getNextPossibleTimeForAction(action4.getStartTime()), 8)

        #Action in middle, no overlap
        action5 = Action(actionID=5, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=1, requiredTimelineType=Worker.Wisp.name)
        action5.setStartTime(13)
        self.assertEqual(timeline.getNextPossibleTimeForAction(action5.getStartTime()), 13)
        #Action in middle, overlaps with next Action
        action6 = Action(actionID=6, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=5, requiredTimelineType=Worker.Wisp.name)
        action6.setStartTime(13)
        self.assertEqual(timeline.getNextPossibleTimeForAction(action6.getStartTime()), 13)
        #Action in middle, overlaps with previous Action -- This means the next possible time will be pushed to the end of the previous Action
        action7 = Action(actionID=7, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=3, requiredTimelineType=Worker.Wisp.name)
        action7.setStartTime(11)
        self.assertEqual(timeline.getNextPossibleTimeForAction(action7.getStartTime()), 12)

        #Action at end, no overlap
        action8 = Action(actionID=8, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=2, requiredTimelineType=Worker.Wisp.name)
        action8.setStartTime(21)
        self.assertEqual(timeline.getNextPossibleTimeForAction(action8.getStartTime()), 21)
        #Action at end, overlaps with previous Action -- This means the next possible time will be pushed to the end of the previous Action
        action9 = Action(actionID=9, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=5, requiredTimelineType=Worker.Wisp.name)
        action9.setStartTime(19)
        self.assertEqual(timeline.getNextPossibleTimeForAction(action9.getStartTime()), 20)

    def testGetNextAction(self):
        timeline = Timeline(timelineType=Worker.Wisp.name, timelineID=0, eventHandler=None)

        actionStartTime=10
        action = Action(actionID=1, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=0, requiredTimelineType=Worker.Wisp.name)
        action.setStartTime(actionStartTime)
        timeline.addAction(action)

        nextAction = timeline.getNextAction(actionStartTime)
        self.assertEqual(action, nextAction)

        nextAction = timeline.getNextAction(0)
        self.assertEqual(action, nextAction)

        nextAction = timeline.getNextAction(actionStartTime + 1)
        self.assertEqual(None, nextAction)

    def testGetPrevAction(self):
        timeline = Timeline(timelineType=Worker.Wisp.name, timelineID=0, eventHandler=None)

        actionStartTime=10
        action = Action(actionID=1, name="", goldCost=0, lumberCost=0, trigger=Trigger(TriggerType.ASAP), travelTime=0, duration=0, requiredTimelineType=Worker.Wisp.name)
        action.setStartTime(actionStartTime)
        timeline.addAction(action)

        #getPrevAction doesn't return an action with start time exactly equal
        prevAction = timeline.getPrevAction(actionStartTime)
        self.assertEqual(None, prevAction)

        prevAction = timeline.getPrevAction(actionStartTime + 1)
        self.assertEqual(action, prevAction)

        prevAction = timeline.getPrevAction(0)
        self.assertEqual(None, prevAction)
