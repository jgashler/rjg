import maya.cmds as mc
import rjg.post.dataIO.ng_weights as rWeightNgIO
import rjg.libs.util as rUtil

from importlib import reload
import platform, time

groups = 'G:' if platform.system() == 'Windows' else '/groups'

reload(rUtil)

manual_skins = [
    'Pants',
    'Underbelt',
    'Boots',
    #'Houlster',
    'SecondaryHoulsterStrap',
    'Vest',
    'VestFlaps',
]

def write_clothes():
    for ms in manual_skins:
        rWeightNgIO.write_skin(ms, groups + '/dungeons/character/Rigging/Rigs/Rayden/Skin/Clothes', name=ms, force=True)
        print("saved:", ms)
        time.sleep(0.5)

def rayden_clothes(skin_src, skin_trg_grp):
    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(mc.select(skin_trg_grp, hierarchy=True), selection=True)
    mc.select(skin_trg_grp, hierarchy=True)
    geo = mc.ls(selection=True, type='mesh')

    geo = [
        "Pants", 
        "Underbelt",
        "Boots",
        #"Houlster",
        "SecondaryHoulsterStrap",
        "Shirt",
        "ShirtCollar",
        "Vest",
        "VestFlaps",
        "UnderGlove",
        "LeatherGlove",
        "R_ArmWraps",
        "ShoulderStraps",
        "Bracer",

        "Tongue",
        "UpperTeeth",
        "LowerTeeth",
        "Eyebrows",
        "Eyelashes",
        "Hair",
        "Fingernails",
        "Eyeballs",
        "Corneas"
    ]

    wrap_sets = [
        ['Pockets', 'Pants'],
        ['Belt', 'Underbelt'],
        ['BeltLoop', 'BeltFasteners', "BeltBuckle", "Belt"],
        ['BootStraps', 'Boots'],
        ['BootBuckles', 'BootStraps'],
        ['StrapFasteners', 'Houlster'],
        ['VestBuckles', 'UnderVestFluff', 'Houlster', 'Vest'],
        ['LegWraps', 'Pants'],
        ['HoulsterMetalSnap', 'CrossbowStraps', 'Houlster'],
        ['UnderVestFlapsFluff', 'VestFlaps']
    ]



    sk_g = []

    for g in geo:
        sk = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1)[0]
        sk_g.append(sk)
        #rUtil.create_pxWrap([g, 'Rayden_UBM'])
        
    for g in sk_g:
        mc.copySkinWeights(ss='skinCluster1', ds=g, surfaceAssociation='closestPoint', noMirror=True, )
        #rUtil.create_pxWrap([g, 'Rayden_UBM'])

    for ws in wrap_sets:
        rUtil.create_pxWrap(ws)
        #for g in ws[:-1]:
        #    rUtil.create_pxWrap([g, 'Rayden_UBM'])

    for ms in manual_skins:
        rWeightNgIO.init_skc(ms)
        rWeightNgIO.read_skin(ms, groups + '/dungeons/character/Rigging/Rigs/Rayden/Skin/Clothes', ms)
        #TODO: import each of the manual skin latest version files and convert to ngSkinTools2 compatible