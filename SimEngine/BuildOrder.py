from SimEngine.SimulationConstants import Race, UnitType, STARTING_FOOD_MAX_MAP, StructureType, WorkerTask
from SimEngine.EventHandler import EventHandler
from SimEngine.Timeline import WispTimeline, GoldMineTimeline, TimelineType, Timeline

class MapStartingPosition:
    def __init__(self, name, lumberTripTravelTimeSec, goldTripTravelTimeSec):
        self.mName = name
        self.mLumberTripTravelTimeSec = lumberTripTravelTimeSec
        self.mLumberTravelTimeIncreasePerTreeChoppedSec = 0
        self.mGoldTripTravelTimeSec = goldTripTravelTimeSec
        #Only applies when fewer than 5 workers. Otherwise will just be 5s each
        self.mGoldTripTravelTimeWithMicroSec = 5

class BuildOrder:
    def __init__(self, race):
        self.mActiveTimelines = []
        self.mInactiveTimelines = []
        self.mName = ""
        self.mRace = race
        self.mMapStartingPosition = MapStartingPosition(name = "Ideal_Map_Ideal_Position", lumberTripTravelTimeSec=15, goldTripTravelTimeSec=5) 

        self.mNextTimelineID = 0

        self.mCurrentResources = CurrentResources(race)
        self.mEventHandler = EventHandler()
        self.mCurrentSimTime = 0

        #Give initial starting units
        if self.mRace == Race.NIGHT_ELF:
            goldMineTimeline = GoldMineTimeline(timelineType = TimelineType.GOLD_MINE, timelineID = self.getNextTimelineID(), race = self.mRace, currentResources = self.mCurrentResources, eventHandler=self.mEventHandler)
            self.mInactiveTimelines.append(goldMineTimeline)
            for i in range(5):
                self.mInactiveTimelines.append(WispTimeline(timelineID = self.getNextTimelineID(), eventHandler=self.mEventHandler))
            self.mInactiveTimelines.append(Timeline(timelineType = TimelineType.TREE_OF_LIFE, timelineID = self.getNextTimelineID(), eventHandler = self.mEventHandler))

    #Will simulate up to specified simtime
    def simulate(self, untilSimTime):
        #Current sim time wll be executed now, even though it was executed last simulate() call
        #Event Handler knows to only execute the events that have been added to the current time since then
        for time in range(self.mCurrentSimTime, untilSimTime + 1):
            self.mCurrentSimTime = time
            self.mEventHandler.executeEvents(time)

    def getNextTimelineID(self):
        timelineID = self.mNextTimelineID
        self.mNextTimelineID += 1
        return timelineID

    def getCurrSimTime(self):
        return self.mCurrentSimTime

    def getEventHandler(self):
        return self.mEventHandler
                
    def getCurrentResources(self):
        return self.mCurrentResources

    def addLumberToCount(self, amount):
        self.mCurrentResources.mCurrentLumber += amount

    def sendWorkerToMine(self, timelineID, travelTime):
        #TODO: Should we also be looking at whether the worker is available to be used like we do with building units?
        #For example, a unit could be building a building, which would be an uninteruptable task (for elf and orc at least)
        goldMineTimeline = self.findMatchingTimeline(TimelineType.GOLD_MINE)
        self.findMatchingTimeline(TimelineType.WORKER, timelineID).sendWorkerToMine(goldMineTimeline, self.mCurrentSimTime, travelTime)
        #After each action, simulate the current time again, in case new events have been added that should be executed before the next command comes in
        self.simulate(self.mCurrentSimTime)

    def sendWorkerToLumber(self, timelineID, travelTime):
        #TODO: A little bit odd that we need to pass teh goldmine here (it's because we might be moving a worker OFF of gold. But if we store it on the timeline, then we need to pass the goldmine to buildUnit just in case the unit is a wisp)
        goldMineTimeline = self.findMatchingTimeline(TimelineType.GOLD_MINE)
        self.findMatchingTimeline(TimelineType.WORKER, timelineID).sendWorkerToLumber(goldMineTimeline, self.mCurrentSimTime, self.mCurrentResources, travelTime)
        #After each action, simulate the current time again, in case new events have been added that should be executed before the next command comes in
        self.simulate(self.mCurrentSimTime)

    #Return True if successfully added, False otherwise
    #If timeline ID is not passed in, ignore it
    def addActionToMatchingTimeline(self, action, timelineID = -1):
        for timeline in self.mActiveTimelines:
            if action.getRequiredTimelineType() == timeline.getTimelineType() and (timelineID == -1 or timeline.getTimelineID() == timelineID) and timeline.addAction(action, self.mCurrentResources):
                return True

        #If none of the active timelines work, try inactive
        i = 0
        while i < len(self.mInactiveTimelines):
            if action.getRequiredTimelineType() == self.mInactiveTimelines[i].getTimelineType() and (timelineID == -1 or self.mInactiveTimelines[i].getTimelineID()) and self.mInactiveTimelines[i].addAction(action, self.mCurrentResources):
                #Now that this timeline has an item on it, it should be considered an 'active' timeline
                self.mActiveTimelines.append(self.mInactiveTimelines.pop(i))
                return True
            else:
                i += 1
        return False

    #Will return the first matching timeline (active first)
    #If timeline ID is not passed in, ignore it
    def findMatchingTimeline(self, timelineType, timelineID = -1):
        for timeline in self.mActiveTimelines:
            if timelineType == timeline.getTimelineType() and (timelineID == -1 or timeline.getTimelineID() == timelineID):
                return timeline

        #If none of the active timelines work, try inactive
        for timeline in self.mInactiveTimelines:
            if timelineType == timeline.getTimelineType() and (timelineID == -1 or timeline.getTimelineID() == timelineID):
                return timeline

    #Returns list of ALL timelines that match (Active ones will be first in the list)
    def findAllMatchingTimelines(self, timelineType):
        matchingTimelines = []

        for timeline in self.mActiveTimelines:
            if timelineType == timeline.getTimelineType():
                matchingTimelines.append(timeline)

        #If none of the active timelines work, try inactive
        for timeline in self.mInactiveTimelines:
            if timelineType == timeline.getTimelineType():
                matchingTimelines.append(timeline)

        return matchingTimelines

    #Return True if successful, False otherwise
    def buildUnit(self, unitType):
        if unitType == UnitType.WISP:
            #TODO: Have a check to make sure this will eventually be true so we don't simiulate into infinity
            while not self.areRequiredResourcesAvailable(goldRequired=60, lumberRequired=0, foodRequired=1):
                self.simulate(self.mCurrentSimTime + 1)

            #Tree of life timeline represents all tiers of tree of life
            matchingTimelines = self.findAllMatchingTimelines(TimelineType.TREE_OF_LIFE)
            if not matchingTimelines:
                print("Tried to build wisp, but did not find a matching timeline")
                return False
            
            #TODO: Need to account for if a new Timeline is scheduled to be added in the future that can handle this request
            minAvailableTime = float('inf')
            for timeline in matchingTimelines:
                prevMinAvailableTime = minAvailableTime
                minAvailableTime = min(minAvailableTime, timeline.getNextPossibleTimeForAction(self.mCurrentSimTime))
                if minAvailableTime != prevMinAvailableTime:
                    nextAvailableTimeline = timeline

            self.simulate(minAvailableTime)
            nextAvailableTimeline.buildUnit(UnitType.WISP, self.mCurrentSimTime, self.mInactiveTimelines, self.getNextTimelineID, self.mCurrentResources)
        #After each action, simulate the current time again, in case new events have been added that should be executed before the next command comes in
        self.simulate(self.mCurrentSimTime)
        return True

    #Return True if successful, False otherwise
    #Will be built with the most idle worker currently doing the workerTask passed in
    def buildStructure(self, structureType, travelTime, workerTask):
        if structureType == StructureType.ALTAR_OF_ELDERS:
            #TODO: Have a check to make sure this will eventually be true so we don't simiulate into infinity
            while not self.areRequiredResourcesAvailable(goldRequired=180, lumberRequired=50, foodRequired=0):
                self.simulate(self.mCurrentSimTime + 1)

            if workerTask == WorkerTask.GOLD or workerTask == WorkerTask.LUMBER:
                workerTimeline = self.getMostIdleWorker(workerTask == WorkerTask.GOLD)
            elif workerTask == WorkerTask.IN_PRODUCTION:
                workerTimeline = self.findMatchingTimeline(TimelineType.WORKER, self.getNextBuiltWorkerTimelineID())
            
            goldMineTimeline = self.findMatchingTimeline(TimelineType.GOLD_MINE)
            return workerTimeline.buildStructure(structureType, self.mCurrentSimTime, travelTime, self.mInactiveTimelines, self.getNextTimelineID, self.mCurrentResources, goldMineTimeline)
        #After each action, simulate the current time again, in case new events have been added that should be executed before the next command comes in
        self.simulate(self.mCurrentSimTime)
        return True
    
    #Get the timeline of the 'most idle' worker on gold or lumber
    #@param isOnGold - True if the worker should be on gold. If false, on lumber
    def getMostIdleWorker(self, isOnGold):
        workerTimelines = self.findAllMatchingTimelines(TimelineType.WORKER)
        correctTaskWorkerTimelines = []
        correctTask = WorkerTask.GOLD if isOnGold else WorkerTask.LUMBER

        for timeline in workerTimelines:
            if timeline.getCurrentTask() == correctTask:
                correctTaskWorkerTimelines.append(timeline)

        if len(correctTaskWorkerTimelines) == 0:
            return None

        #TODO: Determine the idleness of the workers
        #For now, just return the first one
        return correctTaskWorkerTimelines[0]

    #Returns the timeline ID of the next worker that will finish building
    def getNextBuiltWorkerTimelineID(self): 
        #TODO: This function could be optimized if it's a performance issue
        initialNumWorkerTimelines = len(self.findAllMatchingTimelines(TimelineType.WORKER))

        #TODO: Have some way to ensure a worker is being built, so that we know we won't simulate forever here
        self.mCurrentSimTime
        while True:
            self.simulate(self.mCurrentSimTime + 1)   
            workerTimelines = self.findAllMatchingTimelines(TimelineType.WORKER)
            #Number of worker timelines has changed. This means a worker was built
            if initialNumWorkerTimelines != len(workerTimelines):
                break

        #TODO: Handle possible edge-case if we build multiple workers at the same time
        #Return the timeline with the highest timeline ID, since that means it's newest
        highestTimelineID = float('-inf')
        for timeline in self.findAllMatchingTimelines(TimelineType.WORKER):
            highestTimelineID = max(highestTimelineID, timeline.getTimelineID())
            #TODO: Could just track the timeline of the highest here as well and return that instead of the ID - worker movement 
            #functions could call this automatically instead of needing to call this from outside

        return highestTimelineID

    #Return True if we have the gold, lumber, and food required to build a unit/building
    def areRequiredResourcesAvailable(self, goldRequired, lumberRequired, foodRequired):
        if self.mCurrentResources.getCurrentGold() < goldRequired:
            return False
        elif self.mCurrentResources.getCurrentLumber() < lumberRequired:
            return False
        elif max(self.mCurrentResources.mCurrentFoodMax - self.mCurrentResources.mCurrentFood, 0) < foodRequired:
            return False
        return True

    def printAllTimelines(self):
        print("Active Timelines:")
        for timeline in self.mActiveTimelines:
            timeline.printTimeline()
        print("Inactive Timelines:")
        for timeline in self.mInactiveTimelines:
            timeline.printTimeline()

