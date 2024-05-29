
'''
Format for corrective blendshape lists
index 0: path to file containing blendshape targets. targets should be individual meshes with names unique from anything in the main file
indices 1+: tuple or list objects that contain the following
    0: (str) name of main mesh that has the blendshape applied to it
    1: (str) name of attribute that will trigger and drive the corrective
    2: (str) name of blendshape target found in the file indicated in index 0 above
    3: (tuple (double*)) values of the driving attr to use as keyframe landmarks
    4: (tuple (double*)) values of the driven blendshape target to correspond with the tuple above, make sure to use the same number of values in these tuples
    5: (str) curve type to be used for animating the sdk. options are: "auto", "clamped", "fast", "flat", "linear", "plateau", "slow", "spline", "step", and "stepnext"
'''

class CorrectiveInfo:
    def __init__(self):
        self.rayden_correctives = [
            '/groups/dungeons/character/Rigging/Rigs/Rayden/rayden_correctives.mb',
            ('Rayden_UBM', 'foot_L_01_L_CTRL.roll', 'targetBShape', (0, 30, 45), (0, 1, .5), 'spline'),
            ('Rayden_UBM', 'foot_R_01_R_CTRL.roll', 'targetCShape', (0, 30), (0, 1), 'spline'),
        ]

        self.robin_correctives = [

        ]