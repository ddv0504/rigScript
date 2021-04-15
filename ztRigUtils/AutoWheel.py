import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds

toolWindowName='DynamicWheel'
toolLabel='Dynamic Wheel'

buttonMenu1='createDynamic'
buttonMenu2='deleteDynamic'

labelButtonMenu1='Create Dynamic'
labelButtonMenu2='Delete Dynamic'

buttonMenu1Function='createDynamicWheel()'
buttonMenu2Function='deleteDynamicWheel()'

checkBox1='checkAutoName' #check box selected name
checkBox2='checkAutoPosition' #check box selected position
checkBox3='checkAutoBind' #auto bind to selected object
checkBox4='checkAutoCons' #auto constraint to selected object

optionMenu1='optionWheelDirection'
#optionMenu2='optionWheelUp'
#-----------------------------------------

windowwidth = []
windowheight = []
dwidth = []
dheight = []
i=[]
o=[]
sel=[]
dyngrp = 'Dynamics'
createorder = ['_GRP','_Ctrl','_dyn_JNT','_dyn_driver_RG','_dyn_driven_PC','_dyn_bake_ADL']
typeorder = ['transform','joint','joint','transform','pointConstraint','addDoubleLinear']
clist = [] #created list
ctrlattr = 'dynamics_enable', 'link_dynamics_bake', 'link_dynamics_preroll'
drvnattr = 'cacheTranslate'
hideattr = ['.tx','.ty','.tz','.ry','.rz','.sx','.sy','.sz','.v','.radi']
direction = []
up = []
rxyz = []

#-----------------------------------------

        
def changestate():
    if pm.textField('textFieldName', query=1, enable=1):
        pm.textField('textFieldName', edit=1, enable=0)
    else:
        pm.textField('textFieldName', edit=1, enable=1)
    if pm.checkBox(checkBox3, query=1, enable=1):
        pm.checkBox(checkBox3, edit=1, enable=0)
        pm.checkBox(checkBox3, edit=1, v=0)
    else:
        pm.checkBox(checkBox3, edit=1, enable=1)
    if pm.checkBox(checkBox4, query=1, enable=1):
        pm.checkBox(checkBox4, edit=1, enable=0)
        pm.checkBox(checkBox4, edit=1, v=0)
    else:
        pm.checkBox(checkBox4, edit=1, enable=1)

def changestatebind():
    if pm.checkBox(checkBox4, query=1, v=1):
        pm.checkBox(checkBox4, edit=1, v=0)
    
def changestatecons():
    if pm.checkBox(checkBox3, query=1, v=1):
        pm.checkBox(checkBox3, edit=1, v=0)
        
