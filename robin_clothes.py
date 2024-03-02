import maya.cmds as mc

skin_src = 'Robin_Retopologized'

skin_trg_grp = 'Robin_EXTRAS'

bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
geo = mc.ls(mc.select('Robin_EXTRAS', hierarchy=True), selection=True)
mc.select('Robin_EXTRAS', hierarchy=True)
geo = mc.ls(selection=True, type='mesh')
print(geo)

sk_g = []

for g in geo:
    sk = mc.skinCluster(bind_joints, g, tsb=True)[0]
    sk_g.append(sk)
    
for g in sk_g:
    mc.copySkinWeights(ss='skinCluster1', ds=g, surfaceAssociation='closestPoint', noMirror=True, )