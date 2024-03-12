import maya.cmds as mc
from importlib import reload
import rjg.libs.file as rFile
reload(rFile)

def project(body=None, f_model=None, f_rig=None, f_skel=None, rig_par='head_M_02_CTRL_CNST_GRP'):
    # reparent face sections to main rig
    mc.parent(f_model, 'MODEL')
    mc.parent(f_rig, 'RIG')
    mc.parent(f_skel, 'SKEL')

    # project the face rig as an always-on blendShape
    mc.blendShape(f_model, body, name='FaceProjection', w=[(0, 1.0)], foc=True)

    # duplcicate the face rig controls and constrain their root to rig_par
    f_rig_clone = mc.duplicate(f_rig, renameChildren=True)
    mc.select(f_rig, hierarchy=True)
    f_rig_sel = mc.ls(selection=True, type='transform')
    mc.select(f_rig_clone, hierarchy=True)
    f_rig_clone_sel = mc.ls(selection=True, type='transform')
    mc.parentConstraint(rig_par, f_rig_clone_sel[0], mo=True)

    # setup direct connections between the new and original rig and rename 
    for i in range(1, len(f_rig_sel)):
        mc.connectAttr(f_rig_clone_sel[i] + ".translate", f_rig_sel[i] + ".translate")
        mc.connectAttr(f_rig_clone_sel[i] + ".rotate", f_rig_sel[i] + ".rotate")
        mc.connectAttr(f_rig_clone_sel[i] + ".scale", f_rig_sel[i] + ".scale")

        og_suff = f_rig_sel[i].split('_')[-1]
        clone_suff = f_rig_clone_sel[i].split('_')[-1]
        mc.rename(f_rig_sel[i], f_rig_sel[i].replace(og_suff, og_suff + '_clone'))
        mc.rename(f_rig_clone_sel[i], f_rig_clone_sel[i].replace(clone_suff, clone_suff[:-1]))

    mc.hide(f_model)
    mc.hide(f_rig)
