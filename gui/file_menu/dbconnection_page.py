from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import sys

from misc.widgets import *
from misc.errors import *
from database.createDBConnection import createDBC
from newproject import DBInfo

class DBConnectionPage(QWizardPage):
    def __init__(self, parent=None):
        super(DBConnectionPage, self).__init__(parent)

        self.connectionDummy = False

        self.setTitle("Step 5: MySQL Connection Settings")

        hostnameLabel = QLabel("Hostname")
        self.hostnameLineEdit = LineEdit()
        #self.hostnameLineEdit.setText("Enter a MYSQL hostname to connect to")
        self.hostnameLineEdit.setText("localhost")
        self.hostnameLineEdit.selectAll()
        hostnameLabel.setBuddy(self.hostnameLineEdit)
        hostnameHLayout = QHBoxLayout()
        hostnameHLayout.addWidget(hostnameLabel)
        hostnameHLayout.addWidget(self.hostnameLineEdit)

        usernameLabel = QLabel("Username")
        self.usernameLineEdit = LineEdit()
        #self.usernameLineEdit.setText("Enter username for the MYSQL account")
        self.usernameLineEdit.setText("root")
        usernameLabel.setBuddy(self.usernameLineEdit)
        usernameHLayout = QHBoxLayout()
        usernameHLayout.addWidget(usernameLabel)
        usernameHLayout.addWidget(self.usernameLineEdit)

        passwordLabel = QLabel("Password")
        self.passwordLineEdit = LineEdit()
        self.passwordLineEdit.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        #self.passwordLineEdit.setText("Password")
        self.passwordLineEdit.setText("1234")
        passwordLabel.setBuddy(self.passwordLineEdit)
        passwordHLayout = QHBoxLayout()
        passwordHLayout.addWidget(passwordLabel)
        passwordHLayout.addWidget(self.passwordLineEdit)

        vLayout = QVBoxLayout()
        vLayout.addLayout(hostnameHLayout)
        vLayout.addLayout(usernameHLayout)
        vLayout.addLayout(passwordHLayout)
        self.setLayout(vLayout)

        self.connect(self.hostnameLineEdit, SIGNAL("editingFinished()"), self.hostnameCheck)
        self.connect(self.usernameLineEdit, SIGNAL("editingFinished()"), self.usernameCheck)
        self.connect(self.passwordLineEdit, SIGNAL("editingFinished()"), self.passwordCheck)
        self.connect(self, SIGNAL("checkCredentials()"), self.check)

    def hostnameCheck(self):
        text = self.hostnameLineEdit.text()
        self.hostnameDummy = self.hostnameLineEdit.check(text)
        self.emit(SIGNAL("checkCredentials()"))

    def usernameCheck(self):
        text = self.usernameLineEdit.text()
        self.usernameDummy = self.usernameLineEdit.check(text)
        self.emit(SIGNAL("checkCredentials()"))


    def passwordCheck(self):
        self.emit(SIGNAL("checkCredentials()"))

    def check(self):
        db = DBInfo(self.hostnameLineEdit.text(),
                    self.usernameLineEdit.text(),
                    self.passwordLineEdit.text())
                    
        try:
            dbconnection = createDBC(db)
            if not dbconnection.dbc.open():
                raise FileError, dbconnection.dbc.lastError().text()
            
            self.connectionDummy = True
            dbconnection.dbc.close()
        except Exception, e:
            dbconnection.dbc.close()
            self.connectionDummy = False

        self.emit(SIGNAL("completeChanged()"))
        
    def isComplete(self):
        validate = self.connectionDummy
        
        

        if validate:
            return True
        else:
            return False
        

