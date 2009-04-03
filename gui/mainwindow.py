from __future__ import with_statement


import os, sys, pickle
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import qrc_resources
from file_menu.wizard_window_validate import Wizard
from file_menu.filemanager import QTreeWidgetCMenu
from file_menu.open_project import OpenProject
from data_menu.data_process_status import DataDialog
from file_menu.summary_page import SummaryPage

from results_menu.view_aard import *
from results_menu.view_pval import *
from results_menu.view_hhdist import *
from results_menu.view_ppdist import *
from results_menu.view_indgeo import *
from results_menu.view_hhmap import *
from results_menu.coreplot import *

qgis_prefix = "C:\qgis"

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.dirty = False
        self.projectName = None

        
        self.setWindowTitle("PopSim Version-0.50")
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
                                             "projectnew", "Create a new PopSim project.")
        projectOpenAction = self.createAction("&Open Project", self.projectOpen, QKeySequence.Open, 
                                              "projectopen", "Open an existing PopSim project.")
        projectSaveAction = self.createAction("&Save Project", self.projectSave, QKeySequence.Save, 
                                              "projectsave", "Save the current PopSim project.")
        projectSaveAsAction = self.createAction("Save Project &As...", self.projectSaveAs, 
                                                icon="projectsaveas", tip="Save the current PopSim project with a new name.")
        projectCloseAction = self.createAction("&Close Project", self.projectClose, "Ctrl+W",
                                                tip="Close the current PopSim project.")
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
        dataImportAction = self.createAction("&Import", self.dataImport, icon="fileimport", 
                                             tip="Import data into MySQL database.")
        dataStatisticsAction = self.createAction("&Statistics", self.dataStatistics,  
                                                 icon="statistics", tip="Conduct descriptive analysis.")
        dataModifyAction = self.createAction("&Modify", self.dataModify,  
                                             icon="modifydata", tip="Modify the input data.")
# Adding actions to menu
        self.dataMenu = self.menuBar().addMenu("&Data")
        self.addActions(self.dataMenu, (dataSourceAction, None, dataImportAction, dataStatisticsAction, dataModifyAction))

# Adding actions to toolbar
        self.dataToolBar = self.addToolBar("Data")
        self.dataToolBar.setObjectName("DataToolBar")
        self.addActions(self.dataToolBar, (dataSourceAction,  dataImportAction, dataStatisticsAction, dataModifyAction))

        #self.dataMenu.setDisabled(True)
        #self.dataToolBar.setDisabled(True)

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

        self.synthesizerMenu.setDisabled(True)
        self.synthesizerToolBar.setDisabled(True)


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

        resultsViewHHAction = self.createAction("&View Households",
                                                    self.resultsViewHH,
                                                    icon="viewhh",
                                                    tip = "Display synthesized households for the entire region")

# Adding actions to menu
        self.resultsMenu = self.menuBar().addMenu("&Results")
        self.regionwideSubMenu = self.resultsMenu.addMenu(QIcon("images/region.png"),"Regional Statistics")
        self.addActions(self.regionwideSubMenu, (resultsRegionalAARDAction, resultsRegionalPValueAction,
                                                 resultsRegionalHousDistAction, resultsRegionalPersDistAction))

        self.addActions(self.resultsMenu, (resultsIndividualAction,))
        self.addActions(self.resultsMenu, (resultsViewHHAction,))
# Adding actions to toolbar

        self.resultsToolBar = self.addToolBar("Results")
        self.addActions(self.resultsToolBar, (resultsRegionalAction, resultsIndividualAction))

        #self.resultsMenu.setDisabled(True)
        #self.resultsToolBar.setDisabled(True)


# HELP MENU
# Defining menu/toolbar actions
        helpDocumentationAction = self.createAction("Documentation",
                                                    self.showDocumentation, 
                                                    tip="Display the documentation of PopSim.", 
                                                    icon = "documentation")
        helpHelpAction = self.createAction("Help",
                                           self.showHelp, 
                                           tip="Quick reference for important parameters",
                                           icon="help")

        helpAboutAction = self.createAction("About PopSim",
                                            self.showAbout, 
                                            tip="Display software information")

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(self.helpMenu, (helpDocumentationAction, helpHelpAction, None, helpAboutAction))




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
        
        #self.connect(self.fileManager, SIGNAL("itemDoubleClicked(QTreeWidgetItem *,int)"), self.fileManager.editItem)
        self.connect(self.fileManager, SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.fileManager.click)



