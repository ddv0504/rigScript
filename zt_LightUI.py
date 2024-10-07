# -*- coding: utf-8 -*-
from __future__ import print_function
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtUiTools import *
import shiboken2
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import os

currentDir = os.path.dirname(__file__)
tempDir = currentDir + '/temp'
shelfPath = '%s/shelves' % os.path.dirname(__file__)

def maya_main_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()

    mWindow= shiboken2.wrapInstance(long(mayaMainWindowPtr), QMainWindow)

    return mWindow
curser = QCursor()
class LitTools(MayaQWidgetDockableMixin,QWidget):
    
    def __init__(self,parent=None):
        QWidget.__init__(self,parent=None)
        self.setMinimumSize(500,350)


def main():
    title = 'Zt_LitTools'
    if cmds.window('LitTools', exists =True):
        cmds.deleteUI('LitTools', wnd =True)

    win = LitTools()
    win.setObjectName(title)
    win.setWindowTitle(title)
    # win.startScriptJob()
    win.show()
