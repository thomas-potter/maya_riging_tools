import maya.cmds as cmds
import sys
import os

class P_CtrlTools():
	def __init__(self):
		
		self.control_nameSpace = 'CTRL'
		self.controlShapes = []


		
		scriptDir = cmds.internalVar(usd=True)
		self.ctrlDir = scriptDir+'P_rigToolKit/'+'Ctrls/'

		for file in os.listdir(self.ctrlDir):
			lower = file.lower()
			if lower.endswith(".fbx"):
				stripped = str(lower).replace('.fbx','')
				self.controlShapes.append([file,stripped])


	def getShapeNames(self):
		controlNames = []
		for i in  self.controlShapes:
			controlNames.append(i[1])
		controlNames.append('circle')
		controlNames.append('sphere')

		if controlNames:
			return controlNames

	def createShape(self,shape, size, name):
		createdShape = None

		if shape == 'circle':
			createdShape = cmds.circle(name=name, normal=(0,1,0), radius=size)[0]

		elif shape == 'sphere':
			createdShape = self.createSphere(name, size)
		
		
		else:
			full_path = os.path.join(self.ctrlDir, str(shape + '.fbx'))
			print(full_path)
			importedShape = cmds.file(full_path,i=True,type="FBX",ignoreVersion=True, ra=True,mergeNamespacesOnClash=False,options="fbx",pr=True, returnNewNodes=True)
			transforms = cmds.ls(importedShape, type="transform")
			cmds.select(importedShape)
			cmds.scale(size,size,size)
			
			cmds.makeIdentity(importedShape, apply=True, scale = True)  
			if transforms:
				createdShape = transforms[0]
		if createdShape:
			return createdShape

	def replaceShape(self, inputs):
		
		newCtrlType = inputs[0]
		mainAxis = inputs[1]
		negative = inputs[2]
		ctrlSize = inputs[3]
		mirror = inputs[4]
		colourInput = inputs[5]

		self.selection = cmds.ls(selection=True, typ='transform')

		print("colour" + str(colourInput))
		
		if self.selection:
			for ctrl in self.selection:
				print(ctrl)
				if mirror == True:
					
					if ctrl.startswith("l_"):
						opositeColour = None
						if colourInput == 13:
							opositeColour = 6
						if colourInput == 12:
							opositeColour = 5
						opositeCtrl = ctrl.replace("l_", "r_")
						self.makeShapes(ctrl, newCtrlType, ctrlSize, colourInput)
						self.makeShapes(opositeCtrl, newCtrlType, ctrlSize, colourInput)

					elif ctrl.startswith("r_"):
						if colourInput == 6:
							opositeColour = 13
						if colourInput == 5:
							opositeColour = 12
						opositeCtrl = ctrl.replace("r_", "l_")
						self.makeShapes(ctrl, newCtrlType, ctrlSize, colourInput)
						self.makeShapes(opositeCtrl, newCtrlType, ctrlSize, colourInput)


				else:
					self.makeShapes(ctrl, newCtrlType, ctrlSize, colourInput)

				
					
				
				

	def makeShapes(self,originalCtrl, newCtrlType, ctrlSize, ctrlColour):
		##new name for the new control
		temp_name = originalCtrl + "_TEMP"

		## make new ctrl, give it what shape to make, the size and the name to make it
		newCtrl = self.createShape(newCtrlType, ctrlSize, originalCtrl)

		## position and delete parent constraint to place ctrl
		cmds.delete(cmds.parentConstraint(originalCtrl, newCtrl, maintainOffset=False))
				
		##get the shapes under the ctrls
		newShapes = cmds.listRelatives(newCtrl, s=True, fullPath=True) or []
		oldShapes = cmds.listRelatives(originalCtrl, s=True, fullPath=True) or []


		for s in newShapes:
			cmds.parent(s, originalCtrl, r=True, s=True)


		for s in oldShapes:
			cmds.delete(s)

		finalShapes = cmds.listRelatives(originalCtrl, s=True, fullPath=True) or []
		for s in finalShapes:
			cmds.setAttr(s + '.overrideEnabled', 1)
			cmds.setAttr(s + '.overrideColor', ctrlColour)

		

		## after parenting them to original 
		cmds.delete(newCtrl)

		cmds.select(clear=True)
		cmds.select(originalCtrl)

		

				

	def createSphere(self, name, size):
		mainCircle = cmds.circle(normal=(0, 1, 0), radius=size)[0]
		circle2 = cmds.circle(normal=(1, 0, 0), radius=size)[0]
		circle2shape = cmds.listRelatives(circle2, s=True)[0]
		circle3 = cmds.circle(normal=(0, 0, 1), radius=size)[0]
		circle3shape = cmds.listRelatives(circle3, s=True)[0]
		cmds.makeIdentity(circle2, r=True)
		cmds.makeIdentity(circle3, r=True)
		cmds.parent(circle2shape, mainCircle, r=True, s=True)
		cmds.parent(circle3shape, mainCircle, r=True, s=True)
		cmds.delete(circle2, circle3)

		return mainCircle


