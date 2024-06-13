#-*- coding: utf-8 -*-
import sys,os
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import pprint
from collections import OrderedDict
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

######## attribute operation #######

def addAttr(object,longName,type,default=0,min=0,max=1,parent=None):
    '''
    param:
            longName:  Attribute long name
            type:   vector=> "double3"
                    proxy=> "object.attribute"
                    float=> "double"
                    matrix=> "matrix"
                    string=> "message"
                    attribute frame=>  "compound"  ex: use to parent
                    
            default: Default value
            min: Minimize value
            max: Maximize value
            parent : "parent" ex: parent to compound attribute
            usedAsColor : Color slideing value ex: cmds.addAttr( longName='rainbow', usedAsColor=True, attributeType='float3' )
                                                   cmds.addAttr( longName='redBow', attributeType='float', parent='rainbow' )
                                                   cmds.addAttr( longName='greenBow', attributeType='float', parent='rainbow' )
                                                   cmds.addAttr( longName='blueBow', attributeType='float', parent='rainbow' )
    '''
    
    if type=='float3':
        cmds.addAttr(object,longName=longName,attributeType=type,usedAsColor=True)
    elif parent:
        cmds.addAttr(object,longName=longName,attributeType=type,parent=parent)
    else:
        cmds.addAttr(object,longName=longName,attributeType=type,dv=default,min=min,max=max)

######## joint operation ########
def displayJointOrient(joint):
    cmds.setAttr('%s.jointOrientX' % joint,e=True,k=True)
    cmds.setAttr('%s.jointOrientY' % joint,e=True,k=True)
    cmds.setAttr('%s.jointOrientZ' % joint,e=True,k=True)
    
def hideJointOrient(joint):
    cmds.setAttr('%s.jointOrientX' % joint,e=True,k=False)
    cmds.setAttr('%s.jointOrientY' % joint,e=True,k=False)
    cmds.setAttr('%s.jointOrientZ' % joint,e=True,k=False)
    
def rotToOrient(joint):
    orientX = cmds.getAttr('%s.jointOrientX' % joint)
    orientY = cmds.getAttr('%s.jointOrientY' % joint)
    orientZ = cmds.getAttr('%s.jointOrientZ' % joint)
    
    rotX = cmds.getAttr('%s.rx' % joint)
    rotY = cmds.getAttr('%s.ry' % joint)
    rotZ = cmds.getAttr('%s.rz' % joint)
    
    valX = orientX + rotX
    valY = orientY + rotY
    valZ = orientZ + rotZ
    
    cmds.setAttr('%s.rotate' % joint,0,0,0)
    
    cmds.setAttr('%s.jointOrientX' % joint, valX)
    cmds.setAttr('%s.jointOrientY' % joint, valY)
    cmds.setAttr('%s.jointOrientZ' % joint, valZ)


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
def setOrientKeyable(jnt,axis,*args):
    if not cmds.objectType(jnt) == 'joint':
        print('%s is not joint object.' % jnt)
    cmds.setAttr('%s.jointOrient%s' % (jnt,axis),keyable=True,e=True)

def setJointsOrientKeyable(jnts,*args):
    attrs = ['jointOrientX','jointOrientY','jointOrientZ']
    for jnt in jnts:
        for attr in attrs:
            print(attr)
            cmds.setAttr('%s.%s' % (jnt,attr),e=True,keyable=True)

def setJointsOrientUnkeyable(jnts,*args):
    attrs = ['jointOrientX','jointOrientY','jointOrientZ']
    for jnt in jnts:
        for attr in attrs:
            cmds.setAttr('%s.%s' % (jnt,attr),e=True,keyable=False)

