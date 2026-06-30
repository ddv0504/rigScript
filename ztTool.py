# -*- coding: utf-8 -*-
"""
ztTool.py  –  ZT Tool Suite (통합 도구)

원본 파일을 하나로 통합:
  zt_RigUI.py        →  RigTab
  zt_AniUI.py        →  AniTab
  ztool_ToolsUI.py   →  ToolBoxTab
  zt_LightUI.py      →  LightTab
  zt_FXUI.py / ztXgenManager.py   →  XGenTab
  ztMisc/ztSceneCleanup.py        →  SceneTab
  ztAniUtil.py, ztXgenUtil.py     →  내부 임포트 유지
  zTool_v004.py      →  셸프 관리 다이얼로그(ShelfManagerDialog)로 통합

Entry point:
    import ztTool; ztTool.main()
"""

from __future__ import print_function
from imp import reload
import os
import json
import re

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtUiTools import *
    import shiboken2
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide.QtUiTools import *
    import shiboken as shiboken2

# ── 내부 유틸리티 임포트 ──────────────────────────────────────────
from ztLib.ztRig import ztRigUtil
reload(ztRigUtil)
from ztLib.ztMisc import ztMisc, ztSceneCleanup
reload(ztMisc)
reload(ztSceneCleanup)
from ztLib.ztAni import ztAniUtil as zAni
reload(zAni)

# ── 경로 설정 ─────────────────────────────────────────────────────
_CURRENT_PATH = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
_SHELF_PATH   = '%s/shelves' % _CURRENT_PATH
_ICON_PATH    = '%s/icons'   % _CURRENT_PATH

# ── XGen 가용 여부 확인 ──────────────────────────────────────────
try:
    import xgenm as xg
    import xgenm.xgGlobal as xgg
    _XGEN_AVAILABLE = True
except ImportError:
    _XGEN_AVAILABLE = False

# ── 창 이름 ──────────────────────────────────────────────────────
_WINDOW_NAME = 'ZT_MainTool'

# ── Dark Style Sheet ─────────────────────────────────────────────
_DARK_STYLE = """
/* ── Base ─────────────────────────────────────────── */
QWidget {
    background-color: #2b2b2b;
    color: #d4d4d4;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 20px;
}

/* ── MainWindow / Frame ─────────────────────────────*/
QMainWindow, QDialog {
    background-color: #252525;
}

/* ── MenuBar ────────────────────────────────────────*/
QMenuBar {
    background-color: #1e1e1e;
    color: #cccccc;
    border-bottom: 1px solid #3a3a3a;
}
QMenuBar::item:selected {
    background-color: #3c5a8a;
}
QMenu {
    background-color: #2b2b2b;
    border: 1px solid #3a3a3a;
}
QMenu::item:selected {
    background-color: #3c5a8a;
}

/* ── TabWidget ──────────────────────────────────────*/
QTabWidget::pane {
    border: 1px solid #3a3a3a;
    background-color: #2b2b2b;
}
QTabBar::tab {
    background-color: #1e1e1e;
    color: #aaaaaa;
    padding: 5px 12px;
    border: 1px solid #3a3a3a;
    border-bottom: none;
    min-width: 60px;
}
QTabBar::tab:selected {
    background-color: #2b2b2b;
    color: #ffffff;
    border-top: 2px solid #5b9bd5;
}
QTabBar::tab:hover:!selected {
    background-color: #333333;
    color: #cccccc;
}

/* ── Buttons ────────────────────────────────────────*/
QPushButton {
    background-color: #3c3c3c;
    color: #d4d4d4;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 4px 10px;
    min-height: 20px;
}
QPushButton:hover {
    background-color: #4a4a4a;
    border-color: #777777;
}
QPushButton:pressed {
    background-color: #2a2a2a;
    border-color: #5b9bd5;
}
QPushButton:disabled {
    background-color: #2d2d2d;
    color: #666666;
    border-color: #404040;
}

/* ── LineEdit / TextEdit ────────────────────────────*/
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #3a3a3a;
    border-radius: 2px;
    padding: 2px 4px;
    selection-background-color: #3c5a8a;
}
QLineEdit:focus, QTextEdit:focus {
    border-color: #5b9bd5;
}

/* ── ComboBox ───────────────────────────────────────*/
QComboBox {
    background-color: #3c3c3c;
    color: #d4d4d4;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 2px 6px;
    min-height: 20px;
}
QComboBox:hover { border-color: #777777; }
QComboBox::drop-down { border: none; width: 18px; }
QComboBox QAbstractItemView {
    background-color: #2b2b2b;
    color: #d4d4d4;
    border: 1px solid #3a3a3a;
    selection-background-color: #3c5a8a;
}

/* ── SpinBox ─────────────────────────────────────── */
QSpinBox, QDoubleSpinBox {
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #3a3a3a;
    border-radius: 2px;
    padding: 2px 4px;
}
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #3c3c3c;
    border: none;
    width: 14px;
}

/* ── CheckBox / RadioButton ─────────────────────── */
QCheckBox, QRadioButton {
    color: #d4d4d4;
    spacing: 5px;
}
QCheckBox::indicator, QRadioButton::indicator {
    width:  13px;
    height: 13px;
    background-color: #1e1e1e;
    border: 1px solid #555555;
    border-radius: 2px;
}
QCheckBox::indicator:checked {
    background-color: #5b9bd5;
    border-color: #5b9bd5;
}
QRadioButton::indicator { border-radius: 7px; }
QRadioButton::indicator:checked {
    background-color: #5b9bd5;
    border-color: #5b9bd5;
}

/* ── Slider ──────────────────────────────────────── */
QSlider::groove:horizontal {
    height: 4px;
    background-color: #1e1e1e;
    border: 1px solid #3a3a3a;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background-color: #5b9bd5;
    border: 1px solid #4a80bb;
    width: 12px; height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}
QSlider::sub-page:horizontal { background-color: #3c5a8a; border-radius: 2px; }

/* ── ScrollBar ───────────────────────────────────── */
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 10px; margin: 0;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #4a4a4a;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background-color: #5b9bd5; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 10px; margin: 0;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #4a4a4a;
    border-radius: 4px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background-color: #5b9bd5; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── ListWidget / TreeWidget / TableWidget ───────── */
QListWidget, QTreeWidget, QTableWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #3a3a3a;
    alternate-background-color: #252525;
    gridline-color: #3a3a3a;
}
QListWidget::item:selected, QTreeWidget::item:selected,
QTableWidget::item:selected {
    background-color: #3c5a8a;
    color: #ffffff;
}
QListWidget::item:hover, QTreeWidget::item:hover {
    background-color: #333333;
}
QHeaderView::section {
    background-color: #1e1e1e;
    color: #aaaaaa;
    border: 1px solid #3a3a3a;
    padding: 3px 6px;
}

/* ── GroupBox ────────────────────────────────────── */
QGroupBox {
    color: #aaaaaa;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 6px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    color: #7eb3d8;
}

/* ── ToolTip ─────────────────────────────────────── */
QToolTip {
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #5b9bd5;
    padding: 3px;
}

/* ── Splitter ────────────────────────────────────── */
QSplitter::handle {
    background-color: #3a3a3a;
}
QSplitter::handle:horizontal { width: 3px; }
QSplitter::handle:vertical   { height: 3px; }
QSplitter::handle:hover { background-color: #5b9bd5; }

/* ── ProgressBar ─────────────────────────────────── */
QProgressBar {
    background-color: #1e1e1e;
    border: 1px solid #3a3a3a;
    border-radius: 3px;
    text-align: center;
    color: #d4d4d4;
}
QProgressBar::chunk {
    background-color: #5b9bd5;
    border-radius: 2px;
}

/* ── Label ───────────────────────────────────────── */
QLabel { color: #d4d4d4; background-color: transparent; }

/* ── Separator ───────────────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #3a3a3a;
}
"""


# ═════════════════════════════════════════════════════════════════
# 공통 헬퍼
# ═════════════════════════════════════════════════════════════════

def maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    try:
        return shiboken2.wrapInstance(long(ptr), QMainWindow)
    except Exception:
        return shiboken2.wrapInstance(int(ptr), QMainWindow)


# ── Ctrl+휠 스케일 이벤트 필터 ───────────────────────────────────
class WheelScaleFilter(QObject):
    """Ctrl+마우스휠로 창 전체 폰트 크기를 스케일합니다.
    최솟값 7pt ~ 최댓값 20pt.  기본값 11pt.
    """
    _MIN_SIZE = 7
    _MAX_SIZE = 20

    def __init__(self, window):
        super(WheelScaleFilter, self).__init__(window)
        self._window   = window
        self._fontSize = 20          # 현재 폰트 크기 (pt)
        window.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            mods = event.modifiers()
            if mods & Qt.ControlModifier:
                delta = event.angleDelta().y()
                step  = 1 if delta > 0 else -1
                self._fontSize = max(self._MIN_SIZE,
                                     min(self._MAX_SIZE,
                                         self._fontSize + step))
                self._applyScale()
                event.accept()
                return True
        return False

    def _applyScale(self):
        """폰트 크기만 패치한 스타일시트를 재적용합니다."""
        import re
        base = _DARK_STYLE
        # "font-size: Xpx;" 교체
        patched = re.sub(
            r'font-size:\s*\d+px;',
            'font-size: %dpx;' % self._fontSize,
            base
        )
        self._window.setStyleSheet(patched)
        
        # Sync menu check state
        self._window._updateFontSizeMenuCheck(self._fontSize)

        # 상태 표시: 타이틀바에 현재 크기 표시
        self._window.setWindowTitle(
            'ZT Tool Suite  [font %dpt  Ctrl+Wheel: 크기조절  Ctrl+0: 초기화]'
            % self._fontSize
        )


class MayaShelfWidget(QWidget):
    """Maya 셸프 레이아웃을 Qt 위젯 안에 임베드합니다."""

    def __init__(self, name, path='', parent=None):
        super(MayaShelfWidget, self).__init__(parent)
        self.name = name
        self.path = path
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        widget = self._buildShelf()
        if widget:
            widget.setParent(self)
            layout.addWidget(widget)

    def _buildShelf(self):
        funcName = ''
        if self.path and os.path.isfile(self.path):
            with open(self.path, 'r') as f:
                for line in f.readlines():
                    if 'global proc' in line:
                        funcName = '%s()' % line.split(' ')[2]
            mel.eval('source "%s"' % self.path)

        mw = maya_main_window()
        if cmds.shelfLayout(self.name, ex=True):
            cmds.deleteUI(self.name)
        shelfLayout = cmds.shelfLayout(self.name, parent=mw.objectName())
        if funcName:
            mel.eval(funcName)

        try:
            ptr = omui.MQtUtil.findControl(shelfLayout)
        except Exception:
            ptr = omui.MQtUtil_findControl(shelfLayout)
        try:
            return shiboken2.wrapInstance(long(ptr), QWidget)
        except Exception:
            return shiboken2.wrapInstance(int(ptr), QWidget)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        save = QAction('Save Shelf', self)
        menu.addAction(save)
        save.triggered.connect(lambda: (
            cmds.saveShelf(self.name, os.path.splitext(self.path)[0]),
            print('Shelf saved: %s' % self.name)
        ))
        menu.exec_(self.mapToGlobal(event.pos()))


# ═════════════════════════════════════════════════════════════════
# ToolBox 유틸리티 함수 (원본 ztool_ToolsUI.py)
# ═════════════════════════════════════════════════════════════════