#######UI SECTION######

class P_CtrlTools_UI(object):

	def __init__(self):
		self.ctrlTools =  P_CtrlTools()
		self.window = "P_RigShapeTools"
		self.title = "Rig Shape Tools"
		self.size = (400, 400)

		self.activeShape = None
		self.shapeButtons = {}
		
		
		#close old window is open
		if cmds.window(self.window, exists = True):
			cmds.deleteUI(self.window, window=True)
			
		#create new window
		self.window = cmds.window(self.window, title=self.title, widthHeight=self.size)
		
		self.buildUI()

		cmds.showWindow(self.window)

	def buildUI(self):
		shapes = self.ctrlTools.getShapeNames()
		
		mainLayout = cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

		cmds.text(label = "Select Controls you want to change", align='center' )

		cmds.text(label = "Control Shape", align = 'center')

		grid = cmds.gridLayout(numberOfColumns=3,cellWidthHeight=(120, 30))
		
		for shape in shapes:
			btn = cmds.button(label=shape, c=lambda _, s=shape: self.setActiveShape(s))
			self.shapeButtons[shape] = btn


		cmds.setParent(mainLayout)
		cmds.separator(h=8, style="in")
		


		axisRow = cmds.rowLayout(numberOfColumns=2,adjustableColumn=2,columnAlign=(1, "left"))
		cmds.text("Axis")
		self.mainAxis = cmds.optionMenu()
		cmds.menuItem(label='Y')
		cmds.menuItem(label='X')
		cmds.menuItem(label='Z')



		cmds.setParent(mainLayout)

		negRow = cmds.rowLayout(numberOfColumns=2,adjustableColumn=2,columnAlign=(1, "left"))

		cmds.text('Negative Axis')
		self.negative = cmds.checkBox(label='')

		cmds.setParent(mainLayout)

		cmds.text('Control Colour')
		self.colourInput = cmds.colorIndexSliderGrp( min=1, max=32, value=14)

		cmds.setParent(mainLayout)

		cmds.text('Control Size')
		self.ctrlSizeInput = cmds.floatSliderGrp(field=True, minValue=0, maxValue=20, fieldMinValue=0, fieldMaxValue=100, value=1)

		cmds.text('Mirror Changes?')
		self.mirror = cmds.checkBox(label='')

		cmds.setParent(mainLayout)
		
		cmds.button("SwapCtrls ", aop=True, c=lambda *args: self.callCreateShape())


	def setActiveShape(self, shape):
		self.activeShape = shape

		for btn in self.shapeButtons.values():
			cmds.button(btn, e=True, backgroundColor=(0.2, 0.2, 0.2))

		cmds.button(
			self.shapeButtons[shape],
			e=True,
			backgroundColor=(0.4, 0.65, 0.9)
		)

	def callCreateShape(self):
		newInputs = self.updateInputs()
		self.ctrlTools.replaceShape(newInputs)

	def updateInputs(self):
		selectedShape = self.activeShape
		mainAxis = cmds.optionMenu(self.mainAxis,q=True, value=True)
		negative = cmds.checkBox(self.negative, q=True, value=True)
		ctrlSizeInput = cmds.floatSliderGrp(self.ctrlSizeInput, q=True, value=True)
		mirror = cmds.checkBox(self.mirror, q=True, value=True)
		colourInput = cmds.colorIndexSliderGrp(self.colourInput, q=True,value=True) -1


		return [selectedShape,mainAxis,negative, ctrlSizeInput,mirror, colourInput]


 
P_CtrlTools_UI()



