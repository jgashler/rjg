#import maya.cmds as mc

# def get_joint_orientation(joint):
#     """
#     Retrieves the joint's true world-space orientation using xform.
#     """
#     world_matrix = mc.xform(joint, q=True, matrix=True, worldSpace=True)
#     true_orient = mc.xform(joint, q=True, rotation=True, worldSpace=True)
#     return world_matrix, true_orient

# def reformat_parent_name(parent_name, side):
#     """
#     Reformats the parent joint name based on the side ("Left" or "Right").
#     """
#     if side == "Right" and "_L_" in parent_name:
#         return parent_name.replace("_L_", "_R_")
#     return parent_name  # No change for left side or other naming conventions

# def reformat_joint_name(guide_name):
#     """
#     Reformats the guide name according to the provided naming scheme.
#     """
#     replacements = {
#         "hand_l": "hand_L_JNT",
#         "lowerarm_l": "arm_L_02_JNT",
#         "upperarm_l": "arm_L_01_JNT",
#         "clavicle_l": "clavicle_L_01_JNT",
#         "spine_05": "spine_M_05_JNT",
#         "thigh_l": "leg_L_01_JNT",
#         "calf_l": "leg_L_02_JNT",
#         "thumb_01_l": "fingerThumb_L_01_JNT",
#         "thumb_02_l": "fingerThumb_L_02_JNT",
#         "thumb_03_l": "fingerThumb_L_03_JNT",
#         "index_metacarpal_l": "fingerIndex_L_01_JNT",
#         "index_01_l": "fingerIndex_L_02_JNT",
#         "index_02_l": "fingerIndex_L_03_JNT",
#         "index_03_l": "fingerIndex_L_04_JNT",
#         "middle_metacarpal_l": "fingerMiddle_L_01_JNT",
#         "middle_01_l": "fingerMiddle_L_02_JNT",
#         "middle_02_l": "fingerMiddle_L_03_JNT",
#         "middle_03_l": "fingerMiddle_L_04_JNT",
#         "ring_metacarpal_l": "fingerRing_L_01_JNT",
#         "ring_01_l": "fingerRing_L_02_JNT",
#         "ring_02_l": "fingerRing_L_03_JNT",
#         "ring_03_l": "fingerRing_L_04_JNT",
#         "pinky_metacarpal_l": "fingerPinky_L_01_JNT",
#         "pinky_01_l": "fingerPinky_L_02_JNT",
#         "pinky_02_l": "fingerPinky_L_03_JNT",
#         "pinky_03_l": "fingerPinky_L_04_JNT"
#     }

#     for old_name, new_name in replacements.items():
#         if old_name in guide_name:
#             return guide_name.replace(old_name, new_name)
#     return guide_name  # Return the name unchanged if no match found

# def build_parents(CorrGuides, CorrParrent):
#     for side in ["Left", "Right"]:
#         side_prefix = "L_" if side == "Left" else "R_"
#         side_suffix = "_l" if side == "Left" else "_r"
#         for i, guide in enumerate(CorrGuides):
#             try:
#                 # Rename guide with side prefix
#                 guide_name = f"{side}{guide}"
                
#                 # Reformat guide and parent names
#                 guide_name = reformat_joint_name(guide_name)
#                 parent_name = CorrParrent[i]
#                 parent_name = reformat_parent_name(parent_name, side)
                
#                 # Get world transform and true orientation
#                 world_matrix, true_orient = get_joint_orientation(guide_name)
                
#                 # Handle the exception for "spine_05" where no _l or _r is added
#                 if parent_name == "spine_M_05_JNT":
#                     new_joint = guide  # No _l or _r added for "spine_05"
#                 else:
#                     new_joint = guide + side_suffix  # Add _l or _r
                
#                 # Create the corrective joint
#                 mc.select(clear=True)
#                 cor_jnt = mc.joint(name=new_joint)
                
#                 # Apply transformations
#                 mc.xform(cor_jnt, matrix=world_matrix, worldSpace=True)
#                 mc.setAttr(cor_jnt + ".jointOrientX", true_orient[0])
#                 mc.setAttr(cor_jnt + ".jointOrientY", true_orient[1])
#                 mc.setAttr(cor_jnt + ".jointOrientZ", true_orient[2])
                
#                 # Ensure rotate values are zeroed out
#                 mc.setAttr(cor_jnt + ".rotateX", 0)
#                 mc.setAttr(cor_jnt + ".rotateY", 0)
#                 mc.setAttr(cor_jnt + ".rotateZ", 0)
                
#                 # Parent the new joint under the corresponding parent
#                 mc.parent(cor_jnt, parent_name)
                
#                 print(f"Created {cor_jnt} and parented under {parent_name}")
            
