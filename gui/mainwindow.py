# PopGen 1.0 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand 
# Copyright (C) 2009, Arizona State University
# See PopGen/License

from __future__ import with_statement


import os, sys, pickle, re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from database.createDBConnection import createDBC
from file_menu.wizard_window_validate import Wizard
from file_menu.filemanager import QTreeWidgetCMenu
from file_menu.open_project import OpenProject, SaveFile
from file_menu.summary_page import SummaryPage
from data_menu.data_process_status import DataDialog
from data_menu.data_connection import DBConnectionDialog
from data_menu.display_data import DisplayTable, DisplayTableStructure
from results_menu.results_preprocessor import *
from synthesizer_menu.sample_control_corr import SetCorrDialog
from synthesizer_menu.parameters import ParametersDialog
from synthesizer_menu.run import RunDialog
from misc.errors import FileError

from results_menu.view_aard import *
from results_menu.view_pval import *
from results_menu.view_hhdist import *
from results_menu.view_ppdist import *
from results_menu.view_indgeo import *
from results_menu.view_hhmap import *
from results_menu.view_thmap import *
from results_menu.coreplot import *

from help_menu.helpform import *

if sys.platform.startswith('win'):
    qgis_prefix = "C:/qgis"
else:
    qgis_prefix = "/usr"

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        import pp
        ppservers = ()
        if len(sys.argv) > 1:
            ncpus = int(sys.argv[1])
            self.job_server = pp.Server(ncpus, ppservers = ppservers, restart = True)
        else:
            self.job_server = pp.Server(ppservers=ppservers, restart = True)

        self.dirty = False
        self.projectName = None

        
        self.setWindowTitle("PopGen Version-1.0")
        self.setWindowIcon(QIcon("./images/popsyn.png"))
        self.workingWindow = QLabel()
        self.showMaximized()
        self.setMinimumSize(800,500)
        self.workingWindow.setAlignment(Qt.AlignCenter)
        bkground = QPixmap("./images/background.png")
        self.workingWindow.setPixmap(bkground)
        self.workingWindow.setScaledContents(True)
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
        #self.addActions(self.fileMenu, (projectNewAction, projectOpenAction, None, self.projectSaveAction, 
        #                                   self.projectSaveAsAction, None, self.projectCloseAction, None, applicationQuitAction))
        self.addActions(self.fileMenu, (projectNewAction, projectOpenAction, None, self.projectSaveAction, 
                                           None, self.projectCloseAction, None, applicationQuitAction))
# Adding actions to toolbar
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.setObjectName("FileToolBar")
        #self.addActions(self.fileToolBar, (projectNewAction, projectOpenAction, self.projectSaveAction, self.projectSaveAsAction))
        self.addActions(self.fileToolBar, (projectNewAction, projectOpenAction, self.projectSaveAsAction))
        

# DATA MENU 
# Defining menu/toolbar actions        
        dataSourceAction = self.createAction("Data Source &Connection", self.dataSource, 
                                             icon="datasource", tip="Enter MySQL connection settings.")
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
        setCorrespondenceAction = self.createAction("Set Corresponding Variables", self.synthesizerSetCorrBetVariables, 
                                                    icon="varcorr",
                                                    tip="""Select the variables and """
                                                    """set the correspondence map between the variables """
                                                    """in the sample file and variables in the control file.""")
        synthesizerParameterAction = self.createAction("&Parameters/Settings", self.synthesizerParameter,
                                                       icon="parameters",
                                                       tip="Set parameter values.")
        synthesizerRunAction = self.createAction("Run", self.synthesizerRun, 
                                                 icon="run", tip="Run synthesizer.")
        synthesizerStopAction = self.createAction("Stop", self.synthesizerStop, 
                                                  icon="stop", tip="Stop the current population synthesis run.")
