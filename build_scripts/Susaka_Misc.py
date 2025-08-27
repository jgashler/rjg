import maya.cmds as mc
import rjg.post.dataIO.ng_weights as rWeightNgIO
import rjg.libs.util as rUtil
import sys

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

def Susaka_extras(skin_src, skin_trg_grp):
    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(mc.select(skin_trg_grp, hierarchy=True), selection=True)
    mc.select(skin_trg_grp, hierarchy=True)
    geo = mc.ls(selection=True, type='mesh')

    sk_g = []

    geo = [
        ['Wrap', 'Glove', 'UnderPantLayer', 'TempHair', 'Nails', 'TempBrows', 'RightEye', 'RightCornea', 'LeftEye', 'LeftCornea', 'Pants2', 'Belt', 'Scarf', 'CowlBase', 'Hood', 'Straps', 'Collar', 'Shirt', 'Pants', 'ArmBand', 'Kneepad', 'RShoe', 'LShoe', 'TopTeeth', 'BotTeeth', 'Tounge']
    ]

    #rUtil.create_pxWrap('Shirt', 'Pants', 'Gretchen_UBM')
    #rUtil.create_pxWrap('VestFluff', 'Clothes')
    #mc.parent('Fingernails', 'Rayden_EXTRAS')

    for g in geo:
        sk = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1, n='clothingSkc')[0]
        sk_g.append(sk)

    mc.skinCluster('head_M_JNT', 'Hair', tsb=True, skinMethod=1, n='hairSkc') #skin the hair to only the head joint in order to avoid weird stretching
        
    for g in sk_g:
        pass
        mc.copySkinWeights(ss='skinCluster1', ds=g, surfaceAssociation='closestPoint', noMirror=True, )
        #rUtil.create_pxWrap([g, 'Rayden_UBM'])

   

def Susaka_misc_pvis(skin_src, skin_trg_grp):
    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(mc.select(skin_trg_grp, hierarchy=True), selection=True)
    mc.select(skin_trg_grp, hierarchy=True)
    geo = mc.ls(selection=True, type='mesh')

    sk_g = []
    geo = [
        ['Wrap', 'Glove', 'UnderPantLayer', 'TempHair', 'Nails', 'TempBrows', 'RightEye', 'RightCornea', 'LeftEye', 'LeftCornea', 'Pants2', 'Belt', 'Scarf', 'CowlBase', 'Hood', 'Straps', 'Collar', 'Shirt', 'Pants', 'ArmBand', 'Kneepad', 'RShoe', 'LShoe', 'TopTeeth', 'BotTeeth', 'Tounge']
    ]
    for g in geo:
        sk = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1, n='clothingSkc')[0]
        sk_g.append(sk)

    for g in sk_g:
        mc.copySkinWeights(ss='skinCluster1', ds=g, surfaceAssociation='closestPoint', noMirror=True, )


def ribbons():
    L_Strap = ['Strap_01_L', 'Strap_02_L', 'Strap_03_L', 'Strap_04_L', 'Strap_05_L', 'Strap_06_L', 'Strap_07_L', 'Strap_08_L']
    R_Strap = ['Strap_01_R', 'Strap_02_R', 'Strap_03_R', 'Strap_04_R', 'Strap_05_R', 'Strap_06_R', 'Strap_07_R', 'Strap_08_R']
    Collar = ['Collar_01_L', 'Collar_02_L', 'Collar_03_L', 'Collar_04_L', 'Collar_05_L', 'Collar_06_L', 'Collar_07_L', 'Collar_08_L', 'Collar_09_M', 'Collar_08_R', 'Collar_07_R', 'Collar_06_R', 'Collar_05_R', 'Collar_04_R', 'Collar_03_R', 'Collar_02_R', 'Collar_01_R']
    HoodBack = ['HoodBack_01_M', 'HoodBack_02_M', 'HoodBack_03_M', 'HoodBack_04_M', 'HoodBack_05_M', 'HoodBack_06_M']
    HoodFront = ['HoodFront_01_L', 'HoodFront_02_L', 'HoodFront_03_L', 'HoodFront_04_L', 'HoodFront_05_L', 'HoodFront_06_L', 'HoodFront_07_L', 'HoodFront_08_M', 'HoodFront_07_R', 'HoodFront_06_R', 'HoodFront_05_R', 'HoodFront_04_R', 'HoodFront_03_R', 'HoodFront_02_R', 'HoodFront_01_R']
    HoodMid = ['HoodMid_01_L', 'HoodMid_02_L', 'HoodMid_03_L', 'HoodMid_04_L', 'HoodMid_05_L', 'HoodMid_06_L', 'HoodMid_07_L', 'HoodMid_08_M', 'HoodMid_07_R', 'HoodMid_06_R', 'HoodMid_05_R', 'HoodMid_04_R', 'HoodMid_03_R', 'HoodMid_02_R', 'HoodMid_01_R']
    Scarf = ['Scarf_Top01_M', 'Scarf_Top04_L', 'Scarf_Top06_L', 'Scarf_Top02_L', 'Scarf_Top05_L', 'Scarf_Top03_L', 'Scarf_Top11_L', 'Scarf_Top09_L', 'Scarf_Top10_L', 'Scarf_Top13_M', 'Scarf_Top10_R', 'Scarf_Top09_R', 'Scarf_Top11_R', 'Scarf_Top03_R', 'Scarf_Top05_R', 'Scarf_Top02_R', 'Scarf_Top06_R', 'Scarf_Top04_R', 'Scarf_Top01_M']
    SideBag = ['SideBag_01', 'SideBag_02', 'SideBag_03', 'SideBag_04', 'SideBag_05', 'SideBag_06']
    sys.path.append(f'{groups}/bobo/pipeline/pipeline/software/maya/scripts/rjg/build/parts')
    from ribbon import build_ribbon
    build_ribbon(guide_list=L_Strap,
                fromrig=False,
                Control_List=['Strap_01_L', 'Strap_04_L', 'Strap_08_L'],
                axis='x',
                ribbon_width=0.5,
                prefix='L_Strap',
                parent_type='single',
                parent='chest_M_01_CTRL',
                parent_list=[],
                parent_joint='spine_05')
    build_ribbon(guide_list=R_Strap,
                fromrig=False,
                Control_List=['Strap_01_R', 'Strap_04_R', 'Strap_08_R'],
                axis='x',
                ribbon_width=0.5,
                prefix='R_Strap',
                parent_type='single',
                parent='chest_M_01_CTRL',
                parent_list=[],
                parent_joint='spine_05')
    build_ribbon(guide_list=Collar,
                fromrig=False,
                Control_List=['Collar_01_L', 'Collar_09_M', 'Collar_01_R'],
                axis='x',
                ribbon_width=0.5,
                prefix='Collar',
                parent_type='list',
                parent='chest_M_01_CTRL',
                parent_list=['clavicle_L_CTRL', 'chest_M_02_CTRL', 'clavicle_R_CTRL'],
                parent_joint='spine_05')
    """build_ribbon(guide_list=Scarf,
                fromrig=False,
                Control_List=['Scarf_Top01_M', 'Scarf_Top03_L', 'Scarf_Top13_M', 'Scarf_Top03_R'],
                axis='x',
                ribbon_width=0.5,
                prefix='Scarf',
                parent_type='single',
                parent='neck_01_FK_M_CTRL',
                parent_list=[],
                parent_joint='spine_05')"""
    
    

