#-*- coding: utf-8 -*-
# Author: JCOH
# Date: 2024-05-29
# Version: 1.0
# Description: Symmetry Tool
# Usage: Symmetry Tool
# Dependencies: PySide2, Maya

import maya.OpenMaya as om
import maya.OpenMayaUI as omui

import maya.cmds as cmds
import maya.mel as mel

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import shiboken2

# Get Maya Main Window
def getMayaWindow():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    try:
        mWindow= shiboken2.wrapInstance(long(mayaMainWindowPtr), QMainWindow)
    except:
        mWindow= shiboken2.wrapInstance(int(mayaMainWindowPtr), QMainWindow)
    return mWindow

# Symmetry 2 vertices 
def symmetry(vertex1,vertex2):
    '''
    Usage: Symmetry 2 vertices
    '''
    #Get Position
    pos1 = cmds.xform(vertex1,q=True,ws=True,t=True)
    pos2 = cmds.xform(vertex2,q=True,ws=True,t=True)
    
    #Symmetry
    symPos = [pos1[0]*-1,pos1[1],pos1[2]]
    
    #Move
    cmds.move(symPos[0],symPos[1],symPos[2],vertex2,ws=True,a=True,xyz=True)

# Symmetry Tool
# Main UI
class SymmetryToolUI(QMainWindow):
    def __init__(self):
        super(SymmetryToolUI, self).__init__(parent=getMayaWindow())
        self.setWindowTitle("JC_SymmetryTool")
        self.setMinimumWidth(300)
        self.setMinimumHeight(100)
        self.setWindowFlags(Qt.Window)
        self.setObjectName('JC_SymmetryTool')
        self.createUI()
    
    def createUI(self):
        centerWidget = QWidget()   
        self.setCentralWidget(centerWidget)  
        # Layout
        mainLayout = QVBoxLayout()
        centerWidget.setLayout(mainLayout)
        vertextLaout = QHBoxLayout()    
        # vertex id toggle button
        vertexIdButton = QPushButton("Vertex ID")
        vertexIdButton.clicked.connect(self.vertexId)   
        # Source Vertex
        srcVertexLayout = QVBoxLayout()
        srcVertexLabel = QLabel("Source Vertex")
        self.sourceVerticesListWidget = QListWidget()
        # Select Extension
        self.sourceVerticesListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # set drag and drop mode
        self.sourceVerticesListWidget.setDragDropMode(QAbstractItemView.InternalMove)

        srcVertexLayout.addWidget(srcVertexLabel)
        srcVertexLayout.addWidget(self.sourceVerticesListWidget)
        self.srcAddBtn = QPushButton("Add Source Vertex")
        # srcVertexLayout.addWidget(srcAddBtn)
        srcBtnLayout = QHBoxLayout()
        srcBtnLayout.addWidget(self.srcAddBtn)
        self.removeSrcBtn = QPushButton("Remove Source Vertex")
        srcBtnLayout.addWidget(self.removeSrcBtn)
        srcVertexLayout.addLayout(srcBtnLayout)
        self.srcVertexClearBtn = QPushButton("Clear Source Vertex")
        srcBtnLayout.addWidget(self.srcVertexClearBtn)
        
        
        
        # Target Vertex
        trgVertexLayout = QVBoxLayout()
        trgVertexLabel = QLabel("Source Vertex")
        self.targetVerticesListWidget = QListWidget()
        # Select Extension
        self.targetVerticesListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        trgVertexLayout.addWidget(trgVertexLabel)
        trgVertexLayout.addWidget(self.targetVerticesListWidget)
        self.trgAddBtn = QPushButton("Add Source Vertex")

        # trgVertexLayout.addWidget(trgAddBtn)
        trgBtnLayout = QHBoxLayout()
        trgBtnLayout.addWidget(self.trgAddBtn)
        self.removeTrgBtn = QPushButton("Remove Source Vertex")
        trgBtnLayout.addWidget(self.removeTrgBtn)
        trgVertexLayout.addLayout(trgBtnLayout)
        self.trgVertexClearBtn = QPushButton("Clear Source Vertex")
        trgBtnLayout.addWidget(self.trgVertexClearBtn)
        
        # self.trgAddBtn.clicked.connect(self.getTargetVertex)
        
        vertextLaout.addLayout(srcVertexLayout)
        vertextLaout.addLayout(trgVertexLayout)

        # Symmetry Button
        symmetryButton = QPushButton("Symmetry")
        symmetryButton.clicked.connect(self.symmetry)

        
        mainLayout.addWidget(vertexIdButton)
        mainLayout.addLayout(vertextLaout)
        mainLayout.addWidget(symmetryButton)
        self.setLayout(mainLayout)
        

        # button connections
        self.srcAddBtn.clicked.connect(lambda: self.getVertex('source'))
        self.removeSrcBtn.clicked.connect(lambda: self.sourceVerticesListWidget.takeItem(self.sourceVerticesListWidget.currentRow()))
        self.srcVertexClearBtn.clicked.connect(lambda: self.sourceVerticesListWidget.clear())

        self.trgAddBtn.clicked.connect(lambda: self.getVertex('target'))
        self.removeTrgBtn.clicked.connect(lambda: self.targetVerticesListWidget.takeItem(self.targetVerticesListWidget.currentRow()))
        self.trgVertexClearBtn.clicked.connect(lambda: self.targetVerticesListWidget.clear())

        # contextmenu for source vertices
        self.sourceVerticesListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sourceVerticesListWidget.customContextMenuRequested.connect(self.showSrcContextMenu)
        # # contextmenu for target vertices
        # self.targetVerticesListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.targetVerticesListWidget.customContextMenuRequested.connect(lambda: self.showTargetContextMenu)

        self.sourceVerticesListWidget.clicked.connect(lambda: cmds.select(self.sourceVerticesListWidget.currentItem().text()))
        self.targetVerticesListWidget.clicked.connect(lambda: cmds.select(self.targetVerticesListWidget.currentItem().text()))
        
    # Vertex ID
    def vertexId(self):
        mel.eval('setPolygonDisplaySettings("vertIDs");')
    # Get Source Vertex
    def getVertex(self, typ="source"):
        if typ == "source":
            lst = cmds.ls(sl=True,fl=True)
            # self.sourceVerticesListWidget.clear()
            items = [self.sourceVerticesListWidget.item(i).text() for i in range(self.sourceVerticesListWidget.count())]
            for i in lst:
                if i not in items:
                    self.sourceVerticesListWidget.addItem(i)
        
        if typ == "target":
            lst = cmds.ls(sl=True,fl=True)
            # self.targetVerticesListWidget.clear()
            items = [self.targetVerticesListWidget.item(i).text() for i in range(self.targetVerticesListWidget.count())]
            for i in lst:
                if i not in items:
                    self.targetVerticesListWidget.addItem(i)

    
    # Symmetry
    def symmetry(self):
        matchVertices = {}

        # Get Source Vertices
        sourceVertices = [self.sourceVerticesListWidget.item(i).text() for i in range(self.sourceVerticesListWidget.count())]
        # Get Target Vertices
        targetVertices = [self.targetVerticesListWidget.item(i).text() for i in range(self.targetVerticesListWidget.count())]

        # Check if source and target vertices are equal
        if len(sourceVertices) != len(targetVertices):
            cmds.warning("Source and Target vertices are not equal")
            return
        
        # Symmetry
        for src, trg in zip(sourceVertices, targetVertices):
            symmetry(src, trg)
        return
    
    # Show Source Context Menu
    def showSrcContextMenu(self, pos):
        contextMenu = QMenu()
        sortingAct = contextMenu.addAction("Sort")
        action = contextMenu.exec_(self.mapToGlobal(pos))
        if action == sortingAct:
            self.sourceVerticesListWidget.sortItems(Qt.AscendingOrder)
    
    # # Show Target Context Menu
    # def showTargetContextMenu(self, pos):
    #     contextMenu = QMenu()
    #     sortingAct = contextMenu.addAction("Sort")
    #     action = contextMenu.exec_(self.mapToGlobal(pos))
    #     if action == sortingAct:
    #         self.targetVerticesListWidget.sortItems(Qt.AscendingOrder)

# Show UI
def main():
    if cmds.window("JC_SymmetryTool",ex=True):
        cmds.deleteUI("JC_SymmetryTool")
    # cmds.window("SymmetryTool",e=True,wh=(300,100)
    ui = SymmetryToolUI()
    ui.setObjectName("JC_SymmetryTool")
    ui.show()


