import maya.cmds as mc
import maya.mel as mel

from importlib import reload
import rjg.libs.file as rFile
import rjg.libs.control.ctrl as rCtrl
reload(rFile)
reload(rCtrl)

def project(body=None, char=None, b_model=None, b_rig=None, b_skel=None, extras=None, b_extras=None, rig_par='spine_02_FK_M_CTRL_CNST_GRP', tY=0):
    # reparent face sections to main rig
    mc.group(em=True, name='HIDE_BELLY')
    mc.parent('HIDE_BELLY', char)
    mc.parent(b_model, 'HIDE_BELLY')
    mc.parent(b_rig, 'RIG')
    mc.parent(b_skel, 'SKEL')

    # project the face rig as an always-on blendShape
    #mc.xform(f_skel, t=[0, tY, 0])
    mc.blendShape(b_model, body, name='main_blendshapes', w=[(0, 1.0)], foc=True)

    try:
        mc.select(b_extras, hi=True)
        f_ex_list = mc.ls(selection=True, type='transform')
        mc.group(em=True, name='HIDE_BELLY_EXTRAS')
        mc.parent('HIDE_BELLY_EXTRAS', 'HIDE_BELLY')
        for f in f_ex_list[:0:-1]:
            # if 'brows' in f:
            #     continue
            try:
                f = mc.rename(f, f[len(b_extras):]+'_clone')
                if mc.objExists('Fingernails_clone'):
                    mc.delete('Fingernails_clone')
                    continue
                mc.blendShape(f, f[:-6], name=f[:-6]+'Projection', w=[(0, 1.0)], foc=True)
                mc.parent(f, "HIDE_BELLY_EXTRAS")

                mc.hyperShade(f, assign='standardSurface1')
            except Exception as e:
                print(f, ':', e)
    except Exception as e:
        mc.warning(e)

    

    
    # duplcicate the face rig controls and constrain their root to rig_par
    b_rig_name = b_rig
    b_rig = mc.rename(b_rig, b_rig + '_clone')
    b_rig_clone = mc.duplicate(b_rig, renameChildren=True)
    b_rig_clone = mc.rename(b_rig_clone[0], b_rig_name)
    mc.select(b_rig, hierarchy=True)
    b_rig_sel = mc.ls(selection=True, type='transform') #+ mc.ls(selection=True, type='joint') + mc.ls(selection=True, type='follicle')
    mc.select(b_rig_clone, hierarchy=True)
    b_rig_clone_sel = mc.ls(selection=True, type='transform') #+ mc.ls(selection=True, type='joint') + mc.ls(selection=True, type='follicle')
    mc.parentConstraint(rig_par, b_rig_clone_sel[0], mo=True)

    

    # tag incoming controls
    new_controls = mc.listRelatives('belly_M', ad=True, type='nurbsCurve')
    for nc in new_controls:
        ct = mc.listRelatives(nc, parent=True)[0]
        rCtrl.tag_as_controller(ct)

    # setup direct connections between the new and original rig and rename 
    for i in range(1, len(b_rig_sel)):
        try:
            mc.connectAttr(b_rig_clone_sel[i] + ".translate", b_rig_sel[i] + ".translate")
            mc.connectAttr(b_rig_clone_sel[i] + ".rotate", b_rig_sel[i] + ".rotate")
            mc.connectAttr(b_rig_clone_sel[i] + ".scale", b_rig_sel[i] + ".scale")

            og_suff = b_rig_sel[i].split('_')[-1]
            clone_suff = b_rig_clone_sel[i].split('_')[-1]
            mc.rename(b_rig_sel[i], b_rig_sel[i].replace(og_suff, og_suff + '_clone'))
            mc.rename(b_rig_clone_sel[i], b_rig_clone_sel[i].replace(clone_suff, clone_suff[:-1]))
        except Exception as e:
            print(e)
            continue



    # try:
    #     orig = mc.select('*ShapeOrig1')
    #     orig = mc.ls(selection=True)
    #     clean_o, broken_o = [], []
    #     for o in orig:
    #         if '_' not in o:
    #             clean_o.append(o)

    #     for o1 in clean_o:
    #         if mc.objExists(o1[:-1]):
    #             broken_o.append(o1)
            
    #     for o in broken_o:
    #         conn = mc.listConnections(o, d=True)
    #         skc = conn[0]
    #         bs = conn[1]
    #         o_new = o[:-1]
    #         mc.connectAttr(o_new + '.outMesh', bs + '.originalGeometry[0]', f=True)
    #         mc.connectAttr(o_new + '.outMesh', skc + '.originalGeometry[0]', f=True)
    #         mc.connectAttr(o_new + '.worldMesh[0]', bs + '.input[0].inputGeometry', f=True)
    #         mc.delete(o)
    # except Exception as e:
    #     print(e)

    mc.select(cl=True)
            
    mc.hide("HIDE_BELLY")
    mc.hide(b_rig)

