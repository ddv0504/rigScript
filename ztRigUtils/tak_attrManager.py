'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 06/15/2016

Description:
	Attribute manager that can add new attribute.
	You can add multiple attribute by using comma between names.
	e.g.) attr1, attr2, ...

	And reorder, alias, set min/max for selected attribute in channelbox.

Requirements:
	CGM Toolbox

Usage:
	import tak_attrManager
	reload(tak_attrManager)
	tak_attrManager.ui()
'''


import maya.cmds as cmds
import re
from functools import partial
from cgm.lib import guiFactory,dictionary,settings,lists


def ui():
	win = 'attrManagerWin'

	if cmds.window(win, exists = True):
		cmds.deleteUI(win)

	cmds.window(win, title = 'Attribute Manager')

	cmds.columnLayout('mainColLo', adj = True)
	cmds.optionMenu('typeOptMenu', label = 'Type: ')
	cmds.menuItem(label = 'Float')
	cmds.menuItem(label = 'Divider')
	cmds.menuItem(label = 'Boolean')
	cmds.menuItem(label = 'Integer')
	cmds.textFieldGrp('nameTxtFldGrp', label = 'Name: ', columnWidth = [(1, 35), (2, 200)], cc = addAttr)

	cmds.button(label = 'Add', c = addAttr)

	cmds.separator(h = 5, style = 'in')

	cmds.rowColumnLayout('upDnRowColLo', numberOfColumns = 2, columnWidth = [(1, 120), (2, 120)])
	cmds.text(label = 'Reorder Attrs', align = 'left')
	cmds.text(label = '')
	cmds.button(label = 'Up', c = moveUpSelAttrs)
	cmds.button(label = 'Down', c = moveDownSelAttrs)
	cmds.setParent('..')

	cmds.separator(h = 5, style = 'in')

	cmds.rowColumnLayout('minMaxRowColLo', numberOfColumns = 5, columnWidth = [(2, 30), (5, 30)], columnOffset = [(2, 'left', 5),(5, 'right', 5)])
	cmds.text(label = 'Min/Max: ', align = 'left')
	cmds.checkBox('minChkBox', label = '', v = True)
	cmds.floatField('minFloatFld', v = 0)
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Value From Channelbox', c = partial(loadValFromChBox, 'minFloatFld'))
	cmds.floatField('maxFloatFld', v = 1)
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Value From Channelbox', c = partial(loadValFromChBox, 'maxFloatFld'))
	cmds.checkBox('maxChkBox', label = '', v = True)
	cmds.setParent('..')
	cmds.button(label = 'Apply', w = 100, c = setMinMax)

	cmds.separator(h = 5, style = 'in')

	cmds.textFieldGrp('aliasTxtFldGrp', label = 'New Name:', columnWidth = [(1, 55), (2, 180)])
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Selected Attribute', c = loadAttr)
	cmds.button(label = 'Apply', w = 100, c = aliasAttr)

	cmds.window(win, e = True, w = 50, h = 50)
	cmds.showWindow(win)


def addAttr(*args):
	'''
	Add attributes on selected object.
	'''

	attrLs = re.findall(r'\w+', cmds.textFieldGrp('nameTxtFldGrp', q = True, text = True))
	attrType = cmds.optionMenu('typeOptMenu', q = True, value = True)

	selObjs = cmds.ls(sl = True)

	for selObj in selObjs:
		for attr in attrLs:
			if attrType == 'Divider':
				cmds.addAttr(selObj, ln = attr, at = 'enum', en = '---------------:')
				cmds.setAttr('%s.%s' %(selObj, attr), channelBox = True)
			elif attrType == 'Float':
				cmds.addAttr(selObj, ln = attr, at = 'double', keyable = True, dv = 0)
			elif attrType == 'Boolean':
				cmds.addAttr(selObj, ln = attr, at = 'bool', keyable = True)
				# cmds.setAttr('%s.%s' %(selObj, attr), channelBox = True)
			elif attrType == 'Integer':
				cmds.addAttr(selObj, ln = attr, at = 'long', keyable = True, dv = 0)

	# Clear name text field.
	cmds.textFieldGrp('nameTxtFldGrp', e = True, text = '')


def moveUpSelAttrs(*args):
	'''
	Move up for selected attributes.
	'''

	selObj = cmds.ls(sl = True)[0]
	selAttrList = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
	reorderAttributes(selObj, selAttrList, 0)


def moveDownSelAttrs(*args):
	'''
	Move down for selected attributes.
	'''

	selObj = cmds.ls(sl = True)[0]
	selAttrList = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
	reorderAttributes(selObj, selAttrList, 1)


def reorderAttributes(obj, attrs, direction = 0):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	Acknowledgement:
	Thank you to - http://www.the-area.com/forum/autodesk-maya/mel/how-can-we-reorder-an-attribute-in-the-channel-box/
	
	DESCRIPTION:
	Reorders attributes on an object
	
	ARGUMENTS:
	obj(string) - obj with message attrs
	attrs(list) must be attributes on the object
	direction(int) - 0 is is negative (up on the channelbox), 1 is positive (up on the channelbox)
	
	RETURNS:
	messageList - nested list in terms of [[attrName, target],[etc][etc]]
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	assert direction in [0,1],"Direction must be 0 for negative, or 1 for positive movement"
	for attr in attrs:
		assert cmds.objExists(obj+'.'+attr) is True, "'%s.%s' doesn't exist. Swing and a miss..."%(obj,atr)
		
	userAttrs = cmds.listAttr(obj,userDefined = True)
	
	attrsToMove = []
	for attr in userAttrs:
		if not cmds.attributeQuery(attr, node = obj,listParent = True):
			attrsToMove.append(attr)
			
			
	lists.reorderListInPlace(attrsToMove,attrs,direction)
	
	#To reorder, we need delete and undo in the order we want
	for attr in attrsToMove:
		try:
			attrBuffer = '%s.%s'%(obj,attr)
			lockState = False
			if cmds.getAttr(attrBuffer,lock=True) == True:
				lockState = True
				cmds.setAttr(attrBuffer,lock=False)
				
			cmds.deleteAttr('%s.%s'%(obj,attr))
			
			cmds.undo()
			
			if lockState:
				cmds.setAttr(attrBuffer,lock=True)
				
		except:
			guiFactory.warning("'%s' Failed to reorder"%attr)


def setMinMax(*args):
	selObjList = cmds.ls(sl = True)
	selAttrList = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
	minVal = cmds.floatField('minFloatFld', q = True, v = True)
	maxVal =  cmds.floatField('maxFloatFld', q = True, v = True)
	minChkOpt = cmds.checkBox('minChkBox', q = True, v = True)
	maxChkOpt = cmds.checkBox('maxChkBox', q = True, v = True)

	for obj in selObjList:
		userDefAttrs = cmds.listAttr(obj, ud = True)
		for attr in selAttrList:
			# If exists user define attribute do following.
			if userDefAttrs and attr in userDefAttrs:
				if minChkOpt:
					cmds.addAttr('%s.%s' %(obj, attr), e = True, hasMinValue = True, min = minVal)
				elif not minChkOpt:
					cmds.addAttr('%s.%s' %(obj, attr), e = True, hasMinValue = False)
				if maxChkOpt:
					cmds.addAttr('%s.%s' %(obj, attr), e = True, hasMaxValue = True, max = maxVal)
				elif not maxChkOpt:
					cmds.addAttr('%s.%s' %(obj, attr), e = True, hasMaxValue = False)

			# If there is no user define attribute do following.
			else:
				if attr == 'tx':
					cmds.transformLimits(obj, tx = (minVal, maxVal), etx = (minChkOpt, maxChkOpt))
				elif attr == 'ty':
					cmds.transformLimits(obj, ty = (minVal, maxVal), ety = (minChkOpt, maxChkOpt))
				elif attr == 'tz':
					cmds.transformLimits(obj, tz = (minVal, maxVal), etz = (minChkOpt, maxChkOpt))
				elif attr == 'rx':
					cmds.transformLimits(obj, rx = (minVal, maxVal), erx = (minChkOpt, maxChkOpt))
				elif attr == 'ry':
					cmds.transformLimits(obj, ry = (minVal, maxVal), ery = (minChkOpt, maxChkOpt))
				elif attr == 'rz':
					cmds.transformLimits(obj, rz = (minVal, maxVal), erz = (minChkOpt, maxChkOpt))
				elif attr == 'sx':
					cmds.transformLimits(obj, sx = (minVal, maxVal), esx = (minChkOpt, maxChkOpt))
				elif attr == 'sy':
					cmds.transformLimits(obj, sy = (minVal, maxVal), esy = (minChkOpt, maxChkOpt))
				elif attr == 'sz':
					cmds.transformLimits(obj, sz = (minVal, maxVal), esz = (minChkOpt, maxChkOpt))


def aliasAttr(*args):
	selAttr = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)[0]
	replace = cmds.textFieldGrp('aliasTxtFldGrp', q = True, text = True)

	selList = cmds.ls(sl = True)

	for sel in selList:
		cmds.renameAttr('%s.%s' %(sel, selAttr), replace)

	cmds.select(selList, r = True)


def loadAttr(*args):
	selAttr = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)[0]

	selList = cmds.ls(sl = True)

	cmds.textFieldGrp('aliasTxtFldGrp', e = True, text = selAttr)


def loadValFromChBox(floatFldName, *args):
	'''
	Fill float field with selected attribute's value in channelbox.
	'''

	sel = cmds.ls(sl = True)[0]
	selAttr = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)[0]
	selAttrVal = cmds.getAttr(sel + '.' + selAttr)

	cmds.floatField(floatFldName, e = True, v = selAttrVal)
