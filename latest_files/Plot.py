from math import sqrt


class Plot:
    def __init__(self, centreBlock, radius):
        self.centreBlock = centreBlock
        self.radius = radius


    def getX(self):
        return self.centreBlock.x

    def getY(self):
        return self.centreBlock.y

    def getZ(self):
        return self.centreBlock.z


    def setElevationStd(self, elevationStd):
        if elevationStd is None:  # calcElevationStd returns none if the plot contains water
            self.containsWater = True
            self.elevationStd = 999
        else:
            self.containsWater = False    
            self.elevationStd = elevationStd


    # arbitrary value used to calculate plot potential - distance from the town centre
    def calculateDistanceRating(self, townCentreCoords):
        (townX, townY, townZ) = townCentreCoords
        distance = sqrt(abs(self.getX() - townX) ** 2 + abs(self.getZ() - townZ) ** 2)
        self.distanceRating = 5 * (distance ** 2) / (100 ** 2)  # hard code 100 radius for now, seems to work well = 45 block dist is as bad as 1 elevation std


    # arbitrary value used to calculate plot potential - height distance from the town centre
    def calculateHeightRating(self,  townCentreCoords):
        townY = townCentreCoords[1]
        self.heightRating = abs(self.getY() - townY) ** 2 / 100  # 10 block dif is as bad as 1 elevation std


    def calculateOverallRating(self, elevationWeighting, distanceWeighting, heightWeighting):
        if elevationWeighting + distanceWeighting + heightWeighting != 1:
            print("All weights have to add up to 1.")
            self.overallRating = 999
        else:
            self.overallRating = elevationWeighting * self.elevationRating + distanceWeighting * self.distanceRating + self.heightRating * self.heightRating


    # refer to docs for justification behind this calc
    def calculateElevationRating(self):
        self.elevationRating = (self.elevationStd + 0.5) ** 2