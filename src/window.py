import sys
import pypdf
import docx
import numpy as np

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from pyqtgraph import PlotWidget, plot, mkPen
from pyqtgraph.graphicsItems.ViewBox.ViewBox import ViewBox

app = QApplication(sys.argv)

iconDict = {}
iconCacheDict = {}

for i in ["text", "pdf", "docx", "c", "cpp", "cs", "py", "misc"]:
    icon = QIcon()
    icon.addFile(f"src/resources/images/{i}Icon.png")
    iconKey = icon.cacheKey()
    iconDict[f"{i}Icon"] = f"src/resources/images/{i}Icon.png"
    iconCacheDict[iconKey] = f"src/resources/images/{i}Icon.png"

class MainWindow(QDialog):
    def __init__(self, nltkProcessor, databaseProcessor):
        super().__init__()

        self.nltkProcessor = nltkProcessor
        self.databaseProcessor = databaseProcessor

        self.fileDict = {}

        self.setWindowTitle("NLP Application")
        icon = QIcon()
        icon.addFile("src/resources/images/bocchiIcon.png")
        self.setWindowIcon(icon)
        self.setGeometry(100, 100, 1000, 600)
        self.fileProcessor = FileProcessor(self)
        self.mainLayout = MainLayout(self)
        self.setLayout(self.mainLayout)

        self.show()

        self.initFiles()

    def initFiles(self):
        files = self.databaseProcessor.getAllFiles()
        nltkProcessor = self.nltkProcessor
        fileBoxLayout = self.mainLayout.actionsLayout.fileBoxLayout
        comparisonLayout = self.mainLayout.actionsLayout.comparisonLayout

        for row in files:
            indexOriginal = row[0] - 1
            name = row[1]
            fileDir = row[2]
            text, textInfo, icon, iconType = self.fileProcessor.readFile(fileDir)
            file = self.fileProcessor.initFile(name, fileDir, icon, text, textInfo)

            self.actionsLayout.addFile(file, setChecked = False)
            self.fileDict[indexOriginal] = file
            self.fileDict[name] = file

        comparisonLayout.hide()

    def rearrangeFileIds(self, index):
        indexDatabase = index + 1
        fileDict = self.fileDict
        length = int(len(fileDict)/2) + 1

        for i in range(0, length):
            if i > index:
                file = fileDict[i]
                fileDict.pop(i)
                fileDict[i - 1] = file

        self.databaseProcessor.rearrangeFileIds(indexDatabase)
        self.actionsLayout.rearrangeFileIds(index)

class MainLayout(QGridLayout):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        mainWindow.mainLayout = self

        self.textMainLayout = TextMainLayout(self.mainWindow)
        self.actionsLayout = ActionsLayout(self.mainWindow)
        self.addLayout(self.actionsLayout, 0, 0, 1, 1)
        self.addLayout(self.textMainLayout, 0, 1, 1, 3)

