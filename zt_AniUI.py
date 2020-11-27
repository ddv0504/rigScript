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

currentDir = os.path.dirname(__file__)
tempDir = currentDir + '/temp'
shelfPath = '%s/shelves' % os.path.dirname(__file__)

def maya_main_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()        
    
    mWindow= shiboken2.wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
            
    return mWindow 
curser = QCursor()
class aniToolsUI(MayaQWidgetDockableMixin,QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent=None)          
               
        self.setMinimumSize(500,200)
        self.setMaximumSize(500,200)        
        self.move(curser.pos())
        self.setForm()
        self.setLocalList()
        
    def setForm(self):
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)        
        tabWidget  = QTabWidget()
        mainLayout.addWidget(tabWidget)
        toolWidget = QWidget()        
        tabWidget.addTab(toolWidget,'Tools') 

        #Tools UI
        toolLayout = QVBoxLayout()      
        moveKeysLayout = QHBoxLayout()
        overLapLayout  = QHBoxLayout()
        labelLayout = QHBoxLayout()        
        toolWidget.setLayout(toolLayout)
        toolLayout.addLayout(labelLayout)
        toolLayout.addLayout(moveKeysLayout)
        toolLayout.addLayout(overLapLayout)        
        label = QLabel('Move Keys:')
        self.valueLine = QLineEdit()
        forwardBtn   = QPushButton()
        icon = QApplication.style().standardIcon(getattr(QStyle, 'SP_MediaSeekForward'))  
        forwardBtn.setIcon(icon)
        self.startPosCheckBox = QCheckBox('To Frame')
        self.moveRadioBtn     = QRadioButton('Move')
        self.moveRadioBtn.setChecked(True)
        self.overLapRadioBtn  = QRadioButton('OverLap')
        breakAnimCycleBtn = QPushButton('<==Break Cycle==>')

        labelLayout.addWidget(label)
        
        moveKeysLayout.addWidget(self.valueLine)
        moveKeysLayout.addWidget(forwardBtn)
        moveKeysLayout.addWidget(self.startPosCheckBox)
        moveKeysLayout.addWidget(self.moveRadioBtn)
        moveKeysLayout.addWidget(self.overLapRadioBtn)
        moveKeysLayout.addWidget(breakAnimCycleBtn)

        self.startPosCheckBox.stateChanged.connect(self.startPosCheckBoxState)
        forwardBtn.clicked.connect(self.moveKeys)
        breakAnimCycleBtn.clicked.connect(lambda:(
                                                    cmds.undoInfo(openChunk=True),
                                                    breakAnimCycle(),
                                                    cmds.undoInfo(closeChunk=True)
                                                    ))
        
        #Local UI
        localWidget = QWidget()
        tabWidget.addTab(localWidget,'Local')
        localLayout = QVBoxLayout()
        localWidget.setLayout(localLayout)
        self.dirTreeView = dirView()
        #self.dirTreeView.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.dirTreeView.setSortingEnabled(True)
        
       
        localLayout.addWidget(self.dirTreeView)
        
        #self.dirTreeView.doubleClicked.connect(self.modelIndexClicked)
        
    def setLocalList(self):
        fileName = cmds.file(sn=True,q=True)
        path = os.path.dirname(fileName) 
        
        # self.model = QStandardItemModel()
        # self.model.setHorizontalHeaderLabels(['Name'])
        
        if not os.path.isdir(path):
            self.dirTreeView.setModel(None)
            return
        
        self.dirTreeView.setPath(path)
        self.dirTreeView.setRootIndex(self.dirTreeView.model.index(path))
        # for i,f in enumerate(os.listdir(path)):
        #     item = localItem(f)
        #     item.setEditable(False)
        #     self.model.setItem(i,item)
        #     fullName = os.path.join(path,f)
        #     item.setFileName(fullName)
        #     item.setFileIcon()
        #     item.setData({'fileName':fullName})
            
            
        #self.dirTreeView.setRootIndex(self.dirTreeView.model.index(tempDir))
        #self.dirTreeView.setModel(self.model) 

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
    
    def startScriptJob(self):
        jobNum = cmds.scriptJob( event = ["SceneOpened", self.refreshAll ], parent='ZT_AniTools')
        jobNum = cmds.scriptJob( event = ["SceneSaved", self.refreshAll ], parent='ZT_AniTools')
    def refreshAll(self):
        print('refreshed')        
        self.setLocalList()  
    def startPosCheckBoxState(self):
        if self.startPosCheckBox.checkState() == Qt.Checked:
            self.overLapRadioBtn.setEnabled(False)
            self.moveRadioBtn.setEnabled(False)
        else:
            self.overLapRadioBtn.setEnabled(True)
            self.moveRadioBtn.setEnabled(True)
    # @Slot(QModelIndex)
    # def modelIndexClicked(self,QModelIndex):
    #     data = self.model.itemData(QModelIndex)
    #     for value in data.values():
    #         if type(value) == dict and value.keys()[0] == 'fileName':
    #             os.startfile(value.values()[0])

