from __future__ import with_statement


import os, sys, pickle, re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import qrc_resources
from file_menu.wizard_window_validate import Wizard
from file_menu.filemanager import QTreeWidgetCMenu
from file_menu.open_project import OpenProject
from file_menu.summary_page import SummaryPage
from data_menu.data_process_status import DataDialog
from data_menu.data_connection import DBConnectionDialog
from data_menu.display_data import DisplayTable
from results_menu.results_preprocessor import *
from synthesizer_menu.sample_control_corr import SetCorrDialog
from synthesizer_menu.parameters import ParametersDialog
from synthesizer_menu.run import RunDialog

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

        
        self.setWindowTitle("PopGen Version-0.50")
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
                                             "projectnew", "Create a new PopGen project.")
        projectOpenAction = self.createAction("&Open Project", self.projectOpen, QKeySequence.Open, 
                                              "projectopen", "Open an existing PopGen project.")
        self.projectSaveAction = self.createAction("&Save Project", self.projectSave, QKeySequence.Save, 
                                              "projectsave", "Save the current PopGen project.")
        self.projectSaveAsAction = self.createAction("Save Project &As...", self.projectSaveAs, 
                                                icon="projectsaveas", tip="Save the current PopGen project with a new name.")
        self.projectCloseAction = self.createAction("&Close Project", self.projectClose, "Ctrl+W",
                                                tip="Close the current PopGen project.")
        applicationQuitAction = self.createAction("&Quit", self.close, "Ctrl+Q",
                                                icon="quit", tip="Close the application.")
        
        self.projectSaveAction.setEnabled(False)
        self.projectSaveAsAction.setEnabled(False)
        self.projectCloseAction.setEnabled(False)

# Adding actions to menu
        self.fileMenu = self.menuBar().addMenu("&File")
        self.addActions(self.fileMenu, (projectNewAction, projectOpenAction, None, self.projectSaveAction, 
                                           self.projectSaveAsAction, None, self.projectCloseAction, None, applicationQuitAction))
# Adding actions to toolbar
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.setObjectName("FileToolBar")
        self.addActions(self.fileToolBar, (projectNewAction, projectOpenAction, self.projectSaveAction, self.projectSaveAsAction))
        

# DATA MENU 
# Defining menu/toolbar actions        
        dataSourceAction = self.createAction("Data Source &Connection", self.dataSource, 
                                             icon="datasource", tip="Enter credentials for the MySQL data source.")
        dataImportAction = self.createAction("&Import", self.dataImport, icon="fileimport", 
                                             tip="Import data into MySQL database.")
        #dataStatisticsAction = self.createAction("&Statistics", self.dataStatistics,  
        #                                         icon="statistics", tip="Conduct descriptive analysis.")

        dataModifyAction = self.createAction("&View and Modify", self.dataModify,  
                                             icon="modifydata", tip="View, analyze and modify the input data.")
# Adding actions to menu
        self.dataMenu = self.menuBar().addMenu("&Data")

        #self.addActions(self.dataMenu, (dataSourceAction, None, dataImportAction, dataStatisticsAction, dataModifyAction))
        self.addActions(self.dataMenu, (dataSourceAction, None, dataImportAction, dataModifyAction))

# Adding actions to toolbar
        self.dataToolBar = self.addToolBar("Data")
        self.dataToolBar.setObjectName("DataToolBar")
        #self.addActions(self.dataToolBar, (dataSourceAction,  dataImportAction, dataStatisticsAction, dataModifyAction))
        self.addActions(self.dataToolBar, (dataSourceAction,  dataImportAction, dataModifyAction))

        self.dataMenu.setDisabled(True)
        self.dataToolBar.setDisabled(True)

# SYNTHESIZER MENU
# Defining menu/toolbar actions
        #synthesizerControlVariablesAction = self.createAction("Control &Variables", self.synthesizerControlVariables,
        #                                                      icon="controlvariables",
        #                                                      tip="Select variables to control.")
        setCorrespondenceAction = self.createAction("Set Correspondence", self.synthesizerSetCorrBetVariables, 
                                                    icon="varcorr",
                                                    tip="""Select the variables and """
                                                    """set the correspondence map between the variables """
                                                    """in the sample file and variables in the control file.""")
        synthesizerParameterAction = self.createAction("&Parameters/Settings", self.synthesizerParameter,
                                                       icon="parameters",
                                                       tip="Define the different parameter values.")
        synthesizerRunAction = self.createAction("Run", self.synthesizerRun, 
                                                 icon="run", tip="Run the populaiton synthesis.")
        synthesizerStopAction = self.createAction("Stop", self.synthesizerStop, 
                                                  icon="stop", tip="Stop the current population synthesis run.")
