# Copyright (C) 1997-2020 Autodesk, Inc., and/or its licensors.
# All rights reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Autodesk, Inc. ("Autodesk") and/or its licensors,
# which is protected by U.S. and Canadian federal copyright law and by
# international treaties.
#
# The Data is provided for use exclusively by You. You have the right to use,
# modify, and incorporate this Data into other products for purposes authorized 
# by the Autodesk software license agreement, without fee.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. AUTODESK
# DOES NOT MAKE AND HEREBY DISCLAIMS ANY EXPRESS OR IMPLIED WARRANTIES
# INCLUDING, BUT NOT LIMITED TO, THE WARRANTIES OF NON-INFRINGEMENT,
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, OR ARISING FROM A COURSE 
# OF DEALING, USAGE, OR TRADE PRACTICE. IN NO EVENT WILL AUTODESK AND/OR ITS
# LICENSORS BE LIABLE FOR ANY LOST REVENUES, DATA, OR PROFITS, OR SPECIAL,
# DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES, EVEN IF AUTODESK AND/OR ITS
# LICENSORS HAS BEEN ADVISED OF THE POSSIBILITY OR PROBABILITY OF SUCH DAMAGES.
#
# Author  Randall Hess 09/03/2018 (original name create_pivot_bone)
# Updated by Steven Roselle 01/09/19

import maya.cmds as cmds
import pymel.core as pymel

def bt_createJointAtCustomPivotAxis():
	
	
	# get these values	
	loc_xform = None
	loc_rp    = None
	
	# Get manipulator pos and orient	
	manip_pin = cmds.manipPivot(pinPivot=True)
	manip_pos = cmds.manipPivot(q=True, p=True)[0]
	manip_rot = cmds.manipPivot(q=True, o=True)[0]	
	
	# delete existing temp objs
	temp_joint = None
	temp_loc   = None
	temp_cluster= None
	temp_joint_name = 'temp_joint'
	temp_loc_name = 'temp_loc'
	temp_cluster_name = 'temp_cluster'
	temp_objs = [temp_joint_name, temp_loc_name]	
			
	# get the selectMode
	sel_mode_obj       = cmds.selectMode(q=True, o=True)
	sel_mode_component = cmds.selectMode(q=True, co=True)		

	# store and clear selection
	selection = cmds.ls(sl=True)
	py_selection = pymel.ls(sl=True)
	if len(selection) == 0:
		cmds.warning('Select a mesh object or component. Edit custom axis to desired position and orientation.')
		return
	
	
	if len(selection) > 0:
		
		sel = selection[0]
		py_sel = py_selection[0]
	
		# create temp joint and set pos/rot
		cmds.select(cl=True)
		temp_joint= pymel.joint(n=temp_joint_name)
		temp_loc = pymel.spaceLocator(n=temp_loc_name)
		
		# get transform from the selected object
		if type(py_sel) == pymel.nodetypes.Transform:
			# snap loc to position			
			const = pymel.pointConstraint(sel, temp_loc, mo=False, w=1.0)
			pymel.delete(const)
			const = pymel.orientConstraint(sel, temp_loc, mo=False, w=1.0)
			pymel.delete(const)
		else:
			# get transform from parent object
			if type(py_sel.node()) == pymel.nodetypes.Mesh:
				parent = py_sel.node().getParent()
				if parent:
					const = pymel.pointConstraint(parent, temp_loc, mo=False, w=1.0)
					pymel.delete(const)
					const = pymel.orientConstraint(parent, temp_loc, mo=False, w=1.0)
					pymel.delete(const)
					
					# get the transforms
					loc_xform = pymel.xform(temp_loc, q=True, m=True, ws=True)
					loc_rp = pymel.xform(temp_loc, q=True, ws=True, rp=True)					

		# rotate the temp_loc if manip rot has been modified
		if not manip_rot == (0.0,0.0,0.0):				
			pymel.rotate(temp_loc, manip_rot)
			
		# move position to the cluster position
		if not manip_pos == (0.0,0.0,0.0):		
			pymel.xform(temp_loc, ws=True, t=manip_pos)
			
		# get the transforms
		loc_xform = pymel.xform(temp_loc, q=True, m=True, ws=True)
		loc_rp = pymel.xform(temp_loc, q=True, ws=True, rp=True)		
			
		# get the position from the component selection			
		if not type(py_sel) == pymel.nodetypes.Transform:
			cmds.select(selection, r=True)
			cmds.ConvertSelectionToVertices()
			try:
				cluster = cmds.cluster(n=temp_cluster_name)[1]
			except:
				cmds.warning('You must select a mesh object!')
				pymel.delete(temp_joint)
				pymel.delete(temp_loc)
				return
			
			# get the cluster position
			cmds.select(cl=True)		
			pos = cmds.xform(cluster, q=True, ws=True, rp=True)				
			
			# snap to the cluster
			const = pymel.pointConstraint(cluster, temp_loc, mo=False, w=1.0)
			pymel.delete(const)
			
			cmds.delete(cluster)
			
			# rotate the temp_loc if manip rot has been modified
			if not manip_rot == (0.0,0.0,0.0):				
				pymel.rotate(temp_loc, manip_rot)
				
			# move position to the cluster position
			if not manip_pos == (0.0,0.0,0.0):		
				pymel.xform(temp_loc, ws=True, t=manip_pos)				
					
			# get the transforms
			loc_xform = pymel.xform(temp_loc, q=True, m=True, ws=True)
			loc_rp = pymel.xform(temp_loc, q=True, ws=True, rp=True)	
		
		# remove temp loc
		pymel.delete(temp_loc)

	# modify the joint and stu
	if temp_joint:		
		if loc_xform and loc_rp:
			pymel.xform(temp_joint, m=loc_xform, ws=True)
			pymel.xform(temp_joint, piv=loc_rp, ws=True)			
		
		# freeze orient	
		pymel.select(temp_joint)	
		pymel.makeIdentity( apply=True, translate=True, rotate=True, scale=True, n=False )

	# unpin pivot
	cmds.manipPivot(pinPivot=False)
