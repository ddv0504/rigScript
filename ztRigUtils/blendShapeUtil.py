import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import re 

def clearBlendShapeNode(BSNode):
    info  = getBlendShapeInfo(BSNode)
    for k,v in info.items():
        deleteBlendShapeTarget(BSNode,v)


def getBlendShapeInfo(blendShape):
    '''
    Return blendShape's ID and attributes dict..
    '''    
    attribute_dict = {}
    if cmds.nodeType(blendShape) != 'blendShape':
        return attribute_dict

    infomations =  cmds.aliasAttr(blendShape, q=True)
    if not infomations:
        
        return 
    for i in range(len(infomations)):
        if i % 2 == 1:continue
        bs_id   = infomations[i + 1]
        bs_attr = infomations[i + 0]
        bs_id = int(re.search('\d+', bs_id).group())
        attribute_dict[bs_id] = bs_attr
    return attribute_dict

def addTarget(trgShape,BSNode):    

    obj = pm.ls(sl=True)[0]
    trgBase = pm.duplicate()[0]
    trgShape = trgBase.rename(trgShape)

    cmds.select(cl=True)
    for i in trgShape.listRelatives():
        if '|' in i:
            oldName = i.split('|')[1]
            newName = '%s_%s' % (trgShape,oldName)
            i.rename(newName)
        else:
            newName = '%s_%s' % (trgShape,i.name())
            i.rename(newName)
    trgShape.setParent(world=True)

    trgNum = pm.blendShape(BSNode,q=True,wc=True)
    pm.select(trgShape,r=True)
    mel.eval('doBlendShapeAddSelectionAsTarget %s 1 2 "%s" 0 1;' % (BSNode, obj.name()))
    mel.eval('aliasAttr %s %s.w[%s];' % (trgShape,BSNode,trgNum))
    
def addBSAttr(BSNode,ctrl):

    attrLst = cmds.listAttr('%s.w' % BSNode,m=True)
    cmds.undoInfo(ock=True)
    for attr in attrLst:
        cmds.addAttr(ctrl,ln=attr,at='double',min=0,max=1,dv=0)
        cmds.setAttr('%s.%s' % (ctrl,attr),e=True,keyable=True)
        try:
            cmds.connectAttr('%s.%s' % (ctrl,attr),'%s.%s' % (BSNode,attr))
        except :
            pass
    cmds.undoInfo(cck=True)

def addSelectedTarget(BSNode,*args):

    if not BSNode:
        BSNode = 'asARK'
    info = getBlendShapeInfo(BSNode)
    if not info:
        num = 0
    else:
        num = int(info.keys()[-1]) + 1
     
    for trgShape in pm.ls(sl=True):
        try:
            trgShape.setParent(world=True)
        except:
            pass
        
        pm.select(trgShape,r=True)
        mel.eval('doBlendShapeAddSelectionAsTarget %s 1 2 "%s" 0 1;' % (BSNode, trgShape.name()))
        mel.eval('aliasAttr %s %s.w[%s];' % (trgShape,BSNode,num))
        num += 1

def outputBSTarget(bsNode,copyObj,attrMaxVal):
    attrLst = []
    if not cmds.objectType(bsNode) == 'blendShape':
        attrLst = [i for i in cmds.listAttr(bsNode,ud=True) if not i in 'createCtrlMode']
    else:    
        attrLst = cmds.listAttr('%s.w' % bsNode,m=True)
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar');

    cmds.progressBar( gMainProgressBar,
                                    edit=True,
                                    beginProgress=True,
                                    isInterruptable=True,
                                    status='Copy BlendShape Targets ...',
                                    maxValue=len(attrLst) )
    
    for attr in attrLst:
        if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True ) :
                    break
        cmds.setAttr('%s.%s' % (bsNode,attr),attrMaxVal)
        dup = cmds.duplicate(copyObj)[0]
        cmds.parent(dup,w=True)
        cmds.setAttr('%s.v' % dup,0)
        cmds.rename(dup,attr)
        cmds.setAttr('%s.%s' % (bsNode,attr),0)
        cmds.progressBar(gMainProgressBar, edit=True, step=1)
    cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)

def getBlendShapeIndex(bsNode,targetName):
    attr = bsNode + '.w[{}]'
    weightCount = cmds.blendShape(bsNode, q=True, wc=True)
    for index in xrange(weightCount):
        if cmds.aliasAttr(attr.format(index), q=True) == targetName:
            return index
    return -1

def deleteBlendShapeTarget(BSNode,targetName):
    info = getBlendShapeInfo(BSNode)
    index = int([{k:v} for k,v in info.items() if v in targetName][0].keys()[0])
    cmds.removeMultiInstance(BSNode + ".weight[%s]" % index, b=True)
    cmds.removeMultiInstance(BSNode + ".inputTarget[0].inputTargetGroup[%s]" % index, b=True)
    cmds.aliasAttr('%s.%s' % (BSNode,targetName), e=True,rm=True)

def replaceBlendShapeTarget(bsNode,targetName,targetObject):
    srcAttrs = cmds.listConnections('%s.%s'% (bsNode,targetName),plugs=True) 
    if not cmds.objExists('%s.%s' % (bsNode,targetName)):
        print('Have not current blendshape attribute %s.%s' % (bsNode,targetName))
        return
    deleteBlendShapeTarget(bsNode,targetName)
    cmds.select(targetObject,r=True)
    addSelectedTarget(bsNode)
    
    for attr in srcAttrs:
        trgAttr = '%s.%s' % (bsNode,targetObject)
        
        cmds.connectAttr(attr,trgAttr,f=True)

def mirrorBlendShape(bsAttrs):    
    pass