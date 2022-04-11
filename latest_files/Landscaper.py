from mcpi import block


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