def _selPolyMesh(typ=None):
    """타입별 오브젝트를 선택합니다."""
    sel = cmds.ls(long=True, sl=True)
    tops = []
    for obj in sel:
        short = cmds.ls(obj, shortNames=True)[0]
        hier  = obj.split('|')
        if ':' not in short:
            tops.append(hier[1] if len(hier) > 1 else obj)
            continue
        ns = short.partition(':')[0] + ':'
        for each in hier:
            if ns in each:
                tops.append(each)
                break
    if not tops:
        return

    if typ == 'joint':
        nodes = cmds.listRelatives(tops, pa=True, type='joint', ad=True)
        if nodes:
            cmds.select(nodes, r=True)
    elif typ == 'constraint':
        nodes = cmds.listRelatives(tops, pa=True, type='constraint', ad=True)
        if nodes:
            cmds.select(nodes, r=True)
    elif typ == 'hide':
        nodes = cmds.listRelatives(tops, pa=True, type='transform', ad=True) or []
        hidden = [i for i in nodes if cmds.getAttr('%s.v' % i) == 0]
        if hidden:
            cmds.select(hidden, r=True)
    elif typ == 'animNode':
        nodes = cmds.listRelatives(tops, pa=True, type='transform', ad=True) or []
        cmds.select(cl=True)
        for node in nodes:
            conns = cmds.listConnections(node) or []
            for c in conns:
                if 'animCurve' in cmds.objectType(c):
                    cmds.select(c, add=True)
    else:
        nodes = cmds.listRelatives(tops, pa=True, type=typ, ad=True)
        if nodes:
            parents = [cmds.listRelatives(i, p=True)[0] for i in nodes]
            if parents:
                cmds.select(parents, r=True)


def _selKeyedObjs():
    """키프레임이 있는 오브젝트를 선택합니다."""
    sel = cmds.ls(long=True, sl=True)
    tops = []
    for obj in sel:
        short = cmds.ls(obj, shortNames=True)[0]
        hier  = obj.split('|')
        if ':' not in short:
            tops.append(hier[1] if len(hier) > 1 else obj)
            continue
        ns = short.partition(':')[0] + ':'
        for each in hier:
            if ns in each:
                tops.append(each)
                break
    if not tops:
        return
    nodes = cmds.listRelatives(tops, pa=True, type='transform', ad=True) or []
    keyed = [n for n in nodes
             if cmds.keyframe(n, time=(':',), q=True, keyframeCount=True)]
    if keyed:
        cmds.select(keyed, replace=True)


def _getObjAttrs():
    """채널박스에서 선택된 어트리뷰트 목록을 반환합니다."""
    objs  = cmds.ls(sl=True)
    attrs = mel.eval('channelBox -q -selectedMainAttributes mainChannelBox;')
    if not attrs:
        try:
            attrs = mel.eval('channelBox -q -sha mainChannelBox;')
        except Exception:
            return []
    return ['%s.%s' % (o, a) for o in objs for a in attrs] if attrs else []


def _removeItems(listWidget):
    for row in sorted([i.row() for i in listWidget.selectedIndexes()], reverse=True):
        listWidget.takeItem(row)


def _connectAttrs(srcAttr, trgAttrs):
    cmds.undoInfo(ock=True)
    for t in trgAttrs:
        cmds.connectAttr(srcAttr, t, f=True)
    cmds.undoInfo(cck=True)


def _multiConnectAttrs(srcAttrs, trgAttrs):
    if len(srcAttrs) != len(trgAttrs):
        return
    cmds.undoInfo(ock=True)
    for s, t in zip(srcAttrs, trgAttrs):
        cmds.connectAttr(s, t, f=True)
    cmds.undoInfo(cck=True)


def _setDrivenKey(driver, drivens):
    cmds.undoInfo(ock=True)
    for d in drivens:
        cmds.setDrivenKeyframe(d, currentDriver=driver)
    cmds.undoInfo(cck=True)


# ═════════════════════════════════════════════════════════════════
# TAB 1: Rig Tools  (원본 zt_RigUI.py)
# ═════════════════════════════════════════════════════════════════

