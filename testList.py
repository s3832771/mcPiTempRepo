from pprint import pprint
from mcpi.minecraft import Minecraft
from mcpi import block



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


# Helper functions
def is_list(p): 
    return isinstance(p, list)

def deep_reverse(mylist):
    result = []
    for e in mylist:
        if isinstance(e, list):
            result.append(deep_reverse(e))
        else:
            result.append(e)
    result.reverse()
    return result


# (modified version for efficiency)
# Generates 3d matrix of all blocks within cuboid.
# Ordered by Y, then X, then Z (due to how mc.getBlocks returns blocks)
# each block is represented by tuple of (x, y, z, blockID)
def getZoneBlocksEfficient(x0, y0, z0, x1, y1, z1):
    blockIds = mc.getBlocks(x0, y0, z0, x1, y1, z1)
    blockIds = list(blockIds)

    zoneBlocks = []
    for y in range(y1, y0-1, -1):
        y_square = []
        for x in range(x1, x0-1, -1):
            x_row = []
            for z in range(z1, z0-1, -1):
                blockData = (x, y, z, blockIds.pop())
                x_row.append(blockData)
            y_square.append(x_row)
        zoneBlocks.append(y_square)

    return deep_reverse(zoneBlocks)  # Need to recursively reverse blocks so zoneBlocks[0][0][0] starts from the starting block corner instead of the ending block
    


# Accepts 3d matrix of blocks - ordered by Y, X, Z
# startHeight describes the height above INITIAL POSITION at which the function starts searching down for the first non-air block
# Returns 2d matrix ordered by X, Z, containing coordinates of each square's height
def getZoneSurfaceBlocks(zoneBlocks, startHeight):
    zoneHeights = []

    for x in range(len(zoneBlocks[0])):
        x_row = []
        for z in range(len(zoneBlocks[0][0])):
            y = startHeight
            while zoneBlocks[y][x][z][3] == 0 and y >= 0:  # keep checking if that squares block id is AIR
                y -= 1

            surfaceBlockProperties = zoneBlocks[y][x][z]
            # print(surfaceBlockProperties)
            x_row.append(surfaceBlockProperties)
        zoneHeights.append(x_row)

    return zoneHeights





mc = Minecraft.create()

x_player, y_player, z_player = mc.player.getTilePos()
y_player -= 1

zoneBlocks = getZoneBlocksEfficient(x_player, y_player, z_player, x_player+100, y_player+100, z_player+100)
print(zoneBlocks[0][3][1])

zoneSurfaceBlocks = getZoneSurfaceBlocks(zoneBlocks, 32)
print(zoneSurfaceBlocks[0][0])
print(zoneSurfaceBlocks[1][0])