def animPathJnt(curve,jntLst=None,auto=False,target=None):
    if jntLst:
        value = 0
        step = 1/len(jntLst)
        cmds.select(cl=True)
        if jntLst:
            for jnt in jntLst:            
                cmds.select([jnt,curve],r=True)
                node = cmds.pathAnimation(n='%s_motionPath' % jnt,fractionMode=True,follow=True,followAxis='x',upAxis='y',worldUpType="vector",worldUpVector=(0,1,0),inverseUp=False,inverseFront=False,bank=False)
                cmds.setAttr('%s.uValue' % node,value)
                value += step
        return
    curve = pm.ls(curve)[0]
    curveShape = curve.getShape()
    curveShape.getCVs()
    if auto:
        value = 0
        step = 1.0/curveShape.numEPs()
        for ep in range(curveShape.numEPs()):
            cmds.select(cl=True)
            jntIndex = str(ep).zfill(3)
            jnt = cmds.joint(n='curve_%s' % jntIndex)
            cmds.select([jnt,curve.name()],r=True)
            node = cmds.pathAnimation(n='%s_motionPath' % jnt,fractionMode=True,follow=True,followAxis='x',upAxis='y',worldUpType="vector",worldUpVector=(0,1,0),inverseUp=False,inverseFront=False,bank=False)
            cmds.setAttr('%s.uValue' % node,value)
            if target:
                cmds.connectAttr('%s.worldMatrix' % target, '%s.worldUpMatrix' % node,f=True)
            value+=step
            
def createJntToCurve(curve):

    curve = pm.ls(sl=True)[0]
    curveShape = curve.getShape()
    curveShape.getCVs()

    for ep in range(curveShape.numEPs()):
        cmds.select(cl=True)
        editPoint = '%s.ep[%s]' % (curve.name(),ep)
        point = cmds.xform(editPoint,ws=True,t=True,q=True)    
        jnt = cmds.joint()
        cmds.xform(jnt,t=point,ws=True)
        cmds.connectAttr(editPoint,'%s.translate' % jnt,f=True)

def createJntToTarget(lst):
    for l in lst:
        cmds.select(cl=True)
        point = cmds.xform(l,ws=True,q=True,t=True)
        jnt = cmds.joint(n='%s_jnt' % l,p=point)

def offsetJointToGrp(jnt):
    jnt = pm.ls(jnt)[0]
    grp = pm.group(empty=True,n='%s_offset' % jnt)
    pm.matchTransform(grp,jnt)
    pm.parent(jnt,grp)
    
###### Group ########
def addOffsetGroup(obj,name=None):
    parent = cmds.listRelatives(obj,p=True)[0] if cmds.listRelatives(obj,p=True) else None
    if name:
        grp = cmds.group(empty=True,name=name)
    else:
        grp = cmds.group(empty=True,name='%s_offset' % obj)
    cmds.matchTransform(grp,obj)
    cmds.parent(obj,grp)
    if parent:
        cmds.parent(grp,parent)




###### skin weight ######
#Get skinning joint list
            
def getSkinClusterFromMesh(mesh,*args):
    return mel.eval('findRelatedSkinCluster %s;'%mesh)

def getSkinData(skinCluster,*args):
    data = {}
    jntLst = skinJntLstFromSkinCluster(skinCluster)
    mesh   = getMeshFromSkinCluster(skinCluster)
    vertexLst = getVtxNames(mesh)
    weightData = {}
    for jnt in jntLst:
        for vertex in vertexLst:            
            value = cmds.skinPercent(skinCluster, vertex, transform=jnt, query=True )
            weightData[vertex] = value
        data[jnt] = weightData
    return data
def getMeshFromSkinCluster(skinCluster):
    return cmds.skinCluster(skinCluster,q=True,g=True)[0]
def skinJntLstFromMesh(mesh,*args):    
    skinCluster = getSkinClusterFromMesh(mesh)
    return skinJntLstFromSkinCluster(skinCluster)

def skinJntLstFromSkinCluster(skinCluster,*args):
    return cmds.skinCluster(skinCluster,inf=True,q=True)

def getGeoFromSkinCluster(skinCluster,*args):
    return cmds.skinCluster(skinCluster,g=True,q=True)[0]

def setSkinWeight(skinCluster,vtx,joint,value,*args):
    cmds.skinPercent( skinCluster, vtx, transformValue=[(joint,value)])

