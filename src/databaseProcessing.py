from pandas import DataFrame, Series, json_normalize, read_json
import json
from os.path import isfile

class databaseProcessor:
    def __init__(self, nltkProcessor):
        self.nltkProcessor = nltkProcessor

        self.fileDf = DataFrame({
                "FileName": [],
                "FileDir": [],
                "Text": [],
                "ComparisonResults": [] 
            })

    def getSize(self):
        return self.fileDf.shape[0]

    def writeJson(self, directory):
        self.fileDf.to_json(directory, indent=2)

    def readJson(self, directory):
        if isfile(directory):
            jsonFileContent = open(directory).read()
            if jsonFileContent != "":
                self.fileDf = read_json(jsonFileContent)

    def getAllFiles(self):
        print(self.fileDf)
        print("-------------------------")
        files = self.fileDf[["FileName", "FileDir", "Text", "ComparisonResults"]].values.tolist()
        return files