#             except Exception as e:
#                 print(f"Error processing {guide}: {e}")

# def BuildCorrectives(CorrGuides, CorrParrent):
#     build_parents(CorrGuides, CorrParrent)

# Example lists for testing
# CorrGuides2 = ["upperarm_twistCor_01", "lowerarm_correctiveRoot", "upperarm_correctiveRoot", "thigh_correctiveRoot", "calf_correctiveRoot"]
# CorrParrent2 = ["upperarm_L_JNT", "lowerarm_L_02_JNT", "upperarm_L_01_JNT", "thigh_L_01_JNT", "calf_L_02_JNT"]
# build_parents(CorrGuides2, CorrParrent2)

# CorrGuides = ["lowerarm_out", "lowerarm_fwd", "lowerarm_in", "lowerarm_bck", 
#               "wrist_outer", "wrist_inner",
#               "upperarm_bicep", "upperarm_tricep",
#               "upperarm_out", "upperarm_bck", "upperarm_fwd", "upperarm_in", "upperarm_twist_02", 
#               "clavicle_out", "clavicle_scap",
#               "clavicle_pec", "spine_04_latissimus",
#               "thigh_fwd", "thigh_fwd_lwr", "thigh_in", "thigh_bck", "thigh_out", "thigh_bck_lwr", "thigh_twist_01", "thigh_twist_02",
#               "calf_knee", "calf_kneeBack", "calf_twist_01", 
#               "HandThumb0_Bot", "HandThumb1_Bot", "HandThumb1_TOP", "HandThumb2_Bot", "HandThumb2_TOP", "HandThumb3_Bot", "HandThumb3_TOP",
#               "HandIndex0_BOT", "HandIndex1_BOT", "HandIndex1_TOP","HandIndex2_BOT", "HandIndex2_TOP", "HandIndex3_BOT", "HandIndex3_TOP",
#               "HandMiddle0_BOT", "HandMiddle1_BOT", "HandMiddle1_TOP","HandMiddle2_BOT", "HandMiddle2_TOP", "HandMiddle3_BOT", "HandMiddle3_TOP",
#               "HandRing0_BOT", "HandRing1_BOT", "HandRing1_TOP","HandRing2_BOT", "HandRing2_TOP", "HandRing3_BOT", "HandRing3_TOP",
#               "HandPinky0_BOT", "HandPinky1_BOT", "HandPinky1_TOP","HandPinky2_BOT", "HandPinky2_TOP", "HandPinky3_BOT", "HandPinky3_TOP",
#              ]

# CorrParrent = ["lowerarm_L_02_JNT", "lowerarm_L_02_JNT", "lowerarm_L_02_JNT", "lowerarm_L_02_JNT",
#                "hand_L_JNT", "hand_L_JNT",
#                "upperarm_L_01_JNT", "upperarm_L_01_JNT", 
#                "upperarm_L_01_JNT", "upperarm_L_01_JNT", "upperarm_L_01_JNT", "upperarm_L_01_JNT", "upperarm_L_01_JNT",
#                "clavicle_L_01_JNT", "clavicle_L_01_JNT",
#                "spine_M_05_JNT", "spine_M_05_JNT",
#                "thigh_L_01_JNT", "thigh_L_01_JNT", "thigh_L_01_JNT", "thigh_L_01_JNT", "thigh_L_01_JNT", "thigh_L_01_JNT", "thigh_L_01_JNT", "thigh_L_01_JNT",
#                "calf_L_02_JNT", "calf_L_02_JNT", "calf_L_02_JNT",
#                "thumb_L_01_JNT", "thumb_L_01_JNT", "thumb_L_01_JNT", "thumb_L_02_JNT", "thumb_L_02_JNT", "thumb_L_03_JNT", "thumb_L_03_JNT",
#                "index_L_01_JNT", "index_L_01_JNT", "index_L_02_JNT", "index_L_02_JNT", "index_L_03_JNT", "index_L_03_JNT",
#                "middle_L_01_JNT", "middle_L_01_JNT", "middle_L_02_JNT", "middle_L_02_JNT", "middle_L_03_JNT", "middle_L_03_JNT", 
#                "ring_L_01_JNT", "ring_L_01_JNT", "ring_L_02_JNT", "ring_L_02_JNT", "ring_L_03_JNT", "ring_L_03_JNT", 
#                "pinky_L_01_JNT", "pinky_L_01_JNT", "pinky_L_02_JNT", "pinky_L_02_JNT", "pinky_L_03_JNT", "pinky_L_03_JNT", 
#               ]

# BuildCorrectives(CorrGuides, CorrParrent)



import maya.cmds as mc

