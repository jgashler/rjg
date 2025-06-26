import maya.cmds as mc
import maya.mel as mel
import sys, platform
from importlib import reload
groups = 'G:' if platform.system() == 'Windows' else '/groups'
mc.scriptEditorInfo(suppressWarnings=True,suppressInfo=True)
import rjg.build.buildPart as rBuild
import rjg.post.finalize as rFinal
import rjg.build.prop as rProp
import rjg.libs.file as rFile
import rjg.libs.util as rUtil
import rjg.post.dataIO.controls as rCtrlIO
import rjg.post.usd as rUSD
reload(rUtil)
reload(rProp)
reload(rBuild)
reload(rFinal)
reload(rFile)
reload(rUSD)
import pipe.m.space_switch as spsw
import rjg.build_scripts
reload(rjg.build_scripts)
import rjg.post.dataIO.ng_weights as rWeightNgIO
import rjg.post.dataIO.weights as rWeightIO
import rjg.post.dataIO.controls as rCtrlIO
import rjg.libs.util as rUtil
reload(rUtil)
reload(rWeightNgIO)
reload(rWeightIO)
reload(rCtrlIO)

def fix_position():
    side = ['L', 'R']
    cog_fix = "COG_M_CTRL_CNST_GRP_parentConstraint1.target[2].targetOffsetTranslateY"
    cog_fixamount = 111.614
    #hand_fix = f"hand_{s}_01_CTRL_CNST_GRP_parentConstraint1.target[2].targetOffsetTranslateY"
    hand_fix_amount = 236.446
    #leg_fix = f"foot_{s}_01_{s}_CTRL_CNST_GRP_parentConstraint1.target[2].targetOffsetTranslateY"
    leg_fix_amount = 15.863
    fix_amount = 11.5
    root_fix = "root_M_CONTROL.translateY"

    mc.setAttr(cog_fix, cog_fixamount)
    for s in side:
        hand_fix = f"hand_{s}_01_CTRL_CNST_GRP_parentConstraint1.target[2].targetOffsetTranslateY"
        leg_fix = f"foot_{s}_01_{s}_CTRL_CNST_GRP_parentConstraint1.target[2].targetOffsetTranslateY"
        mc.setAttr(hand_fix, hand_fix_amount)
        mc.setAttr(leg_fix, leg_fix_amount)
    mc.setAttr(root_fix, fix_amount)

    for d in ['L', "R"]:
        mc.setAttr(f"fingerRing_{d}_01_fk_CTRL_OFF_GRP.scaleY", .8)
        for fing in ['fingerThumb', 'fingerIndex', 'fingerMiddle', 'fingerRing']:
            mc.setAttr(f'{fing}_{d}_03_fk_CTRL_OFF_GRP.translateY', 2)
        mc.setAttr(f'fingerRing_{d}_02_fk_CTRL_OFF_GRP.scaleY', 1.2)


def clean_claws():
    hide_controls = ['fingerIndex_L_04_fk_CTRL', 'fingerMiddle_L_04_fk_CTRL', 'fingerRing_L_04_fk_CTRL', 'fingerIndex_R_04_fk_CTRL', 'fingerRing_R_04_fk_CTRL', 'fingerMiddle_R_04_fk_CTRL']
    for obj in hide_controls:
        if mc.objExists(obj):
            mc.hide(obj)
    rWeightNgIO.read_skin("HandClaws", f'{groups}/bobo/character/Rigs/Bobo/SkinFiles', 'Bobo_HandClaws_Skin')
    #proxywrap_fur(['FootClaws', 'HandClaws'])

def rename_group_objects(group_name):
    """
    Replaces 'curvenet' with 'sculpt' in the names of all descendants under the specified group.
    """
    if not mc.objExists(group_name):
        mc.warning(f"Group '{group_name}' does not exist.")
        return

    all_descendants = mc.listRelatives(group_name, allDescendents=True, fullPath=False) or []

    for obj in all_descendants:
        if "curvenet" in obj:
            new_name = obj.replace("curvenet", "sculpt")
            try:
                mc.rename(obj, new_name)
            except RuntimeError as e:
                mc.warning(f"Couldn't rename {obj}: {e}")

def proxywrap_fur(*argv):
    a = argv if len(argv) > 1 else argv[0]

    driven = a
    driver = 'Bobo_UBM'

    #print(f"adding driver: {driver} to driven: {driven}")
    mc.select(driven)
    pxWrap = mc.proximityWrap()
    mc.proximityWrap(pxWrap, e=True, addDrivers=driver)
    mc.setAttr(pxWrap[0] + '.falloffScale', 20.0)
    mc.setAttr(f"{pxWrap[0]}.smoothInfluences", 9)
    mc.setAttr(f"{pxWrap[0]}.softNormalization", 1)

def Clean_Fur():
    # Correctly paired objects and attributes
    charater = 'Bobo'
    connections = [
        ('ArmsFur', 'arm_fur_vis'),
        ('BellyFur', 'Body_Fur_Vis'),
        ('FootFur', 'Foot_Guide_Vis'),
        ('HandFur', 'Hand_Guide_Vis'),
        ('HeadFur', 'Head_Chest_Fur'),
        ('LegFur', 'Leg_Fur_Vis'),
        ('SnoutFur', 'Face_Fur_Vis')
    ]

    control_object = 'Options_ctrl'

    # Check if control exists
    if not mc.objExists(control_object):
        raise RuntimeError(f"Control object '{control_object}' does not exist in the scene.")

    # Connect attributes
    for obj, attr in connections:
        if not mc.objExists(obj):
            print(f"Skipping: '{obj}' does not exist.")
            continue

        full_attr = f"{control_object}.{attr}"
        if not mc.objExists(full_attr):
            print(f"Skipping: '{full_attr}' attribute does not exist.")
            continue

        try:
            mc.connectAttr(full_attr, f"{obj}.visibility", force=True)
            print(f"Connected {full_attr} -> {obj}.visibility")
        except Exception as e:
            print(f"Failed to connect {full_attr} -> {obj}.visibility: {e}")

    proxywrap_fur(['HeadFur', 'ArmsFur', 'LegFur', 'BellyFur', 'SnoutFur', 'FootFur', 'HandFur'])





