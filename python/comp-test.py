#! /usr/bin/env python

# Written by Vasaant S/O Krishnan. Thursday, 10 March 2016.

import re
from pylab import *
import sys
from mpldatacursor import datacursor

usrFile = sys.argv[1:]

if len(usrFile) == 0:
    print("")
    print("# comp-test.py takes input from *.COMP files to study the")
    print("# component allocation from Luca Moscadelli's compo.f.")
    print("# First argument must be *.COMP. Order for remaining options")
    print("# does not matter:")
    print("")
    print("# plot* = options are: plot, seq, comp and spec.")
    print("# atate = annotates the spots with their component.")
    print("# vel   = allows user specified velocty range for the colourbar.")
    print("# scale = scales the peak flux of the data by a constant factor.")
    print("")
    print("--> ./comp-test.py file_name.COMP plot* vel=xx.x,yy.y atate scale=xx")
    print("")
    exit()



#=====================================================================
#   Define variables:
#
cTmp = []                   # chan temp
vTmp = []                   # velo temp
pTmp = []                   # peak temp
xTmp = []                   # xoff temp
yTmp = []                   # yoff temp
mTmp = []                   # Co(m)p temp

chan = []
vels = []
peak = []
xoff = []
yoff = []
comp = []

compMask   = []             # Subset of arrays which are not blank
velAvg     = []             # Average of each component
homoVelTmp = []
homoVel    = []             # Homogenised velocity

defaultVels  = True         # Otherwise usrVelLim
defaultScale = True         # Otherwise usrScale

channel = '(\d+)'           # 'Channel' variable from *.COMP
spaDigs = '\s+?\d+?'        # 'Space digits'
floats  = '([+-]?\d+.\d+)'  # Any float variable from *.COMP



#=====================================================================
#   Scale the maser spots by a factor of userScale:
#
for i in usrFile:
    userScale = re.search('scale='+'([+-]?\d+)',i)
    if userScale:
        defaultScale = False # Don't use scaleFactor = 1 if user has defined it in usrFile
        scaleFactor  = int(userScale.group(1))
if defaultScale:             # This allows "scale=" to appear anywhere in usrFile
    scaleFactor = 1



#=====================================================================
#   Harvest values:
#
for line in open(usrFile[0],'r'):
    #                       Channel         Velocity      Peak Flux      xOff         yOff    Remaining stuff...    Components
    #reqInfo = re.search('\s+'+channel+'\s+'+floats +'\s+'+floats+'\s+'+floats+'\s+'+floats+'.*'+'\s+'+floats+'\s+'+channel, line)
    reqInfo = re.search('\s+'+channel+10*('\s+'+floats) +'\s+'+channel+'.*?', line) # Added on Sunday, 10 April 2016, 16:42 PM to grab first column components specifically.
    if reqInfo:                                    # Populate temp arrays, which are reset after each component is harvested
        cTmp.append(  int(reqInfo.group(1)))
        vTmp.append(float(reqInfo.group(2)))
        pTmp.append(float(reqInfo.group(3)))
        xTmp.append(float(reqInfo.group(4)))
        yTmp.append(float(reqInfo.group(5)))
        mTmp.append(  str(reqInfo.group(12)))      # String format for annotations for scatterplots
    if line == '\n':                               # This statement allows each component to exist as its own list within the complete array
        chan.append(cTmp)
        vels.append(vTmp)
        peak.append(pTmp)
        xoff.append(xTmp)
        yoff.append(yTmp)
        comp.append(mTmp)
        cTmp = []                                  # Reset temp arrays
        vTmp = []
        pTmp = []
        xTmp = []
        yTmp = []
        mTmp = []
close(usrFile[0])



#=====================================================================
#   The final values from *Tmp need to be mannualy added:
#
chan.append(cTmp)
vels.append(vTmp)
peak.append(pTmp)
xoff.append(xTmp)
yoff.append(yTmp)
comp.append(mTmp)



#=====================================================================
#   Based on 'chan' array, determine the positions of the '\n's:
#
for i in range(len(chan)):
    if chan[i] != []:
        compMask.append(int(i))



#=====================================================================
#   Remove the '\n's:
#
chan = [chan[i] for i in compMask]
vels = [vels[i] for i in compMask]
peak = [peak[i] for i in compMask]
xoff = [xoff[i] for i in compMask]
yoff = [yoff[i] for i in compMask]
comp = [comp[i] for i in compMask]



#=====================================================================
#   Find mean velocity of each comp:
#
for i in range(len(vels)):
    velAvg.append(float(sum(vels[i])/len(vels[i])))



