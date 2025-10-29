import unittest
import os, glob
import json

from RestAPI.app import app, SAVED_BUILD_STORAGE_DIR

#Prefix used for files that should be cleaned up after the current test
UNIT_TEST_TMP_FILE_PREFIX = "unit_test_tmp_"
#Prefix used for files that should be cleaned up only after the full suite is run
SUITE_TMP_FILE_PREFIX = "suite_" + UNIT_TEST_TMP_FILE_PREFIX

#Filename of the valid save that will be present for the entire suite, for use with tests
VALID_SAVE_NAME = SUITE_TMP_FILE_PREFIX + "ValidSave.json"

class TestRESTEndpoints(unittest.TestCase):
    #Defines code to be run before test suite is run
    @classmethod
    def setUpClass(cls):
        # Set up a valid saved file for use with tests
        with open('Test/TestInput/ValidOrderedActionList.json', 'r') as file:
            fileData = file.read()
        with open(os.path.join(SAVED_BUILD_STORAGE_DIR, VALID_SAVE_NAME), 'w') as file:
            file.write(fileData)

        cls.ctx = app.app_context()
        cls.ctx.push()
        cls.client = app.test_client()

    #Defines code to be run after test suite is run
    @classmethod
    def tearDownClass(cls):
        cls.ctx.pop()

        #Delete any temp files created by the test suite
        for filename in glob.glob(os.path.join(SAVED_BUILD_STORAGE_DIR, SUITE_TMP_FILE_PREFIX + "*")):
            os.remove(filename)

    #TODO: We could probably refactor a lot of the unit tests in other files to use setUp and tearDown
    #Defines code to be run before each test
    def setUp(self):
        pass

    #Defines code to be run after each test
    def tearDown(self):
        #Delete any temp files created by the unit test
        for filename in glob.glob(os.path.join(SAVED_BUILD_STORAGE_DIR, UNIT_TEST_TMP_FILE_PREFIX + "*")):
            os.remove(filename)

    #Get timelines simulated from an ordered action list
    def testGetSimulatedTimelines(self):
        with open('Test/TestInput/HuntBuildSimulationInput.json', 'r') as file:
            actionListData = file.read()
        response = self.client.get("/simulation-results/timelines", json=actionListData)
        self.assertEqual(response.status_code, 200)

        #Timeline JSON data should match what we have on file
        with open('Test/TestInput/HuntBuildSimulationOutputTruth.json', 'r') as file:
            timelineData = file.read()
        self.assertEqual(response.get_data(as_text=True), timelineData)

    #Test that we get an error if trying to simulate from an invalid JSON
    def testSimulateErrorIfInvalidJSON(self):
        with open('Test/TestInput/InvalidOrderedActionList.json', 'r') as file:
            fileData = file.read()
        response = self.client.get("/simulation-results/timelines", json=fileData)
        self.assertEqual(response.status_code, 400)
        #It should also provide some sort of error text
        self.assertNotEqual(response.get_data(as_text=True), "")

    #Get the name of all saved builds as a JSON
    def testGetSavedBuilds(self):
        response = self.client.get("/saved-builds")
        self.assertEqual(response.status_code, 200)

        jsonBuilds = json.loads(response.get_data(as_text=True))

        #This should be the only saved build that persists across tests
        for build in jsonBuilds:
            self.assertEqual(build, VALID_SAVE_NAME )

    #Create a saved build, given an ordered action list
    def testSaveBuild(self):
        with open('Test/TestInput/ValidOrderedActionList.json', 'r') as file:
            origFileData = file.read()
        filename = UNIT_TEST_TMP_FILE_PREFIX + "save.json"
        response = self.client.post("/saved-builds/" + filename, json=origFileData)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_data(as_text=True), "")

        with open(os.path.join(SAVED_BUILD_STORAGE_DIR, filename), 'r') as file:
            newfiledata = file.read()
        self.assertEqual(origFileData, newfiledata)

    #Test that creating a saved build errors if it already exists
    def testSaveBuildErrorsIfAlreadyExist(self):
        response = self.client.post("/saved-builds/" + VALID_SAVE_NAME, json="")
        # Code 409, Conflict
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_data(as_text=True), "")

    #Test loading a saved build
    def testLoadSavedBuild(self):
        with open(os.path.join(SAVED_BUILD_STORAGE_DIR, VALID_SAVE_NAME), 'r') as file:
            fileData = file.read()

        response = self.client.get("/saved-builds/" + VALID_SAVE_NAME)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), fileData)

    #Test that we get an error if loading a saved build that doesn't exist
    def testErrorIfLoadNonExistentSavedBuild(self):
        response = self.client.get("/saved-builds/" + SUITE_TMP_FILE_PREFIX + "nonexistent-build.json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_data(as_text=True), "")

    #Test updating an existing saved build
    def testUpdatingSavedBuild(self):
        with open(os.path.join(SAVED_BUILD_STORAGE_DIR, VALID_SAVE_NAME), 'r') as file:
            origFileData = file.read()

        response = self.client.put("/saved-builds/" + VALID_SAVE_NAME, json="[]")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(as_text=True), "")

        with open(os.path.join(SAVED_BUILD_STORAGE_DIR, VALID_SAVE_NAME), 'r') as file:
            newFileData = file.read()

        self.assertEqual(newFileData, "[]")

        #Update back to how it was
        response = self.client.put("/saved-builds/" + VALID_SAVE_NAME, json=origFileData)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(as_text=True), "")

        with open(os.path.join(SAVED_BUILD_STORAGE_DIR, VALID_SAVE_NAME), 'r') as file:
            newFileData2 = file.read()

        self.assertEqual(newFileData2, origFileData)

    #Test that we get an error if updating a saved build that doesn't exist
    def testErrorUpdatingNonExistentSavedBuild(self):
        response = self.client.put("/saved-builds/" + SUITE_TMP_FILE_PREFIX + "nonexistent-build.json", json="[]")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_data(as_text=True), "")

    #Test deleting a saved build
    def testDeletingSavedBuild(self):
        #Create a file to then delete
        fileName = UNIT_TEST_TMP_FILE_PREFIX + "BuildToDelete.json"
        filePath = os.path.join(SAVED_BUILD_STORAGE_DIR, fileName)
        with open(filePath, 'w') as file:
            file.write("[]")

        self.assertTrue(os.path.exists(filePath))

        response = self.client.delete("/saved-builds/" + fileName)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(as_text=True), "")

        self.assertFalse(os.path.exists(filePath))

    #Test that we get an error if we attempt to delete a saved build that doesn't exist
    def testErrorDeletingNonExistentSavedBuild(self):
        response = self.client.delete("/saved-builds/" + SUITE_TMP_FILE_PREFIX + "nonexistent-build.json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_data(as_text=True), "")