# Adding actions to menu
        self.synthesizerMenu = self.menuBar().addMenu("&Synthesizer")
        #self.addActions(self.synthesizerMenu, (setCorrespondenceAction, 
        #                                       synthesizerParameterAction, None, 
        #                                       synthesizerRunAction, synthesizerStopAction))
        self.addActions(self.synthesizerMenu, (setCorrespondenceAction, 
                                               synthesizerParameterAction, None, 
                                               synthesizerRunAction))
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
        resultsRegionalAARDAction = self.createAction("Average Absolute Relative Difference (AARD)", 
                                                      self.resultsRegionalAARD, 
                                                      tip="""Display the distribution of Average Absolute Relative Difference (AARD) """
                                                      """across individual geographies.""")
        resultsRegionalPValueAction = self.createAction("p-Value", 
                                                        self.resultsRegionalPValue, 
                                                        tip="""Display the distribution of p-value """
                                                        """for the synthetic population across individual geographies.""")
        resultsRegionalHousDistAction = self.createAction("Distribution of Housing Variables", 
                                                          self.resultsRegionalHousDist, 
                                                          tip="Comparison of housing variables.")
        resultsRegionalPersDistAction = self.createAction("Distribution of Person Variables", 
                                                          self.resultsRegionalPersDist, 
                                                          tip="Comparison of person variables.")


        resultsRegionalAction = self.createAction("Regional Geography Statistics",
                                                  self.resultsRegional,
                                                  icon="region",
                                                  tip = "Display performance statistics for the entire region.")


        resultsIndividualAction = self.createAction("&Individual Geography Statistics",
                                                    self.resultsIndividual,
                                                    icon="individualgeo",
                                                    tip = "Display performance statistics for individual geographies.")

        resultsThematicAction = self.createAction("Thematic Maps",
                                                    self.resultsThematic,
                                                    icon="individualgeo",
                                                    tip = "Display thematic attribute maps.")

        resultsViewHHAction = self.createAction("&View Households",
                                                    self.resultsViewHH,
                                                    icon="viewhh",
                                                    tip = "Display synthesized households for the entire region.")

        resultsExportCSVAction = self.createAction("Into &CSV Format", 
                                                self.resultsCSVExport, 
                                                tip = "Export results into a comma-seperated file")

        resultsExportTabAction = self.createAction("Into &Tab-delimited Format", 
                                                self.resultsTabExport, 
                                                tip = "Export results into a tab-delimited file")

# Adding actions to menu
        self.resultsMenu = self.menuBar().addMenu("&Results")
        self.regionwideSubMenu = self.resultsMenu.addMenu(QIcon("images/region.png"),"Regional Statistics")
        self.addActions(self.regionwideSubMenu, (resultsRegionalAARDAction, resultsRegionalPValueAction,
                                                 resultsRegionalHousDistAction, resultsRegionalPersDistAction))
        
        self.addActions(self.resultsMenu, (resultsIndividualAction, resultsThematicAction))
        self.exportSubMenu = self.resultsMenu.addMenu(QIcon("images/export.png"), "&Export Results")
        self.addActions(self.exportSubMenu, (resultsExportCSVAction, resultsExportTabAction))


        #self.addActions(self.resultsMenu, (resultsViewHHAction,))
# Adding actions to toolbar

        #self.resultsToolBar = self.addToolBar("Results")
        #self.resultsToolBar.addToolBar(QIcon("Regional SubMenu"))
        #self.addActions(self.resultsToolBar, (resultsRegionalAction, resultsIndividualAction))

        self.resultsMenu.setDisabled(True)
        #self.resultsToolBar.setDisabled(True)


# HELP MENU
# Defining menu/toolbar actions


        helpDocumentationAction = self.createAction("Documentation",
                                                    self.showDocumentation, 
                                                    tip="Display the documentation of PopGen.", 
                                                    icon = "documentation")
        helpHelpAction = self.createAction("Help",
                                           self.showHelp, 
                                           tip="Quick reference for important parameters.",
                                           icon="help")

        helpAboutAction = self.createAction("About PopGen",
                                            self.showAbout, 
                                            tip="Display software information")

        dataHhldSample = self.createAction("Household Sample",
                                           self.showHhldSampleStruct,
                                           tip = "Data structure for the household sample file.")

        dataGQSample = self.createAction("Groupquarter Sample",
                                           self.showGQSampleStruct,
                                           tip = "Data structure for the groupquarter sample file.")

        dataPersonSample = self.createAction("Person Sample",
                                           self.showPersonSampleStruct,
                                           tip = "Data structure for the person sample file.")

        dataHhldMarginals = self.createAction("Household Marginals",
                                           self.showHhldMarginalsStruct,
                                           tip = "Data structure for the household marginals file.")

        dataGQMarginals = self.createAction("Groupquarter Marginals",
                                           self.showGQMarginalsStruct,
                                           tip = "Data structure for the groupquarter marginals file.")

        dataPersonMarginals = self.createAction("Person Marginals",
                                           self.showPersonMarginalsStruct,
                                           tip = "Data structure for the person marginals file.")

        dataGeocorr = self.createAction("Geographic Correspondence",
                                           self.showGeocorrStruct,
                                           tip = "Data structure for the geographic correspondence file.")

        resHousingSyn = self.createAction("Housing Synthetic Data",
                                           self.showHousingSyn,
                                           tip = "Data structure for the housing synthetic data file.")

        resPersonSyn = self.createAction("Person Synthetic Data",
                                           self.showPersonSyn,
                                           tip = "Data structure for the person synthetic data file.")









        self.helpMenu = self.menuBar().addMenu("&Help")

        self.helpDataTemplateSubMenu = self.helpMenu.addMenu(QIcon("images/structure.png"), "&Data Structures")

        self.addActions(self.helpDataTemplateSubMenu, (dataHhldSample, dataGQSample, dataPersonSample, None,
                                                       dataHhldMarginals, dataGQMarginals, dataPersonMarginals,
                                                       None, dataGeocorr, None, resHousingSyn, resPersonSyn))


        #self.addActions(self.helpMenu, (None, helpDocumentationAction, helpHelpAction, None, helpAboutAction))
        self.addActions(self.helpMenu, (None, helpDocumentationAction, None, helpAboutAction))




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
            self.setWindowTitle("PopGen: Version-1.0 %s*" %self.project.name)
        else:
            self.setWindowTitle("PopGen: Version-1.0 %s" %self.project.name)
            


