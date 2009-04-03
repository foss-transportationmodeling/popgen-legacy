import zipfile
import os

class UnzipFile():
    def __init__(self, mountpoint, filename):
        self.mountpoint = mountpoint
        self.file = zipfile.ZipFile("%s/%s"%(self.mountpoint, filename), "r")

    def unzip(self):
        for i in self.file.namelist():
            try:
                os.makedirs(os.path.join(self.mountpoint, os.path.dirname(i)))
            except OSError:
                pass
            if i[-1]!="?":
                outputfile = open(os.path.join(self.mountpoint, i), 'w')
                outputfile.write(self.file.read(i))
                outputfile.close()

if __name__=="__main__":
    pass
