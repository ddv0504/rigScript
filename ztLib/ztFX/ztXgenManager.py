#-*- coding: utf-8 -*-
import os
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader
import shiboken2
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin  
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm
import sys
from . import ztXgenUtil
import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.XgExternalAPI as xge

#palette : collection
#description: description
#objects : 'SplinePrimitive', 'RandomGenerator', 'RendermanRenderer', 'GLRenderer'
#attrs = xg.allAttrs(palette, description, objects)

'''
example:

if xgg.Maya:
    
    #palette is collection, use palettes to get collections first.
    palettes = xg.palettes()
    for palette in palettes:
        

        #Use descriptions to get description of each collection
        descriptions = xg.descriptions(palette)
        for description in descriptions:
            
            objects = xg.objects(palette, description, True)

            #Get active objects,e.g. SplinePrimtives
            for object in objects:
                print('collection:' + palette)
                print("description:" + description)
                print " Object:" + object
                attrs = xg.allAttrs(palette, description, object)
                for attr in attrs:
                    print " Attribute:" + attr + ", Value:" + xg.getAttr(attr, palette, description, object)

Get attribute value:
xg.getAttr(attr, palette, description, object)                    
'''

def maya_main_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        
    try:
        mWindow= shiboken.wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
    except:
        mWindow= shiboken2.wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
            
    return mWindow

