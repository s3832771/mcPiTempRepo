import statistics
import time
from Landscaper import Landscaper
from Plot import Plot
from Block import Block
from mcpi import block


class Zone:
    def __init__(self, mcApi, startCoord, endCoord, startHeight):  
        self.mcApi = mcApi  # is this how we should be passing the mcApi object?
        self.startCoord = startCoord  # (x, y, z)
        self.endCoord= endCoord  # (x, y, z)
        self.xSize = abs(startCoord[0] - endCoord[0]) + 1
        self.ySize = abs(startCoord[1] - endCoord[1]) + 1
        self.zSize = abs(startCoord[2] - endCoord[2]) + 1
        print("pullZoneBlocks: pulling all blocks from cuboid between -", startCoord, endCoord)
        self.pullZoneBlocks(startCoord, endCoord)
        print("Successfully pulled zone blocks.")
        print("calculateSurfaceBlocks: calculating surface blocks from startHeight -", startHeight)
        self.calculateSurfaceBlocks(startHeight)
        print("Successfully calculated the zone's surface blocks.")
        self.chosenPlots = []  # initialise to no chosen plots


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

        self.zoneBlocks = zoneBlocks


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
        zoneMaxY = max(self.startCoord[1], self.endCoord[1])
        if startHeight >= zoneMaxY:
            print("=============== PLEASE INCREASE SURFACE_SEARCH_START_HEIGHT VAR ===============")
            print("The starting search height is above the ceiling of the zone.")
        
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
        for x in range(zoneMinX + maxPlotRadius, zoneMaxX - maxPlotRadius - 1, 2): # maxPlotRadius // 2):
            for z in range(zoneMinZ + maxPlotRadius, zoneMaxZ - maxPlotRadius - 1, 2): # maxPlotRadius // 2):
                surfaceBlock = self.getSurfaceBlock(x, z)
                newPlot = Plot(surfaceBlock, maxPlotRadius)
                
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
            plotDistanceX = abs(chosenPlot.getX() - checkPlot.getX())
            plotDistanceZ = abs(chosenPlot.getZ() - checkPlot.getZ())
            if plotDistanceX <= minDistance and plotDistanceZ <= minDistance:
                return False
        return True
            

    def locatePlots(self, maxPlotRadius, amountOfPlots, townCentreCoords, elevationWeighting, distanceWeighting, heightWeighting, markWithBeacons):
        print("Locating flat areas..")
        Landscaper.placeTownCentre(self.mcApi, townCentreCoords[0], townCentreCoords[1], townCentreCoords[2])
        potentialPlots = self.calculatePotentialPlots(maxPlotRadius, townCentreCoords, elevationWeighting, distanceWeighting, heightWeighting)
        # elevationStds = self.generateElevationStds(maxPlotRadius)

        chosenPlots = []

        for plot in potentialPlots:
            if len(chosenPlots) >= amountOfPlots:
                break
            if self.plotIsIsolated(plot, chosenPlots, 2 * maxPlotRadius):
                chosenPlots.append(plot)
                print(f"Overall Rating: {plot.overallRating:.2f}\tElev STD: {plot.elevationStd:.2f}\tDist Rating: {plot.distanceRating:.2f}\tHeight Rating: {plot.heightRating:.2f}")
                if markWithBeacons:
                    Landscaper.placeBeacon(self.mcApi, plot.getX(), plot.getY(), plot.getZ(), True)
                time.sleep(0.2)  # for dramatic effect

        self.chosenPlots = chosenPlots
        print("Finished locating plots.")