import json

from SimEngine.SimulationConstants import Race, STARTING_FOOD_MAX_MAP, WorkerTask, TriggerType, TIMELINE_TYPE_GOLD_MINE, isUnitWorker, Worker
from SimEngine.EventHandler import EventHandler, Event
from SimEngine.Timeline import WispTimeline, GoldMineTimeline, Timeline, WorkerTimeline
from SimEngine.Action import ActionType, Action

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
        #All actions that have been executed, in order. If an action in a list of actions we are executing fails, we won't add the rest (so that last one in this list will be the failed one)
        self.mOrderedActionList = []
        self.mActiveTimelines = []
        self.mInactiveTimelines = []
        self.mRace = race
        self.mMapStartingPosition = MapStartingPosition(name = "Ideal_Map_Ideal_Position", lumberTripTravelTimeSec=15, goldTripTravelTimeSec=5) 

        self.mNextTimelineID = 0

        self.mCurrentResources = CurrentResources(race)
        self.mEventHandler = EventHandler()
        self.mCurrentSimTime = 0

        #Give initial starting units
        if self.mRace == Race.NIGHT_ELF:
            goldMineTimeline = GoldMineTimeline(timelineType = TIMELINE_TYPE_GOLD_MINE, timelineID = self.getNextTimelineID(), race = self.mRace, currentResources = self.mCurrentResources, eventHandler=self.mEventHandler)
            self.mInactiveTimelines.append(goldMineTimeline)
            for i in range(5):
                self.mInactiveTimelines.append(WispTimeline(timelineID = self.getNextTimelineID(), eventHandler=self.mEventHandler))
            self.mInactiveTimelines.append(Timeline(timelineType = "Tree of Life", timelineID = self.getNextTimelineID(), eventHandler = self.mEventHandler))
            #TODO: Adding these always for now, but later can have them only on some maps
            self.mInactiveTimelines.append(Timeline(timelineType = "Tavern", timelineID = self.getNextTimelineID(), eventHandler = self.mEventHandler))
            self.mInactiveTimelines.append(Timeline(timelineType = "Goblin Merchant", timelineID = self.getNextTimelineID(), eventHandler = self.mEventHandler))

    def simulateOrderedActionList(self, orderedActionList):
        for action in orderedActionList:
            if not self.simulateAction(action):
                print("Failed to simulate action in action order list. Stopping")
                return False
        
        return True

    def simulateAction(self, action):
        self.mOrderedActionList.append(action)
        if action.getTrigger().mTriggerType == TriggerType.GOLD_AMOUNT:
            if not self._simulateUntilResourcesAvailable( action.getTrigger().mValue, 0, 0 ):
                print("Tried to simulate until", action.getTrigger().mValue, "gold was available, but we would never reach that amount")
                return False
        elif action.getTrigger().mTriggerType == TriggerType.LUMBER_AMOUNT:
            if not self._simulateUntilResourcesAvailable( 0, action.getTrigger().mValue, 0 ):
                print("Tried to simulate until", action.getTrigger().mValue, "lumber was available, but we would never reach that amount")
                return False
        elif action.getTrigger().mTriggerType == TriggerType.FOOD_AMOUNT:
            if not self._simulateUntilResourcesAvailable( 0, 0, action.getTrigger().mValue ):
                print("Tried to simulate until", action.getTrigger().mValue, "food was available, but we would never reach that amount")
                return False
        elif action.getTrigger().mTriggerType == TriggerType.PERCENT_OF_ONGOING_ACTION:
            #TODO:
            pass
        elif action.getTrigger().mTriggerType == TriggerType.NEXT_WORKER_BUILT:
            #This will simulate until the next worker is built
            self._getNextBuiltWorkerTimelineID(action.getTrigger().mValue)

        if action.getActionType() == ActionType.BuildUnit or action.getActionType() == ActionType.BuildUpgrade or action.getActionType() == ActionType.Shop:
            success = self._executeAction(action)
        elif action.getActionType() == ActionType.BuildStructure:
            success = self._buildStructure(action)
        elif action.getActionType() == ActionType.WorkerMovement:
            success = self._moveWorker(action)

        self._moveTimelinesToActiveList()
        return success

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

    def getCurrentSimTime(self):
        return self.mCurrentSimTime

    def getEventHandler(self):
        return self.mEventHandler
                
    def getCurrentResources(self):
        return self.mCurrentResources

    def addLumberToCount(self, amount):
        self.mCurrentResources.mCurrentLumber += amount

    def _getWorkerTimelineForAction(self, action):
        if action.mWorkerTimelineID:
            workerTimeline = self._findMatchingTimeline(action.mRequiredTimelineType, action.mWorkerTimelineID)
        elif action.mCurrentWorkerTask == WorkerTask.IDLE:
            workerTimeline = self._getIdleWorker(action.mRequiredTimelineType)
        elif action.mCurrentWorkerTask == WorkerTask.GOLD or action.mCurrentWorkerTask == WorkerTask.LUMBER:
            workerTimeline = self._getMostIdleWorkerOnResource(action.mRequiredTimelineType, action.mCurrentWorkerTask == WorkerTask.GOLD)
        elif action.mCurrentWorkerTask == WorkerTask.IN_PRODUCTION:
            #We already simulated ahead, to when the worker is made, so now we must get that worker
            workerTimeline = self._getLastBuiltWorkerTimeline(action.mRequiredTimelineType)

        return workerTimeline

    def _moveWorker(self, action):
        workerTimeline = self._getWorkerTimelineForAction(action)

        if not workerTimeline:
            print("Could not get valid worker for moveWorker action!")

        goldMineTimeline = self._findMatchingTimeline(TIMELINE_TYPE_GOLD_MINE)
        action.setStartTime(self.mCurrentSimTime)
        if action.mDesiredWorkerTask == WorkerTask.LUMBER:
            #TODO: A little bit odd that we need to pass the goldmine here (it's because we might be moving a worker OFF of gold. But if we store it on the timeline, then we need to pass the goldmine to buildUnit just in case the unit is a wisp)
            success = workerTimeline.sendWorkerToLumber(action, goldMineTimeline, self.mCurrentSimTime, self.mCurrentResources)
        elif action.mDesiredWorkerTask == WorkerTask.GOLD:
            success = workerTimeline.sendWorkerToMine(action, goldMineTimeline, self.mCurrentSimTime)

        #After each action, simulate the current time again, in case new events have been added that should be executed before the next command comes in
        self.simulate(self.mCurrentSimTime)
        return success

    #Will return the first matching timeline (active first)
    #If timeline ID is not passed in, ignore it
    def _findMatchingTimeline(self, timelineType, timelineID = -1):
        for timeline in self.mActiveTimelines:
            if timelineType == timeline.getTimelineType() and (timelineID == -1 or timeline.getTimelineID() == timelineID):
                return timeline

        #If none of the active timelines work, try inactive
        for timeline in self.mInactiveTimelines:
            if timelineType == timeline.getTimelineType() and (timelineID == -1 or timeline.getTimelineID() == timelineID):
                return timeline

    def _findAllWorkerTimelines(self):
        matchingTimelines = []
        for workerType in Worker:
            matchingTimelines.extend(self.findAllMatchingTimelines(workerType.name))

        return matchingTimelines

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

    #Get this build order's race and ordered action list as dicts to easily serialize to JSON
    def getRaceAndActionListAsDictForSerialization(self):
        dict = { 
            'race' : self.mRace.name,
            'orderedActionList' : []
        }
        for action in self.mOrderedActionList:
            dict['orderedActionList'].append(action.getAsDictForSerialization(False))

        return dict

    #Get this build order's current simtime and timelines as dicts to easily serialize to JSON
    def getSimTimeAndTimelinesAsDictForSerialization(self):
        dict = { 
            'currentSimTime' : self.mCurrentSimTime,
            'activeTimelines' : [],
            'inactiveTimelines' : [],
            'currentResources' : self.mCurrentResources.getAsDictForSerialization()
        }
        for timeline in self.mActiveTimelines:
            dict['activeTimelines'].append(timeline.getAsDictForSerialization())
        for timeline in self.mInactiveTimelines:
            dict['inactiveTimelines'].append(timeline.getAsDictForSerialization())

        return dict

    #Used to deserialize JSON (after converting the JSON to dict)
    #Returns the build order object after simulating the specified ordered action list
    @staticmethod
    def simulateBuildOrderFromDict(buildOrderDict):
        buildOrder = BuildOrder(Race[buildOrderDict['race']])

        orderedActionList = []
        for actionDict in buildOrderDict['orderedActionList']:
            orderedActionList.append( Action.getActionFromDict(actionDict) )

        buildOrder.simulateOrderedActionList(orderedActionList)

        return buildOrder

    #Return True if action executed successfully, False if didn't execute or failed to execute
    def _executeAction(self, action):
        #Get lumber + food cost if they exist and aren't None, else default them to 0
        if not self._simulateUntilResourcesAvailable( goldRequired=action.mGoldCost, lumberRequired=action.mLumberCost if action.mLumberCost != None else 0, foodRequired=getattr(action, 'mFoodCost', 0) ):
            print("Tried to simulate until resources were available for", action, "but we would never reach that amount")
            return False

        self._simulateUntilTimelineExists(action.getRequiredTimelineType())

        matchingTimelines = self.findAllMatchingTimelines(action.mRequiredTimelineType)
        if not matchingTimelines:
            print("Tried to execute action", action.__class__.__name__ + " - " + action.mName + ", but did not find a timeline of type ", action.mRequiredTimelineType)
            return False

        minAvailableTime = float('inf')
        for timeline in matchingTimelines:
            prevMinAvailableTime = minAvailableTime
            minAvailableTime = min(minAvailableTime, timeline.getNextPossibleTimeForAction(self.mCurrentSimTime))
            if minAvailableTime != prevMinAvailableTime:
                nextAvailableTimeline = timeline

        #TODO: This doesn't account for the fact that there could be a new timeline that would have an earlier time available
        self.simulate(minAvailableTime)

        action.setStartTime(self.mCurrentSimTime)

        if action.mDontExecute == True:
            return False 

        if isUnitWorker(action.mName):
            events = [ Event(lambda: self.mInactiveTimelines.append(WorkerTimeline.getNewWorkerTimeline(action.mName, self.getNextTimelineID(), self.mEventHandler)), action.getStartTime() + action.mDuration, 
                                            0, self.mEventHandler.getNewEventID(), "Worker " + action.mName + " produced") ]
            self.mEventHandler.registerEvents(events)

        if not nextAvailableTimeline.addAction(action, self.mCurrentResources):
            print("Failed to execute action", action.__class__.__name__ + " - " + action.mName)
            return False

        #After each action, simulate the current time again, in case new events have been added that should be executed before the next command comes in
        self.simulate(self.mCurrentSimTime)
        return True

    #@return False if we will never have enough resources. True otherwise
    def _simulateUntilResourcesAvailable(self, goldRequired, lumberRequired, foodRequired):
        #TODO: If we eventually have a way for workers to be queued to gold/lumber after they're done building something, that will mess up this logic (we will think we will never mine more gold cause none are on it, but one is queued to gold, for example)
        while True:
            if self.mCurrentResources.getCurrentGold() < goldRequired:
                if self._getNumWorkersOnTask(WorkerTask.GOLD) == 0:
                    return False
            elif self.mCurrentResources.getCurrentLumber() < lumberRequired:
                if self._getNumWorkersOnTask(WorkerTask.LUMBER) == 0:
                    return False
            elif max(self.mCurrentResources.mCurrentFoodMax - self.mCurrentResources.mCurrentFood, 0) < foodRequired:
                if self._getNumWorkersOnTask(WorkerTask.CONSTRUCTING) == 0:
                    return False
            else:
                return True
            self.simulate(self.mCurrentSimTime + 1)

    #@param workerTask - Task to return the number of workers for
    def _getNumWorkersOnTask(self, workerTask):
        numWorkers = 0
        for workerTimeline in self._findAllWorkerTimelines():
            if workerTimeline.mCurrentTask == workerTask:
                numWorkers += 1
        return numWorkers

    def _simulateUntilTimelineExists(self, timelineType):
        #TODO: Have a check to make sure this will eventually be true so we don't simulate into infinity
        while self._findMatchingTimeline(timelineType) == None:
            self.simulate(self.mCurrentSimTime + 1)

    #Commented out -- will rely on front-end for hero handling unless we eventually want to double-check it here
    # def _buildHero(self, action):
    #     #TODO: Enforce not building same hero twice as well
    #     #Can't build any more heroes after the third one
    #     if self.mHeroesBuilt >= 3:
    #         return False

    #     if self.mHeroesBuilt == 0:
    #         #First hero doesn't cost gold or lumber
    #         action.setCostToFree()

    #     if self._doBuildUnit(action):
    #         self.mHeroesBuilt += 1
    #         return True
    #     else:
    #         return False

    #Return True if executed the action successfully, False if didn't execute or failed to execute
    #Will be built with the most idle worker currently doing the workerTask passed in
    def _buildStructure(self, action):
        if not self._simulateUntilResourcesAvailable(goldRequired=action.mGoldCost, lumberRequired=action.mLumberCost, foodRequired=0):
            print("Tried to simulate until resources were available for", action, "but they never were")
            return False

        if action.mCurrentWorkerTask == WorkerTask.IDLE:
            workerTimeline = self._getIdleWorker(action.mRequiredTimelineType)
        elif action.mCurrentWorkerTask == WorkerTask.GOLD or action.mCurrentWorkerTask == WorkerTask.LUMBER:
            workerTimeline = self._getMostIdleWorkerOnResource(action.mRequiredTimelineType, action.mCurrentWorkerTask == WorkerTask.GOLD)
        elif action.mCurrentWorkerTask == WorkerTask.IN_PRODUCTION:
            #We should have already simulated up until the worker was built, since the Trigger Type would be NEXT_WORKER_BUILT
            workerTimeline = self._getLastBuiltWorkerTimeline(action.mRequiredTimelineType)
        
        goldMineTimeline = self._findMatchingTimeline(TIMELINE_TYPE_GOLD_MINE)
        action.setStartTime(self.mCurrentSimTime)
        if action.mDontExecute == True:
            return False
        elif not workerTimeline.buildStructure(action, self.mInactiveTimelines, self.getNextTimelineID, self.mCurrentResources, goldMineTimeline):
            print("Failed to build", action.mName)
            return False

        #After each action, simulate the current time again, in case new events have been added that should be executed before the next command comes in
        self.simulate(self.mCurrentSimTime)
        return True

    def _getIdleWorker(self, workerType):
        if not isUnitWorker(workerType):
            print("Tried to get an idle worker, but worker type of", workerType, " is not the type of a worker!")
            return None

        workerTimelines = self.findAllMatchingTimelines(workerType)

        idleWorkerTimelines = []
        for timeline in workerTimelines:
            if timeline.getCurrentTask() == WorkerTask.IDLE:
                idleWorkerTimelines.append(timeline)

        if len(idleWorkerTimelines) > 0:
            return idleWorkerTimelines[0]
        else:
            return None
    
    #Get the timeline of the 'most idle' worker on a given resource
    #@param onGold - True if the worker should be taken from gold. If false, from lumber
    def _getMostIdleWorkerOnResource(self, workerType, onGold):
        if not isUnitWorker(workerType):
            print("Tried to get most idle worker on resource, but worker type of", workerType, " is not the type of a worker!")
            return None

        workerTimelines = self.findAllMatchingTimelines(workerType)

        correctTaskWorkerTimelines = []
        correctTask = WorkerTask.GOLD if onGold else WorkerTask.LUMBER

        for timeline in workerTimelines:
            if timeline.getCurrentTask() == correctTask:
                correctTaskWorkerTimelines.append(timeline)

        if len(correctTaskWorkerTimelines) == 0:
            return None

        #TODO: Determine the idleness of the workers
        #For now, just return the first one
        return correctTaskWorkerTimelines[0]

    #Return the timeline of the most recently built worker
    def _getLastBuiltWorkerTimeline(self, workerType):
        if not isUnitWorker(workerType):
            print("Tried to get last built worker timeline, but worker type of", workerType, " is not the type of a worker!")
            return None

        #TODO: Handle possible edge-case if we build multiple workers at the same time
        #Return the timeline with the highest timeline ID, since that means it's newest
        highestTimelineID = float('-inf')
        for timeline in self.findAllMatchingTimelines(workerType):
            if timeline.getTimelineID() > highestTimelineID:
                highestTimelineID = timeline.getTimelineID()
                newestTimeline = timeline

        return newestTimeline

    #Simulates until the next worker will be built and returns its timeline ID
    def _getNextBuiltWorkerTimelineID(self, workerType): 
        if not isUnitWorker(workerType):
            print("Tried to get next built worker timeline, but worker type of", workerType, " is not the type of a worker!")
            return None

        #TODO: This function could be optimized if it's a performance issue
        initialNumWorkerTimelines = len(self.findAllMatchingTimelines(workerType))

        #TODO: Have some way to ensure a worker is being built, so that we know we won't simulate forever here
        while True:
            self.simulate(self.mCurrentSimTime + 1)   
            workerTimelines = self.findAllMatchingTimelines(workerType)
            #Number of worker timelines has changed. This means a worker was built
            if initialNumWorkerTimelines != len(workerTimelines):
                break

        #TODO: Handle possible edge-case if we build multiple workers at the same time
        #Return the timeline with the highest timeline ID, since that means it's newest
        highestTimelineID = float('-inf')
        for timeline in self.findAllMatchingTimelines(workerType):
            highestTimelineID = max(highestTimelineID, timeline.getTimelineID())
            #TODO: Could just track the timeline of the highest here as well and return that instead of the ID - worker movement 
            #functions could call this automatically instead of needing to call this from outside

        return highestTimelineID

    #Checks inactive timelines and determines if any should be moved to the active list
    def _moveTimelinesToActiveList(self):
        #TODO: This could be more performant, if performance is an issue
        i = 0
        while i < len(self.mInactiveTimelines):
            for action in self.mInactiveTimelines[i].mActions:
                if not action.mIsInvisibleToUser:
                    #Timeline should be active now, since it has a visible Action on it
                    self.mActiveTimelines.append(self.mInactiveTimelines.pop(i))
                    #Don't increment i, since we just removed an element from the list
                    break
            else:
                i += 1

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

    def getAsDictForSerialization(self):
        dict = {
            'currentGold' : self.mCurrentGold,
            'currentLumber' : self.mCurrentLumber,
            'currentFood' : self.mCurrentFood,
            'currentFoodMax' : self.mCurrentFoodMax
        }

        return dict

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

    def __str__(self):
        return "| Gold:" + str(self.mCurrentGold) + " | Lumber:" + str(self.mCurrentLumber) + " | Food:" + str(self.mCurrentFood) + "/" + str(self.mCurrentFoodMax) + " |"

    def __repr__(self):
        return self.__str__()