class xgenManager(MayaQWidgetDockableMixin, QWidget):
    
    def __init__(self,parent=None):
        QWidget.__init__(self,parent=None,objectName=None)
        self.resize(150,80)
        self.settings = QSettings('optionData','xgenMNG')
        self.mainUI()
        self.addCollections()
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        self.addDesCriptions()
    def mainUI(self):
        if self.settings.value('size'):
            self.resize(self.settings.value('size'))
        if self.settings.value('pos'):
            self.move(self.settings.value('pos'))

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        comboBoxLayout = QHBoxLayout()
        mainLayout.addLayout(comboBoxLayout)

        dsLabel = QLabel(self)
        dsLabel.setText('Collections:')
        self.collectionsComboBox = QComboBox(self)
        self.collectionsComboBox.setCurrentText('')
        self.refBtn = QPushButton(self)
        self.refBtn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_BrowserReload')))
        comboBoxSpacerItem = QSpacerItem(400,10,QSizePolicy.Expanding,QSizePolicy.Minimum)

        comboBoxLayout.addWidget(dsLabel)
        comboBoxLayout.addWidget(self.collectionsComboBox)
        comboBoxLayout.addWidget(self.refBtn)
        comboBoxLayout.addSpacerItem(comboBoxSpacerItem)        

        desLayout   = QVBoxLayout()
        desWidget = QWidget()
        filesWidget = QWidget()
        self.splitter = QSplitter()
        
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(desWidget)
        self.splitter.addWidget(filesWidget)

        mainLayout.addWidget(self.splitter)
        self.desTreeWidget = descriptionTreeWidget(self)
        if self.settings.value('treeWidgetSize'):
            self.desTreeWidget.resize(self.settings.value('treeWidgetSize'))
        self.desTreeWidget.setObjectName('xgenDesCriptions')
        self.desTreeWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.desTreeWidget.setHeaderLabels(['Descriptions:','Value:'])
        self.desTreeWidget.setStyleSheet("background-color: gray;font: 87 13pt \"Arial Black\";")
        self.desTreeWidget.setColumnWidth(0,300)

        renderLayout = QHBoxLayout()
        renderLabel = QLabel('Renderer:')
        self.renderComboBox = QComboBox()
        self.renderComboBox.addItems(['None','Arnold'])
        self.renderComboBox.setEnabled(False)
        renderComboBoxSpacerItem = QSpacerItem(400,10,QSizePolicy.Expanding,QSizePolicy.Minimum)

        renderLayout.addWidget(renderLabel)
        renderLayout.addWidget(self.renderComboBox)
        renderLayout.addSpacerItem(renderComboBoxSpacerItem)

        renderModeLayout = QHBoxLayout()
        renderModeLabel = QLabel('Render Mode:')
        self.renderModeComboBox = QComboBox()
        self.renderModeComboBox.addItems(['Live','Batch Render'])
        self.renderModeComboBox.setEnabled(False)
        renderModeComboBoxSpacerItem = QSpacerItem(400,10,QSizePolicy.Expanding,QSizePolicy.Minimum)

        renderModeLayout.addWidget(renderModeLabel)
        renderModeLayout.addWidget(self.renderModeComboBox)
        renderModeLayout.addSpacerItem(renderModeComboBoxSpacerItem)
        

        fileListLayout    = QVBoxLayout()
        self.fileListWidget = fileListWidget(self)
        if self.settings.value('fileListSize'):
            self.fileListWidget.resize(self.settings.value('fileListSize'))
        self.fileListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        btnLayout         = QHBoxLayout()
        self.addFileBtn  = QPushButton('Add')
        self.remFileBtn  = QPushButton('Remove')    
        self.updateBtn   = QPushButton('updateXgenUI')

        btnLayout.addWidget(self.addFileBtn)
        btnLayout.addWidget(self.remFileBtn)
        btnLayout.addWidget(self.updateBtn)

        fileListLayout.addWidget(self.fileListWidget)
        fileListLayout.addLayout(btnLayout)

        desWidget.setLayout(desLayout)
        desLayout.addWidget(self.desTreeWidget)
        desLayout.addLayout(renderLayout)
        desLayout.addLayout(renderModeLayout)
        filesWidget.setLayout(fileListLayout)


        self.splitter.splitterMoved.connect(self.saveSplliter)
        self.refBtn.clicked.connect(self.refreshDescriptionWidget)
        self.fileListWidget.doubleClicked.connect(self.printPath)
        self.addFileBtn.clicked.connect(self.addFiles)
        self.remFileBtn.clicked.connect(self.removeFile)
        self.updateBtn.clicked.connect(self.updateXgenUI)
        self.desTreeWidget.collapsed.connect(self.allCollapse)
        self.desTreeWidget.expanded.connect(self.allExpand)
        self.desTreeWidget.clicked.connect(self.selectDesItem)
        self.renderComboBox.currentIndexChanged.connect(self.rendererChange)
        self.renderModeComboBox.currentIndexChanged.connect(self.renderModeChange)

    def allCollapse(self):
        items = self.desTreeWidget.selectedItems()
        for item in items:
            self.desTreeWidget.collapseItem(item)

    def allExpand(self):
        items = self.desTreeWidget.selectedItems()
        for item in items:
            self.desTreeWidget.expandItem(item)

    def addCollections(self):        
        [self.collectionsComboBox.addItem(i) for i in xg.palettes()]
        
    def addFiles(self):
        fileNames = QFileDialog().getOpenFileNames()
        if fileNames:
            fileList = sorted(fileNames[0])
            for file in fileList:
                path = file
                name = os.path.splitext(os.path.split(file)[1])[0]
                item = fileListItem(path=path,name=name)
                
                try:
                    if not item in self.fileLIstItems():
                        self.fileListWidget.addItem(item)
                
                except Exception as e:
                    self.fileListWidget.addItem(item)
        self.refreshDescriptionWidget()

    def addDesCriptions(self):
        collection = self.collectionsComboBox.currentText()        
        descriptions = xg.descriptions(str(collection))
        for description in sorted(descriptions):
            treeItem = descriptionItem(name=description,palette=str(collection),parent=self.desTreeWidget)
            self.desTreeWidget.addTopLevelItem(treeItem)

        #self.rendererChange()
        
    def selectDesItem(self):

        if not self.desTreeWidget.selectedItems():
            self.renderComboBox.setEnabled(False)
            self.renderModeComboBox.setEnabled(False)
        else:
            self.renderComboBox.setEnabled(True)
            self.renderModeComboBox.setEnabled(True)
    def rendererChange(self):
        if self.renderComboBox.currentText() == 'None':
            self.renderModeComboBox.setEnabled(False)
            items = self.desTreeWidget.selectedItems()
            for item in items:
                xg.setAttr('renderer','None',str(self.collectionsComboBox.currentText()),str(item.name),'RendermanRenderer')

            #Get the description editor first.
            de = xgg.DescriptionEditor
            #Do a full UI refresh
            de.refresh("Full")
        else:
            self.renderModeComboBox.setEnabled(True)
            items = self.desTreeWidget.selectedItems()
            for item in items:
                xg.setAttr('renderer','Arnold Renderer',str(self.collectionsComboBox.currentText()),str(item.name),'RendermanRenderer')
            #Get the description editor first.
            de = xgg.DescriptionEditor
            #Do a full UI refresh
            de.refresh("Full")

    def renderModeChange(self):
        
        if self.renderModeComboBox.currentText() == 'Live':
            items = self.desTreeWidget.selectedItems()
            
            for item in items:
                xg.setAttr('custom__arnold_rendermode','0',str(self.collectionsComboBox.currentText()),str(item.name),'RendermanRenderer')
            #Get the description editor first.
            de = xgg.DescriptionEditor
            #Do a full UI refresh
            de.refresh("Full")
        else:
            
            items = self.desTreeWidget.selectedItems()
            for item in items:
                xg.setAttr('custom__arnold_rendermode','1',str(self.collectionsComboBox.currentText()),str(item.name),'RendermanRenderer')
            #Get the description editor first.
            de = xgg.DescriptionEditor
            #Do a full UI refresh
            de.refresh("Full")

    def fileLIstItems(self):
        if self.fileListWidget.count():
            items = [self.fileListWidget.item(i) for i in range(self.fileListWidget.count())]
            return items
        
    def printPath(self):
        items = self.fileListWidget.selectedItems()
        for item in items:
            print(item.path)

    def refreshDescriptionWidget(self):
        self.desTreeWidget.clear()
        self.addDesCriptions()

    def removeFile(self):
        indexes = self.fileListWidget.selectedIndexes()
        indexLst = sorted([index.row() for index in indexes],reverse=True)
        for i in indexLst:
            self.fileListWidget.takeItem(i)            

    def resizeEvent(self,event):
        self.settings.setValue('size',self.size())
    
    def saveSplliter(self):
        self.settings.setValue('treeWidgetSize',self.desTreeWidget.size())
        self.settings.setValue('fileListSize',self.fileListWidget.size())
        
    def moveEvent(self,event):
        self.settings.setValue('pos',self.pos())
    
    def updateXgenUI(self):
        for i in range(self.desTreeWidget.topLevelItemCount()):
            item = self.desTreeWidget.topLevelItem(i)
            cacheMode = 'False' if item.cacheMode.checkState(1) == Qt.Unchecked else 'True'
            liveMode  = 'False' if item.liveMode.checkState(1) == Qt.Unchecked else 'True'
            cacheFile = item.cacheFile.text(1)
            auxMode   = '0'     if item.auxMode.checkState(1) == Qt.Unchecked else '1' 
            auxPath   = item.auxPath.text(1)
            #print(cacheMode,liveMode,cacheFile)
            xg.setAttr('useCache',cacheMode,str(self.collectionsComboBox.currentText()),item.name,'SplinePrimitive')
            xg.setAttr('liveMode',liveMode,str(self.collectionsComboBox.currentText()),item.name,'SplinePrimitive')
            xg.setAttr('cacheFileName',str(cacheFile),str(self.collectionsComboBox.currentText()),item.name,'SplinePrimitive')
            xg.setAttr('custom__arnold_useAuxRenderPatch',auxMode,str(self.collectionsComboBox.currentText()),item.name,'RendermanRenderer')
            xg.setAttr('custom__arnold_auxRenderPatch',str(auxPath),str(self.collectionsComboBox.currentText()),item.name,'RendermanRenderer')
        #Get the description editor first.
        de = xgg.DescriptionEditor
        #Do a full UI refresh
        de.refresh("Full")

