from math import sqrt
import statistics
import time
from mcpi.minecraft import Minecraft
from mcpi import block


# DEFINITIONS:
# radius = we are working with square plots, so a radius is the amount of blocks from the middle block to the edge block
# zone = user-defined box boundary containing plots
# square = a single square within a zone/one column of blocks


class Block:
    def __init__(self, x, y, z, id):
        self.x = x
        self.y = y
        self.z = z
        self.id = id

    def info(self):
        print(f"Block: ({self.x}, {self.y}, {self.z}) - ID: {self.id}")


class Plot:
    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius


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
        distance = sqrt(abs(self.x - townX) ** 2 + abs(self.z - townZ) ** 2)
        self.distanceRating = 5 * (distance ** 2) / (100 ** 2)  # hard code 100 radius for now, seems to work well = 45 block dist is as bad as 1 elevation std


    # arbitrary value used to calculate plot potential - height distance from the town centre
    def calculateHeightRating(self,  townCentreCoords):
        townY = townCentreCoords[1]
        self.heightRating = abs(self.y - townY) ** 2 / 100  # 10 block dif is as bad as 1 elevation std


    def calculateOverallRating(self, elevationWeighting, distanceWeighting, heightWeighting):
        if elevationWeighting + distanceWeighting + heightWeighting != 1:
            print("All weights have to add up to 1.")
            self.overallRating = 999
        else:
            self.overallRating = elevationWeighting * self.elevationRating + distanceWeighting * self.distanceRating + self.heightRating * self.heightRating


    # refer to docs for justification behind this calc
    def calculateElevationRating(self):
        self.elevationRating = (self.elevationStd + 0.5) ** 2



