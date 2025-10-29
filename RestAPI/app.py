from flask import Flask, request
import os
import pathlib
from SimEngine.SimulationEngine import SimulationEngine
import json

SAVED_BUILD_STORAGE_DIR = os.path.join(pathlib.Path.home(), "WC3BuildOrderPlanner/SavedBuilds")

app = Flask(__name__)

def createSavedBuildsDir():
    pathlib.Path(SAVED_BUILD_STORAGE_DIR).mkdir(parents=True, exist_ok=True)

#Given an ordered action list as a JSON, simulate and return the timelines
@app.route("/simulation-results/timelines", methods=['GET'])
def get_timelines():
    orderedActionList = request.get_json()
    simEngine = SimulationEngine() 
    try:
        simEngine.loadStateFromActionListsJSON(orderedActionList)
    except KeyError as keyError:
        #Code 400, Bad Request
        return ("KeyError: " + str(keyError), 400)
    except Exception as e:
        return ("Exception: " + str(e), 400)

    #Code 200, OK
    return (simEngine.getJSONStateAsTimelines(), 200)

#Get all saved build names as a JSON
@app.route("/saved-builds", methods=['GET'])
def get_builds():
    createSavedBuildsDir()
    builds = os.listdir(SAVED_BUILD_STORAGE_DIR)
    #Code 200, OK
    return (json.dumps(builds), 200)

#Save a build (CREATE)
@app.route("/saved-builds/<string:name>", methods=['POST'])
def create_build(name):
    createSavedBuildsDir()
    orderedActionList = request.get_json()
    filePath = os.path.join(SAVED_BUILD_STORAGE_DIR, name)

    if not os.path.exists(filePath):
        with open(filePath, "w") as f:
            f.write(orderedActionList)
    else:
        #Code 409, Conflict
        return ("", 409)

    #Code 201, Created
    return ("", 201)

#Load a saved build (READ)
@app.route("/saved-builds/<string:name>", methods=['GET'])
def get_build(name):
    createSavedBuildsDir()
    filePath = os.path.join(SAVED_BUILD_STORAGE_DIR, name)

    fileAsStr = ""
    if os.path.exists(filePath):
        with open(filePath, "r") as f:
            fileAsStr = f.read()
    else:
        #404, Not Found
        return ("", 404)

    #Code 200, OK
    return (fileAsStr, 200)

#Update an existing build (UPDATE)
@app.route("/saved-builds/<string:name>", methods=['PUT'])
def update_build(name):
    createSavedBuildsDir()
    orderedActionList = request.get_json()
    filePath = os.path.join(SAVED_BUILD_STORAGE_DIR, name)

    if os.path.exists(filePath):
        with open(filePath, "w") as f:
            f.write(orderedActionList)
    else:
        return ("", 404)

    #Code 204, No Content
    return ("", 204)

#Delete a saved build (DELETE)
@app.route("/saved-builds/<string:name>", methods=['DELETE'])
def delete_build(name):
    createSavedBuildsDir()
    filePath = os.path.join(SAVED_BUILD_STORAGE_DIR, name)

    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        return ("", 404)

    #Code 204, no content
    return ("", 204)