from __future__ import print_function
from imp import reload
from pprint import pprint
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.mel as mel
import pymel.core as pm
import json
import os
from ztMdlUtils import ztMdlUtil
reload(ztMdlUtil)
gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')

def matchToClosestTarget(*args):
    targetMesh = cmds.textFieldButtonGrp('matchToClosestTargetFieldBtn',q=True,text=True)
    if not cmds.objExists(targetMesh):
        print('Object %s is not exist' % targetMesh)
        return
    vtxs = cmds.ls(sl=True,fl=True)
    ztMdlUtil.matchToClosestPoint(targetMesh,vtxs)
def matchMesh(*args):
    radioBtn = cmds.radioCollection('matchMeshRadioCollection',q=True,sl=True)
    if radioBtn == 'SourceRadioBtn':
        ztMdlUtil.matchMesh(match=False)
    else:
        ztMdlUtil.matchMesh()

def addToField(obj):
    vtxs = cmds.ls(sl=True,fl=True)
    
def saveData(data,*args):
    dataPath = "d:/temp/mirrorData.json"
    if not os.path.exists(os.path.dirname(dataPath)):
        os.makedirs(os.path.dirname(dataPath))
    with open(dataPath,'w') as f:
        json.dump(data,f,indent=4)

def loadData(*args):
    dataPath = "d:/temp/mirrorData.json"
    with open(dataPath,'r') as f:
        data = json.load(f)
    return data

def getVtxInfoFromMesh(sel):
    numOfVtx = cmds.polyEvaluate(v = True)
    leftVtxDic = {}
    rightVtxDic = {}
    centerVtxDic = {}

    try:
        ctVtxTol = cmds.floatField('ctVtxTolFltFld', q = True, v = True)
    except:
        ctVtxTol = 0.001
    cmds.progressBar(gMainProgressBar,
				edit=True,
				beginProgress=True,
				isInterruptable=True,
				status='Get Verteices Info ...',
				maxValue=numOfVtx )
    for i in xrange(numOfVtx):
        if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True ):
            break
        cmds.progressBar( gMainProgressBar,e=True,step=1)
    	iPos = cmds.pointPosition('%s.vtx[%d]' %(sel, i), local = True)
    	# refine raw iPos data
    	for val in xrange(len(iPos)):
    	    if 'e' in str(iPos[val]):
    		    iPos[val] = 0.0
    	    else:
    		    iPos[val] = float('%.3f' %iPos[val])
    	# classify depend on x position
    	if -ctVtxTol <= iPos[0] <= ctVtxTol:
    	    centerVtxDic['%s.vtx[%d]' %(sel, i)] = tuple(iPos)
    	if iPos[0] > 0:
    	    leftVtxDic['%s.vtx[%d]' %(sel, i)] = tuple(iPos)
    	if iPos[0] < 0:
    	    rightVtxDic['%s.vtx[%d]' %(sel, i)] = tuple(iPos)
        
    cmds.progressBar(gMainProgressBar,e=True,ep=True)
    return leftVtxDic, rightVtxDic, centerVtxDic

def getVtxInfoFromSelected(*args):
    vtxs = cmds.ls(sl=True,fl=True)
    leftVtxDic = {}
    rightVtxDic = {}
    centerVtxDic = {}
    try:
        ctVtxTol = cmds.floatField('ctVtxTolFltFld', q = True, v = True)
    except:
        ctVtxTol = 0.001
    for n,vtx in enumerate(vtxs):
        iPos = cmds.pointPosition(vtx, local = True)
    	# refine raw iPos data
    	for val in xrange(len(iPos)):
    	    if 'e' in str(iPos[val]):
    		    iPos[val] = 0.0
    	    else:
    		    iPos[val] = float('%.3f' %iPos[val])
    	# classify depend on x position
    	if -ctVtxTol <= iPos[0] <= ctVtxTol:
    	    centerVtxDic[vtx] = tuple(iPos)
    	if iPos[0] > 0:
    	    leftVtxDic[vtx] = tuple(iPos)
    	if iPos[0] < 0:
    	    rightVtxDic[vtx] = tuple(iPos)
    return leftVtxDic, rightVtxDic, centerVtxDic


