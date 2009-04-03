from PyQt4.QtCore import *
from PyQt4.QtGui import *
import re
from misc.errors import *

class QWizardValidatePage(QWizardPage):
    def __init__(self, complete=False, parent=None):
        super(QWizardValidatePage, self).__init__(parent)
        self.complete = complete

    def isComplete(self):
        if self.complete:
            return True
        else:
            return False

class ComboBoxFolder(QComboBox):
    def __init__(self, parent=None):
        super(ComboBoxFolder, self).__init__(parent)

    def browseFolder(self, index):
        if index  == self.count()-1:
            location = QFileDialog.getExistingDirectory(self, QString("Project Location"), "/home", QFileDialog.ShowDirsOnly)
            if not location.isEmpty():
                indexOfFolder = self.isPresent(location)
                if indexOfFolder is None:
                    self.insertItem(0, QString(location))
                    self.setCurrentIndex(0)
                else:
                    self.setCurrentIndex(indexOfFolder)
            else:
                self.setCurrentIndex(0)

    def isPresent(self, location):
        for i in range(self.count()):
            if location == self.itemText(i):
                return i
        return None        

class ComboBoxFile(QComboBox):
    def __init__(self, parent=None):
        super(ComboBoxFile, self).__init__(parent)

    def browseFile(self, index):
        if index == self.count()-1:
            file = QFileDialog.getOpenFileName(self, QString("Browse to select file"), "/home", "Data Files (*.dat *.txt *.csv)")
            if not file.isEmpty():
                indexOfFile = self.isPresent(file)
                if indexOfFile is None:
                    self.insertItem(1, QString(file))
                    self.setCurrentIndex(1)
                else:
                    self.setCurrentIndex(indexOfFile)
            else:
                self.setCurrentIndex(0)

    def isPresent(self, file):
        for i in range(self.count()):
            if file == self.itemText(i):
                return i
        return None
                
    def findAndSet(self, text):
        for i in range(self.count()):
            if self.itemText(i) == ('%s' %text):
                self.setCurrentIndex(i)
                return True
        else:
            return False


class DisplayLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(DisplayLineEdit, self).__init__(parent)
        self.setEnabled(False)


class LineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)

    def check(self, text):
        text = self.text()
        try:
            if len(text) == 0:
                raise TextError, "Enter a non-empty string"
            if not re.match("[A-Za-z]",text[0]):
                text = text[1:]
                raise TextError, "First character has to be a alphabet"
            
            for i in text[1:]:
                if not re.match("[A-Za-z_0-9]", i):
                    text.replace(i, '')
                    raise TextError, "Project name can only comprise of alphabets and an underscore (_)"
        except TextError, e:
            QMessageBox.information(self, "PopSim: New Project Wizard", 
                                    "%s" %e, 
                                    QMessageBox.Ok)
            self.setText(text)
            self.selectAll()
            self.setFocus()
        return True
            


class Separator(QFrame):
    def __init__(self, parent=None):
        super(Separator, self).__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
