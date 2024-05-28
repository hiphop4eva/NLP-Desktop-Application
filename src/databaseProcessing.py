import mysql.connector
password = open("password/password.txt").read()

database = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="NLP"
)

debugCursor = database.cursor()
debugCursor.execute("CREATE DATABASE IF NOT EXISTS NLP")
#debugCursor.execute("DROP TABLE files")
debugCursor.execute("CREATE TABLE IF NOT EXISTS files (id INT AUTO_INCREMENT PRIMARY KEY, fileName VARCHAR(255), fileDir VARCHAR(255))")
debugCursor.execute("ALTER TABLE files AUTO_INCREMENT = 0")

class databaseProcessor:
    def __init__(self, nltkProcessor):
        self.nltkProcessor = nltkProcessor
        self.cursor = database.cursor()

    def insertFile(self, fileName, fileDir, id = ""):
        self.cursor.execute("SELECT fileName FROM files")
        fileNames = self.cursor.fetchall()

        for name in fileNames:
            if name[0] == fileName:
                return

        if id == "":
            self.cursor.execute("INSERT INTO files (fileName, fileDir) VALUES (%s, %s)", (fileName, fileDir))
        else:
            self.cursor.execute("INSERT INTO files (id, fileName, fileDir) VALUES (%s, %s, %s)", (id, fileName, fileDir))
        database.commit()

    def updateFile(self, id, fileName, fileDir):
        self.cursor.execute("UPDATE files SET fileName = %s, fileDir = %s WHERE id = %s", (fileName, fileDir, id))
        database.commit()

    def updateFileName(self, id, fileName):
        self.cursor.execute("UPDATE files SET fileName = %s WHERE id = %s", (fileName, id))
        database.commit()

    def updateFileDirectory(self, id, fileDir):
        self.cursor.execute("UPDATE files SET fileDir = %s WHERE id = %s", (fileDir, id))
        database.commit()

    def updateFileId(self, oldId, newId):
        self.cursor.execute("UPDATE files SET id = %s WHERE id = %s", (newId, oldId))
        database.commit()

    def getFile(self, id):
        self.cursor.execute("SELECT * FROM files WHERE id = %s", (id,))
        return self.cursor
    
    def getAllFiles(self):
        self.cursor.execute("SELECT * FROM files")
        return self.cursor
    
    def getSize(self):
        self.cursor.execute("SELECT COUNT(*) FROM files")
        return self.cursor.fetchone()[0]
    
    def deleteFile(self, id):
        self.cursor.execute("DELETE FROM files WHERE id = %s", (id,))
        database.commit()
    
    def getLargestId(self):
        self.cursor.execute("SELECT MAX(id) FROM files")
        return self.cursor.fetchone()[0]

    def rearrangeFileIds(self, index):
        size = self.getSize()
        largestRow = 1
        if size != 0:
            largestRow = self.getLargestId()

            for i in range(1, largestRow + 1):
                if i > index:
                    self.updateFileId(i, i - 1)

        self.cursor.execute(f"ALTER TABLE files AUTO_INCREMENT = {largestRow}")

debugCursor.execute("SHOW DATABASES")

for db in debugCursor:
    print(db)
print("-------------------------")

debugCursor.execute("SHOW TABLES")

for tb in debugCursor:
    print(tb)

print("-------------------------")

debugCursor.execute("DESCRIBE files")

for col in debugCursor:
    print(col)
print("-------------------------")

debugCursor.execute("SELECT id, fileName, fileDir FROM files")

for row in debugCursor:
    print(row)

print("-------------------------")