def getMirrorData(mesh=False,vtx=False,*args):
    sel = cmds.ls(sl=True,fl=True)[0]
    if mesh:
        data = getVtxInfoFromMesh(sel)
    elif vtx:
        data = getVtxInfoFromSelected(sel)
    getData = {}
    mirrorData = {}
    for src in data[0].keys():
        srcPoint = data[0][src]
        for trg in data[1].keys():
            trgPoint = data[1][trg]
            if srcPoint[0] * -1 == trgPoint[0] and srcPoint[1] == trgPoint[1] and srcPoint[2] == trgPoint[2] :
                mirrorData[src] = trg
    getData['mirrorData'] = mirrorData
    getData['centerData'] = data[2]
         
    return getData

def mirrorVertex(data,trgObj,*args):
    cmds.progressBar( gMainProgressBar,e=True,status='Set Side Mirror Data...',bp=True)
    for k,v in data['mirrorData'].items():
        if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True ):
            break
        cmds.progressBar( gMainProgressBar,e=True,step=1)
        k=k.replace(k.split('.')[0],trgObj)
        v=v.replace(v.split('.')[0],trgObj)
        src = cmds.pointPosition(k , local = True)
        trg = cmds.pointPosition(v , local = True)
        srcPoint = [trg[0]*-1,trg[1],trg[2]]
        trgPoint = [src[0]*-1,src[1],src[2]]
        cmds.move(trgPoint[0],trgPoint[1],trgPoint[2],v,xyz=True,ls=True)
        cmds.move(srcPoint[0],srcPoint[1],srcPoint[2],k,xyz=True,ls=True)
    cmds.progressBar( gMainProgressBar,e=True,ep=1)
    cmds.progressBar( gMainProgressBar,e=True,status='Set Center Mirror Data...',bp=True)
    for k in data['centerData'].keys():
        if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True ):
            break
        cmds.progressBar( gMainProgressBar,e=True,step=1)
        k = k.replace(k.split('.')[0],trgObj)
        orgVal = cmds.xform(k,t=True,q=True)
        cmds.move(orgVal[0]*-1,orgVal[1],orgVal[2],k,xyz=True,ls=True)
    cmds.progressBar( gMainProgressBar,e=True,ep=1)      
def main(*args):
    if cmds.window('SCCModelTools',ex=True):
        cmds.deleteUI('SCCModelTools')
    cmds.window('SCCModelTools',t='Model Tools',wh=(300,420))
    cmds.frameLayout('MeshLayout',lv=True,l='Match Mesh')
    cmds.rowLayout(nc=2)
    cmds.radioCollection('matchMeshRadioCollection')
    cmds.radioButton('SourceRadioBtn',l='Match to Source')
    cmds.radioButton('TargetRadioBtn',l='Match to Target')
    cmds.setParent('..')
    cmds.button('meshMatchBtn',l='Excute',c=matchMesh)
    cmds.radioCollection('matchMeshRadioCollection',e=True,sl='SourceRadioBtn')
    cmds.setParent('..')
    cmds.frameLayout('matchToClosestTargetLayout',l='Match To Closest Target')
    cmds.textFieldButtonGrp('matchToClosestTargetFieldBtn',l='Target Mesh:',bl='<<',cw3=[100,220,30],bc=lambda:cmds.textFieldButtonGrp('matchToClosestTargetFieldBtn',e=True,text=cmds.ls(sl=True)[0]))
    cmds.button('matchToClosestTargetButton',l='Execute',c=matchToClosestTarget)
    cmds.setParent('..')
    cmds.frameLayout('mirrorLayout',l='Mirror')
    cmds.rowLayout(nc=2)
    cmds.button('srcObjBtn',l='Get Source Object',c=lambda x:(cmds.button('srcObjBtn',e=True,l=cmds.ls(sl=True)[0]),
    saveData(getMirrorData(mesh=True))))
    cmds.button('srcVtxsBtn',l='Get Source Vertices',c=lambda x:(cmds.button('srcVtxsBtn',e=True,l=str(cmds.ls(sl=True))),
    saveData(getMirrorData(vtx=True))))
    cmds.setParent('..')
    cmds.button('mirrorBtn',l='Mirror Target',c=lambda x:(
    mirrorVertex(loadData(),cmds.ls(sl=True)[0])))
    cmds.showWindow()