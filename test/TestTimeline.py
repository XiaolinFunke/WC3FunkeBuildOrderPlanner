import unittest

from SimEngine.Timeline import Timeline, TimelineType, Action

class TestTimeline(unittest.TestCase):
    def testGetNextAction(self):
        timeline = Timeline(timelineType=TimelineType.WORKER, timelineID=0)

        actionStartTime=10
        action = Action(goldCost=0, lumberCost=0, foodCost=0, travelTime=0, startTime=actionStartTime, duration=0, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        timeline.addAction(action)

        nextAction = timeline.getNextAction(actionStartTime)
        self.assertEqual(action, nextAction)

        nextAction = timeline.getNextAction(0)
        self.assertEqual(action, nextAction)

        nextAction = timeline.getNextAction(actionStartTime + 1)
        self.assertEqual(None, nextAction)

    def testGetPrevAction(self):
        timeline = Timeline(timelineType=TimelineType.WORKER, timelineID=0)

        actionStartTime=10
        action = Action(goldCost=0, lumberCost=0, foodCost=0, travelTime=0, startTime=actionStartTime, duration=0, requiredTimelineType=TimelineType.WORKER, events = [], actionName="Test action")
        timeline.addAction(action)

        #getPrevAction doesn't return an action with start time exactly equal
        prevAction = timeline.getPrevAction(actionStartTime)
        self.assertEqual(None, prevAction)

        prevAction = timeline.getPrevAction(actionStartTime + 1)
        self.assertEqual(action, prevAction)

        prevAction = timeline.getPrevAction(0)
        self.assertEqual(None, prevAction)
