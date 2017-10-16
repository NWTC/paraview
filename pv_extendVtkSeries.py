#!/usr/bin/env python
#
# Utility to update a paraview state file that is based on the legacy VTK file reader which doesn't
# glob and load the file series on the file, but rather explicitly saves the VTK files. This will 
# appropriately update the state file with an extended series of VTK files, assuming the files are 
# in the following format:
#   path/to/VTK/series/foo_bar0.vtk
#   path/to/VTK/series/foo_bar1.vtk
#   ...
#   path/to/VTK/series/foo_barN.vtk
#
# After adding more appropriately named files to the data directory, call this script with the new 
# total number of VTK files.
#
# Sample usage: pv_extendVtkSeries.py anim_slice_horizontal_z080.pvsm 360
#
# Written by Eliot Quon (eliot.quon@nrel.gov) -- 2017-10-16
#
import sys
import os
import xml.etree.ElementTree as ET

verbose = False

class ParaviewState(object):

    def __init__(self,statefile):
        self.pvsm = ET.parse(statefile)
        self.root = self.pvsm.getroot()
        self.vtkreader = None       # <Proxy group="sources" type="LegacyVTKFileReader" ...>
        self.filenames = None       #   <Property name="FileNames" number_of_elements="N" ...>
        self.timestepvalues = None  #   <Property name="TimestepValues" number_of_elements="N" ...>
        self.timekeeper = None      # <Proxy group="misc" type="TimeKeeper" ...>
        self.animation = None       # <Proxy group="animation" type="AnimationScene" ...>

        assert(self.root.tag == 'ParaView')
        assert(self.root[0].tag == 'ServerManagerState')
        if verbose: print 'Sources in',statefile,':'
        for idx,child in enumerate(self.root[0]):
            if ('group' in child.attrib) and (child.attrib['group'] == 'sources'):
                if child.attrib['type'] == 'LegacyVTKFileReader':
                    self.vtkreader = self.root[0][idx]
                if verbose: print idx, child.tag, child.attrib
            elif ('group' in child.attrib) and (child.attrib['group'] == 'misc'):
                if child.attrib['type'] == 'TimeKeeper':
                    self.timekeeper = self.root[0][idx]
            elif ('group' in child.attrib) and (child.attrib['group'] == 'animation'):
                if child.attrib['type'] == 'AnimationScene':
                    self.animation = self.root[0][idx]
        if self.vtkreader is not None:
            if verbose: print 'VTK reader found:',self.vtkreader
            for child in self.vtkreader:
                if child.attrib['name'] == 'FileNames':
                    self.filenames = child
                elif child.attrib['name'] == 'TimestepValues':
                    self.timestepvalues = child
            assert(self.filenames is not None)
            assert(self.timestepvalues is not None)

    def write(self,fname):
        self.pvsm.write(fname)
        print 'Wrote out',fname

    def extendFileNames(self,Nframes):
        assert(self.filenames is not None)
        # get index/value for each file name element
        indices = []
        fnames = []
        if verbose: print 'Current filename list:'
        for elem in self.filenames:
            if elem.tag == 'Element':
                if verbose: print elem.tag, elem.attrib
                indices.append(int(elem.attrib['index']))
                fnames.append(elem.attrib['value'])
        if verbose: print 'Current indices:',indices
        # get prefix
        pre, ext = os.path.splitext(fnames[0])
        start_index = pre[-1]
        ist = -1
        try:
            while int(pre[ist-1:]):
                ist -= 1
                start_index = pre[ist:]
        except ValueError: pass
        self.start_index = start_index
        if verbose: print 'Starting index:',self.start_index
        self.prefix = pre[:ist]
        if verbose: print 'Prefix:',self.prefix
        # add additional elements
        Nprev = len(indices)
        if verbose: print 'Previous number of frames:',Nprev
        for i in range(Nprev,Nframes):
            newelem = ET.SubElement(self.filenames,'Element')
            newelem.set('index',str(i))
            newelem.set('value',self.prefix+str(i)+ext)
        self.filenames.set('number_of_elements',str(Nframes))

    def extendTimestepValues(self,Nframes):
        assert(self.timestepvalues is not None)
        indices = []
        values = []
        for elem in self.timestepvalues:
            if elem.tag == 'Element':
                indices.append(int(elem.attrib['index']))
                values.append(int(elem.attrib['value']))
        Nprev = len(indices)
        if verbose: print 'Previous number of frames:',Nprev
        for i in range(Nprev,Nframes):
            newelem = ET.SubElement(self.timestepvalues,'Element')
            newelem.set('index',str(i))
            newelem.set('value',str(i))
        self.timestepvalues.set('number_of_elements',str(Nframes))

    def extendTimeKeeper(self,Nframes):
        assert(self.timekeeper is not None)
        for prop in self.timekeeper:
            if prop.attrib['name'] == 'TimeRange':
                assert(int(prop.attrib['number_of_elements']) == 2)
                if verbose: print 'Previous time range: ',prop[0].attrib['value'],' ',prop[1].attrib['value']
                prop[-1].set('value',str(Nframes-1))
            elif prop.attrib['name'] == 'TimestepValues':
                Nprev = int(prop.attrib['number_of_elements'])
                for i in range(Nprev,Nframes):
                    newelem = ET.SubElement(prop,'Element')
                    newelem.set('index',str(i))
                    newelem.set('value',str(i))
                prop.set('number_of_elements',str(Nframes))

    def updateAnimation(self,Nframes):
        assert(self.animation is not None)
        for prop in self.animation:
            if prop.attrib['name'] == 'EndTime':
                assert(int(prop.attrib['number_of_elements']) == 1)
                prop[0].set('value',str(Nframes-1))
                

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    statefile = sys.argv[1]
    Nframes = int(sys.argv[2])

    pvstate = ParaviewState(statefile)
    pvstate.extendFileNames(Nframes)
    pvstate.extendTimestepValues(Nframes)
    pvstate.extendTimeKeeper(Nframes)
    pvstate.updateAnimation(Nframes)

    pre,ext = os.path.splitext(statefile)
    newstatefile = pre + 'extend'+str(Nframes) + ext
    pvstate.write(newstatefile)