class descriptionTreeWidget(QTreeWidget):
    def __init__(self,parent=None):
        QTreeWidget.__init__(self,parent=None)
    
    def contextMenuEvent(self,event):
        
        contextMenu = QMenu(self)
        checkUseAnimationAct = QAction(u'Check Use Animation',self)
        checkLiveModeAct     = QAction(u'Check Live Mode',self)
        checkAuxRenderPatch  = QAction(u'Check Aux Render Patch',self)
        contextMenu.addAction(checkUseAnimationAct)
        contextMenu.addAction(checkLiveModeAct)
        contextMenu.addAction(checkAuxRenderPatch)

        checkUseAnimationAct.triggered.connect(self.checkUseAnimation)
        checkLiveModeAct.triggered.connect(self.checkLiveMode)
        checkAuxRenderPatch.triggered.connect(self.checkAuxPatch)
        contextMenu.exec_(self.mapToGlobal(event.pos()))
    
    def checkUseAnimation(self):
        try:
            checkBoxList = [item.cacheMode for item in self.selectedItems()]        
            self.checkSwitch(checkBoxList)
        except AttributeError:
            print('Selected item is not correct.')
                            
    
    def checkLiveMode(self):
        try:
            checkBoxList = [item.liveMode for item in self.selectedItems()]        
            self.checkSwitch(checkBoxList)
        except AttributeError:
            print('Selected item is not correct.')

    def checkAuxPatch(self):
        try:
            checkBoxList = [item.auxMode for item in self.selectedItems()]        
            self.checkSwitch(checkBoxList)
        except AttributeError:
            print('Selected item is not correct.')

    def checkSwitch(self,checkBoxList):
        checkConvert = lambda checkBox: True if checkBox.checkState(1) == Qt.Checked else False
        if not all(checkConvert(checkBox) for checkBox in checkBoxList):
            for checkBox in checkBoxList:
                checkBox.setCheckState(1,Qt.Checked)
        else:
             for checkBox in checkBoxList:
                    checkBox.setCheckState(1,Qt.Unchecked)


