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
# created by John Creson 2013
# updated by Steven Roselle 2019

import maya.cmds as cmds
import maya.mel as mel
import maya.utils as utils

def bt_addTransparencyAttr():
    selection = []
    shaders={}
    thisBlend=[]
    thisSpecBlend=[]
    thisBlendList=[]

    if cmds.ls(sl=True):
        selection = cmds.ls(sl=True)
            
        for object in selection:
            cmds.select(object, r=True)
            shader = cmds.ls(cmds.listConnections(cmds.listConnections(cmds.ls(sl=True, o=True, dag=True, s=True), type = "shadingEngine")), mat=True)[0]
            if shader not in list(shaders.keys()):
                shaders[shader]=[]
            shaders[shader].append(object)

        for shader in list(shaders.keys()):
            switches = cmds.listConnections(shader,shaders[shader],type="tripleShadingSwitch",c=True)
            ticks = 0
            sticks = 0
            if switches:
                for member in switches:
                    if str(member).startswith("trans"):
                        switch = member
                        ticks = 1

                    if str(member).startswith("specs"):
                        switchs = member
                        sticks = 1

            if (ticks == 0):
                switch = cmds.shadingNode ("tripleShadingSwitch", asUtility=True, name = "transAttrTripleShadingSwitch1")
                cmds.setAttr( switch+".default", 0,0,0, type="double3" )
                cmds.connectAttr(switch+".output", shader+".transparency", force=True)
            if (sticks == 0):
                if  cmds.attributeQuery("specularColor", node = shader,exists=True):       
                    switchs = cmds.shadingNode ("tripleShadingSwitch", asUtility=True, name = "specsAttrTripleShadingSwitch1")
                    cmds.setAttr( switchs+".default", *cmds.getAttr(shader+".specularColor")[0], type="double3" )
                    cmds.connectAttr(switchs+".output", shader+".specularColor", force=True)

            if cmds.listConnections(switch,source = True, type = "blendColors"):
                index=len(cmds.listConnections(switch,source = True, type = "blendColors"))
            else:
                index=0

            for object in shaders[shader]:
                objectShape = cmds.listRelatives(object, shapes=True)[0]
                if not(cmds.attributeQuery("Transparency",node=object,exists=True)):
                    cmds.addAttr(object, shortName="tr", longName="Transparency", defaultValue=1.0, minValue=0, maxValue=1)
                    cmds.setAttr(object+".Transparency",e=True,keyable=True)
                if not (cmds.listConnections(object,type="blendColors",c=True)):
                    thisBlend = cmds.shadingNode ("blendColors", asUtility=True, name = "transBlendColors1")
                    cmds.setAttr(thisBlend+".color1",  0,0,0, type="double3" )
                    cmds.setAttr(thisBlend+".color2",  1,1,1, type="double3" )
                    cmds.setAttr(thisBlend+".blender",  0)
                    cmds.connectAttr(object+".Transparency", thisBlend+".blender")
                else:
                    thisBlendList = cmds.listConnections(object,type = "blendColors")
                    thisBlend = [blender for blender in thisBlendList if str(blender).startswith("trans")] [0]

                if cmds.attributeQuery("specularColor", node = shader,exists=True): 
                    if len([blender for blender in thisBlendList if str(blender).startswith("specs")])>0:
                        thisSpecBlend = [blender for blender in thisBlendList if str(blender).startswith("specs")][0]
                    if len( [blender for blender in thisBlendList if str(blender).startswith("specs")])==0:
                        thisSpecBlend = cmds.shadingNode ("blendColors", asUtility=True, name = "specsBlendColors1")  
                        print(thisSpecBlend)
                        cmds.setAttr(thisSpecBlend+".color2",  0, 0, 0, type="double3" )
                        cmds.setAttr(thisSpecBlend+".color1",  *cmds.getAttr(shader+".specularColor")[0], type="double3" )
                        cmds.setAttr(thisSpecBlend+".blender",  0)
                        cmds.connectAttr(object+"Transparency", thisSpecBlend+".blender") 
                  
                if (index>1):
                    if cmds.listConnections(switch, source = True,type="blendColors"):
                        index = len(cmds.listConnections(switch, source = True,type="blendColors"))

                if cmds.listConnections(switch, source = True, type = "blendColors"):
                    if (thisBlend not in cmds.listConnections(switch, source = True, type = "blendColors")):
                        cmds.connectAttr(objectShape+".instObjGroups", switch+".input["+str(index)+"].inShape")
                        cmds.connectAttr(thisBlend+".output", switch+".input["+str(index)+"].inTriple")
                    if  cmds.attributeQuery("specularColor", node = shader,exists=True):  
                        if  not cmds.listConnections(switchs, source = True, type = "blendColors"): 
                            cmds.connectAttr(thisSpecBlend+".output", switchs+".input["+str(index)+"].inTriple")
                        elif (thisSpecBlend not in cmds.listConnections(switchs, source = True, type = "blendColors")):
                            cmds.connectAttr(thisSpecBlend+".output", switchs+".input["+str(index)+"].inTriple")
                        if (switchs not in cmds.listConnections(objectShape, source = True)):
                            cmds.connectAttr(objectShape+".instObjGroups", switchs+".input["+str(index)+"].inShape")
                else:
                    cmds.connectAttr(objectShape+".instObjGroups", switch+".input["+str(index)+"].inShape")
                    cmds.connectAttr(thisBlend+".output", switch+".input["+str(index)+"].inTriple")
                    if  cmds.attributeQuery("specularColor", node = shader,exists=True): 
                        cmds.connectAttr(objectShape+".instObjGroups", switchs+".input["+str(index)+"].inShape")
                        if (switchs not in cmds.listConnections(thisSpecBlend, source = True)):
                            cmds.connectAttr(thisSpecBlend+".output", switchs+".input["+str(index)+"].inTriple")
                        
                index=index+1
        cmds.select(selection, r=True)
        cmds.inViewMessage(smg="Viewport must be in shaded+textured mode to see Transparency - 6 key to enable.", pos="midCenter", bkc=0x11111111, alpha=0.5, fade=1, fst=5000)
        cmds.warning("Set Transparency attribute in ChannelBox. Viewport must be in shaded+textured mode to see Transparency - 6 key to enable.")
        
    else:
        print("Please make a selection to create/update Transparency attrs.")
