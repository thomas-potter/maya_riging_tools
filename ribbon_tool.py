import maya.cmds as cmds

twist_jnt_amount = 2

chain = cmds.ls(selection=True, typ="joint")


def startRibbon(chain):

    index = 0
    for i in chain: 
        if index == len(chain) -1:
            break

        joints = createRibbonBase()
        print(chain)
        print(joints)
        cmds.delete(cmds.parentConstraint(chain[index], joints[0]))
        cmds.delete(cmds.pointConstraint(chain[index+1], joints[1]))
        cmds.delete(cmds.orientConstraint(chain[index], joints[1]))

        index +=1
    


def createRibbonBase():
    allJoints = []
    nurbsPlane = cmds.nurbsPlane(lr=5, w = .5, u = 1, v=twist_jnt_amount + 1)[0]
    lengthOfRibbon = twist_jnt_amount + 2

    

    for i in range(lengthOfRibbon):

        v_pos = ( (i / float(lengthOfRibbon - 1)) if lengthOfRibbon > 1 else 0.5)
        u_pos = 0.5

        fol_shape = cmds.createNode("follicle")
        fol_transform = cmds.listRelatives(fol_shape, parent=True)[0]

        cmds.connectAttr(f"{nurbsPlane}.local", f"{fol_shape}.inputSurface")
        cmds.connectAttr(f"{nurbsPlane}.worldMatrix[0]", f"{fol_shape}.inputWorldMatrix",)

        cmds.connectAttr(f"{fol_shape}.outTranslate", f"{fol_transform}.translate")
        cmds.connectAttr(f"{fol_shape}.outRotate", f"{fol_transform}.rotate")

        cmds.setAttr(f"{fol_shape}.parameterU", u_pos)
        cmds.setAttr(f"{fol_shape}.parameterV", v_pos)

        cmds.select(cl=True)
        joint = cmds.joint(rad=.5)
        cmds.parent(joint, fol_transform)
        cmds.setAttr(f"{joint}.translate", 0, 0, 0)

        ##need to name them

        allJoints.append(joint)

    first = cmds.duplicate(allJoints[0])[0]
    cmds.parent(first, w=True)
    cmds.select(first)
    first = cmds.rename("first_joint")
    last = cmds.duplicate(allJoints[len(allJoints)-1])[0]
    cmds.parent(last, w=True)
    cmds.select(last)
    last = cmds.rename("last_joint")
    
    
    
    cmds.setAttr(f"{first}.radius", 1)
    cmds.setAttr(f"{last}.radius", 1)
    cmds.select(cl=True)
    joints = [first, last]
    cmds.skinCluster(joints, nurbsPlane, tsb= True, dropoffRate=2)

    return joints


startRibbon(chain)