def get_joint_orientation(joint):
    """
    Retrieves the joint's true world-space orientation using xform.
    """
    world_matrix = mc.xform(joint, q=True, matrix=True, worldSpace=True)
    true_orient = mc.xform(joint, q=True, rotation=True, worldSpace=True)
    return world_matrix, true_orient

def build_parents(CorrGuides, CorrParrent):
    for side in ["Left", "Right"]:
        side_prefix = "L_" if side == "Left" else "R_"
        side_suffix = "_l" if side == "Left" else "_r"
        for i, guide in enumerate(CorrGuides):
            try:
                # Rename guide with side prefix
                guide_name = f"{side}{guide}"
                
                # Get world transform and true orientation
                world_matrix, true_orient = get_joint_orientation(guide_name)
                renameguide = mc.rename(guide_name, f'{guide_name}_guide')
                # Handle the exception for "spine_05" where no _l or _r is added
                if CorrParrent[i] == "spine_05":
                    new_joint = guide  # No _l or _r added for "spine_05"
                else:
                    new_joint = guide + side_suffix  # Add _l or _r
                
                # Create the corrective joint
                mc.select(clear=True)
                cor_jnt = mc.joint(name=new_joint)
                
                # Apply transformations
                mc.xform(cor_jnt, matrix=world_matrix, worldSpace=True)
                mc.setAttr(cor_jnt + ".jointOrientX", true_orient[0])
                mc.setAttr(cor_jnt + ".jointOrientY", true_orient[1])
                mc.setAttr(cor_jnt + ".jointOrientZ", true_orient[2])
                
                # Ensure rotate values are zeroed out
                mc.setAttr(cor_jnt + ".rotateX", 0)
                mc.setAttr(cor_jnt + ".rotateY", 0)
                mc.setAttr(cor_jnt + ".rotateZ", 0)
                
                # Adjust parent name based on side
                parent_joint = CorrParrent[i]
                if side == "Right" and CorrParrent[i] != "spine_05":
                    parent_joint = parent_joint.replace("_l", "_r")
                
                # Parent the new joint under the corresponding parent
                mc.parent(cor_jnt, parent_joint)
                
                print(f"Created {cor_jnt} and parented under {parent_joint}")
            
            except Exception as e:
                print(f"Error processing {guide}: {e}")

def BuildCorrectives(CorrGuides, CorrParrent):
    build_parents(CorrGuides, CorrParrent)
    for side in ["Left", "Right"]:
        side_prefix = "L_" if side == "Left" else "R_"
        side_suffix = "_l" if side == "Left" else "_r"
        for i, guide in enumerate(CorrGuides):
            try:
                # Rename guide with side prefix
                guide_name = f"{side}{guide}"
                
                # Get world transform and true orientation
                world_matrix, true_orient = get_joint_orientation(guide_name)
                renameguide = mc.rename(guide_name, f'{guide_name}_guide')
                # Handle the exception for "spine_05" where no _l or _r is added
                if CorrParrent[i] == "spine_05":
                    new_joint = guide  # No _l or _r added for "spine_05"
                else:
                    new_joint = guide + side_suffix  # Add _l or _r
                
                # Create the corrective joint
                mc.select(clear=True)
                cor_jnt = mc.joint(name=new_joint)
                
                # Apply transformations
                mc.xform(cor_jnt, matrix=world_matrix, worldSpace=True)
                mc.setAttr(cor_jnt + ".jointOrientX", true_orient[0])
                mc.setAttr(cor_jnt + ".jointOrientY", true_orient[1])
                mc.setAttr(cor_jnt + ".jointOrientZ", true_orient[2])
                
                # Ensure rotate values are zeroed out
                mc.setAttr(cor_jnt + ".rotateX", 0)
                mc.setAttr(cor_jnt + ".rotateY", 0)
                mc.setAttr(cor_jnt + ".rotateZ", 0)
                
                # Adjust parent name based on side
                parent_joint = CorrParrent[i]
                if side == "Right" and CorrParrent[i] != "spine_05":
                    parent_joint = parent_joint.replace("_l", "_r")
                
                # Parent the new joint under the corresponding parent
                mc.parent(cor_jnt, parent_joint)
                
                print(f"Created {cor_jnt} and parented under {parent_joint}")
            
            except Exception as e:
                print(f"Error processing {guide}: {e}")

