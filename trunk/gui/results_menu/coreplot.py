"""
This demo demonstrates how to embed a matplotlib (mpl) plot
into a PyQt4 GUI application, including:

* Using the navigation toolbar
* Adding data to the plot
* Dynamically modifying the plot's properties
* Processing mpl events
* Saving the plot to a file from a menu

The main goal is to serve as a basis for developing rich PyQt GUI
applications featuring mpl plots (using the mpl OO API).

Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 19.01.2009
"""
import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from misc.errors import FileError
from database.createDBConnection import createDBC

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure


class Matplot(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setMinimumSize(QSize(1000,500))
        # Create the mpl Figure and FigCanvas objects.
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        # Since we have only one plot, we can use add_axes
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)

        self.vbox = QVBoxLayout()

    def on_draw(self):
        pass

    def create_action(  self, text, slot=None, shortcut=None,
                        icon=None, tip=None, checkable=False,
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
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

    def executeSelectQuery(self, vars, tablename, filter="", group =""):
        query = QSqlQuery(self.projectDBC.dbc)
        if filter != "" and group != "":
            if not query.exec_("""SELECT %s FROM %s WHERE %s GROUP BY %s"""%(vars,tablename,filter,group)):
                raise FileError, query.lastError().text()
        elif filter != "" and group == "":
            if not query.exec_("""SELECT %s FROM %s WHERE %s"""%(vars,tablename,filter)):
                raise FileError, query.lastError().text()
        elif filter == "" and group != "":
            if not query.exec_("""SELECT %s FROM %s GROUP BY %s"""%(vars,tablename,group)):
                raise FileError, query.lastError().text()
        else:
            if not query.exec_("""SELECT %s FROM %s"""%(vars,tablename)):
                raise FileError, query.lastError().text()
        return query


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
