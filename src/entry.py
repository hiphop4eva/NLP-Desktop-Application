from window import *
from languageProcessing import *
from databaseProcessing import *

nltkProc = nltkProcessor()
databaseProc = databaseProcessor(nltkProc)
mainWindow = MainWindow(nltkProc, databaseProc)

sys.exit(app.exec())