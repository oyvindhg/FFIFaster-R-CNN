class ImageObject():

    def __init__(self, name, Xmin, Ymin, Xmax, Ymax):
        self.name = name
        self.Xmin = Xmin
        self.Ymin = Ymin
        self.Xmax = Xmax
        self.Ymax = Ymax

    def getName(self):
        return self.name
    def getXmin(self):
        return self.Xmin
    def getYmin(self):
        return self.Ymin
    def getXmax(self):
        return self.Xmax
    def getYmax(self):
        return self.Ymax