'''def getdir(): #get direction from 
    global direction, ryxz
    direction = pm.optionMenu(optionMenu1, q=1, v=1)
    if direction == 'x':
        rxyz = [0,90,0]
    elif direction == 'y':
        rxyz = [-90,0,0]
    elif direction == 'z':
        rxyz = [0,0,0]
    elif direction == '-x':
        rxyz = [0,-90,0]
    elif direction == '-y':
        rxyz = [90,0,0]
    elif direction == '-z':
        rxyz = [0,180,0]
    return direction
    
def getup():
    global up
    up = pm.optionMenu(optionMenu2, q=1, v=1)
'''    
def createDynamicWheel():
    global sel,dyngrp,createorder,typeorder,clist,ctrlattr,drvnattr,sel,hideattr,ryxz
    #getdir()
    direction = pm.optionMenu(optionMenu1, q=1, v=1)
    if direction == 'x':
        rxyz = [0,90,0]
    elif direction == 'y':
        rxyz = [-90,0,0]
    elif direction == 'z':
        rxyz = [0,0,0]
    elif direction == '-x':
        rxyz = [0,-90,0]
    elif direction == '-y':
        rxyz = [90,0,0]
    elif direction == '-z':
        rxyz = [0,180,0]
    #check if checkbox of selected name is checked or not
    sel = pm.ls(os=1,ap=1)
    selpos = sel #store select position temp
    if pm.checkBox('checkAutoName',q=1,v=1)==0:
        if not pm.textField('textFieldName',q=1,tx=1)=='':
            sel = [pm.textField('textFieldName',q=1,tx=1)]
            dmynode = pm.createNode('mesh',n=sel[0]+'Shape')
            dmypar = pm.rename(pm.listRelatives(dmynode,p=1),sel[0])
        else:
            sel = []
    else:
        sel = pm.ls(os=1,ap=1)
    pm.select(cl=1)
    if not pm.objExists(dyngrp):
        pm.group(n=dyngrp,w=1)
    #print sel
    for i in sel:
        #get parent and pararent suffix
        try:
            par = pm.listRelatives(i,p=1)[0]
            parpar = pm.listRelatives(i,p=1)[0]
            parsuffix = par.split('_')
            parsuffix.reverse()
        except:
            parsuffix = ['null']
        try:
            n = i.split('_')
            del n[len(n)-1]
            ii = '_'.join(n)
        except:
            ii=i
        clist = []
        if pm.objExists(i+'_Dyn_SETUP'):
            pm.delete(i+'_Dyn_SETUP')
        #create node and append list
        for o in range(len(createorder)):
            if pm.objExists(i+createorder[o]):
                pm.delete(i+createorder[o])
            ####this part  -v-   if the selected item is GRP or joint or curve then it will add to clist's list
            if o == 0 and parsuffix[0] == 'GRP':
                #print parsuffix[0]
                clist.append(par)
                dupgrp = pm.rename(pm.duplicate(par),par+'_Dup')
                #print pm.listRelatives(dupgrp)[0]
                pm.rename(pm.listRelatives(dupgrp)[0],dupgrp.replace('GRP','Ctrl'))
                pm.parent(dupgrp,w=1)
                pm.parent(par,w=1)
                pm.setAttr(par+'.t',0,0,0)
                pm.setAttr(par+'.r',0,0,0)
            elif o == 1 and (pm.objectType(i,i='joint') or pm.objectType(pm.listRelatives(i)[0],i='nurbsCurve')):
                clist.append(i)
                pm.parent(i,w=1)
                pm.setAttr(i+'.t',0,0,0)
                pm.setAttr(i+'.r',0,0,0)
            elif o == 2 and (pm.objectType(i,i='joint') or pm.objectType(pm.listRelatives(i)[0],i='nurbsCurve')):
                clist.append(pm.createNode(typeorder[o], n=i+createorder[o]))
                #con = pm.parentConstraint(i,clist[2],mo=0)
                #pm.delete(con)
            else:
                clist.append(pm.createNode(typeorder[o], n=i+createorder[o]))
        clist.append(pm.spaceLocator(n=i+'_1_Loc'))
        clist.append(pm.spaceLocator(n=i+'_2_Loc'))
        bbox = pm.exactWorldBoundingBox(i)

        if pm.objectType(i,i='joint') or pm.objectType(i,i='nurbsCurve'):
            posctrl = pm.xform(dupgrp,q=1,ws=1,rp=1)
            pm.setAttr(clist[6]+'.ty',posctrl[1])
        elif pm.checkBox('checkAutoName',q=1,v=1)==0:
            pm.setAttr(clist[6]+'.ty',0)
            pm.setAttr(clist[7]+'.ty',0.5)
        else:
            pm.setAttr(clist[6]+'.ty',bbox[1])
            pm.setAttr(clist[7]+'.ty',(bbox[4]+bbox[1])/2)
        distnode = pm.createNode('distanceDimShape', n=i+'_DisShape')
        clist.append(pm.rename(pm.listRelatives(distnode,p=1)[0],i+'_Dis'))
        
        
        #makeshape
        chkshp = pm.listRelatives(i)[0]
        if pm.objectType(chkshp,i='joint') or pm.objectType(chkshp,i='nurbsCurve'):
            pass
        else:
            crcl = pm.circle( nr=(1, 0, 0), c=(0, 0, 0) )
            crclshp = pm.listRelatives(crcl)
            pm.parent(crclshp,clist[1],add=1,s=1)
            pm.rename(crclshp,clist[1]+'Shape')
            pm.delete(crcl)
    
        #parent
        pm.parent(clist[1],clist[0])
        pm.parent(clist[2],clist[1])
        pm.parent(clist[4],clist[3])
        pm.select(clist[3],clist[6],clist[7],clist[8])
        if pm.objExists(i+'_Dyn_SETUP'):
            pm.parent(clist[3],clist[6],clist[7],clist[8],i+'_Dyn_SETUP')
        else:
            pm.select(cl=1)
            pm.select(clist[3],clist[6],clist[7],clist[8])
            pm.group(n=i+'_Dyn_SETUP')
        if pm.objExists(dyngrp):
            pm.parent(i+'_Dyn_SETUP',dyngrp)
        else:
            pm.select(cl=1)
            pm.select(i+'_Dyn_SETUP')
            pm.group(n=dyngrp)
        
        #create pointConstraint
        pcon = pm.pointConstraint(clist[1],clist[3],mo=1)
        pcon = pm.rename(pcon,pcon.replace('RG_pointConstraint1','PC'))
        clist.append(pcon)
        
        
        #create Attribute
        pm.addAttr(clist[1], ln=ctrlattr[0],nn='Dynamic',at='float',hnv=1,min=0,hxv=1,max=1,k=1,h=0,dv=1)
        #pm.addAttr(clist[1], ln=ctrlattr[2],at='float',k=1,h=0)
        #pm.addAttr(clist[3], ln=drvnattr,at='double3',k=1,h=0,nc=3)
        clist[3].addAttr(drvnattr, attributeType='double3')
        clist[3].addAttr(drvnattr+'X', p=drvnattr, attributeType='double',k=1)
        clist[3].addAttr(drvnattr+'Y', p=drvnattr, attributeType='double',k=1)
        clist[3].addAttr(drvnattr+'Z', p=drvnattr, attributeType='double',k=1)
        
        #connect Attributes
        pm.connectAttr(clist[2]+'.parentInverseMatrix',clist[4]+'.constraintParentInverseMatrix',f=1)
        pm.connectAttr(clist[3]+'.parentMatrix[0]',clist[4]+'.target[0].targetParentMatrix',f=1)
        pm.connectAttr(clist[3]+'.cacheTranslate',clist[4]+'.target[0].targetTranslate',f=1)
        pm.connectAttr(clist[1]+'.rx',clist[5]+'.input1',f=1)
        pm.connectAttr(clist[2]+'.rx',clist[5]+'.input2',f=1)
        #pm.connectAttr(clist[5]+'.output',clist[1]+'.'+ctrlattr[2],f=1)
        pm.connectAttr(clist[6]+'.worldPosition',clist[8]+'.startPoint',f=1)
        pm.connectAttr(clist[7]+'.worldPosition',clist[8]+'.endPoint',f=1)
    
        #Expression
        cmd = ('float $rotate = 0.0;\n'
            'vector $pos = <<{0}.tx, {0}.ty, {0}.tz>>;\n'
            '\n'
            'float $state = {1}.dynamics_enable;\n'
            'if ($state > 0.0001) $rotate = .I[4];\n'
            '\n'
            'if (frame > .I[5])\n'
            '{{\n'
            '    $rotate = {2}.rx;\n'
            '\n'
            '    if ($state > 0.0001)\n'
            '    {{\n'
            '        float $radius = {3}.distance;\n'
            '        float $distance = {4}.constraintTranslateZ;\n'
            '        $rotate += $state * -1 * 57.29578 * $distance / $radius;\n'
            '    }}\n'
            '}}\n'
            '\n'
            '{2}.rx = $rotate;\n'
            '{0}.cacheTranslate.cacheTranslateX = $pos.x;\n'
            '{0}.cacheTranslate.cacheTranslateY = $pos.y;\n'
            '{0}.cacheTranslate.cacheTranslateZ = $pos.z;\n')
        #{0} = driver_RG
        #{1} = Rotation_Ctrl
        #{2} = Rotation_Ctrl_dyn_JNT
        #{3} = DistanceShape
        #{4} = Rotation_Ctrl_dyn_driven_PC (supposed to be {4}.constraintTranslateZ)
        #mvdir = ''+clist[4]+'.constraintTranslateZ'
        cmd = cmd.format(clist[3],clist[1],clist[2],clist[8],clist[4])
        if pm.objExists(i+'_dyn_EXP'):
            pm.delete(i+'_dyn_EXP')
        clist.append(pm.expression(n=i+'_dyn_EXP',s=cmd))
        #set group position
        if pm.checkBox(checkBox1,q=1,v=1)==0 and pm.checkBox(checkBox2,q=1,v=1)==1:
            posctrl = pm.xform(selpos[0],q=1,ws=1,rp=1)
            pm.setAttr(clist[0]+'.tx',posctrl[0])
            pm.setAttr(clist[0]+'.ty',posctrl[1])
            pm.setAttr(clist[0]+'.tz',posctrl[2])
            pm.setAttr(clist[0]+'.r',rxyz)
        elif pm.objectType(i,i='joint') or pm.objectType(pm.listRelatives(i)[0],i='nurbsCurve'):
            pass
        elif pm.checkBox(checkBox1,q=1,v=1)==1 and pm.checkBox(checkBox2,q=1,v=1)==1:
            posctrl = pm.xform(i,q=1,ws=1,rp=1)
            pm.setAttr(clist[0]+'.tx',posctrl[0])
            pm.setAttr(clist[0]+'.ty',posctrl[1])
            pm.setAttr(clist[0]+'.tz',posctrl[2])
            pm.setAttr(clist[0]+'.r',rxyz)
        else:
            pm.setAttr(clist[0]+'.r',rxyz)
        
        #hide Attribute
        for h in range(0,2):
            for attr in hideattr:
                if pm.objExists(clist[1+h*1]+attr):
                    pm.setAttr(clist[1+h*1]+attr,e=1,l=1,k=0,cb=0)
        
        #constraint or bind
        if pm.checkBox(checkBox3,q=1,v=1):
            if pm.objectType(i,i='joint') or pm.objectType(pm.listRelatives(i)[0],i='nurbsCurve'):
                #this part is for object with type of joint or nurbscurve
                if pm.checkBox('checkAutoPosition',q=1,v=1):
                    try:
                        con = pm.parentConstraint(dupgrp,clist[0],mo=0)
                        #pm.parent(par,parpar)
                        pm.delete(con,dupgrp)
                    except:
                        print 'Bind Failed. Pass this process'
            else:
                try:
                    pm.skinCluster(clist[2],i,sm=0,nw=1,ibp=1,tsb=1,ih=1)
                except:
                    print 'Bind Failed'
        elif pm.checkBox(checkBox4,q=1,v=1):
            if pm.objectType(i,i='joint') or pm.objectType(pm.listRelatives(i)[0],i='nurbsCurve'):
                #this part is for object with type of joint or nurbscurve
                if pm.checkBox('checkAutoPosition',q=1,v=1):
                    try:
                        con = pm.parentConstraint(dupgrp,clist[0],mo=0)
                        #pm.parent(par,parpar)
                        pm.delete(con,dupgrp)
                    except:
                        print 'Constraint Failed, Pass this process'
            else:
                try:
                    pm.parentConstraint(clist[2],i,mo=1)
                    pm.scaleConstraint(clist[2],i,mo=1)
                except:
                    print 'Constraint Failed'
        else:
            if pm.objectType(i,i='joint') or pm.objectType(pm.listRelatives(i)[0],i='nurbsCurve'):
                #this part is for object with type of joint or nurbscurve
                if pm.checkBox('checkAutoPosition',q=1,v=1):
                    try:
                        con = pm.parentConstraint(dupgrp,clist[0],mo=0)
                        #pm.parent(par,parpar)
                        pm.delete(con,dupgrp)
                    except:
                        print 'Pass this process'
                else:
                    pm.setAttr(clist[0]+'.r',rxyz)
                    pm.delete(dupgrp)
            else:
                print 'Pass this process'
            
        #add dynamic setup to clist
        clist.append(i+'_Dyn_SETUP')
        #rename
        try:
            if pm.checkBox('checkAutoName',q=1,v=1)==1:
                for o in clist:
                    if pm.objectType(i,i='joint') or pm.objectType(pm.listRelatives(i)[0],i='nurbsCurve'):
                        pass
                    else:
                        pm.rename(o,o.replace(str(i),str(ii)))
        except:
            pass
        #delete dummy node
        if pm.checkBox('checkAutoName',q=1,v=1)==0:
            pm.delete(dmypar)
        
        pm.select(clist[1])
        print clist
        print 'done'
        
