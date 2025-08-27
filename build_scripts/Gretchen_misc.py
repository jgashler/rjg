import maya.cmds as mc
import rjg.post.dataIO.ng_weights as rWeightNgIO
import rjg.libs.util as rUtil

from importlib import reload
import platform, time

groups = 'G:' if platform.system() == 'Windows' else '/groups'

reload(rUtil)

manual_skins = [
    #'Eyeball',
    #'Cornea',
    #'Hat',
    #'Shirt',
    #'Boots',
    #'Hair',
    #'Belt',
    #'Tongue',
    #'TopTeeth',
    #'BottomTeeth',
]

def write_clothes():
    for ms in manual_skins:
        rWeightNgIO.write_skin(ms, groups + '/dungeons/character/Rigging/Rigs/Rayden/Skin/Gretchen', name=ms, force=True)
        print("saved:", ms)
        time.sleep(0.5)

def Gretchen_extras(skin_src, skin_trg_grp):
    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(mc.select(skin_trg_grp, hierarchy=True), selection=True)
    mc.select(skin_trg_grp, hierarchy=True)
    geo = mc.ls(selection=True, type='mesh')

    sk_g = []

    #geo = ['hair', 'bandanna', 'eyebrows', 'eyelashes', 'earrrings', 'honey_pin', 'gloves', 'beltloops', 
    #       'RightEye', 'RightPupil', 'RightCornea', 'LeftEye', 'LeftCornea', 'LeftPupil', 'topteeth', 'tounge', 'bottomteeth', 
    #       'hinge', 'frame', 'glasses', 'lenses', 'button', 'button3', 'pPlane4', 'pPlane3', 'pPlane5', 'pPlane6', 'belt', 'buckle', 
    #       'loopleather', 'buckle2', 'backpockets', 'sidepocket', 'frontpockets']
    
    geo = ['belt', 'buckle', 'loopleather', 'buckle2', 'beltloops', 'frontpockets', 'sidepocket', 'backpockets', 
           'button', 'button3', 'thread1', 'thread', 'gloves', 'honey_pin', 'hinge', 'frame', 'glasses', 
           'lenses', 'topteeth', 'tounge', 'bottomteeth', 'RightEye', 'RightPupil', 'RightCornea', 'LeftEye', 'LeftCornea', 
           'LeftPupil', 'earrrings', 'eyelashes', 'eyebrows', 'hair', 'bandanna']

    

    #rUtil.create_pxWrap('shirt1', 'pantsCreased1', 'boots', 'Gretchen_UBM')
    rUtil.create_pxWrap('shirt', 'pants', 'boots', 'Gretchen_UBM')
    #rUtil.create_pxWrap('VestFluff', 'Clothes')
    #mc.parent('Fingernails', 'Rayden_EXTRAS')

    for g in geo:
        sk = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1, n='clothingSkc')[0]
        sk_g.append(sk)

    #mc.skinCluster('head_M_JNT', 'Hair', tsb=True, skinMethod=1, n='hairSkc') #skin the hair to only the head joint in order to avoid weird stretching

    for g in sk_g:
        #pass
        mc.copySkinWeights(ss='skinCluster1', ds=g, surfaceAssociation='closestPoint', noMirror=True, )
        #rUtil.create_pxWrap([g, 'Rayden_UBM'])

   

def Gretchen_misc_pvis(skin_src, skin_trg_grp):
    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(mc.select(skin_trg_grp, hierarchy=True), selection=True)
    mc.select(skin_trg_grp, hierarchy=True)
    geo = mc.ls(selection=True, type='mesh')

    sk_g = []

    for g in geo:
        sk = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1, n='clothingSkc')[0]
        sk_g.append(sk)

    for g in sk_g:
        mc.copySkinWeights(ss='skinCluster1', ds=g, surfaceAssociation='closestPoint', noMirror=True, )
