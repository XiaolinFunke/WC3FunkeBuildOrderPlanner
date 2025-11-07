import unittest

import json
import jsonschema
import os
import jsonschema.exceptions
import referencing

class TestJSONValidation(unittest.TestCase):
    #Defines code to be run before test suite is run
    @classmethod
    def setUpClass(cls):
        # Load the schemas to be used with the tests
        with open('SimEngine/Schema/OrderedActionListSchema.json', 'r') as file:
            actionListJsonSchema = json.load(file)

        with open('SimEngine/Schema/SimulatedTimelinesSchema.json', 'r') as file:
            simulatedTimelinesJsonSchema = json.load(file)

        with open('SimEngine/Schema/ActionObjectSchema.json', 'r') as file:
            actionObjSchema = referencing.Resource.from_contents(json.load(file))

        with open('SimEngine/Schema/TimelineObjectSchema.json', 'r') as file:
            timelineObjSchema = referencing.Resource.from_contents(json.load(file))

        registry = referencing.Registry().with_resources(
            [
                ("urn:ActionObject", actionObjSchema),
                ("urn:TimelineObject", timelineObjSchema)
            ]
        )

        cls.actionListValidator = jsonschema.Draft7Validator( actionListJsonSchema, registry = registry )
        cls.simulatedTimelinesValidator = jsonschema.Draft7Validator( simulatedTimelinesJsonSchema, registry = registry )

    #Ensure validating a valid Ordered Action List JSON will not raise an exception
    def testValidOrderedActionList(self):
        with open('Test/TestInput/ValidOrderedActionList.json', 'r') as file:
            jsonActionList = json.load(file)

        self.actionListValidator.validate(jsonActionList)

    #Ensure validating an invalid Ordered Action List JSON will raise a ValidationError exception
    def testInvalidOrderedActionList(self): 
        with open('Test/TestInput/InvalidOrderedActionList.json', 'r') as file:
            jsonActionList = json.load(file)

        with self.assertRaises(jsonschema.exceptions.ValidationError) as raisesVE:
            self.actionListValidator.validate(jsonActionList)

    #Ensure validating a valid Simulated Timelines JSON will not raise an exception
    def testValidSimulatedTimelinesJSON(self):
        with open('Test/TestInput/ValidSimulatedTimelines.json', 'r') as file:
            jsonTimelines = json.load(file)

        self.simulatedTimelinesValidator.validate(jsonTimelines)

    #Ensure validating an invalid Simulated Timelines JSON will raise a ValidationError exception
    def testInvalidSimulatedTimelinesJSON(self):
        with open('Test/TestInput/InvalidSimulatedTimelines.json', 'r') as file:
            jsonTimelines = json.load(file)

        with self.assertRaises(jsonschema.exceptions.ValidationError) as raisesVE: 
            self.simulatedTimelinesValidator.validate(jsonTimelines)

    #Test that the 2AoW hunt build passes validation for both ordered action list and simulated timelines JSON
    def testHuntBuildPassesValidation(self):
        with open('Test/TestInput/HuntBuildSimulationInput.json', 'r') as file:
            actionListJSON = json.load(file)

        self.actionListValidator.validate(actionListJSON)

        with open('Test/TestInput/HuntBuildSimulationOutputTruth.json', 'r') as file:
            timelinesJSON = json.load(file)

        self.simulatedTimelinesValidator.validate(timelinesJSON)