class descriptionItem(QTreeWidgetItem):
    def __init__(self,name=None,palette=None,parent=None):
        QTreeWidgetItem.__init__(self,name=None,palette=None,parnet=None)
        self.name = name
        self.parent= parent
        self.palette = palette 
        self.setText(0,self.name)
        self.cacheMode = QTreeWidgetItem(self)
        self.cacheMode.setText(0,'Use Animation:') 
        self.cacheMode.setCheckState(1,self.getCacheMode())

        self.liveMode = QTreeWidgetItem(self)
        self.liveMode.setText(0,'Live Mode:')
        self.liveMode.setCheckState(1,self.getLiveMode())
        
        self.cacheFile = QTreeWidgetItem(self)
        self.cacheFile.setText(0,'Cache File:')
        self.cacheFile.setText(1,self.getCacheFile())   

        self.auxMode = QTreeWidgetItem(self)
        self.auxMode.setText(0,'Use Aux Render Patch')
        self.auxMode.setCheckState(1,self.getAuxMode())

        self.auxPath = QTreeWidgetItem(self)
        self.auxPath.setText(0,'Aux Render Patch')
        self.auxPath.setText(1,self.getAuxPatchPath())
        
        if os.path.isfile(self.cacheFile.text(1)) and self.getLiveMode() == Qt.Unchecked and self.getCacheMode() == Qt.Checked:
            self.setIcon(0,self.parent.style().standardIcon(getattr(QStyle, 'SP_DialogApplyButton')))
        else:
            self.setIcon(0,QIcon())
        self.addChild(self.cacheMode)
        self.addChild(self.liveMode)
        self.addChild(self.cacheFile)
        
        
    def getCacheFile(self):
        cacheFile = xg.getAttr('cacheFileName',self.palette,self.name,'SplinePrimitive')
        return cacheFile

    def getLiveMode(self):
        if xg.getAttr('liveMode',self.palette,self.name,'SplinePrimitive') in ['False','false','0']:
            return Qt.Unchecked
        else:
            
            return Qt.Checked

    def getCacheMode(self):
        if xg.getAttr('useCache',self.palette,self.name,'SplinePrimitive') in ['false','False','0'] :
            return Qt.Unchecked
        else:
            return Qt.Checked

    def getAuxMode(self):
        #custom__arnold_useAuxRenderPatch
        if xg.getAttr('custom__arnold_useAuxRenderPatch',self.palette,self.name,'RendermanRenderer') in ['false','False','0']:
            return Qt.Unchecked
        else:
            return Qt.Checked  
    def getAuxPatchPath(self):
        return xg.getAttr('custom__arnold_auxRenderPatch',self.palette,self.name,'RendermanRenderer')

class fileListWidget(QListWidget):
    def __init__(self,parent=None):
        QListWidget.__init__(self,parent=None)
        self.parent=parent

    def contextMenuEvent(self,event):
        
        contextMenu = QMenu(self)
        setCacheAct = QAction(u'Set Cache File',self)
        setCacheAct.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowLeft')))
        
        contextMenu = QMenu(self)
        setAuxAct = QAction(u'Set Aux File',self)
        setAuxAct.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowLeft')))
        
        contextMenu.addAction(setCacheAct)
        contextMenu.addAction(setAuxAct)
        setCacheAct.triggered.connect(self.setCacheFilePath)
        setAuxAct.triggered.connect(self.setAuxCache)
        contextMenu.exec_(self.mapToGlobal(event.pos()))

    def setAuxCache(self):
        fileItem = self.selectedItems()[0]
        treeWidget = self.parent.findChild(QTreeWidget,'xgenDesCriptions')
        treeItems = treeWidget.selectedItems()
        for treeItem in treeItems:
            fileItem.path,treeItem.auxPath.setText(1,fileItem.path)

    def setCacheFilePath(self):
        fileItems = self.selectedItems()
        treeWidget = self.parent.findChild(QTreeWidget,'xgenDesCriptions')
        treeItems = treeWidget.selectedItems()
        if not len(fileItems) == len(treeItems):
            print('Check selected items both of file list and attribute list')

        else:
            for fileItem , treeItem in zip(fileItems,treeItems):
                treeItem.cacheMode.setCheckState(1,Qt.Checked)
                treeItem.liveMode.setCheckState(1,Qt.Unchecked)
                fileItem.path,treeItem.cacheFile.setText(1,fileItem.path)

  

class fileListItem(QListWidgetItem):
    def __init__(self,path=None,name=None):
        QListWidgetItem.__init__(self,path=None,name=None)
        self.path = path
        self.name = name
        self.setText(self.name)
        

def main():
    title = 'Xgen_Manager'    
    if cmds.window('Xgen_Manager',ex=True):
        cmds.deleteUI('Xgen_Manager',wnd=True)
    win = xgenManager(maya_main_window())
    win.setObjectName(title)
    win.setWindowTitle(title)
    win.setWindowIcon(QIcon(':follicle.svg'))
    win.show()

        

