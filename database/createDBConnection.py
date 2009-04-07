from PyQt4.QtSql import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from gui.file_menu.newproject import DBInfo

class createDBC(object):
    def __init__(self, db, name=None):
        super(createDBC, self).__init__()
        self.dbc = QSqlDatabase.addDatabase(db.driver)
        self.dbc.setHostName(db.hostname)
        self.dbc.setUserName(db.username)
        self.dbc.setPassword(db.password)
        if name is not None:
            self.dbc.setDatabaseName(name)


def main():
    app = QApplication(sys.argv)

    db = DBInfo("ewrwrwe", "root", "1234")
    a = createDBC(db, "nth")

    
    try:
        if not a.dbc.open():
            QMessageBox.warning(None, "oisdf", 
                                QString("Database Error: %1").arg(a.dbc.lastError().text()))
            sys.exit(1)
            a.dbc.close()
        else:
            QMessageBox.warning(None, "oisdf", 
                                QString("Found"))
            a.dbc.close()
    except Exception, e:
        print "Error: %s" %e

    


if __name__=="__main__":
    main()


        
        
        
