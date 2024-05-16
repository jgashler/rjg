import maya.cmds as mc
import rjg.post.dataIO.ng_weights as rWeightNgIO


def robin_clothes(skin_src, skin_trg_grp):
    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(mc.select(skin_trg_grp, hierarchy=True), selection=True)
    mc.select(skin_trg_grp, hierarchy=True)
    geo = mc.ls(selection=True, type='mesh')
    
    sk_g = []

    for g in geo:
        sk = mc.skinCluster(bind_joints, g, tsb=True)[0]
        sk_g.append(sk)
        
    for g in sk_g:
        mc.copySkinWeights(ss='skinCluster1', ds=g, surfaceAssociation='closestPoint', noMirror=True, )