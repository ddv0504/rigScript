from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader
import shiboken2
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin  
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import os

shelfPath = '%s/shelves' % os.path.dirname(__file__)

def maya_main_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()        
    
    mWindow= shiboken2.wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
            
    return mWindow 
curser = QCursor()
class aniToolsUI(MayaQWidgetDockableMixin,QMainWindow):
    def __init__(self,parent=None):
        QMainWindow.__init__(self,parent=maya_main_window())  
        self.setObjectName("zt_AniTools")        
        self.setMinimumSize(500,120)
        self.setMaximumSize(500,120)        
        self.move(curser.pos())
        self.setForm()
    def setForm(self):
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)
        mainLayout = QVBoxLayout()
        moveKeysLayout = QHBoxLayout()
        overLapLayout  = QHBoxLayout()
        labelLayout = QHBoxLayout()
        self.mainWidget.setLayout(mainLayout)
        mainLayout.addLayout(labelLayout)
        mainLayout.addLayout(moveKeysLayout)
        mainLayout.addLayout(overLapLayout)
        
        label = QLabel('Move Keys:')
        backBtn   = QPushButton()
        icon = QApplication.style().standardIcon(getattr(QStyle, 'SP_MediaSeekBackward'))  
        backBtn.setIcon(icon)
        valueLine = QLineEdit()
        forwardBtn   = QPushButton()
        icon = QApplication.style().standardIcon(getattr(QStyle, 'SP_MediaSeekForward'))  
        forwardBtn.setIcon(icon)
        startPosCheckBox = QCheckBox('To Frame')
        moveRadioBtn     = QRadioButton('Move')
        moveRadioBtn.setChecked(True)
        overLapRadioBtn  = QRadioButton('OverLap')

        labelLayout.addWidget(label)
        moveKeysLayout.addWidget(backBtn)
        moveKeysLayout.addWidget(valueLine)
        moveKeysLayout.addWidget(forwardBtn)
        moveKeysLayout.addWidget(startPosCheckBox)
        moveKeysLayout.addWidget(moveRadioBtn)
        moveKeysLayout.addWidget(overLapRadioBtn)

def main():
    title = 'ZT_AniTools'
    if cmds.window(title, exists =True):
        cmds.deleteUI(title, wnd =True)
    win = aniToolsUI(maya_main_window())
    win.setObjectName(title)
    win.setWindowTitle(title)
    win.show()

