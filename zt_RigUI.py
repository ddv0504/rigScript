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
from ztRigUtils import ztRigUtil
import os

currentPath = os.path.dirname(__file__).replace('\\','/')
shelfPath = '%s/shelves' % currentPath

def maya_main_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        
    try:
        mWindow= shiboken2.wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
    except:
        mWindow= shiboken2.wrapInstance(int(mayaMainWindowPtr), QMainWindow) 
            
    return mWindow     
mainWindow = maya_main_window()    
class rigWindow(MayaQWidgetDockableMixin, QMainWindow):

    def __init__(self,parent=None):
        QMainWindow.__init__(self,parent=None)
    
        self.resize(480,820)
        self.mainUI()
        self.addMenu()
    def mainUI(self):
        self.mainWidget = QWidget(self)
        mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(mainLayout)            
        displayBox = QToolBox()        
        mainLayout.addWidget(displayBox)
        for f in [ '%s/%s.mel' % (shelfPath,i) for i in ['ztRigDisplay','ztRigEditModel','ztRigBuild','ztRigDeformation','ztRigExtraTools']]:
            name = os.path.splitext(os.path.basename(f))[0]
            shelf = mayaShelfWidget(name=name,path = f)
            displayBox.addItem(shelf,name)
        self.setCentralWidget(self.mainWidget)
    def addMenu(self):
        menubar = self.menuBar()
        fileMenu = QMenu('File',self)
        saveAct = QAction('Save',self)
        fileMenu.addAction(saveAct)
        menubar.addMenu(fileMenu)

        saveAct.triggered.connect(self.saveShelf)
    def saveShelf(self):
        for f in [ '%s/%s' % (shelfPath,i) for i in os.listdir(shelfPath)]:
            name = os.path.basename(os.path.splitext(f)[0])
            print(name,os.path.splitext(f)[0])
            cmds.saveShelf(name,os.path.splitext(f)[0])
            print('%s was Saved' % name)
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
class mayaShelfWidget(QWidget):
    def __init__(self,name,path='',parent=None):
        super(mayaShelfWidget,self).__init__()
        self.name = name
        self.path = path
        self.setObjectName = self.name
        self.vLayout = QVBoxLayout(self)
        self.widget = self.shelfWidget()
        self.widget.setParent(self)
        self.vLayout.addWidget(self.widget)
    def shelfWidget(self): 
        funcName = ''
        if self.path:
            with open( self.path,'r') as f:
                lines = f.readlines()
                
            for line in lines:
                if 'global proc' in line:
                    funcName = '%s()' % line.split(' ')[2]
            mel.eval('source"%s"'% self.path)  
            
        if cmds.shelfLayout(self.name,ex=True):
            cmds.deleteUI(self.name)                        
        shelfLayout = cmds.shelfLayout(self.name,parent=mainWindow.objectName())

        
        mel.eval(funcName)   
        ptr = omui.MQtUtil_findControl(shelfLayout)
        try:   
            return shiboken2.wrapInstance(long(ptr),QWidget)  
        except:
            return shiboken2.wrapInstance(int(ptr),QWidget)    
def main():
        
    title = 'ZT_RIGTools'
    if cmds.window(title, exists =True):
        cmds.deleteUI(title, wnd =True)
    win = rigWindow(maya_main_window())
    win.setObjectName(title)
    win.setWindowTitle(title)
    win.show() 