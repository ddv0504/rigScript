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

from pymel.core import*
from maya import cmds        


def bt_resetSettings(*args):

    cmds.optionVar( iv=('bt_controlType', 1), )   
    cmds.optionVar( iv=('bt_circleSize', 1), )   
    cmds.optionVar( fv=('bt_circleR', 0), )   
    cmds.optionVar( fv=('bt_circleG', 1), )   
    cmds.optionVar( fv=('bt_circleB', 0), )  
    cmds.optionVar( iv=('bt_circleOrient', 1), )   
    cmds.warning('Close and reopen Create Circle Control window for reset settings to update')
    cmds.inViewMessage( amg='Close and reopen Create Circle Control window for reset settings to update.', pos='midCenter', fade=True )
    
def bt_setControlType(*args):

    controlType=cmds.radioButtonGrp('controlType', q=1, sl=1 )
    cmds.optionVar( iv=('bt_controlType', controlType), )   
     
         
def bt_setCircleSize(*args):

    circleSize=cmds.floatSliderGrp('circleSize', q=1, v=1)
    cmds.optionVar( fv=('bt_circleSize', circleSize), )   
     

def bt_setCircleRGB(*args):

    circleRGB=cmds.colorSliderGrp('circleRGB', q=1, rgb=1)
    cmds.optionVar( fv=('bt_circleR', circleRGB[0]), )   
    cmds.optionVar( fv=('bt_circleG', circleRGB[1]), )   
    cmds.optionVar( fv=('bt_circleB', circleRGB[2]), )   
     

def bt_setCircleOrientation(*args):
    
    circleOrientation=cmds.radioButtonGrp('circleOrientation', q=1, sl=1 )
    cmds.optionVar( iv=('bt_circleOrient', circleOrientation), )   


def bt_makeControl(*args):

    # Creates curve controls and align with selected joints

    # initialize type
    if (cmds.optionVar( ex=('bt_controlType') ) ):
        controlType = cmds.optionVar( q=('bt_controlType') )    
    else:
        controlType=1
        
    # initialize size    
    if (cmds.optionVar( ex=('bt_circleSize') ) ):
        circleSize = cmds.optionVar( q=('bt_circleSize') )    
    else:
        circleSize=1
    
    # initialize color
    circleRGB=[0,1,0]
    if (cmds.optionVar( ex=('bt_circleR') ) ):
        circleRGB[0] = cmds.optionVar( q=('bt_circleR') )    
    else:
        circleRGB[0]=0
    if (cmds.optionVar( ex=('bt_circleG') ) ):
        circleRGB[1] = cmds.optionVar( q=('bt_circleG') )    
    else:
        circleRGB[1]=1
    if (cmds.optionVar( ex=('bt_circleB') ) ):
        circleRGB[2] = cmds.optionVar( q=('bt_circleB') )    
    else:
        circleRGB[2]=0    
    
    # initialize up axis  
    if (cmds.optionVar( ex=('bt_circleOrient') ) ):
        circleOrientation = cmds.optionVar( q=('bt_circleOrient') )    
    else:
        circleOrientation=1      
    
    if circleOrientation==2: # Y up
        xUp=0
        yUp=1
        zUp=0
    
    elif circleOrientation==3: # Z up
        xUp=0
        yUp=0
        zUp=1
    
    else: #default to X
        xUp=1
        yUp=0
        zUp=0
        

    selectedTransforms=cmds.ls(sl=1, tr=1) #filter for joints/transforms

    if len(selectedTransforms) == 0:
        cmds.warning( "No joints or transforms selected. Select 1 or more joints/transforms and try again." )

    else:

        # tag a control objects here

        for item in range (len(selectedTransforms)):

            #create circle curve
            circleCurve=cmds.circle( normal=(xUp, yUp, zUp), radius=circleSize, center=(0, 0, 0), name=(selectedTransforms[item] + '_controlCurve')  )
            #create and attach controller node
            #cmds.controller(circle)
            cmds.createNode ('controller', n=(selectedTransforms[item] + '_controlCurve_tag'))
            cmds.connectAttr ((selectedTransforms[item] + '_controlCurve.message'), (selectedTransforms[item] + '_controlCurve_tag.controllerObject'))


            #set color for wireframe override 
            cmds.select (circleCurve)
            selected()[0].getShape().overrideEnabled.set(1)
            selected()[0].getShape().overrideRGBColors.set(1)
            selected()[0].getShape().overrideColorRGB.set(circleRGB)  
            
            #temporarily orient with joint via a constraint
            #cmds.select (circleCurve[0],r=1)
            #cmds.select (selectedTransforms[item],add=1)
            #cmds.MatchTranslation
            #cmds.MatchRotation
            
            
            offsetParent = cmds.group( circleCurve , name = (selectedTransforms[item] + '_controlOffset') )
            tmpParentConst = cmds.parentConstraint(selectedTransforms[item], offsetParent, w=1, maintainOffset = False)
            cmds.delete (tmpParentConst[0])

                

            if(controlType == 2):
                #experimental - zero out t and r, move rot values to local axis
                #tmpRotX = cmds.getAttr(circleCurve[0]+'.rotateX') 
                #tmpRotY = cmds.getAttr(circleCurve[0]+'.rotateY') 
                #tmpRotZ = cmds.getAttr(circleCurve[0]+'.rotateZ') 
                #cmds.setAttr(circleCurve[0]+'.rotateAxisX', tmpRotX)
                #cmds.setAttr(circleCurve[0]+'.rotateAxisY', tmpRotY)
                #cmds.setAttr(circleCurve[0]+'.rotateAxisZ', tmpRotZ)
                #cmds.setAttr(circleCurve[0]+'.rotateX', 0)
                #cmds.setAttr(circleCurve[0]+'.rotateY', 0)
                #cmds.setAttr(circleCurve[0]+'.rotateZ', 0)               
                #cmds.select (circleCurve, r=1)
                #cmds.makeIdentity( apply=True, t=1, r=1, s=0, n=0, pn=1 )
                
                #constrain joint to curve
                cmds.parentConstraint(circleCurve, selectedTransforms[item], w=1, maintainOffset=1)
            else:
                #parent curve shape under joint transform for direct connection
                cmds.select (circleCurve)
                select (selected()[0].getShape())
                tempShape = ls(sl=1)
                cmds.parent (tempShape, selectedTransforms[item], r=1, s=1)
                cmds.delete (circleCurve)
                cmds.delete (offsetParent)                             

        # if contraint mode and if applying to a hierarchy then group control curves accordingly
        if(controlType == 2):
            for item in range (len(selectedTransforms)):
                parent=cmds.listRelatives (selectedTransforms[item], parent=1)
                if parent != None:
                    if cmds.objExists(parent[0]+'_controlCurve'):
                        #create hierarchy
                        cmds.parent(selectedTransforms[item] + '_controlOffset', parent[0] + '_controlCurve')
                        #create control nodes selection hierarchy
                        cmds.controller ((selectedTransforms[item] + '_controlCurve'), (parent[0] + '_controlCurve'), p=1)

        cmds.select(cl=1)
        numCurves = len(selectedTransforms)
        print('Created ', numCurves, 'control curves.')