class RigTab(QWidget):
    """리깅 도구 탭: 셸프, Joint/Curve 도구, 그룹 작업."""

    def __init__(self, parent=None):
        super(RigTab, self).__init__(parent)
        self._build()

    def _build(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(4, 4, 4, 4)

        # ── 리그 셸프 ─────────────────────────────────────────────
        shelfBox = QToolBox()
        for shelfName in ['ztRigDisplay', 'ztRigEditModel', 'ztRigBuild',
                          'ztRigDeformation', 'ztRigExtraTools']:
            f = '%s/%s.mel' % (_SHELF_PATH, shelfName)
            shelf = MayaShelfWidget(name=shelfName, path=f)
            shelfBox.addItem(shelf, shelfName)
        mainLayout.addWidget(shelfBox)

        # ── Joint on Curve ────────────────────────────────────────
        jocGrp = QGroupBox('Joint on Curve')
        jocLayout = QHBoxLayout(jocGrp)
        jocLayout.addWidget(QLabel('Name:'))
        self.jocNameLE = QLineEdit()
        jocLayout.addWidget(self.jocNameLE)
        jocLayout.addWidget(QLabel('Pad:'))
        self.jocPadLE = QLineEdit('0')
        self.jocPadLE.setFixedWidth(28)
        jocLayout.addWidget(self.jocPadLE)
        jocLayout.addWidget(QLabel('Suffix:'))
        self.jocSuffLE = QLineEdit('_jnt')
        jocLayout.addWidget(self.jocSuffLE)
        jocLayout.addWidget(QLabel('Grp:'))
        self.jocGrpLE = QLineEdit('_grp')
        jocLayout.addWidget(self.jocGrpLE)
        self.jocConnectCB = QCheckBox('Connect')
        jocLayout.addWidget(self.jocConnectCB)
        jocBtn = QPushButton('Create')
        jocBtn.clicked.connect(self._createJntOnCurve)
        jocLayout.addWidget(jocBtn)
        mainLayout.addWidget(jocGrp)

        # ── Point on Curve ────────────────────────────────────────
        pocGrp = QGroupBox('Point on Curve')
        pocLayout = QHBoxLayout(pocGrp)
        pocLayout.addWidget(QLabel('오브젝트 선택 후 커브 선택'))
        pocBtn = QPushButton('Create')
        pocBtn.setToolTip('커브에 붙일 오브젝트들을 먼저 선택하고 마지막에 커브를 선택하세요.')
        pocBtn.clicked.connect(self._createPointOnCurve)
        pocLayout.addWidget(pocBtn)
        mainLayout.addWidget(pocGrp)

        # ── Joint Operations ──────────────────────────────────────
        jntGrp = QGroupBox('Joint Operations')
        jntLayout = QHBoxLayout(jntGrp)
        dispOrBtn = QPushButton('Show Orient')
        dispOrBtn.clicked.connect(
            lambda: [ztRigUtil.displayJointOrient(i)
                     for i in cmds.ls(sl=True) if cmds.objectType(i) == 'joint'])
        hideOrBtn = QPushButton('Hide Orient')
        hideOrBtn.clicked.connect(
            lambda: [ztRigUtil.hideJointOrient(i)
                     for i in cmds.ls(sl=True) if cmds.objectType(i) == 'joint'])
        rotToOrBtn = QPushButton('Rot → Orient')
        rotToOrBtn.clicked.connect(self._rotToOrient)
        jntLayout.addWidget(dispOrBtn)
        jntLayout.addWidget(hideOrBtn)
        jntLayout.addWidget(rotToOrBtn)
        mirJntBtn = QPushButton('Mirror Joint')
        mirJntBtn.setToolTip('조인트 미러 (tak_misc.mirJntUi)')
        mirJntBtn.clicked.connect(self._launchMirJnt)
        jntLayout.addWidget(mirJntBtn)
        mirObjBtn = QPushButton('Mirror Object')
        mirObjBtn.setToolTip('오브젝트 미러 (tak_misc.mirObjUi)')
        mirObjBtn.clicked.connect(self._launchMirObj)
        jntLayout.addWidget(mirObjBtn)
        infLockBtn = QPushButton('Influence Locker')
        infLockBtn.setToolTip('스킨 인플루언스 잠금 (ztInfLockerUI)')
        infLockBtn.clicked.connect(self._launchInfluenceLocker)
        jntLayout.addWidget(infLockBtn)
        mainLayout.addWidget(jntGrp)

        # ── Group Operations ──────────────────────────────────────
        grpGrp = QGroupBox('Group Operations')
        grpLayout = QHBoxLayout(grpGrp)
        addOffBtn = QPushButton('Add Offset Group')
        self.defaultRB = QRadioButton('Default')
        self.defaultRB.setChecked(True)
        customRB = QRadioButton('Custom')
        self.suffGrpLE = QLineEdit('_offset')
        self.suffGrpLE.setEnabled(False)
        btnGrp = QButtonGroup(grpGrp)
        btnGrp.addButton(self.defaultRB)
        btnGrp.addButton(customRB)
        btnGrp.buttonClicked.connect(
            lambda: self.suffGrpLE.setEnabled(not self.defaultRB.isChecked()))
        addOffBtn.clicked.connect(lambda: self._addOffsetGroup(btnGrp))
        grpLayout.addWidget(addOffBtn)
        grpLayout.addWidget(self.defaultRB)
        grpLayout.addWidget(customRB)
        grpLayout.addWidget(QLabel('Suffix:'))
        grpLayout.addWidget(self.suffGrpLE)
        mainLayout.addWidget(grpGrp)

        # ── Cleanup ───────────────────────────────────────────────
        cleanGrp = QGroupBox('Cleanup')
        cleanLayout = QHBoxLayout(cleanGrp)
        cleanRigBtn = QPushButton('Clean Up Rig')
        cleanRigBtn.setToolTip('리그 퍼블리시 전 정리 도구 (tak_cleanUpRig)')
        cleanRigBtn.clicked.connect(self._launchCleanUpRig)
        cleanMdlBtn = QPushButton('Clean Up Model')
        cleanMdlBtn.setToolTip('리깅 전 모델 정리 도구 (tak_cleanUpModel)')
        cleanMdlBtn.clicked.connect(self._launchCleanUpModel)
        autoWheelBtn = QPushButton('Auto Wheel')
        autoWheelBtn.setToolTip('동적 바퀴 리그 생성 (ztAutoWheel)')
        autoWheelBtn.clicked.connect(self._launchAutoWheel)
        cleanLayout.addWidget(cleanRigBtn)
        cleanLayout.addWidget(cleanMdlBtn)
        cleanLayout.addWidget(autoWheelBtn)
        mainLayout.addWidget(cleanGrp)

        mainLayout.addStretch()

    def _createJntOnCurve(self):
        try:
            pad = int(self.jocPadLE.text() or 0)
        except ValueError:
            pad = 0
        ztRigUtil.createJntOnCurve(
            self.jocNameLE.text(), pad,
            self.jocSuffLE.text(), self.jocGrpLE.text(),
            self.jocConnectCB.isChecked()
        )

    def _createPointOnCurve(self):
        sel = cmds.ls(sl=True)
        if len(sel) >= 2:
            ztRigUtil.createPointOnCurveInfo(sel[-1], sel[:-1])

    def _rotToOrient(self):
        cmds.undoInfo(ock=True)
        for jnt in cmds.ls(sl=True):
            if cmds.objectType(jnt) == 'joint':
                ztRigUtil.rotToOrient(jnt)
        cmds.undoInfo(cck=True)

    def _addOffsetGroup(self, btnGrp):
        objs = cmds.ls(sl=True)
        btn  = [b for b in btnGrp.buttons() if b.isChecked()][0]
        cmds.undoInfo(ock=True)
        for obj in objs:
            if btn.text() == 'Default':
                ztRigUtil.addOffsetGroup(obj)
            else:
                ztRigUtil.addOffsetGroup(obj, '%s%s' % (obj, self.suffGrpLE.text()))
        cmds.undoInfo(cck=True)

    def _launchCleanUpRig(self):
        try:
            from ztLib.ztRig import tak_cleanUpRig
            reload(tak_cleanUpRig)
            tak_cleanUpRig.ui()
        except Exception as e:
            QMessageBox.critical(self, 'Error', 'Clean Up Rig 실행 실패:\n%s' % e)

    def _launchCleanUpModel(self):
        try:
            from ztLib.ztRig import tak_cleanUpModel
            reload(tak_cleanUpModel)
            tak_cleanUpModel.UI()
        except Exception as e:
            QMessageBox.critical(self, 'Error', 'Clean Up Model 실행 실패:\n%s' % e)

    def _launchMirJnt(self):
        try:
            from ztLib.ztRig import tak_misc
            reload(tak_misc)
            tak_misc.mirJntUi()
        except Exception as e:
            QMessageBox.critical(self, 'Error', 'Mirror Joint 실행 실패:\n%s' % e)

    def _launchMirObj(self):
        try:
            from ztLib.ztRig import tak_misc
            reload(tak_misc)
            tak_misc.mirObjUi()
        except Exception as e:
            QMessageBox.critical(self, 'Error', 'Mirror Object 실행 실패:\n%s' % e)

    def _launchInfluenceLocker(self):
        try:
            from ztLib.ztRig import ztInfLockerUI as infLockerUI
            reload(infLockerUI)
            infLockerUI.main()
        except Exception as e:
            QMessageBox.critical(self, 'Error', 'Influence Locker 실행 실패:\n%s' % e)

    def _launchAutoWheel(self):
        try:
            from ztLib.ztRig import ztAutoWheel as AutoWheel
            reload(AutoWheel)
            AutoWheel.main()
        except Exception as e:
            QMessageBox.critical(self, 'Error', 'Auto Wheel 실행 실패:\n%s' % e)


# ═════════════════════════════════════════════════════════════════
# TAB 2: Animation Tools  (원본 zt_AniUI.py + zt_AniUtil.py)
# ═════════════════════════════════════════════════════════════════

class _DirView(QTreeView):
    """로컬 파일 시스템 트리뷰."""

    def __init__(self):
        super(_DirView, self).__init__()
        self.path   = ''
        self._model = QFileSystemModel()
        self.doubleClicked.connect(self._openFile)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction('Open File',
                       lambda: self._openFile(self.selectedIndexes()[0])
                       if self.selectedIndexes() else None)
        menu.addAction('Open Folder',
                       lambda: os.startfile(self.path) if self.path else None)
        menu.exec_(self.mapFromParent(event.globalPos()))

    def _openFile(self, index):
        path = self._model.filePath(index)
        if path:
            ext = os.path.splitext(path)[1].lower()
            if ext in ('.ma', '.mb'):
                cmds.file(path, o=True, f=True)
            else:
                os.startfile(path)

    def setPath(self, path):
        self.path = path
        self._model.setRootPath(path)
        self.setModel(self._model)
        self.setRootIndex(self._model.index(path))


class AniTab(QWidget):
    """애니메이션 도구 탭: 셸프, 키 정렬/이동, 플레이블라스트, 로컬 파일."""

    playBlastInfo = {}
    toggle = False

    def __init__(self, parent=None):
        super(AniTab, self).__init__(parent)
        self.pbSetting = QSettings('ZT_AniTools_playblast_setting')
        self._build()
        self._loadSettings()
        self.setLocalList()

    def _build(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(4, 4, 4, 4)
        innerTabs = QTabWidget()
        mainLayout.addWidget(innerTabs)

        # ── Tools 내부 탭 ──────────────────────────────────────────
        toolWidget = QWidget()
        innerTabs.addTab(toolWidget, 'Tools')
        toolLayout = QVBoxLayout(toolWidget)
        toolLayout.setContentsMargins(4, 4, 4, 4)

        # 애니메이션 셸프
        shelfFilePath = '%s/ztAnimation.mel' % _SHELF_PATH
        self.aniShelf = MayaShelfWidget('ztAnimation', shelfFilePath)
        self.aniShelf.setMinimumSize(150, 100)
        self.aniShelf.setStyleSheet('')
        saveShelfBtn = QPushButton('Save Shelf')
        saveShelfBtn.clicked.connect(
            lambda: (cmds.saveShelf('ztAnimation', os.path.splitext(shelfFilePath)[0]),
                     print('Animation shelf saved.')))
        toolLayout.addWidget(self.aniShelf)
        toolLayout.addWidget(saveShelfBtn)

        # 레퍼런스 이미지
        refGrp = QGroupBox('Reference Image')
        refLayout = QVBoxLayout(refGrp)
        refImgBtn = QPushButton('Add Ref Image')
        refImgBtn.setIcon(QIcon(':fileOpen.png'))
        refImgBtn.clicked.connect(self._setPreviewImage)
        refLayout.addWidget(refImgBtn)
        self.imageWidget = QListWidget()
        self.imageWidget.setIconSize(QSize(80, 80))
        self.imageWidget.setMaximumHeight(90)
        refLayout.addWidget(self.imageWidget)

        # 카메라 / 레이어
        camLayLayout = QHBoxLayout()
        self.camRefreshBtn = QPushButton()
        self.camRefreshBtn.setFixedWidth(28)
        self.camRefreshBtn.setIcon(QIcon(':refresh.png'))
        self.camRefreshBtn.clicked.connect(self._refreshCamList)
        self.camComboBox = QComboBox()
        self._refreshCamList()
        layNameLbl = QLabel('Layer:')
        self.layerNameLE = QLineEdit('Ref')
        self.createLayerBtn = QPushButton('Create Layer')
        self.createLayerBtn.clicked.connect(self._createLayer)
        camLayLayout.addWidget(self.camRefreshBtn)
        camLayLayout.addWidget(self.camComboBox)
        camLayLayout.addWidget(layNameLbl)
        camLayLayout.addWidget(self.layerNameLE)
        camLayLayout.addWidget(self.createLayerBtn)
        refLayout.addLayout(camLayLayout)
        toolLayout.addWidget(refGrp)

        # FBX 익스포트
        fbxGrp = QGroupBox('FBX Export')
        fbxLayout = QVBoxLayout(fbxGrp)
        
        fbxAddLayout = QHBoxLayout()
        addSelBtn = QPushButton('Add Selected Object(s)')
        addSelBtn.clicked.connect(self._addFbxExportItem)
        fbxAddLayout.addWidget(addSelBtn)
        fbxLayout.addLayout(fbxAddLayout)
        
        self.fbxTable = QTableWidget(0, 6)
        self.fbxTable.setHorizontalHeaderLabels(['Object', 'Clip/File Name', 'Start', 'End', 'Export Path', ''])
        self.fbxTable.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.fbxTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.fbxTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.fbxTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.fbxTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.fbxTable.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.fbxTable.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.fbxTable.setMinimumHeight(150)
        fbxLayout.addWidget(self.fbxTable)
        
        fbxSettingsLayout = QGridLayout()
        
        self.fbxMoveOriginCB = QCheckBox('Move To Origin')
        self.fbxBakeAnimCB = QCheckBox('Bake Animation')
        self.fbxBakeAnimCB.setChecked(True)
        self.fbxInputConnCB = QCheckBox('Input Connections')
        self.fbxInputConnCB.setChecked(True)
        self.fbxEmbedMediaCB = QCheckBox('Embed Media')
        self.fbxEmbedMediaCB.setChecked(True)
        self.fbxOnlyJointsCB = QCheckBox('Export Only Joints')
        self.fbxOnlyJointsCB.setChecked(True)
        self.fbxCurvesCB = QCheckBox('Export Curves')
        
        fbxSettingsLayout.addWidget(self.fbxMoveOriginCB, 0, 0)
        fbxSettingsLayout.addWidget(self.fbxBakeAnimCB, 0, 1)
        fbxSettingsLayout.addWidget(self.fbxInputConnCB, 1, 0)
        fbxSettingsLayout.addWidget(self.fbxEmbedMediaCB, 1, 1)
        
        fbxSettingsLayout.addWidget(self.fbxOnlyJointsCB, 2, 0)
        fbxSettingsLayout.addWidget(self.fbxCurvesCB, 2, 1)
        
        fbxSettingsLayout.addWidget(QLabel('Up Axis:'), 3, 0)
        self.fbxUpAxisCombo = QComboBox()
        self.fbxUpAxisCombo.addItems(['Y', 'Z'])
        fbxSettingsLayout.addWidget(self.fbxUpAxisCombo, 3, 1)
        
        fbxSettingsLayout.addWidget(QLabel('File Type:'), 4, 0)
        self.fbxFileTypeCombo = QComboBox()
        self.fbxFileTypeCombo.addItems(['Binary', 'ASCII'])
        fbxSettingsLayout.addWidget(self.fbxFileTypeCombo, 4, 1)
        
        fbxSettingsLayout.addWidget(QLabel('FBX Version:'), 5, 0)
        self.fbxVersionCombo = QComboBox()
        self.fbxVersionCombo.addItems(['FBX 2020', 'FBX 2018', 'FBX 2016', 'FBX 2014'])
        fbxSettingsLayout.addWidget(self.fbxVersionCombo, 5, 1)
        
        fbxLayout.addLayout(fbxSettingsLayout)
        
        fbxExportBtn = QPushButton('Export FBX')
        fbxExportBtn.clicked.connect(self._exportFbx)
        fbxLayout.addWidget(fbxExportBtn)
        
        toolLayout.addWidget(fbxGrp)

        # 키 정렬
        alignGrp = QGroupBox('Align Keys')
        alignLayout = QHBoxLayout(alignGrp)
        leftBtn = QPushButton()
        leftBtn.setIcon(QApplication.style().standardIcon(QStyle.SP_MediaSkipBackward))
        leftBtn.setToolTip('Align to earliest key')
        leftBtn.clicked.connect(
            lambda: (cmds.undoInfo(openChunk=True),
                     zAni.alignKeyframe(),
                     cmds.undoInfo(closeChunk=True)))
        centerBtn = QPushButton()
        centerBtn.setIcon(QApplication.style().standardIcon(QStyle.SP_MediaPause))
        centerBtn.setToolTip('Align to current time')
        centerBtn.clicked.connect(
            lambda: (cmds.undoInfo(openChunk=True),
                     zAni.alignKeyframe(current=True),
                     cmds.undoInfo(closeChunk=True)))
        rightBtn = QPushButton()
        rightBtn.setIcon(QApplication.style().standardIcon(QStyle.SP_MediaSkipForward))
        rightBtn.setToolTip('Align to latest key')
        rightBtn.clicked.connect(
            lambda: (cmds.undoInfo(openChunk=True),
                     zAni.alignKeyframe(right=True),
                     cmds.undoInfo(closeChunk=True)))
        alignLayout.addWidget(leftBtn)
        alignLayout.addWidget(centerBtn)
        alignLayout.addWidget(rightBtn)
        alignLayout.addStretch()
        toolLayout.addWidget(alignGrp)

        # 키 이동
        moveGrp = QGroupBox('Move Keys')
        moveLayout = QHBoxLayout(moveGrp)
        moveLayout.addWidget(QLabel('Frames:'))
        self.valueLE = QLineEdit()
        self.valueLE.setFixedWidth(50)
        moveLayout.addWidget(self.valueLE)
        fwdBtn = QPushButton()
        fwdBtn.setIcon(QApplication.style().standardIcon(QStyle.SP_MediaSeekForward))
        fwdBtn.clicked.connect(self._moveKeys)
        self.toFrameCB   = QCheckBox('To Frame')
        self.moveRB      = QRadioButton('Move')
        self.moveRB.setChecked(True)
        self.overlapRB   = QRadioButton('Overlap')
        breakBtn = QPushButton('Break Cycle')
        breakBtn.clicked.connect(
            lambda: (cmds.undoInfo(openChunk=True),
                     zAni.breakAnimCycle(),
                     cmds.undoInfo(closeChunk=True)))
        self.toFrameCB.stateChanged.connect(self._toFrameState)
        moveLayout.addWidget(fwdBtn)
        moveLayout.addWidget(self.toFrameCB)
        moveLayout.addWidget(self.moveRB)
        moveLayout.addWidget(self.overlapRB)
        moveLayout.addWidget(breakBtn)
        toolLayout.addWidget(moveGrp)

        # 플레이블라스트
        pbGrp = QGroupBox('Playblast')
        pbLayout = QVBoxLayout(pbGrp)
        
        camLayout = QHBoxLayout()
        self.setCamLbl = QLabel('cam: —')
        setCamBtn = QPushButton('Set Cam')
        setCamBtn.setIcon(QIcon(':CameraDown.png'))
        setCamBtn.clicked.connect(self._setPlayblastCam)
        camLayout.addWidget(self.setCamLbl)
        camLayout.addWidget(setCamBtn)
        pbLayout.addLayout(camLayout)
        
        optLayout = QHBoxLayout()
        optLayout.addWidget(QLabel('Type:'))
        self.pbTypeCombo = QComboBox()
        self.pbTypeCombo.addItems(['mov', 'sequence'])
        optLayout.addWidget(self.pbTypeCombo)
        
        optLayout.addWidget(QLabel('Format:'))
        self.pbFormatCombo = QComboBox()
        optLayout.addWidget(self.pbFormatCombo)
        pbLayout.addLayout(optLayout)
        
        self.pbBtn = QPushButton('Playblast')
        self.pbBtn.clicked.connect(self._playBlast)
        pbLayout.addWidget(self.pbBtn)
        
        self.pbTypeCombo.currentIndexChanged.connect(self._updatePlayblastFormats)
        self.pbFormatCombo.currentIndexChanged.connect(self._onFormatChanged)
        
        toolLayout.addWidget(pbGrp)
        toolLayout.addStretch()

        # ── Local 내부 탭 ──────────────────────────────────────────
        localWidget = QWidget()
        innerTabs.addTab(localWidget, 'Local Files')
        localLayout = QVBoxLayout(localWidget)
        localLayout.setContentsMargins(4, 4, 4, 4)
        urlLayout = QHBoxLayout()
        self.urlLE = QLineEdit()
        self.urlLE.setReadOnly(True)
        openDirBtn = QPushButton()
        openDirBtn.setIcon(QApplication.style().standardIcon(QStyle.SP_DirOpenIcon))
        openDirBtn.clicked.connect(
            lambda: os.startfile(self.urlLE.text())
            if os.path.isdir(self.urlLE.text()) else None)
        urlLayout.addWidget(self.urlLE)
        urlLayout.addWidget(openDirBtn)
        localLayout.addLayout(urlLayout)
        self.dirTreeView = _DirView()
        self.dirTreeView.setSortingEnabled(True)
        localLayout.addWidget(self.dirTreeView)

    # ── 설정 로드 ─────────────────────────────────────────────────
    def _loadSettings(self):
        cam = self.pbSetting.value('cam')
        if cam:
            self.playBlastInfo['cam'] = cam
            self.setCamLbl.setText('cam: %s' % cam)

        pbType = self.pbSetting.value('pbType')
        pbFormat = self.pbSetting.value('pbFormat')
        
        if pbType:
            index = self.pbTypeCombo.findText(pbType)
            if index != -1:
                self.pbTypeCombo.setCurrentIndex(index)
                
        self._updatePlayblastFormats()
        
        if pbFormat:
            index = self.pbFormatCombo.findText(pbFormat)
            if index != -1:
                self.pbFormatCombo.setCurrentIndex(index)
                
        self._updatePlayblastBtnText()

    def _updatePlayblastFormats(self):
        self.pbFormatCombo.clear()
        pb_type = self.pbTypeCombo.currentText()
        if pb_type == 'mov':
            self.pbFormatCombo.addItems(['mov', 'avi', 'gif'])
        elif pb_type == 'sequence':
            self.pbFormatCombo.addItems(['png', 'jpg'])
        
        self.pbSetting.setValue('pbType', pb_type)
        
    def _onFormatChanged(self):
        pb_fmt = self.pbFormatCombo.currentText()
        if pb_fmt:
            self.pbSetting.setValue('pbFormat', pb_fmt)
        self._updatePlayblastBtnText()
        
    def _updatePlayblastBtnText(self):
        pb_type = self.pbTypeCombo.currentText()
        pb_fmt = self.pbFormatCombo.currentText()
        if pb_type == 'mov':
            if pb_fmt == 'mov':
                self.pbBtn.setText('Playblast (QuickTime H.264)')
            elif pb_fmt == 'avi':
                self.pbBtn.setText('Playblast (AVI)')
            elif pb_fmt == 'gif':
                self.pbBtn.setText('Playblast (Animated GIF)')
        elif pb_type == 'sequence':
            if pb_fmt == 'png':
                self.pbBtn.setText('Playblast (PNG Sequence)')
            elif pb_fmt == 'jpg':
                self.pbBtn.setText('Playblast (JPG Sequence)')

    # ── 카메라 목록 갱신 ─────────────────────────────────────────
    def _refreshCamList(self):
        self.camComboBox.clear()
        skip = ('front', 'persp', 'side', 'top')
        cams = [c for c in cmds.ls(type='camera')
                if not any(c.startswith(p) for p in skip)]
        self.camComboBox.addItems(cams)

    # ── 레퍼런스 이미지 ───────────────────────────────────────────
    def _setPreviewImage(self):
        files = cmds.fileDialog2(
            fm=1, caption='Select Reference Image', okc='Import',
            ff='Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.tga *.gif *.exr)',
            ds=1)
        if files:
            item = QListWidgetItem()
            item.setIcon(QIcon(files[0]))
            item.setText(files[0])
            self.imageWidget.addItem(item)

    def _createLayer(self):
        camShape = self.camComboBox.currentText()
        if not cmds.objExists(camShape):
            cmds.confirmDialog(m='Camera does not exist.')
            return
        items = self.imageWidget.selectedItems()
        if not items:
            cmds.confirmDialog(m='Select an image first.')
            return
        image    = items[0].text()
        imgShape = cmds.createNode('imagePlane',
                                   n=os.path.basename(image).split('.')[0])
        cmds.setAttr(imgShape + '.imageName', image, type='string')
        n = 0
        while cmds.listConnections(camShape + '.imagePlane[%s]' % n):
            n += 1
        cmds.connectAttr(imgShape + '.message',
                         camShape + '.imagePlane[%s]' % n, f=True)
        camTrans = cmds.listRelatives(camShape, p=True)[0]
        imgTrans = cmds.listRelatives(imgShape, p=True)[0]
        cmds.parent(imgTrans, camTrans, s=True)
        cmds.setAttr(imgTrans + '.displayOnlyIfCurrent', 1)
        layer = cmds.createDisplayLayer(n='%s_lyr' % self.layerNameLE.text())
        cmds.editDisplayLayerMembers(layer, imgTrans, noRecurse=True)

    # ── 플레이블라스트 ────────────────────────────────────────────
    def _setPlayblastCam(self):
        try:
            panel = cmds.getPanel(wf=True)
            cam   = cmds.modelEditor(panel, cam=True, q=True)
            self.playBlastInfo['cam'] = cam
            self.setCamLbl.setText('cam: %s' % cam)
            self.pbSetting.setValue('cam', cam)
        except RuntimeError:
            cmds.warning('먼저 뷰포트를 선택하세요.')

    def _playBlast(self):
        fileName = cmds.file(sn=True, q=True)
        if not fileName:
            QMessageBox.warning(self, 'Error', '씬을 먼저 저장하세요.')
            return
        cam     = self.playBlastInfo.get('cam', '')
        
        # Get selected options
        pb_type = self.pbTypeCombo.currentText()
        pb_fmt  = self.pbFormatCombo.currentText()
        
        # Determine parameters based on options
        if pb_type == 'mov':
            if pb_fmt == 'mov':
                ext = '.mov'
                pb_format = 'qt'
                pb_compression = 'H.264'
            elif pb_fmt == 'avi':
                ext = '.avi'
                pb_format = 'avi'
                pb_compression = 'none'
            elif pb_fmt == 'gif':
                ext = '.gif'
                pb_format = 'image'  # initially output to png sequence
                pb_compression = 'png'
        else: # sequence
            pb_format = 'image'
            if pb_fmt == 'png':
                ext = '.png'
                pb_compression = 'png'
            else: # jpg
                ext = '.jpg'
                pb_compression = 'jpeg'

        pbFile = self._getPlayblastFileName(fileName, ext)
        wh      = [1280, 720]
        tr      = mel.eval('timeControl -q -ra $gPlayBackSlider;')
        tc      = mel.eval('$tmpVar = $gPlayBackSlider')
        sound   = cmds.timeControl(tc, q=True, sound=True)
        start   = tr[0] if (tr[1] - tr[0]) > 1 else cmds.playbackOptions(q=True, min=True)
        end     = tr[1] if (tr[1] - tr[0]) > 1 else cmds.playbackOptions(q=True, max=True)
        if cmds.window('zt_pbWin', ex=True):
            cmds.deleteUI('zt_pbWin')
        win = cmds.window('zt_pbWin')
        cmds.paneLayout()
        panel = cmds.modelPanel()
        cmds.modelEditor(mp=panel, camera=cam, pm=True, ps=True, dtx=True,
                         displayAppearance='smoothShaded', th=True, alo=False)
        cmds.window(win, e=True, wh=wh)
        cmds.showWindow(win)
        
        temp_dir = None
        try:
            if pb_type == 'mov' and pb_fmt == 'gif':
                import tempfile
                temp_dir = tempfile.mkdtemp()
                temp_prefix = os.path.join(temp_dir, 'temp_pb')
                
                cmds.playblast(epn=panel, startTime=start, endTime=end, sound=sound,
                               format='image', filename=temp_prefix, forceOverwrite=True,
                               clearCache=True, viewer=False, percent=100,
                               compression='png', quality=100, widthHeight=wh)
                               
                import glob
                png_files = sorted(glob.glob(os.path.join(temp_dir, 'temp_pb.*.png')))
                if png_files:
                    try:
                        from PIL import Image
                        frames = [Image.open(f) for f in png_files]
                        
                        fps = 24.0
                        try:
                            fps_unit = cmds.currentUnit(q=True, time=True)
                            fps_map = {
                                'game': 15.0, 'film': 24.0, 'pal': 25.0, 'ntsc': 30.0,
                                'show': 48.0, 'palf': 50.0, 'ntscf': 60.0
                            }
                            if fps_unit in fps_map:
                                fps = fps_map[fps_unit]
                            elif fps_unit.endswith('fps'):
                                fps = float(fps_unit[:-3])
                        except Exception:
                            pass
                            
                        duration = int(1000.0 / fps) if fps > 0 else 40
                        frames[0].save(
                            pbFile,
                            save_all=True,
                            append_images=frames[1:],
                            duration=duration,
                            loop=0
                        )
                        
                        if os.name == 'nt':
                            os.startfile(pbFile)
                        else:
                            import subprocess
                            subprocess.call(('open', pbFile))
                    except ImportError:
                        QMessageBox.warning(
                            self, 'Pillow Missing',
                            'GIF 변환을 위해 Pillow 라이브러리가 필요합니다.\n'
                            'Maya Python 환경에 Pillow를 설치해 주세요.\n'
                            '명령어: mayapy -m pip install Pillow'
                        )
                    except Exception as e:
                        print('GIF conversion error:', e)
                        QMessageBox.critical(self, 'GIF Error', 'GIF 생성 중 오류 발생:\n%s' % e)
            else:
                pb_args = {
                    'epn': panel,
                    'startTime': start,
                    'endTime': end,
                    'sound': sound,
                    'format': pb_format,
                    'filename': pbFile,
                    'forceOverwrite': True,
                    'clearCache': True,
                    'viewer': True,
                    'percent': 100,
                    'quality': 100,
                    'widthHeight': wh
                }
                if pb_compression:
                    pb_args['compression'] = pb_compression
                cmds.playblast(**pb_args)
        except Exception as e:
            print('Playblast error:', e)
        finally:
            cmds.deleteUI(win)
            if temp_dir and os.path.isdir(temp_dir):
                import glob
                for f in glob.glob(os.path.join(temp_dir, '*')):
                    try:
                        os.remove(f)
                    except Exception:
                        pass
                try:
                    os.rmdir(temp_dir)
                except Exception:
                    pass

    def _getPlayblastFileName(self, scenePath, ext):
        dirName  = os.path.dirname(scenePath)
        base     = os.path.splitext(os.path.basename(scenePath))[0]
        
        if ext.lower() in ('.jpg', '.jpeg'):
            ext_pattern = r'\.jpe?g'
        else:
            ext_pattern = re.escape(ext)
            
        pattern = re.compile(
            r'^' + re.escape(base) + r'_P(\d+)(?:\.\d+)?' + ext_pattern + r'$',
            re.IGNORECASE
        )
        
        existing_versions = []
        try:
            for item in os.listdir(dirName):
                m = pattern.match(item)
                if m:
                    existing_versions.append(int(m.group(1)))
        except Exception:
            pass
            
        if not existing_versions:
            nextVer = 1
        else:
            nextVer = max(existing_versions) + 1
            
        pb_type = self.pbTypeCombo.currentText()
        if pb_type == 'sequence':
            return '%s/%s_P%s' % (dirName, base, str(nextVer).zfill(2))
        else:
            return '%s/%s_P%s%s' % (dirName, base, str(nextVer).zfill(2), ext)

    # ── 키 이동 ───────────────────────────────────────────────────
    def _moveKeys(self):
        try:
            value = int(self.valueLE.text())
        except ValueError:
            return
        if self.toFrameCB.isChecked():
            zAni.moveKeyFrame(value, toFrame=True)
        elif self.moveRB.isChecked():
            zAni.moveKeyFrame(value, move=True)
        else:
            cmds.undoInfo(openChunk=True)
            zAni.moveKeyFrame(value, overLap=True)
            cmds.undoInfo(closeChunk=True)

    def _toFrameState(self):
        enabled = not self.toFrameCB.isChecked()
        self.moveRB.setEnabled(enabled)
        self.overlapRB.setEnabled(enabled)

    # ── 로컬 파일 목록 ────────────────────────────────────────────
    def setLocalList(self):
        fileName = cmds.file(sn=True, q=True)
        path     = os.path.dirname(fileName) if fileName else ''
        if not os.path.isdir(path):
            self.urlLE.setText('씬이 아직 저장되지 않았습니다.')
            return
        self.dirTreeView.setPath(path)
        self.urlLE.setText(path)

    # ── ScriptJob (창 오브젝트 이름 전달 필요) ────────────────────
    def startScriptJob(self, parentName):
        cmds.scriptJob(event=['SceneOpened',    self._refreshAll], parent=parentName)
        cmds.scriptJob(event=['SceneSaved',     self._refreshAll], parent=parentName)
        cmds.scriptJob(event=['SceneOpened',    self._clearCam],   parent=parentName)
        cmds.scriptJob(event=['NewSceneOpened', self._clearCam],   parent=parentName)

    def _clearCam(self):
        self.pbSetting.remove('cam')
        self.setCamLbl.setText('cam: —')
        self.playBlastInfo = {}

    def _refreshAll(self):
        self.playBlastInfo = {}
        self.setLocalList()

    # ── FBX Export ───────────────────────────────────────────────
    def _addFbxExportItem(self):
        sel = cmds.ls(sl=True)
        if not sel:
            QMessageBox.warning(self, 'Selection Empty', '선택된 오브젝트가 없습니다.')
            return
            
        scenePath = cmds.file(sn=True, q=True)
        if scenePath:
            sceneDir = os.path.dirname(scenePath).replace('\\', '/')
            sceneBase = os.path.splitext(os.path.basename(scenePath))[0]
        else:
            sceneDir = os.path.expanduser('~/Desktop').replace('\\', '/')
            sceneBase = 'Untitled'
            
        start_frame = int(cmds.playbackOptions(q=True, min=True))
        end_frame = int(cmds.playbackOptions(q=True, max=True))
        
        for obj in sel:
            obj_name = obj.split('|')[-1]
            clip_name = '%s_%s' % (sceneBase, obj_name)
            
            row = self.fbxTable.rowCount()
            self.fbxTable.insertRow(row)
            
            # Col 0: Object Name
            objItem = QTableWidgetItem(obj)
            objItem.setFlags(objItem.flags() ^ Qt.ItemIsEditable)
            self.fbxTable.setItem(row, 0, objItem)
            
            # Col 1: Clip/File Name
            clipLE = QLineEdit(clip_name)
            self.fbxTable.setCellWidget(row, 1, clipLE)
            
            # Col 2: Start
            startSB = QSpinBox()
            startSB.setRange(-999999, 999999)
            startSB.setValue(start_frame)
            self.fbxTable.setCellWidget(row, 2, startSB)
            
            # Col 3: End
            endSB = QSpinBox()
            endSB.setRange(-999999, 999999)
            endSB.setValue(end_frame)
            self.fbxTable.setCellWidget(row, 3, endSB)
            
            # Col 4: Path Widget
            pathWidget = QWidget()
            pathLayout = QHBoxLayout(pathWidget)
            pathLayout.setContentsMargins(2, 2, 2, 2)
            pathLE = QLineEdit(sceneDir)
            pathBrowseBtn = QPushButton('...')
            pathBrowseBtn.setFixedWidth(24)
            pathBrowseBtn.clicked.connect(lambda *args, le=pathLE: self._browseExportPath(le))
            pathLayout.addWidget(pathLE)
            pathLayout.addWidget(pathBrowseBtn)
            pathWidget.pathLE = pathLE
            self.fbxTable.setCellWidget(row, 4, pathWidget)
            
            # Col 5: Delete button
            delBtn = QPushButton('Del')
            delBtn.clicked.connect(self._deleteFbxRow)
            self.fbxTable.setCellWidget(row, 5, delBtn)

    def _browseExportPath(self, pathLE):
        path = cmds.fileDialog2(fileMode=3, caption="Select Export Folder")
        if path:
            pathLE.setText(path[0].replace('\\', '/'))

    def _deleteFbxRow(self):
        button = self.sender()
        if button:
            for r in range(self.fbxTable.rowCount()):
                if self.fbxTable.cellWidget(r, 5) == button:
                    self.fbxTable.removeRow(r)
                    break

    def _exportFbx(self):
        if not cmds.pluginInfo('fbxmaya', q=True, loaded=True):
            try:
                cmds.loadPlugin('fbxmaya')
            except Exception as e:
                QMessageBox.critical(self, 'FBX Plugin Error', 'FBX 플러그인을 로드할 수 없습니다:\n%s' % e)
                return
                
        rowCount = self.fbxTable.rowCount()
        if rowCount == 0:
            QMessageBox.information(self, 'Information', '익스포트할 항목이 없습니다. Add Selected Object(s) 버튼으로 추가하세요.')
            return
            
        move_to_origin = self.fbxMoveOriginCB.isChecked()
        bake_anim = self.fbxBakeAnimCB.isChecked()
        input_connections = self.fbxInputConnCB.isChecked()
        embed_media = self.fbxEmbedMediaCB.isChecked()
        export_only_joints = self.fbxOnlyJointsCB.isChecked()
        export_curves = self.fbxCurvesCB.isChecked()
        up_axis = self.fbxUpAxisCombo.currentText().lower()
        file_type = self.fbxFileTypeCombo.currentText()
        fbx_ver = self.fbxVersionCombo.currentText()
        
        ver_map = {
            'FBX 2020': 'FBX202000',
            'FBX 2018': 'FBX201800',
            'FBX 2016': 'FBX201600',
            'FBX 2014': 'FBX201400'
        }
        fbx_ver_str = ver_map.get(fbx_ver, 'FBX202000')
        
        try:
            mel.eval("FBXResetExport;")
            mel.eval("FBXExportScaleFactor 1;")
            mel.eval("FBXExportShapes -v true;")
            mel.eval("FBXExportSkins -v true;")
            mel.eval("FBXExportInputConnections -v %s;" % ('true' if input_connections else 'false'))
            mel.eval("FBXExportAnimationOnly -v false;")
            mel.eval('FBXExportBakeComplexAnimation -v true')
            mel.eval("FBXExportConstraints -v false;")
            mel.eval("FBXExportCameras -v true;")
            mel.eval("FBXExportLights -v false;")
            mel.eval("FBXExportEmbeddedTextures -v %s;" % ('true' if embed_media else 'false'))
            
            # Up Axis
            mel.eval("FBXExportUpAxis %s;" % up_axis)
            
            # File Type (Binary/ASCII)
            is_ascii = 1 if file_type == 'ASCII' else 0
            mel.eval("FBXExportInAscii -v %d;" % is_ascii)
            
            # FBX Version
            mel.eval("FBXExportFileVersion -v %s;" % fbx_ver_str)
            
            # Curves Exclude/Include
            mel.eval("FBXProperty Export|IncludeGrp|Geometry|NurbsCurves -v %d;" % (1 if export_curves else 0))
        except Exception as e:
            print("FBX configuration warning:", e)
            
        # Turn off viewport refresh to optimize performance
        cmds.refresh(suspend=True)
        try:
            exported_files = []
            for r in range(rowCount):
                obj_item = self.fbxTable.item(r, 0)
                if not obj_item:
                    continue
                obj = obj_item.text()
                
                if not cmds.objExists(obj):
                    cmds.warning("오브젝트가 존재하지 않습니다: %s" % obj)
                    continue
                    
                clip_le = self.fbxTable.cellWidget(r, 1)
                clip_name = clip_le.text() if clip_le else "exported_clip"
                
                start_sb = self.fbxTable.cellWidget(r, 2)
                start_val = start_sb.value() if start_sb else 1
                
                end_sb = self.fbxTable.cellWidget(r, 3)
                end_val = end_sb.value() if end_sb else 100
                
                path_widget = self.fbxTable.cellWidget(r, 4)
                path_le = getattr(path_widget, 'pathLE', None) if path_widget else None
                if not path_le:
                    path_le = path_widget.findChild(QLineEdit) if path_widget else None
                export_dir = path_le.text() if path_le else ""
                
                if not export_dir:
                    cmds.warning("경로가 비어 있습니다.")
                    continue
                    
                if not os.path.isdir(export_dir):
                    try:
                        os.makedirs(export_dir)
                    except Exception as e:
                        cmds.warning("폴더를 생성할 수 없습니다: %s\nError: %s" % (export_dir, e))
                        continue
                    
                export_path = '%s/%s.fbx' % (export_dir.rstrip('/'), clip_name)
                
                try:
                    if bake_anim:
                        mel.eval("FBXExportBakeComplexAnimation -v true;")
                        mel.eval("FBXExportBakeComplexStart -v %d;" % start_val)
                        mel.eval("FBXExportBakeComplexEnd -v %d;" % end_val)
                        mel.eval("FBXExportBakeComplexStep -v 1;")
                        mel.eval("FBXExportBakeResampleAnimation -v true;")
                    else:
                        mel.eval("FBXExportBakeComplexAnimation -v false;")
                except Exception as e:
                    print("FBX bake settings warning:", e)
                    
                cmds.select(obj, r=True)
                
                original_parent = cmds.listRelatives(obj, parent=True)
                temp_grp = None
                if move_to_origin:
                    try:
                        temp_grp = cmds.group(em=True, name="temp_fbx_origin_grp")
                        cmds.parent(obj, temp_grp)
                        pos = cmds.xform(obj, q=True, ws=True, rp=True)
                        cmds.xform(temp_grp, ws=True, t=[-pos[0], -pos[1], -pos[2]])
                    except Exception as e:
                        print("Move to origin grouping warning:", e)
                        
                export_sel = [obj]
                if export_only_joints:
                    joints = cmds.listRelatives(obj, type='joint', ad=True, fullPath=True) or []
                    if cmds.objectType(obj) == 'joint':
                        joints.append(obj)
                    if joints:
                        export_sel = joints
                    else:
                        cmds.warning("오브젝트 하위에 조인트가 존재하지 않습니다: %s" % obj)
                        
                cmds.select(export_sel, r=True)
                
                # Ensure undo is enabled
                undo_state = cmds.undoInfo(q=True, state=True)
                if not undo_state:
                    cmds.undoInfo(state=True)
                
                # Temporary timeline adjustment
                orig_min = cmds.playbackOptions(q=True, minTime=True)
                orig_max = cmds.playbackOptions(q=True, maxTime=True)
                orig_ast = cmds.playbackOptions(q=True, animationStartTime=True)
                orig_aet = cmds.playbackOptions(q=True, animationEndTime=True)
                
                changed_timeline = False
                if orig_min != start_val or orig_max != end_val:
                    cmds.playbackOptions(minTime=start_val, maxTime=end_val)
                    changed_timeline = True
                if orig_ast != start_val or orig_aet != end_val:
                    cmds.playbackOptions(animationStartTime=start_val, animationEndTime=end_val)
                    changed_timeline = True
                
                cmds.undoInfo(openChunk=True)
                try:
                    # Cut keyframes outside range to restrict export duration
                    cmds.cutKey(export_sel, time=(-999999, start_val - 1))
                    cmds.cutKey(export_sel, time=(end_val + 1, 999999))
                    
                    mel.eval('FBXExport -f "%s" -s' % export_path.replace('\\', '/'))
                    exported_files.append(export_path)
                except Exception as e:
                    cmds.error("FBX Export failed for %s:\n%s" % (obj, e))
                finally:
                    cmds.undoInfo(closeChunk=True)
                    cmds.undo()
                    if not undo_state:
                        cmds.undoInfo(state=False)
                    
                    # Restore playback options
                    if changed_timeline:
                        cmds.playbackOptions(minTime=orig_min, maxTime=orig_max)
                        cmds.playbackOptions(animationStartTime=orig_ast, animationEndTime=orig_aet)
                    
                    if temp_grp:
                        try:
                            if original_parent:
                                cmds.parent(obj, original_parent[0])
                            else:
                                cmds.parent(obj, w=True)
                            cmds.delete(temp_grp)
                        except Exception as e:
                            print("Restore grouping warning:", e)
                    try:
                        cmds.select(obj, r=True)
                    except Exception:
                        pass
        finally:
            cmds.refresh(suspend=False)
                        
        if exported_files:
            QMessageBox.information(self, 'Success', 'FBX 익스포트 완료:\n%s' % '\n'.join(exported_files))


# ═════════════════════════════════════════════════════════════════
# TAB 3: ToolBox  (원본 ztool_ToolsUI.py)
# ═════════════════════════════════════════════════════════════════

class ToolBoxTab(QWidget):
    """선택 / 컨스트레인트 / 연결 / 키프레임 도구 탭."""

    _SEL_ITEMS  = ['Polygon', 'Curves', 'Locator', 'Constraint',
                   'Hierarchy', 'HideObject', 'Joint', 'AnimObject', 'AnimNode']
    _CONS_ITEMS = ['ParentConstraint', 'PointConstraint', 'OrientConstraint',
                   'ScaleConstraint', 'AimConstraint']
    _KEY_ITEMS  = ['SetKey', 'Animated', 'Translate', 'Rotate', 'Scale',
                   'HoldCurrentKeys', 'cutKey', 'DeleteKeys']

    def __init__(self, parent=None):
        super(ToolBoxTab, self).__init__(parent)
        self._build()

    def _build(self):
        outerLayout = QVBoxLayout(self)
        outerLayout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Vertical)
        outerLayout.addWidget(splitter)

        # ── 상단 패널 ─────────────────────────────────────────────
        topWidget = QWidget()
        topScroll = QScrollArea()
        topScroll.setWidgetResizable(True)
        topScroll.setWidget(topWidget)
        topLayout = QVBoxLayout(topWidget)
        topLayout.setContentsMargins(4, 4, 4, 4)

        # ── 뷰 / 에디터 셸프 ──────────────────────────────────────
        shelfRow = QHBoxLayout()
        viewGrp  = QGroupBox('View')
        vl = QVBoxLayout(viewGrp)
        vl.setContentsMargins(2, 2, 2, 2)
        vl.addWidget(MayaShelfWidget('ztView',
                                     '%s/ztView.mel' % _SHELF_PATH))
        editorGrp = QGroupBox('Editor Windows')
        el = QVBoxLayout(editorGrp)
        el.setContentsMargins(2, 2, 2, 2)
        el.addWidget(MayaShelfWidget('ztEditorWindow',
                                     '%s/ztEditorWindow.mel' % _SHELF_PATH))
        shelfRow.addWidget(viewGrp)
        shelfRow.addWidget(editorGrp)
        topLayout.addLayout(shelfRow)

        # ── 선택 ─────────────────────────────────────────────────
        selGrp    = QGroupBox('Selection')
        selLayout = QVBoxLayout(selGrp)
        selCmds = {
            'Polygon':    lambda: _selPolyMesh('mesh'),
            'Curves':     lambda: _selPolyMesh('nurbsCurve'),
            'Locator':    lambda: _selPolyMesh('locator'),
            'Constraint': lambda: _selPolyMesh('constraint'),
            'Hierarchy':  lambda: cmds.select(r=True, hi=True),
            'HideObject': lambda: _selPolyMesh('hide'),
            'Joint':      lambda: _selPolyMesh('joint'),
            'AnimObject': lambda: _selKeyedObjs(),
            'AnimNode':   lambda: _selPolyMesh('animNode'),
        }
        row = None
        for i, name in enumerate(self._SEL_ITEMS):
            if i % 3 == 0:
                row = QHBoxLayout()
                selLayout.addLayout(row)
            btn = QPushButton(name)
            btn.clicked.connect(selCmds[name])
            row.addWidget(btn)
        topLayout.addWidget(selGrp)

        # ── 컨스트레인트 ──────────────────────────────────────────
        consGrp    = QGroupBox('Constraints')
        consLayout = QVBoxLayout(consGrp)
        offRow = QHBoxLayout()
        self.maintainOffsetCB = QCheckBox('Maintain Offset')
        self.maintainOffsetCB.setLayoutDirection(Qt.RightToLeft)
        offRow.addWidget(self.maintainOffsetCB)
        offRow.addStretch()
        consLayout.addLayout(offRow)

        chRow = QHBoxLayout()
        chRow.addWidget(QLabel('Channel:'))
        self.chCBs = {}
        for ch in ('x', 'y', 'z'):
            cb = QCheckBox(ch)
            cb.setObjectName(ch)
            cb.setChecked(True)
            cb.setLayoutDirection(Qt.RightToLeft)
            self.chCBs[ch] = cb
            chRow.addWidget(cb)
        chRow.addStretch()
        consLayout.addLayout(chRow)

        consMethods = {
            'ParentConstraint': self._parentconstraint,
            'PointConstraint':  self._pointconstraint,
            'OrientConstraint': self._orientconstraint,
            'ScaleConstraint':  self._scaleconstraint,
            'AimConstraint':    self._aimconstraint,
        }
        row = None
        for i, name in enumerate(self._CONS_ITEMS):
            if i % 3 == 0:
                row = QHBoxLayout()
                consLayout.addLayout(row)
            btn = QPushButton(name)
            btn.clicked.connect(consMethods[name])
            row.addWidget(btn)
        topLayout.addWidget(consGrp)

        # ── 어트리뷰트 직접 연결 ──────────────────────────────────
        attrConnGrp    = QGroupBox('Attribute Connect (Select: src → trg)')
        attrConnLayout = QVBoxLayout(attrConnGrp)
        transRow = QHBoxLayout()
        transRow.addWidget(QLabel('Connect:'))
        self.transCBs = {}
        for t in ('translate', 'rotate', 'scale'):
            cb = QCheckBox(t)
            cb.setObjectName(t)
            cb.setChecked(True)
            cb.setLayoutDirection(Qt.RightToLeft)
            self.transCBs[t] = cb
            transRow.addWidget(cb)
        attrConnLayout.addLayout(transRow)
        connectAttrBtn = QPushButton('Connect Selected → Selected')
        connectAttrBtn.clicked.connect(self._connectAttrsFromSel)
        attrConnLayout.addWidget(connectAttrBtn)
        topLayout.addWidget(attrConnGrp)
        topLayout.addStretch()

        splitter.addWidget(topScroll)

        # ── 하단 패널 ─────────────────────────────────────────────
        botWidget = QWidget()
        botScroll = QScrollArea()
        botScroll.setWidgetResizable(True)
        botScroll.setWidget(botWidget)
        botLayout = QVBoxLayout(botWidget)
        botLayout.setContentsMargins(4, 4, 4, 4)

        # ── 채널박스 기반 연결 (Connection Box) ───────────────────
        connGrp    = QGroupBox('Channel Box Connection')
        connLayout = QVBoxLayout(connGrp)

        listSplitter = QSplitter(Qt.Horizontal)

        srcWidget = QWidget()
        srcCol = QVBoxLayout(srcWidget)
        srcCol.setContentsMargins(0, 0, 0, 0)
        self.srcCountLbl = QLabel('0')
        self.srcWidget   = QListWidget()
        self.srcWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.srcWidget.setFocusPolicy(Qt.NoFocus)
        self.srcWidget.itemSelectionChanged.connect(
            lambda: self.srcCountLbl.setText(str(len(self.srcWidget.selectedItems()))))
        srcBtns = QHBoxLayout()
        srcAddBtn = QPushButton('Add Src')
        srcRemBtn = QPushButton('Remove')
        srcClsBtn = QPushButton('Clear')
        srcAddBtn.clicked.connect(
            lambda: self.srcWidget.addItems(_getObjAttrs() or []))
        srcRemBtn.clicked.connect(lambda: _removeItems(self.srcWidget))
        srcClsBtn.clicked.connect(self.srcWidget.clear)
        srcBtns.addWidget(srcAddBtn); srcBtns.addWidget(srcRemBtn); srcBtns.addWidget(srcClsBtn)
        srcCol.addWidget(self.srcCountLbl)
        srcCol.addWidget(self.srcWidget)
        srcCol.addLayout(srcBtns)

        trgWidget = QWidget()
        trgCol = QVBoxLayout(trgWidget)
        trgCol.setContentsMargins(0, 0, 0, 0)
        self.trgCountLbl = QLabel('0')
        self.trgWidget   = QListWidget()
        self.trgWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.trgWidget.setFocusPolicy(Qt.NoFocus)
        self.trgWidget.itemSelectionChanged.connect(
            lambda: self.trgCountLbl.setText(str(len(self.trgWidget.selectedItems()))))
        trgBtns = QHBoxLayout()
        trgAddBtn = QPushButton('Add Trg')
        trgRemBtn = QPushButton('Remove')
        trgClsBtn = QPushButton('Clear')
        trgAddBtn.clicked.connect(
            lambda: self.trgWidget.addItems(_getObjAttrs() or []))
        trgRemBtn.clicked.connect(lambda: _removeItems(self.trgWidget))
        trgClsBtn.clicked.connect(self.trgWidget.clear)
        trgBtns.addWidget(trgAddBtn); trgBtns.addWidget(trgRemBtn); trgBtns.addWidget(trgClsBtn)
        trgCol.addWidget(self.trgCountLbl)
        trgCol.addWidget(self.trgWidget)
        trgCol.addLayout(trgBtns)

        listSplitter.addWidget(srcWidget)
        listSplitter.addWidget(trgWidget)
        listSplitter.setStretchFactor(0, 1)
        listSplitter.setStretchFactor(1, 1)
        connLayout.addWidget(listSplitter)

        optRow = QHBoxLayout()
        self.oneByOneCB = QCheckBox('1:1')
        self.mulDivCB   = QCheckBox('Multiply-Divide')
        self.addSubCB   = QCheckBox('Add-Subtract')
        optRow.addWidget(self.oneByOneCB)
        optRow.addWidget(self.mulDivCB)
        optRow.addWidget(self.addSubCB)
        connLayout.addLayout(optRow)

        connBtnRow       = QHBoxLayout()
        self.connectBtn  = QPushButton('<== Connect ==>')
        self.drvKeyBtn   = QPushButton('SetDrivenKey ==>')
        connBtnRow.addWidget(self.connectBtn)
        connBtnRow.addWidget(self.drvKeyBtn)
        connLayout.addLayout(connBtnRow)

        self.oneByOneCB.stateChanged.connect(self._updateConnectMode)
        self._updateConnectMode()
        self.drvKeyBtn.clicked.connect(
            lambda: _setDrivenKey(
                self.srcWidget.selectedItems()[0].text(),
                [i.text() for i in self.trgWidget.selectedItems()]
            ) if self.srcWidget.selectedItems() else None)
        botLayout.addWidget(connGrp)

        # ── 키프레임 ─────────────────────────────────────────────
        keyGrp    = QGroupBox('Keyframe')
        keyLayout = QVBoxLayout(keyGrp)
        keyCmds = {
            'SetKey':          lambda: cmds.SetKey(),
            'Animated':        lambda: cmds.SetKeyAnimated(),
            'Translate':       lambda: cmds.SetKeyTranslate(),
            'Rotate':          lambda: cmds.SetKeyRotate(),
            'Scale':           lambda: cmds.SetKeyScale(),
            'HoldCurrentKeys': lambda: cmds.HoldCurrentKeys(),
            'cutKey':          lambda: cmds.cutKey(
                t=(cmds.currentTime(q=True), cmds.currentTime(q=True))),
            'DeleteKeys':      lambda: cmds.DeleteKeys(),
        }
        row = None
        for i, name in enumerate(self._KEY_ITEMS):
            if i % 3 == 0:
                row = QHBoxLayout()
                keyLayout.addLayout(row)
            btn = QPushButton(name)
            btn.clicked.connect(keyCmds[name])
            row.addWidget(btn)
        botLayout.addWidget(keyGrp)

        # ── Attribute Manager ─────────────────────────────────────
        attrMgrGrp = QGroupBox('Attribute Manager')
        attrMgrLayout = QHBoxLayout(attrMgrGrp)
        attrMgrBtn = QPushButton('Attribute Manager')
        attrMgrBtn.setToolTip('어트리뷰트 추가/재정렬 (tak_attrManager — CGM 필요)')
        attrMgrBtn.clicked.connect(self._launchAttrManager)
        attrMgrLayout.addWidget(attrMgrBtn)
        botLayout.addWidget(attrMgrGrp)
        botLayout.addStretch()

        splitter.addWidget(botScroll)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

    # ── 컨스트레인트 헬퍼 ─────────────────────────────────────────
    def _skipAxes(self):
        return [ch for ch, cb in self.chCBs.items() if not cb.isChecked()] or 'none'

    def _offset(self):
        return self.maintainOffsetCB.isChecked()

    def _parentconstraint(self):
        objs = cmds.ls(sl=True)
        for i, obj in enumerate(objs[1:], 1):
            cmds.parentConstraint(objs[0], obj, mo=self._offset())

    def _pointconstraint(self):
        skip = self._skipAxes()
        objs = cmds.ls(sl=True)
        for obj in objs[1:]:
            cmds.pointConstraint(objs[0], obj, mo=self._offset(), skip=skip)

    def _orientconstraint(self):
        skip = self._skipAxes()
        objs = cmds.ls(sl=True)
        for obj in objs[1:]:
            cmds.orientConstraint(objs[0], obj, mo=self._offset(), skip=skip)

    def _scaleconstraint(self):
        skip = self._skipAxes()
        objs = cmds.ls(sl=True)
        for obj in objs[1:]:
            cmds.scaleConstraint(objs[0], obj, mo=self._offset(), skip=skip)

    def _aimconstraint(self):
        skip = self._skipAxes()
        objs = cmds.ls(sl=True)
        for obj in objs[1:]:
            cmds.aimConstraint(objs[0], obj, mo=self._offset(), skip=skip)

    def _connectAttrsFromSel(self):
        axes   = [ch for ch, cb in self.chCBs.items()    if cb.isChecked()]
        trans  = [t  for t,  cb in self.transCBs.items() if cb.isChecked()]
        sel    = cmds.ls(sl=True)
        if len(sel) < 2:
            return
        src, trg = sel[0], sel[1]
        cmds.undoInfo(ock=True)
        for t in trans:
            for ax in axes:
                cmds.connectAttr('%s.%s%s' % (src, t, ax.upper()),
                                 '%s.%s%s' % (trg, t, ax.upper()), f=True)
        cmds.undoInfo(cck=True)

    def _updateConnectMode(self):
        try:
            self.connectBtn.clicked.disconnect()
        except RuntimeError:
            pass
        if self.oneByOneCB.isChecked():
            self.connectBtn.clicked.connect(
                lambda: _multiConnectAttrs(
                    [i.text() for i in self.srcWidget.selectedItems()],
                    [i.text() for i in self.trgWidget.selectedItems()]))
        else:
            self.connectBtn.clicked.connect(
                lambda: _connectAttrs(
                    self.srcWidget.selectedItems()[0].text(),
                    [i.text() for i in self.trgWidget.selectedItems()]
                ) if self.srcWidget.selectedItems() else None)

    def _launchAttrManager(self):
        try:
            from ztLib.ztRig import tak_attrManager
            reload(tak_attrManager)
            tak_attrManager.ui()
        except ImportError as e:
            QMessageBox.warning(
                self, 'Dependency Missing',
                'Attribute Manager는 CGM Toolbox가 필요합니다.\n'
                '경로: ztLib/ztRig/cgmtools/mayaTools\n\nError: %s' % e)
        except Exception as e:
            QMessageBox.critical(self, 'Error', 'Attribute Manager 실행 실패:\n%s' % e)


# ═════════════════════════════════════════════════════════════════
# TAB 4: Scene Cleanup  (원본 ztMisc/ztSceneCleanup.py)
# ═════════════════════════════════════════════════════════════════

class SceneTab(QWidget):
    """씬 정리 및 Vaccine 악성코드 제거 탭."""

    def __init__(self, parent=None):
        super(SceneTab, self).__init__(parent)
        self._build()

    def _build(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(4, 4, 4, 4)

        # ── Vaccine / 악성코드 ────────────────────────────────────
        malGrp    = QGroupBox('Maya Vaccine / Malware Cleanup')
        malLayout = QVBoxLayout(malGrp)
        self.malLog = QTextEdit()
        self.malLog.setReadOnly(True)
        self.malLog.setMaximumHeight(130)
        malLayout.addWidget(self.malLog)
        btnRow   = QHBoxLayout()
        checkBtn = QPushButton('Check Scene')
        checkBtn.clicked.connect(self._checkMalware)
        fixBtn   = QPushButton('Fix All')
        fixBtn.clicked.connect(self._fixAll)
        btnRow.addWidget(checkBtn)
        btnRow.addWidget(fixBtn)
        malLayout.addLayout(btnRow)
        mainLayout.addWidget(malGrp)

        # ── 알 수 없는 플러그인 / 노드 ────────────────────────────
        unkGrp    = QGroupBox('Unknown Plugins & Nodes')
        unkLayout = QVBoxLayout(unkGrp)
        self.pluginList = QListWidget()
        self.pluginList.setMaximumHeight(100)
        unkLayout.addWidget(self.pluginList)
        plugBtnRow      = QHBoxLayout()
        refreshPlugBtn  = QPushButton('Refresh')
        removePlugBtn   = QPushButton('Remove Selected')
        removeAllBtn    = QPushButton('Remove All Unknown Plugins')
        removeNodeBtn   = QPushButton('Remove Unknown Type Nodes')
        refreshPlugBtn.clicked.connect(self._refreshPlugins)
        removePlugBtn.clicked.connect(self._removeSelectedPlugin)
        removeAllBtn.clicked.connect(self._removeAllPlugins)
        removeNodeBtn.clicked.connect(self._removeUnknownNodes)
        plugBtnRow.addWidget(refreshPlugBtn)
        plugBtnRow.addWidget(removePlugBtn)
        plugBtnRow.addWidget(removeAllBtn)
        unkLayout.addLayout(plugBtnRow)
        unkLayout.addWidget(removeNodeBtn)
        mainLayout.addWidget(unkGrp)

        mainLayout.addStretch()

    def _log(self, msg):
        self.malLog.append(msg)

    def _checkMalware(self):
        self.malLog.clear()
        userSetups, status, malType = ztSceneCleanup.test_ConcreteScriptFiles()
        nodes = ztSceneCleanup.test_scriptNodes()
        jobs  = ztSceneCleanup.test_scriptJob()

        if status:
            self._log('[!] userSetup 상태: %s' % status)
            for f in userSetups:
                self._log('    파일: %s' % f)
        else:
            self._log('[OK] userSetup: 정상')

        if nodes:
            self._log('[!] 악성 scriptNode 발견: %s' % nodes)
        else:
            self._log('[OK] scriptNodes: 정상')

        if jobs:
            self._log('[!] 악성 scriptJob 발견: %s' % jobs)
        else:
            self._log('[OK] scriptJobs: 정상')

    def _fixAll(self):
        self.malLog.clear()
        f, fx, mt = ztSceneCleanup.fix_userSetup()
        self._log('userSetup   → found:%s  fixed:%s  type:%s' % (f, fx, mt))
        f, fx = ztSceneCleanup.fix_scriptNodes()
        self._log('scriptNodes → found:%s  fixed:%s' % (f, fx))
        f, fx = ztSceneCleanup.fix_scriptJob()
        self._log('scriptJobs  → found:%s  fixed:%s' % (f, fx))
        ztSceneCleanup.removeAllUnknownPlugins()
        self._log('Unknown plugins 제거 완료.')
        self._refreshPlugins()

    def _refreshPlugins(self):
        self.pluginList.clear()
        plugins = ztSceneCleanup.getUnknownPlugins() or []
        self.pluginList.addItems(plugins)

    def _removeSelectedPlugin(self):
        for item in self.pluginList.selectedItems():
            try:
                ztSceneCleanup.removeUnknownPlugins(item.text())
                self.pluginList.takeItem(self.pluginList.row(item))
            except Exception as e:
                print('Plugin remove error:', e)

    def _removeAllPlugins(self):
        ztSceneCleanup.removeAllUnknownPlugins()
        self._refreshPlugins()

    def _removeUnknownNodes(self):
        ztSceneCleanup.removeUnknownTypeNode()
        cmds.confirmDialog(m='Unknown type nodes 제거 완료. (Script Editor 확인)')


# ═════════════════════════════════════════════════════════════════
# TAB 5: Light
# ═════════════════════════════════════════════════════════════════

class LightTab(QWidget):
    """라이팅 도구 탭 (확장 예정)."""

    def __init__(self, parent=None):
        super(LightTab, self).__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        lbl = QLabel('Lighting tools\n— 추후 확장 예정 —')
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        layout.addStretch()


# ═════════════════════════════════════════════════════════════════
# TAB 6: XGen Manager
# ═════════════════════════════════════════════════════════════════

class XGenTab(QWidget):
    """XGen 관리 탭 (xgenm 모듈이 없는 환경에서는 메시지 표시)."""

    def __init__(self, parent=None):
        super(XGenTab, self).__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        if not _XGEN_AVAILABLE:
            lbl = QLabel('XGen을 사용할 수 없는 Maya 세션입니다.')
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)
            layout.addStretch()
            return
        try:
            from ztLib.ztFX.ztXgenManager import xgenManager
            self._mgr = xgenManager(parent=self)
            layout.addWidget(self._mgr)
        except Exception as e:
            layout.addWidget(QLabel('XGen Manager 로드 실패:\n%s' % e))
            layout.addStretch()


# ═════════════════════════════════════════════════════════════════
# 셸프 관리 다이얼로그
# ═════════════════════════════════════════════════════════════════

class ShelfManagerDialog(QDialog):
    """e:/rigScript/shelves/ 의 zt* 셸프 파일을 관리하는 다이얼로그."""

    def __init__(self, parent=None):
        super(ShelfManagerDialog, self).__init__(parent)
        self.setWindowTitle('Shelf Manager')
        self.resize(420, 320)
        self._build()
        self._refresh()

    def _build(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel('셸프 파일 목록  (%s)' % _SHELF_PATH))

        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self.listWidget)

        btnRow   = QHBoxLayout()
        loadBtn  = QPushButton('Maya에 로드')
        saveBtn  = QPushButton('선택 저장')
        openBtn  = QPushButton('폴더 열기')
        loadBtn.setToolTip('선택한 셸프를 Maya에 소스로 불러옵니다')
        saveBtn.setToolTip('선택한 셸프를 현재 Maya 셸프 상태로 저장합니다')
        loadBtn.clicked.connect(self._loadShelves)
        saveBtn.clicked.connect(self._saveShelves)
        openBtn.clicked.connect(lambda: os.startfile(_SHELF_PATH.replace('/', '\\')))
        btnRow.addWidget(loadBtn)
        btnRow.addWidget(saveBtn)
        btnRow.addWidget(openBtn)
        layout.addLayout(btnRow)

    def _refresh(self):
        self.listWidget.clear()
        if os.path.isdir(_SHELF_PATH):
            files = sorted(f for f in os.listdir(_SHELF_PATH)
                           if f.endswith('.mel'))
            for f in files:
                name = os.path.splitext(f)[0]
                item = QListWidgetItem(name)
                # Maya에 이미 로드된 셸프는 파란색으로 표시
                try:
                    loaded = cmds.shelfLayout(name, exists=True)
                    if loaded:
                        item.setForeground(QColor('#80c8ff'))
                except Exception:
                    pass
                self.listWidget.addItem(item)

    def _loadShelves(self):
        items = self.listWidget.selectedItems()
        if not items:
            QMessageBox.information(self, '안내', '로드할 셸프를 선택하세요.')
            return
        for item in items:
            name = item.text()
            path = '%s/%s.mel' % (_SHELF_PATH, name)
            try:
                mel.eval('loadNewShelf "%s"' % path)
                print('Shelf loaded: %s' % name)
            except Exception as e:
                QMessageBox.warning(self, '로드 실패', '%s:\n%s' % (name, e))
        self._refresh()

    def _saveShelves(self):
        items = self.listWidget.selectedItems()
        if not items:
            QMessageBox.information(self, '안내', '저장할 셸프를 선택하세요.')
            return
        for item in items:
            name = item.text()
            path = os.path.splitext('%s/%s.mel' % (_SHELF_PATH, name))[0]
            try:
                cmds.saveShelf(name, path)
                print('Shelf saved: %s' % path)
            except Exception as e:
                QMessageBox.warning(self, '저장 실패', '%s:\n%s' % (name, e))
        self._refresh()


