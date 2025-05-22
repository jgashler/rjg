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


def run(character, mp=None, gp=None, ep=None, cp=None, sp=None, pp=None, face=True, previs=False):
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
    
    not_previs = False if previs or character in ['DungeonMonster', 'Jett', 'Blitz', 'Susaka'] else True
    bony = False if (character in ['Robin', 'Rayden', 'Jett', 'Blitz', 'Bobo', "BoboQuad", 'Gretchen', 'Susaka']) else True

    body_mesh = f'{character}_UBM'


    mc.file(new=True, f=True)

    ### BUILD SCRIPT
    root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
    if ep:
        extras = rFile.import_hierarchy(ep, parent='MODEL')[0]
    mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)
    
    if character == 'Skeleton':
        body_mesh = mc.listRelatives('skeleton_grp', children=True)
    elif character == 'DungeonMonster':
        body_mesh = mc.listRelatives('dungeonmonster_FINAL_GEO', children=True)
    #elif character = "BoboQuad":['Robin', 'Rayden', 'Jett', 'Blitz', 'Bobo', "BoboQuad", 'Gretchen', 'Susaka'])
    #   body_mesh = 'Bobo_UBM'

    hip = rBuild.build_module(module_type='hip', side='M', part='COG', guide_list=['Hips'], ctrl_scale=50, cog_shape='quad_arrow', waist_shape='circle')
    chest = rBuild.build_module(module_type='chest', side='M', part='chest', guide_list=['Spine2'], ctrl_scale=70, chest_shape='circle')
    spine = rBuild.build_module(module_type='spine', side='M', part='spine', guide_list=['Hips', 'Spine', 'Spine1', 'Spine2'], ctrl_scale=1, mid_ctrl=True, joint_num=4 if character not in ['Jett', 'Blitz', 'Susaka'] else 6)
    neck = rBuild.build_module(module_type='biped_limb', side='M', part='neck', guide_list=['Neck', 'Neck1', 'Head'], ctrl_scale=10, bendy=False, twisty=False, stretchy=False, segments=1, create_ik=False)
    head = rBuild.build_module(module_type='head', side='M', part='head', guide_list=['Head'], ctrl_scale=50)

    if character == "Skeleton":
        jaw = rBuild.build_module(module_type='hinge', side='M', part='jaw', guide_list=['JawBase', 'JawTip'], ctrl_scale=10, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')

    # dungeon monster tail, jaw, ribcage
    if character == "DungeonMonster":
        tail = rBuild.build_module(module_type='tail', side='M', part='tail', guide_list=['Tail_' + str(t) for t in range(1, 8)], ctrl_scale=25, pad=2)
        jaw = rBuild.build_module(module_type='hinge', side='M', part='jaw', guide_list=['JawBase', 'JawTip'], ctrl_scale=40, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')
        
        # this code block fixes the splineIK in the spine to work for quadrupedal characters
        mc.setAttr("spine_M_spline_IKH.dForwardAxis", 4)
        mc.setAttr("spine_M_spline_IKH.dWorldUpAxis", 0)
        mc.setAttr("spine_M_spline_IKH.dWorldUpVectorY", 1)
        mc.setAttr("spine_M_spline_IKH.dWorldUpVectorZ", 0)
        mc.setAttr("spine_M_spline_IKH.dWorldUpVectorEndY", 1)
        mc.setAttr("spine_M_spline_IKH.dWorldUpVectorEndZ", 0)

        for side in ['L', 'R']:
            for sw in range(1, 11):
                sword = str(sw).zfill(2)
                if int(sword) <= 5:
                    par = 'chest_M_JNT'
                else:
                    par = 'spine_M_03_JNT'
                try:
                    rib = rBuild.build_module(module_type='finger', side=side, part='rib_' + sword, guide_list=[f'sword_{sword}_{side}_{t}_JNT' for t in ['top', 'mid', 'end']], ctrl_scale=12, par_ctrl=par)
                except Exception as e:
                    mc.warning(e)
                    mc.delete(f'rib_{sword}_{side}_01_fk_CTRL_CNST_GRP')
                    continue
        # mc.select('rib_*_JNT', 'sword_02_R_geo', 'sword_07_R_geo', 'sword_06_R_geo', 'sword_04_R_geo', 'sword_03_R_geo', 'sword_01_R_geo', 'sword_08_R_geo', 'sword_06_L_geo', 'sword_02_L_geo', 'sword_01_L_geo', 'sword_04_L_geo', 'sword_07_L_geo', 'sword_05_L_geo', 'sword_10_L_geo')
        # mc.bindSkin(tsb=True, cj=False)
        for side in ['L', 'R']:
            for n in range(10):
                try:
                    mc.select(f'rib_0{n}_{side}_01_JNT', f'sword_0{n}_{side}_geo')
                    mc.bindSkin(tsb=False, cj=False)
                except:
                    continue
        mc.select('rib_10_L_01_JNT', 'sword_10_L_geo')
        mc.bindSkin(tsb=True, cj=False)
        

    if character == "BoboQuad":
        tail = rBuild.build_module(module_type='tail', side='M', part='tail', guide_list=['Tail_' + str(t) for t in range(1, 3)], ctrl_scale=25, pad=2)
        #jaw = rBuild.build_module(module_type='hinge', side='M', part='jaw', guide_list=['JawBase', 'JawTip'], ctrl_scale=40, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')
        


    # previs face rig
    if not not_previs and not bony and character != 'Jett' and character != 'Blitz' and character != 'Bobo' and character != 'Susaka':
        arbit_guides = mc.listRelatives('FaceGuides', children=True)
        for ag in arbit_guides:
            if ag in ['lipLower']:#, 'lipLeft', 'lipRight']:
                pj = 'jaw_M_JNT'
                pc = 'jaw_M_M_CTRL'
            else:
                pj = 'head_M_JNT'
                pc = 'head_M_01_CTRL'           
            arb = rBuild.build_module(module_type='arbitrary', side='M', part=ag, guide_list=mc.getAttr(ag + '.translate'), ctrl_scale=1, par_jnt=pj, par_ctrl=pc)
        jaw = rBuild.build_module(module_type='hinge', side='M', part='jaw', guide_list=['JawBase', 'JawTip'], ctrl_scale=40, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')
        eyes = rBuild.build_module(module_type='look_eyes', side='M', part='lookEyes', guide_list=['eye_L', 'eye_R', 'look_L', 'look_R'], ctrl_scale=1, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')

    if not not_previs and character == 'Bobo':
        arbit_guides = mc.listRelatives('FaceGuides', children=True)
        for ag in arbit_guides:
            if ag in ['lipLower']:#, 'lipLeft', 'lipRight']:
                pj = 'jaw_M_JNT'
                pc = 'jaw_M_M_CTRL'
            else:
                pj = 'head_M_JNT'
                pc = 'head_M_01_CTRL'           
            arb = rBuild.build_module(module_type='arbitrary', side='M', part=ag, guide_list=mc.getAttr(ag + '.translate'), ctrl_scale=1, par_jnt=pj, par_ctrl=pc)
        jaw = rBuild.build_module(module_type='hinge', side='M', part='jaw', guide_list=['JawBase', 'JawTip'], ctrl_scale=40, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')
        eyes = rBuild.build_module(module_type='look_eyes', side='M', part='lookEyes', guide_list=['eye_L', 'eye_R', 'look_L', 'look_R'], ctrl_scale=1, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')
    
    if character == 'Susaka':
        arbit_guides = mc.listRelatives('FaceGuides', children=True)
        for ag in arbit_guides:
            if ag in ['lipLower', 'lipLowerL', 'lipLowerR']:#, 'lipLeft', 'lipRight']:
                pj = 'jaw_M_JNT'
                pc = 'jaw_M_M_CTRL'
            else:
                pj = 'head_M_JNT'
                pc = 'head_M_01_CTRL'           
            arb = rBuild.build_module(module_type='arbitrary2', side='M', part=ag, guide_list=ag, ctrl_scale=1, par_jnt=pj, par_ctrl=pc)
        #for ag in ['browLeft1', 'browLeft2', 'browLeft3']: #['browLeft1', 'browLeft2', 'browLeft3', 'browRight1', 'browRight2', 'browRight3']
        #    arb = rBuild.build_module(module_type='arbitrary', side='L', part=ag, guide_list=mc.getAttr(ag + '.translate'), ctrl_scale=1, par_jnt=browLeft_M_JNT, par_ctrl=browLeft_M_M_CTRL)
        #for ag in ['browRight1', 'browRight2', 'browRight3']: #['browLeft1', 'browLeft2', 'browLeft3', 'browRight1', 'browRight2', 'browRight3']
        #    arb = rBuild.build_module(module_type='arbitrary', side='L', part=ag, guide_list=mc.getAttr(ag + '.translate'), ctrl_scale=1, par_jnt=browLeft_M_JNT, par_ctrl=browLeft_M_M_CTRL)


        jaw = rBuild.build_module(module_type='hinge', side='M', part='jaw', guide_list=['JawBase', 'JawTip'], ctrl_scale=40, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')
        eyes = rBuild.build_module(module_type='look_eyes', side='M', part='lookEyes', guide_list=['eye_L', 'eye_R', 'look_L', 'look_R'], ctrl_scale=1, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')
    

    for fs in ['Left', 'Right']:    
        arm = rBuild.build_module(module_type='biped_limb', side=fs[0], part='arm', guide_list=[fs + piece for piece in ['Arm', 'ForeArm', 'Hand']], offset_pv=50, ctrl_scale=5, bendy=not_previs, twisty=not_previs, stretchy=not_previs, segments=4 if not_previs else 1)
        clavicle = rBuild.build_module(module_type='clavicle', side=fs[0], part='clavicle', guide_list=[fs + piece for piece in ['Shoulder', 'Arm']], local_orient=False, ctrl_scale=9) 
        hand = rBuild.build_module(module_type='hand', side=fs[0], part='hand', guide_list=[fs + 'Hand'], ctrl_scale=8)
        
        leg = rBuild.build_module(module_type='biped_limb', side=fs[0], part='leg', guide_list=[fs + piece for piece in ['UpLeg', 'Leg', 'Foot']], offset_pv=50, ctrl_scale=8, bendy=not_previs, twisty=not_previs, stretchy=not_previs, segments=4 if not_previs else 1)
        foot = rBuild.build_module(module_type='foot', side=fs[0], part='foot', guide_list=[fs + piece for piece in ['Foot', 'ToeBase', 'Toe_End']], ctrl_scale=10, toe_piv=fs+'ToePiv', heel_piv=fs+'HeelPiv', in_piv=fs+'In', out_piv=fs+'Out')
        
        fingers = []
        
        ffs = ['Index', 'Middle', 'Ring', 'Pinky']
        if character == 'Bobo':
            ffs = ffs[:-1]
        for f in ffs:
            finger = rBuild.build_module(module_type='finger', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num) for num in range(4 if character in ['DungeonMonster', 'BoboQuad'] else 5)], ctrl_scale=1, fk_shape='lollipop')
            fingers.append(finger)
        thumb = rBuild.build_module(module_type='finger', side=fs[0], part='fingerThumb', guide_list=[fs + 'HandThumb' + str(num+1) for num in range(4)], ctrl_scale=1, fk_shape='lollipop')
        fingers.append(thumb) 

    if character == 'Bobo':
        tail = rBuild.build_module(module_type='tail', side='M', part='tail', guide_list=['Tail' + str(t) for t in range(1, 4)], ctrl_scale=10, pad=2)
        # for ar in ('BellyLowerM', 'BellyLowerL1', 'BellyLowerL2', 'BellyLowerR1', 'BellyLowerR2'):
        rb = rBuild.build_module(module_type='arbitrary', side='M', part='BellyHighM', guide_list=mc.getAttr('BellyHighM' + '.translate'), ctrl_scale=15, par_jnt='spine_M_01_JNT', par_ctrl='spine_02_FK_M_CTRL')
        
        if not not_previs:
            for fs in ['Left', 'Right']:
                ear = rBuild.build_module(module_type='ear', side=fs[0], part='ear', guide_list=[str(fs) + 'Ear' + str(t) for t in range(1, 4)], ctrl_scale=10, pad=2)



        '''if character == 'BoboQuad':
            ffs = ffs[:-1]
        for f in ffs:
            finger = rBuild.build_module(module_type='finger', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num) for num in range(4 if character == 'DungeonMonster' else 5)], ctrl_scale=1, fk_shape='lollipop')
            fingers.append(finger)
        thumb = rBuild.build_module(module_type='finger', side=fs[0], part='fingerThumb', guide_list=[fs + 'HandThumb' + str(num+1) for num in range(4)], ctrl_scale=1, fk_shape='lollipop')
        fingers.append(thumb) '''
           
    if character in ['Jett', 'Blitz']:
        rBuild.build_module(module_type='UeCorrective', side='L', part='upperarmCorrective', guide_list=['upperarm_out_l', 'upperarm_fwd_l', 'upperarm_bck_l', 'upperarm_in_l', 'upperarm_twist_02_l', 'upperarm_twist_01_l' ], ctrl_scale=1, par_jnt='arm_L_01_JNT', par_ctrl='arm_L_01_fk_CTRL', root_loc='LeftArm')
        rBuild.build_module(module_type='UeCorrective', side='R', part='upperarmCorrective', guide_list=['upperarm_out_r', 'upperarm_fwd_r', 'upperarm_bck_r', 'upperarm_in_r', 'upperarm_twist_02_r', 'upperarm_twist_01_r' ], ctrl_scale=1, par_jnt='arm_R_01_JNT', par_ctrl='arm_R_01_fk_CTRL', root_loc='RightArm')

        rBuild.build_module(module_type='UeCorrective', side='L', part='lowerarmCorrective', guide_list=['lowerarm_in_l', 'lowerarm_out_l', 'lowerarm_fwd_l', 'lowerarm_bck_l', 'lowerarm_twist_02_l', 'lowerarm_twist_01_l' ], ctrl_scale=1, par_jnt='arm_L_02_JNT', par_ctrl='arm_L_02_fk_CTRL', root_loc='LeftForeArm')
        rBuild.build_module(module_type='UeCorrective', side='R', part='lowerarmCorrective', guide_list=['lowerarm_in_r', 'lowerarm_out_r', 'lowerarm_fwd_r', 'lowerarm_bck_r', 'lowerarm_twist_02_r', 'lowerarm_twist_01_r'], ctrl_scale=1, par_jnt='arm_R_02_JNT', par_ctrl='arm_R_02_fk_CTRL', root_loc='RightForeArm')
        
        rBuild.build_module(module_type='UeCorrective', side='L', part='thighCorrective', guide_list=['thigh_fwd_l', 'thigh_out_l', 'thigh_fwd_lwr_l', 'thigh_in_l', 'thigh_bck_lwr_l', 'thigh_bck_l', 'thigh_twist_02_l', 'thigh_twist_01_l' ], ctrl_scale=1, par_jnt='leg_L_01_JNT', par_ctrl='leg_L_01_JNT', root_loc='LeftUpLeg')
        rBuild.build_module(module_type='UeCorrective', side='R', part='thighCorrective', guide_list=['thigh_fwd_r', 'thigh_out_r', 'thigh_fwd_lwr_r', 'thigh_in_r', 'thigh_bck_lwr_r', 'thigh_bck_r', 'thigh_twist_02_r', 'thigh_twist_01_r' ], ctrl_scale=1, par_jnt='leg_R_01_JNT', par_ctrl='leg_R_01_JNT', root_loc='RightUpLeg')
        
        rBuild.build_module(module_type='UeCorrective', side='L', part='calfCorrective', guide_list=['calf_knee_l', 'calf_kneeBack_l', 'calf_twist_02_l', 'calf_twist_01_l' ], ctrl_scale=1, par_jnt='leg_L_02_JNT', par_ctrl='leg_L_02_JNT', root_loc='LeftLeg')
        rBuild.build_module(module_type='UeCorrective', side='R', part='calfCorrective', guide_list=['calf_knee_r', 'calf_kneeBack_r', 'calf_twist_02_r', 'calf_twist_01_r' ], ctrl_scale=1, par_jnt='leg_R_02_JNT', par_ctrl='leg_R_02_JNT', root_loc='RightLeg')
    
        ### new
        # /groups/skyguard/Anim/Rigging/Jett/jett_full_guides.mb
        
        for guide in [('ankle_bck_r', 'leg_R_03_JNT', 'leg_R_03_JNT'),
                      ('ankle_fwd_r', 'leg_R_03_JNT', 'leg_R_03_JNT'),
                      ('ankle_bck_l', 'leg_L_03_JNT', 'leg_L_03_JNT'),
                      ('ankle_fwd_l', 'leg_L_03_JNT', 'leg_L_03_JNT'),
                      ('clavicle_pec_r', 'chest_M_JNT', 'chest_M_02_CTRL'),
                      ('clavicle_pec_l', 'chest_M_JNT', 'chest_M_02_CTRL'),
                      ('spine_04_latissimus_l', 'chest_M_JNT', 'chest_M_02_CTRL'),
                      ('spine_04_latissimus_r', 'chest_M_JNT', 'chest_M_02_CTRL'),
                      ('clavicle_scap_r', 'clavicle_R_01_JNT', 'clavicle_R_CTRL'),
                      ('clavicle_scap_l', 'clavicle_L_01_JNT', 'clavicle_L_CTRL'),
                      ('clavicle_out_r', 'clavicle_R_01_JNT', 'clavicle_R_CTRL'),
                      ('clavicle_out_l', 'clavicle_L_01_JNT', 'clavicle_L_CTRL'),
                      ('upperarm_tricep_l', 'upperarm_twist_02_l_L_Bind_JNT_L_JNT', 'arm_L_01_fk_CTRL'),
                      ('upperarm_bicep_l', 'upperarm_twist_02_l_L_Bind_JNT_L_JNT', 'arm_L_01_fk_CTRL'),
                      ('upperarm_tricep_r', 'upperarm_twist_02_r_R_Bind_JNT_R_JNT', 'arm_R_01_fk_CTRL'),
                      ('upperarm_bicep_r', 'upperarm_twist_02_r_R_Bind_JNT_R_JNT', 'arm_R_01_fk_CTRL'),
                      ('wrist_inner_r', 'arm_R_03_JNT', 'arm_R_03_fk_CTRL'),
                      ('wrist_outer_r', 'arm_R_03_JNT', 'arm_R_03_fk_CTRL'),
                      ('wrist_inner_l', 'arm_L_03_JNT', 'arm_L_03_fk_CTRL'),
                      ('wrist_outer_l', 'arm_L_03_JNT', 'arm_L_03_fk_CTRL'),
                      ]:
            try:
                rBuild.build_module(module_type='arbitrary', side='M', part=guide[0], guide_list=mc.getAttr(guide[0] + '.translate'), par_jnt=guide[1], par_ctrl=guide[2], ctrl_scale=1)
            except Exception as e:
                mc.warning(e)

        mc.joint('calf_twist_02_l_L_Bind_JNT_L_JNT', n='calf_twistCor_02_l')
        mc.joint('calf_twist_02_r_R_Bind_JNT_R_JNT', n='calf_twistCor_02_r')
        mc.joint('thigh_twist_02_l_L_Bind_JNT_L_JNT', n='thigh_twistCor_02_l')
        mc.joint('thigh_twist_02_r_R_Bind_JNT_R_JNT', n='thigh_twistCor_02_r')
        mc.joint('thigh_twist_01_l_L_Bind_JNT_L_JNT', n='thigh_twistCor_01_l')
        mc.joint('thigh_twist_01_r_R_Bind_JNT_R_JNT', n='thigh_twistCor_01_r')
        mc.joint('upperarm_twist_02_l_L_Bind_JNT_L_JNT', n='upperarm_twistCor_02_l')
        mc.joint('upperarm_twist_02_r_R_Bind_JNT_R_JNT', n='upperarm_twistCor_02_r')
        mc.joint('upperarm_twist_01_l_L_Bind_JNT_L_JNT', n='upperarm_twistCor_01_l')
        mc.joint('upperarm_twist_01_r_R_Bind_JNT_R_JNT', n='upperarm_twistCor_01_r')

    if character in ['Susaka', 'Drummer']:
        mc.parent("UE_Correctives", w=True)
    if character in ['Bobo', 'Bobo_quad']:
        mc.parent("CurveNet_Guide_Group", w=True)

    mc.delete('Guides')
    
    
    if bony and pp:
        import rjg.build_scripts.dm_bone_dict as dm_bd
        import rjg.build_scripts.sk_bone_dict as sk_bd
        reload(dm_bd)
        reload(sk_bd)
        
        if character == 'DungeonMonster':
            bone_dict = dm_bd.BoneDict().bone_dict
        elif character == 'Skeleton':
            bone_dict = sk_bd.BoneDict().bone_dict
        
        bone_locs = rFile.import_hierarchy(pp)   
        bone_locs = mc.listRelatives('bone_locs', children=True)
        
        bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
        for j in bind_joints:
            mc.deleteAttr(j + '.bindJoint')

        if character == 'DungeonMonster':
            for b in bone_dict:
                mc.select(f'{b}.vtx[:]')
                mc.componentTag(create=True, ntn=b[:-4])


            
        float_bone_grp = mc.group(empty=True, name='floatBones_F')
        mc.parent(float_bone_grp, 'RIG')
        for b in bone_locs:
            bone_name = b[:-4]
            if bone_name in bone_dict:
                par_jnt = bone_dict[bone_name][0]
                par_ctrl = bone_dict[bone_name][1]
                if len(bone_dict[bone_name]) > 2:
                    print("TODO: handle extra cases")
            else:
                #print(f'    Bone {bone_name} not found in bone dictionary')
                par_jnt = 'root_M_JNT'
                par_ctrl = 'root_02_M_CTRL'
            floatBone = rBuild.build_module(module_type='float_bone', side='F', part=b[:-4], guide_list=[b], ctrl_scale=2, par_jnt=par_jnt, par_ctrl=par_ctrl)
            mc.parent(floatBone.part_grp, float_bone_grp)
            #mc.connectJoint(floatBone.floatBone_jnt, par_jnt, pm=True)
            mc.connectJoint(floatBone.bind_joints[0], par_jnt, pm=True)
            mc.parentConstraint(par_jnt, floatBone.floatBone_ctrl.top, mo=True)


            
        mc.delete('bone_locs')

            #fix UeCorrectives


    ### DEFAULT SKIN
    if not bony:
        bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
        geo = mc.ls(body_mesh)
        for g in geo:
            skc = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1, bindMethod=0)[0]
            mc.setAttr(skc + '.dqsSupportNonRigid', 1)
    else:
        geo = mc.ls(body_mesh)
        bone_skcs = []
        for g in geo:
            if g == 'swords':
                continue
            mc.select(g, g + '_F_JNT')
            skc = mc.skinCluster(g + '_F_JNT', g, tsb=True)
            bone_skcs.append(skc)
        try:
            mc.select(geo)
            mc.select('eye_L_geo', 'eye_R_geo', deselect=True)
            geo = mc.ls(selection=True)
            # merged = mc.polyUniteSkinned(geo, ch=1, mergeUVSets=1)
            # mc.rename(merged[0], 'skeleton_geo')
            # mc.rename(merged[1], 'skeleton_skc')
            # mc.parent('skeleton_geo', 'MODEL')
            mc.parent('eye_*_geo', 'MODEL')
            #mc.delete('dungeonmonster_FINAL_GEO')
        except Exception as e:
            mc.warning(e)


    ### SKIN/CURVE IO
    try:
        import ngSkinTools2; ngSkinTools2.workspace_control_main_window(); ngSkinTools2.open_ui()
    except Exception as e:
        print(e)

    if character=="DungeonMonster":
            rFile.import_hierarchy(path='/groups/dungeons/anim/Rigs/Gem_Heart_Rocks.mb')

            mc.parent('GemHeartRocks_GEO', 'ROOT|MODEL') 
            mc.parent('root_offset', 'ROOT|RIG')
            mc.parent('root_jnt', 'spine_06_geo_F_JNT')

            mc.xform('root_offset', translation=[0.195, 328.153+3.061, 140.865+1.173], rotation=[15.9, 0, 0], scale=[2, 2, 2])

            mc.delete('GemHeartRocks_Rig')

            mc.parentConstraint('spine_06_geo_F_JNT', 'root_offset', mo=True)

            mc.rename('root_ctrl', 'heart_ctrl')
            mc.rename('root_jnt', 'heart_root_jnt')


    # read skin data
    if sp:
        if not not_previs and character != 'Jett' and character != 'Blitz' and character !='Susaka':
            sp = sp[:-5]
            sp += '_pvis.json'
        sp_div = sp.split('/')
        dir = '/'.join(sp_div[:-1])
        rWeightNgIO.read_skin(body_mesh, dir, sp_div[-1][:-5])

    #### Bobo SPECIFICS
    ### Anim Face
    if character == 'Bobo' and not_previs and face:
        reload(rFile)
        face = rFile.import_hierarchy(groups + f'/bobo/anim/Rigs/{character}Face.mb')
        #Transfrom Face Rig
        #Flip Quad setting
        import rjg.post.BobofaceProject as rBFaceProj
        reload(rBFaceProj)
        rBFaceProj.project(body=body_mesh, char='ROOT', f_model='FaceAtOrigin', f_rig='face_M', extras=f'{character}_Extras', f_extras='F_EXTRAS', f_skel='faceRoot_JNT')#, tY=1.103)
        mc.delete(face)
        
        mc.joint(n='root_root_JNT')
        mc.parent('root_root_JNT', 'SKEL')
        mc.parent('root_M_JNT', 'faceRoot_JNT', 'root_root_JNT')
        mc.select('head_M_01_CTRL', 'Look_ctrl')
        spsw.run()
        mc.addAttr('Look_ctrl.spaceSwitch', e=True, enumName='world:head:')
        mc.setAttr('Look_ctrl.spaceSwitch', 1)
        mc.parent('Look_ctrl_space_switch_GRP', 'RIG')
        '''
        import rjg.post.BellyProject as rBellyProj
        reload(rBellyProj)
        belly = rFile.import_hierarchy(groups + f'/bobo/anim/Rigs/{character}Belly.mb')
        rBellyProj.project(body=body_mesh, char='ROOT', b_model='BellyAtOrigin', b_rig='belly_M', extras=f'{character}_Extras', b_extras='B_EXTRAS', b_skel='bellyRoot_JNT')#, tY=1.103)
        mc.delete(belly)
        '''


    if character == 'Bobo':
        import rjg.build_scripts.bobo_misc as rc
        reload(rc)
    
        if not_previs:
           try: 
                rc.bobo_extras(body_mesh, extras)
           except Exception as e:
                print('line 350',e)
        else:
           try:
               rc.bobo_misc_pvis(body_mesh, ['TempBrows', 'Tounge', 'BotTeeth', 'HandClaws', 'TopTeeth', 'FootClaws', 'LeftEye', 'LeftCornea', 'RightEye', 'RightCornea'])
           except:
               print('line 350',e)
            

    #### Gretchen SPECIFICS
    ### Anim Face
    if character == 'Gretchen' and not_previs and face:
        reload(rFile)
        face = rFile.import_hierarchy(groups + f'/bobo/anim/Rigs/{character}Face.mb')
        import rjg.post.faceProject as rFaceProj
        reload(rFaceProj)
        rFaceProj.project(body=body_mesh, char='ROOT', f_model='FaceAtOrigin', f_rig='face_M', extras=f'{character}_Extras', f_extras='F_EXTRAS', f_skel='faceRoot_JNT')#, tY=1.103)
        mc.delete(face)
        
        mc.joint(n='root_root_JNT')
        mc.parent('root_root_JNT', 'SKEL')
        mc.parent('root_M_JNT', 'faceRoot_JNT', 'root_root_JNT')
        '''
        mc.select('head_M_01_CTRL', 'Look_Control')
        spsw.run()
        mc.addAttr('Look_Control.spaceSwitch', e=True, enumName='world:head:')
        mc.setAttr('Look_Control.spaceSwitch', 1)
        mc.parent('Look_Control_space_switch_GRP', 'RIG')
        '''
    if character == 'Gretchen':
        import rjg.build_scripts.Gretchen_misc as rc
        reload(rc)

        if not_previs:
            try: 
                rc.Gretchen_extras(body_mesh, extras)
            except:
                pass
        else:
            try:
                rc.Gretchen_misc_pvis(body_mesh, ['Eyeball','Cornea','Bandanna','Shirt','Boots','Hair', 'Glasses', 'Pants'])
            except:
                pass


    #    import rjg.build_scripts.bobo_misc as rc
    #    reload(rc)
    #    bobo_misc_pvis(body_mesh, ["Tongue","UpperTeeth","LowerTeeth","Claws","Eyeballs","Corneas",])

    #### RAYDEN SPECIFICS
    if character == 'Rayden':
        import rjg.build_scripts.rayden_clothes as rc
        reload(rc)
        if not_previs:
            rc.rayden_clothes(body_mesh, extras)
        else:
            try:
                rc.rayden_clothes_pvis(body_mesh, ['Shirt', 'VestFluff', 'Clothes', 'Fingernails', 'Eyeballs', 'Corneas', 'Tongue', 'LowerTeeth', 'UpperTeeth', 'RaydenHair'])
            except:
                rc.rayden_clothes_pvis(body_mesh, ['Clothes'])    
        try:
            rUtil.create_pxPin(0, 142.159, -12.095, 'Clothes.vtx[83073]', 'S_Crossbow:crossbow', ctrl=True, prop='S_Crossbow:crossbow_geo')
    
            mc.parent('S_Crossbow:crossbow_geo', 'S_Crossbow:crossbow')
            mc.hide('pinInput')
            mc.parent('S_Crossbow:ROOT', world=True)
            mc.select('chest_M_02_CTRL', 'arm_R_03_fk_CTRL', 'arm_L_03_fk_CTRL', 'S_Crossbow:crossbow_M_CTRL')
            # spsw.run()
            # mc.addAttr('S_Crossbow:crossbow_M_CTRL.spaceSwitch', e=True, enumName='world:back:right hand:left hand:')
            # mc.setAttr('S_Crossbow:crossbow_M_CTRL.spaceSwitch', 1)
            # mc.parent('S_Crossbow:crossbow_M_CTRL_space_switch_GRP', 'RIG')
            mc.parent('S_Crossbow:crossbow', 'S_Crossbow:MODEL')
            
        except:
            pass
        
        
    #### ROBIN SPECIFICS
    elif character == 'Robin':
        import rjg.build_scripts.robin_clothes as rc
        reload(rc)
        
        if not_previs:
            rc.robin_clothes(body_mesh, extras)
        else:
            rc.robin_clothes_pvis(body_mesh, ['Clothes', 'Hairtie', 'Earrings', 'Tongue', 'UpperTeeth', 'LowerTeeth', 'Eyes', 'Cornea', 'Eyebrows', 'static_hair', 'Fingernails'])
        
        mc.parent('hair_M', 'RIG')
        mc.parent('hair_root_jnt', 'head_M_JNT')
        mc.parentConstraint('head_M_01_CTRL', 'CoG_hair_root_ctrl_OFST', mo=True)
        #mc.parentConstraint('head_M_01_CTRL', 'bun_01_ofst', mo=True)
        
        mc.select('LowerTeeth', 'UpperTeeth', 'Tongue')
        mel.eval('hyperShade -assign Robin_Skin1;')
        
        mc.select(clear=True)
        
        #rUtil.create_pxPin(0, 132.481, -11.065, 'Clothes.vtx[54013]', 'icepick', ctrl=True, prop='icepick_geo')
        #rUtil.create_pxPin(0, 132.481, -11.065, 'Clothes.vtx[52995]', 'holster', ctrl=False, prop='icepick_holster')
        rUtil.create_pxPin(0, 132.481, -11.065, 'Clothes.vtx[52995]', 'icepick', ctrl=True, prop='icepick_geo')
        rUtil.create_pxPin(0, 132.481, -11.065, 'Clothes.vtx[52995]', 'holster', ctrl=True, prop='holster_geo')
        
        mc.parent('icepick_geo', 'icepick')
        mc.parent('holster_geo', 'holster')
        mc.hide('pinInput')
        mc.hide('pinInput1')
        #mc.parent('icepick_PIN', 'MODEL')
        mc.parent('icepick', 'MODEL')
        mc.parent('holster', 'MODEL')
        '''
        mc.select('chest_M_02_CTRL', 'arm_R_03_fk_CTRL', 'arm_L_03_fk_CTRL', 'icepick_M_CTRL')
        spsw.run()
        mc.addAttr('icepick_M_CTRL.spaceSwitch', e=True, enumName='world:back:right hand:left hand:')
        mc.setAttr('icepick_M_CTRL.spaceSwitch', 1)
        mc.parent('icepick_M_CTRL_space_switch_GRP', 'RIG')
        '''

        # rUtil.create_pxPin(0, 132.481, -11.065, 'Clothes.vtx[52995]', 'holster', ctrl=True, prop='icepick_holster')
        # mc.parent('icepick_holster', 'holster')
        # mc.parent('holster_PIN', 'MODEL')
        # mc.parent('holster', 'holster_PIN')
        # mc.hide('pinInput1')

    # initialize skin clusters as ngST layers
    if not bony:
        for s in mc.ls(type='skinCluster'):
            try:
                rWeightNgIO.init_skc(s)
            except Exception as e:
                print(e)
                
    if not_previs and not bony:
        try:
            mc.blendShape(n='breath_blendshapes', foc=True, ip=groups + f'/dungeons/character/Rigging/Rigs/{character}/Skin/breath_shapes.shp')
            mc.select('chest_M_01_CTRL')
            mc.addAttr(at='float', longName='chestBreath', min=0, max=1, k=True)
            mc.addAttr(at='float', longName='bellyBreath', min=0, max=1, k=True)

            mc.connectAttr('chest_M_01_CTRL.chestBreath', 'breath_blendshapes.chest_breath')
            mc.connectAttr('chest_M_01_CTRL.bellyBreath', 'breath_blendshapes.belly_breath')
        except Exception as e:
            print('no breath blendshapes connected:', e)


    ##### PROJECT FACE
    if face and not bony and character != 'Bobo' and character !='Gretchen' and character != 'BoboQuad' and character !='Susaka':
        reload(rFile)
        face = rFile.import_hierarchy(groups + f'/dungeons/anim/Rigs/{character}Face.mb')
        import rjg.post.faceProject as rFaceProj
        reload(rFaceProj)
        
        rFaceProj.project(body=body_mesh, char='ROOT', f_model='FaceAtOrigin', f_rig='face_M', extras=f'{character}_Extras', f_extras='F_EXTRAS', f_skel='faceRoot_JNT')#, tY=1.103)
        mc.delete(face)
        
        mc.joint(n='root_root_JNT')
        mc.parent('root_root_JNT', 'SKEL')
        mc.parent('root_M_JNT', 'faceRoot_JNT', 'root_root_JNT')
        
        mc.select('head_M_01_CTRL', 'Look_Control')
        spsw.run()
        mc.addAttr('Look_Control.spaceSwitch', e=True, enumName='world:head:')
        mc.setAttr('Look_Control.spaceSwitch', 1)
        mc.parent('Look_Control_space_switch_GRP', 'RIG')
        
        
        

        

        
    # delete anim curves
    # mc.select(all=True)
    # ac = mc.ls(selection=True, type='animCurve')
    # mc.delete(ac)

    # finalize. create all connections/constraints
    if not bony:
        rFinal.final(utX=90, utY=0, DutZ=15, utScale=3, polish=False, character=character)
    else:
        rFinal.final(utX=90, utY=0, DutZ=15, utScale=3, polish=False)
    
    # set up control shapes
    if cp:
        cp_div = cp.split('/')
        dir = '/'.join(cp_div[:-1])
        rCtrlIO.read_ctrls(dir, curve_file=cp_div[-1][:-5])    
    
    # add prop to set
    if character == 'Robin':
        mc.sets('icepick_geo', add='cache_SET')
        mc.sets('holster_geo', add='cache_SET')
        pass
    elif character == 'Rayden':
        mc.parent('S_Crossbow:crossbow', 'S_Crossbow:MODEL')
        mc.sets('S_Crossbow:MODEL', add='prop_SET')

    ##### IMPORT POSE INTERPOLATORS
    if pp and not_previs and not bony:
        import rjg.libs.util as rUtil
        rUtil.import_poseInterpolator(pp)
        
    if character == 'Rayden':
        mc.connectAttr('cbow_rev.outputX', 'S_Crossbow:crossbow.visibility')
        
    # clean up scene
    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    
    # create groom bust
    if not bony:
        create_groom_bust(body_mesh)
        
    # set up textures
    import rjg.post.textures as rTex
    reload(rTex)
    for item in mc.ls('*_MT1'):
        mc.rename(item, item[:-1])
    rTex.set_textures(character)

    try:
        mc.disconnectAttr('standardSurface1.outColor', 'initialParticleSE.surfaceShader')
        mc.disconnectAttr('standardSurface1.outColor', 'initialShadingGroup.surfaceShader')
        mc.select('GemHeartRocks_GEO')
    except Exception as e:
        print(e)
    
    if not not_previs and not bony and character != 'Gretchen' and character != 'BoboQuad':
        try:
            mc.blendShape(character + '_UBM', name = 'pvis_shapes', foc=True)
            mc.blendShape('pvis_shapes', e=True, ip=f'{groups}/dungeons/character/Rigging/Rigs/{character}/Skin/pvis_shapes.shp')
            mc.connectAttr('look_L_CTRL.blink', 'pvis_shapes.blink_LShape')
            mc.connectAttr('look_R_CTRL.blink', 'pvis_shapes.blink_RShape')
        except:
            pass

    if not not_previs and not bony and character in ['Bobo', 'Gretchen']:
        try:
            mc.blendShape(character + '_UBM', name = 'pvis_shapes', foc=True)
            mc.blendShape('pvis_shapes', e=True, ip=f'{groups}/bobo/character/Rigs/{character}/Poses/pvis_shapes.shp')
            mc.connectAttr('look_L_CTRL.blink', 'pvis_shapes.blink_LShape')
            mc.connectAttr('look_R_CTRL.blink', 'pvis_shapes.blink_RShape')
        except:
            pass
        

            
    if not not_previs and not bony and character != 'Gretchen' and character != 'BoboQuad':
        try:
            for o in ['lipLeft_M_M_CTRL_SDK_GRP.', 'lipRight_M_M_CTRL_SDK_GRP.']:
                for a in ['translateY', 'rotateX']:
                    mc.setDrivenKeyframe(o, at=a, cd='jaw_M_M_CTRL.rotateX')
            mc.setAttr('jaw_M_M_CTRL.rotateX', 38)
            mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.translateY', -1.773)
            mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.rotateX', 21.592)
            mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.translateZ', -.56)
            mc.setAttr('lipRight_M_M_CTRL_SDK_GRP.translateY', -1.773)
            mc.setAttr('lipRight_M_M_CTRL_SDK_GRP.rotateX', 21.592)
            mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.translateZ', -.56)
            for o in ['lipLeft_M_M_CTRL_SDK_GRP.', 'lipRight_M_M_CTRL_SDK_GRP.']:
                for a in ['translateY', 'rotateX']:
                    mc.setDrivenKeyframe(o, at=a, cd='jaw_M_M_CTRL.rotateX')
            mc.setAttr('jaw_M_M_CTRL.rotateX', 0)
        except:
            pass
        
    try:
        mc.BakeAllNonDefHistory()
        mc.bakePartialHistory(all=True)    
    except Exception as e:
        mc.warning("Delete history error:", e)
        
    rUSD.connectUSDAttr()
    
    ### TEMP ###
    try:
        if character == 'Rayden' and not not_previs:
            mc.hide('Eyelashes')
    except:
        pass
    try:
        mc.parent('Fingernails', body_mesh[:-4] + '_EXTRAS')
    except:
        pass
    try:
        mc.delete('locator1')
    except:
        pass
    try:
        lpc = mc.parentConstraint('head_M_01_CTRL', 'lipLeft_M_M_CTRL_CNST_GRP', mo=True)
        rpc = mc.parentConstraint('head_M_01_CTRL', 'lipRight_M_M_CTRL_CNST_GRP', mo=True)
        mc.setAttr(lpc[0] + '.interpType', 0)
        mc.setAttr(rpc[0] + '.interpType', 0)
    except Exception as e:
        print(e)
    try:
        mc.disconnectAttr('Robin_H_file.outColor', 'Robin_Hair.baseColor')
        mc.disconnectAttr('Robin_S_file.outColor', 'Robin_Silk.baseColor')
        mc.setAttr('Robin_Silk.baseColor', 0.124521, 0.0142565, 0.00418706, type='double3')
    except Exception as e:
        print(e)
        
    if character == 'DungeonMonster':
        mc.setAttr('switch_CTRL.armL_IKFK', 0)
        mc.setAttr('switch_CTRL.armR_IKFK', 0)
    try:
        orig = mc.select('*ShapeOrig1')
        orig = mc.ls(selection=True)
        clean_o, broken_o = [], []
        for o in orig:
            if '_' not in o:
                clean_o.append(o)

        for o1 in clean_o:
            if mc.objExists(o1[:-1]):
                broken_o.append(o1)
            
        for o in broken_o:
            conn = mc.listConnections(o, d=True)
            skc = conn[0]
            bs = conn[1]
            o_new = o[:-1]
            mc.connectAttr(o_new + '.outMesh', bs + '.originalGeometry[0]', f=True)
            mc.connectAttr(o_new + '.outMesh', skc + '.originalGeometry[0]', f=True)
            mc.connectAttr(o_new + '.worldMesh[0]', bs + '.input[0].inputGeometry', f=True)
            mc.delete(o)
    except Exception as e:
        print('shapeOrig1 error:',e)
        if character == 'Robin' and face:
            run(character, mp=mp, gp=gp, ep=ep, cp=cp, sp=sp, pp=pp, face=face, previs=previs)
            print("attempt etc.")
            return
    if character == 'Robin':
        ext = rFile.import_hierarchy(f'{groups}/dungeons/character/Rigging/Rigs/Robin/robin_hand_fix.mb')
        mc.blendShape('robin_skin_hands_ears', 'Robin_UBM', n='fix_shape')
        mc.select('switch_CTRL')
        mc.addAttr(at='float', longName='biggerHands', min=0, max=1, k=True)
        mc.connectAttr('switch_CTRL.biggerHands', 'fix_shape.robin_skin_hands_ears')
        mc.delete(ext)
    if character == 'Rayden':
        mc.select('switch_CTRL')
        mc.addAttr(at='float', longName='holsterFlat', min=0, max=1, k=True)
        mc.connectAttr('switch_CTRL.holsterFlat', 'clothes_blendshape.holster_flat')
        
    

    ############
            #fix UeCorrectives
    if character in ['Jett', 'Blitz']:
        try:
            mc.setAttr('upperarmCorrective_L_L_JNT.translate', 0, 0, 0, type='double3')
            mc.setAttr('upperarmCorrective_R_R_JNT.translate', 0, 0, 0, type='double3')

            mc.setAttr('lowerarmCorrective_L_L_JNT.translate', 0, 0, 0, type='double3')
            mc.setAttr('lowerarmCorrective_R_R_JNT.translate', 0, 0, 0, type='double3')

            mc.setAttr('thighCorrective_L_L_JNT.translate', 0, 0, 0, type='double3')
            mc.setAttr('thighCorrective_R_R_JNT.translate', 0, 0, 0, type='double3')

            mc.setAttr('calfCorrective_L_L_JNT.translate', 0, 0, 0, type='double3')
            mc.setAttr('calfCorrective_R_R_JNT.translate', 0, 0, 0, type='double3')
        except Exception as e:
            print(e)

        import rjg.post.unrealJntRename as rUEJnt
        rUEJnt.unrealJntRename()

    if character in ['Susaka']:
        import rjg.post.unrealJntRename as rUEJnt
        rUEJnt.unrealJntRename()
        sys.path.append(f'{groups}/dungeons/pipeline/pipeline/software/maya/scripts/rjg/build_scripts')
        from UnrealCorrectives import BuildCorrectives
        from UnrealCorrectives import build_parents  # Assuming UnrealCorrectives.py is in the same directory or on the PYTHONPATH
        CorrGuides2 = ["upperarm_twistCor_01", "lowerarm_correctiveRoot", "upperarm_correctiveRoot", "thigh_correctiveRoot", "calf_correctiveRoot"]
        CorrParrent2 = ["upperarm_l", "lowerarm_l", "upperarm_l", "thigh_l", "calf_l"]
        build_parents(CorrGuides2, CorrParrent2)

        CorrGuides = ["lowerarm_out", "lowerarm_fwd", "lowerarm_in", "lowerarm_bck", "lowerarm_twist_01", "lowerarm_twist_02", 
                    "wrist_outer", "wrist_inner",
                    "upperarm_bicep", "upperarm_tricep",
                    "upperarm_out", "upperarm_bck", "upperarm_fwd", "upperarm_in", "upperarm_twist_02", 
                    "clavicle_out", "clavicle_scap",
                    "clavicle_pec", "spine_04_latissimus",
                    "thigh_fwd", "thigh_fwd_lwr", "thigh_in", "thigh_bck", "thigh_out", "thigh_bck_lwr", "thigh_twist_01", "thigh_twist_02",
                    "calf_knee", "calf_kneeBack", "calf_twist_01", "calf_twist_02",
                    "HandThumb0_Bot", "HandThumb1_Bot", "HandThumb1_TOP", "HandThumb2_Bot", "HandThumb2_TOP", "HandThumb3_Bot", "HandThumb3_TOP",
                    "HandIndex0_BOT", "HandIndex1_BOT", "HandIndex1_TOP","HandIndex2_BOT", "HandIndex2_TOP", "HandIndex3_BOT", "HandIndex3_TOP",
                    "HandMiddle0_BOT", "HandMiddle1_BOT", "HandMiddle1_TOP","HandMiddle2_BOT", "HandMiddle2_TOP", "HandMiddle3_BOT", "HandMiddle3_TOP",
                    "HandRing0_BOT", "HandRing1_BOT", "HandRing1_TOP","HandRing2_BOT", "HandRing2_TOP", "HandRing3_BOT", "HandRing3_TOP",
                    "HandPinky0_BOT", "HandPinky1_BOT", "HandPinky1_TOP","HandPinky2_BOT", "HandPinky2_TOP", "HandPinky3_BOT", "HandPinky3_TOP",
                    "ankle_fwd", "ankle_bck",
                    ]

        CorrParrent = ["lowerarm_correctiveRoot_l", "lowerarm_correctiveRoot_l", "lowerarm_correctiveRoot_l", "lowerarm_correctiveRoot_l", "lowerarm_correctiveRoot_l", "lowerarm_correctiveRoot_l",
                    "hand_l", "hand_l",
                    "upperarm_twistCor_01_l", "upperarm_twistCor_01_l", 
                    "upperarm_correctiveRoot_l", "upperarm_correctiveRoot_l", "upperarm_correctiveRoot_l", "upperarm_correctiveRoot_l", "upperarm_correctiveRoot_l",
                    "clavicle_l", "clavicle_l",
                    "spine_05", "spine_05",
                    "thigh_correctiveRoot_l", "thigh_correctiveRoot_l", "thigh_correctiveRoot_l", "thigh_correctiveRoot_l", "thigh_correctiveRoot_l", "thigh_correctiveRoot_l", "thigh_correctiveRoot_l", "thigh_correctiveRoot_l",
                    "calf_correctiveRoot_l", "calf_correctiveRoot_l", "calf_correctiveRoot_l", "calf_correctiveRoot_l",
                    "thumb_01_l", "thumb_01_l", "thumb_01_l", "thumb_02_l", "thumb_02_l", "thumb_03_l", "thumb_03_l",
                    "index_metacarpal_l", "index_01_l", "index_01_l", "index_02_l", "index_02_l", "index_03_l", "index_03_l",
                    "middle_metacarpal_l", "middle_01_l", "middle_01_l", "middle_02_l", "middle_02_l", "middle_03_l", "middle_03_l", 
                    "ring_metacarpal_l", "ring_01_l", "ring_01_l", "ring_02_l", "ring_02_l", "ring_03_l", "ring_03_l", 
                    "pinky_metacarpal_l", "pinky_01_l", "pinky_01_l", "pinky_02_l", "pinky_02_l", "pinky_03_l", "pinky_03_l",
                    "foot_l", "foot_l", 
                    ]

        BuildCorrectives(CorrGuides, CorrParrent)
        #mc.delete("UE_Correctives")
        bindjoints = mc.select(mc.listRelatives("SKEL", ad=True, type="joint"))
        mc.select('Susaka_UBM')
        #mel.eval('doDetachSkin 3 { "1", "1", "1" };')
        mc.skinCluster('Susaka_UBM', edit=True, unbind=True)
        skc = mc.skinCluster('root', 'Susaka_UBM', tsb=False, skinMethod=1, bindMethod=0)[0]
        mc.setAttr(skc + '.dqsSupportNonRigid', 1)
        if sp:
            sp_div = sp.split('/')
            dir = '/'.join(sp_div[:-1])
            rWeightNgIO.read_skin("Susaka_UBM", dir, sp_div[-1][:-5])
        #print('Reskin1')
        geo = ['Wrap', 'Glove', 'UnderPantLayer', 'TempHair', 'Nails', 'TempBrows', 'RightEye', 'RightCornea', 'LeftEye', 'LeftCornea', 'Pants2', 'Belt', 'Scarf', 'CowlBase', 'Hood', 'Straps', 'Collar', 'Shirt', 'Pants', 'ArmBand', 'Kneepad', 'RShoe', 'LShoe']
        for g in geo:
            sk = mc.skinCluster('root', g, tsb=False, skinMethod=1, n=f'clothingSkc{g}')[0]
            mc.copySkinWeights(ss='skinCluster1', ds=f'clothingSkc{g}', surfaceAssociation='closestPoint', noMirror=True, )
        
        # import rjg.build_scripts.Susaka_Misc as rc
        # reload(rc)
        # # try: 
        #     rc.Susaka_misc_pvis(body_mesh, ['Wrap', 'Glove', 'UnderPantLayer', 'TempHair', 'Nails', 'TempBrows', 'REye', 'RCornea', 'LEye', 'LCornea', 'Pants2', 'Belt', 'Scarf', 'CowlBase', 'Hood', 'Straps', 'Collar', 'Shirt', 'Pants', 'ArmBand', 'Kneepad', 'RShoe', 'LShoe'])
        # except Exception as e:
        #         print(e)
        print("ExtraSkins")
        try:
            try:
                mc.select('LeftEye', 'RightEye', 'LeftCornea', 'RightCornea', 'BotTeeth', 'TopTeeth', 'Tounge')
                mel.eval('doDetachSkin 3 { "1", "1", "1" };')
                mc.skinCluster('eye_L_JNT', 'LeftCornea', mi=1, tsb=True)
                mc.skinCluster('eye_R_JNT', 'RightCornea', mi=1, tsb=True)
                mc.skinCluster('eye_L_JNT', 'LeftEye', mi=1, tsb=True)
                mc.skinCluster('eye_R_JNT', 'RightEye', mi=1, tsb=True)
                mc.skinCluster('jaw_M_JNT', 'BotTeeth', mi=1, tsb=True)
                mc.skinCluster('jaw_M_JNT', 'Tounge', mi=1, tsb=True)
                mc.skinCluster('head', 'TopTeeth', mi=1, tsb=True)
                print('Reskinned')
            except Exception as e:
                print(e)
            #try:
            #    rUtil.pvis_blink('eyelid_L_JNT', 'look_L_CTRL', 40)
            #    rUtil.pvis_blink('eyelid_R_JNT', 'look_R_CTRL', 40)
        except Exception as e:
            print(e)
        
        
    if not not_previs and not bony and character != 'Bobo' and character != 'Gretchen' and character != 'BoboQuad' and character !='Susaka':
        try:
            try:
                mc.select('Eyes', 'Cornea', 'LowerTeeth', 'UpperTeeth', 'Tongue')
                mel.eval('doDetachSkin 3 { "1", "1", "1" };')
                mc.skinCluster('eyeBind_L_JNT', 'eyeBind_R_JNT', 'Cornea', mi=1, tsb=True)
                mc.skinCluster('eyeBind_L_JNT', 'eyeBind_R_JNT', 'Eyes', mi=1, tsb=True)
                mc.skinCluster('jaw_M_JNT', 'LowerTeeth', mi=1, tsb=True)
                mc.skinCluster('jaw_M_JNT', 'Tongue', mi=1, tsb=True)
                mc.skinCluster('head_M_JNT', 'UpperTeeth', mi=1, tsb=True)
            except Exception as e:
                mc.select('Eyeballs', 'Corneas', 'LowerTeeth', 'UpperTeeth', 'Tongue')
                mel.eval('doDetachSkin 3 { "1", "1", "1" };')
                mc.skinCluster('eyeBind_L_JNT', 'eyeBind_R_JNT', 'Corneas', mi=1, tsb=True)
                mc.skinCluster('eyeBind_L_JNT', 'eyeBind_R_JNT', 'Eyeballs', mi=1, tsb=True)
                mc.skinCluster('jaw_M_JNT', 'LowerTeeth', mi=1, tsb=True)
                mc.skinCluster('jaw_M_JNT', 'Tongue', mi=1, tsb=True)
                mc.skinCluster('head_M_JNT', 'UpperTeeth', mi=1, tsb=True)
            try:
                rUtil.pvis_blink('eyelid_L_JNT', 'look_L_CTRL', 40)
                rUtil.pvis_blink('eyelid_R_JNT', 'look_R_CTRL', 40)
            except Exception as e:
                print(e)
        except:
            pass



    if not not_previs and character == 'Bobo':
        try:
            try:
                mc.select('LeftEye', 'RightEye', 'LeftCornea', 'RightCornea', 'BotTeeth', 'TopTeeth', 'Tounge')
                mel.eval('doDetachSkin 3 { "1", "1", "1" };')
                mc.skinCluster('eye_L_JNT', 'LeftCornea', mi=1, tsb=True)
                mc.skinCluster('eye_R_JNT', 'RightCornea', mi=1, tsb=True)
                mc.skinCluster('eye_L_JNT', 'LeftEye', mi=1, tsb=True)
                mc.skinCluster('eye_R_JNT', 'RightEye', mi=1, tsb=True)
                mc.skinCluster('jaw_M_JNT', 'BotTeeth', mi=1, tsb=True)
                mc.skinCluster('jaw_M_JNT', 'Tounge', mi=1, tsb=True)
                mc.skinCluster('head_M_JNT', 'TopTeeth', mi=1, tsb=True)
                print('Reskinned')
            except Exception as e:
                print(e)
            #try:
            #    rUtil.pvis_blink('eyelid_L_JNT', 'look_L_CTRL', 40)
            #    rUtil.pvis_blink('eyelid_R_JNT', 'look_R_CTRL', 40)
            #except Exception as e:
            #    print(e)
            try:
                for joint in ["eye_L_JNT", "eye_R_JNT"]:
                    offset_grp = mc.group(empty=True, name=f"{joint}_Sheeroffset")
                    # Match position and orientation
                    mc.delete(mc.parentConstraint(joint, offset_grp))
                    # Parent the joint under the group
                    mc.parent(joint, offset_grp)
                    # Scale the group on Z-axis
                    mc.setAttr(f"{offset_grp}.scaleZ", 0.75)
                    mc.parent(f"{offset_grp}", 'lookEyes_M_JNT_GRP')
            except Exception as e:
                print(e)
        except:
            pass

    if not_previs and character == 'Bobo':
        try:
            try:
                mc.select('LeftEye', 'RightEye', 'LeftCornea', 'RightCornea', 'BotTeeth', 'TopTeeth', 'Tounge')
                mel.eval('doDetachSkin 3 { "1", "1", "1" };')
                mc.skinCluster('head_M_JNT', 'LeftCornea', mi=1, tsb=True)
                mc.skinCluster('head_M_JNT', 'RightCornea', mi=1, tsb=True)
                mc.skinCluster('head_M_JNT', 'LeftEye', mi=1, tsb=True)
                mc.skinCluster('head_M_JNT', 'RightEye', mi=1, tsb=True)
                mc.skinCluster('head_M_JNT', 'BotTeeth', mi=1, tsb=True)
                mc.skinCluster('head_M_JNT', 'Tounge', mi=1, tsb=True)
                mc.skinCluster('head_M_JNT', 'TopTeeth', mi=1, tsb=True)
                print('Reskinned')
            except Exception as e:
                print(e)
            #try:
            #    rUtil.pvis_blink('eyelid_L_JNT', 'look_L_CTRL', 40)
            #    rUtil.pvis_blink('eyelid_R_JNT', 'look_R_CTRL', 40)
            #except Exception as e:
            #    print(e)
        except:
            pass
            
    ######

    #Bobo Fix
    if face and character == 'Bobo':
        try:
            mc.reorderDeformers( 'pose_blendhapes', 'main_blendshapes', ['Bobo_UBM'])
        except Exception as e:
            print(e)
        #try: 
        #    for offsets in ["tail_M_02_fk_CTRL_OFF_GRP", "tail_M_01_fk_CTRL_OFF_GRP"]:
        #        mc.setAttr(f"{offsets}.translateY", 2)
        #except Exception as e:
        #    print(e)

    if character == 'Bobo' and not_previs:
        try:
            deformer = mc.deltaMush('Bobo_UBM')[0]
            mc.setAttr(f"{deformer}.smoothingIterations", 100)
            mc.setAttr(f"{deformer}.smoothingStep", .1)
            mc.deformerWeights("BoboDeltaMush.xml", im=True,  deformer=deformer, path=f'{groups}/bobo/character/Rigs/Bobo/SkinFiles/')
            deformer2 = mc.deltaMush('Bobo_UBM')[0]
            mc.setAttr(f"{deformer2}.smoothingIterations", 2)
            mc.setAttr(f"{deformer2}.smoothingStep", .5)
            mc.deformerWeights("BoboDeltaMush.xml", im=True,  deformer=deformer2, path=f'{groups}/bobo/character/Rigs/Bobo/SkinFiles/')
            sys.path.append(f'{groups}/dungeons/pipeline/pipeline/software/maya/scripts/rjg/build_scripts/SteveUtils')
            from CurveNetAtHome import create_curve_net_joints
            create_curve_net_joints('Body', 'Bobo_UBM') 
            skin_clusters = "curve_net_skin_cluster"
            


            mc.delete('CurveNet_Guide_Group')
        
        except Exception as e:
            print(e)




    mc.select(clear=True)
    print(f"\n{character} rig build complete.")



def create_groom_bust(model):
    mc.select(f'{model}.f[0:2041]',
              f'{model}.f[5887:5903]',
              f'{model}.f[5920]', 
              f'{model}.f[5981:5982]', 
              f'{model}.f[6042]', 
              f'{model}.f[6099]', 
              f'{model}.f[6762]', 
              f'{model}.f[7086:9274]', 
              f'{model}.f[13120:13136]', 
              f'{model}.f[13153]', 
              f'{model}.f[13214:13215]', 
              f'{model}.f[13275]', 
              f'{model}.f[13332]', 
              f'{model}.f[13995]', 
              f'{model}.f[14319:14649]', 
              f'{model}.f[14722:14953]')
              
    mc.componentTag(create=True, ntn='GroomBust')

            

#BoboFix


#rCtrlIO.write_ctrls("/groups/dungeons/character/Rigging/Rigs/Rayden/Controls", force=True, name='rayden_control_curves')
#rCtrlIO.write_ctrls("/groups/dungeons/character/Rigging/Rigs/Robin/Controls", force=True, name='robin_control_curves')
#rCtrlIO.write_ctrls("/groups/dungeons/character/Rigging/Rigs/DungeonMonster/Controls", force=True, name='dm_control_curves')


'''   
for o in ['lipLeft_M_M_CTRL_SDK_GRP.', 'lipRight_M_M_CTRL_SDK_GRP.']:
    for a in ['translateY', 'rotateX']:
        mc.setDrivenKeyframe(o, at=a, cd='jaw_M_M_CTRL.rotateX')
mc.setAttr('jaw_M_M_CTRL.rotateX', 38)
mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.translateY', -1.773)
mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.rotateX', 21.592)
mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.translateZ', -.56)
mc.setAttr('lipRight_M_M_CTRL_SDK_GRP.translateY', -1.773)
mc.setAttr('lipRight_M_M_CTRL_SDK_GRP.rotateX', 21.592)
mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.translateZ', -.56)
for o in ['lipLeft_M_M_CTRL_SDK_GRP.', 'lipRight_M_M_CTRL_SDK_GRP.']:
    for a in ['translateY', 'rotateX']:
        mc.setDrivenKeyframe(o, at=a, cd='jaw_M_M_CTRL.rotateX')
mc.setAttr('jaw_M_M_CTRL.rotateX', 0)
'''