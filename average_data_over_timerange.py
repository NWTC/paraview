# Paraview Time Averaging Macro
#
# Eliot Quon (eliot.quon@nrel.gov) -- 10/03/2017
#
# Based on demonstration script for paraview version 5.0
# written by Jean M. Favre, Swiss National Supercomputing Centre
# tested Tue Feb 16 08:43:13 CET 2016
# 
# Usage instructions:
# - Add this script as a macro (Macros >> Add new macro...)
# - Update the AVERAGING PARAMETERS section (Macros >> Edit... >> average_data_over_timerange)
# - Select the source data to be avearged
# - Apply the filter (Macros >> average_data_over_timerange)
# - Check averaging operations in log (Tools >> Python Shell)
#
from paraview.simple import *

Stats_ReqData = """
##############################
#*** AVERAGING PARAMETERS ***#
averagingStartTime = 0
averagingEndTime = 99
averagingCellData = \'U\'
averagingPointData = None
averagedFieldName = \'U_tavg\'
##############################
    
executive = self.GetExecutive()
outInfo = executive.GetOutputInformation(0)

if averagingCellData is not None:
  data = inputs[0].CellData[averagingCellData]
elif averagingPointData is not None:
  data = inputs[0].PointData[averagingPointData]
else:
  print "ERROR: Specify averagingCellData or averagingPointData"
  request.Remove(vtk.vtkStreamingDemandDrivenPipeline.CONTINUE_EXECUTING())
  
ti = self.ts[self.CurrentTimeIndex]

if (self.Navg == 0) and (ti >= averagingStartTime):
  self.temp_data = data
  print "        INIT: CurrentTimeIndex = ", self.CurrentTimeIndex, ", tlen = ", self.tlen, ", t = ", ti
  self.Navg = 1
elif (ti > averagingStartTime) and (ti <= averagingEndTime):
  print "        ACCUMULATE: Accumulate  ts[", self.CurrentTimeIndex, "] = ", ti
  self.temp_data = data + self.temp_data
  self.Navg += 1

self.CurrentTimeIndex = self.CurrentTimeIndex + 1

if (ti >= averagingEndTime) or (self.CurrentTimeIndex >= self.tlen):
  # finish
  request.Remove(vtk.vtkStreamingDemandDrivenPipeline.CONTINUE_EXECUTING())
  #self.CurrentTimeIndex = 0
  output.CellData.append(self.temp_data/self.Navg, averagedFieldName)
  print "        FINISH: Finish (self.Navg = ",self.Navg,")"
else:
  # continue executing
  request.Set(vtk.vtkStreamingDemandDrivenPipeline.CONTINUE_EXECUTING(), 1)

"""

Stats_ReqInfo = """
executive = self.GetExecutive ()
outInfo = executive.GetOutputInformation(0)
self.CurrentTimeIndex = 0
self.Navg = 0

self.tlen = outInfo.Length(executive.TIME_STEPS())
self.ts = [executive.TIME_STEPS().Get(outInfo, i) for i in xrange(self.tlen)]
print "ReqInf: ts = ", self.ts
print "ReqInf: tlen = ", self.tlen
outInfo.Remove(executive.TIME_STEPS())
outInfo.Remove(executive.TIME_RANGE())
#print "Stats_ReqInfo: remove TIME_STEPS and TIME_RANGE"
"""

Stats_ReqExtents = """
executive = self.GetExecutive()
outInfo = executive.GetOutputInformation(0)

if self.tlen > 0:
  #print "    ProgrammableFilter: set UPDATE_TIME_STEP = ", self.ts[self.CurrentTimeIndex]
  outInfo.Set(executive.UPDATE_TIME_STEP(), self.ts[self.CurrentTimeIndex])
"""

inp1 = GetActiveSource() #FindSource('U_*')

programmableFilter1 = ProgrammableFilter(Input = inp1)
programmableFilter1.Script = Stats_ReqData
programmableFilter1.RequestInformationScript = Stats_ReqInfo
programmableFilter1.RequestUpdateExtentScript = Stats_ReqExtents
programmableFilter1.PythonPath = ''

programmableFilter1Display = Show(programmableFilter1)
programmableFilter1Display.Representation = 'Surface'

Render()
