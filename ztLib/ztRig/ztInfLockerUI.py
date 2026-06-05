import maya.cmds as cmds
from importlib import reload
from . import ztRigUtil
reload(ztRigUtil)

# Tracks joint names currently shown in the list
_current_joints = []


def _toUiName(name):
    """Convert joint name to a safe Maya UI element name."""
    return name.replace(':', '__').replace('|', '_')


def _getShape(transform):
    """Get the first shape node name from a transform. Returns None if not found."""
    shapes = cmds.listRelatives(transform, shapes=True, fullPath=False) or []
    return shapes[0] if shapes else None


def _getMeshFromField():
    """Return the transform name currently in the object text field."""
    return cmds.textFieldButtonGrp('meshNameTxField', q=True, tx=True).strip()


class _JointRow(object):
    """One row in the joint list: [joint button] [ ] [locked/unlocked text]"""
    def __init__(self, jntName, transform, parent):
        self.jntName   = jntName
        self.transform = transform
        self.uiName    = _toUiName(jntName)

        shape = _getShape(transform)
        locked = ztRigUtil.getLockState(shape, jntName) if shape else False

        cmds.rowLayout('%s_Row' % self.uiName, nc=3, adj=1,
                       cl3=('left', 'left', 'right'),
                       cw3=(200, 4, 60), parent=parent)
        cmds.button('%s_Btn' % self.uiName, l=jntName, c=self._toggle)
        cmds.text(' ')
        cmds.text('%s_Tx' % self.uiName,
                  l='locked' if locked else 'unlocked',
                  w=60, al='center')
        cmds.setParent('..')
        self._applyColor(locked)

    def _applyColor(self, locked):
        color = (1, 0.3, 0.3) if locked else (0.3, 1, 0.3)
        cmds.button('%s_Btn' % self.uiName, e=True, bgc=color)

    def _toggle(self, *args):
        transform = _getMeshFromField()
        shape = _getShape(transform) if transform else None
        if not shape:
            cmds.warning('infLocker: 오브젝트 정보를 찾을 수 없습니다.')
            return
        locked = ztRigUtil.getLockState(shape, self.jntName)
        if locked:
            ztRigUtil.unlockInf(shape, self.jntName)
            cmds.text('%s_Tx' % self.uiName, e=True, l='unlocked')
        else:
            ztRigUtil.lockInf(shape, self.jntName)
            cmds.text('%s_Tx' % self.uiName, e=True, l='locked')
        self._applyColor(not locked)


def _addJoints(*args):
    global _current_joints
    transform = _getMeshFromField()
    if not transform:
        cmds.warning('infLocker: 오브젝트 필드가 비어있습니다. << 버튼으로 메시를 선택하세요.')
        return
    shape = _getShape(transform)
    if not shape:
        cmds.warning('infLocker: "%s" 의 Shape를 찾을 수 없습니다.' % transform)
        return
    sc = ztRigUtil.getSkinClusterFromMesh(shape)
    if not sc:
        cmds.warning('infLocker: "%s" 에 SkinCluster가 없습니다. 먼저 스킨 바인딩을 해주세요.' % transform)
        return

    sel = cmds.ls(sl=True, type='joint')
    if not sel:
        cmds.warning('infLocker: 조인트를 선택한 후 Get Joints를 눌러주세요.')
        return

    scInfluences = ztRigUtil.skinJntLstFromSkinCluster(sc) or []
    for jnt in sel:
        if jnt in _current_joints:
            continue
        if jnt not in scInfluences:
            cmds.warning('infLocker: "%s" 은 "%s" 의 인플루언스가 아닙니다.' % (jnt, transform))
            continue
        _current_joints.append(jnt)
        _JointRow(jnt, transform, 'jntScrollLayout')


def _clearLayout(*args):
    global _current_joints
    _current_joints = []
    children = cmds.scrollLayout('jntScrollLayout', q=True, ca=True) or []
    for c in children:
        cmds.deleteUI(c)


def _lockAll(*args):
    _setAllLock(locked=True)


def _unlockAll(*args):
    _setAllLock(locked=False)


def _setAllLock(locked):
    global _current_joints
    transform = _getMeshFromField()
    shape = _getShape(transform) if transform else None
    if not shape:
        cmds.warning('infLocker: 오브젝트 정보를 찾을 수 없습니다.')
        return
    sc = ztRigUtil.getSkinClusterFromMesh(shape)
    if not sc:
        return
    for jnt in _current_joints:
        uiName = _toUiName(jnt)
        if locked:
            ztRigUtil.lockInf(shape, jnt)
            label = 'locked'
            color = (1, 0.3, 0.3)
        else:
            ztRigUtil.unlockInf(shape, jnt)
            label = 'unlocked'
            color = (0.3, 1, 0.3)
        if cmds.text('%s_Tx' % uiName, ex=True):
            cmds.text('%s_Tx' % uiName, e=True, l=label)
        if cmds.button('%s_Btn' % uiName, ex=True):
            cmds.button('%s_Btn' % uiName, e=True, bgc=color)


def _setMeshFromSel(*args):
    sel = cmds.ls(sl=True)
    if not sel:
        cmds.warning('infLocker: 메시를 선택해주세요.')
        return
    obj = sel[0]
    # Accept transform or shape — always store transform
    if cmds.objectType(obj) in ('mesh', 'nurbsSurface'):
        parents = cmds.listRelatives(obj, parent=True, fullPath=False)
        obj = parents[0] if parents else obj
    cmds.textFieldButtonGrp('meshNameTxField', e=True, tx=obj)


def main(*args):
    global _current_joints
    _current_joints = []

    winName = 'infLockerWin'
    if cmds.window(winName, ex=True):
        cmds.deleteUI(winName)

    cmds.window(winName, title='Inf Locker', wh=(340, 500), sizeable=True)
    cmds.columnLayout(adj=True)

    # ── Object field ──────────────────────────────────────
    cmds.frameLayout(l='Object', mh=4, mw=4, bgs=True, cll=False)
    cmds.textFieldButtonGrp('meshNameTxField', ed=False, bl='  <<  ',
                            bc=_setMeshFromSel, tcc=lambda *a: None,
                            adj=2, cw=(2, 50))
    cmds.setParent('..')  # frameLayout

    # ── Lock / Unlock all ─────────────────────────────────
    cmds.rowLayout(nc=2, adj=1, cw2=(170, 170))
    cmds.button(l='Lock All',   h=28, bgc=(0.8, 0.3, 0.3), c=_lockAll)
    cmds.button(l='Unlock All', h=28, bgc=(0.3, 0.8, 0.3), c=_unlockAll)
    cmds.setParent('..')

    # ── Joint list ────────────────────────────────────────
    cmds.frameLayout(l='Joint List', mh=4, mw=4, bgs=True, cll=False)
    cmds.scrollLayout('jntScrollLayout', cr=True, h=340)
    cmds.setParent('..')  # scrollLayout
    cmds.setParent('..')  # frameLayout

    cmds.separator(style='in', h=8)

    # ── Bottom buttons ────────────────────────────────────
    cmds.rowLayout(nc=2, adj=1, cw2=(170, 170))
    cmds.button(l='Get Joints', h=30, c=_addJoints)
    cmds.button(l='Clear',      h=30, c=_clearLayout)
    cmds.setParent('..')

    cmds.setParent('..')  # columnLayout
    cmds.showWindow(winName)