#=====================================================================
#   Determine if user has requested for custom vel range:
#
for i in usrFile:
    usrVelLim = re.search('vel='+'([+-]?\d+.?\d+),([+-]?\d+.?\d+)',i)
    if usrVelLim:
        defaultVels = False  # Don't use defaultVels if user has defined it in usrFile
        velOne = float(usrVelLim.group(1))
        velTwo = float(usrVelLim.group(2))
        if velOne > velTwo:
            velMax = velOne
            velMin = velTwo
        elif velTwo > velOne:
            velMax = velTwo
            velMin = velOne
        elif velOne == velTwo:
            print("User velocities are identical. Reverting to default.")
            defaultVels = True
if defaultVels:              # Default vels are the min/max of the velAvg for each comp.
    velMin = min(velAvg)
    velMax = max(velAvg)



#=====================================================================
#   Each component is assigned a single homogenised vel for all spots,
#   instead of each spot having its own individual vel:
#
for i in range(len(velAvg)):
    for j in vels[i]:
        homoVelTmp.append(velAvg[i])
    homoVel.append(homoVelTmp)
    homoVelTmp = []


#=====================================================================
#   Plot user specified components (version2.0):
#
if 'comp' in usrFile:

    xoffAdd = []
    yoffAdd = []
    peakAdd = []
    velsAdd = []
    compAdd = []

    print("Enter 'q' to quit.")
    print("")
    machineQuery = 'Component ID: '
    response     = input(machineQuery)
    while response != 'q':
        if response == '' or float(response) < 0:
            response = input(machineQuery)
        else:
            usrComp = int(response)
            for i in range(len(comp)):                 # Iterate through the list
                if usrComp == int(comp[i][0]):
                    for j in range(len(xoff[i])):      # Iterate through sub-lists
                        xoffAdd.append(xoff[i][j])
                        yoffAdd.append(yoff[i][j])
                        peakAdd.append(peak[i][j]+1.0)  # Add 1 to ensure that components with flux<1 are not negative when log.
                        velsAdd.append(vels[i][j])
                        compAdd.append(comp[i][j])
            if xoffAdd != []:                           # Catch scrip in-case first choice is empty array
                scatter(xoffAdd,yoffAdd,s=scaleFactor*log(peakAdd),c=velsAdd,vmin=velMin,vmax=velMax)
                if 'atate' in usrFile:
                    for j in range(len(compAdd)):
                        annotate(compAdd[j],xy=(xoffAdd[j],yoffAdd[j]))
                title(str(usrFile[0]))
                xlabel('x offset')
                ylabel('y offset')
                cbar = colorbar()
                cbar.set_label('Velocity')
                gca().invert_xaxis()
                datacursor(hover=True)
                show(block = False)
            response = input(machineQuery)
            clf()
            close()



#=====================================================================
#   Plots entire sequence of compoments:
#
if 'seq' in usrFile:
    print("Enter 'q' to quit.")
    print("")
    for i in range(len(comp)):
        velMin = min(vels[i])
        velMax = max(vels[i])
        peak[i] = [j + 1.0 for j in peak[i]]            # Add 1 to ensure that components with flux<1 are not negative when log.
        scatter(xoff[i],yoff[i],s=scaleFactor*log(peak[i]),c=vels[i],cmap=matplotlib.cm.jet,vmin=velMin,vmax=velMax)
        if 'atate' in usrFile:
            for j in range(len(xoff[i])):
                annotate(comp[i][j],xy=(xoff[i][j],yoff[i][j]))
        title(str(usrFile[0]))
        xlabel('x offset')
        ylabel('y offset')
        cbar = colorbar()
        cbar.set_label('Velocity')
        gca().invert_xaxis()
        datacursor(hover=True)
        show(block = False)

        response = input('Component '+str(comp[i][0])+':')
        if response == 'q':
            exit()
        else:
            clf()
            close()



#=====================================================================
#   Plots spot map of maser emission:
#
if 'plot' in usrFile:
    for i in range(len(chan)):
        peak[i] = [j + 1.0 for j in peak[i]]            # Add 1 to ensure that components with flux<1 are not negative when log.
        scatter(xoff[i],yoff[i],s=scaleFactor*log(peak[i]),c=homoVel[i],cmap=matplotlib.cm.jet,vmin=velMin,vmax=velMax,marker='^')
        if 'atate' in usrFile:
            for j in range(len(xoff[i])):
                annotate(comp[i][j],xy=(xoff[i][j],yoff[i][j]))
    gca().invert_xaxis()
    title(str(usrFile[0]))
    xlabel('x offset')
    ylabel('y offset')
    cbar = colorbar()
    cbar.set_label('Velocity')
    datacursor(hover=True)
    show()



#=====================================================================
#   Plots the spectrum.
#
if 'spec' in usrFile:
    for j in range(len(chan)):
        plot(vels[j],peak[j],marker="o",linewidth=0)
    gca().invert_xaxis()
    title(str(usrFile[0]))
    xlabel('velocity')
    ylabel('flux')
    datacursor(hover=True)
    show()
