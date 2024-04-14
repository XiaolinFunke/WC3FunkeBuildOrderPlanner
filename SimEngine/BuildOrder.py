from enum import Enum, auto

from SimulationConstants import WorkerTask, Race, SECONDS_TO_SIMTIME
from EventHandler import Event, EventHandler
from Timeline import WispTimeline, GoldMineTimeline, Action

class MapStartingPosition:
    def __init__(self, name, lumberTripTravelTimeSec, goldTripTravelTimeSec):
        self.mName = name
        self.mLumberTripTravelTimeSec = lumberTripTravelTimeSec
        self.mLumberTravelTimeIncreasePerTreeChoppedSec = 0
        self.mGoldTripTravelTimeSec = goldTripTravelTimeSec
        #Only applies when fewer than 5 workers. Otherwise will just be 5s each
        self.mGoldTripTravelTimeWithMicroSec = 5

# Each building that can make units/upgrades has its own timeline
# There are also timelines for constructing buildings, shops to buy/sell items and tavern
class TimelineType(Enum):
    #NEUTRAL
    WORKER = auto()
    TAVERN = auto()
    GOBLIN_MERCHANT = auto()
    GOLD_MINE = auto()
    #HUMAN
    #Represents all tiers of the town hall
    TOWN_HALL = auto()
    HUMAN_BARRACKS = auto()
    LUMBER_MILL = auto()
    BLACKSMITH = auto()
    ALTAR_OF_KINGS = auto()
    ARCANE_SANCTUM = auto()
    WORKSHOP = auto()
    SCOUT_TOWER = auto()
    GRYPHON_AVIARY = auto()
    ARCANE_VAULT = auto()
    #NIGHT ELF
    #Represents all tiers of the tree of life
    TREE_OF_LIFE = auto()
    ANCIENT_OF_WAR = auto()
    HUNTERS_HALL = auto()
    ALTAR_OF_ELDERS = auto()
    ANCIENT_OF_LORE = auto()
    ANCIENT_OF_WIND = auto()
    CHIMAERA_ROOST = auto()
    ANCIENT_OF_WONDERS = auto()

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
                self.mInactiveTimelines.append(WispTimeline(timelineType = TimelineType.WORKER, currentTask = WorkerTask.ROAMING, timelineID = self.getNextTimelineID()))
            self.mInactiveTimelines.append(GoldMineTimeline(timelineType = TimelineType.GOLD_MINE, timelineID = self.getNextTimelineID(), maxWorkersInMine = 5))
            #TODO: Give main town hall timeline as well

    #Will simulate up to specified simtime
    def simulate(self, untilSimTime):
        #Ensure we execute events at time 0 even though we skip over executing events at the current
        #time generally (because they normally will have already been executed)
        if (self.mCurrentSimTime == 0):
            self.mEventHandler.executeEvents(self.mCurrentSimTime)

        self.mEventHandler.executeEventsInRange(self.mCurrentSimTime + 1, untilSimTime)
        self.mCurrentSimTime = untilSimTime

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

    def addGoldToCount(self, amount):
        self.mCurrentResources.mCurrentGold += amount

    def addLumberToCount(self, amount):
        self.mCurrentResources.mCurrentLumber += amount

    #Sim time only needed for Undead and Elf, to bring their next +10 gold proportionally forward
    def addWorkerToMine(self, simTime):
        if self.mRace == Race.NIGHT_ELF or self.mRace == Race.UNDEAD:
            mineTimeline = self.findMatchingTimeline(TimelineType.GOLD_MINE)

            if mineTimeline.mineIsFull():
                print("Tried to add a worker to mine when it's already full")
                return

            if mineTimeline.mineIsEmpty():
                #Time to mine for 1 worker (diminishes proportionally with number of workers)
                timeToMine = 5 * SECONDS_TO_SIMTIME
                goldMined = 10

                #For first worker, we need to create the +10 gold event that we will use from here on out
                gainGoldEvent = Event(eventFunction = lambda: self.addGoldToCount(goldMined), eventTime=simTime + timeToMine , recurPeriodSimtime = timeToMine, eventName = "Gain 10 gold", 
                                      eventID = self.mEventHandler.getNewEventID())
                self.mEventHandler.registerEvent(gainGoldEvent)
            else:
                gainGoldEvent = self.modifyGainGoldEvent(mineTimeline.getNumWorkersInMine(), mineTimeline.getNumWorkersInMine() + 1, mineTimeline, simTime)

            mineTimeline.addWorkerToMine()

            newWorkerInMineAction = Action(goldCost = 0, lumberCost = 0, foodCost = 0, travelTime = 0, startTime = simTime, duration = 0, 
                               requiredTimelineType = TimelineType.GOLD_MINE, events = [gainGoldEvent], interruptable=False, actionName="New Worker in Mine")
            if not mineTimeline.addAction(newAction = newWorkerInMineAction):
                print("Failed to add new worker action to mine timeline")

    #Sim time only needed for Undead and Elf, to bring their next +10 gold proportionally forward
    def removeWorkerFromMine(self, simTime):
        if self.mRace == Race.NIGHT_ELF or self.mRace == Race.UNDEAD:
            mineTimeline = self.findMatchingTimeline(TimelineType.GOLD_MINE)

            if mineTimeline.mineIsEmpty():
                print("Tried to remove a worker from mine when it's already empty")
                return

            gainGoldEventPair = self.modifyGainGoldEvent(mineTimeline.getNumWorkersInMine(), mineTimeline.getNumWorkersInMine() - 1, mineTimeline, simTime)

            mineTimeline.addWorkerToMine()

            removeWorkerFromMineAction = Action(goldCost = 0, lumberCost = 0, foodCost = 0, travelTime = 0, startTime = simTime, duration = 0, 
                               requiredTimelineType = TimelineType.GOLD_MINE, events = [gainGoldEventPair], interruptable=False, actionName="Remove Worker from Mine")
            if not mineTimeline.addAction(newAction = removeWorkerFromMineAction):
                print("Failed to add new worker action to mine timeline")

    def modifyGainGoldEvent(self, oldNumWorkers, newNumWorkers, mineTimeline, simTime):
        #Already a worker in the mine, and a +10 gold event
        #Next 10 gold gained will be proportionally faster now that we have another worker
        #Will need to bring that event forward
        prevAction = mineTimeline.getPrevAction(simTime)
        #The "New worker in mine" or "Remove worker from mine" action on the mine timeline will be associated with a gain gold event
        gainGoldEvent = prevAction.getAssociatedEvent()

        speedChangeProportion =  oldNumWorkers / newNumWorkers
        #The new time of the +10 gold event will be proportionally sooner
        goldEventNewSimTime = simTime + round((gainGoldEvent.getEventTime() - simTime) * speedChangeProportion)

        #Re-register the event at the new time
        unregisteredEvent = self.mEventHandler.unRegisterEvent(gainGoldEvent.getEventTime(), gainGoldEvent.getEventID())
        unregisteredEvent.mRecurPeriodSimTime = round(unregisteredEvent.mRecurPeriodSimTime * speedChangeProportion)

        if newNumWorkers != 0:
            unregisteredEvent.setEventTime(goldEventNewSimTime)
            self.mEventHandler.registerEvent(unregisteredEvent)
            return unregisteredEvent
        else:
            return None

    def sendWorkerToMine(self, timelineID, simTime, travelTime):
        if self.mRace == Race.NIGHT_ELF or self.mRace == Race.UNDEAD:
            enterMineEvent = Event(eventFunction = lambda: self.addWorkerToMine(simTime + travelTime), eventTime=simTime + travelTime, recurPeriodSimtime = 0, eventName = "Enter mine", eventID = self.mEventHandler.getNewEventID())
            goToMineAction = Action(goldCost = 0, lumberCost = 0, foodCost = 0, travelTime = travelTime, startTime = simTime, duration = 0, 
                               requiredTimelineType = TimelineType.WORKER, events = [enterMineEvent], interruptable=True, actionName="Go to mine")
            if not self.addActionToMatchingTimeline(action = goToMineAction):
                print("Failed to add go to mine action to timeline")

            self.mEventHandler.registerEvent(enterMineEvent)

        elif self.mRace == Race.ORC or self.mRace == Race.HUMAN:
            #TODO:
            newEvents = []
            timeToMine = 5 * SECONDS_TO_SIMTIME
            goldMined = 10
            event = Event(eventFunction = self.addGoldToCount(goldMined), recurPeriodSimtime = timeToMine, eventName = "Return 10 gold")
            self.mEventHandler.registerEvent(eventTime=simTime + timeToMine, event=event)

    def sendWorkerToLumber(self, timelineID, simTime, travelTime):
        if self.mRace == Race.NIGHT_ELF:
            timeToLumb = 8 * SECONDS_TO_SIMTIME
            lumberGained = 5
            gainLumberEvent = Event(eventFunction = lambda: self.addLumberToCount(lumberGained), eventTime=simTime + travelTime + timeToLumb , recurPeriodSimtime = timeToLumb, eventName = "Gain 5 lumber", eventID = self.mEventHandler.getNewEventID())
            goToLumberAction = Action(goldCost = 0, lumberCost = 0, foodCost = 0, travelTime = travelTime, startTime = simTime, duration = 0, 
                               requiredTimelineType = TimelineType.WORKER, events = [(simTime + travelTime + timeToLumb, gainLumberEvent)], interruptable=True, actionName="Go to lumber")
            if not self.addActionToMatchingTimeline(action = goToLumberAction):
                print("Failed to add go to lumber action to timeline")

            self.mEventHandler.registerEvent(gainLumberEvent)

        elif self.mRace == Race.ORC or self.mRace == Race.HUMAN or self.mRace == Race.UNDEAD:
            #TODO:
            pass

    #Return True if successfully added, False otherwise
    #If timeline ID is not passed in, ignore it
    def addActionToMatchingTimeline(self, action, timelineID = -1):
        for timeline in self.mActiveTimelines:
            if action.getRequiredTimelineType() == timeline.getTimelineType() and (timelineID == -1 or timeline.getTimelineID() == timelineID) and timeline.addAction(action):
                return True

        #If none of the active timelines work, try inactive
        i = 0
        while i < len(self.mInactiveTimelines):
            if action.getRequiredTimelineType() == self.mInactiveTimelines[i].getTimelineType() and (timelineID == -1 or self.mInactiveTimelines[i].getTimelineID()) and self.mInactiveTimelines[i].addAction(action):
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
        

    def buildUnit(self, unitType, time):
        #TODO:
        #Check if have enough money
        #Simulate until do
        #Look thorugh active timelines. Track next available time
        #If any available, use it. If not, check inactive
        pass

class CurrentResources:
    def __init__(self, race):
        self.mCurrentGold = 500
        self.mCurrentLumber = 150
        self.mCurrentFood = 5

        if (race == Race.HUMAN):
            self.mCurrentFoodMax = 12
        elif (race == Race.ORC):
            self.mCurrentFoodMax = 11
        elif (race == Race.NIGHT_ELF or race == Race.UNDEAD):
            self.mCurrentFoodMax = 10

    def print(self):
        print("| Gold:", self.mCurrentGold, "| Lumber:", self.mCurrentLumber, "| Food:", str(self.mCurrentFood) + "/" + str(self.mCurrentFoodMax) + " |")