def Fix_Colors():
    Left = ['Body_sculpt_37LHand_ctrl', 'Body_sculpt_58LHand_ctrl', 'Body_sculpt_03LElbow_ctrl', 'Body_sculpt_08NoseL_ctrl', 'Body_sculpt_04EyeLidL_ctrl', 'Body_sculpt_02LFoot_ctrl', 'Body_sculpt_01legL_ctrl', 'Body_sculpt_05EyeLidL_ctrl', 'Body_sculpt_04LFoot_ctrl', 'Body_sculpt_35LHand_ctrl', 'Body_sculpt_06LFoot_ctrl', 'Body_sculpt_04SnoutL_ctrl', 'Body_sculpt_07CheekL_ctrl', 'Body_sculpt_02kneeL_ctrl', 'Body_sculpt_02BackL_ctrl', 'Body_sculpt_07LFoot_ctrl', 'Body_sculpt_13LFoot_ctrl', 'Body_sculpt_09SnoutL_ctrl', 'Body_sculpt_03EarL_ctrl', 'Body_sculpt_02UnderEyeL_ctrl', 'Body_sculpt_51LHand_ctrl', 'Body_sculpt_02EyeLidL_ctrl', 'Body_sculpt_03lowlegL_ctrl', 'Body_sculpt_04LLowArm_ctrl', 'Body_sculpt_15LFoot_ctrl', 'Body_sculpt_07EyeLidL_ctrl', 'Body_sculpt_02MidLipL_ctrl', 'Body_sculpt_06EyeOuterL_ctrl', 'Body_sculpt_32LHand_ctrl', 'Body_sculpt_04EarL_ctrl', 'Body_sculpt_22LHand_ctrl', 'Body_sculpt_02LLowArm_ctrl', 'Body_sculpt_04CheekL_ctrl', 'Body_sculpt_23LHand_ctrl', 'Body_sculpt_06SnoutL_ctrl', 'Body_sculpt_05EarL_ctrl', 'Body_sculpt_02LWrist_ctrl', 'Body_sculpt_17LHand_ctrl', 'Body_sculpt_06ULipL_ctrl', 'Body_sculpt_56LHand_ctrl', 'Body_sculpt_05LHand_ctrl', 'Body_sculpt_03BrowL_ctrl', 'Body_sculpt_42LHand_ctrl', 'Body_sculpt_11LFoot_ctrl', 'Body_sculpt_31LHand_ctrl', 'Body_sculpt_01LFoot_ctrl', 'Body_sculpt_08LLipL_ctrl', 'Body_sculpt_04LWrist_ctrl', 'Body_sculpt_01SnoutL_ctrl', 'Body_sculpt_01UnderEyeL_ctrl', 'Body_sculpt_14LHand_ctrl', 'Body_sculpt_07SnoutL_ctrl', 'Body_sculpt_26LHand_ctrl', 'Body_sculpt_03LFoot_ctrl', 'Body_sculpt_02NostralL_ctrl', 'Body_sculpt_01NostralL_ctrl', 'Body_sculpt_45LHand_ctrl', 'Body_sculpt_07ULipL_ctrl', 'Body_sculpt_02LShoulder_ctrl', 'Body_sculpt_01EyeLidL_ctrl', 'Body_sculpt_02SnoutL_ctrl', 'Body_sculpt_02FrontL_ctrl', 'Body_sculpt_06MidLipL_ctrl', 'Body_sculpt_04MidLipL_ctrl', 'Body_sculpt_09LFoot_ctrl', 'Body_sculpt_04lowlegL_ctrl', 'Body_sculpt_05MidLipL_ctrl', 'Body_sculpt_01EarL_ctrl', 'Body_sculpt_03ULipL_ctrl', 'Body_sculpt_05NoseL_ctrl', 'Body_sculpt_29LHand_ctrl', 'Body_sculpt_03LWrist_ctrl', 'Body_sculpt_03EyeLidL_ctrl', 'Body_sculpt_13LHand_ctrl', 'Body_sculpt_02UJawL_ctrl', 'Body_sculpt_09ULipL_ctrl', 'Body_sculpt_01FrontL_ctrl', 'Body_sculpt_01LAnkle_ctrl', 'Body_sculpt_05SnoutL_ctrl', 'Body_sculpt_09LHand_ctrl', 'Body_sculpt_01UJawL_ctrl', 'Body_sculpt_05LLipL_ctrl', 'Body_sculpt_02CheekL_ctrl', 'Body_sculpt_08LFoot_ctrl', 'Body_sculpt_04LHand_ctrl', 'Body_sculpt_06LLipL_ctrl', 'Body_sculpt_27LHand_ctrl', 'Body_sculpt_05CheekL_ctrl', 'Body_sculpt_07LLipL_ctrl', 'Body_sculpt_04EyeOuterL_ctrl', 'Body_sculpt_04TopL_ctrl', 'Body_sculpt_03BackL_ctrl', 'Body_sculpt_02NL_ctrl', 'Body_sculpt_01BrowL_ctrl', 'Body_sculpt_01SideL_ctrl', 'Body_sculpt_03kneeL_ctrl', 'Body_sculpt_02LElbow_ctrl', 'Body_sculpt_50LHand_ctrl', 'Body_sculpt_03LAnkle_ctrl', 'Body_sculpt_02EarL_ctrl', 'Body_sculpt_02LAnkle_ctrl', 'Body_sculpt_02ULipL_ctrl', 'Body_sculpt_03NL_ctrl', 'Body_sculpt_46LHand_ctrl', 'Body_sculpt_38LHand_ctrl', 'Body_sculpt_02SideL_ctrl', 'Body_sculpt_09LLipL_ctrl', 'Body_sculpt_28LHand_ctrl', 'Body_sculpt_04FrontL_ctrl', 'Body_sculpt_08LHand_ctrl', 'Body_sculpt_47LHand_ctrl', 'Body_sculpt_09EyeOuterL_ctrl', 'Body_sculpt_01NL_ctrl', 'Body_sculpt_01EyeOuterL_ctrl', 'Body_sculpt_21LHand_ctrl', 'Body_sculpt_04legL_ctrl', 'Body_sculpt_11LHand_ctrl', 'Body_sculpt_03UJawL_ctrl', 'Body_sculpt_03LLowArm_ctrl', 'Body_sculpt_01BackL_ctrl', 'Body_sculpt_03EyeOuterL_ctrl', 'Body_sculpt_04NL_ctrl', 'Body_sculpt_18LHand_ctrl', 'Body_sculpt_01kneeL_ctrl', 'Body_sculpt_06EarL_ctrl', 'Body_sculpt_05BackL_ctrl', 'Body_sculpt_02ClavL_ctrl', 'Body_sculpt_49LHand_ctrl', 'Body_sculpt_07MidLipL_ctrl', 'Body_sculpt_03LHand_ctrl', 'Body_sculpt_10LFoot_ctrl', 'Body_sculpt_01uplegL_ctrl', 'Body_sculpt_03SideL1_ctrl', 'Body_sculpt_07EarL_ctrl', 'Body_sculpt_03LBicep_ctrl', 'Body_sculpt_04BackL_ctrl', 'Body_sculpt_03LLipL_ctrl', 'Body_sculpt_02LHand_ctrl', 'Body_sculpt_04NostralL_ctrl', 'Body_sculpt_39LHand_ctrl', 'Body_sculpt_02LLipL_ctrl', 'Body_sculpt_03ShdrL_ctrl', 'Body_sculpt_03NostralL_ctrl', 'Body_sculpt_06EyeLidL_ctrl', 'Body_sculpt_10LHand_ctrl', 'Body_sculpt_52LHand_ctrl', 'Body_sculpt_07LHand_ctrl', 'Body_sculpt_20LHand_ctrl', 'Body_sculpt_05SideL_ctrl', 'Body_sculpt_08ULipL_ctrl', 'Body_sculpt_07BackM_ctrl', 'Body_sculpt_03legL_ctrl', 'Body_sculpt_08EyeLidL_ctrl', 'Body_sculpt_02uplegL_ctrl', 'Body_sculpt_02LBicep_ctrl', 'Body_sculpt_04kneeL_ctrl', 'Body_sculpt_06FrontL_ctrl', 'Body_sculpt_02SideL1_ctrl', 'Body_sculpt_05ULipL_ctrl', 'Body_sculpt_04LBicep_ctrl', 'Body_sculpt_34LHand_ctrl', 'Body_sculpt_15LHand_ctrl', 'Body_sculpt_16LHand_ctrl', 'Body_sculpt_02EyeOuterL_ctrl', 'Body_sculpt_08SnoutL_ctrl', 'Body_sculpt_03SideL_ctrl', 'Body_sculpt_02lowlegL_ctrl', 'Body_sculpt_43LHand_ctrl', 'Body_sculpt_06ShdrL_ctrl', 'Body_sculpt_01LShoulder_ctrl', 'Body_sculpt_09CheekL_ctrl', 'Body_sculpt_02legL_ctrl', 'Body_sculpt_57LHand_ctrl', 'Body_sculpt_33LHand_ctrl', 'Body_sculpt_03SnoutL_ctrl', 'Body_sculpt_12LFoot_ctrl', 'Body_sculpt_05FrontL_ctrl', 'Body_sculpt_04NoseL_ctrl', 'Body_sculpt_17LFoot_ctrl', 'Body_sculpt_48LHand_ctrl', 'Body_sculpt_08CheekL_ctrl', 'Body_sculpt_03uplegL_ctrl', 'Body_sculpt_04BrowL_ctrl', 'Body_sculpt_01SideL1_ctrl', 'Body_sculpt_02BrowL_ctrl', 'Body_sculpt_06LHand_ctrl', 'Body_sculpt_03FrontL_ctrl', 'Body_sculpt_04LAnkle_ctrl', 'Body_sculpt_01CheekL_ctrl', 'Body_sculpt_01LLowArm_ctrl', 'Body_sculpt_04uplegL_ctrl', 'Body_sculpt_05UJawL_ctrl', 'Body_sculpt_03CheekL_ctrl', 'Body_sculpt_06CheekL_ctrl', 'Body_sculpt_36LHand_ctrl', 'Body_sculpt_01ClavL_ctrl', 'Body_sculpt_04ULipL_ctrl', 'Body_sculpt_30LHand_ctrl', 'Body_sculpt_19LHand_ctrl', 'Body_sculpt_01ShdrL_ctrl', 'Body_sculpt_40LHand_ctrl', 'Body_sculpt_05LFoot_ctrl', 'Body_sculpt_05ShdrL_ctrl', 'Body_sculpt_07EyeOuterL_ctrl', 'Body_sculpt_16LFoot_ctrl', 'Body_sculpt_04SideL_ctrl', 'Body_sculpt_14LFoot_ctrl', 'Body_sculpt_01LElbow_ctrl', 'Body_sculpt_24LHand_ctrl', 'Body_sculpt_04UJawL_ctrl', 'Body_sculpt_05EyeOuterL_ctrl', 'Body_sculpt_03LShoulder_ctrl', 'Body_sculpt_03ClavL_ctrl', 'Body_sculpt_03MidLipL_ctrl', 'Body_sculpt_12LHand_ctrl', 'Body_sculpt_44LHand_ctrl', 'Body_sculpt_02ShdrL_ctrl', 'Body_sculpt_01LBicep_ctrl', 'Body_sculpt_04LLipL_ctrl', 'Body_sculpt_01lowlegL_ctrl', 'Body_sculpt_41LHand_ctrl', 'Body_sculpt_04LElbow_ctrl', 'Body_sculpt_08EyeOuterL_ctrl', 'Body_sculpt_04LShoulder_ctrl', 'Body_sculpt_01LWrist_ctrl']
    Right = ['Body_sculpt_04BrowR_ctrl', 'Body_sculpt_05EyeLidR_ctrl', 'Body_sculpt_02FrontR_ctrl', 'Body_sculpt_04BackR_ctrl', 'Body_sculpt_01NR_ctrl', 'Body_sculpt_02ShdrR_ctrl', 'Body_sculpt_02NostralR_ctrl', 'Body_sculpt_03EarR_ctrl', 'Body_sculpt_01CheekR_ctrl', 'Body_sculpt_06RHand_ctrl', 'Body_sculpt_37RHand_ctrl', 'Body_sculpt_04NostralR_ctrl', 'Body_sculpt_01RWrist_ctrl', 'Body_sculpt_27RHand_ctrl', 'Body_sculpt_04RShoulder_ctrl', 'Body_sculpt_03RFoot_ctrl', 'Body_sculpt_01SideR1_ctrl', 'Body_sculpt_07EarR_ctrl', 'Body_sculpt_03BackR_ctrl', 'Body_sculpt_03NR_ctrl', 'Body_sculpt_35RHand_ctrl', 'Body_sculpt_31RHand_ctrl', 'Body_sculpt_02BrowR_ctrl', 'Body_sculpt_36RHand_ctrl', 'Body_sculpt_08NoseR_ctrl', 'Body_sculpt_07RFoot_ctrl', 'Body_sculpt_04RHand_ctrl', 'Body_sculpt_04RElbow_ctrl', 'Body_sculpt_08EyeOuterR_ctrl', 'Body_sculpt_09CheekR_ctrl', 'Body_sculpt_02SideR_ctrl', 'Body_sculpt_03RAnkle_ctrl', 'Body_sculpt_03EyeLidR_ctrl', 'Body_sculpt_13RFoot_ctrl', 'Body_sculpt_02BackR_ctrl', 'Body_sculpt_48RHand_ctrl', 'Body_sculpt_07CheekR_ctrl', 'Body_sculpt_04LLipR_ctrl', 'Body_sculpt_02UnderEyeR_ctrl', 'Body_sculpt_03RHand_ctrl', 'Body_sculpt_09RFoot_ctrl', 'Body_sculpt_01RLowArm_ctrl', 'Body_sculpt_06ShdrR_ctrl', 'Body_sculpt_09EyeOuterR_ctrl', 'Body_sculpt_12RHand_ctrl', 'Body_sculpt_52RHand_ctrl', 'Body_sculpt_43RHand_ctrl', 'Body_sculpt_02ULipR_ctrl', 'Body_sculpt_03RShoulder_ctrl', 'Body_sculpt_03legR_ctrl', 'Body_sculpt_05FrontR_ctrl', 'Body_sculpt_02RHand_ctrl', 'Body_sculpt_30RHand_ctrl', 'Body_sculpt_44RHand_ctrl', 'Body_sculpt_04MidLipR_ctrl', 'Body_sculpt_04kneeR_ctrl', 'Body_sculpt_12RFoot_ctrl', 'Body_sculpt_06EyeOuterR_ctrl', 'Body_sculpt_02RShoulder_ctrl', 'Body_sculpt_51RHand_ctrl', 'Body_sculpt_10RFoot_ctrl', 'Body_sculpt_02UJawR_ctrl', 'Body_sculpt_58RHand_ctrl', 'Body_sculpt_02lowlegR_ctrl', 'Body_sculpt_04RWrist_ctrl', 'Body_sculpt_06FrontR_ctrl', 'Body_sculpt_01ShdrR_ctrl', 'Body_sculpt_01RFoot_ctrl', 'Body_sculpt_07ULipR_ctrl', 'Body_sculpt_05LLipR_ctrl', 'Body_sculpt_04lowlegR_ctrl', 'Body_sculpt_06CheekR_ctrl', 'Body_sculpt_01ClavR_ctrl', 'Body_sculpt_01RAnkle_ctrl', 'Body_sculpt_10RHand_ctrl', 'Body_sculpt_03EyeOuterR_ctrl', 'Body_sculpt_05RFoot_ctrl', 'Body_sculpt_05MidLipR_ctrl', 'Body_sculpt_06EyeLidR_ctrl', 'Body_sculpt_22RHand_ctrl', 'Body_sculpt_20RHand_ctrl', 'Body_sculpt_03RBicep_ctrl', 'Body_sculpt_16RFoot_ctrl', 'Body_sculpt_04EyeLidR_ctrl', 'Body_sculpt_03RWrist_ctrl', 'Body_sculpt_01BackR_ctrl', 'Body_sculpt_03NostralR_ctrl', 'Body_sculpt_02MidLipR_ctrl', 'Body_sculpt_01UJawR_ctrl', 'Body_sculpt_02legR_ctrl', 'Body_sculpt_32RHand_ctrl', 'Body_sculpt_03ClavR_ctrl', 'Body_sculpt_04NR_ctrl', 'Body_sculpt_08SnoutR_ctrl', 'Body_sculpt_03RElbow_ctrl', 'Body_sculpt_07LLipR_ctrl', 'Body_sculpt_03BrowR_ctrl', 'Body_sculpt_56RHand_ctrl', 'Body_sculpt_01RShoulder_ctrl', 'Body_sculpt_05NoseR_ctrl', 'Body_sculpt_08RHand_ctrl', 'Body_sculpt_07EyeLidR_ctrl', 'Body_sculpt_07RHand_ctrl', 'Body_sculpt_01SideR_ctrl', 'Body_sculpt_01uplegR_ctrl', 'Body_sculpt_02EarR_ctrl', 'Body_sculpt_26RHand_ctrl', 'Body_sculpt_49RHand_ctrl', 'Body_sculpt_01BrowR_ctrl', 'Body_sculpt_01kneeR_ctrl', 'Body_sculpt_01RElbow_ctrl', 'Body_sculpt_06MidLipR_ctrl', 'Body_sculpt_02RAnkle_ctrl', 'Body_sculpt_03UJawR_ctrl', 'Body_sculpt_14RHand_ctrl', 'Body_sculpt_02EyeLidR_ctrl', 'Body_sculpt_04SnoutR_ctrl', 'Body_sculpt_02RWrist_ctrl', 'Body_sculpt_18RHand_ctrl', 'Body_sculpt_39RHand_ctrl', 'Body_sculpt_46RHand_ctrl', 'Body_sculpt_09BackM_ctrl', 'Body_sculpt_38RHand_ctrl', 'Body_sculpt_04uplegR_ctrl', 'Body_sculpt_03CheekR_ctrl', 'Body_sculpt_33RHand_ctrl', 'Body_sculpt_05EyeOuterR_ctrl', 'Body_sculpt_05ShdrR_ctrl', 'Body_sculpt_01RBicep_ctrl', 'Body_sculpt_05RHand_ctrl', 'Body_sculpt_03FrontR_ctrl', 'Body_sculpt_01EyeLidR_ctrl', 'Body_sculpt_05SnoutR_ctrl', 'Body_sculpt_03MidLipR_ctrl', 'Body_sculpt_03kneeR_ctrl', 'Body_sculpt_01EarR_ctrl', 'Body_sculpt_02RLowArm_ctrl', 'Body_sculpt_02kneeR_ctrl', 'Body_sculpt_01EyeOuterR_ctrl', 'Body_sculpt_01UnderEyeR_ctrl', 'Body_sculpt_05UJawR_ctrl', 'Body_sculpt_24RHand_ctrl', 'Body_sculpt_03SideR_ctrl', 'Body_sculpt_09LLipR_ctrl', 'Body_sculpt_07SnoutR_ctrl', 'Body_sculpt_47RHand_ctrl', 'Body_sculpt_08RFoot_ctrl', 'Body_sculpt_17RFoot_ctrl', 'Body_sculpt_03ULipR_ctrl', 'Body_sculpt_29RHand_ctrl', 'Body_sculpt_17RHand_ctrl', 'Body_sculpt_04RFoot_ctrl', 'Body_sculpt_11RFoot_ctrl', 'Body_sculpt_01SnoutR_ctrl', 'Body_sculpt_05SideR_ctrl', 'Body_sculpt_11RHand_ctrl', 'Body_sculpt_02RFoot_ctrl', 'Body_sculpt_06LLipR_ctrl', 'Body_sculpt_02SnoutR_ctrl', 'Body_sculpt_06ULipR_ctrl', 'Body_sculpt_06SnoutR_ctrl', 'Body_sculpt_01legR_ctrl', 'Body_sculpt_02CheekR_ctrl', 'Body_sculpt_03LLipR_ctrl', 'Body_sculpt_13RHand_ctrl', 'Body_sculpt_02EyeOuterR_ctrl', 'Body_sculpt_28RHand_ctrl', 'Body_sculpt_57RHand_ctrl', 'Body_sculpt_04SideR_ctrl', 'Body_sculpt_08EyeLidR_ctrl', 'Body_sculpt_03ShdrR_ctrl', 'Body_sculpt_07EyeOuterR_ctrl', 'Body_sculpt_01FrontR_ctrl', 'Body_sculpt_04ULipR_ctrl', 'Body_sculpt_04CheekR_ctrl', 'Body_sculpt_09RHand_ctrl', 'Body_sculpt_03uplegR_ctrl', 'Body_sculpt_14RFoot_ctrl', 'Body_sculpt_15RHand_ctrl', 'Body_sculpt_02uplegR_ctrl', 'Body_sculpt_05EarR_ctrl', 'Body_sculpt_04TopM_ctrl', 'Body_sculpt_50RHand_ctrl', 'Body_sculpt_42RHand_ctrl', 'Body_sculpt_06EarR_ctrl', 'Body_sculpt_04RBicep_ctrl', 'Body_sculpt_01NostralR_ctrl', 'Body_sculpt_08CheekR_ctrl', 'Body_sculpt_03lowlegR_ctrl', 'Body_sculpt_41RHand_ctrl', 'Body_sculpt_23RHand_ctrl', 'Body_sculpt_04RLowArm_ctrl', 'Body_sculpt_08ULipR_ctrl', 'Body_sculpt_04RAnkle_ctrl', 'Body_sculpt_09ULipR_ctrl', 'Body_sculpt_04UJawR_ctrl', 'Body_sculpt_05BackR_ctrl', 'Body_sculpt_03RLowArm_ctrl', 'Body_sculpt_02ClavR_ctrl', 'Body_sculpt_40RHand_ctrl', 'Body_sculpt_04legR_ctrl', 'Body_sculpt_04EarR_ctrl', 'Body_sculpt_45RHand_ctrl', 'Body_sculpt_02LLipR_ctrl', 'Body_sculpt_04NoseR_ctrl', 'Body_sculpt_02NR_ctrl', 'Body_sculpt_02RBicep_ctrl', 'Body_sculpt_04TopR_ctrl', 'Body_sculpt_05ULipR_ctrl', 'Body_sculpt_03SideR1_ctrl', 'Body_sculpt_07MidLipR_ctrl', 'Body_sculpt_01lowlegR_ctrl', 'Body_sculpt_04EyeOuterR_ctrl', 'Body_sculpt_04FrontR_ctrl', 'Body_sculpt_15RFoot_ctrl', 'Body_sculpt_16RHand_ctrl', 'Body_sculpt_02RElbow_ctrl', 'Body_sculpt_08LLipR_ctrl', 'Body_sculpt_03SnoutR_ctrl', 'Body_sculpt_21RHand_ctrl', 'Body_sculpt_34RHand_ctrl', 'Body_sculpt_06RFoot_ctrl', 'Body_sculpt_02SideR1_ctrl', 'Body_sculpt_19RHand_ctrl', 'Body_sculpt_05CheekR_ctrl', 'Body_sculpt_09SnoutR_ctrl']
    Mid = ['Body_sculpt_02UJawM_ctrl', 'Body_sculpt_02BackM_ctrl', 'Body_sculpt_01UJawM_ctrl', 'Body_sculpt_05FrontM_ctrl', 'Body_sculpt_04FrontM_ctrl', 'Body_sculpt_01BrowM_ctrl', 'Body_sculpt_01LLipM_ctrl', 'Body_sculpt_06BackM_ctrl', 'Body_sculpt_02FrontM_ctrl', 'Body_sculpt_10SnoutM_ctrl', 'Body_sculpt_03FrontM_ctrl', 'Body_sculpt_05BackM_ctrl', 'Body_sculpt_01ULipM_ctrl', 'Body_sculpt_04UJawM_ctrl', 'Body_sculpt_03BackM_ctrl', 'Body_sculpt_07NoseM_ctrl', 'Body_sculpt_06NoseM_ctrl', 'Body_sculpt_02Under_ctrl', 'Body_sculpt_03UJawM_ctrl', 'Body_sculpt_08BackM_ctrl', 'Body_sculpt_02NoseM_ctrl', 'Body_sculpt_11SnoutM_ctrl', 'Body_sculpt_03Under_ctrl', 'Body_sculpt_13SnoutM_ctrl', 'Body_sculpt_01BackM_ctrl', 'Body_sculpt_03NoseM_ctrl', 'Body_sculpt_06FrontM_ctrl', 'Body_sculpt_01MidLipM_ctrl', 'Body_sculpt_01Under_ctrl', 'Body_sculpt_07FrontM_ctrl', 'Body_sculpt_01NoseM_ctrl', 'Body_sculpt_01FrontM_ctrl', 'Body_sculpt_04BackM_ctrl', 'Body_sculpt_04TopM_ctrl']
    
    material3 = 'Body_CurveNet_controls3'
    material2 = 'Body_CurveNet_controls2'

    # Get the shading group connected to the material
    shading_groups3 = mc.listConnections(material3, type='shadingEngine')
    if not shading_groups3:
        print(f"No shading group connected to {material3}, creating one...")
        shading_group3 = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=material3 + 'SG')
        mc.connectAttr(material3 + '.outColor', shading_group3 + '.surfaceShader', force=True)
    else:
        shading_group3 = shading_groups3[0]

    mc.sets(Mid, edit=True, forceElement=shading_group3)

    shading_groups2 = mc.listConnections(material2, type='shadingEngine')
    if not shading_groups2:
        print(f"No shading group connected to {material2}, creating one...")
        shading_group2 = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=material2 + 'SG')
        mc.connectAttr(material2 + '.outColor', shading_group2 + '.surfaceShader', force=True)
    else:
        shading_group2 = shading_groups2[0]

    mc.sets(Left, edit=True, forceElement=shading_group2)