def pruneSmallWeight(skinCluster,vtx,joint,*args):
    pass

def getLockState(mesh,jnt):
    skinCluster = getSkinClusterFromMesh(mesh)
    return cmds.skinCluster(skinCluster,q=True,lw=True,inf=jnt)

def lockInf(mesh,jnt):
    jntLst = skinJntLstFromMesh(mesh)
    if not jnt in jntLst:
        print('%s is not infuluence joint in %s' % (jnt,mesh))
        return
    cmds.skinCluster(mesh,e=True,lw=True,inf=jnt)

def unlockInf(mesh,jnt):
    jntLst = skinJntLstFromMesh(mesh)
    if not jnt in jntLst:
        print('%s is not infuluence joint in %s' % (jnt,mesh))
        return
    cmds.skinCluster(mesh,e=True,lw=False,inf=jnt)

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

def getVtxNames(mesh):
    vtxCount = cmds.polyEvaluate(mesh,v=True)
    return ['%s.vtx[%s]' % (mesh,i) for i in xrange(vtxCount)]    

###### Matrix #########

def setDefaultMatrix(node,*args):
    defaultMatrix =[1.0,0.0,0.0,0.0,
                    0.0,1.0,0.0,0.0,
                    0.0,0.0,1.0,0.0,
                    0.0,0.0,0.0,1.0 ]
    cmds.setAttr('%s.offsetParentMatrix' % node,defaultMatrix,type='matrix')
##### Curve operation ######
def makeCurveToTargets(curveName = None,*args):
    lst = cmds.ls(sl=True)
    pointLst = []
    for l in lst:
        point = cmds.xform(l,q=True,rp=True,ws=True)
        pointLst.append(point)
        # print(point)
    
    cmds.curve(curveName,d=1,p=pointLst)
