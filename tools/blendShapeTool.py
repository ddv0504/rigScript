# -*- coding: utf-8 -*-
from __future__ import print_function
from imp import reload
import maya.cmds as cmds
import maya.mel as mel
from functools import partial
from ztRigUtils import blendShapeUtil as bsu
reload(bsu)

def replaceTarget(*args):
    BSNode       = cmds.textFieldGrp('BSNodeField',q=True,tx=True)
    targetName   = cmds.textFieldGrp('BSTargetField',q=True,tx=True)
    targetObject = cmds.textFieldButtonGrp('BSObjField',q=True,tx=True)
    bsu.replaceBlendShapeTarget(BSNode,targetName,targetObject)

def outPutTarget(*args):
    obj = cmds.textFieldButtonGrp('outPutTargetField',q=True,text=True)
    bsNode = cmds.textFieldButtonGrp('OutputBlendShapeField',q=True,text=True)
    maxVal = int(cmds.textFieldGrp('OutputBlendShapeMaxValue',q=True,text=True))
    if not cmds.objectType(bsNode) == 'blendShape':
        pass
    bsu.outputBSTarget(bsNode,obj,maxVal)

def main(*args):
    if cmds.window('BlendShapeTools',ex=True):
        cmds.deleteUI('BlendShapeTools')
    cmds.window('BlendShapeTools',wh=(450,320))
    cmds.frameLayout('outPutTargetMainLayout',lv=False,l='Output BlendShape Targets')
    cmds.frameLayout('outPutTargetLayout',lv=True,l='Output BlendShape Targets',cll=True)
    cmds.textFieldButtonGrp('outPutTargetField',l='OutputObject:',bl='<<',bc=lambda:cmds.textFieldButtonGrp('outPutTargetField',e=True,text=cmds.ls(sl=True)[0]))
    cmds.textFieldButtonGrp('OutputBlendShapeField',l='BlendShapeNode:',bl='<<',bc=lambda:cmds.textFieldButtonGrp('OutputBlendShapeField',e=True,text=cmds.ls(sl=True)[0]))
    cmds.textFieldGrp('OutputBlendShapeMaxValue',l='Max Value:')
    cmds.button(l='Excute',c=outPutTarget)
    cmds.setParent('..')
    cmds.frameLayout('AddSelectedTargetFrameLayout',lv=True,l='Add Selected BlendShape Targets')
    cmds.textFieldButtonGrp('addBlendShapeTargetField',l='BlendShapeNode:',bl='<<',bc=lambda:cmds.textFieldButtonGrp('addBlendShapeTargetField',e=True,text=cmds.ls(sl=True)[0]))
    cmds.button('AddSelectedTargetBtn',l='addBlendShapeTarget',c=lambda x:bsu.addSelectedTarget(BSNode=cmds.textFieldButtonGrp('addBlendShapeTargetField',q=True,text=True)))
    cmds.setParent('..')
    cmds.frameLayout('BSReplaceLayout',l='BlendShape Replace')
    cmds.columnLayout(cat=('left',0),adj=True)
    cmds.textFieldGrp('BSNodeField',l='BlendShape Node:',cw2=(100,120))
    cmds.textFieldGrp('BSTargetField',l='Target Name:',cw2=(100,120))
    cmds.textFieldButtonGrp('BSObjField',l='Target Object:',bl='Replace',bc=replaceTarget,cw3=(100,120,30))
    cmds.showWindow()