def bt_createCircleControl(*args):

    # initialize type
    if (cmds.optionVar( ex=('bt_controlType') ) ):
        controlType = cmds.optionVar( q=('bt_controlType') )    
    else:
        controlType=1
        
    # initialize size    
    if (cmds.optionVar( ex=('bt_circleSize') ) ):
        circleSize = cmds.optionVar( q=('bt_circleSize') )    
    else:
        circleSize=1
    
    # initialize color
    circleRGB=[0,1,0]
    if (cmds.optionVar( ex=('bt_circleR') ) ):
        circleRGB[0] = cmds.optionVar( q=('bt_circleR') )    
    else:
        circleRGB[0]=0
    if (cmds.optionVar( ex=('bt_circleG') ) ):
        circleRGB[1] = cmds.optionVar( q=('bt_circleG') )    
    else:
        circleRGB[1]=1
    if (cmds.optionVar( ex=('bt_circleB') ) ):
        circleRGB[2] = cmds.optionVar( q=('bt_circleB') )    
    else:
        circleRGB[2]=0    
    
    # initialize up axis  
    if (cmds.optionVar( ex=('bt_circleOrient') ) ):
        circleOrientation = cmds.optionVar( q=('bt_circleOrient') )    
    else:
        circleOrientation=1  
        
    # Setup UI   
    if cmds.window('CircleControlWin', ex=1):
        cmds.deleteUI('CircleControlWin', wnd=1)
        #cmds.windowPref ('CircleControlWin', r=1)
    
    
    window=cmds.window( 'CircleControlWin', t="Create Circle Control", w=350, s=0,  mb=1 )

    cmds.menu( label='Edit', tearOff=False )
    cmds.menuItem( label='Reset Settings', command='bt_resetSettings()' )
    
    cmds.columnLayout( adj=1 )
    cmds.separator() 
    cmds.text (' ')
    cmds.text ('Select one or more joints / transforms then apply to create circle controller for each.')
    cmds.text (' ')
    cmds.separator( st='single' )
    cmds.radioButtonGrp( 'controlType', l='Control Type:    ', cw=(2,150), la2=['Shape Under Transform', 'Parent Constraint'], nrb=2, sl=controlType , onc=bt_setControlType)
    cmds.floatSliderGrp( 'circleSize', l='Circle Size:    ', f=1, min=0.1, max=20.0, fmn=1.0, fmx=100.0, v=circleSize, dc=bt_setCircleSize, cc=bt_setCircleSize)
    cmds.colorSliderGrp( 'circleRGB', l='Circle Color:    ', rgb=circleRGB , dc=bt_setCircleRGB, cc=bt_setCircleRGB)
    cmds.radioButtonGrp( 'circleOrientation', l='Circle Orientation:    ', la3=['X Up', 'Y Up', 'Z Up'], nrb=3, sl=circleOrientation, onc=bt_setCircleOrientation )
    cmds.text (' ')
    cmds.setParent('..')
    
    cmds.columnLayout( adjustableColumn=1 )
    cmds.separator() 
    cmds.setParent('..')
    
    cmds.rowColumnLayout(nc=3,co=(2,'both',5), adj=2 )
    cmds.button( l='Create Circle', w=150 , c=('bt_makeControl(), cmds.deleteUI(\"' + window + '\", window=1)') )
    cmds.button( l='Apply' , w=150, c=bt_makeControl )
    cmds.button( l='Close', w=150, c =('cmds.deleteUI(\"' + window + '\", window=1)') )
    cmds.setParent( '..' )
    
    
    cmds.showWindow( 'CircleControlWin' )
    
 
  
# Open Create Circle Control UI  

bt_createCircleControl()