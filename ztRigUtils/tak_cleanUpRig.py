'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 11/11/2015

Description:
Script to help clean up the rig.

Usage:
import tak_cleanUpRig
reload(tak_cleanUpRig)
tak_cleanUpRig.ui()
'''

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
from functools import partial
import tak_cleanUpModel
import tak_lib



reload(tak_lib)
reload(tak_cleanUpModel)


mel.eval('source channelBoxCommand;')
mel.eval('source cleanUpScene;')


def ui():
    '''
    Main ui.
    '''

    winName = 'cleanUpRigWin'
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)
    if cmds.window('ripGrpWin', exists=True):
        cmds.deleteUI('ripGrpWin')

    cmds.window(winName, title='Clean Up Rig', mnb=False, mxb=False)

    cmds.columnLayout('mainColLo', p=winName, adj=True)

    cmds.button(label="Check material that assigned to face for render model.", c=chkFaceAssignedMat)
    cmds.button(label="Check Freeze Transform State", c=chkTrsfIdentity)
    cmds.separator(h=5, style='in')
    cmds.button(label="Connect lod02 Deformation to lod03 Model", c=cntLod02ToLod03,
                annotation="If selected object exists then assign to selection.")
    cmds.button(label="Connect lod02 Attributes to lod03 Attributes", c=cntLod02AttrToLod03,
                annotation="If selected object exists then assign to selection.")
    cmds.separator(h=5, style='in')
    cmds.button(label="Add Selected or lod01~03 to 'geo_layer'", c=addGeoLayer,
                annotation='Add selected geometries to the geo_layer.')
    cmds.button(label="Remove Unused Influences in 'geo_layer'", c=rmvUnuseInf)
    cmds.button(label='Visibility Attributes Set Up on Selected Control', c=visCtrl)
    cmds.button(label="'floorContactCheck_geo' set up", c=flrCntChkGeoSet)
    # cmds.button(label = "Add Control(s) to The Control Sets/Create Control Set", c = addCtrlSets)
    cmds.text(label="# Lock and Hide Unusing Attributes for Control Curves")
    cmds.text(label="# Clean Up Outliner(Parent unused objects to 'wip_GRP')")
    cmds.separator(h=5, style='in')
    cmds.button(label="Lock Geometry Transform", c=lockGeoTrsf)
    cmds.button(label="Delete Display/Render/Animation Layers", c=delAllLayers)
    cmds.button(label="Delete Keys and Set to Default Value", c=delKeys)
    cmds.button(label="Check Namespace", c=chkNamespace)
    cmds.button(label="Delete Caches", c=delCache)
    cmds.button(label="Hide Joints", c=hideJoints)
    cmds.button(label="Remove Constraints Under Rendel Model Group.", c=rmvRenMdlCnst)
    cmds.button(label='Remove Unused Animation Curves', c='''mel.eval('deleteUnusedCommon("animCurve", 0, uiRes("m_cleanUpScene.kDeletingUnusedAnimationCurves2"));')''')
    cmds.button(label="All in One", c=allInOne, h=40, bgc=[0, 0.5, 0.5])

    cmds.separator(h=5, style='in')
    cmds.button(label="Ready to Publish Render Model", c=cleanUpMdl, h=50, bgc=[1, 0.5, 0.2])

    cmds.setParent('mainColLo')
    cmds.frameLayout(label="Extra Functions", collapsable=True, collapse=True)
    cmds.columnLayout(adj=True)
    cmds.button(label='Add Smooth Control', annotation='Select a controller to add smooth control. Smooth will add to meshes under the lod03_GRP.', c=addSmoothCtrl)
    cmds.button(label='Make Rig Group UI', c=rigGrpUI)
    cmds.button(label="Show Joints", c=showJoints)
    cmds.button(label="Unlock lod01/02/03 Transform in Channelbox", c=unlockGeoTrsf)
    cmds.button(label="Remove Selected from 'geo_layer'", c=rmvGeoLayer,
                annotation='Add selected geometries from the geo_layer.')
    cmds.button(label="Remove Control(s) from The Control Sets", c=rmvCtrlSets)
    cmds.button(label='Set Smooth Level Control with Selected Control', c=setSmoothLevelCtrl)
    cmds.button(label="Check Hierarchy Old Model vs New Model", c=chkHierOldNewMdl,
                ann='Select old model lod03_GRP and new model lod03_GRP in order then click button.')
    cmds.button(label="Check Topology Old Model vs New Model", c=chkTopoOldNewMdl,
                ann='Select old model lod03_GRP and new model lod03_GRP in order then click button.')

    cmds.window(winName, e=True, w=200, h=50)
    cmds.showWindow(winName)


def cntLod02ToLod03(*args):
    selLs = cmds.ls(sl=True, dag=True, g=True, ni=True)
    lod02ShpLs = selLs if selLs else cmds.ls('lod02_GRP', dag=True, g=True, ni=True)

    for shp in lod02ShpLs:
        lod02Geo = cmds.listRelatives(shp, p=True)[0]
        lod03Geo = lod02Geo.split('lod02_')[-1]

        if cmds.objExists(lod03Geo):
            lod03DefLs = tak_lib.getAllDeformers(lod03Geo)
        else:
            OpenMaya.MGlobal.displayWarning('"%s" is not exists that matching with "%s". Skip this' % (lod03Geo, lod02Geo))
            continue

        if not lod03DefLs:
            try:
                cmds.blendShape(lod02Geo, lod03Geo, frontOfChain=True, w=[0, 1])
            except:
                OpenMaya.MGlobal.displayWarning('"%s" has different topology compare to "%s". Connect using wrap' % (lod02Geo, lod03Geo))
                cmds.select(lod03Geo, lod02Geo)
                cmds.CreateWrap()


def cntLod02AttrToLod03(*args):
    """
    Connect rigged lod02 model's keyable attributes to lod03 render model's attributes.
    """

    selLs = cmds.ls(sl=True, type="transform")

    lod02ObjLs = cmds.listRelatives('lod02_GRP', ad=True, type='transform')
    if selLs:
        lod02ObjLs = selLs

    unlockGeoTrsf()

    notExistsAttrLs = []
    lockOrCnctedAttrLs = []

    for lod02Obj in lod02ObjLs:
        if exclNameChk(lod02Obj):
            continue
        else:
            pairLod03Obj = lod02Obj.split('lod02_')[-1]

            keyAbleAttrLs = cmds.listAttr(lod02Obj, keyable=True, visible=True)
            for attr in keyAbleAttrLs:
                if exclNameChk(attr):
                    continue
                else:
                    if cmds.objExists('%s.%s' % (pairLod03Obj, attr)):
                        try:
                            cmds.connectAttr('%s.%s' % (lod02Obj, attr), '%s.%s' % (pairLod03Obj, attr), f=True)
                        except:
                            lockOrCnctedAttrLs.append('%s.%s' % (pairLod03Obj, attr))
                    else:
                        notExistsAttrLs.append('%s.%s' % (pairLod03Obj, attr))

    if notExistsAttrLs or lockOrCnctedAttrLs:
        divider = '=' * 30
        joinStr = "\n"
        # cmds.confirmDialog(title = 'Warning', message = "In lod03_GRP\nThe following attributes are don't exists\n%s\n%s\n%s\n\nThe following attributes are locked or connected already\n%s\n%s\n%s" %(divider, str(joinStr.join(notExistsAttrLs)), divider, divider, str(joinStr.join(lockOrCnctedAttrLs)), divider))
        print "In lod03_GRP\nThe following attributes are don't exists\n%s\n%s\n%s\n\nThe following attributes are locked or connected already\n%s\n%s\n%s" % (
        divider, str(joinStr.join(notExistsAttrLs)), divider, divider, str(joinStr.join(lockOrCnctedAttrLs)), divider)


def exclNameChk(inputName):
    '''
    Checking whether given name inclued in cheking list.
    If given name is exclusive name then return True.
    '''

    exclusiveNameLs = ['Constraint', 'dropoff', 'smoothness']

    for name in exclusiveNameLs:
        if name in inputName:
            return True
        else:
            continue

    return False


def flrCntChkGeoSet(*args):
    flrCntChkGeo = cmds.ls(sl=True)

    cmds.rename(flrCntChkGeo, 'floorContactCheck_geo')

    renAttrLs = ['castsShadows', 'receiveShadows', 'primaryVisibility', 'visibleInReflections', 'visibleInRefractions']
    for renAttr in renAttrLs:
        cmds.setAttr('floorContactCheck_geoShape.%s' % renAttr, False)

    cmds.setAttr('floorContactCheck_geo.inheritsTransform', False)
    cmds.connectAttr('Sub.floorContactCheckVis', 'floorContactCheck_geo.visibility', f=True)

    if not cmds.objExists('misc_rig_grp'):
        cmds.createNode('transform', n='misc_rig_grp')
        cmds.parent('misc_rig_grp', 'Sub')
    try:
        cmds.parent('floorContactCheck_geo', 'misc_rig_grp')
    except:
        pass


def rmvRenMdlCnst(*args):
    '''
    Move constriant nodes in 'lod03_GRP' under 'geometry' group.
    '''

    renMdlCnstLs = cmds.listRelatives('lod03_GRP', ad=True, path=True, type='constraint')
    if renMdlCnstLs:
        if cmds.objExists('renMdlCnst_grp'):
            cmds.parent(renMdlCnstLs, 'renMdlCnst_grp')
        else:
            cmds.select(renMdlCnstLs, r=True)
            cmds.group(p='geometry', n='renMdlCnst_grp')
    else:
        print '> There is no constraint assigned to geometry.'


def addGeoLayer(*args):
    '''
    Add selected geometry or geometries to the geo_layer.
    '''

    selList = cmds.ls(sl=True)

    if not cmds.objExists('geo_layer'):
        geoLayer = cmds.createNode('displayLayer', n='geo_layer')

    if selList:
        cmds.editDisplayLayerMembers('geo_layer', selList)
    else:
        cmds.select(cl=True)
        if cmds.objExists('lod01_GRP'):
            cmds.select('lod01_GRP', add=True, hi=True)
        if cmds.objExists('lod02_GRP'):
            cmds.select('lod02_GRP', add=True, hi=True)
        if cmds.objExists('lod03_GRP'):
            cmds.select('lod03_GRP', add=True, hi=True)
        if cmds.objExists('floorContactCheck_geo'):
            cmds.select('floorContactCheck_geo', add=True)

        selList = cmds.ls(sl=True)
        cmds.editDisplayLayerMembers('geo_layer', selList)


def rmvGeoLayer(*args):
    '''
    Remove selected geometry or geometries from 'geo_layer'.
    '''

    selList = cmds.ls(sl=True)
    cmds.editDisplayLayerMembers('defaultLayer', selList)


def visCtrl(*args):
    '''
    Set up visibility control for the rig.
    '''

    visCtrl = cmds.ls(sl=True)[0]

    # Check if attributes exists
    visAttrDic = {'lodVis': ['enum', 'Low', 'Mid', 'High'], 'geometryVis': ['enum', 'Normal', 'Template', 'Reference'],
                  'extraControlVis': ['bool'], 'facialControlVis': ['bool'], 'floorContactCheckVis': ['bool']}
    for visAttr in visAttrDic.keys():
        if cmds.objExists('%s.%s' % (visCtrl, visAttr)):
            continue
        else:
            if visAttrDic[visAttr][0] == 'enum':
                joinStr = ':'
                cmds.addAttr(visCtrl, ln=visAttr, at=visAttrDic[visAttr][0], en=joinStr.join(visAttrDic[visAttr][1:]))
                cmds.setAttr('%s.%s' % (visCtrl, visAttr), channelBox=True)
            elif visAttrDic[visAttr][0] == 'bool':
                if visAttr == 'modelVis':
                    cmds.addAttr(visCtrl, ln=visAttr, at=visAttrDic[visAttr][0], keyable=False)
                    if cmds.objExists('lod01_GRP'):
                        models = cmds.listRelatives('lod01_GRP')
                        if models:
                            for model in models:
                                cmds.connectAttr('%s.%s' % (visCtrl, visAttr), '%s.visibility' % model, f=True)

                    if cmds.objExists('lod02_GRP'):
                        models = cmds.listRelatives('lod02_GRP')
                        for model in models:
                            cmds.connectAttr('%s.%s' % (visCtrl, visAttr), '%s.visibility' % model, f=True)
                    else:
                        models = cmds.listRelatives('lod03_GRP')
                        for model in models:
                            cmds.connectAttr('%s.%s' % (visCtrl, visAttr), '%s.visibility' % model, f=True)
                else:
                    cmds.addAttr(visCtrl, ln=visAttr, at=visAttrDic[visAttr][0])
                    cmds.setAttr('%s.%s' % (visCtrl, visAttr), channelBox=True)

    # Connect attributes
    if not cmds.isConnected('%s.geometryVis' % visCtrl, 'geo_layer.displayType'):
        cmds.connectAttr('%s.geometryVis' % visCtrl, 'geo_layer.displayType', f=True)
    if cmds.objExists('facial_gui_grp'):
        if not cmds.isConnected('%s.facialControlVis' % visCtrl, 'facial_gui_grp.visibility'):
            cmds.connectAttr('%s.facialControlVis' % visCtrl, 'facial_gui_grp.visibility', f=True)
    if cmds.objExists('extra_ctrl_grp'):
        if not cmds.isConnected('%s.extraControlVis' % visCtrl, 'extra_ctrl_grp.visibility'):
            cmds.connectAttr('%s.extraControlVis' % visCtrl, 'extra_ctrl_grp.visibility', f=True)
    if cmds.objExists('floorContactCheck_geo'):
        if not cmds.isConnected('%s.floorContactCheckVis' % visCtrl, 'floorContactCheck_geo.visibility'):
            cmds.connectAttr('%s.floorContactCheckVis' % visCtrl, 'floorContactCheck_geo.visibility', f=True)

    # LOD visibility control setup
    if cmds.objExists('lod01_GRP'):
        mel.eval('CBdeleteConnection "lod01_GRP.visibility"')
    if cmds.objExists('lod02_GRP'):
        mel.eval('CBdeleteConnection "lod02_GRP.visibility"')
    if cmds.objExists('lod03_GRP'):
        mel.eval('CBdeleteConnection "lod03_GRP.visibility"')

    if cmds.objExists('lod02_GRP') and cmds.objExists('lod01_GRP'):
        cmds.setDrivenKeyframe('lod01_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=0, v=1)
        cmds.setDrivenKeyframe('lod02_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=0, v=0)
        cmds.setDrivenKeyframe('lod03_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=0, v=0)

        cmds.setDrivenKeyframe('lod01_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=1, v=0)
        cmds.setDrivenKeyframe('lod02_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=1, v=1)
        cmds.setDrivenKeyframe('lod03_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=1, v=0)

        cmds.setDrivenKeyframe('lod01_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=2, v=0)
        cmds.setDrivenKeyframe('lod02_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=2, v=0)
        cmds.setDrivenKeyframe('lod03_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=2, v=1)

    elif cmds.objExists('lod02_GRP') and not cmds.objExists('lod01_GRP'):
        cmds.setDrivenKeyframe('lod02_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=0, v=0)
        cmds.setDrivenKeyframe('lod03_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=0, v=0)

        cmds.setDrivenKeyframe('lod02_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=1, v=1)
        cmds.setDrivenKeyframe('lod03_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=1, v=0)

        cmds.setDrivenKeyframe('lod02_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=2, v=0)
        cmds.setDrivenKeyframe('lod03_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=2, v=1)

    elif cmds.objExists('lod02_GRP') and not cmds.objExists('lod01_GRP'):
        pass

    # Dynamic control visibility setup
    if cmds.objExists('dyn_ctr_crv'):
        if cmds.objExists('dyn_ctr_crv.clothSolverOnOff') and cmds.objExists('dyn_ctr_crv.hairSolverOnOff'):
            dynExprStr = '''
            // Expression for Dynamic Visibility //
            string $clothSolverState = dyn_ctr_crv.clothSolverOnOff;
            string $hairSolverState = dyn_ctr_crv.hairSolverOnOff;

            if (($hairSolverState == 1) || ($clothSolverState == 1)){
                geometry.visibility = 0;
                Geometry.visibility = 0;
            }
            else if (($hairSolverState == 0) && ($clothSolverState == 0)){
                geometry.visibility = 1;
                Geometry.visibility = 1;
            }
            '''
            cmds.expression(s=dynExprStr, ae=True, uc='all', n='dynVis_expr')

    # Turn off smooth preview for low poly group.
    if cmds.objExists('lod02_GRP'):
        cmds.select("lod02_GRP", r=True)
        mel.eval('setDisplaySmoothness 1;')

    cmds.select(visCtrl, r=True)


def setSmoothLevelCtrl(*args):
    # Smooth Level Set Up #
    addAttrToCtrl = cmds.ls(sl=True)[0]

    if cmds.objExists('%s.smoothLevel' % addAttrToCtrl):
        cmds.deleteAttr('Main.smoothLevel')
    cmds.addAttr(addAttrToCtrl, ln='smoothLevel', at='long', keyable=True, dv=0, min=0, max=2)

    # Connect smoothLevel attribute to render geometry's smoothLevel attribute.
    cmds.select('lod03_GRP', hi=True, r=True)
    mel.eval('setDisplaySmoothness 3;')
    renGeoShpLs = cmds.ls(sl=True, type='mesh')
    # cmds.HighQualityDisplay()
    for renGeoShp in renGeoShpLs:
        cmds.connectAttr('%s.smoothLevel' % (addAttrToCtrl), '%s.smoothLevel' % (renGeoShp), f=True)


def rmvUnuseInf(*args):
    '''
    Remove prune skin weights and remove unused skin influences for skin geometries.
    '''

    shpInGeoLyr = [x
                   for x in cmds.editDisplayLayerMembers('geo_layer', q=True)
                   if not cmds.getAttr(x + '.intermediateObject') and cmds.nodeType(x) == 'mesh']

    for shp in shpInGeoLyr:
        allDefSets = cmds.listSets(object=shp, type=2, extendToShape=True)
        if 'skinCluster' in str(allDefSets):
            cmds.select(shp, r=True)
            mel.eval('PruneSmallWeights;')
            mel.eval('removeUnusedInfluences;')


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


def delCache(*args):
    '''
    Delete nCahes, geoCaches in the current scene.
    '''

    cacheLs = cmds.ls(type='cacheFile')

    if not cacheLs:
        OpenMaya.MGlobal.displayInfo("There is no cache in current scene.")
        return

    nCacheShpLs = []
    geoCacheNodeLs = []

    for cache in cacheLs:
        cacheAllCnnt = cmds.listHistory(cache, future=True)

        if cmds.ls(cacheAllCnnt, type='nCloth'):
            nCacheShpLs.append(cmds.ls(cacheAllCnnt, type='nCloth')[0])
        elif cmds.ls(cacheAllCnnt, type='historySwitch'):
            geoCacheNodeLs.append(cache)

    if nCacheShpLs:
        cmds.select(nCacheShpLs, r=True)
        mel.eval('deleteCacheFile 3 { "keep", "", "nCloth" };')
        OpenMaya.MGlobal.displayInfo("%s\'s nCache deleted." % nCacheShpLs)

    if geoCacheNodeLs:
        cmds.delete(geoCacheNodeLs)
        mel.eval('deleteCacheFile 3 { "keep", "", "geometry" };')
        OpenMaya.MGlobal.displayInfo("geoCache [%s] deleted." % geoCacheNodeLs)


def addCtrlSets(*args):
    '''
    Add selected control(s) to the control sets.
    '''

    ctrls = cmds.ls(sl=True)

    if cmds.objExists('ControlSet'):
        cmds.sets(ctrls, add='ControlSet')
    else:
        cmds.sets(ctrls, n='ControlSet')

    if cmds.objExists('Sets'):
        cmds.sets('ControlSet', add='Sets')
    else:
        cmds.sets('ControlSet', n='Sets')


def rmvCtrlSets(*args):
    '''
    Remove selected control(s) from the control sets.
    '''

    ctrls = cmds.ls(sl=True)
    if cmds.objExists('ControlSet'):
        cmds.sets(ctrls, remove='ControlSet')


def lockGeoTrsf(*args):
    '''
    Lock geometries transform in channel box.
    '''

    # Select geometry group and all children.
    cmds.select('lod03_GRP', r=True, hi=True)
    if cmds.objExists('lod02_GRP'):
        cmds.select('lod02_GRP', add=True, hi=True)
    if cmds.objExists('lod01_GRP'):
        cmds.select('lod01_GRP', add=True, hi=True)
    cmds.select('root', 'geometry', add=True)
    if cmds.objExists('Geometry'):
        cmds.select('Geometry', add=True)

    selLs = cmds.ls(sl=True)
    for sel in selLs:
        attrs = cmds.listAttr(sel, keyable=True)
        for attr in attrs:
            if 'translate' in attr or 'rotate' in attr or 'scale' in attr:
                cmds.setAttr('%s.%s' % (sel, attr), lock=True)
            else:
                pass


def unlockGeoTrsf(*args):
    '''
    Unlock geometries transform in channel box.
    '''

    selLs = cmds.ls(sl=True)

    if selLs:
        pass
    else:
        # Select geometry group and all children.
        cmds.select('lod03_GRP', r=True, hi=True)
        if cmds.objExists('lod02_GRP'):
            cmds.select('lod02_GRP', add=True, hi=True)
        if cmds.objExists('lod01_GRP'):
            cmds.select('lod01_GRP', add=True, hi=True)
        cmds.select('root', 'geometry', add=True)
        if cmds.objExists('Geometry'):
            cmds.select('Geometry', add=True)

        selLs = cmds.ls(sl=True)

    for sel in selLs:
        attrs = cmds.listAttr(sel, keyable=True)
        for attr in attrs:
            if 'translate' in attr or 'rotate' in attr or 'scale' in attr:
                cmds.setAttr('%s.%s' % (sel, attr), lock=False)
            else:
                pass


def delKeys(*args):
    # # Remove unused animCurves.
    # mel.eval('scOpt_performOneCleanup( { "animationCurveOption" } );')

    # Go to the first frame
    # firstFrame = cmds.playbackOptions(q = True, min = True)
    cmds.currentTime(1)

    # If advanced skeleton is used launch advanced skeleton selector and select all controls in the control set.
    if cmds.objExists('Sets'):
        mel.eval('source "AdvancedSkeleton/Selector/biped.mel";asSelectorbiped;')
        mel.eval('asSelect "biped" {"ControlSet"};')
    if cmds.objExists('FKRoot_M'):
        cmds.select('FKRoot_M', add=True)

    # Delete keys
    ctrlList = cmds.ls(sl=True)
    cmds.select(ctrlList, r=True)
    mel.eval(
        'doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","0","animationList","0","noOptions","0","0" };')

    # Set default value.
    for ctrl in ctrlList:
        attrLs = cmds.listAttr(ctrl, keyable=True)
        if attrLs:
            for attr in attrLs:
                if 'translate' in attr or 'rotate' in attr:
                    try:
                        cmds.setAttr('%s.%s' % (ctrl, attr), 0)
                    except:
                        pass

    # # Playback timeline from start to end skipping 5 frame.
    # startFrame = cmds.playbackOptions(q = True, min = True)
    # endFrame = cmds.playbackOptions(q = True, max = True)
    # while startFrame < endFrame:
    # 	cmds.currentTime(startFrame)
    # 	startFrame += 5
    # cmds.currentTime(cmds.playbackOptions(q = True, min = True))

    # If advanced skeleton is used run reset pose.
    if cmds.objExists('Sets'):
        try:
            mel.eval("asGoToBuildPose asSelectorbiped;")
        except:
            pass


def allInOne(*args):
    '''
    Some stuff to publish rig.
    '''

    # Turn off inherits transform of 'geometry' group.
    cmds.setAttr('geometry.inheritsTransform', False)

    # Turn off visibility of place3dTexture nodes.
    plc3dTexLs = cmds.ls(type='place3dTexture')
    for plc3dTex in plc3dTexLs:
        try:
            cmds.setAttr(plc3dTex + '.visibility', 0)
        except:
            pass

    # Turn off visibility of nucleus nodes.
    nclsLs = cmds.ls(type='nucleus')
    for ncls in nclsLs:
        cmds.setAttr('%s.visibility' % ncls, False)

    # Set smooth preview
    if cmds.objExists('lod01_GRP'):
        cmds.select("lod01_GRP", r=True)
        mel.eval('setDisplaySmoothness 1;')
    if cmds.objExists('lod02_GRP'):
        cmds.select("lod02_GRP", r=True)
        mel.eval('setDisplaySmoothness 1;')
    if cmds.objExists('lod03_GRP'):
        cmds.select("lod03_GRP", r=True)
        mel.eval('setDisplaySmoothness 1;')

    # Delete Animation Layer #
    animLyrLs = cmds.ls(type='animLayer')
    if animLyrLs:
        cmds.delete(animLyrLs)

    addGeoLayer()
    delAllLayers()
    delKeys()
    lockGeoTrsf()
    chkNamespace()
    delCache()
    hideJoints()
    rmvRenMdlCnst()

    # Set visibility control attributes to default value.
    visCtrl = cmds.ls('*.geometryVis')
    if visCtrl:
        visCtrl = visCtrl[0].split('.')[0]
        if cmds.objExists(visCtrl + '.facialControlVis'): cmds.setAttr(visCtrl + '.facialControlVis', 1)
        if cmds.objExists(visCtrl + '.extraControlVis'): cmds.setAttr(visCtrl + '.extraControlVis', 1)
        if cmds.objExists(visCtrl + '.footDummyVis'): cmds.setAttr(visCtrl + '.footDummyVis', 1)
        if cmds.objExists(visCtrl + '.geometryVis'): cmds.setAttr(visCtrl + '.geometryVis', 2)
        if cmds.objExists(visCtrl + '.lodVis'): cmds.setAttr(visCtrl + '.lodVis', 1)
        if cmds.objExists(visCtrl + '.correctiveCtrlVis'): cmds.setAttr(visCtrl + '.correctiveCtrlVis', 0)

    globalScaleCtrl = cmds.ls('*.DefaultScale')
    if globalScaleCtrl:
        globalScaleCtrl = globalScaleCtrl[0].split('.')[0]
        try:
            if cmds.objExists(globalScaleCtrl + '.DefaultScale'): cmds.setAttr(globalScaleCtrl + '.DefaultScale', 0, lock=True)
        except:
            pass

    # Set dynamic control's start frame attributes value to 100000.
    if cmds.objExists('dyn_ctr_crv'):
        cmds.select('dyn_ctr_crv')
        dynCtrl = cmds.ls(sl=True)[0]
        udAttrs = cmds.listAttr(dynCtrl, ud=True)
        for attr in udAttrs:
            if 'startFrame' in attr or 'StartFrame' in attr:
                cmds.setAttr('%s.%s' % (dynCtrl, attr), 100000)

    if cmds.objExists('Sets'):
        # Trun on control curves.
        mel.eval('source "AdvancedSkeleton/asBody.mel";asBody;')
        mel.eval('asHideMotionSystem 0;')

    mel.eval('deleteUnusedCommon("animCurve", 0, uiRes("m_cleanUpScene.kDeletingUnusedAnimationCurves2"));')


def delSets(*args):
    # Delete quick selection sets.
    outlinerSets = getOutlinerSets()
    keepSets = ['AllSet', 'ControlSet', 'DeformSet', 'Sets', 'set', 'cache_set', 'TurtleDefaultBakeLayer',
                'defaultLightSet', 'defaultObjectSet']
    for item in outlinerSets:
        if not item in keepSets:
            cmds.delete(item)


def setFilterScript(name):
    # We first test for plug-in object sets.
    try:
        apiNodeType = cmds.nodeType(name, api=True)
    except RuntimeError:
        return False

    if apiNodeType == "kPluginObjectSet":
        return True

    # We do not need to test is the object is a set, since that test
    # has already been done by the outliner
    try:
        nodeType = cmds.nodeType(name)
    except RuntimeError:
        return False

    # We do not want any rendering sets
    if nodeType == "shadingEngine":
        return False

    # if the object is not a set, return false
    if not (nodeType == "objectSet" or
                    nodeType == "textureBakeSet" or
                    nodeType == "vertexBakeSet" or
                    nodeType == "character"):
        return False

    # We also do not want any sets with restrictions
    restrictionAttrs = ["verticesOnlySet", "edgesOnlySet", "facetsOnlySet", "editPointsOnlySet", "renderableOnlySet"]
    if any(cmds.getAttr("{0}.{1}".format(name, attr)) for attr in restrictionAttrs):
        return False

    # Do not show layers
    if cmds.getAttr("{0}.isLayer".format(name)):
        return False

    # Do not show bookmarks
    annotation = cmds.getAttr("{0}.annotation".format(name))
    if annotation == "bookmarkAnimCurves":
        return False

    # Whew ... we can finally show it
    return True


def getOutlinerSets():
    return [name for name in cmds.ls(sets=True) if setFilterScript(name)]


def cleanUpMdl(*args):
    """Cleanup to publish render model"""

    answer = cmds.confirmDialog(title='Clean Up Render Model', message='Are you sure?\nRig will be deleted.',
                                button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
    if answer == "No":
        return

    answer = cmds.confirmDialog(title='Clean Up Render Model', message='Keep model to rig state',
                                button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
    if answer == "No":
        # All deformer's envelope of lod03 set to 0.
        lod03GeoLs = cmds.ls('lod03_GRP', dag = True)
        lod03GeoLs = [x for x in lod03GeoLs if not 'Shape' in x]
        for lod03Geo in lod03GeoLs:
            tak_lib.setAllDefEnvlope(lod03Geo, 0)

    defaultScaleCtrl = cmds.ls('*.DefaultScale')
    if defaultScaleCtrl:
        cmds.setAttr(defaultScaleCtrl[0], lock=False)
        cmds.setAttr(defaultScaleCtrl[0], 1)

    if cmds.ls('*.lodVis'):
        cmds.setAttr(cmds.ls('*.lodVis')[0], 2)
    if cmds.ls('*.geometryVis'):
        cmds.setAttr(cmds.ls('*.geometryVis')[0], 0)

    # Set Main control attributes.
    if cmds.objExists('Main.smoothLevel'):
        cmds.setAttr('Main.smoothLevel', 2)

    # Clean up render model.
    cmds.select('lod03_GRP', hi=True, r=True)
    tak_cleanUpModel.allInOne()

    # Delete rig and 'geo_layer' that display layer.
    rootChldLs = cmds.listRelatives('root', c=True)
    for chld in rootChldLs:
        if not chld == 'geometry':
            cmds.delete(chld)
    if cmds.objExists('geo_layer'):
        cmds.delete('geo_layer')

    # Delete sets using in rig.
    if cmds.objExists('Sets'):
        cmds.delete('Sets')
    if cmds.objExists('AllSet'):
        cmds.delete('AllSet')
    if cmds.objExists('renMdlCnst_grp'):
        cmds.delete('renMdlCnst_grp')

    # Clean up root, geometry group.
    cmds.select('root', 'geometry', r=True)
    tak_cleanUpModel.cleanChBox()

    # Set smoothDrawType and smooth preview and smooth level.
    lod03ShpLs = cmds.ls('lod03_GRP', dag=True, g=True)
    for shp in lod03ShpLs:
        shpPrnt = cmds.listRelatives(shp, p=True)
        cmds.select(shpPrnt, r=True)
        mel.eval('setDisplaySmoothness 3;')
        if cmds.nodeType(shp) == 'mesh':
            cmds.setAttr('%s.useGlobalSmoothDrawType' % shp, 0)
            cmds.setAttr('%s.smoothDrawType' % shp, 0)
            cmds.setAttr('%s.smoothLevel' % shp, 2)

    if cmds.objExists('wip_GRP'):
        cmds.delete('wip_GRP')

    cmds.select(cl=True)


def showJoints(*args):
    '''
    Show all joints in current scene.
    '''

    jntLs = cmds.ls(type='joint')

    for jnt in jntLs:
        cmds.setAttr('%s.drawStyle' % (jnt), 0)


def hideJoints(*args):
    '''
    Hide all joints in current scene.
    '''

    jntLs = cmds.ls(type='joint')
    for jnt in jntLs:
        cmds.setAttr('%s.drawStyle' % jnt, 2)


def delAllLayers(*args):
    cmds.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')
    disLayList = cmds.ls(type='displayLayer')
    renLayList = cmds.ls(type='renderLayer')
    aniLyrLs = cmds.ls(type='animLayer')

    for disLay in disLayList:
        if disLay in ['defaultLayer', 'geo_layer', 'jointLayer']:
            pass
        else:
            cmds.delete(disLay)

    for renLay in renLayList:
        if renLay != 'defaultRenderLayer':
            cmds.delete(renLay)

    for aniLyr in aniLyrLs:
        if aniLyr == 'BaseAnimation':
            cmds.delete(aniLyr)


def setLod01Lod02SmoothLevel(*args):
    cmds.select('lod01_GRP', 'lod02_GRP', hi=True, r=True)
    proxyGeoList = cmds.ls(sl=True, type='mesh')

    for proxyGeo in proxyGeoList:
        cmds.setAttr(proxyGeo + '.smoothLevel', 0)


def chkFaceAssignedMat(*args):
    cmds.select('lod03_GRP', hi=True, r=True)

    selObjLs = cmds.ls(sl=True)

    selGeoFaceMatLs = tak_cleanUpModel.faceAssignedMat(selObjLs)

    faceAssignedMatGeoLs = []

    for mat in selGeoFaceMatLs:
        cmds.hyperShade(objects=mat)
        matAssignGeoLs = cmds.ls(sl=True)
        faces = cmds.filterExpand(matAssignGeoLs, ex=False, sm=34)

        if faces:
            matAssignedFaceShapes = tak_cleanUpModel.getShapesFromFaces(faces)

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


def chkHierOldNewMdl(*args):
    # Check Hierarchy Difference Between Old Model and New Model #

    selLs = cmds.ls(sl=True)
    oldMdlLod03Grp = selLs[0]
    newMdlLod03Grp = selLs[1]

    oldMdlLs = [x for x in cmds.listRelatives(oldMdlLod03Grp, ad=True, fullPath=True) if 'Shape' not in x]
    newMdlLs = [x for x in cmds.listRelatives(newMdlLod03Grp, ad=True, fullPath=True) if 'Shape' not in x]

    difMdlLs = []
    for i in xrange(len(oldMdlLs)):
        print oldMdlLs[i], newMdlLs[i]
        oldMdlPartialName = oldMdlLs[i].rsplit(':', 1)[-1]
        newMdlPartialName = newMdlLs[i].rsplit(':', 1)[-1]

        if oldMdlPartialName != newMdlPartialName:
            difMdlLs.append(oldMdlLs[i])
            difMdlLs.append(newMdlLs[i])

    if difMdlLs:
        cmds.select(difMdlLs, r=True)
        cmds.warning('Selected objecs are have different name.')
    else:
        cmds.select(cl=True)


def chkTopoOldNewMdl(*args):
    # Check Topology Difference Between Old Model and New Model #

    selLs = cmds.ls(sl=True)
    oldMdlLod03Grp = selLs[0]
    newMdlLod03Grp = selLs[1]

    oldMdlLs = cmds.listRelatives(oldMdlLod03Grp, ad=True, fullPath=True, type='mesh')
    newMdlLs = cmds.listRelatives(newMdlLod03Grp, ad=True, fullPath=True, type='mesh')

    difMdlLs = []
    for i in xrange(len(oldMdlLs)):
        oldMdlNumVertex = cmds.polyEvaluate(oldMdlLs[i], vertex=True)
        newMdlNumVertex = cmds.polyEvaluate(newMdlLs[i], vertex=True)

        if oldMdlNumVertex != newMdlNumVertex:
            difMdlLs.append(oldMdlLs[i])
            difMdlLs.append(newMdlLs[i])

    if difMdlLs:
        cmds.select(difMdlLs, r=True)
        cmds.warning('Selected objecs are have different topology.')
    else:
        cmds.select(cl=True)


def rigGrpUI(*args):
    WIN = 'ripGrpWin'

    if cmds.window(WIN, exists=True):
        cmds.deleteUI(WIN)

    cmds.window(WIN, title='Make Rig Group', mxb=False, mnb=False)

    cmds.columnLayout(adj=True)
    cmds.textFieldGrp('rigNameTxtFld', label='Rig Name: ', columnWidth=[(1, 70), (2, 100)])
    cmds.button(label='Create \'rig_grp\'', c=partial(makeRigGrp, 'rig_grp'))
    cmds.button(label='Create \'bnd_jnt_grp\'', c=partial(makeRigGrp, 'bnd_jnt_grp'))
    cmds.button(label='Create \'ctrl_grp\'', c=partial(makeRigGrp, 'ctrl_grp'))
    cmds.button(label='Create \'system_grp\'', c=partial(makeRigGrp, 'system_grp'))
    cmds.button(label='Create \'doNotTouch_grp\'', c=partial(makeRigGrp, 'doNotTouch_grp'))
    cmds.button(label='Parent to the \'extra_ctrl_grp\'', c="cmds.parent(cmds.ls(sl = True)[0], 'extra_ctrl_grp')")

    # Default fill 'rigNameTxtFld'
    dfltRigName = cmds.ls(sl=True)[0].split('_', 1)[0]
    cmds.textFieldGrp('rigNameTxtFld', e=True, text=dfltRigName)

    cmds.window(WIN, e=True, w=50, h=50)
    cmds.showWindow(WIN)


def makeRigGrp(grpName, *args):
    rigName = cmds.textFieldGrp('rigNameTxtFld', q=True, text=True)

    if not rigName:
        cmds.error('Please specify rig name.')

    selLs = cmds.ls(sl=True)
    cmds.group(selLs, n=rigName + '_' + grpName)


def chkTrsfIdentity(*args):
    '''
    Check 'lod02_GRP, lod03_GRP's transform nodes freeze state.
    '''

    lod02Lod03Objs = cmds.ls('lod02_GRP', 'lod03_GRP', dag=True)
    identityMatrix = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]

    nonIdentityTrsfs = []
    for obj in lod02Lod03Objs:
        if cmds.nodeType(obj) == 'transform':
            objMatrix = cmds.xform(obj, q=True, matrix=True)
            objMatrix = [round(x, 1) for x in
                         objMatrix]  # Cleanup matrix values. Sometimes 1.0000000 or 3.12312412e-423 exists.
            if not objMatrix == identityMatrix:
                nonIdentityTrsfs.append(obj)

    if nonIdentityTrsfs:
        cmds.select(nonIdentityTrsfs, r=True)
        cmds.error('Selected transform nodes are not freezed.')
    else:
        print 'All transform nodes are freezed.'


def addSmoothCtrl(*args):
    ctrl = cmds.ls(sl=True)[0]
    meshGrp = 'lod03_GRP'
    trt.lib.component.addSmoothControl(ctrl, meshGrp)