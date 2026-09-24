import maya.cmds as cmds

class P_rigToolKit(object):
	def __init__(self, uiInstance):
		self.lastCtrl = None
		self.lastMultiCtrl = None
		self.joint_nameSpace = '_JNT'
		self.control_nameSpace = '_CTRL'
		self.offset_nameSpace = '_Offset'
		self.group_nameSpace = '_OffsetGRP'
		self.main_axis = 'Y'
		self.negative = False
		self.parentType = 'Parent'
		self.jointFollow = False
		self.ctrlSize = 1
		self.allCtrlRelationships = []
		self.ui = uiInstance
		self.parentedStatus = False
		self.shouldMakeIK = True

	def updateInputs(self):
		updatedVariables = P_rigToolKitUI.updateUiInputValues(self.ui)


		defaultJntName = "_JNT"
		defaultCtrlName = "_CTRL"
		defaultOffsetName = "_Offset"
		defaultgroupOffsetName = "_OffsetGRP"

		self.joint_nameSpace = updatedVariables[0]
		self.control_nameSpace = updatedVariables[1]
		self.offset_nameSpace = updatedVariables[2]
		self.group_nameSpace = updatedVariables[3]
		self.main_axis = updatedVariables[4]
		self.negative = updatedVariables[5]
		self.parentType = updatedVariables[6]
		self.jointFollow = updatedVariables[7]
		self.ctrlSize = updatedVariables[8]
		self.shouldMakeIK = updatedVariables[9]

		if not self.joint_nameSpace.strip():
			self.joint_nameSpace = defaultJntName
		if not self.control_nameSpace.strip():
			self.control_nameSpace = defaultCtrlName
		if not self.offset_nameSpace.strip():
			self.offset_nameSpace = defaultOffsetName
		if not self.group_nameSpace.strip():
			self.group_nameSpace = defaultgroupOffsetName	
	

	def createFKCtrls(self, allJointRelationships):	
		print("fk creation")
		
		lastMainOffSetGroup = None
		allMainOffsetGroups = []
		for i in allJointRelationships:
			curSelection = i[0]
			parentJoint = i[1]
			
			if curSelection:
				if self.joint_nameSpace in str(curSelection):
					
					current_name = str(curSelection).replace(self.joint_nameSpace,"")

					createdCtrls = self.createCtrls(current_name, curSelection,'', True)
					parentCtrl = []
					if parentJoint:
						parentCtrlName = str(parentJoint).replace(self.joint_nameSpace, self.control_nameSpace)
						parentCtrl = cmds.ls(parentCtrlName)
					if parentJoint:
						if "hand" in parentJoint or "foot" in parentJoint:
							tempParentName = str(parentJoint).replace(self.joint_nameSpace,'')
							if lastMainOffSetGroup:
								if tempParentName in lastMainOffSetGroup:
									cmds.parent(createdCtrls[1], lastMainOffSetGroup)
								else:
									lastMainOffSetGroup = cmds.group(empty=True, name=tempParentName + '_groupOffsetGRP')
									cmds.delete(cmds.parentConstraint(parentJoint, lastMainOffSetGroup, maintainOffset=False))
									cmds.parent(createdCtrls[1], lastMainOffSetGroup)
									allMainOffsetGroups.append(lastMainOffSetGroup)
							else:
								lastMainOffSetGroup = cmds.group(empty=True, name=tempParentName + '_groupOffsetGRP')
								cmds.delete(cmds.parentConstraint(parentJoint, lastMainOffSetGroup, maintainOffset=False))
								cmds.parent(createdCtrls[1], lastMainOffSetGroup)
								allMainOffsetGroups.append(lastMainOffSetGroup)
							
							

					self.allCtrlRelationships.append([parentCtrl, createdCtrls[0], createdCtrls[1],curSelection])
		return allMainOffsetGroups

	def selectAllJoints(self):
		root = cmds.ls(selection=True)
		cmds.select(root, hi=True, vis=True)
		selection = cmds.ls(selection=True)
		currentRelationship = []
		allJointRelationships = []
		for i in selection:
			currentRelationship = []
			children = cmds.listRelatives(i,c=True)
			parents = cmds.listRelatives(i, c=False, p=True)
			currentRelationship.append(i)
			if parents:
				currentRelationship.append(parents[0])
			else:
				currentRelationship.append(None)
			allJointRelationships.append(currentRelationship)
		return(allJointRelationships)
	
	def findChainStarts(self):
		allJoints = self.selectAllJoints()
		jointsToFind = [('l_', 'upperarm', 'upper_arm', 'bicep'), ('r_', 'upperarm', 'upper_arm', 'bicep'), ('l_', 'upperleg', 'upper_leg', 'thigh'),('r_', 'upperleg', 'upper_leg', 'thigh') ]
		jointStarts = []
		for x in jointsToFind:
			for i in allJoints:
				selectedJoint = i[0]
				jointLower = selectedJoint.lower()
				if x[0] + x[1] in jointLower or x[0] + x[2] in jointLower or x[0]+x[3] in jointLower:
					jointStarts.append(selectedJoint)
		return jointStarts
	
	def getArmChain(self, jointStarts):
		allChains = []
		for i in jointStarts:
			armChain = [i]
			currentJoint = i
			while True:
				children = cmds.listRelatives(currentJoint, type = 'joint')

				if not children:
					break

				if children:
					if len(children) > 1:
						break

				
				
				child = children[0]
				lower = child.lower()

				armChain.append(child)
				currentJoint = child

				if 'hand' in lower or 'foot' in lower:
					break
				
			allChains.append(armChain)
		print(allChains)
		return allChains
	
	def duplicateJoints(self):
		jointNameSpace = '_JNT'
		
		chainStarts = self.findChainStarts()
		allChains = self.getArmChain(chainStarts)
		
		allChain_FK = []
		allChain_IK = []
		
		for i in allChains:
			armChain_IK = []
			armChain_FK = []
			for mode in ['_IK', '_FK']:
				duplicatedRootJoint = cmds.duplicate(i[0], rc=True)
				duplicatedChain = [duplicatedRootJoint[0]]
				duplicateChildren = cmds.listRelatives(duplicatedRootJoint[0], ad= True, type ='joint')
				tempChain = []
				for y in duplicateChildren:
					baseName = y.rstrip('1')
					if baseName in i:
						tempChain.append(y)
					else:
						cmds.delete(y)
				duplicatedChain.extend(reversed(tempChain))
				for x in duplicatedChain:
					updatedName = x.replace(jointNameSpace+ '1', mode + jointNameSpace )
					newName = cmds.rename(x, updatedName)
					if mode == '_FK':
						armChain_FK.append(newName)
					if mode == '_IK':
						armChain_IK.append(newName)
			allChain_FK.append(armChain_FK)		
			allChain_IK.append(armChain_IK)			
		return allChains, allChain_FK, allChain_IK

	def makeIK(self, ikChain, side):
		ikCtrls = []
		ikChainLength = len(ikChain)
		ikName = None
		isLeg = None
		if 'arm' in ikChain[0]:
			ikName = str(side) + 'arm'
			isLeg = False
		elif 'leg' in ikChain[0] or 'thigh' in ikChain[0]:
			ikName = str(side) + 'leg'
			isLeg = True
		ikhandle = cmds.ikHandle(sj=ikChain[0],ee=ikChain[ikChainLength -1 ], sol='ikRPsolver',n=ikName)
		ikCtrl = self.createCtrls(ikName, ikChain[ikChainLength -1], '_IK', False)
		middleIndex = ikChainLength - 2
		poleTarget = self.createCtrls(ikName,ikChain[middleIndex], '_PT' , True)[0]
		settingsCtrl = self.createCtrls(ikName, ikChain[ikChainLength-1],'_switch', False)
		poleTargetOffset = None
		if side == 'l_':
			poleTargetOffset = 30
		else:
			poleTargetOffset = -30
		if self.main_axis == "Y":
				cmds.move(0, 0, poleTargetOffset * -1 , poleTarget, ls=True, r=True)
				cmds.move(0,0,-5,settingsCtrl, r=True)
		elif self.main_axis == "X":
			cmds.move(0, poleTargetOffset, 0, poleTarget, ls=True, r=True)
		elif self.main_axis == "Z":
			cmds.move(poleTargetOffset, 0, 0, poleTarget, ls=True, r=True)
		
		cmds.poleVectorConstraint(poleTarget, ikhandle[0])
		cmds.parent(ikhandle[0], ikCtrl)
		ikCtrls.append(ikCtrl)
		ikCtrls.append(poleTarget)
		ikCtrls.append(settingsCtrl)
		return ikCtrls


	def createCtrls(self,name,placement, type, getMaster):
		rotateAmount = None
		masterGroup = cmds.group(empty=True, name=name + type + self.group_nameSpace)
		ctrl = cmds.circle(name=name + type + self.control_nameSpace, radius = self.ctrlSize)[0]

		if self.negative == True:
			rotateAmount = 90
		else:
			rotateAmount = -90

		if self.main_axis == "Y":
			cmds.rotate(rotateAmount, 0, 0, ctrl)
		elif self.main_axis == "X":
			cmds.rotate(0, rotateAmount, 0, ctrl)
		elif self.main_axis == "Z":
			cmds.rotate(0, rotateAmount, 0, ctrl)
		cmds.makeIdentity( ctrl,apply=True, r=1)
		cmds.delete(ctrl, ch=True)
		
		cmds.parent(ctrl, masterGroup)

		cmds.delete(cmds.parentConstraint(placement, masterGroup, maintainOffset=False))

		if placement.startswith('l_'):
			cmds.setAttr(ctrl+'.overrideEnabled', 1)
			cmds.setAttr(ctrl+'.overrideColor', 13)
					
		if placement.startswith('r_'):
			cmds.setAttr(ctrl+'.overrideEnabled', 1)
			cmds.setAttr(ctrl+'.overrideColor', 6)
		if getMaster == True: 
			return [ctrl, masterGroup]
		return ctrl

	def setupIK(self):
		allBaseChains, allFKChains, allIKChains = self.duplicateJoints()
		newBaseChains = []
		newFKChains = []
		endJNTS = []
		endFkCtrls = []
		ikSwitches = []
		print(allIKChains)

		
		settingsLockedAttr = ['tx', 'ty','tz', 'rx', 'ry','rz','sx','sy','sz']
		for baseChain, FKChain, IKChain in zip(allBaseChains,allFKChains,allIKChains):
			
			newBaseChains.extend(baseChain)
			newFKChains.extend(FKChain)
			if IKChain[0].startswith('l_'):
				ikCtrls = self.makeIK(IKChain, 'l_')
			if IKChain[0].startswith('r_'):
				ikCtrls = self.makeIK(IKChain, 'r_')

			fkCtrls = []
			for i in FKChain:
				parentJoint = cmds.listRelatives(i, ap=True)[0]
				current_name = str(i).replace(self.joint_nameSpace,"")
				parentCtrl = str(parentJoint).replace(self.joint_nameSpace,self.control_nameSpace)
				currentCtrl, currentOffsetGrp = self.createCtrls(current_name,i, '', True)
				fkCtrls.append(currentCtrl)
				##ctrl to parent to - current ctrl - current offset group - current joint
				self.allCtrlRelationships.append([parentCtrl, currentCtrl, currentOffsetGrp ,i])
			
			fkLength = len(fkCtrls)
			lastfk = fkCtrls[fkLength-1]

			ikLength = len(IKChain)
			lastJNT = IKChain[ikLength-1]

			ikCtrl = ikCtrls[0]
			poleTarget = ikCtrls[1]
			ikSetting = ikCtrls[2]


			ikLength = len(IKChain)
			cmds.orientConstraint(ikCtrl, IKChain[ikLength-1])
			
			cmds.addAttr(ikSetting, longName ='IkFkSwitch', attributeType="double", min=0, max=1, defaultValue=0, keyable=True)

			reverseNode = cmds.createNode('reverse', n='ikFk_VIS_reverse')
			cmds.connectAttr(ikSetting + '.IkFkSwitch', reverseNode + '.inputX')
			cmds.connectAttr(reverseNode + '.outputX', ikCtrl + '.visibility')
			cmds.connectAttr(reverseNode + '.outputX', poleTarget + '.visibility')

			for ctrls in fkCtrls:
				cmds.connectAttr(ikSetting + '.IkFkSwitch', ctrls + '.visibility')
			for base_joint, fk_joint, ik_joint, fkCtrls in zip(baseChain, FKChain, IKChain, fkCtrls):
				
				switchName = str(base_joint).replace('_JNT', '_Switch')
				switch = cmds.createNode('blendColors', n=switchName)
				cmds.connectAttr(ikSetting + '.IkFkSwitch', switch +'.blender')
				cmds.connectAttr( fk_joint + '.rotate', switch + '.color1')
				cmds.connectAttr( ik_joint + '.rotate', switch + '.color2')
				cmds.connectAttr(switch + '.output', base_joint +'.rotate')

			settingsFollow = cmds.pointConstraint(lastfk, ikSetting, maintainOffset=True)[0]
			cmds.pointConstraint(ikCtrl, ikSetting, maintainOffset=True)
			
			children = cmds.pointConstraint(settingsFollow, q=True, wal=True)
			cmds.connectAttr(ikSetting + '.IkFkSwitch', settingsFollow + '.' + children[0])
			cmds.connectAttr(reverseNode + '.outputX', settingsFollow + '.' + children[1])

			for attr in settingsLockedAttr:
				cmds.setAttr(f'{ikSetting}.{attr}', lock=True, keyable=False, channelBox=False)


			ikSwitches.append([ikSetting + '.IkFkSwitch', reverseNode + '.outputX'])
			
			endFkCtrls.append(lastfk)
			endJNTS.append(lastJNT)
			
		
		return newBaseChains, newFKChains, endFkCtrls, endJNTS, ikSwitches

	def constrainCtrls(self):
		self.parentedStatus = True
		for index in self.allCtrlRelationships:
			parentCtrl = index[0]
			currentCtrl = index[1]
			currentMasterGroup = index[2]
			currentJoint = index[3]
			if parentCtrl:
				if self.parentType == 'Constrain':
							cmds.parentConstraint(parentCtrl, currentMasterGroup, maintainOffset=True)
							
				elif self.parentType == 'Parent':
					cmds.parent(currentMasterGroup, parentCtrl)

				if self.jointFollow == True:
					cmds.parentConstraint(currentCtrl, currentJoint, maintainOffset= True)

	def updateJointRelations(self,baseChains, ikChains, allJointRelations):
		newJointRelation = []
		for i in allJointRelations:
			
			for x,y in zip(baseChains, ikChains):
				if x == i[0]:
					i[0]=None
			newJointRelation.append([i[0],i[1]])
		return newJointRelation
	
	def parentOffsets(self, offsetGroups, endFkCtrls, endJnts, ikSwitches):
		

		for switches, fkCtrl, joint, Group in zip(ikSwitches, endFkCtrls, endJnts, offsetGroups):
			Constraint = cmds.parentConstraint(fkCtrl, Group, maintainOffset= True)[0]
			cmds.parentConstraint(joint, Group, maintainOffset= True)

			children = cmds.parentConstraint(Constraint, q=True, wal=True)
			mainSwitch = switches[0]
			reversedSwitch = switches[1]
			cmds.connectAttr(mainSwitch, Constraint+ '.' + children[0])
			cmds.connectAttr(reversedSwitch, Constraint+ '.' + children[1])
				
	def makeIkFk(self):
		print('wtf')
		print(self.shouldMakeIK)

		if self.shouldMakeIK is True:
			self.updateInputs()
			allJointRelationships = self.selectAllJoints()
			baseChains, ikChains, endFkCtrls, endJNTs, ikSettings = self.setupIK()
			updatedJointRelations = self.updateJointRelations(baseChains, ikChains,allJointRelationships)
			handFeetOffsetGroups = self.createFKCtrls(updatedJointRelations)
			self.parentOffsets(handFeetOffsetGroups, endFkCtrls, endJNTs, ikSettings)
			if self.jointFollow is True:
				self.constrainCtrls()


		elif self.shouldMakeIK is not True:
			self.createFKCtrls(allJointRelationships)
			if self.jointFollow is True:
				self.constrainCtrls()

