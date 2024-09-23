from enum import Enum, auto

class Trigger():
    def __init__(self, triggerType, triggerValue = None, actionID = None):
        self.mTriggerType = triggerType
        #Not used for ASAP trigger type
        #Integer for other types, except NEXT_WORKER, for which it's a string designating the worker type
        self.mValue = triggerValue

        #Only used for PERCENT_OF_ONGOING_ACTION trigger type -- specifies the action whose percentage we're looking at
        self.mActionID = actionID

    #Used for deserializing JSON
    @staticmethod
    def getTriggerFromDict(triggerDict):
        triggerType = TriggerType[triggerDict['triggerType']]

        #Use get instead of [] because it will return None if there is no value
        triggerValue = triggerDict.get('value')
        triggerActionID = triggerDict.get('actionID')
        triggerObj = Trigger(triggerType, triggerValue, triggerActionID)

        return triggerObj

    #Get as dict for JSON encoding
    def getAsDictForSerialization(self):
        dict = {
            'triggerType' : self.mTriggerType.name,
        }
        if self.mValue != None:
            dict['value'] = self.mValue
        if self.mActionID != None:
            dict['actionID'] = self.mActionID

        return dict

class TriggerType(Enum):
    ASAP = auto()
    GOLD_AMOUNT = auto()
    LUMBER_AMOUNT = auto()
    FOOD_AMOUNT = auto()
    NEXT_WORKER_BUILT = auto()
    PERCENT_OF_ONGOING_ACTION = auto()