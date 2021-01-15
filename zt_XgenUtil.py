#-*- coding: utf-8 -*-
import pymel.core as pm
import maya.cmds as cmds
import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.XgExternalAPI as xge
import xgenm.ui as xgui
import xgenm.xmaya.xgmConvertPrimToPolygon as cpp
import maya.mel as mel

################ Guide Curve operation ##################

def selectOverlapGuide():
    
    guides = [i for i in pm.ls(sl=True)]
    dic = {}
    for guide in guides:
        vect = guide.getPivots()[0]    
        dic[guide] = vect    
    newDic = {} 
    for key in dic.keys():
        count = 0    
        for value in dic.values():        
            if dic[key] == value:            
                count+=1
                newDic[key] = count
    cmds.select(cl=True)
    for key in newDic.keys():
        if newDic[key] >1:
            cmds.select(key.name(),add=True)

def selectOverlapNurbsCurve():
    nurbsTransforms = [i for i in pm.ls(sl=True)]
    dic = {}
    for trans in nurbsTransforms:
        curveShape = trans.listRelatives(c=True)[0]  
        point = curveShape.getCV(0)
        dic[trans] = point    
    newDic = {} 
    for key in dic.keys():
        count = 0    
        for value in dic.values():        
            if dic[key] == value:            
                count+=1
                newDic[key] = count
    cmds.select(cl=True)
    for key in newDic.keys():
        if newDic[key] >1:
            cmds.select(key.name(),add=True)

def overrideCurveToGuide(curve,guide):
    curve,guide = pm.ls(curve,guide)
    curveShape = curve.listRelatives(c=True)[0]
    guideShape = guide.listRelatives(c=True)[0]
    makeGuide = [i for i in guideShape.listConnections() if i.type()=='xgmMakeGuide'][0]
    curveShape.connectAttr('worldSpace[0]','%s.override' % makeGuide.name(),f=True)

def overrideGuide():
    guideCurves = cmds.ls(sl=True)
    
    for guideCurve in guideCurves:
        guide = guideCurve.replace('_tempCurve','')
        print(guideCurve,guide)
        overrideCurveToGuide(guideCurve,guide)

def createGuidesToCurve():
    deses = cmds.ls(sl=True)
    for des in deses:
        grpName = '%s_guideCurves' % des
        cmds.select(des,r=True)
        mel.eval("xgmCreateCurvesFromGuidesOption 1 1 %s ;" % grpName)
   