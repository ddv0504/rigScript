'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This script is for cleaning up the models before into the rigging stage.

Requirement:
tak_logging.py

Usage:
import tak_cleanUpModel
reload(tak_cleanUpModel)
tak_cleanUpModel.UI()
'''

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya

from ztRigUtils import tak_misc, tak_lib

from functools import partial
import re

PLUGINS = {
    '2015': ['modelCleanup_2015'],
    '2016': [],
    '2018': ['modelCleanup_2018'],
    '2019': [],
    '2020': []
}
mayaVersion = pm.versions.shortName()
for plugin in PLUGINS[mayaVersion]:
    if plugin and not pm.pluginInfo(plugin, q=True, loaded=True):
        pm.loadPlugin(plugin)



def UI():
    winName = 'CUMWin'
    if cmds.window(winName, exists = True):
        cmds.deleteUI(winName)
    cmds.window(winName, title = 'Cleanup Model', mnb = False, mxb = False)

    cmds.tabLayout('mainTab', tv = False)
    cmds.columnLayout('procColLay', adj = True)

    # unique name section
    cmds.setParent('procColLay')
    cmds.frameLayout(label = 'Correct Naming', collapsable = True, collapse = True)
    cmds.rowColumnLayout('uniqNameRowColLay', numberOfColumns=3, columnSpacing=[(2, 5), (3, 5)])
    cmds.button(label="Check Namespace", w=127, c=chkNamespace)
    cmds.button('uniqTransformButt', w=127, label='Unique Transform Name', c=uniqTransformName)
    cmds.button('autoUniqButt', w=127, label='Auto Unique Name', c=autoUniqName)

    # Check the mesh errors
    cmds.setParent('procColLay')
    cmds.separator(h = 5, style = 'in')
    cmds.frameLayout(label = 'Geometry Error Check', collapsable = True, collapse = True)
    cmds.rowColumnLayout('mdlErrChkRowColLay', numberOfColumns = 3, columnSpacing = [(2, 5), (3, 5)])
    cmds.button(label = 'Nonmanifold Geometry', w=128, c=lambda args: mel.eval('polyCleanupArgList 3 { "0","2","1","0","0","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","1","0" };selectMode -component;selectType -pv true;string $selLs[] = `ls -sl`;if(size($selLs) == 0){selectMode -object;}'))
    cmds.button(label = 'More than 4-Side', w=128, c=lambda args: mel.eval('polyCleanupArgList 4 { "0","2","1","0","1","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    cmds.button(label = 'Overlapped Vertex', w=128, c=checkOverlapVertices)
    cmds.button(label = 'Overlapped Root Curve', w=128, c=findOverlappedRootCurve)

    cmds.setParent('procColLay')
    cmds.separator(h = 5, style = 'in')
    cmds.frameLayout(label = 'Manual Check List', collapsable = True, collapse = True)
    cmds.checkBox('mdlGridChkBox', label = 'World Position: Front/Side Center of the Grid, Bottom on Grid', cc = partial(chkBoxCC, 'mdlGridChkBox'))
    cmds.checkBox('scaleChkBox', label = 'Scale: Compare to other characters, Real World Scale', cc = partial(chkBoxCC, 'scaleChkBox'))
    cmds.checkBox('dfltStateChkBox', label = 'Default Pose: Foot Direction on Z-Axis, Middle Pose of Range', cc = partial(chkBoxCC, 'dfltStateChkBox'))
    cmds.checkBox('topoChkBox', label = 'Topology: Deformable/Continuous Flow, Enough Supporting Edge(Eyelid, Under Shoulder), Quad', cc = partial(chkBoxCC, 'topoChkBox'))
    cmds.checkBox('hiddenChkBox', label = 'Hidden Area: Inner Mouth, Inner Cloth', cc = partial(chkBoxCC, 'hiddenChkBox'))
    cmds.checkBox('combineChkBox', label = 'Combine: Same Material, Symmetry Object', cc = partial(chkBoxCC, 'combineChkBox'))
    cmds.checkBox('OutlinerChkBox', label = 'Outliner: Grouping, Naming', cc = partial(chkBoxCC, 'OutlinerChkBox'))

    cmds.setParent('procColLay')
    cmds.separator(h = 5, style = 'in')
    cmds.frameLayout('symFrameLo', label = 'Symmetry', collapsable = True, collapse = True)
    cmds.columnLayout('symColLo', adj = True)
    cmds.rowColumnLayout('checkSymRowColLo', numberOfColumns=3, columnSpacing=[(2, 3), (3, 3)])
    cmds.text(label='Search Tolerance: ')
    cmds.floatField('ctVtxTolFltFld', v = 0.001)
    cmds.button('symChkButton', label = 'Check Symmetry', c = checkSym)
    cmds.setParent('symColLo')
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.floatSliderGrp(label='Match Sym Vertex: ', field=True, value=0.001, min=0.001, max=5.000, step=0.001, columnWidth=[(1, 93), (2, 40), (3, 150)], cc=matchMirrorVtxPosition)
    cmds.button(label='translateX to Zero', c=tak_misc.zeroVtx)
    cmds.setParent('symColLo')
    cmds.separator()
    cmds.text(label = 'Warning! Check uv is correctly copied.\nFor uv comparison recommended to duplicate original mesh.')
    cmds.radioButtonGrp('symSmpSpcRdoBtn', label = 'Sample Space for UV Copy: ', numberOfRadioButtons = 3, labelArray3 = ['World', 'Component', 'Topology'], select = 1, columnWidth = [(2, 70), (3, 100), (4, 70)])
    cmds.rowColumnLayout('symRowColLay', numberOfColumns = 2, columnSpacing=[(2, 20)])
    cmds.button('makeSymButton', label = 'Make Symmetry', c = makeSym)
    cmds.radioButtonGrp('symOptRadButGrp', numberOfRadioButtons = 2, labelArray2 = ['x to -x', '-x to x'], columnWidth = [(1, 60), (2, 50)], select = 1)
    cmds.setParent('symFrameLo')

    # Material Clean Up
    cmds.setParent('procColLay')
    cmds.separator(h = 5, style = 'in')
    cmds.frameLayout(label = 'Material Clean Up', collapsable = True, collapse = True)
    cmds.button(label="Check material that assigned to face", c=chkFaceAssignedMat)
    cmds.rowColumnLayout('viewShaderRowColLay', numberOfColumns = 3, columnWidth = [(1, 135), (2, 135), (3, 120)], columnSpacing = [(2, 2), (3, 2)])
    cmds.button(label = 'Reassign Material to Object', c = reAssignMatToObj)
    cmds.button(label = 'Separate Faces by Material', c = partial(sepCombineByMat, 'separate'))
    cmds.button(label = 'Combine Faces by Material', c = partial(sepCombineByMat, 'combine'))
    cmds.button(label = 'Combine Objects by Mat', c = combineObjByMat, ann = 'Select poly objects.')

    cmds.setParent('procColLay')
    cmds.separator(h = 5, style = 'in')
    cmds.frameLayout(label = 'Essential Procedures', collapsable = True)
    cmds.columnLayout(adj = True)
    cmds.button(label = 'Delete Junk Child of Shape', c = delChildOfShape)
    cmds.button('matchShapeButt', label = 'Match Shape Name', c = matchShape)
    cmds.button('histButton', label = 'Unlock Attribute, Break Connections', c = cleanChBox)
    cmds.button('frzBtn', label = 'Freeze Transform', c = freezeTrnf)
    cmds.button('resetVtxBtn', label = 'Reset Vertex', c = resetVtx)
    cmds.button(label = 'Delete History', c = delHis)
    cmds.button('intermButton', label = 'Delete Intermediate Object', c = delInterMediObj)
    cmds.button(label = 'Off Drawing Override of Shape, Double Sided On, Primary visibility On', c = setShpAttrs)
    cmds.button(label = 'Set Texture Channel to Combined Texture', c = combinedTexture)
    cmds.button(label = 'Into Default Display Layer', c = intoDfltDisLyr)
    cmds.button(label = 'Remove MI Label', c = rmvMILabel)

    cmds.button('allButton', label = 'All in One', c = allInOne, h = 40, bgc = [1, 0.5, 0.2])

    cmds.setParent('procColLay')
    cmds.separator(h = 5, style = 'in')
    cmds.frameLayout(label = 'Extra Procedures', collapsable = True, collapse = True)
    cmds.columnLayout(adj = True)
    cmds.button(label = 'Delete Empty Transform', c = delEmptyTrnsf)
    cmds.button('layerButton', label = 'Delete Display and Render Layers', c = delLayer)
    cmds.button(label = 'Set Up Group Hierarchy Structure for Pipeline', c = pipeHier)

    cmds.window(winName, edit = True, w = 400, h = 300)
    cmds.showWindow(winName)

    cmds.showWindow()

def chkBoxCC(wdgName, *args):
    chkState = cmds.checkBox(wdgName, q = True, v = True)

    if chkState:
        cmds.checkBox(wdgName, e = True, enable = False)


def combineObjByMat(*args):
    '''
    Combine objects that assigned same material.
    '''

    # Get material list
    selLs = cmds.ls(sl = True)
    matLs = getMatLs(selLs)

    # Iterate for materials
    for mat in matLs:
        # Select by material
        cmds.hyperShade(objects = mat)

        # Get transform node
        selLs = cmds.ls(sl = True)
        trsfLs = getTrsfLs(selLs)

        # Combine objects
        if len(trsfLs) == 1:
            cmds.select(trsfLs[0])
            cmds.hyperShade(assign = mat)
        else:
            cmds.polyUnite(trsfLs)


def getMatLs(objLs):
    '''
    Get all materials assigned to given objecs.
    '''

    matLs = []

    for obj in objLs:
        mat = tak_lib.getMatFromSel(obj)
        matLs.extend(mat)

    return list(set(matLs))


def getTrsfLs(selLs):
    '''
    Get all transform node from selected objects.
    '''

    trsfLs = []

    for sel in selLs:
        objType = cmds.objectType(sel)
        if objType == 'transform':
            trsfLs.extend(sel)
        else:
            # Recurse until find parent transform node
            while objType != 'transform':
                sel = cmds.listRelatives(sel, p = True, path = True)
                objType = cmds.objectType(sel)

            trsfLs.extend(sel)

    return list(set(trsfLs))


def chkFaceAssignedMat(*args):
    cmds.select('lod03_GRP', hi=True, r=True)

    selObjLs = cmds.ls(sl=True)

    selGeoFaceMatLs = faceAssignedMat(selObjLs)

    faceAssignedMatGeoLs = []

    for mat in selGeoFaceMatLs:
        cmds.hyperShade(objects=mat)
        matAssignGeoLs = cmds.ls(sl=True)
        faces = cmds.filterExpand(matAssignGeoLs, ex=False, sm=34)

        if faces:
            matAssignedFaceShapes = getShapesFromFaces(faces)

            for faceShp in matAssignedFaceShapes:
                trsf = cmds.listRelatives(faceShp, p=True)
                if trsf[0] in selObjLs:
                    faceAssignedMatGeoLs.extend(trsf)

    if faceAssignedMatGeoLs:
        cmds.select(faceAssignedMatGeoLs, r=True)
        cmds.error('Selected objects are has materials that assigned to face.')
    else:
        OpenMaya.MGlobal.displayInfo('All render models are clean.')
        cmds.select(cl=True)


def reAssignMatToObj(*args):
    sels = pm.selected()
    for sel in sels:
        shadingEngine = sel.getShape().connections(type='shadingEngine', s=False)[0]
        mat = shadingEngine.surfaceShader.connections(d=False)[0]
        pm.delete(shadingEngine)
        pm.select(sel, r=True)
        pm.hyperShade(assign=mat)


def sepCombineByMat(mode, *args):
    '''
    Separate face by material main function.
    '''

    selObjLs = cmds.ls(sl = True, long = True)

    selGeoFaceMatLs = faceAssignedMat(selObjLs)

    delGeoLs = []

    for mat in selGeoFaceMatLs:
        cmds.hyperShade(objects = mat)
        matAssignGeoLs = cmds.ls(sl = True)
        faces = cmds.filterExpand(matAssignGeoLs, ex = False, sm = 34)

        if faces:
            matAssignedFaceShapes = getShapesFromFaces(faces)
            matAssignedShapes = cmds.ls(matAssignGeoLs, type = 'mesh')
            toCombineGeoLs = []

            for faceShp in matAssignedFaceShapes:
                trsf = cmds.listRelatives(faceShp, p = True, fullPath = True)
                if trsf[0] in selObjLs: # Do it for selected objects only.
                    dupGeo = cmds.duplicate(trsf, renameChildren = True)

                    shpCorFaces = getCorrespondFaces(faceShp, faces)
                    dupGeoFaces = replaceGeoName(dupGeo[0], shpCorFaces)

                    cmds.select(dupGeoFaces, r = True)
                    cmds.InvertSelection()
                    cmds.delete()

                    # Remove faces from shading group
                    shapeName = cmds.listRelatives(dupGeo, ni = True, path = True, s = True)
                    sgName = list(set(cmds.listConnections('%s.instObjGroups.objectGroups' %shapeName[0], d = True, type = "shadingEngine")))
                    cmds.select('%s.f[*]' %dupGeo[0], r = True)
                    cmds.sets(remove = sgName[0])

                    # Select transform and assign material
                    cmds.select(dupGeo, r = True)
                    cmds.hyperShade(assign = mat)
                    cmds.delete(ch = True)

                    toCombineGeoLs.extend(dupGeo)
                    delGeoLs.extend(trsf)

                    print '>> "%s" has face assigned material.' %trsf

                if mode == 'combine':
                    if len(toCombineGeoLs) > 1:
                        cmds.select(toCombineGeoLs, r = True)
                        finalGeo = cmds.polyUnite(toCombineGeoLs)
                        cmds.select(finalGeo, r = True)
                        cmds.hyperShade(assign = mat)
                    elif len(toCombineGeoLs) == 1:
                        cmds.select(toCombineGeoLs, r = True)
                        cmds.hyperShade(assign = mat)

                    cmds.delete(ch = True)

    if delGeoLs:
        cmds.delete(delGeoLs)

    else:
        cmds.select(cl = True)
        OpenMaya.MGlobal.displayInfo('>> There is no object that material assigned to face.')


def faceAssignedMat(geoLs):
    matLs = []
    for geo in geoLs:
        shapeName = cmds.listRelatives(geo, ni = True, path = True, s = True)

        if shapeName:
            sgName = cmds.listConnections('%s.instObjGroups.objectGroups' %shapeName[0], d = True, type = "shadingEngine")
            matName = cmds.ls(cmds.listConnections(sgName), materials = True)
            matLs.extend(matName)

    return list(set(matLs))


def getShapesFromFaces(faces):
    faceShpLs = []
    for face in faces:
        faceShpLs.extend(cmds.listRelatives(face, p = True, path = True))
    return list(set(faceShpLs))


def getCorrespondFaces(shp, faces):
    geoName = cmds.listRelatives(shp, p = True, path = True)
    faceLs = []
    for face in faces:
        if geoName[0] in face:
            faceLs.append(face)
    return faceLs


def replaceGeoName(geoName, faces):
    newShpFaces = []
    for face in faces:
        newShpFaces.append(geoName + '.' + face.split('.')[-1])
    return newShpFaces


def combinedTexture(*args):
    # Hardware Texturing Set to Combined Texture of Selected Objects's Materials #
    selObjs = cmds.ls(sl = True)

    # Get materials
    mats = []
    for selObj in selObjs:
        selObjMat = tak_lib.getMatFromSel(selObj)
        mats.extend(selObjMat)
    mats = list(set(mats))

    for mat in mats:
        materialInfoNode = cmds.ls(cmds.listConnections(mat), type = 'materialInfo')[-1]
        connectedMat = cmds.listConnections(materialInfoNode + ".texture[0]")
        if connectedMat:
            cmds.disconnectAttr('%s.message' %connectedMat[0], '%s.texture[0]' %materialInfoNode)
        cmds.connectAttr('%s.message' %mat, '%s.texture[0]' %materialInfoNode, nextAvailable = True)


def assignSurfMatWithFileTex(*args):
    '''
    Select a file texture then run.
    '''

    fileTex = cmds.ls(sl = True)[0]

    shadingEngine = tak_lib.findShadingEngine(fileTex)

    lamShd = cmds.shadingNode('lambert', n='%s_lambert_mat' %fileTex, asShader=True)
    cmds.connectAttr('%s.outColor' %fileTex, '%s.color' %lamShd, f = True)
    cmds.connectAttr('%s.outColor' %lamShd, '%s.surfaceShader' %shadingEngine, f = True)


def assignSurfMatWithPickColor(*args):
    selGeo = cmds.ls( sl=True )[0]

    shapeName = cmds.ls( selGeo, s=True, dag=True )
    shadingEngine = cmds.listConnections( shapeName, d=True, type="shadingEngine" )[0]

    color = cmds.grabColor(rgb = True)

    shaderName = cmds.shadingNode( 'lambert', n='%s_solCol_mat' %selGeo, asShader=True )
    cmds.setAttr("%s.color" %shaderName, color[0], color[1], color[2], type = 'double3')
    cmds.setAttr('%s.diffuse' %shaderName, 1)

    cmds.connectAttr('%s.outColor' %shaderName, '%s.surfaceShader' %shadingEngine, f = True)


def getInstances():
    instances = []
    iterDag = OpenMaya.MItDag(OpenMaya.MItDag.kBreadthFirst)
    while not iterDag.isDone():
        instanced = OpenMaya.MItDag.isInstanced(iterDag)
        if instanced:
            instances.append(iterDag.fullPathName())
        iterDag.next()
    return instances

def uninstance(*args):
    instances = getInstances()
    while len(instances):
        parent = cmds.listRelatives(instances[0], parent=True, fullPath=True)[0]
        cmds.duplicate(parent, renameChildren=True)
        cmds.delete(parent)
        instances = getInstances()




def chkNamespace(*args):
    '''
    Check unused namespace.
    '''

    namespaceList = cmds.namespaceInfo(lon=True)
    ignoreNamespaces = ['UI', 'shared']
    for _namespace in namespaceList:
        if not _namespace in ignoreNamespaces:
            cmds.NamespaceEditor()
            break

def uniqTransformName(*args):
    # UI
    if cmds.window('utnWin', exists = True):
	cmds.deleteUI('utnWin')
    cmds.window('utnWin', title = 'Unique Transform Name')
    cmds.frameLayout('mainframLay', labelVisible = False)
    cmds.textScrollList('utnTexScr', ams = True, selectCommand = partial(texScrListSelCmd, 'utnTexScr'), doubleClickCommand = utnDoubClicCmd)
    cmds.popupMenu()
    cmds.menuItem(label = 'Refresh List', c = utnPopuTexScr)
    cmds.menuItem(label = 'Delete Selected', c = utnDelSel)
    cmds.window('utnWin', e = True, w = 300, h = 300)

    result = notUniqNameExsistChk()

    if result:
        cmds.showWindow('utnWin')
        utnPopuTexScr()

def utnPopuTexScr(*args):
    if cmds.textScrollList('utnTexScr', q = True, allItems = True):
        cmds.textScrollList('utnTexScr', e = True, removeAll = True)
    # populate scroll list with not unique transform name
    sceneList = cmds.ls()
    for item in sceneList:
        if '|' in item and cmds.objectType(item) != 'mesh':
            cmds.textScrollList('utnTexScr', e = True, append = item)

def utnDelSel(*args):
    selItems = cmds.textScrollList('utnTexScr', q = True, selectItem = True)
    cmds.delete(selItems)

def utnDoubClicCmd(*args):
    origName = cmds.textScrollList('utnTexScr', q = True, selectItem = True)[0]
    origNiceName = origName.rsplit('|')[-1]
    result = cmds.promptDialog(title = 'Rename Object',
                               message = 'Enter Name:',
                               button = ['OK', 'Cancel'],
                               defaultButton = 'OK',
                               cancelButton = 'Cancel',
                               dismissString = 'Cancel',
                               text = origNiceName)
    if result == 'OK':
	newName = cmds.promptDialog(q = True, text = True)
	cmds.rename(origName, newName)
    # refresh unique name list
    utnPopuTexScr()

def notUniqNameExsistChk():
    '''
    Check if not unique named object exists in the current scene.
    '''

    sceneList = cmds.ls(type = 'transform')

    if '|' in str(sceneList):
        return True
    else:
        return False


def texScrListSelCmd(widgetName, *args):
    selItem = cmds.textScrollList(widgetName, q = True, selectItem = True)
    cmds.select(selItem, r = True)

def autoUniqName(*args):
    sceneList = cmds.ls()
    notUniqTranList = []
    notUniqTranDic = {}
    # get not unique trasform list
    for item in sceneList:
	if '|' in item and not 'Shape' in item:
	    notUniqTranList.append(item)
    # get dictionary that contains hierachy level information as value for each item in notUniqTranList
    for each in notUniqTranList:
	hierLevel = len(each.split('|'))
	notUniqTranDic[each] = hierLevel
    # get hierarchy level list and sorting
    valueList = notUniqTranDic.values()
    valueList.sort()
    # index and number variables
    i = -1
    n = 0
    # rename part
    for value in valueList:
	for k, v in notUniqTranDic.iteritems():
	    if v == valueList[i]:
		objName = k.rpartition('|')[2]
		cmds.rename(k, objName + '_uNum' + str(n))
		break
	notUniqTranDic.pop(k)
	i -= 1
	n += 1

def matchShape(*args):
    selList = cmds.ls(sl = True, type = 'transform')

    for sel in selList:
        # Get shape name
        shpLs = cmds.listRelatives(sel, s = True, fullPath = True)

        if shpLs:
            shapName = shpLs[0]

            # If not match to transform name then rename.
            if shapName != '%sShape' %sel:
                # In case transform name is not unique.
                if '|' in sel:
                    niceShpBaseName = sel.rsplit('|')[-1]
                    cmds.rename(shapName, '%sShape' %niceShpBaseName)
                else:
                    cmds.rename(shapName, '%sShape' %sel)





def selVtx(*args):
    sel = cmds.ls(sl = True, fl = True)
    if not 'vtx' in str(sel):
	sel = sel[0]
	numOfVtx = cmds.polyEvaluate(sel, v = True)
    else:
	numOfVtx = len(sel)
    threshold = cmds.floatField('mergeVtxThres', q = True, v = True)
    matchingVtxList = []

    # progressionBar
    if cmds.window('progWin', exists = True): cmds.deleteUI('progWin')
    cmds.window('progWin', title = 'Searching vertices...')
    cmds.columnLayout()
    cmds.progressBar('vtxProgBar', minValue = 0, maxValue = numOfVtx, width = 300, isMainProgressBar = True, beginProgress = True, isInterruptable = True)
    cmds.window('progWin', e = True, w = 300, h = 10)
    cmds.showWindow('progWin')

    for i in xrange(numOfVtx):
        if cmds.progressBar('vtxProgBar', q = True, isCancelled = True):
            break
        cmds.progressBar('vtxProgBar', e = True, step = 1)

        if not 'vtx' in str(sel):
	    vtxPosA = cmds.pointPosition('%s.vtx[%d]' %(sel, i), world = True)
	else:
	    vtxPosA = cmds.pointPosition(sel[i], world = True)
        vtxVecA = OpenMaya.MVector(*vtxPosA)
        for v in range(numOfVtx)[i + 1::]:
            if not 'vtx' in str(sel):
		vtxPosB = cmds.pointPosition('%s.vtx[%d]' %(sel, v), world = True)
	    else:
		vtxPosB = cmds.pointPosition(sel[v])
            vtxVecB = OpenMaya.MVector(*vtxPosB)
            VecC = vtxVecB - vtxVecA
            if VecC.length() <= threshold:
		if not 'vtx' in str(sel):
		    matchingVtxList.append('%s.vtx[%d]' %(sel, i))
		    matchingVtxList.append('%s.vtx[%d]' %(sel, v))
		else:
		    matchingVtxList.append(sel[i])
		    matchingVtxList.append(sel[v])

    cmds.progressBar('vtxProgBar', e = True, endProgress = True)
    cmds.deleteUI('progWin')
    # remove repeated items
    matchingVtxList = list(set(matchingVtxList))
    if matchingVtxList:
        cmds.select(matchingVtxList, r = True)
	mel.eval('print "Matching vertices selected."')
    else:
	cmds.select(cl = True)
        mel.eval('print "No vertices to match."')

def mergeVtx(*args):
    threshold = cmds.floatField('mergeVtxThres', q = True, v = True)
    cmds.polyMergeVertex(distance = threshold)






def getVtxInfo(sel):
    numOfVtx = cmds.polyEvaluate(v = True)
    leftVtxDic = {}
    rightVtxDic = {}
    centerVtxDic = {}

    try:
        ctVtxTol = cmds.floatField('ctVtxTolFltFld', q = True, v = True)
    except:
        ctVtxTol = 0.001

    for i in xrange(numOfVtx):
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
    return leftVtxDic, rightVtxDic, centerVtxDic

def getSidestVtx(vtxInfoDic):
    vtxName = ''
    sidestVal = 0

    for vtx in vtxInfoDic.keys():
        vtxPosition = vtxInfoDic[vtx]
        if sidestVal < abs(vtxPosition[0]):
            vtxName = vtx
            sidestVal = abs(vtxPosition[0])

    return vtxName

def checkSym(*args):
    sel = cmds.ls(sl = True)[0]
    aSymVtxList = []
    # get data
    leftVtxDic, rightVtxDic, centerVtxDic = getVtxInfo(sel)
    # search asymmetrical vertices
    for lVtx in leftVtxDic.keys():
	symVtxPos = -leftVtxDic[lVtx][0], leftVtxDic[lVtx][1], leftVtxDic[lVtx][2]
	if not symVtxPos in rightVtxDic.values():
	    aSymVtxList.append(lVtx)
    for rVtx in rightVtxDic.keys():
	symVtxPos = -rightVtxDic[rVtx][0], rightVtxDic[rVtx][1], rightVtxDic[rVtx][2]
	if not symVtxPos in leftVtxDic.values():
	    aSymVtxList.append(rVtx)
    # report the result
    if aSymVtxList:
            cmds.warning('"%s" is not symmetrical.' %sel)
            cmds.select(aSymVtxList)
            return False
    else:
	mel.eval('print "%s is symmetrical."' %sel)
        return True

def matchMirrorVtxPosition(searchTolerance):
    vtxs = cmds.ls(sl=True, fl=True)
    if not '.' in str(vtxs):
        return

    lfVtxs = [vtx for vtx in vtxs if cmds.pointPosition(vtx, local=True)[0] > 0]
    rtVtxs = list(set(vtxs) - set(lfVtxs))

    nonMatchVtxs = []

    for leftVtx in lfVtxs:
        vtxPoint = OpenMaya.MPoint(*cmds.pointPosition(leftVtx, local=True))
        mirrorPoint = OpenMaya.MPoint(-vtxPoint.x, vtxPoint.y, vtxPoint.z)

        mirrorVtx = findMirrorVtx(mirrorPoint, rtVtxs, searchTolerance=searchTolerance)
        if mirrorVtx:
            rtVtxs.pop(rtVtxs.index(mirrorVtx))
            cmds.xform(mirrorVtx, translation=[mirrorPoint.x, mirrorPoint.y, mirrorPoint.z], os=True)
        else:
            nonMatchVtxs.append(leftVtx)

    cmds.select(nonMatchVtxs, rtVtxs, r=True)


def findMirrorVtx(mirrorPoint, vtxList, searchTolerance):
    resultVtx = None
    minDistance = 100
    for vtx in vtxList:
        vtxPoint = OpenMaya.MPoint(*cmds.pointPosition(vtx, local=True))
        vec = vtxPoint - mirrorPoint
        if vec.length() <= searchTolerance and vec.length() <= minDistance:
            minDistance = vec.length()
            resultVtx = vtx
    return resultVtx

def makeSym(*args):
    selLs = cmds.ls(sl = True)

    # When user select center edge loop.
    if '.e' in selLs[0]:
        numOfShells = cmds.polyEvaluate(shell = True)
        if numOfShells > 1:
            cmds.confirmDialog(title = 'Warning', message = 'Selected mesh is made of combining several geometry. Separate mesh and try it again.')
            return False

        centerEdgeLoop = selLs
        objName = centerEdgeLoop[0].split('.')[0]
        uvKeepGeo = cmds.duplicate(objName, n = '{0}_uvKeep_geo'.format(objName))

        mel.eval('PolySelectConvert 3;')
        tak_misc.zeroVtx()

        cmds.select(centerEdgeLoop, r = True)
        cmds.DetachComponent()

        leftVtxDic, rightVtxDic, centerVtxDic = getVtxInfo(objName)

        symOpt = cmds.radioButtonGrp('symOptRadButGrp', q = True, select = True)

        # If user select 'x to -x' mean left to right.
        if symOpt == 1:
            rightestVtx = getSidestVtx(rightVtxDic)
            cmds.select(rightestVtx, r = True)
            mel.eval('PolySelectConvert 1;') # Convert vertex selection to face.

            rightestFace = cmds.ls(sl = True, fl = True)[0]
            rightestFaceId = int(re.search(r'.+f\[(\d+)\]', rightestFace).group(1))
            cmds.polySelect(extendToShell = rightestFaceId)
            cmds.delete()

            # mirror geometry
            mirrorNode = cmds.polyMirrorFace(objName, ws = True, direction = 1, mergeMode = 0, mergeThreshold = 0.001, ch = True)
            cmds.polyMirrorFace(mirrorNode, e = True, pivotX = 0.0)

        # If user select '-x to x' mean right to left.
        if symOpt == 2:
            leftestVtx = getSidestVtx(leftVtxDic)
            cmds.select(leftestVtx, r = True)
            mel.eval('PolySelectConvert 1;') # Convert vertex selection to face.

            leftestFace = cmds.ls(sl = True, fl = True)[0]
            leftestFaceId = int(re.search(r'.+f\[(\d+)\]', leftestFace).group(1))
            cmds.polySelect(extendToShell = leftestFaceId)
            cmds.delete()

            # mirror geometry
            mirrorNode = cmds.polyMirrorFace(objName, ws = True, direction = 1, mergeMode = 0, mergeThreshold = 0.001, ch = True)
            cmds.polyMirrorFace(mirrorNode, e = True, pivotX = 0.0)

    # When user select object.
    else:
        objName = selLs[0]
        uvKeepGeo = cmds.duplicate(objName, n = '{0}_uvKeep_geo'.format(objName))

        leftVtxDic, rightVtxDic, centerVtxDic = getVtxInfo(objName)

        symOpt = cmds.radioButtonGrp('symOptRadButGrp', q = True, select = True)

        if centerVtxDic.keys():
            cmds.select(centerVtxDic.keys(), r = True)
            mel.eval('SelectEdgeLoopSp;')
            tak_misc.zeroVtx()

        leftVtxDic, rightVtxDic, centerVtxDic = getVtxInfo(objName) # Refresh vertex position information.

        # If user select 'x to -x' mean left to right.
        if symOpt == 1:
            cmds.select(rightVtxDic.keys(), r = True)
            mel.eval('PolySelectConvert 1;') # Convert vertex selection to face.
            cmds.delete()

            # mirror geometry
            mirrorNode = cmds.polyMirrorFace(objName, ws = True, direction = 1, ch = True)
            cmds.polyMirrorFace(mirrorNode, e = True, pivotX = 0.0)

        # If user select 'x to -x' mean right to left.
        if symOpt == 2:
            cmds.select(leftVtxDic.keys(), r = True)
            mel.eval('PolySelectConvert 1;') # Convert vertex selection to face.
            cmds.delete()

            # mirror geometry
            mirrorNode = cmds.polyMirrorFace(objName, ws = True, direction = 1, ch = True)
            cmds.polyMirrorFace(mirrorNode, e = True, pivotX = 0.0)


    leftVtxDic, rightVtxDic, centerVtxDic = getVtxInfo(objName)
    if centerVtxDic.keys():
        cmds.select(centerVtxDic.keys(), r = True)
        cmds.polyMergeVertex(distance = 0.001)


    # Copy uv from uv keeped geometry to new symmetrized geometry.
    smpSpc = cmds.radioButtonGrp('symSmpSpcRdoBtn', q = True, select = True)
    if smpSpc == 2:
        smpSpc = 4
    elif smpSpc == 3:
        smpSpc = 5
    cmds.transferAttributes(uvKeepGeo, objName, transferUVs = 2, sampleSpace = smpSpc)

    # cmds.select(objName, r = True)
    # mel.eval("SoftPolyEdgeElements 1;")

    # cmds.select(objName, r = True)
    # mel.eval('polyNormalPerVertex -ufn true;')

    cmds.delete(objName, ch = True)
    cmds.delete(uvKeepGeo)

    cmds.select(objName, r = True)
    # cmds.select(origMesh, add = True)





def tglTwoSidedLit(*args):
    hudWdgName = 'twoSidedHud'

    curPanel = cmds.paneLayout('viewPanes', q = True, pane1= True)
    if cmds.modelEditor(curPanel, q = True, twoSidedLighting = True):
        cmds.modelEditor(curPanel, e = True, twoSidedLighting = False)
        cmds.headsUpDisplay(hudWdgName, remove = True)
    else:
        cmds.modelEditor(curPanel, e = True, twoSidedLighting = True)
        tak_lib.showHUD(hudWdgName, title = 'Two Sided Lighting On')





def cleanChBox(*args):
    mel.eval('source channelBoxCommand;')
    attrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ', 'visibility']
    selList = cmds.ls(sl = True)

    for sel in selList:
        # If sel is shape, skip sel.
        if cmds.objectType(sel) == 'mesh' or "Shape" in sel:
            continue
        # unlock attribute
        for attr in attrList:
            cmds.setAttr(sel + '.' + str(attr), lock = False)
        # break connections
        for attr in attrList:
            cmds.delete('{0}.{1}'.format(sel, attr), inputConnectionsAndNodes = True)
            mel.eval('CBdeleteConnection' + ' %s.%s;' %(sel, attr))

    cmds.select(selList, r = True)





def chkFrzTrsfm(*args):
    attrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ', 'visibility']
    selList = cmds.ls(sl = True)
    freTranVal = (0, 0, 0, 0, 0, 0, 1, 1, 1)
    tranValList = []
    nonFreTranList = []

    for sel in selList:
            # if sel is not transform node, skip to next item
            if cmds.objectType(sel) != 'transform':
                continue

            # get channel value list of sel
            for attr in attrList:
                attrVal = cmds.getAttr('%s.%s' %(sel, attr))
                tranValList.append(attrVal)
            # remove visibility value
            tranValList.pop(-1)

            if tuple(tranValList) != freTranVal:
                nonFreTranList.append(sel)
            tranValList = []
    nonfrzTrnsfUI(nonFreTranList)
    if selList:
        cmds.select(selList, r = True)

def nonfrzTrnsfUI(nonFreTranList):
    winName = 'freTranWin'
    if cmds.window(winName, exists = True):
        cmds.deleteUI(winName)
    cmds.window(winName, title = 'Non Freeze Transform List')
    cmds.columnLayout('mainColLay', adj = True)
    cmds.frameLayout('mainframLay', labelVisible = False)
    cmds.textScrollList('freTranTexScr', h = 150, selectCommand = partial(texScrListSelCmd, 'freTranTexScr'), allowMultiSelection = True)
    cmds.setParent('mainColLay')
    cmds.button('freTranBtn', label = 'Freeze Transform Selected', h = 50, c = freTranSel)
    cmds.window(winName, e = True, w = 250, h = 200)
    if nonFreTranList:
        cmds.showWindow(winName)
        freTranPopuTexScr(nonFreTranList)
    else:
        cmds.deleteUI(winName)

def freTranPopuTexScr(nonFreTranList):
    if cmds.textScrollList('freTranTexScr', q = True, allItems = True):
        cmds.textScrollList('freTranTexScr', e = True, removeAll = True)
    # populate scroll list with nonFreTranList
    cmds.textScrollList('freTranTexScr', e = True, append = nonFreTranList)

def freTranSel(*args):
    cmds.makeIdentity(apply = True)
    sel = cmds.textScrollList('freTranTexScr', q = True, selectItem = True)
    cmds.textScrollList('freTranTexScr', e = True, removeItem = sel)
    if not cmds.textScrollList('freTranTexScr', q = True, allItems = True):
        cmds.deleteUI('freTranWin')





def resetVtx(*args):
    selList = cmds.ls(sl = True)

    # progress window
    cmds.progressWindow(title = 'Reset Vertex', minValue = 0, maxValue = len(selList), progress = 0, status = 'Stand by', isInterruptable = True)

    for sel in selList:
        if cmds.progressWindow(q = True, isCancelled = True):
        	break

        cmds.progressWindow(e = True, progress = selList.index(sel), status = 'Working on \'%s\'' %(sel))

        if not cmds.listRelatives(sel, path = True, s = True, ni = True):
            continue
        else:
            # Reset vertex
            try:
                cmds.polyMoveVertex(sel, localTranslate = (0, 0, 0))
            except:
                pass

    cmds.progressWindow(e = True, progress = 0, status = 'Reset Vertex Work Done.')
    cmds.progressWindow(endProgress = True)

    cmds.select(selList, r = True)





def delHis(*args):
    cmds.delete(ch = True)





def delInterMediObj(*args):
    selList = cmds.ls(sl = True)
    for sel in selList:
	    # delete intermediate object
	    itmdShapList = cmds.ls(sel, dag = True, s = True, io = True)
	    for shap in itmdShapList:
		    intmResult = cmds.getAttr('%s.intermediateObject' %(shap))
		    if intmResult:
			cmds.delete(shap)
			print 'Intermediate object "%s" is deleted.' %shap






def setShpAttrs(*args):
    selList = cmds.ls(sl = True)
    for sel in selList:
        if cmds.objectType(sel) == 'transform':
            selShape = cmds.listRelatives(sel, c = True, s = True, path = True)
            # If transform has no shape, skip to next item.
            if not selShape:
                continue
            elif len(selShape) > 1:
                continue
                # cmds.error("%s object has more than one shape." %sel)
            else:
                # Check if selShape is uniqe.
                if not tak_lib.isUniqeName(selShape):
                    cmds.error("%s object's name is not uniqe. May exists same object name." %sel)

            # turn off drawing override of the shape
            drovInput = cmds.listConnections('%s.drawOverride' %selShape[0], s = True, d = False, p = True)
            if drovInput:
                cmds.disconnectAttr(drovInput[0], '%s.drawOverride' %selShape[0])
            cmds.setAttr('%s.overrideEnabled' %selShape[0], 0)
            if cmds.objExists('%s.doubleSided' %selShape[0]):
                cmds.setAttr('%s.doubleSided' %selShape[0], 1)
            if cmds.objExists('%s.opposite' %selShape[0]):
                cmds.setAttr('%s.opposite' %selShape[0], 0)
            if cmds.objExists('%s.primaryVisibility' %selShape[0]):
                cmds.setAttr('%s.primaryVisibility' %selShape[0], 1)

        # if sel is shape, set overrideEnabeld to 0
        elif cmds.objectType(sel) == 'mesh':
            drovInput = cmds.listConnections('%s.drawOverride' %sel, s = True, d = False, p = True)
            if drovInput:
                cmds.disconnectAttr(drovInput[0], '%s.drawOverride' %sel)
            cmds.setAttr('%s.overrideEnabled' %sel, 0)
            cmds.setAttr('%s.doubleSided' %sel, 1)
            cmds.setAttr('%s.opposite' %sel, 0)
            cmds.setAttr('%s.primaryVisibility' %sel, 1)
        else:
            pass





def delUnused(*args):
    mel.eval('source cleanUpScene;')

    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    mel.eval('scOpt_performOneCleanup( { "unknownNodesOption" } );')






def delLayer(*args):
    cmds.editRenderLayerGlobals(currentRenderLayer = 'defaultRenderLayer')
    disLayList = cmds.ls(type = 'displayLayer')
    renLayList = cmds.ls(type = 'renderLayer')

    for disLay in disLayList:
	if disLay != 'defaultLayer':
	    cmds.delete(disLay)

    for renLay in renLayList:
	if renLay != 'defaultRenderLayer':
	    cmds.delete(renLay)





def pipeHier(*args):
    '''
    Build group hierarchy structure depend on pipeline.
    '''

    # Create pipeline hierarchy structure.
    hierDic = { 'wip_GRP': ['base_body_grp', 'light_cam_grp'],
                'root': ['geometry'],
                'geometry': ['lod03_GRP', 'hair_fur_grp'],
                'lod03_GRP': ['facial_grp', 'body_grp', 'cloth_grp', 'polyHair_grp'],
                'hair_fur_grp': ['renderHair_grp', 'hairSystem_grp', 'input_crv_grp', 'output_crv_grp']}

    for item in hierDic.keys():
        if not cmds.objExists(item):
            cmds.createNode('transform', n = item)
        for child in hierDic[item]:
            if not cmds.objExists(child):
                cmds.createNode('transform', n = child, p = item)
            else:
                cmds.parent(child, item)





def delEmptyTrnsf(*args):
    ''' delete empty transform nodes '''
    trsfLs = cmds.ls(type = 'transform')
    emptyTrnsfLs = []

    for sel in trsfLs:
        if not cmds.listRelatives(sel, children = True, path = True) and not cmds.listConnections(sel):
            cmds.delete(sel)
            emptyTrnsfLs.append(sel)

    if emptyTrnsfLs:
        print '=' * 50
        for x in emptyTrnsfLs:
            print 'Empty Transform "%s" is deleted.' % x
        print '=' * 50





def intoDfltDisLyr(*args):
    '''
    Move selected geometry into 'defaultDisplayLayer'.
    '''

    selList = cmds.ls(sl = True)
    cmds.editDisplayLayerMembers('defaultLayer', selList)





def freezeTrnf(*args):
    '''
    Freeze transform.
    '''

    sels = cmds.ls(sl = True, dag = True)

    # Get place3dTexture nodes.
    plc3dTexLs = cmds.ls(sl = True, dag = True, type = 'place3dTexture')

    # Get place3dTexture nodes's parent group.
    plc3dTexGrpLs = []
    for plce3dTex in plc3dTexLs:
        plc3dTexGrpLs.append(cmds.listRelatives(plce3dTex, p = True, path = True)[0])

    plc3dTexGrpLs = list(set(plc3dTexGrpLs))


    # Get ordered list for group.
    plc3dTexDic = {}
    for grp in plc3dTexGrpLs:
        plc3dTexLsInOrder = cmds.listRelatives(grp, path = True)
        plc3dTexLsInOrder = [x for x in plc3dTexLsInOrder if 'Shape' not in x]
        plc3dTexDic[grp] = plc3dTexLsInOrder

    # Parent to the world.
    for plc3dTex in plc3dTexLs:
        cmds.parent(plc3dTex, world = True)

    # Remove place3dTexture in selection list.
    for plce3dTex in plc3dTexLs:
        sels.remove(plce3dTex)

    # Freeze transform.
    cmds.select(sels, r = True)
    cmds.makeIdentity(apply = True)

    # Parent to the world for all childs of plce3dTexGrp.
    for grp in plc3dTexDic.keys():
        for item in plc3dTexDic[grp]:
            if not cmds.listRelatives(item, p = True) == None:
                cmds.parent(item, world = True)

    # Turn back.
    for grp in plc3dTexDic.keys():
        for item in plc3dTexDic[grp]:
            cmds.parent(item, grp)

    cmds.select(sels, r = True)





def setSubdMayaCatmullClark(*args):
    '''
    Set subdivision method to maya catmull-clark.
    'Opensubdiv catmull-clark' and 'opensubdiv catmull-clark adaptive 'subdivision method has some problem on viewport.
    '''

    selMeshLs = cmds.ls(sl = True, dag = True, type = 'mesh', ni = True)

    for mesh in selMeshLs:
        cmds.setAttr('%s.useGlobalSmoothDrawType' %mesh, 0)
        cmds.setAttr('%s.smoothDrawType' %mesh, 0)





def rmvMILabel(*args):
    '''
    Remove material id label in transform node.
    '''

    selTrsfLs = cmds.ls(sl = True, dag = True, type = 'transform')

    for trsf in selTrsfLs:
        if cmds.objExists('%s.miLabel' %trsf):
            cmds.deleteAttr('%s.miLabel' %trsf)



def delChildOfShape(*args):
	""" Delete children of shape that isn't necessary """
	shapes = pm.ls(sl=True, type='shape')
	for shape in shapes:
		junkShapes = shape.listRelatives()
		if junkShapes:
			pm.delete(junkShapes)


def findOverlappedRootCurve(*args):
    rootCVs = [crv.getShape().cv[0] for crv in pm.selected()]
    thresholds = 0.1
    stackedCvs = []
    for i in xrange(len(rootCVs)):
        iCvPos = rootCVs[i].getPosition(space='world')
        for cv in rootCVs[i+1:]:
            cvPos = cv.getPosition(space='world')
            if (cvPos - iCvPos).length() <= thresholds:
                stackedCvs.append(cv)

    pm.select([cv.split('.')[0] for cv in stackedCvs], r=True)


def checkOverlapVertices(*args):
    overlapVertices = []
    for sel in pm.selected():
        overlapVertices.extend(pm.checkOverlapVertices(sel))
    pm.select(overlapVertices, r=True)


def allInOne(*args):
	delChildOfShape()
	matchShape()
	cleanChBox()
	freezeTrnf()
	resetVtx()
	delHis()
	delInterMediObj()
	setShpAttrs()
	intoDfltDisLyr()
	rmvMILabel()
	cmds.PolyDisplayReset()
