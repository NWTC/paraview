# Paraview macro: wake data from horizontal plane
#
# - data extracted from lines at specified downstream distances
# - assume flow in +x
# - data extent is +/- 2D
#
# Eliot Quon (eliot.quon@nrel.gov) -- 06/13/2019
#
# trace generated using paraview version 5.6.0


#### import the simple module from the paraview
from paraview.simple import *
import os

##################################
#### INPUTS FOR LINE SAMPLING ####
rotorDiameter = 126.0
downstreamDistances = [1,2,3,4,5,6,7,8]
baseLocations = {
    'WT35': [1175.2, 3912.8, 90.01],
    'WT36': [ 788.2, 3406.1, 90.01],
    'WT37': [ 586.8, 2801.2, 90.01],
    'WT19': [ 592.6, 2163.7, 90.01],
    'WT20': [ 805.2, 1562.6, 90.01],
    'WT21': [1201.4, 1063.1, 90.01],
}
outdir = '/path/to/output/directory'
##################################

# find source
src = GetActiveSource() #FindSource('U_tavg1hr_slice_horizontal_1.vtk')

# create a new 'Plot Over Line'
plotOverLine1 = PlotOverLine(Input=src, Source='High Resolution Line Source')

if not os.path.isdir(outdir):
    os.makedirs(outdir)

for prefix,baseLocation in baseLocations.items():

    x0,y0,z0 = baseLocation

    for downD in downstreamDistances:

        pt1 = [x0 + downD*rotorDiameter, y0 - 2*rotorDiameter, z0]
        pt2 = [x0 + downD*rotorDiameter, y0 + 2*rotorDiameter, z0]

        outfile = os.path.join(outdir,
                               '{:s}_{:.2g}D.csv'.format(prefix,downD))

        # Properties modified on plotOverLine1.Source
        plotOverLine1.Source.Point1 = pt1
        plotOverLine1.Source.Point2 = pt2

        # save data
        SaveData(outfile, proxy=plotOverLine1)

