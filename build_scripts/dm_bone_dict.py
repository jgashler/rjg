# Class containing a dictionary to define relationship between bone and rig
# 
# Key: bone name as str (no suffix; 'boneName01_LOC' will be found by using key 'boneName01')
# Value: list containing [parentInSkeleton, parentInRig, optional: commandFlag followed by extra arguments]

# bone_dict = {
#     'polySurface1' : ['leg_L_01_JNT', 'leg_L_IK_BASE_CTRL'],
#     'polySurface2' : ['leg_L_05_JNT', 'leg_L_05_JNT'],
#     'test' : None
# }

class BoneDict:
    def __init__(self):
        self.bone_dict = {

            # tail
            'tail_13_geo' : ['tail_M_06_JNT', 'tail_M_06_fk_CTRL'],
            'tailchip_08_geo' : ['tail_M_06_JNT', 'tail_M_06_fk_CTRL'],
            'tail_12_geo' : ['tail_M_06_JNT', 'tail_M_06_fk_CTRL'],
            'tail_11_geo' : ['tail_M_06_JNT', 'tail_M_06_fk_CTRL'],

            'tail_10_geo' : ['tail_M_05_JNT', 'tail_M_05_fk_CTRL'],
            'tailchip_07_geo' : ['tail_M_05_JNT', 'tail_M_05_fk_CTRL'],
            'tail_09_geo' : ['tail_M_05_JNT', 'tail_M_05_fk_CTRL'],

            'tail_08_geo' : ['tail_M_04_JNT', 'tail_M_04_fk_CTRL'],
            'tailchip_06_geo' : ['tail_M_04_JNT', 'tail_M_04_fk_CTRL'],
            'tail_07_geo' : ['tail_M_04_JNT', 'tail_M_04_fk_CTRL'],

            'tailchip_05_geo' : ['tail_M_03_JNT', 'tail_M_03_fk_CTRL'],
            'tail_06_geo' : ['tail_M_03_JNT', 'tail_M_03_fk_CTRL'],
            'tailchip_04_geo' : ['tail_M_03_JNT', 'tail_M_03_fk_CTRL'],
            'tail_05_geo' : ['tail_M_03_JNT', 'tail_M_03_fk_CTRL'],

            'tail_04_geo' : ['tail_M_02_JNT', 'tail_M_02_fk_CTRL'],
            'tail_03_geo' : ['tail_M_02_JNT', 'tail_M_02_fk_CTRL'],

            'tailchip_02_geo' : ['tail_M_01_JNT', 'tail_M_01_fk_CTRL'],
            'tailchip_03_geo' : ['tail_M_01_JNT', 'tail_M_01_fk_CTRL'],
            'tail_02_geo' : ['tail_M_01_JNT', 'tail_M_01_fk_CTRL'],
            'tailchip_01_geo' : ['tail_M_01_JNT', 'tail_M_01_fk_CTRL'],
            'tail_01_geo' : ['tail_M_01_JNT', 'tail_M_01_fk_CTRL'],

            # left leg
            'toe_pointer_01_L_geo' : ['foot_L_02_JNT', 'foot_L_toe_L_CTRL'],
            'toe_pointer_02_L_geo' : ['foot_L_02_JNT', 'foot_L_toe_L_CTRL'],

            'toe_middle_01_L_geo' : ['foot_L_02_JNT', 'foot_L_toe_L_CTRL'],
            'toe_middle_02_L_geo' : ['foot_L_02_JNT', 'foot_L_toe_L_CTRL'],

            'toe_ring_01_L_geo' : ['foot_L_02_JNT', 'foot_L_toe_L_CTRL'],
            'toe_ring_02_L_geo' : ['foot_L_02_JNT', 'foot_L_toe_L_CTRL'],

            'toe_pinky_02_L_geo' : ['foot_L_02_JNT', 'foot_L_toe_L_CTRL'],
            'toe_pinky_01_L_geo' : ['foot_L_02_JNT', 'foot_L_toe_L_CTRL'],

            'tarsus_L_geo' : ['foot_L_01_JNT', 'foot_L_01_fk_CTRL'],
            'toe_thumb_01_L_geo' : ['foot_L_01_JNT', 'foot_L_01_fk_CTRL'],

            'tibia_L_geo' : ['leg_L_02_JNT', 'leg_L_02_fk_CTRL'],
            'femur_L_geo' : ['leg_L_01_JNT', 'leg_L_01_fk_CTRL'],

            # right leg
            'toe_pointer_01_R_geo' : ['foot_R_02_JNT', 'foot_R_toe_R_CTRL'],
            'toe_pointer_02_R_geo' : ['foot_R_02_JNT', 'foot_R_toe_R_CTRL'],

            'toe_middle_01_R_geo' : ['foot_R_02_JNT', 'foot_R_toe_R_CTRL'],
            'toe_middle_02_R_geo' : ['foot_R_02_JNT', 'foot_R_toe_R_CTRL'],

            'toe_ring_01_R_geo' : ['foot_R_02_JNT', 'foot_R_toe_R_CTRL'],
            'toe_ring_02_R_geo' : ['foot_R_02_JNT', 'foot_R_toe_R_CTRL'],

            'toe_pinky_02_R_geo' : ['foot_R_02_JNT', 'foot_R_toe_R_CTRL'],
            'toe_pinky_01_R_geo' : ['foot_R_02_JNT', 'foot_R_toe_R_CTRL'],

            'tarsus_R_geo' : ['foot_R_01_JNT', 'foot_R_01_fk_CTRL'],
            'toe_thumb_01_R_geo' : ['foot_R_01_JNT', 'foot_R_01_fk_CTRL'],

            'tibia_R_geo' : ['leg_R_02_JNT', 'leg_R_02_fk_CTRL'],
            'femur_R_geo' : ['leg_R_01_JNT', 'leg_R_01_fk_CTRL'],

            # left arm
            'finger_thumb_03_L_geo' : ['fingerThumb_L_03_JNT', 'fingerThumb_L_03_fk_CTRL'],
            'finger_thumb_02_L_geo' : ['fingerThumb_L_02_JNT', 'fingerThumb_L_02_fk_CTRL'],
            'finger_thumb_01_L_geo' : ['fingerThumb_L_01_JNT', 'fingerThumb_L_01_fk_CTRL'],

            'finger_pointer_03_L_geo' : ['fingerIndex_L_03_JNT', 'fingerIndex_L_03_fk_CTRL'],
            'finger_pointer_02_L_geo' : ['fingerIndex_L_02_JNT', 'fingerIndex_L_02_fk_CTRL'],
            'finger_pointer_01_L_geo' : ['fingerIndex_L_01_JNT', 'fingerIndex_L_01_fk_CTRL'],

            'finger_middle_03_L_geo' : ['fingerMiddle_L_03_JNT', 'fingerMiddle_L_03_fk_CTRL'],
            'finger_middle_02_L_geo' : ['fingerMiddle_L_02_JNT', 'fingerMiddle_L_02_fk_CTRL'],
            'finger_middle_01_L_geo' : ['fingerMiddle_L_01_JNT', 'fingerMiddle_L_01_fk_CTRL'],

            'finger_ring_03_L_geo' : ['fingerRing_L_03_JNT', 'fingerRing_L_03_fk_CTRL'],
            'finger_ring_02_L_geo' : ['fingerRing_L_02_JNT', 'fingerRing_L_02_fk_CTRL'],
            'finger_ring_01_L_geo' : ['fingerRing_L_01_JNT', 'fingerRing_L_01_fk_CTRL'],

            'finger_pinky_03_L_geo' : ['fingerPinky_L_03_JNT', 'fingerPinky_L_03_fk_CTRL'],
            'finger_pinky_02_L_geo' : ['fingerPinky_L_02_JNT', 'fingerPinky_L_02_fk_CTRL'],
            'finger_pinky_01_L_geo' : ['fingerPinky_L_01_JNT', 'fingerPinky_L_01_fk_CTRL'],

            'metacarpal_L_geo' : ['hand_L_JNT', 'hand_L_local_CTRL'],
            'ulna_L_geo' : ['arm_L_02_JNT', 'arm_L_02_fk_CTRL'],
            'radius_L_geo' : ['arm_L_02_JNT', 'arm_L_02_fk_CTRL'],
            'humerus_L_geo' : ['arm_L_01_JNT', 'arm_L_01_fk_CTRL'],
            'scapula_L_geo' : ['clavicle_L_01_JNT', 'clavicle_L_01_JNT'],

            # right arm
            'finger_thumb_03_R_geo' : ['fingerThumb_R_03_JNT', 'fingerThumb_R_03_fk_CTRL'],
            'finger_thumb_02_R_geo' : ['fingerThumb_R_02_JNT', 'fingerThumb_R_02_fk_CTRL'],
            'finger_thumb_01_R_geo' : ['fingerThumb_R_01_JNT', 'fingerThumb_R_01_fk_CTRL'],

            'finger_pointer_03_R_geo' : ['fingerIndex_R_03_JNT', 'fingerIndex_R_03_fk_CTRL'],
            'finger_pointer_02_R_geo' : ['fingerIndex_R_02_JNT', 'fingerIndex_R_02_fk_CTRL'],
            'finger_pointer_01_R_geo' : ['fingerIndex_R_01_JNT', 'fingerIndex_R_01_fk_CTRL'],

            'finger_middle_03_R_geo' : ['fingerMiddle_R_03_JNT', 'fingerMiddle_R_03_fk_CTRL'],
            'finger_middle_02_R_geo' : ['fingerMiddle_R_02_JNT', 'fingerMiddle_R_02_fk_CTRL'],
            'finger_middle_01_R_geo' : ['fingerMiddle_R_01_JNT', 'fingerMiddle_R_01_fk_CTRL'],

            'finger_ring_03_R_geo' : ['fingerRing_R_03_JNT', 'fingerRing_R_03_fk_CTRL'],
            'finger_ring_02_R_geo' : ['fingerRing_R_02_JNT', 'fingerRing_R_02_fk_CTRL'],
            'finger_ring_01_R_geo' : ['fingerRing_R_01_JNT', 'fingerRing_R_01_fk_CTRL'],

            'finger_pinky_03_R_geo' : ['fingerPinky_R_03_JNT', 'fingerPinky_R_03_fk_CTRL'],
            'finger_pinky_02_R_geo' : ['fingerPinky_R_02_JNT', 'fingerPinky_R_02_fk_CTRL'],
            'finger_pinky_01_R_geo' : ['fingerPinky_R_01_JNT', 'fingerPinky_R_01_fk_CTRL'],

            'metacarpal_R_geo' : ['hand_R_JNT', 'hand_R_local_CTRL'],
            'ulna_R_geo' : ['arm_R_02_JNT', 'arm_R_02_fk_CTRL'],
            'radius_R_geo' : ['arm_R_02_JNT', 'arm_R_02_fk_CTRL'],
            'humerus_R_geo' : ['arm_R_01_JNT', 'arm_R_01_fk_CTRL'],
            'scapula_R_geo' : ['clavicle_R_01_JNT', 'clavicle_R_01_JNT'],

            # spine
            'pelvis_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],
            'lumbarvertebrae_05_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],
            'lumbarvertebrae_04_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],
            'lumbarvertebrae_03_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],
            'lumbarvertebraechip_01_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],

            'lumbarvertebrae_02_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'lumbarvertebrae_01_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'chestrock_32_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'chestrock_31_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'chestrock_30_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'chestrock_29_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'chestrock_28_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'chestrock_27_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'chestrock_26_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'chestrock_25_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'chestrock_24_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'spine_01_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'spine_02_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],

            'spine_03_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'spine_04_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'spine_05_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_23_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_22_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_21_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_20_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_19_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_18_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_17_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_16_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_15_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_14_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_13_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_12_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_11_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_10_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_09_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_08_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_07_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_06_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_05_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'chestrock_33_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],

            'spine_06_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'chestrock_05_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'chestrock_04_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'chestrock_03_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'chestrock_02_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'chestrock_01_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],

            # neck and head
            'neck_01_geo' : ['neck_M_01_JNT', 'neck_01_FK_M_CTRL'],
            'neck_02_geo' : ['neck_M_01_JNT', 'neck_01_FK_M_CTRL'],
            'neck_03_geo' : ['neck_M_02_JNT', 'neck_02_FK_M_CTRL'],
            'neck_04_geo' : ['neck_M_02_JNT', 'neck_02_FK_M_CTRL'],
            'neck_05_geo' : ['neck_M_02_JNT', 'neck_02_FK_M_CTRL'],

            'head_geo' : ['head_M_JNT', 'head_M_01_CTRL'],
            'upperteeth_geo' : ['head_M_JNT', 'head_M_01_CTRL'],
            'eye_L_geo' : ['head_M_JNT', 'head_M_01_CTRL'],
            'eye_R_geo' : ['head_M_JNT', 'head_M_01_CTRL'],

            'jaw_geo' : ['jaw_M_JNT', 'jaw_M_M_CTRL'],
            'lowerteeth_geo' : ['jaw_M_JNT', 'jaw_M_M_CTRL'],
            'tongue_geo' : ['jaw_M_JNT', 'jaw_M_M_CTRL'],




        }