#
# General Paraview batch processing script for generating PNG snapshots from 
# 2D VTK data.
#
# written by Eliot Quon (eliot.quon@nrel.gov) -- 2017-07-24
#
import sys,os
import yaml
if len(sys.argv) <= 1:
    sys.exit('Specify yaml slice definition file')

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

opt = yaml.load(open(sys.argv[1],'r'))
# default options:
verbose = False
fieldName = 'U'
annotateFilename = True
horizontalColorbar = True
dataCenter = [0,0,0]
sliceNormal = 'z' # assume to be aligned with x, y, or z
viewSize = [1200, 800]
colorbarRange = [None,None]
for key, value in opt.iteritems():
    locals()[key] = value

dirIndex = { 'x': 0, 'y': 1, 'z': 2 }
viewMapping = { 'x': [0,0,1], 'y': [0,0,1], 'z': [0,1,0] } # "up" direction in visualization
cameraOffset = { 'x': -10000.0, 'y': -10000.0, 'z': 10000.0 } # from dataCenter

#-------------------------------------------------------------------------------

#imageName = 'snapshot.png'
inputFiles = [ os.path.abspath(fname) for fname in opt['sliceFiles'] ]
#outputFiles = [ os.path.split(path)[0]+os.sep+imageName for path in inputFiles ]
outputFiles = [ path[:-4]+'.png' for path in inputFiles ]

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
renderView1.ViewSize = viewSize

# reset view to fit data
#renderView1.ResetCamera()
viewUp = viewMapping[sliceNormal]
needReset = True

# TODO: calculate optimal view size and camera settings
# http://public.kitware.com/pipermail/paraview/2015-September/035151.html
cameraPos = list(dataCenter) # copy
cameraPos[dirIndex[sliceNormal]] += cameraOffset[sliceNormal]
Lref = max(dataCenter)

for fname in opt['sliceFiles']:

    # get absolute path for input / output files
    inputFile = os.path.abspath(fname)
    outputFile = os.path.splitext(inputFile)[0] + '.png'

    # create a new 'Legacy VTK Reader'
    slice2d = LegacyVTKReader(FileNames=inputFile)

    # show data in view
    slice2dDisplay = Show(slice2d, renderView1)

    # set scalar coloring
    ColorBy(slice2dDisplay, ('CELLS', fieldName))

    # rescale color and/or opacity maps used to include current data range
    slice2dDisplay.RescaleTransferFunctionToDataRange(True)

    # show color bar/color legend
    slice2dDisplay.SetScalarBarVisibility(renderView1, True)

    # get color transfer function/color map for specified field
    uLUT = GetColorTransferFunction(fieldName)

    # get opacity transfer function/opacity map for specified field
    uPWF = GetOpacityTransferFunction(fieldName)

    # rescale color and/or opacity maps used to exactly fit the current data range
    slice2dDisplay.RescaleTransferFunctionToDataRange(False)

    # rescale transfer function
    if (colorbarRange[0] is not None) and (colorbarRange[1] is not None):
        uLUT.RescaleTransferFunction(colorbarRange[0], colorbarRange[1])
        uPWF.RescaleTransferFunction(colorbarRange[0], colorbarRange[1])

    # reset view to fit data (just once)
    if needReset:
        renderView1.ResetCamera()
        needReset = False

    # current camera placement for renderView1
    renderView1.InteractionMode = '2D'
    renderView1.CameraPosition = cameraPos
    renderView1.CameraFocalPoint = dataCenter
    renderView1.CameraViewUp = viewUp
    renderView1.CameraParallelScale = 0.7*Lref # zoom out
    if verbose:
        print 'viewUp:',viewUp,' cameraPos:',cameraPos,' dataCenter:',dataCenter

    # customize colorbar (optional)
    if horizontalColorbar:
        uLUTColorBar = GetScalarBar(uLUT, renderView1)
        uLUTColorBar.Position = [0.36, 0.09] # lower-left corner (fraction of view size)
        uLUTColorBar.Position2 = [0.43, 0.12] # relative distance to upper-right corner (fraction of view size)
        uLUTColorBar.Orientation = 'Horizontal'
       #uLUTColorBar.Title = fieldName
       #uLUTColorBar.ComponentTitle = 'Magnitude'
       #uLUTColorBar.TitleFontSize = 12 # has no effect?
       #uLUTColorBar.LabelFontSize = 11 # has no effect?
       #uLUTColorBar.AutoOrient = 0

    # annotate the input filename (optional)
    if annotateFilename:
        text1 = Text()
        text1Display = Show(text1, renderView1)
        text1.Text = fname # input file name (not necessarily abs path)
        text1Display.FontSize = 10
        text1Display.WindowLocation = 'UpperLeftCorner'

    # save screenshot
    if os.path.isfile(outputFile):
        action = 'Overwriting'
    else:
        action = 'Writing'
    print action, outputFile
    SaveScreenshot(outputFile, magnification=1, quality=100, view=renderView1)

    # destroy objects
    Delete(slice2d)
    if annotateFilename: Delete(text1)

