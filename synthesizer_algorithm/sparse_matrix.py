

class SparseMatrix():
    def __init__(self, project):
        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.db.open()

        


    def PopulateMasterMatrix(self, 
        
