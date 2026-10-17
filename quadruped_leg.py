import maya.cmds as cmds

selection = cmds.ls(sl=True, typ="joint") 

mainChain = cmds.listRelatives(selection, ad=True)
mainChain.append(selection[0])

mainChain.reverse()
controlChain = cmds.duplicate(selection, rc=True)

tempChain = []
for i in controlChain:
    newname = str(i.removesuffix("_JNT1")) + "_MCH"
    cmds.select(i)
    cmds.rename(newname)
    tempChain.append(newname)

controlChain = tempChain

##ik handle between the first joint in the chain to the paw on the driverChain
driverIK = cmds.ikHandle(sj = controlChain[0], ee=controlChain[3], sol="ikSpringSolver")