def deleteDynamicWheel():
    #check if value box is 1 or not
    if pm.checkBox('checkAutoName',q=1,v=1)==0:
        if not pm.textField('textFieldName',q=1,tx=1)=='':
            sel = [pm.textField('textFieldName',q=1,tx=1)]
        else:
            sel = []
    else:
        sel = pm.ls(os=1,ap=1)
    pm.select(cl=1)
    #print sel
    for i in sel:
        if pm.checkBox('checkAutoName',q=1,v=1)==0:
            ii=i
        else:
            try:
                n = i.split('_')
                del n[len(n)-1]
                ii = '_'.join(n)
            except:
                ii=i
        #print ii
        if pm.objExists(ii+'_dyn_EXP'):
            pm.delete(ii+'_dyn_EXP')
        if pm.objExists(ii+'_GRP'):
            pm.delete(ii+'_GRP')
        if pm.objExists(ii+'_Dyn_SETUP'):
            pm.delete(ii+'_Dyn_SETUP')
        
#-----------------------------------------

def resizeMainWindow (*arg):
    windowwidth = pm.window(toolWindowName,query = 1, width=1)-12
    windowheight = pm.window(toolWindowName,query = 1, height=1)
    dwidth = windowwidth/2
    pm.text('toolWindowNameText', edit=1, w=windowwidth)
    #pm.text('textName',edit=1, w=(dwidth-60))
    pm.textField('textFieldName',edit=1, w=(165)+(windowwidth-210))
    pm.optionMenu(optionMenu1,edit=1, w=windowwidth+5)
    #pm.optionMenu(optionMenu2,edit=1, w=windowwidth+5)
    i = [checkBox1,checkBox2,checkBox3,checkBox4,buttonMenu1,buttonMenu2]#,buttonMenu3,buttonMenu4,buttonMenu5,buttonMenu6,buttonMenu7,buttonMenu8,buttonMenu9,buttonMenu10,buttonMenu11,buttonMenu12,buttonMenu13,buttonMenu14,buttonMenu15,buttonMenu16]
    
    for o in range(len(i)):
        try:
            pm.button(i[o], edit=1, w=dwidth)
        except:
            pm.checkBox(i[o], edit=1, w=dwidth)
        
        