# ═════════════════════════════════════════════════════════════════
# 메인 윈도우  ZTMainTool
# ═════════════════════════════════════════════════════════════════

class ZTMainTool(MayaQWidgetDockableMixin, QMainWindow):
    """ZT Tool Suite 통합 메인 윈도우."""

    def __init__(self, parent=None):
        super(ZTMainTool, self).__init__(parent)
        self.setWindowTitle('ZT Tool Suite')
        self.setObjectName(_WINDOW_NAME)
        self.resize(530, 740)
        self.setStyleSheet(_DARK_STYLE)
        self._build()
        self._buildMenuBar()
        
        # Ctrl+휠 폰트 스케일 필터
        self._wheelFilter = WheelScaleFilter(self)
        self._wheelFilter._applyScale()

        # Ctrl+0 → 폰트 크기 초기화
        resetShortcut = QShortcut(QKeySequence('Ctrl+0'), self)
        resetShortcut.activated.connect(self._resetFontSize)

    def _resetFontSize(self):
        self.setStyleSheet(_DARK_STYLE)
        self.setWindowTitle('ZT Tool Suite')
        self._wheelFilter._fontSize = 20
        self._updateFontSizeMenuCheck(20)

    def _build(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)
        mainLayout.setContentsMargins(4, 4, 4, 4)

        self.tabs = QTabWidget()
        mainLayout.addWidget(self.tabs)

        self._rigTab     = RigTab()
        self._aniTab     = AniTab()
        self._toolBoxTab = ToolBoxTab()
        self._sceneTab   = SceneTab()
        self._lightTab   = LightTab()
        self._xgenTab    = XGenTab()

        self.tabs.addTab(self._rigTab,     'Rig')
        self.tabs.addTab(self._aniTab,     'Animation')
        self.tabs.addTab(self._toolBoxTab, 'ToolBox')
        self.tabs.addTab(self._sceneTab,   'Scene')
        self.tabs.addTab(self._lightTab,   'Light')
        self.tabs.addTab(self._xgenTab,    'XGen')

    def _buildMenuBar(self):
        menubar = self.menuBar()

        # ── File ──────────────────────────────────────────────────
        fileMenu = menubar.addMenu('File')
        saveShelvesAct = QAction('Save All Shelves', self)
        saveShelvesAct.triggered.connect(self._saveAllShelves)
        shelfMgrAct    = QAction('Shelf Manager...', self)
        shelfMgrAct.triggered.connect(self._openShelfManager)
        fileMenu.addAction(saveShelvesAct)
        fileMenu.addAction(shelfMgrAct)

        # ── View ──────────────────────────────────────────────────
        viewMenu = menubar.addMenu('View')
        fontSizeMenu = viewMenu.addMenu('Font Size')
        
        self.fontSizeGroup = QActionGroup(self)
        for size in range(9, 21):
            act = QAction('%d px' % size, self, checkable=True)
            act.setData(size)
            act.triggered.connect(self._changeFontSizeFromMenu)
            fontSizeMenu.addAction(act)
            self.fontSizeGroup.addAction(act)
            
        resetFontAct = QAction('Reset (Ctrl+0)', self)
        resetFontAct.triggered.connect(self._resetFontSize)
        viewMenu.addAction(resetFontAct)

        # ── Scene ─────────────────────────────────────────────────
        sceneMenu = menubar.addMenu('Scene')
        checkAct = QAction('Check Malware', self)
        checkAct.triggered.connect(lambda: (
            self.tabs.setCurrentWidget(self._sceneTab),
            self._sceneTab._checkMalware()))
        fixAct   = QAction('Fix All (Vaccine)', self)
        fixAct.triggered.connect(lambda: (
            self.tabs.setCurrentWidget(self._sceneTab),
            self._sceneTab._fixAll()))
        sceneMenu.addAction(checkAct)
        sceneMenu.addAction(fixAct)

    def _changeFontSizeFromMenu(self):
        act = self.sender()
        if act:
            size = act.data()
            self._wheelFilter._fontSize = size
            self._wheelFilter._applyScale()

    def _updateFontSizeMenuCheck(self, size):
        if hasattr(self, 'fontSizeGroup'):
            for act in self.fontSizeGroup.actions():
                if act.data() == size:
                    act.setChecked(True)
                    break

    def _saveAllShelves(self):
        for f in os.listdir(_SHELF_PATH):
            name = os.path.splitext(f)[0]
            path = os.path.join(_SHELF_PATH, f)
            if os.path.splitext(f)[1] == '.mel':
                try:
                    cmds.saveShelf(name, os.path.splitext(path)[0])
                    print('Saved: %s' % name)
                except Exception as e:
                    print('Skip %s: %s' % (name, e))

    def _openShelfManager(self):
        dlg = ShelfManagerDialog(parent=self)
        dlg.exec_()

    def showEvent(self, event):
        super(ZTMainTool, self).showEvent(event)
        # ScriptJob은 창 오브젝트 이름을 부모로 등록
        self._aniTab.startScriptJob(self.objectName())


