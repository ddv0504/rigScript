# -*- coding:utf-8 -*

import os, sys
import os
from maya.api import OpenMaya as om2
import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mel
import maya.utils as utils
from imp import reload
from ztMisc import ztSceneCleanup
#from setuptools import setup, find_namespace_packages
path = os.path.dirname(__file__).replace('\\','/')
mayaVersion = cmds.about(v=True)

# 환경변수 setup.
# print '//////////////////////////////////////////////////////////'
envKeyLst = ['MAYA_SCRIPT_PATH','XBMLANGPATH','PYTHONPATH','MAYA_PLUGIN_PATH','MAYA_MODULE_PATH']

def addEnvPath(envKey,path):
    keyPath = os.getenv(envKey)    
    if keyPath:
        pathLst = keyPath.split(';')
    else:
        pathLst = []
    pathLst.append(path)
    os.environ[envKey] = ';'.join(pathLst)
    print('{0} ---->{1}'.format(envKey,path))

# Main script path:
addEnvPath('MAYA_SCRIPT_PATH','%s/melScripts' % path)
# AdvencedSkeleton5 script path:
addEnvPath('MAYA_SCRIPT_PATH','%s/advenced_Skeleton5' % path)
addEnvPath('MAYA_SCRIPT_PATH','%s/advenced_Skeleton5/AdvancedSkeleton5Files/Selector' % path)
# QuadRemesher script path:
addEnvPath('MAYA_SCRIPT_PATH','%s/plugins/QuadRemesher/Contents/scripts' % path)
# ngSkinTools script path:
addEnvPath('MAYA_SCRIPT_PATH','%s/plugins/ngskintools2/Contents/scripts' % path)
# MayaBonusTools script path:
addEnvPath('MAYA_SCRIPT_PATH','%s/plugins/MayaBonusTools-2017-2020/Contents/scripts-%s'% (path,mayaVersion))
# brSmoothWeight script path:
addEnvPath('MAYA_SCRIPT_PATH','%s/plugins/brSmoothWeights/scripts' % path)
# brSmoothWeight script path:
addEnvPath('MAYA_SCRIPT_PATH','%s/plugins/weightDriver/scripts' % path)

# Icon path:
addEnvPath('XBMLANGPATH','%s/icons' % path)
addEnvPath('XBMLANGPATH','%s/advenced_Skeleton5/AdvancedSkeleton5Files/Selector/face' % path)
addEnvPath('XBMLANGPATH','%s/advenced_Skeleton5/AdvancedSkeleton5Files/Selector/biped' % path)

# PYTHONPATH main:
addEnvPath('PYTHONPATH',path)
# ngSkinTools python path:
addEnvPath('PYTHONPATH','%s/plugins/ngskintools2/Contents/scripts' % path)
# QuadRemesher python path:
addEnvPath('PYTHONPATH','%s/plugins/QuadRemesher/Contents/scripts' % path)
# MayaBonusTools python path:
addEnvPath('PYTHONPATH','%s/plugins/MayaBonusTools-2017-2020/Contents/python-%s'% (path,mayaVersion))


# ngSkinTools plugin path:
addEnvPath('MAYA_PLUG_IN_PATH','%s/plugins/ngskintools2/Contents/plug-ins/%s' % (path,mayaVersion))
# Quad Remesher plugin path:
addEnvPath('MAYA_PLUG_IN_PATH','%s/plugins/QuadRemesher/Contents/plug-ins' % path)
# MayaBonusTools plugin path:
addEnvPath('MAYA_PLUG_IN_PATH','%s/plugins/MayaBonusTools-2017-2020/Contents/plug-ins/win64-%s' % (path,mayaVersion))
# brSmoothWeight plugin path:
addEnvPath('MAYA_PLUG_IN_PATH','%s/plugins/brSmoothWeights/plug-ins/win64/%s' % (path,mayaVersion))
# RBF plugin path:
addEnvPath('MAYA_PLUG_IN_PATH','%s/plugins/weightDriver/plug-ins/win64/%s' % (path,mayaVersion))

# Module path:
addEnvPath('MAYA_MODULE_PATH','%s/module' % path)

# Python script path:
pythonPathLst = [path,
                '%s/plugins/ngskintools2/Contents/scripts' % path,
                '%s/plugins/QuadRemesher/Contents/scripts' % path,
                '%s/plugins/MayaBonusTools-2017-2020/Contents/python-%s'% (path,mayaVersion),
                '%s/ztRigUtils/cgmtools/mayaTools' % path,
                '%s/tools' % path
                ]
for path in pythonPathLst:
    if not path in sys.path:
        sys.path.append(path)
        print(path)
# remove commandPort error.
if cmds.optionVar( q='commandportOpenByDefault' ):
    cmds.optionVar( iv=('commandportOpenByDefault', 0) )


def addMenuItems():
    if not cmds.about(batch=True):
        # Auto startup brSmoothWeight
        mel.eval("source brSmoothWeightsCreateMenuItems; brSmoothWeightsAddMenuCommand;")
        # Startup MayaBonusTools
        mel.eval('source "bonusToolsMenu.mel";')
        mel.eval("bonusToolsMenu();")
        # Startup QuedRemesher
        mel.eval('source "QuadRemesher_load.mel";')
        # Auto startup ztool
        import zTool_v004
        reload(zTool_v004)
        zTool_v004.main()

pluginLst = [
    'ngSkinTools2',
    'QuadRemesherPlugIn',
    'brSmoothWeights',
    'weightDriver'
    ]

def loadPlugin():
    for plug in pluginLst:
        try:
            cmds.loadPlugin(plug,qt=True)
        except Exception as e:
            print(plug,e)

def loadMelScript():
    mel.eval('source "QuadRemesher_shelf.mel";')

utils.executeDeferred(loadMelScript)
utils.executeDeferred(addMenuItems)
utils.executeDeferred(loadPlugin)
# Before save cleanup unknown node and unknown plugins.
_id = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kBeforeSave, ztSceneCleanup.cleanUp )
print(_id)