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
    toggle = False
    playBlastInfo = {}
    def __init__(self,parent=None):
        QWidget.__init__(self,parent=None)          
               
        self.setMinimumSize(500,350)
        self.setMaximumSize(500,350)        
        self.move(curser.pos())
        self.setForm()
        self.setLocalList()
        self.setFocusPolicy(Qt.NoFocus)
        
    def setForm(self):
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)        
        tabWidget  = QTabWidget()
        mainLayout.addWidget(tabWidget)
        toolWidget = QWidget()        
        tabWidget.addTab(toolWidget,'Tools') 

        #Tools UI
        toolLayout = QVBoxLayout()
        alignLayout = QVBoxLayout()
        alignKeyLayout = QHBoxLayout()    
        moveKeysLayout = QHBoxLayout()
        overLapLayout  = QHBoxLayout()
        labelLayout = QVBoxLayout() 
        setCameraLayout = QHBoxLayout()       
        toolWidget.setLayout(toolLayout)
        toolLayout.addLayout(labelLayout)
        toolLayout.addLayout(moveKeysLayout)
        toolLayout.addLayout(overLapLayout)   
        topSpacerItem = QSpacerItem(20, 300, QSizePolicy.Minimum,QSizePolicy.Expanding)  

        ###Align Widgets###
        alignLabel= QLabel('Align Keys:')
        alignLeftBtn = QPushButton()
        icon = QApplication.style().standardIcon(getattr(QStyle, 'SP_MediaSkipBackward')) 
        alignLeftBtn.setIcon(icon)
        alignCenterBtn = QPushButton()
        icon = QApplication.style().standardIcon(getattr(QStyle, 'SP_MediaPause')) 
        alignCenterBtn.setIcon(icon)
        alignRightBtn = QPushButton() 
        icon = QApplication.style().standardIcon(getattr(QStyle, 'SP_MediaSkipForward'))        
        alignRightBtn.setIcon(icon)
        alignSpacerItem = QSpacerItem(500, 40, QSizePolicy.Minimum,QSizePolicy.Expanding)  
        ###Move key Widgets###
        moveKeyLabel = QLabel('Move Keys:')
        self.valueLine = QLineEdit()
        forwardBtn   = QPushButton()
        icon = QApplication.style().standardIcon(getattr(QStyle, 'SP_MediaSeekForward'))  
        forwardBtn.setIcon(icon)
        self.startPosCheckBox = QCheckBox('To Frame')
        self.moveRadioBtn     = QRadioButton('Move')
        self.moveRadioBtn.setChecked(True)
        self.overLapRadioBtn  = QRadioButton('OverLap')
        breakAnimCycleBtn = QPushButton('<==Break Cycle==>')
        self.setCameraLabel = QLabel('cam:')
        if self.playBlastInfo:
            self.setCameraLabel.setText(self.playBlastInfo['cam'])
        setCameraBtn   = QPushButton('setCamera')
        setCameraBtn.setIcon(QIcon(':CameraDown.png'))
        playBlastBtn     = QPushButton('<==PlayBlast With QuickTime==>')


        #### Layout add widgets ###
        alignKeyLayout.addWidget(alignLeftBtn)
        alignKeyLayout.addWidget(alignCenterBtn)
        alignKeyLayout.addWidget(alignRightBtn)
        alignKeyLayout.addSpacerItem(alignSpacerItem) 
        alignLayout.addWidget(alignLabel)
        alignLayout.addLayout(alignKeyLayout)
        labelLayout.addSpacerItem(topSpacerItem)
        
        labelLayout.addLayout(alignLayout)
        labelLayout.addWidget(moveKeyLabel)        
        moveKeysLayout.addWidget(self.valueLine)
        moveKeysLayout.addWidget(forwardBtn)
        moveKeysLayout.addWidget(self.startPosCheckBox)
        moveKeysLayout.addWidget(self.moveRadioBtn)
        moveKeysLayout.addWidget(self.overLapRadioBtn)
        moveKeysLayout.addWidget(breakAnimCycleBtn)        

        setCameraLayout.addWidget(self.setCameraLabel)
        setCameraLayout.addWidget(setCameraBtn)
        setCameraLayout.addWidget(playBlastBtn)

        mainLayout.addLayout(setCameraLayout)

        alignLeftBtn.clicked.connect(
            lambda:(
            cmds.undoInfo(openChunk=True),
            alignKeyframe(),
            cmds.undoInfo(closeChunk=True)
        ))

        alignCenterBtn.clicked.connect(
            lambda:(
            cmds.undoInfo(openChunk=True),
            alignKeyframe(current=True),
            cmds.undoInfo(closeChunk=True)
        ))

        alignRightBtn.clicked.connect(
            lambda:(
            cmds.undoInfo(openChunk=True),
            alignKeyframe(right=True),
            cmds.undoInfo(closeChunk=True)
        ))

        self.startPosCheckBox.stateChanged.connect(self.startPosCheckBoxState)
        forwardBtn.clicked.connect(self.moveKeys)
        breakAnimCycleBtn.clicked.connect(lambda:(
                                                    cmds.undoInfo(openChunk=True),
                                                    breakAnimCycle(),
                                                    cmds.undoInfo(closeChunk=True)
                                                    ))
        
        setCameraBtn.clicked.connect(self.setPlayblastCam)                
        playBlastBtn.clicked.connect(self.playBlast)

        #Local UI
        localWidget = QWidget()
        tabWidget.addTab(localWidget,'Local')
        localLayout = QVBoxLayout()
        localWidget.setLayout(localLayout)

        urlLayout = QHBoxLayout()
        urlLabel = QLabel()        
        icon = QIcon(self.style().standardIcon(getattr(QStyle, 'SP_DirLinkIcon')))
        pixmap = icon.pixmap(80,80)        
        urlLabel.setPixmap(pixmap)
        self.urlLineEdit = QLineEdit()
        self.urlLineEdit.setReadOnly(True)
        explanBtn = QPushButton()
        explanBtn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_TitleBarUnshadeButton')))
        
        urlLayout.addWidget(urlLabel)
        urlLayout.addWidget(self.urlLineEdit)
        urlLayout.addWidget(explanBtn)

        localLayout.addLayout(urlLayout)   
        self.dirTreeView = dirView()
        self.dirTreeView.setSortingEnabled(True)       
        localLayout.addWidget(self.dirTreeView)

        explanBtn.clicked.connect(self.setToggle)
    def setPlayblastCam(self):
        try:
            panel = cmds.getPanel(wf=True)        
            cam = cmds.modelEditor(panel,cam=True,q=True)
            self.playBlastInfo['panel'] = panel
            self.playBlastInfo['cam']  = cam

            self.setCameraLabel.setText('cam:%s' % cam)
        except RuntimeError:
            print('Select viewport 1st.')
            cmds.warning('Camera was not set')
        
    def playBlast(self):
        fileName = cmds.file(sn=True,q=True)
        panel = cmds.getPanel(wf=True)  
        if fileName ==u'':
            print('File may not saved yet')            
            return
        if  self.playBlastInfo:
            panel = self.playBlastInfo['panel']
        
        movFile = self.setMovFileName(fileName)
        
        widthHeight = [cmds.getAttr('defaultResolution.%s' % i) for i in ["width","height"]]
        timeRange = mel.eval('timeControl -q -ra $gPlayBackSlider;')
        timeControl = mel.eval('$tmpVar = $gPlayBackSlider')
        sound = cmds.timeControl(timeControl,q=True,sound=True)
        startFrame = cmds.playbackOptions(q=True,min=True)
        endFrame   = cmds.playbackOptions(q=True,max=True)
        if timeRange[1] - timeRange[0] >1:
            startFrame = timeRange[0]
            endFrame   = timeRange[1]
            
        try:
            
            cmds.playblast(epn=panel,startTime=startFrame,endTime=endFrame,sound=sound,format='qt',filename=movFile, forceOverwrite=True,clearCache=True,viewer=True,offScreen=True,percent=100,compression="H.264", quality=100, widthHeight=widthHeight)
        except Exception as e:
            
            print("Install quicktime first.")
            
    def setMovFileName(self,sceneFileName):
        movFile = ''        
        dirName = os.path.dirname(sceneFileName)
        allBaseName = [
            '%s/%s' % (dirName,i.split('.mov')[0]) for i in os.listdir(dirName) if all([
            '.mov' in os.path.splitext(i)[1],
            os.path.splitext(os.path.basename(sceneFileName))[0] in i,
            i.split("_")[-1].startswith('P')
            ])
            ]
        
        if not allBaseName:
            movFile = '%s_P01.mov' % os.path.splitext(sceneFileName)[0]
            print(movFile)
            return movFile

        lastBaseName = sorted(allBaseName)[-1]
        nextVer = int(lastBaseName.split('_P')[-1]) + 1
        movFile = '%s_P%s.mov' % (lastBaseName[:-4],str(nextVer).zfill(2))
        print(movFile)
        
        return movFile            

    def setToggle(self):
        if self.toggle==False:
            self.hideColumns()
            self.toggle=True
        else:
            self.showColumns()
            self.toggle=False

    def setLocalList(self):
        fileName = cmds.file(sn=True,q=True)
        path = os.path.dirname(fileName)

        if not os.path.isdir(path):
            self.dirTreeView.setModel(None)
            self.urlLineEdit.setText('File may not saved yet.')
            return 
        self.dirTreeView.setPath(path)
        self.dirTreeView.setRootIndex(self.dirTreeView.model.index(path))
        
        self.urlLineEdit.setText(path)
        
    def hideColumns(self):
        self.dirTreeView.hideColumn(1)
        self.dirTreeView.hideColumn(2)
        self.dirTreeView.hideColumn(3)
        self.dirTreeView.hideColumn(4)
    def showColumns(self):
        self.dirTreeView.showColumn(1)
        self.dirTreeView.showColumn(2)
        self.dirTreeView.showColumn(3)
        self.dirTreeView.showColumn(4)
        self.dirTreeView.resizeColumnToContents(0)

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
        #jobNum = cmds.scriptJob( event = ["NewSceneOpened", self.refreshAll ], parent='ZT_AniTools')
    def refreshAll(self):
        print('Local refreshed')
        self.playBlastInfo={}        
        self.setLocalList()  
    def startPosCheckBoxState(self):
        if self.startPosCheckBox.checkState() == Qt.Checked:
            self.overLapRadioBtn.setEnabled(False)
            self.moveRadioBtn.setEnabled(False)
        else:
            self.overLapRadioBtn.setEnabled(True)
            self.moveRadioBtn.setEnabled(True)

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
        dirAction.triggered.connect(self.openPath)

        menu.addAction(fileAction)
        menu.addAction(dirAction)
        menu.exec_(self.mapFromParent(event.globalPos()))
    @Slot(QModelIndex)
    def openFile(self,index):        
        fileName = self.model.filePath(index)
        os.startfile(fileName)
    
    def openPath(self):
        # fileName = self.model.filePath(index)
        # path = os.path.dirname(fileName)
        os.startfile(self.path)
        
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

def alignKeyframe(right=False,current=False):
    animCurves = pm.keyframe(name=True,q=True)
    times  = pm.keyframe(tc=True,q=True)
    if not any([animCurves,times]):
        print('Select keys first...')
        return
    dic = {}
    for animCurve,t in zip(animCurves,times):
        dic[animCurve] = t
    minTime = min(dic.values())
    maxTime = max(dic.values())
    currentTime = cmds.currentTime(q=True)

    for anim,t in dic.items():
        tc = (t-minTime)*-1
        if right:
            tc = (t-maxTime)*-1
        if current:
            tc = (currentTime - t)
        cmds.keyframe(anim,e=True, iub=True,r=True, o='over',tc=tc,t=(t,t))


def main():
    title = 'ZT_AniTools'
    if cmds.window('ZT_AniTools', exists =True):
        cmds.deleteUI('ZT_AniTools', wnd =True)
    
    win = aniToolsUI()
    win.setObjectName(title)
    win.setWindowTitle(title)    
    win.startScriptJob()
    win.show()
    

