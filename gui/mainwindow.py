import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import qrc_resources
from file_menu.test_new2 import Wizard
from file_menu.process_raw_data import PrepareData, PopulateFileManager
from file_menu.import_data import autoProcessPUMSData


qgis_prefix = "C:\qgis"

class QTreeWidgetCMenu(QTreeWidget):
    def __init__(self, parent = None):
        super(QTreeWidgetCMenu, self).__init__(parent)

        
       
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        importDataAction = menu.addAction("&Import Data")
        self.connect(importDataAction, SIGNAL("triggered()"), self.importData)
        if self.item.parent() is None:
            menu.exec_(event.globalPos())

    def click(self, item, column):
        self.item = item
        
        
    def editItem(self, item, column):
        self.item = item
        if self.item.parent() is not None:
            self.openPersistentEditor(self.item, 1)

    def importData(self):
        QMessageBox.information(None, "Check", "Import Data", QMessageBox.Ok)
        

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.dirty = False
        self.projectName = None

        
        self.setWindowTitle("HIPGen Version-0.50")
        self.setWindowIcon(QIcon("./images/popsyn.png"))
        self.workingWindow = QLabel()
        self.showMaximized()
        self.setMinimumSize(800,500)
        self.workingWindow.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.workingWindow)
        
        
        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready", 5000)
        
# FILE MENU 
# Defining menu/toolbar actions        
        projectNewAction = self.createAction("&New Project", self.projectNew, QKeySequence.New, 
                                             "projectnew", "Create a new HIPGen project.")
        projectOpenAction = self.createAction("&Open Project", self.projectOpen, QKeySequence.Open, 
                                              "projectopen", "Open an existing HIPGen project.")
        projectSaveAction = self.createAction("&Save Project", self.projectSave, QKeySequence.Save, 
                                              "projectsave", "Save the current HIPGen project.")
        projectSaveAsAction = self.createAction("Save Project &As...", self.projectSaveAs, 
                                                icon="projectsaveas", tip="Save the current HIPGen project with a new name.")
        projectCloseAction = self.createAction("&Close Project", self.projectClose, "Ctrl+W",
                                                tip="Close the current HIPGen project.")
        applicationQuitAction = self.createAction("&Quit", self.close, "Ctrl+Q",
                                                icon="quit", tip="Close the application.")
# Adding actions to menu
        self.fileMenu = self.menuBar().addMenu("&File")
        self.addActions(self.fileMenu, (projectNewAction, projectOpenAction, None, projectSaveAction, 
                                           projectSaveAsAction, None, projectCloseAction, None, applicationQuitAction))
# Adding actions to toolbar
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.setObjectName("FileToolBar")
        self.addActions(self.fileToolBar, (projectNewAction, projectOpenAction, projectSaveAction, projectSaveAsAction))
        

# DATA MENU 
# Defining menu/toolbar actions        
        dataSourceAction = self.createAction("Data Source &Connection", self.dataSource, 
                                             icon="datasource", tip="Enter credentials for the MySQL data source.")
        dataStatisticsAction = self.createAction("&Statistics", self.dataStatistics,  
                                              icon="statistics", tip="Conduct descriptive analysis.")
        dataModifyAction = self.createAction("&Modify", self.dataModify,  
                                              icon="modifydata", tip="Modify the input data.")
# Adding actions to menu
        self.dataMenu = self.menuBar().addMenu("&Data")
        self.addActions(self.dataMenu, (dataSourceAction, None, dataStatisticsAction, dataModifyAction))
# Adding actions to toolbar
        self.dataToolBar = self.addToolBar("Data")
        self.dataToolBar.setObjectName("DataToolBar")
        self.addActions(self.dataToolBar, (dataSourceAction,  dataStatisticsAction, dataModifyAction))

# SYNTHESIZER MENU
# Defining menu/toolbar actions
        synthesizerControlVariablesAction = self.createAction("Control &Variables", self.synthesizerControlVariables,
                                                   icon="controlvariables",
                                                   tip="Select variables to control.")
        synthesizerParameterAction = self.createAction("&Parameters/Settings", self.synthesizerParameter,
                                                       icon="parameters",
                                                       tip="Define the different parameter values.")
        synthesizerRunAction = self.createAction("Run", self.synthesizerRun, 
                                               icon="run", tip="Run the populaiton synthesis.")
        synthesizerRunAction.setEnabled(False)
        synthesizerStopAction = self.createAction("Stop", self.synthesizerStop, 
                                                   icon="stop", tip="Stop the current population synthesis run.")
# Adding actions to menu
        self.synthesizerMenu = self.menuBar().addMenu("&Synthesizer")
        self.addActions(self.synthesizerMenu, (synthesizerControlVariablesAction, synthesizerParameterAction, None, 
                                               synthesizerRunAction, synthesizerStopAction))
# Adding actions to toolbar
        self.synthesizerToolBar = self.addToolBar("Synthesizer")
        self.addActions(self.synthesizerToolBar, (synthesizerControlVariablesAction, synthesizerParameterAction, 
                                                  synthesizerRunAction))


# RESULTS MENU
# Defining menu/toolbar actions
        resultsRegionalAARDAction = self.createAction("Average Absolute Relative Difference", 
                                                      self.resultsRegionalAARD, 
                                                      tip="""Display the distribution of AARD"""
                                                      """across all individual geographies.""")
        resultsRegionalPValueAction = self.createAction("P-Value", 
                                                      self.resultsRegionalPValue, 
                                                      tip="""Display the distribution of P-value"""
                                                      """for the synthetic population across all individual geographies.""")
        resultsRegionalHousDistAction = self.createAction("Housing Attribute Distribution", 
                                                      self.resultsRegionalHousDist, 
                                                      tip="Comparison of Housing Attributes.")
        resultsRegionalPersDistAction = self.createAction("Person Attribute Distribution", 
                                                      self.resultsRegionalPersDist, 
                                                      tip="Comparison of Person Attributes.")


        resultsRegionalAction = self.createAction("Regional Geography Statistics",
                                                  self.resultsRegional,
                                                  icon="region",
                                                  tip = "Display performance statistics for the entire region")



        resultsIndividualAction = self.createAction("&Individual Geography Statistics",
                                                    self.resultsIndividual,
                                                    icon="individualgeo",
                                                    tip = "Display performance statistics for individual geographies")


