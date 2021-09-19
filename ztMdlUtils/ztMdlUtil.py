import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

def getModelVerticesData(obj):
    shape = pm.ls(obj)[0].getShape()
    verticesIDList = set(shape.getVertices()[1])
    vtxs = ['%s.vtx[%s]' % (shape.name(),i) for i in verticesIDList]
    data = {}
    points = [shape.getPoint(i) for i in verticesIDList]
    for idnum , point in zip(verticesIDList ,points):
        data[idnum]=point
    return data


def compareMesh(obj1,obj2,result=True):
    data1 = getModelVerticesData(obj1)
    data2 = getModelVerticesData(obj2)
    data = {}
    if not len(data1) == len(data2):
        print("Not equal point numbers")
    pm.select(cl=True)
    vtxLst = []
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
    cmds.progressBar( gMainProgressBar,
				edit=True,
				beginProgress=True,
				isInterruptable=True,
				status='Compare data ...',
				maxValue=len(data1) )
    for k,v in data1.items():
        if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
            break
        if data1[k] != data2[k]:
            vtx1 = '%s.vtx[%s]' % (obj1,k)
            vtx2 = '%s.vtx[%s]' % (obj2,k)
            vtxLst.append([vtx1,vtx2])
            if result:
                vtx1 = pm.ls(vtx1)[0]
                vtx2 = pm.ls(vtx2)[0]
                
                point1 = vtx1.getPosition()
                point2 = vtx2.getPosition()
                
                data[vtx2] = list(point1-point2)
        cmds.progressBar(gMainProgressBar, e=True, step=1)   
    cmds.progressBar(gMainProgressBar, ep=True,e=True)       
    #pm.select(vtxLst,r=True)
    
    return data
        
    
        
def matchMesh(match=True): 
    '''
    Usage: Selected vertices match to target object
    Condition: Must can be blendshape between objects.
    '''  
    #Analysis meshes
    sels = pm.ls(sl=True,fl=True)
    for n,sel in enumerate(sels):
        
        if not sel == sels[-1]:
            if not pm.objectType(sel) == "mesh":
                return
        else:
            if not pm.objectType(sels[-1]) == 'transform':
                return   
    if match:
        #Operation
        trgObj = sels[-1].getShape()
        for n,sel in enumerate(sels):
            if sel == sels[-1]:
                 
                return        
            index = sel.currentItemIndex()
            trgVtx = pm.ls('%s.vtx[%s]' % (trgObj.name(),index))[0]
            point = trgVtx.getPosition()
            sel.setPosition(point)
            cmds.refresh()
    else:
        #Operation
        trgObj = sels[-1].getShape()
        for n,sel in enumerate(sels):
            if sel == sels[-1]:
                 
                return        
            index = sel.currentItemIndex()
            trgVtx = pm.ls('%s.vtx[%s]' % (trgObj.name(),index))[0]
            point = sel.getPosition()
            
            trgVtx.setPosition(point)
            cmds.refresh()
def getMirrorVertexes(*args):
    vtxs  = cmds.ls(sl=True,fl=True)
    obj = vtxs[0].split('.')[0]
    data = {}
    xMinusVtxs = [i for i in vtxs if cmds.xform(i,q=True,ws=True,t=True)[0]<0]
    xPlusVtxs = [i for i in vtxs if cmds.xform(i,q=True,ws=True,t=True)[0]>0]
    data['leftVtx'] = xMinusVtxs
    data['rightVtx'] = xPlusVtxs
    return data
    
def offsetMesh(data,trgMesh=None,*args):
    for k,v in data.items():
        if trgMesh:
            vtxName = k.name().split('.')[1]
            trgVtx = pm.MeshVertex('%s.%s' % (trgMesh,vtxName))
        currentPoint = trgVtx.getPosition()
        point = pm.dt.Point(v)
        
        trgPoint = currentPoint + point
        trgVtx.setPosition(trgPoint)
        

def matchToClosestPoint(trgMesh,vtxLst):
    '''
    Parameter: Vertex list
    Usage: From a polygon mesh vertices move the closest point on another polygon mesh.
    ''' 
    
    #Create Node:
    srcTransform = cmds.createNode('transform',name='srcTransform')
    trgTransform = cmds.createNode('transform',name='trgTransform')
    closestPointNode = cmds.createNode('closestPointOnMesh',name='matchToClosestPointNode')
    trgShape = ''
    for i in cmds.listRelatives(trgMesh):
        if cmds.objectType(i) =='mesh':
            trgShape=i
            closestPointNode = cmds.createNode('closestPointOnMesh',name='matchToClosestPointNode')
            cmds.connectAttr('%s.worldMesh' % trgShape,'%s.inMesh' % closestPointNode,f=True)
            cmds.connectAttr('%s.worldMatrix' % trgShape,'%s.inputMatrix' % closestPointNode,f=True)
        elif cmds.objectType(i) == 'nurbsSurface':
            trgShape=i
            closestPointNode = cmds.createNode('closestPointOnSurface',name='matchToClosestPointNode')
            cmds.connectAttr('%s.worldSpace' % trgShape,'%s.inputSurface' % closestPointNode,f=True)
        elif  cmds.objectType(i) == 'nurbsCurve':
            trgShape=i
            closestPointNode = cmds.createNode('nearestPointOnCurve',name='matchToClosestPointNode')
            cmds.connectAttr('%s.worldSpace' % trgShape,'%s.inputCurve' % closestPointNode,f=True)
    #Connect Attribute
    cmds.connectAttr('%s.translate' % srcTransform,'%s.inPosition' % closestPointNode,f=True)
    cmds.connectAttr('%s.position' % closestPointNode,'%s.translate' % trgTransform, f=True)
    
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
    cmds.progressBar( gMainProgressBar,
				edit=True,
				beginProgress=True,
				isInterruptable=True,
				status='Match To Closest Point ...',
				maxValue=len(vtxLst) )
                
    #Move to target
    for vtx in vtxLst:
        if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
            break

        srcPos = []
        for value in cmds.xform(vtx,q=True,ws=True,translation=True):
            if 'e' in str(value):
                srcPos.append(0)
            else:
                srcPos.append(value)
        
        cmds.xform(srcTransform,ws=True,translation=srcPos)
               
        targetPos = []
        for value in cmds.xform(trgTransform,ws=True,q=True,translation=True):
            if 'e' in str(value):
                targetPos.append(0)
            else:
                targetPos.append(value)
        cmds.refresh()
        cmds.move(targetPos[0],targetPos[1],targetPos[2],vtx,ws=True,a=True,xyz=True)
        cmds.progressBar(gMainProgressBar, e=True, step=1)   
    cmds.progressBar(gMainProgressBar, ep=True,e=True)  
    cmds.delete([srcTransform,trgTransform,closestPointNode])
        