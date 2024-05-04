from SimEngine.SimulationConstants import WorkerTask, Race, SECONDS_TO_SIMTIME, UnitType, STARTING_FOOD_MAX_MAP
from SimEngine.EventHandler import Event, EventHandler
from SimEngine.Timeline import WispTimeline, GoldMineTimeline, TimelineType, WorkerMovementAction, Timeline

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
            for i in range(5):
                self.mInactiveTimelines.append(WispTimeline(timelineType = TimelineType.WORKER, currentTask = WorkerTask.ROAMING, timelineID = self.getNextTimelineID(), eventHandler=self.mEventHandler))
            self.mInactiveTimelines.append(GoldMineTimeline(timelineType = TimelineType.GOLD_MINE, timelineID = self.getNextTimelineID(), race = self.mRace, currentResources = self.mCurrentResources, eventHandler=self.mEventHandler))
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

    def addWorkerToMine(self):
        mineTimeline = self.findMatchingTimeline(TimelineType.GOLD_MINE)
        mineTimeline.addWorkerToMine(self.mCurrentSimTime)

    def removeWorkerFromMine(self):
        mineTimeline = self.findMatchingTimeline(TimelineType.GOLD_MINE)
        mineTimeline.removeWorkerFromMine(self.mCurrentSimTime)

    def sendWorkerToMine(self, timelineID, travelTime):
        #TODO: Should these two actions just be called on the timeline once it's found?
        #TODO: Should we also be looking at whether the worker is available to be used like we do with building units?
        #For example, a unit could be building a building, which would be an uninteruptable task (for elf and orc at least)
        if self.mRace == Race.NIGHT_ELF or self.mRace == Race.UNDEAD:
            enterMineEvent = Event(eventFunction = lambda: self.addWorkerToMine(), eventTime=self.mCurrentSimTime + travelTime, recurPeriodSimtime = 0, eventName = "Enter mine", eventID = self.mEventHandler.getNewEventID())
            goToMineAction = WorkerMovementAction(travelTime = travelTime, startTime = self.mCurrentSimTime, requiredTimelineType=TimelineType.WORKER, events = [enterMineEvent], actionName="Go to mine")
            if not self.addActionToMatchingTimeline(action = goToMineAction):
                print("Failed to add go to mine action to timeline")

            self.mEventHandler.registerEvent(enterMineEvent)

    def sendWorkerToLumber(self, timelineID, travelTime):
        if self.mRace == Race.NIGHT_ELF:
            timeToLumb = 8 * SECONDS_TO_SIMTIME
            lumberGained = 5
            gainLumberEvent = Event(eventFunction = lambda: self.addLumberToCount(lumberGained), eventTime=self.mCurrentSimTime + travelTime + timeToLumb , recurPeriodSimtime = timeToLumb, eventName = "Gain 5 lumber", eventID = self.mEventHandler.getNewEventID())
            goToLumberAction = WorkerMovementAction(travelTime = travelTime, startTime = self.mCurrentSimTime, requiredTimelineType=TimelineType.WORKER, events = [gainLumberEvent], actionName="Go to lumber")
            if not self.addActionToMatchingTimeline(action = goToLumberAction):
                print("Failed to add go to lumber action to timeline")

            self.mEventHandler.registerEvent(gainLumberEvent)

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
        return True

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