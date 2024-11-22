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
            ### Feet and legs
            'distal_phalanx_foot_1_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'proximal_phalanx_foot_1_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'distal_phalanx_foot_2_L_geo' :  ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'middle_phalanx_foot_2_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'proximal_phalanx_foot_2_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'distal_phalanx_foot_3_L_geo' :  ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'middle_phalanx_foot_3_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'proximal_phalanx_foot_3_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'distal_phalanx_foot_4_L_geo' :  ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'middle_phalanx_foot_4_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'proximal_phalanx_foot_4_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'distal_phalanx_foot_5_L_geo' :  ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'middle_phalanx_foot_5_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'proximal_phalanx_foot_5_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'metatarsal_1_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'metatarsal_2_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'metatarsal_3_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'metatarsal_4_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            'metatarsal_5_L_geo' : ['foot_L_02_JNT', 'foot_L_02_fk_CTRL'],
            
            'distal_phalanx_foot_1_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'proximal_phalanx_foot_1_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'distal_phalanx_foot_2_R_geo' :  ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'middle_phalanx_foot_2_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'proximal_phalanx_foot_2_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'distal_phalanx_foot_3_R_geo' :  ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'middle_phalanx_foot_3_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'proximal_phalanx_foot_3_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'distal_phalanx_foot_4_R_geo' :  ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'middle_phalanx_foot_4_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'proximal_phalanx_foot_4_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'distal_phalanx_foot_5_R_geo' :  ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'middle_phalanx_foot_5_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'proximal_phalanx_foot_5_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'metatarsal_1_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'metatarsal_2_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'metatarsal_3_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'metatarsal_4_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            'metatarsal_5_R_geo' : ['foot_R_02_JNT', 'foot_R_02_fk_CTRL'],
            
            'medial_cuneiform_L_geo' : ['foot_L_01_JNT', 'foot_L_01_fk_CTRL'],
            'intermediate_cuneiform_L_geo' : ['foot_L_01_JNT', 'foot_L_01_fk_CTRL'],
            'lateral_cuneiform_L_geo' : ['foot_L_01_JNT', 'foot_L_01_fk_CTRL'],
            'cuboid_L_geo' : ['foot_L_01_JNT', 'foot_L_01_fk_CTRL'],
            'navicular_L_geo' : ['foot_L_01_JNT', 'foot_L_01_fk_CTRL'],
            'talus_L_geo' : ['foot_L_01_JNT', 'foot_L_01_fk_CTRL'],
            'calcaneus_L_geo' : ['foot_L_01_JNT', 'foot_L_01_fk_CTRL'],
                
            'medial_cuneiform_R_geo' : ['foot_R_01_JNT', 'foot_R_01_fk_CTRL'],
            'intermediate_cuneiform_R_geo' : ['foot_R_01_JNT', 'foot_R_01_fk_CTRL'],
            'lateral_cuneiform_R_geo' : ['foot_R_01_JNT', 'foot_R_01_fk_CTRL'],
            'cuboid_R_geo' : ['foot_R_01_JNT', 'foot_R_01_fk_CTRL'],
            'navicular_R_geo' : ['foot_R_01_JNT', 'foot_R_01_fk_CTRL'],
            'talus_R_geo' : ['foot_R_01_JNT', 'foot_R_01_fk_CTRL'],
            'calcaneus_R_geo' : ['foot_R_01_JNT', 'foot_R_01_fk_CTRL'],
            
            'tibia_L_geo' : ['leg_L_05_JNT', 'leg_L_02_fk_CTRL'],
            'fibula_L_geo' : ['leg_L_05_JNT', 'leg_L_02_fk_CTRL'],
            'patella_L_geo' : ['leg_L_05_JNT', 'leg_L_02_fk_CTRL'],
                
            'tibia_R_geo' :  ['leg_R_05_JNT', 'leg_R_02_fk_CTRL'],
            'fibula_R_geo' : ['leg_R_05_JNT', 'leg_R_02_fk_CTRL'],
            'patella_R_geo' : ['leg_R_05_JNT', 'leg_R_02_fk_CTRL'],
            
            'femur_L_geo' : ['leg_L_01_JNT', 'leg_L_01_fk_CTRL'],
            
            'femur_R_geo' : ['leg_R_01_JNT', 'leg_R_01_fk_CTRL'],
            
            # Hands and arms
            'distal_phalanx_hand_1_L_geo' : ['fingerThumb_L_03_JNT', 'fingerThumb_L_03_fk_CTRL'],
            'proximal_phalanx_hand_1_L_geo' : ['fingerThumb_L_02_JNT', 'fingerThumb_L_02_fk_CTRL'],
            'metacarpal_1_L_geo' : ['fingerThumb_L_01_JNT', 'fingerThumb_L_01_fk_CTRL'],
            'distal_phalanx_hand_2_L_geo' : ['fingerIndex_L_04_JNT', 'fingerIndex_L_04_fk_CTRL'],
            'middle_phalanx_hand_2_L_geo' : ['fingerIndex_L_03_JNT', 'fingerIndex_L_03_fk_CTRL'],
            'proximal_phalanx_hand_2_L_geo' : ['fingerIndex_L_02_JNT', 'fingerIndex_L_02_fk_CTRL'],
            'metacarpal_2_L_geo' : ['fingerIndex_L_01_JNT', 'fingerIndex_L_01_fk_CTRL'],
            'distal_phalanx_hand_3_L_geo' : ['fingerMiddle_L_04_JNT', 'fingerMiddle_L_04_fk_CTRL'],
            'middle_phalanx_hand_3_L_geo' : ['fingerMiddle_L_03_JNT', 'fingerMiddle_L_03_fk_CTRL'],
            'proximal_phalanx_hand_3_L_geo' : ['fingerMiddle_L_02_JNT', 'fingerMiddle_L_02_fk_CTRL'],
            'metacarpal_3_L_geo' : ['fingerMiddle_L_01_JNT', 'fingerMiddle_L_01_fk_CTRL'],
            'distal_phalanx_hand_4_L_geo' : ['fingerRing_L_04_JNT', 'fingerRing_L_04_fk_CTRL'],
            'middle_phalanx_hand_4_L_geo' : ['fingerRing_L_03_JNT', 'fingerRing_L_03_fk_CTRL'],
            'proximal_phalanx_hand_4_L_geo' : ['fingerRing_L_02_JNT', 'fingerRing_L_02_fk_CTRL'],
            'metacarpal_4_L_geo' : ['fingerRing_L_01_JNT', 'fingerRing_L_01_fk_CTRL'],
            'distal_phalanx_hand_5_L_geo' : ['fingerPinky_L_04_JNT', 'fingerPinky_L_04_fk_CTRL'],
            'middle_phalanx_hand_5_L_geo' : ['fingerPinky_L_03_JNT', 'fingerPinky_L_03_fk_CTRL'],
            'proximal_phalanx_hand_5_L_geo' : ['fingerPinky_L_02_JNT', 'fingerPinky_L_02_fk_CTRL'],
            'metacarpal_5_L_geo' : ['fingerPinky_L_01_JNT', 'fingerPinky_L_01_fk_CTRL'],
            
            'distal_phalanx_hand_1_R_geo' : ['fingerThumb_R_03_JNT', 'fingerThumb_R_03_fk_CTRL'],
            'proximal_phalanx_hand_1_R_geo' : ['fingerThumb_R_02_JNT', 'fingerThumb_R_02_fk_CTRL'],
            'metacarpal_1_R_geo' : ['fingerThumb_R_01_JNT', 'fingerThumb_R_01_fk_CTRL'],
            'distal_phalanx_hand_2_R_geo' : ['fingerIndex_R_04_JNT', 'fingerIndex_R_04_fk_CTRL'],
            'middle_phalanx_hand_2_R_geo' : ['fingerIndex_R_03_JNT', 'fingerIndex_R_03_fk_CTRL'],
            'proximal_phalanx_hand_2_R_geo' : ['fingerIndex_R_02_JNT', 'fingerIndex_R_02_fk_CTRL'],
            'metacarpal_2_R_geo' : ['fingerIndex_R_01_JNT', 'fingerIndex_R_01_fk_CTRL'],
            'distal_phalanx_hand_3_R_geo' : ['fingerMiddle_R_04_JNT', 'fingerMiddle_R_04_fk_CTRL'],
            'middle_phalanx_hand_3_R_geo' : ['fingerMiddle_R_03_JNT', 'fingerMiddle_R_03_fk_CTRL'],
            'proximal_phalanx_hand_3_R_geo' : ['fingerMiddle_R_02_JNT', 'fingerMiddle_R_02_fk_CTRL'],
            'metacarpal_3_R_geo' : ['fingerMiddle_R_01_JNT', 'fingerMiddle_R_01_fk_CTRL'],
            'distal_phalanx_hand_4_R_geo' : ['fingerRing_R_04_JNT', 'fingerRing_R_04_fk_CTRL'],
            'middle_phalanx_hand_4_R_geo' : ['fingerRing_R_03_JNT', 'fingerRing_R_03_fk_CTRL'],
            'proximal_phalanx_hand_4_R_geo' : ['fingerRing_R_02_JNT', 'fingerRing_R_02_fk_CTRL'],
            'metacarpal_4_R_geo' : ['fingerRing_R_01_JNT', 'fingerRing_R_01_fk_CTRL'],
            'distal_phalanx_hand_5_R_geo' : ['fingerPinky_R_04_JNT', 'fingerPinky_R_04_fk_CTRL'],
            'middle_phalanx_hand_5_R_geo' : ['fingerPinky_R_03_JNT', 'fingerPinky_R_03_fk_CTRL'],
            'proximal_phalanx_hand_5_R_geo' : ['fingerPinky_R_02_JNT', 'fingerPinky_R_02_fk_CTRL'],
            'metacarpal_5_R_geo' : ['fingerPinky_R_01_JNT', 'fingerPinky_R_01_fk_CTRL'],
            
            'trapezium_L_geo' : ['arm_L_09_JNT', 'arm_L_03_fk_CTRL'],
            'trapezoid_L_geo' : ['arm_L_09_JNT', 'arm_L_03_fk_CTRL'],
            'scaphoid_L_geo' : ['arm_L_09_JNT', 'arm_L_03_fk_CTRL'],
            'capitate_L_geo' : ['arm_L_09_JNT', 'arm_L_03_fk_CTRL'],
            'lunate_L_geo' : ['arm_L_09_JNT', 'arm_L_03_fk_CTRL'],
            'hamate_L_geo' : ['arm_L_09_JNT', 'arm_L_03_fk_CTRL'],
            'triquetrum_L_geo' : ['arm_L_09_JNT', 'arm_L_03_fk_CTRL'],
            'pisiform_L_geo' : ['arm_L_09_JNT', 'arm_L_03_fk_CTRL'],
            
            'trapezium_R_geo' : ['arm_R_09_JNT', 'arm_R_03_fk_CTRL'],
            'trapezoid_R_geo' : ['arm_R_09_JNT', 'arm_R_03_fk_CTRL'],
            'scaphoid_R_geo' : ['arm_R_09_JNT', 'arm_R_03_fk_CTRL'],
            'capitate_R_geo' : ['arm_R_09_JNT', 'arm_R_03_fk_CTRL'],
            'lunate_R_geo' : ['arm_R_09_JNT', 'arm_R_03_fk_CTRL'],
            'hamate_R_geo' : ['arm_R_09_JNT', 'arm_R_03_fk_CTRL'],
            'triquetrum_R_geo' : ['arm_R_09_JNT', 'arm_R_03_fk_CTRL'],
            'pisiform_R_geo' : ['arm_R_09_JNT', 'arm_R_03_fk_CTRL'],
                
            'radius_L_geo' : ['arm_L_05_JNT', 'arm_L_02_fk_CTRL'],
            'ulna_L_geo' : ['arm_L_05_JNT', 'arm_L_02_fk_CTRL'],
                
            'radius_R_geo' : ['arm_R_05_JNT', 'arm_R_02_fk_CTRL'],
            'ulna_R_geo' : ['arm_R_05_JNT', 'arm_R_02_fk_CTRL'],
            
            'humerus_L_geo' : ['arm_L_01_JNT', 'arm_L_01_fk_CTRL'],
                
            'humerus_R_geo' : ['arm_R_01_JNT', 'arm_R_01_fk_CTRL'],

            # Hips and spine
            'os_coxa_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],
            'coccyx_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],
            'sacrum_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],
            'lumbar_disc_l5_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],
            'lumbar_vertebra_l5_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],
            'lumbar_disc_l4_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],
            'lumbar_vertebra_l4_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],
            'lumbar_disc_l3_geo' : ['spine_M_01_JNT', 'COG_M_CTRL'],

            'lumbra_vertebra_l3_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'lumbar_disc_l2_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'lumbar_vertebra_l2_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'lumbar_disc_l1_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'lumbar_vertebra_l1_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],
            'thoracic_disc_t12_geo' : ['spine_M_02_JNT', 'spine_02_FK_M_CTRL'],

            'thoracic_vertebra_t12_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'thoracic_disc_t11_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'thoracic_vertebra_t11_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'thoracic_disc_t10_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'thoracic_vertebra_t10_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'thoracic_disc_t9_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'thoracic_vertebra_t9_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'rib_10_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'rib_11_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            'rib_12_geo' : ['spine_M_03_JNT', 'spine_03_FK_M_CTRL'],
            
            'thoracic_disc_t8_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_vertebra_t8_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_disc_t7_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_vertebra_t7_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_disc_t6_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_vertebra_t6_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_disc_t5_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_vertebra_t5_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_disc_t4_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_vertebra_t4_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_disc_t3_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_vertebra_t3_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_disc_t2_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_vertebra_t2_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_disc_t1_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'thoracic_vertebra_t1_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'rib_01_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'rib_02_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'rib_03_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'rib_04_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'rib_05_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'rib_06_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'rib_07_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'rib_08_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'rib_09_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'sternum_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'costal_cartilage_1_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'costal_cartilage_2_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'costal_cartilage_3_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'costal_cartilage_4_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'costal_cartilage_5_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],
            'costal_cartilage_6_geo' : ['chest_M_JNT', 'chest_M_02_CTRL'],

            'clavicle_L_geo' : ['clavicle_L_01_JNT', 'clavicle_L_CTRL'],
            'scapula_L_geo'  : ['clavicle_L_01_JNT', 'clavicle_L_CTRL'],

            'clavicle_R_geo' : ['clavicle_R_01_JNT', 'clavicle_R_CTRL'],
            'scapula_R_geo'  : ['clavicle_R_01_JNT', 'clavicle_R_CTRL'],

            'cervical_disc_c7_geo' : ['neck_M_01_JNT', 'neck_01_FK_M_CTRL'],
            'cervical_vertebra_c7_geo' : ['neck_M_01_JNT', 'neck_01_FK_M_CTRL'],
            'cervical_disc_c6_geo' : ['neck_M_01_JNT', 'neck_01_FK_M_CTRL'],
            'cervical_vertebra_c6_geo' : ['neck_M_01_JNT', 'neck_01_FK_M_CTRL'],
            'cervical_disc_c5_geo' : ['neck_M_01_JNT', 'neck_01_FK_M_CTRL'],

            'cervical_vertebra_c5_geo' : ['neck_M_02_JNT', 'neck_02_FK_M_CTRL'],
            'cervical_disc_c4_geo' : ['neck_M_02_JNT', 'neck_02_FK_M_CTRL'],
            'cervical_vertebra_c4_geo' : ['neck_M_02_JNT', 'neck_02_FK_M_CTRL'],
            'cervical_disc_c3_geo' : ['neck_M_02_JNT', 'neck_02_FK_M_CTRL'],
            'cervical_vertebra_c3_geo' : ['neck_M_02_JNT', 'neck_02_FK_M_CTRL'],
            'cervical_disc_c2_geo' : ['neck_M_02_JNT', 'neck_02_FK_M_CTRL'],

            'cervical_vertebra_c2_geo' : ['neck_M_03_JNT', 'head_M_01_CTRL'],
            'cranium_geo' : ['neck_M_03_JNT', 'head_M_01_CTRL'],
            'mandible_geo' : ['neck_M_03_JNT', 'head_M_01_CTRL'],
            'teeth_top_geo' : ['neck_M_03_JNT', 'head_M_01_CTRL'],
            'teeth_bottom_geo' : ['neck_M_03_JNT', 'head_M_01_CTRL'],




        }