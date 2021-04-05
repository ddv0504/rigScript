#-*- coding: utf-8 -*-
import sys,os
import maya.cmds as cmds

def jointDrawUI():
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