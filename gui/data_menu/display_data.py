from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from database.createDBConnection import createDBC
from gui.file_menu.newproject import DBInfo

class DisplayTable(QObject):
    def __init__(self, tablename, parent=None):
        super(DisplayTable, self).__init__(parent)

        self.model = QSqlTableModel()
        self.model.setTable(tablename)
        self.model.select()

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setFixedSize(QSize(800, 500))
        #self.view.showFullScreen()


class ModifyData(QDialog):
    def __init__(self, parent=None):
        super(ModifyData, self).__init__(parent)
        
        self.setFixedSize(900, 600)
        self.setTitle("Modify table %s" %(tablename))

        self.ediLabel = QLabel("Enter your SQL modifying commands here")
        self.commandTextEdit = QTextEdit()

        #self.dialogButtonBox = QDialogButtonBox( 


def main():
    app = QApplication(sys.argv)

    db = DBInfo("localhost", "root", "1234")
    a = createDBC(db, "first")


    try:
        if not a.dbc.open():
            QMessageBox.warning(None, "oisdf",
                                QString("Database Error: %1").arg(a.dbc.lastError().text()))
            sys.exit(1)

        else:
            pass
            #QMessageBox.warning(None, "oisdf",
            #                    QString("Found"))

    except Exception, e:
        print "Error: %s" %e

    display = DisplayTable("hhld_marginals")
    display.view.show()

    """
    model = QSqlTableModel()
    print model.database().databaseName()
    model.setTable("hhld_marginals")
    #model.setFilter("i>0")
    model.select()

    #print model.record(0).value("i").toString()




    view = QTableView()
    view.setModel(model)
    view.show()
    """
    a.dbc.close()
 
    app.exec_()

if __name__ == "__main__":
    import sys
    main()

