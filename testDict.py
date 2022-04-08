from pprint import pprint
from mcpi.minecraft import Minecraft
from mcpi import block


# DEFINITIONS:
# zone = user-defined box boundary containing plots
# radius = we are working with square plots, so a radius is half the width/height of a square
# square = a single square within a zone/one column of blocks


# (modified version for efficiency)
# Generates 3d matrix of all blocks within cuboid.
# Ordered by Y, then X, then Z (due to how mc.getBlocks returns blocks)
# each block is represented by tuple of (x, y, z, blockID)
def getZoneBlocksEfficient(x0, y0, z0, x1, y1, z1):
    blockIds = mc.getBlocks(x0, y0, z0, x1, y1, z1)
    blockIds = list(blockIds)

    zoneBlocks = {}
    for y in range(y1, y0-1, -1):
        y_square = {}
        for x in range(x1, x0-1, -1):
            x_row = {}
            for z in range(z1, z0-1, -1):
                blockData = (x, y, z, blockIds.pop())
                x_row[z] = blockData
            y_square[x] = x_row
        zoneBlocks[y] = y_square

    return zoneBlocks
    


# Accepts 3d matrix of blocks - ordered by Y, X, Z
# startHeight describes the y coord at which the function starts searching down for the first non-air block
# Returns 2d matrix ordered by X, Z, containing coordinates of each square's height
def getZoneSurfaceBlocks(zoneBlocks, startHeight):
    zoneHeights = {}

    zoneMinY = min(list(zoneBlocks.keys()))  # gets the min height of the zone cuboid to stop lowering y on search for non-air block
    zoneMinX = min(list(zoneBlocks[list(zoneBlocks.keys())[0]].keys()))
    zoneMinZ = min(list(zoneBlocks
        [list(zoneBlocks.keys())[0]]
        [list(zoneBlocks[list(zoneBlocks.keys())[0]].keys())[0]]
        .keys()))

    amountOfXs = len(zoneBlocks[list(zoneBlocks.keys())[0]].keys())  # get size of dict in the first y level = size of zone in the x dimension
    amountOfZs = len(zoneBlocks
        [list(zoneBlocks.keys())[0]]
        [list(zoneBlocks[list(zoneBlocks.keys())[0]].keys())[0]]
        .keys())  # get size of dict in the first x level of the first y level = size of zone in the z dimension

    for x in range(zoneMinX, zoneMinX + amountOfXs):
        x_row = {}
        for z in range(zoneMinZ, zoneMinZ + amountOfZs):
            y = startHeight
            while y > zoneMinY and zoneBlocks[y][x][z][3] == 0:  # keep checking if that squares block id is AIR
                y -= 1

            surfaceBlockProperties = zoneBlocks[y][x][z]
            # print(surfaceBlockProperties)
            x_row[z] = surfaceBlockProperties
        zoneHeights[x] = x_row

    return zoneHeights



# old - using as reference
def selectPlots(searchRadius, maxPlotRadius):
    x_player, y_player, z_player = mc.player.getTilePos()
    zoneHeights = []

    for x in range(x_player-searchRadius, x_player+searchRadius):
        x_row = []
        for z in range(z_player-searchRadius, z_player+searchRadius):
            y = mc.getHeight(x, z)
            squareProperties = (x, y, z)  # add block type later
            print(squareProperties)
            x_row.append(squareProperties)
        zoneHeights.append(x_row)

    pprint(zoneHeights)



def selectPlots(zoneSurfaceBlocks, maxPlotRadius):
    zoneHeights = []




mc = Minecraft.create()

x_player, y_player, z_player = mc.player.getTilePos()
# y_player -= 1
print("Player position:", x_player, y_player, z_player)
print("==============================")

zoneBlocks = getZoneBlocksEfficient(x_player-100, y_player-50, z_player-100, x_player+100, y_player+50, z_player+100)
# print(zoneBlocks)
print(zoneBlocks[76][-6][-14])


zoneSurfaceBlocks = getZoneSurfaceBlocks(zoneBlocks, 100)
print(zoneSurfaceBlocks[1][-8])
print(zoneSurfaceBlocks[1][-7])
print(zoneSurfaceBlocks[80][-101])


