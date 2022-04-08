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
        print("calculateSurfaceBlocks: calculating surface blocks from startHeigh -", startHeight)
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


    # Uses zoneblocks (3d matrix of blocks - ordered by Y, X, Z)
    # startHeight describes the y coord at which the function starts searching down for the first non-air block
    # Sets surfaceBlocks to 2d matrix ordered by X, Z, containing the block on the surface of that SQUARE
    # TODO: ignore trees and other non-ground structures
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
                while y > zoneMinY and zoneBlocks[y][x][z].id == 0:  # keep checking if that squares block id is AIR
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
    

    # Searches for the flattest areas, calculating the elevationStd of each block every half maxPlotRadius
    # TODO: set temporary beacons at lowest std blocks
    # TODO: set a min distance between plots
    """
    zoneSurfaceBlocks:
       [[(), (), (), (), ()],
        [(), (), (), (), ()],
        [(), (), (), (), ()],
        [(), (), (), (), ()],
        [(), (), (), (), ()]]
    """
    def locateFlatAreas(self, maxPlotRadius):
        elevationStds = []

        zoneMinX = min(self.startCoord[0], self.endCoord[0])
        zoneMinZ = min(self.startCoord[2], self.endCoord[2])
        
        zoneMaxX = max(self.startCoord[0], self.endCoord[0])
        zoneMaxZ = max(self.startCoord[2], self.endCoord[2])

        # search through every block every half radius (effectively every quarter of a plot)
        # and calculate the slevation std
        for x in range(zoneMinX + maxPlotRadius, zoneMaxX - maxPlotRadius - 1, maxPlotRadius // 2):
            for z in range(zoneMinZ + maxPlotRadius, zoneMaxZ - maxPlotRadius - 1, maxPlotRadius // 2):
                surroundingBlockHeights = []
                for i in range(-maxPlotRadius, maxPlotRadius + 1):
                    for j in range(-maxPlotRadius, maxPlotRadius + 1):
                        blockHeight = self.getSurfaceBlock(x + i, z + j).y
                        surroundingBlockHeights.append(blockHeight)
                # print(surroundingBlockHeights)
                blockElevationStd = statistics.stdev(surroundingBlockHeights)
                surfaceBlock = self.getSurfaceBlock(x, z)
                elevationStds.append((surfaceBlock, blockElevationStd))  # append tuple of coords + elevationStd

        sortedElevationStds = sorted(elevationStds, key=lambda x:x[1], reverse=False)  # sort by descending elevation std 

        for i in range(10):
            print("STD", sortedElevationStds[i][1], "\t", end=" ")
            sortedElevationStds[i][0].info()




ZONE_RADIUS = 50
SURFACE_SEARCH_START_HEIGHT = 100

start_time = time.time()
mc = Minecraft.create()
x_player, y_player, z_player = mc.player.getTilePos()
print("Player position:", x_player, y_player, z_player)

zoneStartCoords = (x_player-ZONE_RADIUS, y_player-50, z_player-ZONE_RADIUS)
zoneEndCoords = (x_player+ZONE_RADIUS, y_player+50, z_player+ZONE_RADIUS)

newZone = Zone(mc, zoneStartCoords, zoneEndCoords, SURFACE_SEARCH_START_HEIGHT)

# newZone.getBlock(0, 78, 0).info()
# newZone.getSurfaceBlock(1, 0).info()
# newZone.getSurfaceBlock(24, -8).info()

newZone.locateFlatAreas(10)



print("--- %s seconds ---" % (time.time() - start_time))

