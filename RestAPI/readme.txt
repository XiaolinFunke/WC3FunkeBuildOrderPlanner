#Running the REST API:
To activate the venv that contains flask for running the REST API: (when in the WC3BuildOrderPlanner dir in powershell or cmd)
.\.venv\Scripts\activate
To run the REST API:
cd RestAPI
flask run


#REST API Endpoints:
###/simulation-results/timelines
GET:
Takes a JSON of an ordered action list, simulates from it, and returns a JSON of the timelines

###/saved-builds/<string:buildName>
POST:
Takes a JSON of an ordered action list and saves it using the build name in the URI. Saved builds will be stored in %userprofile%\WC3BuildOrderPlanner\SavedBuilds
GET:
Return the ordered action list JSON from the saved build
PUT:
Update an existing saved build
DELETE:
Delete a saved build

###/saved-builds
GET:
Returns a JSON containing all saved build names