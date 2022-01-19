# Copyright(C) 1997-2020 Autodesk, Inc., and/or its licensors.
# All rights reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Autodesk, Inc. ("Autodesk") and/or its licensors,
# which is protected by U.S. and Canadian federal copyright law and by
# international treaties.
#
# The Data is provided for use exclusively by You. You have the right to use,
# modify, and incorporate this Data into other products for purposes authorized
# by the Autodesk software license agreement, without fee.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. AUTODESK
# DOES NOT MAKE AND HEREBY DISCLAIMS ANY EXPRESS OR IMPLIED WARRANTIES
# INCLUDING, BUT NOT LIMITED TO, THE WARRANTIES OF NON-INFRINGEMENT,
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, OR ARISING FROM A COURSE
# OF DEALING, USAGE, OR TRADE PRACTICE. IN NO EVENT WILL AUTODESK AND/OR ITS
# LICENSORS BE LIABLE FOR ANY LOST REVENUES, DATA, OR PROFITS, OR SPECIAL,
# DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES, EVEN IF AUTODESK AND/OR ITS
# LICENSORS HAS BEEN ADVISED OF THE POSSIBILITY OR PROBABILITY OF SUCH DAMAGES.
#
# Author: Steven T. L. Roselle
# Last updated: 2020/10/13
#

from maya.cmds import *
import maya.api.OpenMaya as om
import bt_flattenComponentsUtils as utils

def bt_curveToRibbonMesh():
    select(filterExpand(sm=9),r=True)
    sel = ls(sl=True)
    if len(sel) == 0:
        warning('Select one or more curves\n')
        return

    allInstances = []
    allProfiles = []
    allMeshes = []

    for crv in sel:

        # Create unique profile curvve
        curve(p=[(0, -0.25, 0.5), (0, 0.5, 0.5), (0, 0.5, -0.5), (0, -0.25, -0.5)] )
        profileCurve = ls(sl=True)

        # Move pivot of curve to first CV
        origin = om.MPoint(pointPosition('{}.cv[0]'.format(crv), w=1))
        print(origin)
        node = utils.nameToNode(crv)
        transform = om.MFnTransform(node)
        transform.setRotatePivot(origin, om.MSpace.kObject, False)
        transform.setScalePivot(origin, om.MSpace.kObject, False)

        # instance curve and move to origin
        curveInstance = instance(crv, n='{}_instance#'.format(crv))
        move(0,0,0, curveInstance, rpr=1)
        attrs = { 'rx': 0, 'ry': 0, 'rz' : 0, 'sx' : 1, 'sy' : 1, 'sz': 1 }
        for k,v in attrs.items():
            setAttr('{}.{}'.format(curveInstance[0],k),v)
        allInstances.append(curveInstance[0])
        allProfiles.append(profileCurve[0])

        # extrude curve with profiler
        select(profileCurve[0], curveInstance,r=1)
        extrudeResult = extrude(ch=1, rn=0, po=1, et=2, ucp=2, fpt=1, upn=1, rotation=0, scale=0, rsp=1, name='ribbonMesh#')
        extrudedSurface = ls(sl=True)
        print(extrudedSurface[0])
        addAttr(longName='width',min=0.01,at='double',dv=1)
        addAttr(longName='curvature',min=-1,max=1,at='double',dv=0)
        addAttr(longName='orientation',min=-360,max=360,at='long',dv=1)
        addAttr(longName='taper',min=0,at='double',dv=1)
        addAttr(longName='twist',at='double',dv=1)
        addAttr(longName='lengthDivisionSpacing',at='enum',enumName="uniform=1:non-uniform=2", dv=1)
        addAttr(longName='lengthDivisions',min=1,at='long',dv=7)
        addAttr(longName='widthDivisions',min=4,at='long',dv=7)

        setAttr('{}.width'.format(extrudedSurface[0]),e=1,k=1)
        setAttr('{}.curvature'.format(extrudedSurface[0]),e=1,k=1)
        setAttr('{}.orientation'.format(extrudedSurface[0]),e=1,k=1)
        setAttr('{}.taper'.format(extrudedSurface[0]),e=1,k=1)
        setAttr('{}.twist'.format(extrudedSurface[0]),e=1,k=1)
        setAttr('{}.widthDivisions'.format(extrudedSurface[0]),e=1,k=1)
        setAttr('{}.lengthDivisions'.format(extrudedSurface[0]),e=1,k=1)
        setAttr('{}.lengthDivisionSpacing'.format(extrudedSurface[0]),e=1,k=1)

        connectAttr('{}.taper'.format(extrudedSurface[0]), '{}.scale'.format(extrudeResult[1]))
        connectAttr('{}.twist'.format(extrudedSurface[0]), '{}.rotation'.format(extrudeResult[1]))
        allMeshes.append(extrudedSurface[0])

        # Setup nurbsTesselate node
        extrudeInput = listConnections(extrudeResult[1])
        print(extrudeInput)
        setAttr('{}.format'.format(extrudeInput[0]), 2)
        setAttr('{}.uType'.format(extrudeInput[0]), 1) # uniform
        setAttr('{}.polygonType'.format(extrudeInput[0]), 1) 

        connectAttr('{}.widthDivisions'.format(extrudedSurface[0]), '{}.uNumber'.format(extrudeInput[0]))
        connectAttr('{}.lengthDivisions'.format(extrudedSurface[0]), '{}.vNumber'.format(extrudeInput[0]))
        connectAttr('{}.lengthDivisionSpacing'.format(extrudedSurface[0]), '{}.vType'.format(extrudeInput[0]))

        connectAttr('{}.width'.format(extrudedSurface[0]), '{}.sx'.format(profileCurve[0]))
        connectAttr('{}.curvature'.format(extrudedSurface[0]), '{}.sy'.format(profileCurve[0]))
        connectAttr('{}.width'.format(extrudedSurface[0]), '{}.sz'.format(profileCurve[0]))
        connectAttr('{}.orientation'.format(extrudedSurface[0]), '{}.rx'.format(profileCurve[0]))

        # constrain extrude to target curve position
        select(crv, extrudedSurface[0], r=1)
        pointConstraint(w=1)
        orientConstraint(o=(0, 0, 0), w=1)
        scaleConstraint(mo=0, w=1)

    if(ls('ribbonCurveHistory')):
        select(allProfiles, allInstances, 'ribbonCurveHistory', r=1)
        parent()
    else:
        hide(group(allProfiles, allInstances, w=1, name='ribbonCurveHistory'))

    if(ls('ribbonMeshes')):
        select(allMeshes, 'ribbonMeshes', r=1)
        parent()
    else:
        group(allMeshes, w=1, name='ribbonMeshes')

    select(allMeshes, r=1)