class checkMaxSkinInfluences(object):
    ''' This script takes a mesh with a skinCluster and checks it for N skin weights.
    If it has more than N, it selects the verts, so you can edit them.
    The script automatically prunes tiny values, because if you paint away an influence,
    it won't always zero out the values properly.
    Usage: select the number of influences your engine supports and a tiny prune value.
    Select the mesh and run the script
    # based on the script by Tyler Thornock from http://www.charactersetup.com/tutorial_skinWeights.html
    Modified for use by Chris Lesage
    '''

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.name = 'checkMaxSkinInfluences'
        self.title = 'Check Max Skin Influences'
        self.version = 0.8
        self.author = 'Chris Lesage'

        self.maxInfluences = 8
        self.pruneValue = 0.001
        self.btn1 = None
        self.btn2 = None

        self.ui()


    def ui(self):
        if pm.window(self.name, q=1, exists=1):
            pm.deleteUI(self.name)

        with pm.window(self.name, title=self.title + " v" + str(self.version), width=200, menuBar=True) as win:
            with pm.rowLayout(nc=4):
                pm.text(label='Max Influences: ', font='boldLabelFont', align='center')
                self.btn1 = pm.intField(width=40)
                self.btn1.setValue(self.maxInfluences)
                self.btn1.changeCommand(pm.Callback(self.max_inf_value_change, self.btn1, self.maxInfluences))
                pm.text(label='Auto Prune: ', font='boldLabelFont', align='center')
                self.btn2 = pm.floatField(width=40 * 3)
                self.btn2.setValue(self.pruneValue)
                self.btn2.changeCommand(pm.Callback(self.prune_value_change, self.btn2, self.pruneValue))
            with pm.horizontalLayout() as layout:
                btn = pm.button(width=290, label=str('Check Max Influences'), command=pm.Callback(self.do_the_thing))
            layout.redistribute()
        pm.showWindow()


    def prune_value_change(self, button, value):
        self.pruneValue = button.getValue()


    def max_inf_value_change(self, button, value):
        self.maxInfluences = button.getValue()


    def check_influences(self, mesh, maxInfluences, pruneValue):
        # TODO: Make a simple interface for choosing the options.
        #pm.select(mesh, d=True)
        skinCluster = None
        for node in pm.listHistory(mesh):
            if type(node) == pm.nodetypes.SkinCluster:
                skinCluster = node
                break

        #TODO: Do a first pass with NO pruning. If it passes check, make no change!
        pm.skinPercent(skinCluster, mesh, pruneWeights=pruneValue)
        # get the MFnSkinCluster for skinCluster
        selList = OpenMaya.MSelectionList()
        selList.add(skinCluster.name())
        clusterNode = OpenMaya.MObject()
        selList.getDependNode(0, clusterNode)
        skinFn = OpenMayaAnim.MFnSkinCluster(clusterNode)

        # get the MDagPath for all influence
        infDags = OpenMaya.MDagPathArray()
        skinFn.influenceObjects(infDags)

        # create a dictionary whose key is the MPlug indice id and
        # whose value is the influence list id
        infIds = {}
        infs = []
        for x in xrange(infDags.length()):
            infPath = infDags[x].fullPathName()
            infId = int(skinFn.indexForInfluenceObject(infDags[x]))
            infIds[infId] = x
            infs.append(infPath)

        # get the MPlug for the weightList and weights attributes
        wlPlug = skinFn.findPlug('weightList')
        wPlug = skinFn.findPlug('weights')
        wlAttr = wlPlug.attribute()
        wAttr = wPlug.attribute()
        wInfIds = OpenMaya.MIntArray()

        # the weights are stored in dictionary, the key is the vertId,
        # the value is another dictionary whose key is the influence id and
        # value is the weight for that influence
        weights = {}
        for vId in xrange(wlPlug.numElements()):
            vWeights = {}
            # tell the weights attribute which vertex id it represents
            wPlug.selectAncestorLogicalIndex(vId, wlAttr)

            # get the indice of all non-zero weights for this vert
            wPlug.getExistingArrayAttributeIndices(wInfIds)

            # create a copy of the current wPlug
            infPlug = OpenMaya.MPlug(wPlug)
            for infId in wInfIds:
                # tell the infPlug it represents the current influence id
                infPlug.selectAncestorLogicalIndex(infId, wAttr)

                # add this influence and its weight to this verts weights
                try:
                    vWeights[infIds[infId]] = infPlug.asDouble()
                except KeyError:
                    # assumes a removed influence
                    pass
            weights[vId] = vWeights

        overWeighted = [x for x in weights.keys() if len(weights[x]) > maxInfluences]
        [pm.select(mesh.vtx[x], add=True) for x in overWeighted]
        if len(overWeighted) > 0:
            pm.selectMode(component=True)
            pm.warning('{1} has {0} overloaded ({2}) influences.'.format(len(overWeighted), mesh, self.maxInfluences))
        else:
            pm.select(mesh.vtx, d=True)
            print('{1} is properly pruned to max {2}.'.format(len(overWeighted), mesh, self.maxInfluences))


    def do_the_thing(self):
        # hack: get the values of the buttons, in case they didn't register a change. (type but don't hit enter)
        self.maxInfluences = self.btn1.getValue()
        self.pruneValue = self.btn2.getValue()

        # NOTE: This is a bit of a selection hack. The purpose is this:
        # Even if I have component or object selected, it will search the proper mesh
        # And it puts me into component mode so I can instantly work with the weights
        # And it doesn't remove the transform from my selection list, so I can keep working on the same mesh
        # AND it clears the existing component selection (if you don't, it causes bugs.)
        pm.selectMode(object=True)  # this lets you have components selected when running the script
        for node in pm.selected(type='transform'):
            pm.selectMode(component=True)
            pm.select(node.vtx, d=True)  # first, clear any vtx selection
        pm.selectMode(object=True)
        for node in pm.selected(type='transform'):
            self.check_influences(node, self.maxInfluences, self.pruneValue)  # mesh, maxInfluences, pruneValue

