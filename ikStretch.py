import maya.cmds as cmds

"""
['r_upperarm_IK_JNT', 'r_lower_arm_IK_JNT', 'r_hand_IK_JNT']
r_arm_IK_CTRL
r_arm_switch_CTRL
"""

def setupArmStretch(ikChain, ikCtrl, ikSettings):
    newname = ""
    if ikCtrl.endswith("IK_CTRL") == True:
        newname = ikCtrl.removesuffix("IK_CTRL")

    ikChainAbove = cmds.listRelatives(ikChain[0], ap=True)
    shoulderLocator = cmds.spaceLocator()[0]
    shoulderLocator = cmds.rename(ikChain[0]+ "_locator")
    cmds.delete(cmds.parentConstraint(ikChain[0], shoulderLocator, maintainOffset=False))
    cmds.parentConstraint(ikChainAbove, shoulderLocator, maintainOffset=True)

    handIKLocator = cmds.spaceLocator()[0]
    handIKLocator = cmds.rename(ikCtrl + "_locator")
    cmds.parentConstraint(ikCtrl, handIKLocator, maintainOffset=False)

    ##setups

    ##ikSettings
    cmds.select(ikSettings)
    stretchinessValue = newname + "stretchiness"
    stretchTypeValue =  newname+"stretch_type"
    ikSwitchValue = newname+"IK_Switch"
    cmds.addAttr( longName=stretchinessValue, niceName="Stretchiness", attributeType="float", defaultValue=1, hidden=False, keyable=True, min=0, max=1)
    cmds.addAttr( longName=stretchTypeValue, niceName="Stretch Type", attributeType="enum", enumName = "Both:Only Stretch:Only Squash", defaultValue=1,  hidden=False, keyable=True)
    cmds.addAttr( longName=ikSwitchValue, niceName="ik_value", attributeType="float", defaultValue=0, hidden=False, keyable=True, min=0, max=1)
    
    ##nodes
    ##stretch factor needs to be divide
    stretchFactor = cmds.createNode("multiplyDivide", n=newname + "stretchFactor")
    cmds.setAttr(f"{stretchFactor}.operation", 2)
    distanceNode = cmds.createNode("distanceBetween", n=newname+ "stretch_distance")

    stretchBlend = cmds.createNode("blendColors", n=newname + "stretch_blend")
    stretchIKBlend = cmds.createNode("blendColors", n=newname + "stretch_IK_blend")

    ikPMA = cmds.createNode("plusMinusAverage", n=newname + "stretch_control_pma")

    stretchCondition = cmds.createNode("condition",n = newname+"stretchCondition")


    ## stretch factor setup
    cmds.connectAttr(f"{shoulderLocator}.worldMatrix",f"{distanceNode}.im1")
    cmds.connectAttr(f"{handIKLocator}.worldMatrix",f"{distanceNode}.im2")

    cmds.connectAttr(f"{distanceNode}.distance", f"{stretchFactor}.input1X")
    
    ##****need to set attribute input2x to the length of both ik bones****
    chainLength = chainLengthCalulation(ikChain)
    cmds.setAttr(f"{stretchFactor}.input2X", chainLength) 
    
    ##setup for stretch type and stretch amount
    cmds.connectAttr(f"{stretchFactor}.outputX", f"{stretchBlend}.color1R")   
    cmds.setAttr(f"{stretchBlend}.color2R", 1) 
    cmds.connectAttr(f"{ikSettings}.{stretchinessValue}", f"{stretchBlend}.blender")    
    
    cmds.setAttr(f"{ikPMA}.input1D[0]", 1.0)
    cmds.connectAttr(f"{ikSettings}.{stretchTypeValue}",f"{ikPMA}.input1D[1]")
    cmds.connectAttr(f"{ikSettings}.{stretchTypeValue}",f"{ikPMA}.input1D[2]")

    ##connecting values to stretch condition
    cmds.connectAttr(f"{stretchFactor}.outputX", f"{stretchCondition}.firstTerm")
    cmds.connectAttr(f"{stretchBlend}.outputR", f"{stretchCondition}.colorIfTrueR")
    cmds.connectAttr(f"{ikPMA}.output1D", f"{stretchCondition}.operation")
    cmds.setAttr(f"{stretchCondition}.secondTerm", 1)

    cmds.connectAttr(f"{ikSettings}.{ikSwitchValue}", f"{stretchIKBlend}.blender")
    cmds.connectAttr(f"{stretchCondition}.outColorR", f"{stretchIKBlend}.color2R")


    ##connecting to joints
    cmds.connectAttr(f"{stretchIKBlend}.outputR", f"{ikChain[0]}.scaleY")
    cmds.connectAttr(f"{stretchIKBlend}.outputR", f"{ikChain[1]}.scaleY")


    

    printNode = ikChain[0]
    connectable_inputs = cmds.listAttr(printNode, connectable=True, write=True, read=True)
    #print(connectable_inputs)
    
def chainLengthCalulation(chain):
    if len(chain) == 3:
        secondOffset = cmds.getAttr(f"{chain[1]}.translateY")
        thridOffset = cmds.getAttr(f"{chain[1]}.translateY")
        print(secondOffset+thridOffset)
        length = secondOffset+thridOffset
        if length < 0:
            length  *= -1
        return length


#setupArmStretch(["jnt_01", "jnt_02", "jnt_03"] ,"ik_ctrl", "ik_settings")
