import maya.cmds as mc
import rjg.post.dataIO.ng_weights as rWeightNgIO
import rjg.libs.util as rUtil

from importlib import reload

reload(rUtil)

manual_skins = [
    'Pants',
    'Underbelt',
    'Boots',
    'Houlster',
    'SecondaryHoulsterStrap',
    'Vest',
    'VestFlaps',
]

def rayden_clothes(skin_src, skin_trg_grp):
    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(mc.select(skin_trg_grp, hierarchy=True), selection=True)
    mc.select(skin_trg_grp, hierarchy=True)
    geo = mc.ls(selection=True, type='mesh')

    geo = [
        "Pants", 
        "Underbelt",
        "Boots",
        "Houlster",
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
        ['VestBuckles', 'UnderVestFluff', 'Vest'],
        ['LegWraps', 'Pants'],
        ['HoulsterMetalSnap', 'CrossbowStraps', 'Houlster'],
        ['UnderVestFlapsFluff', 'VestFlaps']
    ]



    sk_g = []

    for g in geo:
        sk = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1)[0]
        sk_g.append(sk)
        
    for g in sk_g:
        mc.copySkinWeights(ss='skinCluster1', ds=g, surfaceAssociation='closestPoint', noMirror=True, )

    for ws in wrap_sets:
        rUtil.create_pxWrap(ws)

    for ms in manual_skins:
        rWeightNgIO.init_skc(ms)

        #TODO: import each of the manual skin latest version files and convert to ngSkinTools2 compatible