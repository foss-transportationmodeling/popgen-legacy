from __future__ import with_statement

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import pickle


class OpenProject(QFileDialog):
    def __init__(self, parent=None):
        super(OpenProject, self).__init__(parent)
        self.file = self.getOpenFileName(parent, "Browse to select file", "/home",
                                         "PopGen File (*.pop)")
        

        
            

            
    



