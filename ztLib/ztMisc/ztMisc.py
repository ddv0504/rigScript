# -*- coding: utf-8 -*-
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import maya.cmds as cmds
from maya import mel
from math import pow,sqrt,degrees
import pymel.core as pm
def distanceFromCam(obj,*args):
    # Get current active camera
    view = omui.M3dView.active3dView()
    cam = om.MDagPath()
    view.getCamera(cam)

    # Get the parent of the camera shape
    getCamera = cmds.listRelatives(cam.fullPathName(), p=True)

    # Wodlspace xform of the camera
    camXForm = cmds.xform(getCamera[0], q=True, t=True, ws=True)

    # Worldspace xform of the selected object
    objXform = cmds.xform(obj, q=True, t=True, ws=True)

    # Distance formula : √((x2 - x1)2 + (y2 - y1)2 + (z2 - z1)2)
    distance = sqrt(pow(camXForm[0]-objXform[0],2)+pow(camXForm[1]-objXform[1],2)+pow(camXForm[2]-objXform[2],2))

    return distance


def getFaceCenter(face,rot=False):
    obj = cmds.ls(sl=True)
    cmds.select(face,r=True)
    mel.eval('TranslateToolWithSnapMarkingMenu;')
    cmds.manipMoveContext('Move',e=True,mode=10,ah=3)
    pos = cmds.manipMoveContext('Move',mode=2,q=True,p=True)
    deg = [degrees(i) for i in cmds.manipMoveContext('Move',mode=2,q=True,oa=True)]
    cmds.select(obj,r=True)
    mel.eval('MarkingMenuPopDown;')
    if rot:
        return pos,deg
    return pos
    
def face_normal(face):
    vtxface = cmds.polyListComponentConversion(face, tvf = True)
    xes = cmds.polyNormalPerVertex(vtxface, q=True, x =True)
    yes = cmds.polyNormalPerVertex(vtxface, q=True, y =True)
    zes = cmds.polyNormalPerVertex(vtxface, q=True, z =True)
    divisor = 1.0 / len(xes)
    return sum(xes)* divisor, sum(yes)  * divisor, sum(zes) * divisor
    
    
def TransSkinWeights(*args):
    selList = mel.eval('string $selList[] = `ls -sl`;')
    src = mel.eval('string $source = $selList[0];')
    trgs = selList[1:]

    for trg in trgs:
        # get the source's shape
        srcShape = cmds.listRelatives(src, c=True, s=True)[0]
        # get skin cluster of the source
        skClu = mel.eval('findRelatedSkinCluster($source);')
        jnts = cmds.skinCluster(skClu, q=True, inf=True)
        # get the target shape
        trgShape = cmds.listRelatives(trg, c=True, s=True, path=True)[0]
        # bind target shape with joints of the source
        desSkClu = cmds.skinCluster(jnts, trgShape, mi=3, dr=4.5, tsb=True, omi=False, nw=1)[0]
        # copy skin weights from the source to the target
        cmds.copySkinWeights(ss=skClu, ds=desSkClu, sa='closestPoint', ia='oneToOne', nm=True)
        print('Skin weights transfered from %s to %s.' % (src, trg))
    print('#' * 50)
    print('Transfer skin weights job is done.')
    print('#' * 50)
    cmds.select(selList)

def makeDisplayLayer(objs,layerName):
    if not cmds.objExists(layerName):
        cmds.createDisplayLayer(name=layerName, number=1, nr=True)
    cmds.editDisplayLayerMembers(layerName,objs,noRecurse=True)
    return layerName

def importImagePlane(*args):
    img = cmds.fileDialog2(fm=1,ds=2,ff='Image Files (*.jpg *.png *.bmp *.tga *.tif *.tiff *.tga *.gif *.hdr *.psd *.exr *.iff *.jpeg *.jpe *.jif *.jfif *.jfi *.jp2 *.j2k *.jpf *.jpx *.jpm *.mj2);;All Files (*.*)')
    if not img:
        return
    img = img[0]
    imgName = img.split('/')[-1].split('.')[0]
    cmds.createNode('imagePlane',n=imgName)
    cmds.setAttr(imgName+'.imageName',img,type='string')
    if cmds.listRelatives(imgName,p=True):
        transformNode = cmds.listRelatives(imgName,p=True)[0]
        # rename the imagePlane transform node
        transformNode = cmds.rename(transformNode,imgName+'_transform')
    return transformNode,imgName

def linkImageToCam(cam,img):
    # Get the camera's shape
    camShape = cmds.listRelatives(cam, c=True, s=True)[0]
    # Link the image to the camera
    cmds.connectAttr(img+'.message', camShape+'.imagePlane[0]', f=True)
    print('Image linked to the camera.')
    return img

# import image and link it to the camera
def importImagePlaneToCam(cam,img=None,*args):
    if not img:
        transform,img = importImagePlane()
    if not img:
        return
    linkImageToCam(cam,img)
    
# undo decorator
def undo(func):
    def wrapper(*args, **kwargs):
        try:
            cmds.undoInfo(openChunk=True)
            return func(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
    return wrapper