def breakAnimCycle():
    currentTime=cmds.currentTime(q=True)      
    animCurves = cmds.keyframe(n=True,sl=True,q=True)
    if not animCurves:
        print('Select animation curves first!')
        return
    for animCurve in animCurves:
        frames = cmds.keyframe(animCurve,q=True)        
        maxFrame = max(frames)
        minFrame = min(frames)
        frameRange = maxFrame-minFrame
        cmds.copyKey(animCurve)         
        if currentTime > maxFrame: 
            while maxFrame < currentTime:           
                cmds.pasteKey(animCurve,copies= 1)        
                maxFrame = max(cmds.keyframe(animCurve,q=True))
            cmds.setKeyframe(animCurve,insert=True,t=currentTime)
            cmds.cutKey(animCurve,t=(currentTime+1,currentTime+frameRange))
            
        if currentTime < minFrame:             
            n=0
            while minFrame > currentTime:
                n += 1
                pastFrame = maxFrame-frameRange*n
                cmds.pasteKey(animCurve,copies=1,timeOffset = 0,option='merge',connect=0,floatOffset=0,valueOffset=0,t=(pastFrame,pastFrame))
                minFrame = min(cmds.keyframe(animCurve,q=True))                
                minFrame=min(cmds.keyframe(animCurve,q=True))
            cmds.setKeyframe(animCurve,insert=True,t=currentTime)
            cmds.cutKey(animCurve,t=(currentTime-frameRange,currentTime-1))

class dirView(QTreeView):
    def __init__(self):
        super(dirView,self).__init__()
        self.path = r''
        self.model = QFileSystemModel()
        self.doubleClicked.connect(self.openFile)
    def contextMenuEvent(self,event):
        menu = QMenu(self)

        fileAction = QAction('Open File',self)
        dirAction = QAction('Go to Path',self)

        fileAction.triggered.connect(lambda:self.openFile(self.selectedIndexes()[0]))
        dirAction.triggered.connect(lambda:self.openPath(self.selectedIndexes()[0]))

        menu.addAction(fileAction)
        menu.addAction(dirAction)
        menu.exec_(self.mapToParent(event.globalPos()))
    @Slot(QModelIndex)
    def openFile(self,index):
        #source_index = self.proxy_model.mapToSource(index)
        fileName = self.model.filePath(index)
        #fileName = self.model.fileName(path)
        os.startfile(fileName)
    
    def openPath(self,index):
        fileName = self.model.filePath(index)
        path = os.path.dirname(fileName)
        os.startfile(path)
        #os.start()
    def setPath(self,path):
        
        self.path = path
        self.model.setRootPath(self.path)
        self.setModel(self.model)
        

class localItem(QStandardItem):
    def __init__(self,text):
        super(localItem,self).__init__()
        self.setText(text)
        self.fileName = ''       

    def setFileName(self,fileName):
        self.fileName = fileName

    def setFileIcon(self):
        if self.fileName:
            fullName = os.path.join(self.fileName)
            fileInfo = QFileInfo(fullName)
            iconProvider = QFileIconProvider()
            icon = iconProvider.icon(fileInfo)
            self.setIcon(icon)
        pass

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
    win = aniToolsUI()
    win.setObjectName(title)
    win.setWindowTitle(title)    
    win.startScriptJob()
    win.show()
    