#Follicle Constraint
def follicleConstraint(vertex,object,*args):
    #Convert to uv from selected vertex
    cmds.select(cmds.ls(vertex)[0],r=True)
    cmds.ConvertSelectionToUVs() 
    #Get UV value   
    uv = cmds.ls(sl=True)[0]
    uvValue = cmds.polyEditUV(uv,q=True)
    #Create follicle node and connect transform node
    follicle= cmds.createNode('follicle',name='%s_follicle' % object)
    transName = cmds.listRelatives(follicle,p=True)[0]    
    transName = cmds.rename(transName,'%sfollicle' % object )
    follicleGrp = cmds.group(name='%s_grp' % follicle,empty=True)
    cmds.parent(transName,follicleGrp)
    cmds.connectAttr('%s.outRotate' % follicle,'%s.rotate' % follicleGrp)
    cmds.connectAttr('%s.outTranslate' % follicle,'%s.translate' % follicleGrp)

    #Set follicle parameter value
    cmds.setAttr('%s.parameterU' % follicle,uvValue[0])
    cmds.setAttr('%s.parameterV' % follicle,uvValue[1])

    #Get shape from vertex
    vertexMesh = cmds.ls(vertex,o=True)[0]
    #Connect follicle world matrix,world mesh from vertex mesh
    cmds.connectAttr('%s.worldMatrix' % vertexMesh,'%s.inputWorldMatrix' % follicle,f=True)
    cmds.connectAttr('%s.worldMesh' % vertexMesh,'%s.inputMesh' % follicle,f=True)

    #Parent constraint follicleGrp to object
    cmds.parent(object,follicleGrp)

######## misc #########
def printObjectType(*args):
    print(cmds.objectType(cmds.ls(sl=True)[0]))


def mirrorSDK(srcDriveAttr,srcDrivenAttr,trgDriveObj,trgDrivenObj,inverse=False,*args):
    animCurves = cmds.listConnections(srcDrivenAttr,s=True,d=False,type='animCurve')
    driveAttr = srcDriveAttr.split('.')[-1]
    drivenAttr = srcDrivenAttr.split('.')[-1]
    if animCurves:
        animCurve  = animCurves[0]
        trgCurve = cmds.duplicate(animCurve)
        trgCurve = cmds.rename(trgCurve,'%s_%s' % (trgDrivenObj,drivenAttr))
        trgAttr = '%s.%s' % (trgDriveObj,driveAttr)
        
        cmds.connectAttr('%s.%s' % (trgDriveObj,driveAttr),'%s.input' % trgCurve,f=True)
        cmds.connectAttr('%s.output' % trgCurve,'%s.%s' % (trgDrivenObj,drivenAttr),f=True)

        if inverse:
            # print(trgCurve)
            animCurve = pm.ls(trgCurve)[0]
            count = animCurve.numKeys()
            
            for index in range(count):
                value = animCurve.getValue(index)
                animCurve.setValue(index,value*-1)
            # cmds.lockNode('__pymelUndoNode',lock=False)
            # cmds.delete('__pymelUndoNode')
            



###### Tools UI #######

