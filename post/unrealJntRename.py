import maya.cmds as mc

def unrealJntRename():
    jnts = [
        'root_M_JNT', 'root',
        'COG_M_JNT', 'pelvis',
        'spine_M_02_JNT', 'spine_01',
        'spine_M_03_JNT', 'spine_02',
        'spine_M_04_JNT', 'spine_03',
        'spine_M_05_JNT', 'spine_04',
        'chest_M_JNT', 'spine_05',
        'neck_M_01_JNT', 'neck_01',
        'neck_M_02_JNT', 'neck_02',
        'head_M_JNT', 'head',

        'clavicle_L_01_JNT', 'clavicle_l',
        'arm_L_01_JNT', 'upperarm_l',
        'arm_L_02_JNT', 'lowerarm_l',
        'hand_L_JNT', 'hand_l',
        'fingerIndex_L_01_JNT', 'index_metacarpal_l',
        'fingerIndex_L_02_JNT', 'index_01_l',
        'fingerIndex_L_03_JNT', 'index_02_l',
        'fingerIndex_L_04_JNT', 'index_03_l',
        'fingerMiddle_L_01_JNT', 'middle_metacarpal_l',
        'fingerMiddle_L_02_JNT', 'middle_01_l',
        'fingerMiddle_L_03_JNT', 'middle_02_l',
        'fingerMiddle_L_04_JNT', 'middle_03_l',
        'fingerRing_L_01_JNT', 'ring_metacarpal_l',
        'fingerRing_L_02_JNT', 'ring_01_l',
        'fingerRing_L_03_JNT', 'ring_02_l',
        'fingerRing_L_04_JNT', 'ring_03_l',
        'fingerPinky_L_01_JNT', 'pinky_metacarpal_l',
        'fingerPinky_L_02_JNT', 'pinky_01_l',
        'fingerPinky_L_03_JNT', 'pinky_02_l',
        'fingerPinky_L_04_JNT', 'pinky_03_l',
        'fingerThumb_L_01_JNT', 'thumb_01_l',
        'fingerThumb_L_02_JNT', 'thumb_02_l',
        'fingerThumb_L_03_JNT', 'thumb_03_l',
        'leg_L_01_JNT', 'thigh_l',
        'leg_L_02_JNT', 'calf_l',
        'foot_L_01_JNT', 'foot_l',
        'foot_L_02_JNT', 'ball_l',

        'clavicle_R_01_JNT', 'clavicle_r',
        'arm_R_01_JNT', 'upperarm_r',
        'arm_R_02_JNT', 'lowerarm_r',
        'hand_R_JNT', 'hand_r',
        'fingerIndex_R_01_JNT', 'index_metacarpal_r',
        'fingerIndex_R_02_JNT', 'index_01_r',
        'fingerIndex_R_03_JNT', 'index_02_r',
        'fingerIndex_R_04_JNT', 'index_03_r',
        'fingerMiddle_R_01_JNT', 'middle_metacarpal_r',
        'fingerMiddle_R_02_JNT', 'middle_01_r',
        'fingerMiddle_R_03_JNT', 'middle_02_r',
        'fingerMiddle_R_04_JNT', 'middle_03_r',
        'fingerRing_R_01_JNT', 'ring_metacarpal_r',
        'fingerRing_R_02_JNT', 'ring_01_r',
        'fingerRing_R_03_JNT', 'ring_02_r',
        'fingerRing_R_04_JNT', 'ring_03_r',
        'fingerPinky_R_01_JNT', 'pinky_metacarpal_r',
        'fingerPinky_R_02_JNT', 'pinky_01_r',
        'fingerPinky_R_03_JNT', 'pinky_02_r',
        'fingerPinky_R_04_JNT', 'pinky_03_r',
        'fingerThumb_R_01_JNT', 'thumb_01_r',
        'fingerThumb_R_02_JNT', 'thumb_02_r',
        'fingerThumb_R_03_JNT', 'thumb_03_r',
        'leg_R_01_JNT', 'thigh_r',
        'leg_R_02_JNT', 'calf_r',
        'foot_R_01_JNT', 'foot_r',
        'foot_R_02_JNT', 'ball_r',

        'upperarm_bicep_l_M_JNT', 'upperarm_bicep_l',
        'upperarm_tricep_l_M_JNT', 'upperarm_tricep_l',
        'upperarm_fwd_l_L_Bind_JNT_L_JNT', 'upperarm_fwd_l',
        'upperarm_bck_l_L_Bind_JNT_L_JNT', 'upperarm_bck_l',
        'upperarm_in_l_L_Bind_JNT_L_JNT', 'upperarm_in_l',
        'upperarm_out_l_L_Bind_JNT_L_JNT', 'upperarm_out_l',
        'upperarm_twist_02_l_L_Bind_JNT_L_JNT', 'upperarm_twist_02_l',
        'upperarm_twist_01_l_L_Bind_JNT_L_JNT', 'upperarm_twist_02_l',
        'lowerarm_fwd_l_L_Bind_JNT_L_JNT', 'lowerarm_fwd_l',
        'lowerarm_bck_l_L_Bind_JNT_L_JNT', 'lowerarm_bck_l',
        'lowerarm_in_l_L_Bind_JNT_L_JNT', 'lowerarm_in_l',
        'lowerarm_out_l_L_Bind_JNT_L_JNT', 'lowerarm_out_l',
        'lowerarm_twist_02_l_L_Bind_JNT_L_JNT', 'lowerarm_twist_02_l',
        'lowerarm_twist_01_l_L_Bind_JNT_L_JNT', 'lowerarm_twist_02_l',
        'thigh_fwd_l_L_Bind_JNT_L_JNT', 'thigh_fwd_l',
        'thigh_bck_l_L_Bind_JNT_L_JNT', 'thigh_bck_l',
        'thigh_in_l_L_Bind_JNT_L_JNT', 'thigh_in_l',
        'thigh_out_l_L_Bind_JNT_L_JNT', 'thigh_out_l',
        'thigh_bck_lwr_l_L_Bind_JNT_L_JNT', 'thigh_bck_lwr_l',
        'thigh_fwd_lwr_l_L_Bind_JNT_L_JNT', 'thigh_fwd_lwr_l',
        'thigh_twist_02_l_L_Bind_JNT_L_JNT', 'thigh_twist_02_l',
        'thigh_twist_01_l_L_Bind_JNT_L_JNT', 'thigh_twist_02_l',
        'calf_knee_l_L_Bind_JNT_L_JNT', 'calf_knee_l',
        'calf_kneeBack_l_L_Bind_JNT_L_JNT', 'calf_kneeBack_l',
        'calf_twist_02_l_L_Bind_JNT_L_JNT', 'calf_twist_02_l',
        'calf_twist_01_l_L_Bind_JNT_L_JNT', 'calf_twist_02_l',
        'upperarmCorrective_R_R_JNT', 'upperarm_correctiveRoot_r',
        'upperarmCorrective_L_L_JNT', 'upperarm_correctiveRoot_l',
        'thighCorrective_L_L_JNT', 'thigh_correctiveRoot_l',
        'thighCorrective_R_R_JNT', 'thigh_correctiveRoot_r',

        'upperarm_bicep_r_M_JNT', 'upperarm_bicep_r',
        'upperarm_tricep_r_M_JNT', 'upperarm_tricep_r',
        'upperarm_fwd_r_R_Bind_JNT_R_JNT', 'upperarm_fwd_r',
        'upperarm_bck_r_R_Bind_JNT_R_JNT', 'upperarm_bck_r',
        'upperarm_in_r_R_Bind_JNT_R_JNT', 'upperarm_in_r',
        'upperarm_out_r_R_Bind_JNT_R_JNT', 'upperarm_out_r',
        'upperarm_twist_02_r_R_Bind_JNT_R_JNT', 'upperarm_twist_02_r',
        'upperarm_twist_01_r_R_Bind_JNT_R_JNT', 'upperarm_twist_02_r',
        'lowerarm_fwd_r_R_Bind_JNT_R_JNT', 'lowerarm_fwd_r',
        'lowerarm_bck_r_R_Bind_JNT_R_JNT', 'lowerarm_bck_r',
        'lowerarm_in_r_R_Bind_JNT_R_JNT', 'lowerarm_in_r',
        'lowerarm_out_r_R_Bind_JNT_R_JNT', 'lowerarm_out_r',
        'lowerarm_twist_02_r_R_Bind_JNT_R_JNT', 'lowerarm_twist_02_r',
        'lowerarm_twist_01_r_R_Bind_JNT_R_JNT', 'lowerarm_twist_02_r',
        'thigh_fwd_r_R_Bind_JNT_R_JNT', 'thigh_fwd_r',
        'thigh_bck_r_R_Bind_JNT_R_JNT', 'thigh_bck_r',
        'thigh_in_r_R_Bind_JNT_R_JNT', 'thigh_in_r',
        'thigh_out_r_R_Bind_JNT_R_JNT', 'thigh_out_r',
        'thigh_bck_lwr_r_R_Bind_JNT_R_JNT', 'thigh_bck_lwr_r',
        'thigh_fwd_lwr_r_R_Bind_JNT_R_JNT', 'thigh_fwd_lwr_r',
        'thigh_twist_02_r_R_Bind_JNT_R_JNT', 'thigh_twist_02_r',
        'thigh_twist_01_r_R_Bind_JNT_R_JNT', 'thigh_twist_02_r',
        'calf_knee_r_R_Bind_JNT_R_JNT', 'calf_knee_r',
        'calf_kneeBack_r_R_Bind_JNT_R_JNT', 'calf_kneeBack_r',
        'calf_twist_02_r_R_Bind_JNT_R_JNT', 'calf_twist_02_r',
        'calf_twist_01_r_R_Bind_JNT_R_JNT', 'calf_twist_02_r',

        'ankle_bck_l_M_JNT', 'ankle_bck_l',
        'ankle_fwd_l_M_JNT', 'ankle_fwd_l',
        'clavicle_pec_l_M_JNT', 'clavicle_pec_l',
        'clavicle_scap_l_M_JNT', 'clavicle_scap_l',
        'clavicle_out_l_M_JNT', 'clavicle_out_l',
        'spine_04_latissimus_l_M_JNT', 'spine_04_latissimus_l',
        'wrist_inner_l_M_JNT', 'wrist_inner_l',
        'wrist_outer_l_M_JNT', 'wrist_outer_l',

        'ankle_bck_r_M_JNT', 'ankle_bck_r',
        'ankle_fwd_r_M_JNT', 'ankle_fwd_r',
        'clavicle_pec_r_M_JNT', 'clavicle_pec_r',
        'clavicle_scap_r_M_JNT', 'clavicle_scap_r',
        'clavicle_out_r_M_JNT', 'clavicle_out_r',
        'spine_04_latissimus_r_M_JNT', 'spine_04_latissimus_r',
        'wrist_inner_r_M_JNT', 'wrist_inner_r',
        'wrist_outer_r_M_JNT', 'wrist_outer_r',
    ]

    for i in range(0, len(jnts), 2):
        try:
            mc.rename(jnts[i], jnts[i+1])
        except Exception as e:
            mc.warning(e)
            continue