import maya.cmds as mc

all_bones = mc.listRelatives('DM_combine', children=True)

print(len(all_bones), all_bones)
loc_grp = mc.group(empty=True, n='bone_locs')
for bone in all_bones:
    mc.select(bone)
    mc.CenterPivot()
    
    loc = mc.spaceLocator(n=bone + '_LOC')
    mc.matchTransform(loc, bone)
    
    mc.parent(loc, loc_grp)