class ActionsLayout(QVBoxLayout):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        mainWindow.actionsLayout = self
        self.fileTextLayout = self.mainWindow.fileTextLayout

        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setSpacing(0)
        self.addLayout(self.buttonsLayout)
        self.lowerLayout = QVBoxLayout()
        self.addLayout(self.lowerLayout)
        
        self.buttonFiles = QPushButton()
        font = self.buttonFiles.font()
        font.setBold(True)
        self.buttonFiles.setFont(font)
        self.buttonFiles.setText("Files")
        self.buttonsLayout.addWidget(self.buttonFiles)
        
        self.buttonComparison = QPushButton()
        font = self.buttonComparison.font()
        font.setBold(True)
        self.buttonComparison.setFont(font)
        self.buttonComparison.setText("Comparison")
        self.buttonsLayout.addWidget(self.buttonComparison)

        self.buttonInfo = QPushButton()
        font = self.buttonInfo.font()
        font.setBold(True)
        self.buttonInfo.setFont(font)
        self.buttonInfo.setText("Information")
        self.buttonsLayout.addWidget(self.buttonInfo)

        self.fileBoxLayout = FileBoxLayout(self.mainWindow)
        self.comparisonLayout = ComparisonLayout(self.mainWindow)
        self.informationFileLayout = InformationFileLayout(self.mainWindow)
        self.lowerLayout.addLayout(self.fileBoxLayout)

        self.comparisonLayout.hide()

        self.buttonFiles.clicked.connect(self.buttonFilesPressed)
        self.buttonComparison.clicked.connect(self.buttonComparisonPressed)
        self.buttonInfo.clicked.connect(self.buttonInfoPressed)

    def addFile(self, file, setChecked=True):
        self.fileBoxLayout.addFile(file, setChecked)
        self.comparisonLayout.addFile(file)
        self.informationFileLayout.addFile(file)

    def deleteFile(self, file):
        self.fileBoxLayout.deleteFile(file)
        self.comparisonLayout.deleteFile(file)
        self.informationFileLayout.deleteFile(file)

    def rearrangeFileIds(self, index):
        self.fileBoxLayout.rearrangeFileIds(index)
        self.comparisonLayout.rearrangeFileIds(index)
        self.informationFileLayout.rearrangeFileIds(index)

    def setLayout(self, newLayout):
        for layout in (self.fileBoxLayout, self.comparisonLayout, self.informationFileLayout):
            if layout == newLayout:
                self.lowerLayout.addLayout(layout)
                layout.show()
            else:
                self.lowerLayout.removeItem(layout)
                layout.hide()

    def buttonFilesPressed(self):
        self.setLayout(self.fileBoxLayout)
        self.mainWindow.textMainLayout.setLayout(self.mainWindow.fileTextLayout)

    def buttonComparisonPressed(self):
        self.setLayout(self.comparisonLayout)
        self.mainWindow.textMainLayout.setLayout(self.mainWindow.comparisonTextLayout)

    def buttonInfoPressed(self):
        self.setLayout(self.informationFileLayout)
        self.mainWindow.textMainLayout.setLayout(self.mainWindow.informationGraphLayout)

class FilesLayout(QVBoxLayout):
    def __init__(self, exclusive=True):
        super().__init__()

        self.fileButtonGroup = QButtonGroup()
        if exclusive:
            self.fileButtonGroup.setExclusive(True)
        else:
            self.fileButtonGroup.setExclusive(False)

    def addFile(self, fileClass, setChecked=False):
        radioButton = QRadioButton()
        index = self.fileButtonGroup.buttons().__len__()

        self.fileButtonGroup.addButton(radioButton, index)
        newFileButton = self.fileButtonGroup.button(index)
        newFileButton.setText(fileClass.fileName)
        newFileButton.setIcon(fileClass.icon)
        if setChecked:
            newFileButton.setChecked(True)
        self.addWidget(newFileButton)

    def deleteFile(self, index):
        self.removeWidget(self.fileButtonGroup.button(index))

    def rearrangeFileIds(self, index):
        for i in range(0, len(self.fileButtonGroup.buttons()) + 1):
            if i > index:
                button = self.fileButtonGroup.button(i)
                self.fileButtonGroup.setId(button, i - 1)

    def getSize(self):
        return self.fileButtonGroup.buttons().__len__()
    
    def getCurrentCheckedIndex(self):
        return self.fileButtonGroup.checkedId()
    
    def getButtons(self):
        return self.fileButtonGroup.buttons()

class FileClass():
    def __init__(self, fileName, fileDir, icon = QIcon(), text = "", textInfo = {}):
        self.fileName = fileName
        self.fileDir = fileDir
        self.icon = icon
        self.text = text
        self.textInfo = textInfo

