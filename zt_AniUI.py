# -*- coding: utf-8 -*-
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtUiTools import *
import shiboken2
import ztool_ToolsUI as zToolUI
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin  
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import os
from collections import OrderedDict


shelfPath = '%s/shelves' % os.path.dirname(__file__)

def maya_main_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()        
    
    mWindow= shiboken2.wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
            
    return mWindow 
curser = QCursor()
class aniToolsUI(MayaQWidgetDockableMixin,QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent=None) 
         
        self.setObjectName("zt_AniTools")        
        self.setMinimumSize(500,120)
        self.setMaximumSize(500,120)        
        self.move(curser.pos())
        self.setForm()

    def setForm(self):
        
        mainLayout = QVBoxLayout()        
        moveKeysLayout = QHBoxLayout()
        overLapLayout  = QHBoxLayout()
        labelLayout = QHBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.addLayout(labelLayout)
        mainLayout.addLayout(moveKeysLayout)
        mainLayout.addLayout(overLapLayout)
        
        label = QLabel('Move Keys:')
        self.valueLine = QLineEdit()
        forwardBtn   = QPushButton()
        icon = QApplication.style().standardIcon(getattr(QStyle, 'SP_MediaSeekForward'))  
        forwardBtn.setIcon(icon)
        self.startPosCheckBox = QCheckBox('To Frame')
        self.moveRadioBtn     = QRadioButton('Move')
        self.moveRadioBtn.setChecked(True)
        self.overLapRadioBtn  = QRadioButton('OverLap')

        labelLayout.addWidget(label)
        
        moveKeysLayout.addWidget(self.valueLine)
        moveKeysLayout.addWidget(forwardBtn)
        moveKeysLayout.addWidget(self.startPosCheckBox)
        moveKeysLayout.addWidget(self.moveRadioBtn)
        moveKeysLayout.addWidget(self.overLapRadioBtn)

        self.startPosCheckBox.stateChanged.connect(self.startPosCheckBoxState)
        forwardBtn.clicked.connect(self.moveKeys)

    def moveKeys(self):
        try:
            value = int(self.valueLine.text())
        except ValueError:
            print("Nope~!")
            return

        if self.startPosCheckBox.checkState() == Qt.Checked:
            moveKeyFrame(value,toFrame=True)
        else:
            if self.moveRadioBtn.isChecked():
                moveKeyFrame(value,move=True)
            else:
                cmds.undoInfo(openChunk=True)
                moveKeyFrame(value,overLap=True)  
                cmds.undoInfo(closeChunk=True)
    
    def startPosCheckBoxState(self):
        if self.startPosCheckBox.checkState() == Qt.Checked:
            self.overLapRadioBtn.setEnabled(False)
            self.moveRadioBtn.setEnabled(False)
        else:
            self.overLapRadioBtn.setEnabled(True)
            self.moveRadioBtn.setEnabled(True)

def breakCycle():
    currentTime=cmds.currentTime(q=True)    
    animInfo = {}
    animCurves = cmds.keyframe(n=True,sl=True,q=True)
    for animCurve in animCurves:
        frames = cmds.keyframe(animCurve,q=True)
        values = cmds.keyframe(animCurve,q=True,vc=True)
        animCurveDic = OrderedDict()
        for frame,value in zip(frames,values):
            animCurveDic.update({frame:value})        
        animInfo.update({animCurve:animCurveDic})
    

def moveKeyFrame(frame=0,toFrame=False,move=False,overLap=False):
    if toFrame:
        minFrame = min(cmds.keyframe(sl=True,q=True))
        moveValue = frame - minFrame
        cmds.keyframe(e=True,tc=moveValue,iub=True,r=True,o='over')

    if move:
        cmds.keyframe(e=True,tc=frame,iub=True,r=True,o='over')
    
    if overLap:
        n=0
        for obj in cmds.ls(sl=True):
            cmds.keyframe(obj,e=True,tc=n,iub=True,r=True,o='over')
            n+=frame

def main():
    title = 'ZT_AniTools'
    if cmds.window(title, exists =True):
        cmds.deleteUI(title, wnd =True)
    win = aniToolsUI('Toolbox')
    win.setObjectName(title)
    win.setWindowTitle(title)
    win.show()
    