#----------------------------------------------------------------------
def main():
    if (pm.window(toolWindowName, exists=True)):
        pm.deleteUI(toolWindowName)
    pm.window(toolWindowName,title=toolWindowName,iconName='t', rtf=1, h=130, w=210)
    windowwidth = pm.window(toolWindowName, query = 1, width=1)
    windowheight = pm.window(toolWindowName, query = 1, height=1)
    dwidth = windowwidth/2-5
    twidth = windowwidth/3-5
    pm.columnLayout('mainWindowColumnLayout', adjustableColumn=1, w=windowwidth)
    pm.scrollLayout('mainWindowScrollLayout', rc=resizeMainWindow, mcw=210, hst=0, vst=0, h=windowheight, w=windowwidth)
    pm.text('toolWindowNameText', label=toolLabel, w=windowwidth-6)
    pm.rowLayout(numberOfColumns=2, columnWidth2=(dwidth-60, dwidth+60), adj=2, columnAlign=(1, 'center'), columnAttach=[(1, 'both', 0), (2, 'both', 0)] )
    pm.text('textName', label='Name')
    pm.textField('textFieldName', text='')
    pm.setParent('..')
    pm.rowLayout(numberOfColumns=2, columnWidth2=(dwidth, dwidth), columnAlign=(1, 'center'), columnAttach=[(1, 'both', 0), (2, 'both', 0)] )
    pm.checkBox(checkBox1, label='Selected Name', w=dwidth, cc='changestate()')
    pm.checkBox(checkBox2, label='Selected Pos', w=dwidth)
    pm.setParent('..')
    pm.rowLayout(numberOfColumns=2, columnWidth2=(dwidth, dwidth), columnAlign=(1, 'center'), columnAttach=[(1, 'both', 0), (2, 'both', 0)] )
    pm.checkBox(checkBox3, label='Auto Bind', w=dwidth, cc='changestatebind()',enable=0)
    pm.checkBox(checkBox4, label='Auto Const', w=dwidth, cc='changestatecons()',enable=0)
    pm.setParent('..')
    pm.optionMenu(optionMenu1, label='Front Direction',ni=6)
    pm.menuItem('x', label='x' )
    pm.menuItem('y', label='y' )
    pm.menuItem('z', label='z' )
    pm.menuItem('xx', label='-x' )
    pm.menuItem('yy', label='-y' )
    pm.menuItem('zz', label='-z' )
    pm.optionMenu(optionMenu1, e=1, v='z')
    '''pm.optionMenu(optionMenu2, label='Up Direction    ',ni=6)
    pm.menuItem('x', label='x' )
    pm.menuItem('y', label='y' )
    pm.menuItem('z', label='z' )
    pm.menuItem('xx', label='-x' )
    pm.menuItem('yy', label='-y' )
    pm.menuItem('zz', label='-z' )
    pm.optionMenu(optionMenu2, e=1, v='y')'''
    pm.rowLayout(numberOfColumns=2, columnWidth2=(dwidth, dwidth), columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0)] )
    pm.button(buttonMenu1, label=labelButtonMenu1, command=buttonMenu1Function, w=dwidth)
    pm.button(buttonMenu2, label=labelButtonMenu2, command=buttonMenu2Function, w=dwidth)
    pm.setParent('..')
    pm.showWindow()
