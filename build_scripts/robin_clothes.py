import maya.cmds as mc
import rjg.post.dataIO.ng_weights as rWeightNgIO
import rjg.libs.util as rUtil


def robin_clothes(skin_src, skin_trg_grp):
    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(mc.select(skin_trg_grp, hierarchy=True), selection=True)
    mc.select(skin_trg_grp, hierarchy=True)
    geo = mc.ls(selection=True, type='mesh')
    
    sk_g = []
    
    geo = [
        "Tongue",
        "UpperTeeth",
        "LowerTeeth",
        "Eyebrows",
        "Eyelashes",
        "Cornea",
        "Eyes",
        "Earrings",
        "static_hair",
        #"Hairtie"
    ]

    rUtil.create_pxWrap('Clothes', 'Fingernails', 'Robin_UBM')

    for g in geo:
        sk = mc.skinCluster('head_M_JNT', g, tsb=True, skinMethod=1, n='clothingSkc')[0]
        sk_g.append(sk)
  
    for g in sk_g:
        pass
        print(g)
        try:                    
            mc.copySkinWeights(ss='skinCluster1', ds=g, surfaceAssociation='closestPoint', noMirror=True, )
        except Exception as e:
            print(e)


def robin_clothes_pvis(skin_src, skin_trg_grp):
    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(mc.select(skin_trg_grp, hierarchy=True), selection=True)
    mc.select(skin_trg_grp, hierarchy=True)
    geo = mc.ls(selection=True, type='mesh')

    sk_g = []

    for g in geo:
        try:
            sk = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1, n='clothingSkc')[0]
            sk_g.append(sk)
        except:
            pass

    for g in sk_g:
        mc.copySkinWeights(ss='skinCluster13', ds=g, surfaceAssociation='closestPoint', noMirror=True, )