# Defining all the slots and supporting methods

    def projectNew(self):
        if not self.fileManager.isEnabled():
            self.runWizard()
        else:
            reply = QMessageBox.question(None, "PopSim: New Project Wizard",
                                         QString("""A PopSim project already open. Do you wish to continue?"""),
                                         QMessageBox.Yes| QMessageBox.No)
            if reply == QMessageBox.Yes:
                save = QMessageBox.question(None, "PopSim: New Project Wizard",
                                            QString("""Do you wish to save the project?"""),
                                            QMessageBox.Yes| QMessageBox.No)
                if save == QMessageBox.Yes:
                    self.project.save()
                else:
                    self.runWizard()


    def runWizard(self):
        self.wizard = Wizard()
        self.wizard.setWindowIcon(QIcon("./images/projectnew.png"))
        
        if self.wizard.exec_():
            print "complete"
            self.project = self.wizard.project
            self.fileManager.project = self.project
            self.fileManager.populate()

    def projectOpen(self):
        project = OpenProject()
        
        if not project.file.isEmpty():
            if self.fileManager.isEnabled():
                reply = QMessageBox.warning(None, "PopSim: Open Existing Project",
                                            QString("""A PopSim project already open. Do you wish to continue?"""),
                                            QMessageBox.Yes| QMessageBox.No)
                if reply == QMessageBox.Yes:
                    save = QMessageBox.warning(None, "PopSim: Save Existing Project",
                                               QString("""Do you wish to save the project?"""),
                                               QMessageBox.Yes| QMessageBox.No)
                    if save == QMessageBox.Yes:
                        SaveProject(self.project)
                    with open(project.file, 'rb') as f:
                        self.project = pickle.load(f)
                        self.fileManager.project = self.project
                        self.fileManager.populate()
                        #PopulateFileManager(self.project, self.fileManager)

            else:
                with open(project.file, 'rb') as f:
                    self.project = pickle.load(f)
                    self.fileManager.project = self.project
                    self.fileManager.populate()
                    #PopulateFileManager(self.project, self.fileManager)
                    

    def projectSave(self):
        QMessageBox.information(self, "Information", "Save project", QMessageBox.Ok)
        #use = UserImportSFData()


    def projectSaveAs(self):
        QMessageBox.information(self, "Information", "Save project as", QMessageBox.Ok)

    
    def projectClose(self):
        QMessageBox.information(self, "Information", "Close project", QMessageBox.Ok)


    def dataSource(self):
        QMessageBox.information(self, "Information", "Define MySQL datasource", QMessageBox.Ok)


    def dataImport(self):
        dataprocesscheck = DataDialog(self.project)
        dataprocesscheck.exec_()

    def dataStatistics(self):
        QMessageBox.information(self, "Information", "Run some descriptive analysis", QMessageBox.Ok)

    
    def dataModify(self):
        from database.createDBConnection import createDBC
        from gui.file_menu.newproject import DBInfo
        db = DBInfo("localhost", "root", "1234")
        a = createDBC(db, "fifth")
        a.dbc.open()
        
        from data_menu.display_data import DisplayTable
        b = DisplayTable("person_marginals_az")
        
        c = QDialog()
        layout = QVBoxLayout()

        layout.addWidget(b.view)
        
        c.setLayout(layout)
        c.exec_()
        
        

        a.dbc.close()


    def synthesizerControlVariables(self):
        QMessageBox.information(self, "Synthesizer", "Select control variables", QMessageBox.Ok)

    def synthesizerParameter(self):
        QMessageBox.information(self, "Synthesizer", "Define synthesizer parameters", QMessageBox.Ok)

    def synthesizerRun(self):
        QMessageBox.information(self, "Synthesizer", "Run the population synthesizer", QMessageBox.Ok)


    def synthesizerStop(self):
        QMessageBox.information(self, "Synthesizer", "Stop the current run of the population synthesizer", QMessageBox.Ok)

    
    def resultsRegionalAARD(self):
        aard = Absreldiff()
        aard.exec_()
    def resultsRegionalPValue(self):
        pval = Pval()
        pval.exec_()  
    def resultsRegionalHousDist(self):
        hhdist = Hhdist()
        hhdist.exec_()
    def resultsRegionalPersDist(self):
        ppdist = Ppdist()
        ppdist.exec_()    
        
    def resultsRegional(self):
        QMessageBox.information(self, "Results", "Regional Performance Statistics", QMessageBox.Ok)
    
    def resultsIndividual(self):
        indgeo = Indgeo()
        indgeo.exec_()         
    def resultsViewHH(self):
        res = Hhmap()
        res.exec_()
        

    def showDocumentation(self):
        QMessageBox.information(self, "Help", "Documentation", QMessageBox.Ok)

    def showHelp(self):
        QMessageBox.information(self, "Help", "Help", QMessageBox.Ok)

    def showAbout(self):
        QMessageBox.information(self, "Help", "About", QMessageBox.Ok)

    def createAction(self, text, slot=None, shortcut=None, icon=None, 
                     tip=None, checkable=False, disabled = None, signal="triggered()"):
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
        if disabled:
            action.setDisabled(True)

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
    app.setApplicationName("Synthetic Population Simulator (HIPGen)")
    form = MainWindow()
    form.show()
    app.exec_()


if __name__=="__main__":
    main()
