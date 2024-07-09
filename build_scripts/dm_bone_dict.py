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
            'polySurface1' : ['leg_L_01_JNT', 'leg_L_IK_BASE_CTRL'],
            'polySurface2' : ['leg_L_05_JNT', 'leg_L_05_JNT'],
        }