class FileProcessor:
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        mainWindow.fileProcessor = self

    def initFile(self, fileName, fileDir, icon, text, textInfo):
        if "/" in fileName:
            fileName = fileName.split("/")[-1]

        file = FileClass(fileName, fileDir, icon, text, textInfo)
        return file

    def readFile(self, fileDir):
        nltkProc = self.mainWindow.nltkProcessor
        icon = QIcon()
        text = ""
        iconType = ""

        if fileDir[-4:] == ".txt":
            text = open(fileDir, "r", encoding="utf-8").read()
            icon.addFile(iconDict["textIcon"])
            iconType = "textIcon"

        elif fileDir[-4:] == ".pdf":
            pdf = pypdf.PdfReader(fileDir)
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
            icon.addFile(iconDict["pdfIcon"])
            iconType = "pdfIcon"

        elif fileDir[-3:] == ".py":
            text = open(fileDir, "r", encoding="utf-8").read()
            icon.addFile(iconDict["pyIcon"])
            iconType = "pyIcon"

        elif fileDir[-4:] == ".cpp":
            text = open(fileDir, "r", encoding="utf-8").read()
            icon.addFile(iconDict["cppIcon"])
            iconType = "cppIcon"

        elif fileDir[-2:] == ".c":
            text = open(fileDir, "r", encoding="utf-8").read()
            icon.addFile(iconDict["cIcon"])
            iconType = "cIcon"

        elif fileDir[-3:] == ".cs":
            text = open(fileDir, "r", encoding="utf-8").read()
            icon.addFile(iconDict["csIcon"])
            iconType = "csIcon"

        elif fileDir[-5:] == ".docx":
            doc = docx.Document(fileDir)
            for para in doc.paragraphs:
                text += para.text
                text += "\n"
            icon.addFile(iconDict["docxIcon"])
            iconType = "docxIcon"

        else:
            text = fileDir
            icon.addFile(iconDict["miscIcon"])
            iconType = "miscIcon"

        textInfo = nltkProc.processTextInfo(text)
        return text, textInfo, icon, iconType

class FileBoxLayout(QVBoxLayout):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        mainWindow.fileBoxLayout = self

        self.fileDict = self.mainWindow.fileDict
        self.filesLayout = FilesLayout(exclusive=True)
        self.buttonLayout = QHBoxLayout()
        self.addLayout(self.filesLayout)
        self.addStretch()
        self.addLayout(self.buttonLayout)

        self.buttonLoadFile = QPushButton()
        self.buttonLoadFile.setText("Load File")
        self.buttonLayout.addWidget(self.buttonLoadFile)

        self.buttonDeleteFile = QPushButton()
        self.buttonDeleteFile.setText("Delete File")
        self.buttonLayout.addWidget(self.buttonDeleteFile)
        
        self.filesLayout.fileButtonGroup.buttonClicked.connect(self.fileSelected)
        self.buttonLoadFile.clicked.connect(self.buttonLoadPressed)
        self.buttonDeleteFile.clicked.connect(self.buttonDeletePressed)

    def show(self):
        self.buttonLoadFile.show()
        self.buttonDeleteFile.show()
        buttons = self.filesLayout.getButtons()
        for button in buttons:
            button.show()            
    
    def hide(self):
        self.buttonLoadFile.hide()
        self.buttonDeleteFile.hide()
        buttons = self.filesLayout.getButtons()
        for button in buttons:
            button.hide()

    def fileSelected(self):
        index = self.filesLayout.getCurrentCheckedIndex()
        if index == -1:
            return
        fileTextLayout = self.mainWindow.fileTextLayout
        fileInfoLayout = self.mainWindow.fileInfoLayout
        
        file = self.fileDict[index]

        fileTextLayout.editBoxes(file)
        fileInfoLayout.editBoxes(file)

    def buttonLoadPressed(self):
        dialogBox = QFileDialog(self.mainWindow)
        dialogBox.fileSelected.connect(self.dialogBoxSelected)

        dialogBox.show()

    def dialogBoxSelected(self, fileDir):
        actionsLayout = self.mainWindow.actionsLayout
        fileTextLayout = self.mainWindow.fileTextLayout
        databaseProcessor = self.mainWindow.databaseProcessor 
        fileProcessor = self.mainWindow.fileProcessor

        text, textInfo, icon, iconType = fileProcessor.readFile(fileDir)
        file = fileProcessor.initFile(fileDir, fileDir, icon, text, textInfo)

        if self.fileDict.get(file.fileName) == None:
            actionsLayout.addFile(file)
            databaseProcessor.insertFile(file.fileName, file.fileDir)
            fileTextLayout.editBoxes(file)
        else:
            dialogBox = QMessageBox(self.mainWindow)
            dialogBox.setText("File already exists!")
            dialogBox.setStandardButtons(QMessageBox.StandardButton.Ok)
            dialogBox.show()

    def buttonDeletePressed(self):
        actionsLayout = self.mainWindow.actionsLayout

        dialogBox = QMessageBox(self.mainWindow)

        if self.fileDict.__len__() != 0:
            dialogBox.setText("Are you sure you want to delete this file?")
            dialogBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            dialogBox.exec()

            if dialogBox.clickedButton().text() == "&Yes":
                index = self.filesLayout.getCurrentCheckedIndex()
                actionsLayout.deleteFile(index)
        else:
            dialogBox.setText("There is no file to delete!")
            dialogBox.setStandardButtons(QMessageBox.StandardButton.Ok)
            dialogBox.show()

    def addFile(self, fileClass, setChecked=True):
        index = self.filesLayout.getSize()

        self.fileDict[fileClass.fileName] = fileClass
        self.fileDict[index] = fileClass
        self.filesLayout.addFile(fileClass, setChecked = setChecked)
 
    def deleteFile(self, index):
        indexDatabase = index + 1
        fileTextLayout = self.mainWindow.fileTextLayout
        infoBoxLayout = self.mainWindow.fileInfoLayout

        self.filesLayout.deleteFile(index)
        fileTextLayout.editBoxes(0)
        infoBoxLayout.editBoxes(0)

        if self.fileDict.__len__() != 0:
            self.fileDict.pop(self.fileDict[index].fileName)
            self.fileDict.pop(index)

        self.mainWindow.databaseProcessor.deleteFile(indexDatabase)
        self.mainWindow.rearrangeFileIds(index)

    def rearrangeFileIds(self, index):
        self.filesLayout.rearrangeFileIds(index)