# ═════════════════════════════════════════════════════════════════
# 진입점
# ═════════════════════════════════════════════════════════════════

def reload_all():
    """ZT Tool Suite의 모든 서브모듈을 reload한 후 창을 다시 엽니다."""
    import importlib, sys

    _prefixes = ('ztLib.', 'ztTool',)

    # 1) 현재 창 닫기
    if cmds.window(_WINDOW_NAME, exists=True):
        cmds.deleteUI(_WINDOW_NAME, wnd=True)

    # 2) ztLib 하위 모듈 전부 reload
    mods = [m for name, m in sorted(sys.modules.items())
            if any(name == p or name.startswith(p) for p in _prefixes)]
    for mod in mods:
        try:
            importlib.reload(mod)
            print('reloaded:', mod.__name__)
        except Exception as e:
            print('reload skip:', getattr(mod, '__name__', mod), '—', e)

    # 3) ztTool 자신 reload 후 main() 실행
    import ztTool
    importlib.reload(ztTool)
    ztTool.main()


def main():
    """ZT Tool Suite를 실행합니다.

    사용법:
        import ztTool
        ztTool.main()

    전체 reload 후 실행:
        import ztTool
        ztTool.reload_all()
    """
    if cmds.window(_WINDOW_NAME, exists=True):
        cmds.deleteUI(_WINDOW_NAME, wnd=True)
    win = ZTMainTool(maya_main_window())
    win.show()