class P_rigToolKitUI(object):

	def __init__(self):

		self.rigTools= P_rigToolKit(self)
		
		self.window = "P_rigToolKit"
		self.title = "Maya Rigify"
		self.size = (400, 400)
		
		#close old window if open
		if cmds.window(self.window, exists = True):
			cmds.deleteUI(self.window, window=True)
			
		#create new window
		self.window = cmds.window(self.window, title=self.title, widthHeight=self.size)

		mainLayout = cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

		cmds.rowColumnLayout(numberOfColumns=2)
		
		cmds.text("joints name space")
		self.jointName = cmds.textField(editable=True,placeholderText="_JNT")
		cmds.text("controls name space")
		self.ctrlName = cmds.textField(editable=True,placeholderText="_CTRL")
		cmds.text("offset name space")
		self.offsetName = cmds.textField(editable=True,placeholderText="_Offset")
		cmds.text("group offset name space")
		self.groupName = cmds.textField(editable=True,placeholderText="_OffsetGRP")


		cmds.text("Axis")
		self.mainAxis = cmds.optionMenu()
		cmds.menuItem(label='Y')
		cmds.menuItem(label='X')
		cmds.menuItem(label='Z')
		
		cmds.text('negative')
		self.isNegative = cmds.checkBox(label='')
		
		cmds.text("Parent")
		self.parentType = cmds.optionMenu()
		cmds.menuItem(label='Parent')
		cmds.menuItem(label='Constrain')
		cmds.menuItem(label='None')
		
		
		cmds.text('Control Size')
		self.ctrlSizeInput = cmds.floatSliderGrp(field=True, minValue=0, maxValue=20, fieldMinValue=0, fieldMaxValue=100, value=4)

		cmds.text('Make IK')
		self.makeIK = cmds.checkBox(label='', value=True)
		cmds.text('Joint Follow')
		self.jointParent = cmds.checkBox(label='', value=True)

		cmds.rowColumnLayout(numberOfColumns=1)
		cmds.button("Create Controls",aop=True,c=lambda *args: self.rigTools.makeIkFk())

		cmds.showWindow()

	def updateUiInputValues(self):
		updatedVariables = []
		updatedVariables.append(cmds.textField(self.jointName,q=True, text=True))
		updatedVariables.append(cmds.textField(self.ctrlName,q=True, text=True))
		updatedVariables.append(cmds.textField(self.offsetName,q=True, text=True))
		updatedVariables.append(cmds.textField(self.groupName,q=True, text=True))
		updatedVariables.append(cmds.optionMenu(self.mainAxis,q=True, value=True))
		updatedVariables.append(cmds.checkBox(self.isNegative, q=True, value=True))
		updatedVariables.append(cmds.optionMenu(self.parentType, q=True, value=True))
		updatedVariables.append(cmds.checkBox(self.jointParent, q=True, value=True))
		updatedVariables.append(cmds.floatSliderGrp(self.ctrlSizeInput, q=True, value=True))
		updatedVariables.append(cmds.checkBox(self.makeIK, q=True, value=True))


		return updatedVariables
P_rigToolKitUI()

