"""
Arm ctrl - full, stretch only, squash only
Arm ctrl - stretchiness 0-10

Multiply divide — scale factor — divide — input one is calulated, input 2 is the combined length of both joints offset


1 - Make locator at shoulder  — done
2 - Make locator at ik hand ctrl — done

Distance between node

world matrix 0 to in matrix 1 - done
World matrix 0 to in matrix 2 - done

Distance to input 1 x on scale factor - done 


Blend colour - stretch blend

- Input stretchiness
- Output r into condition colour if true R 

Condition node 

- Scale factor x output into first term on condition

Blend colour 2 - ik blend

Set both to 1 for everything 


Plus minus average  
1d0 set to 1
-stretch type connected to  1d1 1d2
"""

import maya.cmds as cmds


ikChain = ['joint1', 'joint2', 'joint3']
handIKCtrl = 'hand_ik' 
hand_settings = 'hand_settings'

def start():

    shoulderLocator = cmds.spaceLocator()[0]
    shoulderLocator = cmds.rename(ikChain[0]+ "_locator")
    cmds.parentConstraint(ikChain[0], shoulderLocator, maintainOffset=False)

    handIKLocator = cmds.spaceLocator()[0]
    handIKLocator = cmds.rename(handIKCtrl+ "_locator")
    cmds.parentConstraint(handIKCtrl, handIKLocator, maintainOffset=False)

    ##setups

    ##hand_settings
    cmds.select(hand_settings)
    stretchinessValue = "l_arm_stretchiness"
    stretchTypeValue =  "l_arm_stretch_type"
    ikSwitchValue = "l_arm_IK"
    cmds.addAttr( longName=stretchinessValue, niceName="Stretchiness", attributeType="float", defaultValue=1, hidden=False, keyable=True, min=0, max=1)
    cmds.addAttr( longName=stretchTypeValue, niceName="Stretch Type", attributeType="enum", enumName = "Both:Only Stretch:Only Squash", defaultValue=1,  hidden=False, keyable=True)
    cmds.addAttr( longName=ikSwitchValue, niceName="ik_value", attributeType="float", defaultValue=0, hidden=False, keyable=True, min=0, max=1)
    
    ##nodes
    ##stretch factor needs to be divide
    stretchFactor = cmds.createNode("multiplyDivide", n="arm_stretchFactor")
    cmds.setAttr(f"{stretchFactor}.operation", 2)
    distanceNode = cmds.createNode("distanceBetween", n="arm_stretch_distance")

    stretchBlend = cmds.createNode("blendColors", n="stretch_blend")
    stretchIKBlend = cmds.createNode("blendColors", n="stretch_IK_blend")

    ikPMA = cmds.createNode("plusMinusAverage", n="arm_stretch_control_pma")

    stretchCondition = cmds.createNode("condition",n = "stretchCondition")


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
    cmds.connectAttr(f"{hand_settings}.{stretchinessValue}", f"{stretchBlend}.blender")    
    
    cmds.setAttr(f"{ikPMA}.input1D[0]", 1.0)
    cmds.connectAttr(f"{hand_settings}.{stretchTypeValue}",f"{ikPMA}.input1D[1]")
    cmds.connectAttr(f"{hand_settings}.{stretchTypeValue}",f"{ikPMA}.input1D[2]")

    ##connecting values to stretch condition
    cmds.connectAttr(f"{stretchFactor}.outputX", f"{stretchCondition}.firstTerm")
    cmds.connectAttr(f"{stretchBlend}.outputR", f"{stretchCondition}.colorIfTrueR")
    cmds.connectAttr(f"{ikPMA}.output1D", f"{stretchCondition}.operation")

    cmds.connectAttr(f"{hand_settings}.{ikSwitchValue}", f"{stretchIKBlend}.blender")
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
        return length



start()



