from PyQt4.QtCore import *
from PyQt4.QtGui import *
from collections import defaultdict

from zipfile import ZipFile
import os

class UnzipFile:
    def __init__(self, mountpoint, file):
        self.mountpoint = mountpoint

        self.mountpoint = os.path.realpath(self.mountpoint)
        self.mountpoint = self.mountpoint.replace("\\", "/")

        self.filename = os.path.join(self.mountpoint, file)

    def unzip(self):
        zipObject = ZipFile(self.filename)
        
        archFiles = zipObject.namelist()

        for i in archFiles:
            fileArchInfo = zipObject.getinfo(i)
            try:
                fileExtrInfo = os.stat(os.path.join(self.mountpoint, i))
                reply = QMessageBox.question(None, "PopGen: Extracting Data",
                                             QString("""Do you like to replace the existing file %s (size %s)"""
                                                     """ with the file %s (size %s) from the zip folder?""" 
                                             %(i, fileExtrInfo.st_size, i, fileArchInfo.file_size)), 
                                             QMessageBox.Yes| QMessageBox.YesToAll|
                                             QMessageBox.No| QMessageBox.NoToAll)
                if reply == QMessageBox.Yes:
                    zipObject.extract(fileArchInfo, self.mountpoint)
                if reply == QMessageBox.YesToAll:
                    index = archFiles.index(i)
                    for j in archFiles[index:]:
                        fileArchInfo = zipObject.getinfo(j)
                        zipObject.extract(fileArchInfo, self.mountpoint)
                    break

                if reply == QMessageBox.NoToAll:
                    break

            except Exception, e:
                zipObject.extract(fileArchInfo, self.mountpoint)



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    a = UnzipFile('C:\\PopGen\\data\\California\\PUMS', 'all_California.zip')
    a.unzip()