class Zone:
    def __init__(self, mcApi, startCoord, endCoord, startHeight):  
        self.mcApi = mcApi  # is this how we should be passing the mcApi object?
        self.startCoord = startCoord  # (x, y, z)
        self.endCoord= endCoord  # (x, y, z)
        self.xSize = abs(startCoord[0] - endCoord[0]) + 1
        self.ySize = abs(startCoord[1] - endCoord[1]) + 1
        self.zSize = abs(startCoord[2] - endCoord[2]) + 1
        print("pullZoneBlocks: pulling all blocks from cuboid in start and end coords -", startCoord, endCoord)
        self.zoneBlocks = self.pullZoneBlocks(startCoord, endCoord)
        print("Successfully pulled zone blocks.")
        print("calculateSurfaceBlocks: calculating surface blocks from startHeight -", startHeight)
        self.calculateSurfaceBlocks(startHeight)
        print("Successfully calculated the zone's surface blocks.")


    # (modified version for efficiency)
    # Generates 3d matrix of all blocks within cuboid.
    # Ordered by Y, then X, then Z (due to how mc.getBlocks returns blocks)
    # each block is represented by tuple of (x, y, z, blockID)
    def pullZoneBlocks(self, startCoord, endCoord):
        (x0, y0, z0) = startCoord
        (x1, y1, z1) = endCoord

        blockIds = self.mcApi.getBlocks(x0, y0, z0, x1, y1, z1)
        blockIds = list(blockIds)

        zoneBlocks = {}
        for y in range(y1, y0-1, -1):
            y_square = {}
            for x in range(x1, x0-1, -1):
                x_row = {}
                for z in range(z1, z0-1, -1):
                    newBlock = Block(x, y, z, blockIds.pop())
                    x_row[z] = newBlock
                y_square[x] = x_row
            zoneBlocks[y] = y_square

        return zoneBlocks


    def isGroundBlock(self, blockId):
        # auto-return false on air
        if blockId == 0:
            return False
        
        groundBlockIds = [
            block.WATER.id,
            block.WATER_STATIONARY.id,
            block.STONE.id,
            block.GRASS.id,
            block.DIRT.id,
            block.COBBLESTONE.id,
            block.SAND.id,
            block.GRAVEL.id,
            block.SANDSTONE.id,
            block.ICE.id,
            block.SNOW_BLOCK.id,
            block.CLAY.id,
            block.COAL_ORE.id,
            block.IRON_ORE.id,
        ]

        for groundBlockId in groundBlockIds:
            if blockId == groundBlockId:
                return True

        return False
        
        


    # Uses zoneblocks (3d matrix of blocks - ordered by Y, X, Z)
    # startHeight describes the y coord at which the function starts searching down for the first non-air block
    # Sets surfaceBlocks to 2d matrix ordered by X, Z, containing the block on the surface of that SQUARE
    # TODO: ignore trees and other non-ground structures
    # TODO: ignore water
    def calculateSurfaceBlocks(self, startHeight):
        zoneBlocks = self.zoneBlocks
        surfaceBlocks = {}

        zoneMinX = min(self.startCoord[0], self.endCoord[0])
        zoneMinY = min(self.startCoord[1], self.endCoord[1])
        zoneMinZ = min(self.startCoord[2], self.endCoord[2])

        for x in range(zoneMinX, zoneMinX + self.xSize):
            x_row = {}
            for z in range(zoneMinZ, zoneMinZ + self.zSize):
                y = startHeight
                while y > zoneMinY and not self.isGroundBlock(zoneBlocks[y][x][z].id):  # keep checking if that squares block id is AIR
                    y -= 1

                surfaceBlock = zoneBlocks[y][x][z]
                x_row[z] = surfaceBlock
            surfaceBlocks[x] = x_row

        self.surfaceBlocks = surfaceBlocks


    # due to the way mc.getBlocks works, zoneBlocks are sorted by y, x then z
    # use getBlock method to retrieve blocks from the zone sorted by x, y, then z which is more intuitive
    def getBlock(self, x, y, z):
        return self.zoneBlocks[y][x][z]


    def getSurfaceBlock(self, x, z):
        return self.surfaceBlocks[x][z]
    

    def calculateElevationStd(self, x, z, maxPlotRadius):
        surroundingBlockHeights = []
        plotContainsWater = False
        
        for i in range(-maxPlotRadius, maxPlotRadius + 1):
            for j in range(-maxPlotRadius, maxPlotRadius + 1):
                surroundingBlock = self.getSurfaceBlock(x + i, z + j)
                blockHeight = surroundingBlock.y
                surroundingBlockHeights.append(blockHeight)
                if surroundingBlock.id == block.WATER_STATIONARY.id or surroundingBlock.id == block.WATER.id:
                    plotContainsWater = True

        blockElevationStd = statistics.stdev(surroundingBlockHeights)

        return blockElevationStd if not plotContainsWater else None  # return None if the plot contains water so it is rejected from potential plots


    def calculatePotentialPlots(self, maxPlotRadius, townCentreCoords, elevationWeighting, distanceWeighting, heightWeighting):
        potentialPlots = []

        zoneMinX = min(self.startCoord[0], self.endCoord[0])
        zoneMinZ = min(self.startCoord[2], self.endCoord[2])
        zoneMaxX = max(self.startCoord[0], self.endCoord[0])
        zoneMaxZ = max(self.startCoord[2], self.endCoord[2])

        # search through every block every half radius (effectively every quarter of a plot)
        # and calculate the slevation std
        for x in range(zoneMinX + maxPlotRadius, zoneMaxX - maxPlotRadius - 1, maxPlotRadius // 2):
            for z in range(zoneMinZ + maxPlotRadius, zoneMaxZ - maxPlotRadius - 1, maxPlotRadius // 2):
                surfaceBlock = self.getSurfaceBlock(x, z)
                newPlot = Plot(x, surfaceBlock.y, z, maxPlotRadius)
                
                blockElevationStd = self.calculateElevationStd(x, z, maxPlotRadius)

                newPlot.setElevationStd(blockElevationStd)
                newPlot.calculateElevationRating()
                newPlot.calculateDistanceRating(townCentreCoords)
                newPlot.calculateHeightRating(townCentreCoords)

                if not newPlot.containsWater:
                    newPlot.calculateOverallRating(elevationWeighting, distanceWeighting, heightWeighting)
                    potentialPlots.append(newPlot)

        sortedPotentialPlots = sorted(potentialPlots, key=lambda x:x.overallRating)

        return sortedPotentialPlots

    
    # helper function that checks if plot is isolated far enough from other chosen plots
    def plotIsIsolated(self, checkPlot, chosenPlots, minDistance):
        minDistance = int(minDistance)
        for chosenPlot in chosenPlots:
            plotDistanceX = abs(chosenPlot.x - checkPlot.x)
            plotDistanceZ = abs(chosenPlot.z - checkPlot.z)
            if plotDistanceX < minDistance and plotDistanceZ < minDistance:
                return False
        return True
            

    def locateFlatAreas(self, maxPlotRadius, amountOfPlots, townCentreCoords, elevationWeighting, distanceWeighting, heightWeighting):
        print("Locating flat areas..")
        Landscaper.placeTownCentre(self.mcApi, townCentreCoords[0], townCentreCoords[1], townCentreCoords[2])
        potentialPlots = self.calculatePotentialPlots(maxPlotRadius, townCentreCoords, elevationWeighting, distanceWeighting, heightWeighting)
        # elevationStds = self.generateElevationStds(maxPlotRadius)

        chosenPlots = []

        for plot in potentialPlots:
            if len(chosenPlots) >= amountOfPlots:
                break
            if self.plotIsIsolated(plot, chosenPlots, 2.5 * maxPlotRadius):
                chosenPlots.append(plot)
                print(f"Overall Rating: {plot.overallRating:.2f}\tElev STD: {plot.elevationStd:.2f}\tDist Rating: {plot.distanceRating:.2f}\tHeight Rating: {plot.heightRating:.2f}")
                # print("STD", plot.elevationStd, "\tAt", plot.x, plot.y, plot.z)
                Landscaper.placeBeacon(self.mcApi, plot.x, plot.y, plot.z, True)
                time.sleep(0.2)  # for dramatic effect

        print("Finished locating plots.")



class Landscaper:
    @staticmethod
    def placeBeacon(mcApi, x, y, z, verbose=False):
        mcApi.setBlock(x, y, z, 138)
        mcApi.setBlocks(x-1, y-1, z-1, x+1, y-1, z+1, block.DIAMOND_BLOCK)
        if verbose:
            print("Placed beacon at:", x, y, z)

    
    @staticmethod
    def placeTownCentre(mcApi, x, y, z, verbose=False):
        mcApi.setBlocks(x-1, y-1, z-1, x+1, y-1, z+1, block.GOLD_BLOCK)
        if verbose:
            print("Placed town centre at:", x, y, z)





ZONE_RADIUS = 80
SURFACE_SEARCH_START_HEIGHT = 150
MAX_PLOT_RADIUS = 8
AMOUNT_OF_PLOTS = 10
# weights used to calculate ideal plot placement
ELEVATION_WEIGHTING = 0.5
DISTANCE_WEIGHTING = 0.4
HEIGHT_WEIGHTING = 0.1

start_time = time.time()
mc = Minecraft.create()
x_player, y_player, z_player = mc.player.getTilePos()
print("Player position:", x_player, y_player, z_player)

zoneStartCoords = (x_player-ZONE_RADIUS, y_player-50, z_player-ZONE_RADIUS)
zoneEndCoords = (x_player+ZONE_RADIUS, y_player+100, z_player+ZONE_RADIUS)

newZone = Zone(mc, zoneStartCoords, zoneEndCoords, SURFACE_SEARCH_START_HEIGHT)

# newZone.getBlock(0, 78, 0).info()
# newZone.getSurfaceBlock(1, 0).info()
# newZone.getSurfaceBlock(24, -8).info()

playerPosTuple = (x_player, y_player, z_player)  # temporarily use for town centre
newZone.locateFlatAreas(MAX_PLOT_RADIUS, AMOUNT_OF_PLOTS, playerPosTuple, ELEVATION_WEIGHTING, DISTANCE_WEIGHTING, HEIGHT_WEIGHTING)




print("--- %s seconds ---" % (time.time() - start_time))

