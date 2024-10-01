import maya.cmds as mc
import rjg.post.dataIO.ng_weights as rWeightNgIO
import rjg.libs.util as rUtil


def robin_clothes(skin_src, skin_trg_grp):
    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(mc.select(skin_trg_grp, hierarchy=True), selection=True)
    mc.select(skin_trg_grp, hierarchy=True)
    geo = mc.ls(selection=True, type='mesh')
    
    sk_g = []

    rUtil.create_pxWrap('Clothes', 
                        'Fingernails', 
                        'Eyebrows', 
                        'Eyes', 
                        'Cornea', 
                        'static_hair',
                        'Hairtie',
                        'Earrings',
                        'LowerTeeth',
                        'UpperTeeth',
                        'Tongue',
                        skin_src)
    #rUtil.create_pxWrap('Cornea', 'Eyes', 'Earrings', 'Hairtie', 'Clothes', 'Eyebrows', 'Eyelashes', 'Fingernails', 'static_hair', 'UpperTeeth', 'LowerTeeth', 'Tongue', skin_src)
    #rUtil.create_pxWrap('cornea', 'eyes', 'earrings',  'Clothes', 'eyebrows', 'eyelashes', 'Fingernails', skin_src)

    no_skin = ['ClothesShape', 
               'GroomBustShape', 
               'bun_clump', 
               'left_bang_clump', 
               'pickShape', 
               'bun_clump_exportShape', 
               'left_bang_clump_exportShape', 
               'EyebrowsShape',
               ''
               ]
    
    for g in sk_g:
        print(g)
        try:                    
            mc.copySkinWeights(ss='skinCluster1', ds=g, surfaceAssociation='closestPoint', noMirror=True, )
        except Exception as e:
            print(e)

    #geo = list(set(geo) - set(no_skin))
'''
    for g in geo:
        if g in no_skin:
            continue
        try:
            sk = mc.skinCluster(bind_joints, g, tsb=True)[0]
            sk_g.append(sk)
        except Exception as e:
            print(e)
'''


def robin_clothes_pvis(skin_src, skin_trg_grp):
    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(mc.select(skin_trg_grp, hierarchy=True), selection=True)
    mc.select(skin_trg_grp, hierarchy=True)
    geo = mc.ls(selection=True, type='mesh')

    sk_g = []

    for g in geo:
        sk = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1, n='clothingSkc')[0]
        sk_g.append(sk)

    for g in sk_g:
        mc.copySkinWeights(ss='skinCluster6', ds=g, surfaceAssociation='closestPoint', noMirror=True, )