import maya.cmds as mc
from importlib import reload
import rjg.libs.file as rFile
reload(rFile)

def project(body=None, char=None, f_model=None, f_rig=None, f_skel=None, extras=None, f_extras=None, rig_par='head_M_02_CTRL_CNST_GRP', tY=0):
    # reparent face sections to main rig
    mc.group(em=True, name='HIDE_FACE')
    mc.parent('HIDE_FACE', char)
    mc.parent(f_model, 'HIDE_FACE')
    mc.parent(f_rig, 'RIG')
    mc.parent(f_skel, 'SKEL')

    # project the face rig as an always-on blendShape
    #mc.xform(f_skel, t=[0, tY, 0])
    mc.blendShape(f_model, body, name='main_blendshapes', w=[(0, 1.0)], foc=True)

    mc.select(f_extras, hi=True)
    f_ex_list = mc.ls(selection=True, type='transform')
    mc.group(em=True, name='HIDE_FACE_EXTRAS')
    mc.parent('HIDE_FACE_EXTRAS', 'HIDE_FACE')
    for f in f_ex_list[:0:-1]:
        # if 'brows' in f:
        #     continue
        try:
            f = mc.rename(f, f[len(f_extras):]+'_clone')
            mc.blendShape(f, f[:-6], name=f[:-6]+'Projection', w=[(0, 1.0)], foc=True)
            mc.parent(f, "HIDE_FACE_EXTRAS")
        except Exception as e:
            print(f, ':', e)

    
    # duplcicate the face rig controls and constrain their root to rig_par
    f_rig_name = f_rig
    f_rig = mc.rename(f_rig, f_rig + '_clone')
    f_rig_clone = mc.duplicate(f_rig, renameChildren=True)
    f_rig_clone = mc.rename(f_rig_clone[0], f_rig_name)
    mc.select(f_rig, hierarchy=True)
    f_rig_sel = mc.ls(selection=True, type='transform') #+ mc.ls(selection=True, type='joint') + mc.ls(selection=True, type='follicle')
    mc.select(f_rig_clone, hierarchy=True)
    f_rig_clone_sel = mc.ls(selection=True, type='transform') #+ mc.ls(selection=True, type='joint') + mc.ls(selection=True, type='follicle')
    mc.parentConstraint(rig_par, f_rig_clone_sel[0], mo=True)

    # setup direct connections between the new and original rig and rename 
    for i in range(1, len(f_rig_sel)):
        try:
            mc.connectAttr(f_rig_clone_sel[i] + ".translate", f_rig_sel[i] + ".translate")
            mc.connectAttr(f_rig_clone_sel[i] + ".rotate", f_rig_sel[i] + ".rotate")
            mc.connectAttr(f_rig_clone_sel[i] + ".scale", f_rig_sel[i] + ".scale")

            og_suff = f_rig_sel[i].split('_')[-1]
            clone_suff = f_rig_clone_sel[i].split('_')[-1]
            mc.rename(f_rig_sel[i], f_rig_sel[i].replace(og_suff, og_suff + '_clone'))
            mc.rename(f_rig_clone_sel[i], f_rig_clone_sel[i].replace(clone_suff, clone_suff[:-1]))
        except Exception as e:
            print(e)
            continue

    try:
        mc.select('*_driver')
        drivers = mc.ls(selection=True)

        for d in drivers:
            try:
                mc.connectAttr(d + '.rotate', d + '1.rotate')
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        print(e)
        
    try:
        mc.select('*Mouth_offset_clone')
        drivers = mc.ls(selection=True)

        for d in drivers:
            try:
                mc.disconnectAttr(d[:-6] + '.translate', d + '.translate')
                mc.disconnectAttr(d[:-6] + '.rotate', d + '.rotate')
                mc.disconnectAttr(d[:-6] + '.scale', d + '.scale') 
                mc.connectAttr(d + '.translateX', d[:-6] + '.translateX')
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        print(e)

    try:
        for s in ['R', 'L']:
            for attr in ['Blink', 'Blink_Height', 'Blink_Influence', 'Eyelid_Follow']:
                mc.connectAttr(f'{s}_eyeCTRL.{attr}', f'{s}_eyeCTRL_clone.{attr}')
    except:
        pass


            
    mc.hide("HIDE_FACE")
    mc.hide(f_rig)