class CurrentResources:
    def __init__(self, race):
        self.mCurrentGold = 500
        self.mCurrentLumber = 150
        self.mCurrentFood = 5

        self.mCurrentFoodMax = STARTING_FOOD_MAX_MAP[race]

    def deductGold(self, amount):
        if amount > self.mCurrentGold:
            print("Tried to deduct", amount, "gold, but only have", self.mCurrentGold)
        else:
            self.mCurrentGold -= amount

    def deductLumber(self, amount):
        if amount > self.mCurrentLumber:
            print("Tried to deduct", amount, "lumber, but only have", self.mCurrentLumber)
        else:
            self.mCurrentLumber -= amount

    def increaseMaxFood(self, amount):
        self.mCurrentFoodMax += amount

    def increaseFoodUsed(self, amount):
        self.mCurrentFood += amount

    def decreaseFoodUsedByOne(self):
        if self.mCurrentFood <= 0:
            print("Tried to decrease food used by one, but food count was", self.mCurrentFood)
        else:
            self.mCurrentFood -= 1

    def getCurrentGold(self):
        return self.mCurrentGold

    def getCurrentLumber(self):
        return self.mCurrentLumber

    def getCurrentFood(self):
        return self.mCurrentFood

    def getCurrentFoodMax(self):
        return self.mCurrentFoodMax

    def print(self):
        print("| Gold:", self.mCurrentGold, "| Lumber:", self.mCurrentLumber, "| Food:", str(self.mCurrentFood) + "/" + str(self.mCurrentFoodMax) + " |")