'''
# Example lists for testing
CorrGuides2 = ["upperarm_twistCor_01", "lowerarm_correctiveRoot", "upperarm_correctiveRoot", "thigh_correctiveRoot", "calf_correctiveRoot"]
CorrParrent2 = ["upperarm_l", "lowerarm_l", "upperarm_l", "thigh_l", "calf_l"]
build_parents(CorrGuides2, CorrParrent2)

CorrGuides = ["lowerarm_out", "lowerarm_fwd", "lowerarm_in", "lowerarm_bck", 
              "wrist_outer", "wrist_inner",
              "upperarm_bicep", "upperarm_tricep",
              "upperarm_out", "upperarm_bck", "upperarm_fwd", "upperarm_in", "upperarm_twist_02", 
              "clavicle_out", "clavicle_scap",
              "clavicle_pec", "spine_04_latissimus",
              "thigh_fwd", "thigh_fwd_lwr", "thigh_in", "thigh_bck", "thigh_out", "thigh_bck_lwr", "thigh_twist_01", "thigh_twist_02",
              "calf_knee", "calf_kneeBack", "calf_twist_01", 
              "HandThumb0_Bot", "HandThumb1_Bot", "HandThumb1_TOP", "HandThumb2_Bot", "HandThumb2_TOP", "HandThumb3_Bot", "HandThumb3_TOP",
              "HandIndex0_BOT", "HandIndex1_BOT", "HandIndex1_TOP","HandIndex2_BOT", "HandIndex2_TOP", "HandIndex3_BOT", "HandIndex3_TOP",
              "HandMiddle0_BOT", "HandMiddle1_BOT", "HandMiddle1_TOP","HandMiddle2_BOT", "HandMiddle2_TOP", "HandMiddle3_BOT", "HandMiddle3_TOP",
              "HandRing0_BOT", "HandRing1_BOT", "HandRing1_TOP","HandRing2_BOT", "HandRing2_TOP", "HandRing3_BOT", "HandRing3_TOP",
              "HandPinky0_BOT", "HandPinky1_BOT", "HandPinky1_TOP","HandPinky2_BOT", "HandPinky2_TOP", "HandPinky3_BOT", "HandPinky3_TOP",
             ]

CorrParrent = ["lowerarm_correctiveRoot_l", "lowerarm_correctiveRoot_l", "lowerarm_correctiveRoot_l", "lowerarm_correctiveRoot_l",
               "hand_l", "hand_l",
               "upperarm_twistCor_01_l", "upperarm_twistCor_01_l", 
               "upperarm_correctiveRoot_l", "upperarm_correctiveRoot_l", "upperarm_correctiveRoot_l", "upperarm_correctiveRoot_l", "upperarm_correctiveRoot_l",
               "clavicle_l", "clavicle_l",
               "spine_05", "spine_05",
               "thigh_correctiveRoot_l", "thigh_correctiveRoot_l", "thigh_correctiveRoot_l", "thigh_correctiveRoot_l", "thigh_correctiveRoot_l", "thigh_correctiveRoot_l", "thigh_correctiveRoot_l", "thigh_correctiveRoot_l",
               "calf_correctiveRoot_l", "calf_correctiveRoot_l", "calf_correctiveRoot_l",
               "thumb_01_l", "thumb_01_l", "thumb_01_l", "thumb_02_l", "thumb_02_l", "thumb_03_l", "thumb_03_l",
               "index_metacarpal_l", "index_01_l", "index_01_l", "index_02_l", "index_02_l", "index_03_l", "index_03_l",
               "middle_metacarpal_l", "middle_01_l", "middle_01_l", "middle_02_l", "middle_02_l", "middle_03_l", "middle_03_l", 
               "index_metacarpal_l", "index_01_l", "index_01_l", "index_02_l", "index_02_l", "index_03_l", "index_03_l", 
               "ring_metacarpal_l", "ring_01_l", "ring_01_l", "ring_02_l", "ring_02_l", "ring_03_l", "ring_03_l", 
               "pinky_metacarpal_l", "pinky_01_l", "pinky_01_l", "pinky_02_l", "pinky_02_l", "pinky_03_l", "pinky_03_l", 
              ]

BuildCorrectives(CorrGuides, CorrParrent)



so with this i need to change up the parent names a lille bit so some of my oarents are formated like this instead of how i have them written, JOINTNAME_L_JNT instead of JOINTNAME_l if that makes sense, so what we need to do in naming the parents we need to, if the parent has the name scheme with the _L_ instead of _l cange it to _R_ if the side is right, and not change it at all if its side left, then in the acutal lists we need to replace hand_l with hand_L_JNT, lowerarm__l with arm_L_02_JNT, upperarm_l with arm_L_01_JNT, clavical_l with clavicle_L_01_JNT, spine_05 with spine_M_05_JNT, thigh_l with leg_L_01_JNT, calf_l with leg_L_02_JNT then all of the fingers so thumb, pinkey, index, middle, and ring to be reformated like this , middle_metacarpal_l:fingerMiddle_L_01_JNT, middle_01_l:fingerMiddle_L_02_JNT, middle_02_l:fingerMiddle_L_03_JNT, middle_03_l:fingerMiddle_L_04_JNT does that make sense?
'''