# Adding actions to menu
        self.synthesizerMenu = self.menuBar().addMenu("&Synthesizer")
        #self.addActions(self.synthesizerMenu, (synthesizerControlVariablesAction, setCorrespondenceAction, 
        #                                       synthesizerParameterAction, None, 
        #                                       synthesizerRunAction, synthesizerStopAction))
        self.addActions(self.synthesizerMenu, (setCorrespondenceAction, 
                                               synthesizerParameterAction, None, 
                                               synthesizerRunAction, synthesizerStopAction))
# Adding actions to toolbar
        self.synthesizerToolBar = self.addToolBar("Synthesizer")
        #self.addActions(self.synthesizerToolBar, (synthesizerControlVariablesAction, synthesizerParameterAction, 
        #                                          synthesizerRunAction))
        self.addActions(self.synthesizerToolBar, (setCorrespondenceAction, synthesizerParameterAction, 
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
        #self.resultsToolBar.addToolBar(QIcon("Regional SubMenu"))
        self.addActions(self.resultsToolBar, (resultsRegionalAction, resultsIndividualAction))

        self.resultsMenu.setDisabled(True)
        self.resultsToolBar.setDisabled(True)


# HELP MENU
# Defining menu/toolbar actions
        helpDocumentationAction = self.createAction("Documentation",
                                                    self.showDocumentation, 
                                                    tip="Display the documentation of PopGen.", 
                                                    icon = "documentation")
        helpHelpAction = self.createAction("Help",
                                           self.showHelp, 
                                           tip="Quick reference for important parameters",
                                           icon="help")

        helpAboutAction = self.createAction("About PopGen",
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
        fileManagerDockWidget.setWidget(self.fileManager)
        self.addDockWidget(Qt.LeftDockWidgetArea, fileManagerDockWidget)
        
        #self.connect(self.fileManager, SIGNAL("itemDoubleClicked(QTreeWidgetItem *,int)"), self.fileManager.editItem)
        self.connect(self.fileManager, SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.fileManager.click)
        self.connect(self, SIGNAL("Dirty(bool)"), self.windowDirty)

    def windowDirty(self, value):
        print 'entering dirty %s' %value
        if value:
            self.setWindowTitle("PopGen Version-0.50 %s*" %self.project.name)
        else:
            self.setWindowTitle("PopGen Version-0.50 %s" %self.project.name)
            


# Defining all the slots and supporting methods

    def projectNew(self):
        if not self.fileManager.isEnabled():
            self.runWizard()
        else:
            reply = QMessageBox.question(None, "PopGen: New Project Wizard",
                                         QString("""A PopGen project already open. Do you wish to continue?"""),
                                         QMessageBox.Yes| QMessageBox.No)
            if reply == QMessageBox.Yes:
                save = QMessageBox.question(None, "PopGen: New Project Wizard",
                                            QString("""Do you wish to save the project?"""),
                                            QMessageBox.Yes| QMessageBox.No)
                self.fileManager.clear()
                self.fileManager.setEnabled(False)
                self.enableFunctions(False)
                self.project = None

                if save == QMessageBox.Yes:
                    self.project.save()
                self.runWizard()


    def runWizard(self):
        self.wizard = Wizard()
        self.wizard.setWindowIcon(QIcon("./images/projectnew.png"))
        
        if self.wizard.exec_():
            #print "complete"
            self.project = self.wizard.project
            self.setWindowTitle("PopGen: Version-0.50 (%s)" %(self.project.filename))
            self.project.save()
            self.fileManager.project = self.project
            self.fileManager.populate()
            self.enableFunctions(True)


    def enableFunctions(self, option):
        self.projectSaveAction.setEnabled(option)
        self.projectSaveAsAction.setEnabled(option)
        self.projectCloseAction.setEnabled(option)
        
        self.dataMenu.setEnabled(option)
        self.dataToolBar.setEnabled(option)

        self.synthesizerMenu.setEnabled(option)
        self.synthesizerToolBar.setEnabled(option)

        self.resultsMenu.setEnabled(option)
        self.resultsToolBar.setEnabled(option)

    def projectOpen(self):
        project = OpenProject()

        if not project.file.isEmpty():
            if self.fileManager.isEnabled():
                reply = QMessageBox.warning(None, "PopGen: Open Existing Project",
                                            QString("""A PopGen project already open. Do you wish to continue?"""),
                                            QMessageBox.Yes| QMessageBox.No)
                if reply == QMessageBox.Yes:
                    save = QMessageBox.warning(None, "PopGen: Save Existing Project",
                                               QString("""Do you wish to save the project?"""),
                                               QMessageBox.Yes| QMessageBox.No)
                    if save == QMessageBox.Yes:
                        SaveProject(self.project)
                    with open(project.file, 'rb') as f:
                        self.project = pickle.load(f)
                        self.setWindowTitle("PopGen: Version-0.50 (%s)" %self.project.filename)
                        self.fileManager.project = self.project
                        self.fileManager.populate()
                        self.enableFunctions(True)
                        #PopulateFileManager(self.project, self.fileManager)

            else:
                with open(project.file, 'rb') as f:
                    self.project = pickle.load(f)
                    self.setWindowTitle("PopGen: Version-0.50 (%s)" %self.project.filename)
                    self.fileManager.project = self.project
                    self.fileManager.populate()
                    self.enableFunctions(True)
                    #PopulateFileManager(self.project, self.fileManager)
                    

    def projectSave(self):
        if self.project:
            self.project.save()


    def projectSaveAs(self):
        file = QFileDialog.getSaveFileName(self, QString("Save As..."), 
                                                             "%s" %self.project.location, 
                                                             "PopGen File (*.pop)")
        
        file = re.split("[/.]", file)
        filename = file[-2]
        if not filename.isEmpty():
            reply = QMessageBox.warning(self, "PopGen: Save Existing Projec As...",
                                        QString("""Do you wish to continue?"""), 
                                        QMessageBox.Yes| QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.project.filename = filename
                self.project.save()
                self.setWindowTitle("PopGen: Version-0.50 (%s)" %self.project.filename)

    
    def projectClose(self):
        QMessageBox.information(self, "Information", "Close project", QMessageBox.Ok)
        self.fileManager.clear()
        self.fileManager.setEnabled(False)
        self.enableFunctions(False)
        self.project = None


    def dataSource(self):
        dataConnectionDia = DBConnectionDialog(self.project)
        if dataConnectionDia.exec_():
            if self.project <> dataConnectionDia.project:
                self.project = dataConnectionDia.project
                self.project.save()
                self.fileManager.populate()


    def dataImport(self):
        dataprocesscheck = DataDialog(self.project)
        dataprocesscheck.exec_()
        self.fileManager.populate()

    def dataStatistics(self):
        QMessageBox.information(self, "Information", "Run some descriptive analysis", QMessageBox.Ok)

    
    def dataModify(self):
        try:
            check = self.fileManager.item.parent().text(0) == 'Data Tables'
            tablename = self.fileManager.item.text(0)
            if check:
                b = DisplayTable(self.project, tablename)
                
                b.exec_()
        except Exception, e:
            print "Please highlight a valid table to display or use the context menu to bring up a table."
            

    def synthesizerControlVariables(self):
        QMessageBox.information(self, "Synthesizer", "Select control variables", QMessageBox.Ok)


    def synthesizerSetCorrBetVariables(self):
        #Set the correspondence between variables
        vars = SetCorrDialog(self.project)
        if vars.exec_():
            self.project = vars.project
            self.project.save()
            self.fileManager.populate()



    def synthesizerParameter(self):
        parameters = ParametersDialog(self.project)
        if parameters.exec_():
            self.project.save()

    def synthesizerRun(self):
        runDia = RunDialog(self.project)
        
        runDia.exec_()
        
        for i in self.project.synGeoIds:
            print i

        self.fileManager.populate()
        self.project.save()

        
    def synthesizerStop(self):
        QMessageBox.information(self, "Synthesizer", "Stop the current run of the population synthesizer", QMessageBox.Ok)

    def resultsRegionalAARD(self):
        aard = Absreldiff(self.project)
        aard.exec_()
    def resultsRegionalPValue(self):
        pval = Pval(self.project)
        pval.exec_()  
    def resultsRegionalHousDist(self):
        hhdist = Hhdist(self.project)
        hhdist.exec_()
    def resultsRegionalPersDist(self):
        ppdist = Ppdist(self.project)
        ppdist.exec_()    
        
    def resultsRegional(self):
        QMessageBox.information(self, "Results", "Regional Performance Statistics", QMessageBox.Ok)
    
    def resultsIndividual(self):
        #res = ResultsGen(self.project)
        indgeo = Indgeo(self.project)
        indgeo.exec_()         
    def resultsViewHH(self):
        res = Hhmap(self.project)
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