def make_sets():
    #Eye, Brow, Snout, Cheek, Ear, Hand, Body, Leg
    #['Body_sculpt_01ShdrL_ctrl', 'Body_sculpt_03LShoulder_ctrl', 'Body_sculpt_02LShoulder_ctrl', 'Body_sculpt_01LShoulder_ctrl', 'Body_sculpt_03LElbow_ctrl', 'Body_sculpt_04LLowArm_ctrl', 'Body_sculpt_02LLowArm_ctrl', 'Body_sculpt_02LWrist_ctrl', 'Body_sculpt_04LWrist_ctrl', 'Body_sculpt_03LWrist_ctrl', 'Body_sculpt_02LElbow_ctrl', 'Body_sculpt_03LLowArm_ctrl', 'Body_sculpt_03LBicep_ctrl', 'Body_sculpt_02LBicep_ctrl', 'Body_sculpt_04LBicep_ctrl', 'Body_sculpt_01LLowArm_ctrl', 'Body_sculpt_01LElbow_ctrl', 'Body_sculpt_01LBicep_ctrl', 'Body_sculpt_04LElbow_ctrl', 'Body_sculpt_04LShoulder_ctrl', 'Body_sculpt_09SnoutR_ctrl', 'Body_sculpt_01LWrist_ctrl', 'Body_sculpt_01RShoulder_ctrl', 'Body_sculpt_02RShoulder_ctrl', 'Body_sculpt_03RBicep_ctrl', 'Body_sculpt_04RBicep_ctrl', 'Body_sculpt_03RShoulder_ctrl', 'Body_sculpt_01RWrist_ctrl', 'Body_sculpt_04RElbow_ctrl', 'Body_sculpt_01RLowArm_ctrl', 'Body_sculpt_04RWrist_ctrl', 'Body_sculpt_03RWrist_ctrl', 'Body_sculpt_03RElbow_ctrl', 'Body_sculpt_01RElbow_ctrl', 'Body_sculpt_02RWrist_ctrl', 'Body_sculpt_01RBicep_ctrl', 'Body_sculpt_02RLowArm_ctrl', 'Body_sculpt_04RLowArm_ctrl', 'Body_sculpt_03RLowArm_ctrl', 'Body_sculpt_02RBicep_ctrl', 'Body_sculpt_02RElbow_ctrl']
    Arm_parents = ['Body_sculpt_01ShdrL_grp', 'Body_sculpt_03LShoulder_grp', 'Body_sculpt_02LShoulder_grp', 'Body_sculpt_01LShoulder_grp', 'Body_sculpt_03LElbow_grp', 'Body_sculpt_04LLowArm_grp', 'Body_sculpt_02LLowArm_grp', 'Body_sculpt_02LWrist_grp', 'Body_sculpt_04LWrist_grp', 'Body_sculpt_03LWrist_grp', 'Body_sculpt_02LElbow_grp', 'Body_sculpt_03LLowArm_grp', 'Body_sculpt_03LBicep_grp', 'Body_sculpt_02LBicep_grp', 'Body_sculpt_04LBicep_grp', 'Body_sculpt_01LLowArm_grp', 'Body_sculpt_01LElbow_grp', 'Body_sculpt_01LBicep_grp', 'Body_sculpt_04LElbow_grp', 'Body_sculpt_04LShoulder_grp', 'Body_sculpt_09SnoutR_grp', 'Body_sculpt_01LWrist_grp', 'Body_sculpt_01RShoulder_grp', 'Body_sculpt_02RShoulder_grp', 'Body_sculpt_03RBicep_grp', 'Body_sculpt_04RBicep_grp', 'Body_sculpt_03RShoulder_grp', 'Body_sculpt_01RWrist_grp', 'Body_sculpt_04RElbow_grp', 'Body_sculpt_01RLowArm_grp', 'Body_sculpt_04RWrist_grp', 'Body_sculpt_03RWrist_grp', 'Body_sculpt_03RElbow_grp', 'Body_sculpt_01RElbow_grp', 'Body_sculpt_02RWrist_grp', 'Body_sculpt_01RBicep_grp', 'Body_sculpt_02RLowArm_grp', 'Body_sculpt_04RLowArm_grp', 'Body_sculpt_03RLowArm_grp', 'Body_sculpt_02RBicep_grp', 'Body_sculpt_02RElbow_grp']
    Hand_parents = ['Body_sculpt_37LHand_grp', 'Body_sculpt_58LHand_grp', 'Body_sculpt_35LHand_grp', 'Body_sculpt_51LHand_grp', 'Body_sculpt_32LHand_grp', 'Body_sculpt_22LHand_grp', 'Body_sculpt_23LHand_grp', 'Body_sculpt_17LHand_grp', 'Body_sculpt_56LHand_grp', 'Body_sculpt_05LHand_grp', 'Body_sculpt_42LHand_grp', 'Body_sculpt_31LHand_grp', 'Body_sculpt_14LHand_grp', 'Body_sculpt_26LHand_grp', 'Body_sculpt_45LHand_grp', 'Body_sculpt_29LHand_grp', 'Body_sculpt_13LHand_grp', 'Body_sculpt_09LHand_grp', 'Body_sculpt_04LHand_grp', 'Body_sculpt_27LHand_grp', 'Body_sculpt_50LHand_grp', 'Body_sculpt_46LHand_grp', 'Body_sculpt_38LHand_grp', 'Body_sculpt_28LHand_grp', 'Body_sculpt_08LHand_grp', 'Body_sculpt_47LHand_grp', 'Body_sculpt_21LHand_grp', 'Body_sculpt_11LHand_grp', 'Body_sculpt_18LHand_grp', 'Body_sculpt_49LHand_grp', 'Body_sculpt_03LHand_grp', 'Body_sculpt_02LHand_grp', 'Body_sculpt_39LHand_grp', 'Body_sculpt_10LHand_grp', 'Body_sculpt_52LHand_grp', 'Body_sculpt_07LHand_grp', 'Body_sculpt_20LHand_grp', 'Body_sculpt_34LHand_grp', 'Body_sculpt_15LHand_grp', 'Body_sculpt_16LHand_grp', 'Body_sculpt_43LHand_grp', 'Body_sculpt_57LHand_grp', 'Body_sculpt_33LHand_grp', 'Body_sculpt_48LHand_grp', 'Body_sculpt_06LHand_grp', 'Body_sculpt_36LHand_grp', 'Body_sculpt_30LHand_grp', 'Body_sculpt_19LHand_grp', 'Body_sculpt_40LHand_grp', 'Body_sculpt_24LHand_grp', 'Body_sculpt_12LHand_grp', 'Body_sculpt_44LHand_grp', 'Body_sculpt_41LHand_grp', 'Body_sculpt_06RHand_grp', 'Body_sculpt_37RHand_grp', 'Body_sculpt_27RHand_grp', 'Body_sculpt_35RHand_grp', 'Body_sculpt_31RHand_grp', 'Body_sculpt_36RHand_grp', 'Body_sculpt_04RHand_grp', 'Body_sculpt_48RHand_grp', 'Body_sculpt_03RHand_grp', 'Body_sculpt_12RHand_grp', 'Body_sculpt_52RHand_grp', 'Body_sculpt_43RHand_grp', 'Body_sculpt_02RHand_grp', 'Body_sculpt_30RHand_grp', 'Body_sculpt_44RHand_grp', 'Body_sculpt_51RHand_grp', 'Body_sculpt_58RHand_grp', 'Body_sculpt_10RHand_grp', 'Body_sculpt_22RHand_grp', 'Body_sculpt_20RHand_grp', 'Body_sculpt_32RHand_grp', 'Body_sculpt_56RHand_grp', 'Body_sculpt_08RHand_grp', 'Body_sculpt_07RHand_grp', 'Body_sculpt_26RHand_grp', 'Body_sculpt_49RHand_grp', 'Body_sculpt_14RHand_grp', 'Body_sculpt_18RHand_grp', 'Body_sculpt_39RHand_grp', 'Body_sculpt_46RHand_grp', 'Body_sculpt_38RHand_grp', 'Body_sculpt_33RHand_grp', 'Body_sculpt_05RHand_grp', 'Body_sculpt_24RHand_grp', 'Body_sculpt_47RHand_grp', 'Body_sculpt_29RHand_grp', 'Body_sculpt_17RHand_grp', 'Body_sculpt_11RHand_grp', 'Body_sculpt_13RHand_grp', 'Body_sculpt_28RHand_grp', 'Body_sculpt_57RHand_grp', 'Body_sculpt_09RHand_grp', 'Body_sculpt_15RHand_grp', 'Body_sculpt_50RHand_grp', 'Body_sculpt_42RHand_grp', 'Body_sculpt_41RHand_grp', 'Body_sculpt_23RHand_grp', 'Body_sculpt_40RHand_grp', 'Body_sculpt_45RHand_grp', 'Body_sculpt_16RHand_grp', 'Body_sculpt_21RHand_grp', 'Body_sculpt_34RHand_grp', 'Body_sculpt_19RHand_grp']
    Leg_parents = ['Body_sculpt_06LFoot_grp', 'Body_sculpt_07LFoot_grp', 'Body_sculpt_15LFoot_grp', 'Body_sculpt_09LFoot_grp', 'Body_sculpt_04lowlegL_grp', 'Body_sculpt_04legL_grp', 'Body_sculpt_04kneeL_grp', 'Body_sculpt_04LAnkle_grp', 'Body_sculpt_04uplegL_grp', 'Body_sculpt_05LFoot_grp', 'Body_sculpt_14LFoot_grp', 'Body_sculpt_02LFoot_grp', 'Body_sculpt_04LFoot_grp', 'Body_sculpt_02kneeL_grp', 'Body_sculpt_13LFoot_grp', 'Body_sculpt_03lowlegL_grp', 'Body_sculpt_01LFoot_grp', 'Body_sculpt_03LFoot_grp', 'Body_sculpt_01LAnkle_grp', 'Body_sculpt_08LFoot_grp', 'Body_sculpt_03kneeL_grp', 'Body_sculpt_03LAnkle_grp', 'Body_sculpt_02LAnkle_grp', 'Body_sculpt_01kneeL_grp', 'Body_sculpt_10LFoot_grp', 'Body_sculpt_02lowlegL_grp', 'Body_sculpt_12LFoot_grp', 'Body_sculpt_17LFoot_grp', 'Body_sculpt_03uplegL_grp', 'Body_sculpt_16LFoot_grp', 'Body_sculpt_01lowlegL_grp', 'Body_sculpt_11LFoot_grp', 'Body_sculpt_01uplegL_grp', 'Body_sculpt_02uplegL_grp', 'Body_sculpt_04kneeR_grp', 'Body_sculpt_01uplegR_grp', 'Body_sculpt_01kneeR_grp', 'Body_sculpt_04uplegR_grp', 'Body_sculpt_03kneeR_grp', 'Body_sculpt_02kneeR_grp', 'Body_sculpt_03uplegR_grp', 'Body_sculpt_02uplegR_grp', 'Body_sculpt_04legR_grp', 'Body_sculpt_03RFoot_grp', 'Body_sculpt_07RFoot_grp', 'Body_sculpt_03RAnkle_grp', 'Body_sculpt_13RFoot_grp', 'Body_sculpt_09RFoot_grp', 'Body_sculpt_12RFoot_grp', 'Body_sculpt_10RFoot_grp', 'Body_sculpt_02lowlegR_grp', 'Body_sculpt_01RFoot_grp', 'Body_sculpt_04lowlegR_grp', 'Body_sculpt_01RAnkle_grp', 'Body_sculpt_05RFoot_grp', 'Body_sculpt_16RFoot_grp', 'Body_sculpt_02RAnkle_grp', 'Body_sculpt_08RFoot_grp', 'Body_sculpt_17RFoot_grp', 'Body_sculpt_04RFoot_grp', 'Body_sculpt_11RFoot_grp', 'Body_sculpt_02RFoot_grp', 'Body_sculpt_14RFoot_grp', 'Body_sculpt_03lowlegR_grp', 'Body_sculpt_04RAnkle_grp', 'Body_sculpt_01lowlegR_grp', 'Body_sculpt_15RFoot_grp', 'Body_sculpt_06RFoot_grp']
    Body_parents = ['Body_sculpt_02BackM_grp', 'Body_sculpt_02FrontR_grp', 'Body_sculpt_04BackR_grp', 'Body_sculpt_01legL_grp', 'Body_sculpt_02ShdrR_grp', 'Body_sculpt_04RShoulder_grp', 'Body_sculpt_02BackL_grp', 'Body_sculpt_05FrontM_grp', 'Body_sculpt_03BackR_grp', 'Body_sculpt_04FrontM_grp', 'Body_sculpt_02SideR_grp', 'Body_sculpt_06BackM_grp', 'Body_sculpt_02BackR_grp', 'Body_sculpt_02FrontM_grp', 'Body_sculpt_06ShdrR_grp', 'Body_sculpt_03FrontM_grp', 'Body_sculpt_03legR_grp', 'Body_sculpt_05BackM_grp', 'Body_sculpt_05FrontR_grp', 'Body_sculpt_02FrontL_grp', 'Body_sculpt_06FrontR_grp', 'Body_sculpt_01ShdrR_grp', 'Body_sculpt_01FrontL_grp', 'Body_sculpt_03BackL_grp', 'Body_sculpt_01BackR_grp', 'Body_sculpt_03BackM_grp', 'Body_sculpt_01SideL_grp', 'Body_sculpt_02legR_grp', 'Body_sculpt_03ClavR_grp', 'Body_sculpt_02SideL_grp', 'Body_sculpt_04FrontL_grp', 'Body_sculpt_02Under_grp', 'Body_sculpt_01SideR_grp', 'Body_sculpt_01BackL_grp', 'Body_sculpt_05BackL_grp', 'Body_sculpt_02ClavL_grp', 'Body_sculpt_09BackM_grp', 'Body_sculpt_05ShdrR_grp', 'Body_sculpt_08BackM_grp', 'Body_sculpt_03FrontR_grp', 'Body_sculpt_04BackL_grp', 'Body_sculpt_03ShdrL_grp', 'Body_sculpt_03SideR_grp', 'Body_sculpt_07BackM_grp', 'Body_sculpt_03legL_grp', 'Body_sculpt_06FrontL_grp', 'Body_sculpt_03Under_grp', 'Body_sculpt_01BackM_grp', 'Body_sculpt_06FrontM_grp', 'Body_sculpt_01legR_grp', 'Body_sculpt_03SideL_grp', 'Body_sculpt_06ShdrL_grp', 'Body_sculpt_02legL_grp', 'Body_sculpt_05FrontL_grp', 'Body_sculpt_03ShdrR_grp', 'Body_sculpt_01FrontR_grp', 'Body_sculpt_01Under_grp', 'Body_sculpt_07FrontM_grp', 'Body_sculpt_03FrontL_grp', 'Body_sculpt_05BackR_grp', 'Body_sculpt_02ClavR_grp', 'Body_sculpt_05ShdrL_grp', 'Body_sculpt_04FrontR_grp', 'Body_sculpt_01FrontM_grp', 'Body_sculpt_03ClavL_grp', 'Body_sculpt_02ShdrL_grp', 'Body_sculpt_04BackM_grp', 'Body_sculpt_01ClavR_grp', 'Body_sculpt_01ClavL_grp']
    Eye_parents = ['Body_sculpt_04EyeLidL_grp', 'Body_sculpt_05EyeLidL_grp', 'Body_sculpt_02EyeLidL_grp', 'Body_sculpt_08EyeOuterR_grp', 'Body_sculpt_07EyeLidL_grp', 'Body_sculpt_06EyeOuterL_grp', 'Body_sculpt_01EyeLidL_grp', 'Body_sculpt_03EyeLidL_grp', 'Body_sculpt_04EyeOuterL_grp', 'Body_sculpt_08EyeOuterL_grp', 'Body_sculpt_01EyeOuterL_grp', 'Body_sculpt_03EyeOuterL_grp', 'Body_sculpt_06EyeLidL_grp', 'Body_sculpt_08EyeLidL_grp', 'Body_sculpt_02EyeOuterL_grp', 'Body_sculpt_07EyeOuterL_grp', 'Body_sculpt_05EyeOuterL_grp', 'Body_sculpt_05EyeLidR_grp', 'Body_sculpt_03EyeLidR_grp', 'Body_sculpt_06EyeOuterR_grp', 'Body_sculpt_06EyeLidR_grp', 'Body_sculpt_04EyeLidR_grp', 'Body_sculpt_07EyeLidR_grp', 'Body_sculpt_05EyeOuterR_grp', 'Body_sculpt_01EyeLidR_grp', 'Body_sculpt_08EyeLidR_grp', 'Body_sculpt_07EyeOuterR_grp', 'Body_sculpt_04EyeOuterR_grp', 'Body_sculpt_02EyeLidR_grp', 'Body_sculpt_03EyeOuterR_grp', 'Body_sculpt_02EyeOuterR_grp', 'Body_sculpt_01EyeOuterR_grp']
    Brow_parents = ['Body_sculpt_04NR_grp', 'Body_sculpt_01SideR1_grp', 'Body_sculpt_02SideR1_grp', 'Body_sculpt_04TopR_grp', 'Body_sculpt_02BrowR_grp', 'Body_sculpt_01BrowR_grp', 'Body_sculpt_04BrowR_grp', 'Body_sculpt_01BrowM_grp', 'Body_sculpt_03BrowL_grp', 'Body_sculpt_04TopL_grp', 'Body_sculpt_03BrowR_grp', 'Body_sculpt_04BrowL_grp', 'Body_sculpt_02BrowL_grp', 'Body_sculpt_04TopM_grp', 'Body_sculpt_01BrowL_grp', 'Body_sculpt_04NL_grp', 'Body_sculpt_02SideL1_grp', 'Body_sculpt_01SideL1_grp', 'Body_sculpt_03SideL1_grp', 'Body_sculpt_05SideL_grp', 'Body_sculpt_05SideR_grp', 'Body_sculpt_04SideR_grp', 'Body_sculpt_04SideL_grp', 'Body_sculpt_03SideR1_grp']
    Snout_parents = ['Body_sculpt_08NoseL_grp', 'Body_sculpt_01NR_grp', 'Body_sculpt_02NostralR_grp', 'Body_sculpt_04NostralR_grp', 'Body_sculpt_04SnoutL_grp', 'Body_sculpt_03NR_grp', 'Body_sculpt_09SnoutL_grp', 'Body_sculpt_02UnderEyeL_grp', 'Body_sculpt_08NoseR_grp', 'Body_sculpt_02MidLipL_grp', 'Body_sculpt_01LLipM_grp', 'Body_sculpt_06SnoutL_grp', 'Body_sculpt_10SnoutM_grp', 'Body_sculpt_04LLipR_grp', 'Body_sculpt_02UnderEyeR_grp', 'Body_sculpt_06ULipL_grp', 'Body_sculpt_09EyeOuterR_grp', 'Body_sculpt_08LLipL_grp', 'Body_sculpt_02ULipR_grp', 'Body_sculpt_01SnoutL_grp', 'Body_sculpt_01UnderEyeL_grp', 'Body_sculpt_07SnoutL_grp', 'Body_sculpt_02NostralL_grp', 'Body_sculpt_01NostralL_grp', 'Body_sculpt_07ULipL_grp', 'Body_sculpt_02SnoutL_grp', 'Body_sculpt_06MidLipL_grp', 'Body_sculpt_04MidLipL_grp', 'Body_sculpt_04MidLipR_grp', 'Body_sculpt_05MidLipL_grp', 'Body_sculpt_01ULipM_grp', 'Body_sculpt_03ULipL_grp', 'Body_sculpt_05NoseL_grp', 'Body_sculpt_02UJawR_grp', 'Body_sculpt_04UJawM_grp', 'Body_sculpt_02UJawL_grp', 'Body_sculpt_09ULipL_grp', 'Body_sculpt_07ULipR_grp', 'Body_sculpt_05LLipR_grp', 'Body_sculpt_05SnoutL_grp', 'Body_sculpt_01UJawL_grp', 'Body_sculpt_05LLipL_grp', 'Body_sculpt_05MidLipR_grp', 'Body_sculpt_06LLipL_grp', 'Body_sculpt_07LLipL_grp', 'Body_sculpt_02NL_grp', 'Body_sculpt_03NostralR_grp', 'Body_sculpt_07NoseM_grp', 'Body_sculpt_02MidLipR_grp', 'Body_sculpt_01UJawR_grp', 'Body_sculpt_02ULipL_grp', 'Body_sculpt_03NL_grp', 'Body_sculpt_08SnoutR_grp', 'Body_sculpt_07LLipR_grp', 'Body_sculpt_06NoseM_grp', 'Body_sculpt_05NoseR_grp', 'Body_sculpt_09LLipL_grp', 'Body_sculpt_09EyeOuterL_grp', 'Body_sculpt_01NL_grp', 'Body_sculpt_06MidLipR_grp', 'Body_sculpt_04SnoutR_grp', 'Body_sculpt_03UJawM_grp', 'Body_sculpt_03LLipL_grp', 'Body_sculpt_05SnoutR_grp', 'Body_sculpt_03MidLipR_grp', 'Body_sculpt_04NostralL_grp', 'Body_sculpt_02LLipL_grp', 'Body_sculpt_03NostralL_grp', 'Body_sculpt_01UnderEyeR_grp', 'Body_sculpt_02NoseM_grp', 'Body_sculpt_09LLipR_grp', 'Body_sculpt_07SnoutR_grp', 'Body_sculpt_08ULipL_grp', 'Body_sculpt_03ULipR_grp', 'Body_sculpt_11SnoutM_grp', 'Body_sculpt_01SnoutR_grp', 'Body_sculpt_05ULipL_grp', 'Body_sculpt_13SnoutM_grp', 'Body_sculpt_06LLipR_grp', 'Body_sculpt_02SnoutR_grp', 'Body_sculpt_03NoseM_grp', 'Body_sculpt_06ULipR_grp', 'Body_sculpt_08SnoutL_grp', 'Body_sculpt_06SnoutR_grp', 'Body_sculpt_03LLipR_grp', 'Body_sculpt_01MidLipM_grp', 'Body_sculpt_03SnoutL_grp', 'Body_sculpt_04NoseL_grp', 'Body_sculpt_04ULipR_grp', 'Body_sculpt_01NostralR_grp', 'Body_sculpt_01NoseM_grp', 'Body_sculpt_08ULipR_grp', 'Body_sculpt_09ULipR_grp', 'Body_sculpt_04ULipL_grp', 'Body_sculpt_02LLipR_grp', 'Body_sculpt_04NoseR_grp', 'Body_sculpt_02NR_grp', 'Body_sculpt_05ULipR_grp', 'Body_sculpt_07MidLipR_grp', 'Body_sculpt_03MidLipL_grp', 'Body_sculpt_08LLipR_grp', 'Body_sculpt_03SnoutR_grp', 'Body_sculpt_04LLipL_grp', 'Body_sculpt_02UJawM_grp', 'Body_sculpt_01UJawM_grp', 'Body_sculpt_05UJawR_grp', 'Body_sculpt_05UJawL_grp', 'Body_sculpt_04UJawR_grp', 'Body_sculpt_04UJawL_grp', 'Body_sculpt_03UJawL_grp', 'Body_sculpt_03UJawR_grp', 'Body_sculpt_07MidLipL_grp']
    Cheek_parents = ['Body_sculpt_01CheekR_grp', 'Body_sculpt_07CheekL_grp', 'Body_sculpt_09CheekR_grp', 'Body_sculpt_07CheekR_grp', 'Body_sculpt_04CheekL_grp', 'Body_sculpt_06CheekR_grp', 'Body_sculpt_02CheekL_grp', 'Body_sculpt_05CheekL_grp', 'Body_sculpt_03CheekR_grp', 'Body_sculpt_02CheekR_grp', 'Body_sculpt_09CheekL_grp', 'Body_sculpt_08CheekL_grp', 'Body_sculpt_04CheekR_grp', 'Body_sculpt_01CheekL_grp', 'Body_sculpt_08CheekR_grp', 'Body_sculpt_03CheekL_grp', 'Body_sculpt_06CheekL_grp', 'Body_sculpt_05CheekR_grp']
    Ear_parents = ['Body_sculpt_03EarR_grp', 'Body_sculpt_07EarR_grp', 'Body_sculpt_03EarL_grp', 'Body_sculpt_04EarL_grp', 'Body_sculpt_05EarL_grp', 'Body_sculpt_01EarL_grp', 'Body_sculpt_02EarL_grp', 'Body_sculpt_02EarR_grp', 'Body_sculpt_06EarL_grp', 'Body_sculpt_07EarL_grp', 'Body_sculpt_01EarR_grp', 'Body_sculpt_05EarR_grp', 'Body_sculpt_06EarR_grp', 'Body_sculpt_04EarR_grp']

    for part in ["Arm", "Hand", "Leg", "Body", "Eye", "Brow", "Snout", "Cheek", "Ear"]:
        part_list = locals()[f'{part}_parents']
        mc.group(part_list, name=f'{part}_vis_group')
        mc.connectAttr(f'Options_ctrl.{part}_Sculpt', f'{part}_vis_group.visibility', force=True)

def skin_sculpt_jnts():
    dir = f'{groups}/bobo/character/Rigs/Bobo/SkinFiles'
    rWeightNgIO.read_skin("Bobo_UBM", dir, 'Bobo_CurveNet')



def Clean_up_SculptJoints():
    joint_grp = 'Body_defpoints_grp'
    Control_grp = 'Body_Controls_grp'
    NUll_jnt = 'curve_net_null_joint'

    mc.parent(Control_grp, 'RIG')
    mc.parent(joint_grp, 'SKEL')
    mc.parent(NUll_jnt, 'SKEL')
    
    skin_sculpt_jnts()
    rename_group_objects(Control_grp)
    rename_group_objects(joint_grp)
    Fix_Colors()
    make_sets()
