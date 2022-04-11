# mcPiTempRepo

## Summary
1. Refer to files in the latest_files folder.
2. So far this repo contains 4 basic classes - **Block, Plot, Zone and Landscaper**, which have been designed to be of use across all 4 parts of the assignment.
3. In summary, we pull all the blocks within a user-defined cuboid around the player location - which we call the ‘zone’. Every single block is processed and stored as a block object in a 3d nested dictionary (zone.zoneBlocks) inside the zone object. Each block can be accessed using the zone.getBlock method - could be useful for the pathing section of the assignment.
* On creation of a zone object, each surface block is found and can be accessed using zone.getSurfaceBlock() - (note: using the mcApi getHeight method is extremely inefficient when dealing with multiple blocks so the zone.getSurfaceBlock method is preferred as every surface block within each zone is calculated at the beginning and stored in memory).

## Plot selection
4. Various methods within the zone object help to locate the most ideal plot locations - which consider 3 different factors - surrounding steepness (elevationStd), distance and the height difference of each surface block from the current player location.
* Overall, nearby, flat areas that are on somewhat similar y levels to the current player position are prioritised.
* This follows a close to real-world process in plot area selection and retains the natural randomness seen in a normal minecraft world.

## Where to start
5. In order to provide a starting point for the other parts of the assignment, plot area selection has been finished and information on each chosen plot can be accessed in the zone object through the zone.chosenPlots attribute.
* To get started, have a read through the example tomMain.py file, which sets up essential variables and calls methods required for everything to work together.
* And feel free to read through the other class files to better understand what each object does and what variables they hold.
* Side note: beacons are being used to mark out chosen plots for debugging places but can be turned off via a parameter in locatePlots.
