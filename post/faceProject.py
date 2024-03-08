'''

Assuming:
    Incoming face model is hierarchically structured as FACE(F_MODEL, F_RIG, F_SKEL)
    MODEL contains full body mesh
    RIG contains face_M, which contains offset groups for all face controls

Import the face rig. (in build script)
Move full body mesh into CHAR(MODEL) group and hide
Move face_M into CHAR(RIG) group
    parentConstrain face_M to "Head_M_01_CTRL_CNST_GRP"
Create blendShape deformer group on CHAR(MODEL(bodyRigGeo))
Add blendShape target from CHAR(MODEL(faceRigGeo))


'''

import maya.cmds as mc
from importlib import reload
import rjg.libs.file as rFile
reload(rFile)

def project(body=None, f_model=None, f_rig=None, rig_par='head_M_02_CTRL_CNST_GRP'):
    mc.parent(f_model, 'MODEL')
    mc.parent(f_rig, 'RIG')

    mc.hide(f_model)

    mc.blendShape(f_model, body, name='FaceProjection', w=[(0, 1.0)], foc=True)
    mc.parentConstraint(rig_par, f_rig, mo=True)

    #TODO: figure out how to get bones into the scene

