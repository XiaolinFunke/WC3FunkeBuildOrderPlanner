#Class to make handling unique IDs (like Action IDs) easier to handle, since python doesn't have postincrement
class UniqueIDHandler:
    def __init__(self):
        self.id = 0

    def getNextID(self):
        currID = self.id
        self.id += 1
        return currID

    