# Adding actions to menu
        self.resultsMenu = self.menuBar().addMenu("&Results")
        self.regionwideSubMenu = self.resultsMenu.addMenu(QIcon("images/region.png"),"Regional Statistics")
        self.addActions(self.regionwideSubMenu, (resultsRegionalAARDAction, resultsRegionalPValueAction,
                                                 resultsRegionalHousDistAction, resultsRegionalPersDistAction))

        self.addActions(self.resultsMenu, (resultsIndividualAction,))
# Adding actions to toolbar

        self.resultsToolBar = self.addToolBar("Results")
        self.addActions(self.resultsToolBar, (resultsRegionalAction, resultsIndividualAction))

# HELP MENU
        self.helpMenu = self.menuBar().addMenu("&Help")




# FILE MANAGER
# Setting up the file manager
        fileManagerDockWidget = QDockWidget("File Manager", self)
        fileManagerDockWidget.setObjectName("FileManagerDockWidget")
        fileManagerDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea)

        self.fileManager = QTreeWidgetCMenu()
        self.fileManager.setMinimumSize(250, 400)
        self.fileManager.setColumnCount(2)
        self.fileManager.setHeaderLabels(["Name", "Value"])
        self.fileManager.setItemsExpandable(True)
        fileManagerDockWidget.setWidget(self.fileManager)
        self.addDockWidget(Qt.LeftDockWidgetArea, fileManagerDockWidget)
        
        ancestor = QTreeWidgetItem(self.fileManager, [QString("<Database>"), QString("<location>")])
        parent = QTreeWidgetItem(ancestor, [QString("<Tables>")])
        QTreeWidgetItem(parent, [QString("<Variables>")])
        self.fileManager.expandItem(parent)
        self.fileManager.expandItem(ancestor)
        self.fileManager.setEnabled(False)
        
        self.connect(self.fileManager, SIGNAL("itemDoubleClicked(QTreeWidgetItem *,int)"), self.fileManager.editItem)
        self.connect(self.fileManager, SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.fileManager.click)



# Defining all the slots and supporting methods

    def projectNew(self):
        #QMessageBox.information(self, "Information", "Create new project", QMessageBox.Ok)
        wizard = Wizard()
        wizard.setWindowIcon(QIcon("./images/projectnew.png"))

        if wizard.exec_():
            print "complete"
            PopulateFileManager(wizard.project, self.fileManager)
            if wizard.project.sampleUserProv.userProv:
                autoProcessPUMSData(wizard.project)
            #PrepareData(wizard.project)
        else:
            print "working"



    def projectOpen(self):
        QMessageBox.information(self, "Information", "Open project", QMessageBox.Ok)


    def projectSave(self):
        QMessageBox.information(self, "Information", "Save project", QMessageBox.Ok)


    def projectSaveAs(self):
        QMessageBox.information(self, "Information", "Save project as", QMessageBox.Ok)

    
    def projectClose(self):
        QMessageBox.information(self, "Information", "Close project", QMessageBox.Ok)


    def dataSource(self):
        QMessageBox.information(self, "Information", "Define MySQL datasource", QMessageBox.Ok)


    def dataStatistics(self):
        QMessageBox.information(self, "Information", "Run some descriptive analysis", QMessageBox.Ok)

    
    def dataModify(self):
        QMessageBox.information(self, "Information", "Modify data categories", QMessageBox.Ok)


    def synthesizerControlVariables(self):
        QMessageBox.information(self, "Synthesizer", "Select control variables", QMessageBox.Ok)

    def synthesizerParameter(self):
        QMessageBox.information(self, "Synthesizer", "Define synthesizer parameters", QMessageBox.Ok)

    def synthesizerRun(self):
        QMessageBox.information(self, "Synthesizer", "Run the population synthesizer", QMessageBox.Ok)


    def synthesizerStop(self):
        QMessageBox.information(self, "Synthesizer", "Stop the current run of the population synthesizer", QMessageBox.Ok)

    
    def resultsRegionalAARD(self):
        QMessageBox.information(self, "Results", "Regional AARD distribution", QMessageBox.Ok)
    
    def resultsRegionalPValue(self):
        QMessageBox.information(self, "Results", "Regional P-Value Distribution", QMessageBox.Ok)
    
    def resultsRegionalHousDist(self):
        QMessageBox.information(self, "Results", "Regional Housing Attribute Distribution", QMessageBox.Ok)
    
    def resultsRegionalPersDist(self):
        QMessageBox.information(self, "Results", "Regional Person Attribute Distribution", QMessageBox.Ok)
    
    def resultsRegional(self):
        QMessageBox.information(self, "Results", "Regional Performance Statistics", QMessageBox.Ok)
    
    def resultsIndividual(self):
        QMessageBox.information(self, "Results", "Individual Performance Statistics", QMessageBox.Ok)





    def createAction(self, text, slot=None, shortcut=None, icon=None, 
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon("./images/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
        

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
    
def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
    app.setApplicationName("Heurisitc Iterative Population Generator (HIPGen)")
    form = MainWindow()
    form.show()
    app.exec_()


if __name__=="__main__":
    main()
