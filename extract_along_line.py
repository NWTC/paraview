# Paraview macro: data extraction along line
#
# Eliot Quon (eliot.quon@nrel.gov) -- 06/13/2019
#
# trace generated using paraview version 5.6.0


#### import the simple module from the paraview
from paraview.simple import *

##################################
#### INPUTS FOR LINE SAMPLING ####
pt1 = [600, 2000, 90.01]
pt2 = [600, 2300, 90.01]
outfile = '/path/to/output.csv'
##################################

# find source
src = GetActiveSource() #FindSource('U_tavg1hr_slice_horizontal_1.vtk')

# create a new 'Plot Over Line'
plotOverLine1 = PlotOverLine(Input=src, Source='High Resolution Line Source')

# Properties modified on plotOverLine1.Source
plotOverLine1.Source.Point1 = pt1
plotOverLine1.Source.Point2 = pt2

# save data
SaveData(outfile, proxy=plotOverLine1)