# Defining all the slots and supporting methods

    def projectNew(self):
        if not self.fileManager.isEnabled():
            self.runWizard()
        else:
            reply = QMessageBox.question(None, "Project Setup Wizard",
                                         QString("""A PopGen project already open. Would you like to continue?"""),
                                         QMessageBox.Yes| QMessageBox.No)
            if reply == QMessageBox.Yes:
                save = QMessageBox.question(None, "Project Setup Wizard",
                                            QString("""Would you like to save the project?"""),
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
            self.setWindowTitle("PopGen: Version-1.0 (%s)" %(self.project.filename))
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
        #self.resultsToolBar.setEnabled(option)

    def projectOpen(self):
        project = OpenProject()

        if not project.file.isEmpty():
            if self.fileManager.isEnabled():
                reply = QMessageBox.warning(None, "Open Existing Project",
                                            QString("""A PopGen project already open. Would you like to continue?"""),
                                            QMessageBox.Yes| QMessageBox.No)
                if reply == QMessageBox.Yes:
                    save = QMessageBox.warning(None, "Save Existing Project",
                                               QString("""Would you like to save the project?"""),
                                               QMessageBox.Yes| QMessageBox.No)
                    if save == QMessageBox.Yes:
                        SaveProject(self.project)
                    with open(project.file, 'rb') as f:
                        self.project = pickle.load(f)
                        self.setWindowTitle("PopGen: Version-1.0 (%s)" %self.project.filename)
                        self.fileManager.project = self.project
                        self.fileManager.populate()
                        self.enableFunctions(True)
                        #PopulateFileManager(self.project, self.fileManager)

            else:
                with open(project.file, 'rb') as f:
                    self.project = pickle.load(f)
                    self.setWindowTitle("PopGen: Version-1.0 (%s)" %self.project.filename)
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
            reply = QMessageBox.warning(self, "Save Existing Project As...",
                                        QString("""Would you like to continue?"""), 
                                        QMessageBox.Yes| QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.project.filename = filename
                self.project.save()
                self.setWindowTitle("PopGen: Version-1.0 (%s)" %self.project.filename)

    
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
        reqTables = ['hhld_sample', 'hhld_sample', 'person_marginals', 'person_sample']
        if self.checkIfTablesExist(reqTables):
            vars = SetCorrDialog(self.project)
            if vars.exec_():
                self.project = vars.project
                self.project.save()
                self.fileManager.populate()
        else:
            QMessageBox.warning(self, "Synthesizer", "Import and process tables before setting variable correspondence.", QMessageBox.Ok)

    def checkIfTablesExist(self, reqTables):

        tables = self.tableList()

        #print tables

        for i in reqTables:
            try:
                tables.index(i)
            except:
                return False
        return True
         
            
    def tableList(self):
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()
        self.query = QSqlQuery(self.projectDBC.dbc)

        tables = []

        if not self.query.exec_("""show tables"""):
            raise FileError, self.query.lastError.text()
        while self.query.next():
            tables.append('%s' %self.query.value(0).toString())
        self.projectDBC.dbc.close()
        return tables
    


    def synthesizerParameter(self):
        parameters = ParametersDialog(self.project)
        if parameters.exec_():
            self.project.save()

    def synthesizerRun(self):
        filename = '%s/%s/%s.pop' %(self.project.location, self.project.name, self.project.filename)
        with open(filename, 'rb') as f:
            self.project = pickle.load(f)

        if len(self.project.selVariableDicts.hhld) > 0 and len(self.project.selVariableDicts.person) > 0:
            runDia = RunDialog(self.project, self.job_server)
            runDia.exec_()
            self.fileManager.populate()
            self.project.save()
        else:
            QMessageBox.warning(self, "Synthesizer", "Define variable correspondence before synthesizing population.", QMessageBox.Ok)

        #for i in self.project.synGeoIds:
        #    print i


        
    def synthesizerStop(self):
        QMessageBox.information(self, "Synthesizer", "Stop the synthesizer", QMessageBox.Ok)

    def resultsRegionalAARD(self):
        aard = Absreldiff(self.project)
        if aard.valid:
            aard.exec_()
    def resultsRegionalPValue(self):
        pval = Pval(self.project)
        if pval.valid:
            pval.exec_()  
    def resultsRegionalHousDist(self):
        hhdist = Hhdist(self.project)
        if hhdist.valid:
            hhdist.exec_()
    def resultsRegionalPersDist(self):
        ppdist = Ppdist(self.project)
        if ppdist.valid:
            ppdist.exec_()    
        
    def resultsRegional(self):
        QMessageBox.information(self, "Results", "Regional Performance Statistics", QMessageBox.Ok)
    
    def resultsIndividual(self):
        #res = ResultsGen(self.project)
        indgeo = Indgeo(self.project)
        if indgeo.valid:
            indgeo.exec_()    
            
    def resultsThematic(self):
        #res = ResultsGen(self.project)
        thamp = Thmap(self.project)
        if thamp.valid:
            thamp.exec_()   
            
    def resultsViewHH(self):
        res = Hhmap(self.project)
        res.exec_()
        
    def resultsCSVExport(self):
        reqTables = ['housing_synthetic_data', 'person_synthetic_data']
        if self.checkIfTablesExist(reqTables):
            fileDlg = SaveFile(self.project, "csv")
        else:
            QMessageBox.warning(self, "Synthesizer", "Run synthesizer before exporting results.", 
                                QMessageBox.Ok)

    def resultsTabExport(self):
        reqTables = ['housing_synthetic_data', 'person_synthetic_data']
        if self.checkIfTablesExist(reqTables):
            fileDlg = SaveFile(self.project, "dat")
        else:
            QMessageBox.warning(self, "Synthesizer", "Run synthesizer before exporting results.", 
                                QMessageBox.Ok)

    def showHhldSampleStruct(self):
        headers = ['state', 'pumano', 'hhid', 'serialno', '<householdvariable1>', 
                   '<householdvariable2>', '...']
        data = self.returnData(headers)
        a = DisplayTableStructure(data, headers, 'Data structure for household sample file', 
                                  """If you would like to provide your own data, """
                                  """use the above data structure for the <b>household sample file</b>. """
                                  """In the <b>variable type</b> row, use keyword <b>bigint</b> for integer variables, """
                                  """keyword <b>float</b> or <b>double</b> for floating point variables, """
                                  """and keyword <b>text</b> for string variables.""")
        a.exec_()

    def showGQSampleStruct(self):
        headers = ['state', 'pumano', 'hhid', 'serialno', '<groupquartervariable1>', 
                   '<groupquartervariable2>', '...']
        data = self.returnData(headers)
        a = DisplayTableStructure(data, headers, 'Data structure for groupquarter sample file', 
                                  """If you would like to provide your own data, """
                                  """use the above data structure for the <b>groupquarter sample file</b>. """
                                  """In the <b>variable type</b> row, use keyword <b>bigint</b> for integer variables, """
                                  """keyword <b>float</b> or <b>double</b> for floating point variables, """
                                  """and keyword <b>text</b> for string variables.""")

        a.exec_()

    def showPersonSampleStruct(self):
        headers = ['state', 'pumano', 'hhid', 'serialno', 'pnum', '<personvariable1>', 
                   '<personvariable2>', '...']

        data = self.returnData(headers)
        a = DisplayTableStructure(data, headers, 'Data structure for person sample file', 
                                  """If you would like to provide your own data, """
                                  """use the above data structure for the <b>person sample file</b>. """
                                  """In the <b>variable type</b> row, use keyword <b>bigint</b> for integer variables, """
                                  """keyword <b>float</b> or <b>double</b> for floating point variables, """
                                  """and keyword <b>text</b> for string variables.""")

        a.exec_()

    def showHhldMarginalsStruct(self):
        headers = ['state', 'county', 'tract', 'bg', '<householdvariable1category1>', '<householdvariable1category2>', 
                   '...', '<householdvariable2category1>', '...']
        data = self.returnData(headers)
        a = DisplayTableStructure(data, headers, 'Data structure for household marginals file', 
                                  """If you would like to provide your own data, """
                                  """use the above data structure for the <b>household marginals file</b>. """
                                  """In the <b>variable type</b> row, use keyword <b>bigint</b> for integer variables, """
                                  """keyword <b>float</b> or <b>double</b> for floating point variables, """
                                  """and keyword <b>text</b> for string variables.""")

        a.exec_()

    def showGQMarginalsStruct(self):
        headers = ['state', 'county', 'tract', 'bg', '<groupquartervariable1category1>', '<groupquartervariable1category2>', 
                   '...', '<groupquartervariable2category1>', '...']
        data = self.returnData(headers)
        a = DisplayTableStructure(data, headers, 'Data structure for groupquarter marginals file', 
                                  """If you would like to provide your own data, """
                                  """use the above data structure for the <b>groupquarter marginals file</b>. """
                                  """In the <b>variable type</b> row, use keyword <b>bigint</b> for integer variables, """
                                  """keyword <b>float</b> or <b>double</b> for floating point variables, """
                                  """and keyword <b>text</b> for string variables.""")

        a.exec_()

    def showPersonMarginalsStruct(self):
        headers = ['state', 'county', 'tract', 'bg', '<personvariable1category1>', '<personvariable1category2>', 
                   '...', '<personvariable2category1>', '...']
        data = self.returnData(headers)
        a = DisplayTableStructure(data, headers, 'Data structure for person marginals file', 
                                  """If you would like to provide your own data, """
                                  """use the above data structure for the <b>person marginals file</b>. """
                                  """In the <b>variable type</b> row, use keyword <b>bigint</b> for integer variables, """
                                  """keyword <b>float</b> or <b>double</b> for floating point variables, """
                                  """and keyword <b>text</b> for string variables.""")

        a.exec_()

    def showGeocorrStruct(self):
        headers = ['county', 'tract', 'bg','state', 'pumano', 'stateabb', 
                   'countyname']
        data = self.returnData(headers)
        a = DisplayTableStructure(data, headers, 'Data structure for geographic correspondence file', 
                                  """If you would like to provide your own data, """
                                  """use the above data structure for the <b>geographic correspondence file</b>. """
                                  """In the <b>variable type</b> row, use keyword <b>bigint</b> for integer variables, """
                                  """keyword <b>float</b> or <b>double</b> for floating point variables, """
                                  """and keyword <b>text</b> for string variables.""")

        a.exec_()


    def showHousingSyn(self):
        headers = ['state', 'county', 'tract', 'bg','hhid', 'serialno', 'frequency', 'hhuniqueid']
        data = self.returnData(headers, varTypes=False)
        a = DisplayTableStructure(data, headers, 'Data structure for synthetic housing file',
                                  "Layout of the data in the housing synthetic data file.")

        a.exec_()


    def showPersonSyn(self):
        headers = ['state', 'county', 'tract', 'bg','hhid', 'serialno', 'pnum', 'frequency', 'personuniqueid']
        data = self.returnData(headers, varTypes=False)
        a = DisplayTableStructure(data, headers, 'Data structure for synthetic person file',
                                  "Layout of the data in the person synthetic data file.") 

        a.exec_()

    
    def returnData(self, headers, varTypes=True):
        data = []
        if varTypes:
            data.append(['<variable type>']*len(headers))
        for i in range(4):
            data.append(['value']*len(headers))
        return data

    
    def showDocumentation(self):
        form = HelpForm("index.html", self)
        form.show()
        #QMessageBox.information(self, "Help", "Documentation", QMessageBox.Ok)

    def showHelp(self):
        QMessageBox.information(self, "Help", "Help", QMessageBox.Ok)

    def showAbout(self):
        aboutdialog = QDialog()
        aboutlabel = QLabel()
        pixmap = QPixmap()
        pixmap.load("./images/splashscreen.png")
        aboutlabel.setPixmap(pixmap)
        layout = QHBoxLayout()
        layout.addWidget(aboutlabel)
        aboutdialog.setLayout(layout)
        aboutdialog.setWindowTitle("About")
        aboutdialog.exec_()
        
        #QMessageBox.information(self, "Help", "About", QMessageBox.Ok)

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
    pixmap = QPixmap("./images/splashscreen.png")
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.show()
    splash.showMessage("Starting PopGen 1.0 ...", Qt.AlignRight| Qt.AlignBottom, Qt.yellow)
    app.processEvents()
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
    app.setApplicationName("Population Generator (PopGen)")
    form = MainWindow()
    form.show()
    
    splash.finish(form)

    app.exec_()



if __name__=="__main__":
    main()
