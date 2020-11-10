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
        
    try:
        mWindow= shiboken.wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
    except:
        mWindow= shiboken2.wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
            
    return mWindow     
    
class rigWidget(MayaQWidgetDockableMixin, QMainWindow):

    def __init__(self,parent=None):
        QMainWindow.__init__(self,parent=None)
        
        self.resize(480,820)
        self.mainUI()
    def mainUI(self):
        self.mainWidget = QWidget(self)
        mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(mainLayout)        
        disGrpBox = QGroupBox(self)
        mainLayout.addWidget(disGrpBox)
        disGrpBox.setTitle('EDITOR')
        disHLayout = QHBoxLayout()
        disGrpBox.setLayout(disHLayout) 
                  
        jntGrpBox = QGroupBox(self)
        mainLayout.addWidget(jntGrpBox)
        jntGrpBox.setTitle('JOINT')
        
        
        self.setCentralWidget(self.mainWidget)

class listItem(QStandardItem):
    def __init__(self,name=None,image=None,cmd=None):
        QStandardItem.__init__(self)
        self.name=name
        self.cmd=cmd
        self.setText(self.name)
        
        self.setIcon(QIcon(':{0}'.format(image)))
        self.setToolTip(image)
        
    
    def excute(self):        
        if self.cmd:
            try:
                mel.eval(self.cmd)                
            except Exception as e:
                
                print(e)     
               
              
def main():
        
    title = 'ZT_RIGTools'
    if cmds.window(title, exists =True):
        cmds.deleteUI(title, wnd =True)
    win = rigWidget(maya_main_window())
    win.setObjectName(title)
    win.setWindowTitle(title)
    win.show() 