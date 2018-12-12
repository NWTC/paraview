#
# Script for adding simple rotor representations to the flow field
#
# Written by Eliot Quon (eliot.quon@nrel.gov)
# Tested with ParaView 5.5.0-RC4 64-bit
#

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

###############################################################################
# SPECIY THESE INPUTS:
zhub = 80.
hub_rad = 1.31 # m
tip_rad = 46.31 # m
yaw_angle = 4.5 # deg (positive rotation about z, 0 deg ==> +x)
shaft_tilt = -6.0 # deg (FAST convention, <0 for upwind turbines) 

# turbine locations in array with shape==(Nturbines,3)
import numpy as np
coordinates = np.loadtxt('windplant.xyz.csv',delimiter=',')

# defaults
disk_color = [0.0, 0.0, 0.0]
disk_opacity = 0.4 # 1: opaque
###############################################################################

disks = []
transforms = []
displays = []

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [912, 459]

# # update the view to ensure updated data information
# renderView1.Update()

for i in range(len(coordinates)):

    # create a new 'Disk'
    disks.append(Disk())
    RenameSource('WT'+str(i+1), disks[i])

    # set disk properties
    disks[i].InnerRadius = hub_rad
    disks[i].OuterRadius = tip_rad

    # create a new 'Transform'
    rotor_apex = coordinates[i,:]
    rotor_apex[2] += zhub
    transforms.append(Transform(Input=disks[i]))
    transforms[i].Transform = 'Transform'
    transforms[i].Transform.Translate = rotor_apex
    transforms[i].Transform.Rotate = [0.0, 90.0-shaft_tilt, yaw_angle]

    # show data in view
    displays.append(Show(transforms[i], renderView1))
    displays[i].DiffuseColor = disk_color
    displays[i].Opacity = disk_opacity

    # update the view to ensure updated data information
    #renderView1.Update()

#### uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).
