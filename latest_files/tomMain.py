import time
from Zone import Zone
from mcpi.minecraft import Minecraft


ZONE_RADIUS = 80  # size of the zone (100 will pull ~ 6 million blocks)
SURFACE_SEARCH_START_HEIGHT = 150  # the y level at which the program starts searching downwards to determine the surface block - set to something above the highest block
MAX_PLOT_RADIUS = 8  # the max radius a plot can have (indicates size for terraforming)
AMOUNT_OF_PLOTS = 10
ELEVATION_WEIGHTING = 0.5 # weights used to calculate ideal plot placement, must add up to 1
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
newZone.locatePlots(MAX_PLOT_RADIUS, AMOUNT_OF_PLOTS, playerPosTuple, ELEVATION_WEIGHTING, DISTANCE_WEIGHTING, HEIGHT_WEIGHTING, True)  # set to false to remove beacons


print("--- Took %s seconds ---" % (time.time() - start_time))