class ComparisonLayout(QVBoxLayout):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        mainWindow.comparisonLayout = self
        self.fileDict = self.mainWindow.fileDict
        self.nltkProcessor = self.mainWindow.nltkProcessor

        self.filesLayout = FilesLayout(exclusive=False)
        self.buttonsLayout = QHBoxLayout()

        self.buttonCompare = QPushButton()
        self.buttonCompare.setText("Compare")
        self.buttonsLayout.addWidget(self.buttonCompare)
        
        self.addLayout(self.filesLayout)
        self.addStretch()
        self.addLayout(self.buttonsLayout)

        self.buttonCompare.clicked.connect(self.buttonComparePressed)

    def hide(self):
        self.buttonCompare.hide()
        for button in self.filesLayout.getButtons():
            button.hide()

    def show(self):
        self.buttonCompare.show()
        for button in self.filesLayout.getButtons():
            button.show()

    def addFile(self, fileClass):
        self.filesLayout.addFile(fileClass)

    def deleteFile(self, index):
        self.filesLayout.deleteFile(index)

    def rearrangeFileIds(self, index):
        self.filesLayout.rearrangeFileIds(index)

    def buttonComparePressed(self):
        selectedIds = []
        buttons = self.filesLayout.getButtons()
        for button in buttons:
            if button.isChecked():
                id = self.filesLayout.fileButtonGroup.id(button)
                selectedIds.append(id)
        files = [self.fileDict[id] for id in selectedIds]
        mainText = ""
        fileMatrix = {}
        id1 = 0
        id2 = 0

        for file1 in files:
            mainText += file1.fileName + ":\n"
            id2 = 0
            for file2 in files:
                if file1 != file2:
                    if id1 < id2:
                        text1 = file1.textInfo["TextFiltered"]
                        text2 = file2.textInfo["TextFiltered"]
                        average = self.nltkProcessor.customFreqSimilarity(text1, text2)
                        average = round(average * 100, 3)

                        fileMatrix[f"{id1}, {id2}"] = average
                        fileMatrix[f"{id2}, {id1}"] = average

                    mainText += file2.fileName + ": %" + str(fileMatrix[f"{id1}, {id2}"]) + "\n"

                id2 += 1
            id1 += 1
            mainText += "\n\n"
        
        self.mainWindow.comparisonTextLayout.editBoxes(mainText)

