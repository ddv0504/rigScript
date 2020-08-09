'''
author: wuzhengtian
email : wuzhengtian2@gmaile.com

description:

    Usage common rigging util.
'''
import maya.cmds as cmds
import pymel.core as pm


def constraint(src,trg,translate=False,rotate=False,scale=False,mo=False):
    
    if mo:
        newSrc = cmds.createNode('transform' ,name = '%s_src' % trg)
        cmds.parent(newSrc,src)
        cmds.matchTransform(newSrc,trg)
          
        src = newSrc
        srcParent = [i for i in cmds.listRelatives(src,p=True)][0]
        
    multMatrix = cmds.shadingNode('multMatrix'  ,asUtility=True,name='%s_multiMatrix' % src)
    decMatrix  = cmds.shadingNode('decomposeMatrix',asUtility =True, name = '%s_decomposeMatrix' % src)

    cmds.connectAttr('%s.worldMatrix[0]' % src,'%s.matrixIn[0]' % multMatrix,f=True)
    cmds.connectAttr('%s.matrixSum' % multMatrix,'%s.inputMatrix' % decMatrix,f=True)
    cmds.connectAttr('%s.parentInverseMatrix[0]' % trg, '%s.matrixIn[1]' % multMatrix ,f=True)
    
    if translate:            
        cmds.connectAttr('%s.outputTranslate' % decMatrix , '%s.translate' % trg,f=True)
                    
    if rotate:        
        cmds.connectAttr('%s.outputRotate' % decMatrix , '%s.rotate' % trg,f=True)
           
    if scale:
        cmds.connectAttr('%s.outputScale' % decMatrix , '%s.scale' % trg,f=True)           
    
    if mo:
        cmds.select([i for i in cmds.listRelatives(src,p=True)][0])        
    else:
        cmds.select(src,r=True)
        

