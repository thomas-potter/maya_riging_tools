import maya.cmds as cmds
import maya.mel as mel


mel.eval("ikSpringSolver")
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


print(mainChain)
print(controlChain)
driverIK = cmds.ikHandle(sj = controlChain[0], ee=controlChain[3], sol='ikSpringSolver')

ankleIK = cmds.ikHandle(sj = mainChain[0], ee=mainChain[2], sol="ikRPsolver") [0]
hockIK = cmds.ikHandle(sj = mainChain[2], ee=mainChain[3], sol="ikSCsolver") [0]

cmds.parent(ankleIK,controlChain[2])
cmds.parent(hockIK,controlChain[3])

## ctrl at foot to control ankle ik handle


## reverse foot