class InformationFileLayout(QVBoxLayout):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        mainWindow.informationFileLayout = self

        self.filesLayout = FilesLayout(exclusive=True)

        self.addLayout(self.filesLayout)
        self.addStretch(1)

        self.filesLayout.fileButtonGroup.buttonClicked.connect(self.fileSelected)

    def fileSelected(self):
        informationGraphLayout = self.mainWindow.informationGraphLayout
        
        id = self.filesLayout.getCurrentCheckedIndex()
        file = self.mainWindow.fileDict[id]

        informationGraphLayout.updateGraph(file)

    def show(self):
        for button in self.filesLayout.getButtons():
            button.show()

    def hide(self):
        for button in self.filesLayout.getButtons():
            button.hide()

    def addFile(self, fileClass):
        self.filesLayout.addFile(fileClass)

    def deleteFile(self, index):
        self.filesLayout.deleteFile(index)

    def rearrangeFileIds(self, index):
        self.filesLayout.rearrangeFileIds(index)

class TextMainLayout(QVBoxLayout):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        mainWindow.textMainLayout = self

        self.fileTextLayout = fileTextLayout(mainWindow)
        self.comparisonTextLayout = ComparisonTextLayout(mainWindow)
        self.informationGraphLayout = InformationGraphLayout(mainWindow)

        self.addLayout(self.fileTextLayout)
        self.addLayout(self.comparisonTextLayout)
        self.addLayout(self.informationGraphLayout)

        self.comparisonTextLayout.hide()
        self.informationGraphLayout.hide()

    def setLayout(self, newLayout): 
        for layout in [self.fileTextLayout, self.comparisonTextLayout, self.informationGraphLayout]:
            if layout is newLayout:
                layout.show()
            else:
                layout.hide()

class fileTextLayout(QVBoxLayout):
    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        mainWindow.fileTextLayout = self
        
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        self.textBox = QLabel()
        self.fileInfoLayout = FileInfoLayout(MainWindow)
        self.textBox.setFrameStyle(2)
        self.scrollArea.setWidget(self.textBox)

        self.textBox.setWordWrap(True)
        self.addWidget(self.scrollArea)
        self.addLayout(self.fileInfoLayout)

    def editBoxes(self, input):
        if input == 0:
            self.textBox.setText("")
            self.fileInfoLayout.editBoxes(0)
        else:
            text = input.text
            self.textBox.setText(text)
            self.fileInfoLayout.editBoxes(input)

    def show(self):
        self.scrollArea.show()
        self.textBox.show()
        self.fileInfoLayout.show()

    def hide(self):
        self.scrollArea.hide()
        self.textBox.hide()
        self.fileInfoLayout.hide()

class FileInfoLayout(QVBoxLayout):
    def __init__(self, mainWindow):
        super().__init__()
        
        self.mainWindow = mainWindow
        self.mainWindow.fileInfoLayout = self

        self.scrollArea = QScrollArea()
        self.scrollArea.setMaximumHeight(100)
        self.scrollArea.setWidgetResizable(True)
        self.addWidget(self.scrollArea)

        self.infoText = QLabel()
        self.scrollArea.setWidget(self.infoText)

    def editBoxes(self, fileClass):
        if fileClass == 0:
            text = "Length: \nWord Count: \nMost Common Words: \nLeast Common Words: \nStop Words: "
            self.infoText.setText(text)
        else:
            textInfo = fileClass.textInfo
            text = "Length: " + str(textInfo["Length"]) + "\nWord Count: " + str(textInfo["WordCount"]) + "\nMost Common Words: " + str(textInfo["MostCommonWords"]) + "\nLeast Common Words: " + str(textInfo["LeastCommonWords"]) + "\nStop Words: " + str(textInfo["MostCommonStopWords"])
            self.infoText.setText(text)

    def show(self):
        self.scrollArea.show()
        self.infoText.show()

    def hide(self):
        self.scrollArea.hide()
        self.infoText.hide()

class ComparisonTextLayout(QVBoxLayout):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        mainWindow.comparisonTextLayout = self

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        self.textBox = QLabel()
        self.textBox.setFrameStyle(2)
        self.textBox.setWordWrap(True)
        self.scrollArea.setWidget(self.textBox)

        self.addWidget(self.scrollArea)

    def editBoxes(self, text):
        self.textBox.setText(text)

    def show(self):
        self.scrollArea.show()
        self.textBox.show()

    def hide(self):
        self.scrollArea.hide()
        self.textBox.hide()

