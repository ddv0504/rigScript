#-*- coding: utf-8 -*-
import sys,os
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import pprint
from collections import OrderedDict

def jointDrawUI(*args):
    '''
    jnt: string ; joint name
    style: int ;  0 or 2
    '''
    if cmds.window('jointDrawUI' ,ex=True):
        cmds.deleteUI('jointDrawUI')
    cmds.window('jointDrawUI',wh=(150,100))
    cmds.frameLayout(lv=False)
    cmds.optionMenuGrp('JointStyleMenu',label='Joint Style:',cc=jointDraw)
    cmds.menuItem('None')
    cmds.menuItem('Bone')
    cmds.showWindow()
    
def jointDraw(*args):
    
    if not cmds.ls(sl=True):
        return
    elif not [i for i in cmds.ls(sl=True) if cmds.objectType(i)=='joint']:
        return
    
    value = cmds.optionMenuGrp('JointStyleMenu',q=True,sl=True)
    print(value)
    if value == 2:
        [cmds.setAttr('%s.drawStyle' % i,0) for i in cmds.ls(sl=True)]
    else:
        [cmds.setAttr('%s.drawStyle' % i,2) for i in cmds.ls(sl=True)]

def displayType():
    if cmds.window('dtWin', exists=True):
        cmds.deleteUI('dtWin')
    cmds.window('dtWin', title='Display Type', maximizeButton=False, minimizeButton=False)
    cmds.columnLayout()
    cmds.optionMenu('dtOptMenu', label='Display Type: ', cc=dtChangeCmd)
    cmds.menuItem(label='Normal')
    cmds.menuItem(label='Template')
    cmds.menuItem(label='Reference')
    cmds.showWindow('dtWin')

def dtChangeCmd(*args):
    opt = cmds.optionMenu('dtOptMenu', q=True, v=True)
    if opt == 'Normal':
        opt = 0
    elif opt == 'Template':
        opt = 1
    elif opt == 'Reference':
        opt = 2
    selList = cmds.ls(sl=True)
    for sel in selList:
        shps = cmds.listRelatives(sel, s=True)
        if not shps:
            return
        for shp in shps:
            try:
                cmds.setAttr('%s.overrideEnabled' % shp, 1)
            except:
                pass
            try:
                cmds.setAttr('%s.overrideDisplayType' % shp, opt)
            except:
                cmds.error('Same shape name exists.')

def dupMatAndAssign():
    selGeoLs = cmds.ls(sl=True)

    # Get materials
    srcMats = []
    for selGeo in selGeoLs:
        selGeoMat = getMatFromSel(selGeo)
        srcMats.extend(selGeoMat)
    srcMats = list(set(srcMats))

    for srcMat in srcMats:
        cmds.select(srcMat, r=True)
        cmds.hyperShade(duplicate=True)
        
def getMatFromSel(obj):
    """ Get material From selected object """

    shapeName = cmds.listRelatives(obj, ni=True, path=True, s=True)

    if shapeName:
        sgName = cmds.listConnections(shapeName[0], d=True, type="shadingEngine")
        matName = [mat for mat in cmds.ls(cmds.listConnections(sgName), materials=True) if not cmds.nodeType(mat) == 'displacementShader']

        return list(set(matName))

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


###### blenShape #######
'''
Get connected blendshape node 
'''
def getBlendShapeNodes(obj):       
    history = cmds.listHistory(obj)
    bs = cmds.ls(history,type='blendShape')

    return bs     
'''
Blendshape command 
'''
def blendShape():
    src,trg = cmds.ls(sl=True)
    bsName = cmds.blendShape(name='%s_blendShape'%src,origin='world')
    return bsName

def setBlendShapeWeight(bsNode,val):
    bsNode = pm.ls(bsNode)[0]
    attr , weight = bsNode.listAliases()[0]
    bsNode.setAttr(attr,val)

def selectChirdrenNursCurve(): # 하위 넓스 커브를 전부 선택
    cmds.select([cmds.listRelatives(i,p=True)[0] for i in cmds.ls(sl=True,dag=True,type='nurbsCurve')])

def createControlDrv(): #실제 컨트롤러를 제어할 locator 생성
    objs = cmds.ls(sl=True)
    for obj in objs:
        locator = cmds.spaceLocator(name='%s_DrvCons' % obj) 
        cmds.matchTransform(locator,obj)
        drvGroup = obj.replace(obj.split("_")[-1],'drv')

        cmds.parentConstraint(locator,drvGroup,mo=False)

def getBlendShapeNode(obj):
    shape = cmds.listRelatives(obj,c=True,type='shape')[0]
    bsNode = cmds.listConnections(shape,source=True,type='blendShape')[0]
    
    return bsNode

def getBlendShapeWeights(obj):    
    bsNode = getBlendShapeNode(obj)    
    VertexNb = cmds.polyEvaluate(obj, v=1)    
    weightLst = cmds.getAttr('{0}.inputTarget[0].baseWeights[0:{1}]'.format(bsNode, VertexNb))
    return weightLst

def setBlendShapeWeights(obj,weightLst):
    bsNode = getBlendShapeNode(obj)
    
    VertexNb = cmds.polyEvaluate(obj, v=1)    
    cmds.setAttr('{0}.inputTarget[0].baseWeights[0:{1}]'.format(bsNode, VertexNb),*weightLst)  

def addSelectionAsTarget(bsNode,newNodeName=None):
    try:
        bsNode = [i for i in pm.ls(bsNode) if pm.objectType(i.name()) == 'blendShape'][0]
        mel.eval('doBlendShapeAddSelectionAsTarget %s 1 1 "" 1 1;' % (bsNode.name()))
        last_used_index = pm.blendShape(bsNode, q=True, weightCount=True)
        new_target_index = 0 if last_used_index == 0 else last_used_index - 1
        if newNodeName:
            
            attr = bsNode.listAliases()[new_target_index][1]
            pm.aliasAttr(newNodeName,attr)
        
    except Exception as e:
        print(e)
        return

###### vertex operation ##########
def getVtxPos( shapeNode ) :
     
	vtxWorldPosition = []    # will contain positions un space of all object vertex
 
	vtxIndexList = cmds.getAttr( shapeNode+".vrts", multiIndices=True )
 
	for i in vtxIndexList :
		curPointPosition = cmds.xform( str(shapeNode)+".pnts["+str(i)+"]", query=True, translation=True, worldSpace=True )    # [1.1269192869360154, 4.5408735275268555, 1.3387055339628269]
		vtxWorldPosition.append( curPointPosition )
 
	return vtxWorldPosition

def setVtxPos( shapeNode, valueLst=None):
    cmds.undoInfo(ock=True,chunkName='verticsMatch')
    if valueLst:
        for index,value in enumerate(valueLst):
            cmds.xform(str(shapeNode)+".pnts["+str(index)+"]",translation=value,worldSpace=True)
    cmds.undoInfo(cck=True)
    

###### Matrix #########

def setDefaultMatrix(node,*args):
    defaultMatrix =[1.0,0.0,0.0,0.0,
                    0.0,1.0,0.0,0.0,
                    0.0,0.0,1.0,0.0,
                    0.0,0.0,0.0,1.0 ]
    cmds.setAttr('%s.offsetParentMatrix' % node,defaultMatrix,type='matrix')
