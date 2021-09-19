# -*- coding:utf-8 -*

import os, sys

import maya.cmds as cmds
import maya.mel as mel

path = os.path.dirname(__file__)
mayaVersion = cmds.about(v=True)


# 환경변수 setup.
# print '///////////////////////////////////////////////////////////'
envKeyLst = ['MAYA_SCRIPT_PATH','XBMLANGPATH','PYTHONPATH','MAYA_PLUGIN_PATH']

scriptPath = os.getenv('MAYA_SCRIPT_PATH')
scriptPathLst = scriptPath.split(';')
scriptPathLst.append('%s/melScripts' % path)
scriptPathLst.append('%s/advenced_Skeleton5' % path)
os.environ['MAYA_SCRIPT_PATH'] = ';'.join(scriptPathLst)
print('MAYA_SCRIPT_PATH ---->{0}/melScripts;{0}/advenced_Skeleton5'.format(path))

iconPath = os.getenv('XBMLANGPATH')
iconPathLst = iconPath.split(';')
iconPathLst.append('%s/icons' % path)
iconPathLst.append('%s/advenced_Skeleton5/AdvancedSkeleton5Files/icons' % path)
os.environ['XBMLANGPATH'] = ';'.join(iconPathLst)
print('XBMLANGPATH ---->{0}/icons;{0}/advenced_Skeleton5/AdvancedSkeleton5Files/icons'.format(path))

pythonPath = os.getenv('PYTHONPATH')
pythonPathLst = pythonPath.split(';')
pythonPathLst.append(path)
os.environ['PYTHONPATH'] = ';'.join(pythonPathLst)
print('PYTHONPATH ---->{0}'.format(path))

pluginPath = os.getenv('MAYA_PLUGIN_PATH')

if not path in sys.path:
    sys.path.append(path)



# remove commandPort error.
if cmds.optionVar( q='commandportOpenByDefault' ):
    cmds.optionVar( iv=('commandportOpenByDefault', 0) )


# Auto startup ztool
import zTool_v004
zTool_v004.main()