class InformationGraphLayout(QVBoxLayout):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        mainWindow.informationGraphLayout = self

        self.graphLayout = GraphLayout(mainWindow)
        self.informationButtonLayout = InformationButtonLayout(mainWindow)

        self.addLayout(self.graphLayout)
        self.addLayout(self.informationButtonLayout)

    def updateGraph(self, fileClass):
        self.graphLayout.updateGraph(fileClass)

    def show(self):
        self.graphLayout.show()
        self.informationButtonLayout.show()

    def hide(self):
        self.graphLayout.hide()
        self.informationButtonLayout.hide()

class GraphLayout(QVBoxLayout):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        mainWindow.graphLayout = self

        self.graph = PlotWidget()
        self.graph.enableAutoRange(ViewBox.YAxis, True)

        self.addWidget(self.graph)

    def updateGraph(self, fileClass):
        self.graph.clear()

        mostCommonWordsClicked = self.mainWindow.informationButtonLayout.mostCommonWordsClicked
        leastCommonWordsClicked = self.mainWindow.informationButtonLayout.leastCommonWordsClicked

        mostCommonWords = fileClass.textInfo["MostCommonWords"]
        mostCommonWordsFreq = [word[1] for word in mostCommonWords]
        mostCommonWordsCount = 5
        
        leastCommonWords = fileClass.textInfo["LeastCommonWords"]
        leastCommonWordsFreq = [word[1] for word in leastCommonWords]
        leastCommonWordsCount = 5

        ticks = []
        for i in range(5):
            text = ""
            if mostCommonWordsClicked and len(mostCommonWords) > i:
                text += str(mostCommonWords[i][0]) + "\n"
            if leastCommonWordsClicked and len(leastCommonWords) > i:
                text += str(leastCommonWords[i][0]) + "\n"
            ticks.append((i, text))

        xAxis = self.graph.getAxis("bottom")
        xAxis.setTicks([ticks])
        self.graph.setAxisItems({"bottom": xAxis})

        if mostCommonWordsClicked:
            self.graph.plot(mostCommonWordsFreq, pen = mkPen(color="red"))
        if leastCommonWordsClicked:
            self.graph.plot(leastCommonWordsFreq, pen = mkPen(color="blue"))

    def show(self):
        self.graph.show()

    def hide(self):
        self.graph.hide()

class InformationButtonLayout(QVBoxLayout):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        mainWindow.informationButtonLayout = self
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(False)

        self.mostCommonWordsClicked = True
        self.leastCommonWordsClicked = False

        self.buttonMostCommonWords = QRadioButton()
        self.buttonMostCommonWords.setText("Most Common Words")
        self.buttonGroup.addButton(self.buttonMostCommonWords)
        self.buttonMostCommonWords.setChecked(True)
        self.addWidget(self.buttonMostCommonWords)

        self.buttonLeastCommonWords = QRadioButton()
        self.buttonLeastCommonWords.setText("Least Common Words")
        self.buttonGroup.addButton(self.buttonLeastCommonWords)
        self.addWidget(self.buttonLeastCommonWords)

        self.buttonGroup.buttonClicked.connect(self.buttonClicked)

    def buttonClicked(self, button):
        if button == self.buttonMostCommonWords:
            if not self.mostCommonWordsClicked:
                self.mostCommonWordsClicked = True
            else:
                self.mostCommonWordsClicked = False

        elif button == self.buttonLeastCommonWords:
            if not self.leastCommonWordsClicked:
                self.leastCommonWordsClicked = True
            else:
                self.leastCommonWordsClicked = False

    def getSelectedButtons(self):
        checkedButtonIds = []

        for button in self.buttonGroup.buttons():
            if button.isChecked():
                id = self.buttonGroup.id(button)
                checkedButtonIds.append(id)
        
        return checkedButtonIds

    def show(self):
        self.buttonMostCommonWords.show()
        self.buttonLeastCommonWords.show()

    def hide(self):
        self.buttonMostCommonWords.hide()
        self.buttonLeastCommonWords.hide()
