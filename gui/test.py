
from __future__ import with_statement

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from mainwindow import MainWindow
"""
def main():
    app = QApplication(sys.argv)
    pixmap = QPixmap("./images/splashscreen.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    app.processEvents()

    raw_input()

    main1 = MainWindow()
    main1.show()
    splash.finish(main1)
    return app.exec_()
"""


def fileRead():
    with open('c:\PopSim\data\California\PUMS\PUMS5_06.TXT', 'r') as f:
        with open('c:\PopSim\data\California\PUMS\Housing.text', 'w') as fhousing:
            with open('c:\PopSim\data\California\PUMS\Person.text', 'w') as fperson:
                    n = 0
                    for i in f:
                        rectype = i[0:1]
                        if rectype == 'H':
                            a = hparse(i)
                            fhousing.write(str(a))
                        else:
                            b = pparse(i)
                            fperson.write(str(b))
                        n = n+ 1


        print 'Total number of records:',n


def hparse(i):
    SERIALNO = i[1:8]
    STATE = i[9:11]
    PUMA5 = i[13:18]
    HWEIGHT = i[101:105]
    PERSONS = i[105:107]
    UNITTYPE = i[107:108]
    HHT = i[212:213]
    NOC = i[219:221]
    HINC = i[250:258]
    a = (SERIALNO, STATE, PUMA5, HWEIGHT, PERSONS, UNITTYPE, HHT, NOC, HINC)
    return a

def pparse(i):
    SERIALNO = i[1:8]
    PNUM = i[8:10]
    PWEIGHT = i[12:16]
    SEX = i[22:23]
    AGE = i[24:26]
    RACE1 = i[37:38]
    ESR = i[153:154]

    b = (SERIALNO, PNUM, PWEIGHT, SEX, AGE, RACE1, ESR)
    return b

if __name__ == "__main__":
    #main()
    import time
    ti = time.time()
    fileRead()
    print "Time elapsed - %.4f" %(time.time()-ti)
