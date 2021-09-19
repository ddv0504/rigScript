# Copyright (C) 1997-2020 Autodesk, Inc., and/or its licensors.
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
# Author:   Steven T. L. Roselle    
#
# Created:        ( 04/01/15 )

from pymel.core import *
import maya.cmds as cmds


def bt_createMeshLocator():
    
    locObj = polyCube(w=0.2, h=0.2, d=0.2, name='polyLocator1')
    select(locObj,r=1)
    extNode = polyExtrudeFacet(kft=0, thickness=1)
    select(locObj,r=1)
    polySoftEdge(a=0, ch=1)
    select(locObj,r=1)
    setAttr((locObj[0]+'.displayHandle'),1)
    
    addAttr(locObj[0],ln='length', min=.01, dv=1)
    setAttr((locObj[0]+'.length'),keyable=1)
    
    addAttr(locObj[0],ln='thickness', min=.01, dv=0.1)
    setAttr((locObj[0]+'.thickness'),keyable=1)
    
    #setAttr((locObj[0]+'.sx'),keyable=0, lock=1)
    #setAttr((locObj[0]+'.sy'),keyable=0, lock=1)
    #setAttr((locObj[0]+'.sz'),keyable=0, lock=1)
    
    connectAttr((locObj[0]+'.length'),(extNode[0]+'.thickness'))
    connectAttr((locObj[0]+'.thickness'),(locObj[1]+'.width'))
    connectAttr((locObj[0]+'.thickness'),(locObj[1]+'.height'))
    connectAttr((locObj[0]+'.thickness'),(locObj[1]+'.depth'))
    
    
    if (objExists('locatorShader') == 1):
        print ('\nUsing existing locatorShader\n') 
    else:
        shader = shadingNode('lambert', asShader=1, name='locatorShader');
        shader.setColor( [0,0,1] )
        
    select(locObj,r=1)
    hyperShade(assign='locatorShader')    