###### Set Driven Keys UI #######
class SetDrivenKeysUI(object):
    def __init__(self):
        self.win = 'mirrorDrivenKeysUI'
        self.title = 'Mirror Driven Keys'
        self.width = 300
        self.height = 300
        self.create_ui()

    def create_ui(self):
        if cmds.window(self.win, exists=True):
            cmds.deleteUI(self.win)
        cmds.window(self.win, title=self.title, width=self.width, height=self.height)
        cmds.columnLayout(adj=True)
        cmds.textFieldButtonGrp('srcDriveAttr',label='Source Attribute:',text='',buttonLabel='Select',bc=lambda: self.select_attr('srcDriveAttr'))
        cmds.textFieldButtonGrp('srcDrivenAttr',label='Driven Attribute:',text='',buttonLabel='Select' ,bc=lambda: self.select_attr('srcDrivenAttr'))
        cmds.textFieldButtonGrp('trgDriveObj',label='Target Object:',text='',buttonLabel='Select',bc=lambda: self.select_obj('trgDriveObj'))
        cmds.textFieldButtonGrp('trgDrivenObj',label='Driven Object:',text='',buttonLabel='Select',bc=lambda: self.select_obj('trgDrivenObj'))
        cmds.checkBox('inverse',label='Inverse')
        cmds.button(label='Set Driven Keys',command=self.setDrivenKeys)
        cmds.showWindow()
    
    def setDrivenKeys(self,*args):
        srcDriveAttr = cmds.textFieldButtonGrp('srcDriveAttr',q=True,text=True)
        srcDrivenAttr = cmds.textFieldButtonGrp('srcDrivenAttr',q=True,text=True)
        trgDriveObj = cmds.textFieldButtonGrp('trgDriveObj',q=True,text=True)
        trgDrivenObj = cmds.textFieldButtonGrp('trgDrivenObj',q=True,text=True)
        inverse = cmds.checkBox('inverse',q=True,v=True)
        mirrorSDK(srcDriveAttr,srcDrivenAttr,trgDriveObj,trgDrivenObj,inverse)

    def select_attr(self,*args):
        objs = cmds.ls(sl=True)
        attrs = mel.eval('channelBox -q -selectedMainAttributes mainChannelBox;')
        
        if not attrs:
            try:
                attrs = mel.eval('channelBox -q -sha mainChannelBox;')
            except:
                return
        attrFullNames = []
        for obj in objs:
            for attr in attrs:
                attrFullNames.append('%s.%s' % (obj,attr))
        if attrFullNames:
            cmds.textFieldButtonGrp(args[0],e=True,text=attrFullNames[0])
            # return attrFullNames[0] 
    def select_obj(self,*args):
        objs = cmds.ls(sl=True)
        if objs:
            cmds.textFieldButtonGrp(args[0],e=True,text=objs[0])
            # return objs[0]
            
def mirrorSDKUI(*args):
    UI = SetDrivenKeysUI()
    UI.create_ui()

###### motion path #######

def motionPathUI(*args):
    if cmds.window('motionPathUI',ex=True):
        cmds.deleteUI('motionPathUI')
    
    cmds.window('motionPathUI',title='Motion Path Window')
    cmds.frameLayout(lv=False)
    cmds.textScrollList()
    cmds.showWindow()

###### expression #######

def addExpression(n=None,string=None):
    cmds.expression(n=n,s=string)

def sinExp(obj,attr):
    '''
    obj: string,controller name
    attr: tx or ty or tz or rx or ry or rz
    '''
    
    name = '{0}_{1}_sin_Exp'.format(obj,attr)
    if cmds.objExists(name):
        cmds.delete(name)

    grps = cmds.listRelatives(obj,p=True)
    if not grps:
        print('Object %s has not group' % obj)
        return
    else:
        if cmds.getAttr('%s.%s' % (grps[0],attr)):
            print('Group attribute value must be 0')
            return
    grp = grps[0]
    
    sinScale = '%s.sinScale' % obj
    sinScaleOffset = '%s.sinScaleOffset' % obj
    sinTimeOffset = '%s.sinTimeOffset' % obj
    sinFrequency = '%s.sinFrequency' % obj
    for attribute in [sinScale,sinScaleOffset,sinFrequency]:
        if cmds.objExists(attribute):
            cmds.deleteAttr(attribute.split('.')[0],at=attribute.split('.')[1])
            print(cmds.objExists(attribute))
    
    cmds.addAttr(obj,k=True,at='float',ln='sinScale',dv=1)
    cmds.addAttr(obj,k=True,at='float',ln='sinScaleOffset',dv=1)
    cmds.addAttr(obj,k=True,at='float',ln='sinTimeOffset',dv=0)
    cmds.addAttr(obj,k=True,at='float',ln='sinFrequency',dv=1)
    
    string = '{0}.{1} = sin((frame + {2})*{3}) * {4} + {5}'.format(grp,attr,sinTimeOffset,sinFrequency,sinScale,sinScaleOffset)
    
    
    addExpression(name,string)