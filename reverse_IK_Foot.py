import maya.cmds as cmds

selection = cmds.ls(selection=True, typ="joint")
footStart = selection[0]
heel = selection[1]

footChain = (cmds.listRelatives(ad=True))
footChain.append(footStart)
footChain.reverse()

def startIKFoot(ikFootChain, heelJoint, name):
    reverseFootChaintemp = cmds.duplicate(ikFootChain[0], rc=True)
    reverseFootChain = []

    reverseFootChaintemp.append(heelJoint)
    print(reverseFootChaintemp)
    for i in reverseFootChaintemp:
        cmds.select(i)
        if i.endswith("1") == True:
            x = i.removesuffix("1")
            newJoint = cmds.rename(x+"_reverse")
        else: 
            newJoint = cmds.rename(i+"_reverse")
        reverseFootChain.append(newJoint)


    print(reverseFootChain)
    cmds.parent(reverseFootChain[len(reverseFootChain)-1], reverseFootChain[len(reverseFootChain)-2])

    print(cmds.select(reverseFootChain[len(reverseFootChain)-1]))
    cmds.reroot()
    print(reverseFootChain)
    #orient the joints
    cmds.joint(edit=True, orientJoint='yzx', secondaryAxisOrient='zup', autoOrientSecondaryAxis=True, children=True, zeroScaleOrient=True)   

    ##index of both joint chains - heel = 3 - toepivot = 2 - heelpivot = 1 - foot = 0

    print(reverseFootChain)

    #make the iks 1st one is from reg foot to second joint and need to parent it to heel pivot
    firstIkHandle = cmds.ikHandle(sj = ikFootChain[0], ee=ikFootChain[1] , sol= "ikSCsolver")[0]
    cmds.parentConstraint(reverseFootChain[1],firstIkHandle, maintainOffset=True)

    #second ik from heel pivot to toe - need to parent it to toepivot
    secondIkHandle = cmds.ikHandle(sj = ikFootChain[1], ee=ikFootChain[2] , sol= "ikSCsolver")[0]
    cmds.parentConstraint(reverseFootChain[2],secondIkHandle, maintainOffset=True)






startIKFoot(footChain, heel)