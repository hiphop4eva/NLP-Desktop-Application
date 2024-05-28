import mysql.connector
from pandas import DataFrame, Series, json_normalize, read_json
import json
from os.path import isfile

class databaseProcessor:
    def __init__(self, nltkProcessor):
        self.nltkProcessor = nltkProcessor

        self.jsonDir = "files/files.json"
        self.fileDf = DataFrame({
                "FileName": [],
                "FileDir": [],
                "Text": [],
                "ComparisonResults": [] 
            })
    
    def getSize(self):
        return self.fileDf.shape[0]

    def writeJson(self):
        self.fileDf.to_json(self.jsonDir, indent=2)

    def readJson(self):
        if isfile(self.jsonDir):
            jsonFileContent = open(self.jsonDir).read()
            if jsonFileContent != "":
                self.fileDf = read_json(jsonFileContent)

    def getAllFiles(self):
        print(self.fileDf)
        print("-------------------------")
        files = self.fileDf[["FileName", "FileDir", "Text", "ComparisonResults"]].values.tolist()
        return files