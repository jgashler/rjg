import maya.cmds as mc
import maya.mel as mel
import sys, platform
from importlib import reload

groups = 'G:' if platform.system() == 'Windows' else '/groups'
mc.scriptEditorInfo(suppressWarnings=True,suppressInfo=True)

import rjg.build.buildPart as rBuild
import rjg.post.finalize as rFinal
import rjg.build.prop as rProp
import rjg.libs.file as rFile
import rjg.libs.util as rUtil
reload(rUtil)
reload(rProp)
reload(rBuild)
reload(rFinal)
reload(rFile)

#run(previs=True)


def run(character, mp, gp, ep, cp=None, sp=None, pp=None, face=True, previs=False):
    import rjg.build_scripts
    reload(rjg.build_scripts)
    
    pvis_toggle = False if previs else True

    body_mesh = f'{character}_UBM'

    mc.file(new=True, f=True)

    ### BUILD SCRIPT
    root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
    extras = rFile.import_hierarchy(ep, parent='MODEL')[0]
    mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)

    hip = rBuild.build_module(module_type='hip', side='M', part='COG', guide_list=['Hips'], ctrl_scale=50, cog_shape='quad_arrow', waist_shape='circle')
    chest = rBuild.build_module(module_type='chest', side='M', part='chest', guide_list=['Spine2'], ctrl_scale=70, chest_shape='circle')
    spine = rBuild.build_module(module_type='spine', side='M', part='spine', guide_list=['Hips', 'Spine', 'Spine1', 'Spine2'], ctrl_scale=1, mid_ctrl=True)
    #neck = rBuild.build_module(module_type='spine', side='M', part='neck', guide_list=['Neck', 'Neck1', 'Head'], ctrl_scale=1, mid_ctrl=False, joint_num=3)
    neck = rBuild.build_module(module_type='biped_limb', side='M', part='neck', guide_list=['Neck', 'Neck1', 'Head'], ctrl_scale=10, bendy=False, twisty=False, stretchy=False, segments=1, create_ik=False)
    head = rBuild.build_module(module_type='head', side='M', part='head', guide_list=['Head'], ctrl_scale=50)

    if character == "DungeonMonster":
        tail = rBuild.build_module(module_type='tail', side='M', part='tail', guide_list=['Tail_' + str(t) for t in range(1, 15)], ctrl_scale=25, pad=2)
        jaw = rBuild.build_module(module_type='hinge', side='M', part='jaw', guide_list=['JawBase', 'JawTip'], ctrl_scale=40, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')


    for fs in ['Left', 'Right']:    
        arm = rBuild.build_module(module_type='biped_limb', side=fs[0], part='arm', guide_list=[fs + piece for piece in ['Arm', 'ForeArm', 'Hand']], offset_pv=50, ctrl_scale=5, bendy=pvis_toggle, twisty=pvis_toggle, stretchy=pvis_toggle, segments=4 if pvis_toggle else 1)
        clavicle = rBuild.build_module(module_type='clavicle', side=fs[0], part='clavicle', guide_list=[fs + piece for piece in ['Shoulder', 'Arm']], local_orient=False, ctrl_scale=9) 
        hand = rBuild.build_module(module_type='hand', side=fs[0], part='hand', guide_list=[fs + 'Hand'], ctrl_scale=8)
        
        leg = rBuild.build_module(module_type='biped_limb', side=fs[0], part='leg', guide_list=[fs + piece for piece in ['UpLeg', 'Leg', 'Foot']], offset_pv=50, ctrl_scale=8, bendy=pvis_toggle, twisty=pvis_toggle, stretchy=pvis_toggle, segments=4 if pvis_toggle else 1)
        foot = rBuild.build_module(module_type='foot', side=fs[0], part='foot', guide_list=[fs + piece for piece in ['Foot', 'ToeBase', 'Toe_End']], ctrl_scale=10, toe_piv=fs+'ToePiv', heel_piv=fs+'HeelPiv', in_piv=fs+'In', out_piv=fs+'Out')
        
        fingers = []
            
        for f in ['Index', 'Middle', 'Ring', 'Pinky']:
            finger = rBuild.build_module(module_type='finger', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num) for num in range(5)], ctrl_scale=1, fk_shape='lollipop')
            fingers.append(finger)
        thumb = rBuild.build_module(module_type='finger', side=fs[0], part='fingerThumb', guide_list=[fs + 'HandThumb' + str(num+1) for num in range(4)], ctrl_scale=1, fk_shape='lollipop')
        fingers.append(thumb)    
        
    mc.delete('Hips')

    ### DEFAULT SKIN

    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(body_mesh)
    for g in geo:
        skc = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1, bindMethod=0)[0]
        mc.setAttr(skc + '.dqsSupportNonRigid', 1)


    ### SKIN/CURVE IO
    
    #if 'ngSkinTools2' not in sys.modules:
    try:
        import ngSkinTools2; ngSkinTools2.workspace_control_main_window(); ngSkinTools2.open_ui()
    except Exception as e:
        print(e)

    import rjg.post.dataIO.ng_weights as rWeightNgIO
    import rjg.post.dataIO.weights as rWeightIO
    import rjg.post.dataIO.controls as rCtrlIO
    import rjg.libs.util as rUtil
    reload(rUtil)
    reload(rWeightNgIO)
    reload(rWeightIO)
    reload(rCtrlIO)

    print("Reading skin weight files...")

    if cp:
        cp_div = cp.split('/')
        dir = '/'.join(cp_div[:-1])
        rCtrlIO.read_ctrls(dir, curve_file=cp_div[-1][:-5])

    if sp:
        sp_div = sp.split('/')
        dir = '/'.join(sp_div[:-1])
        rWeightNgIO.read_skin(body_mesh, dir, sp_div[-1][:-5])

    #mc.copySkinWeights(ss='skinCluster1', ds='skinCluster1', mm='YZ', sa='closestPoint', ia='closestJoint') # necessary??

    if character == 'Rayden':
        import rjg.build_scripts.rayden_clothes as rc
        reload(rc)
        if pvis_toggle:
            rc.rayden_clothes(body_mesh, extras)
        else:
            rc.rayden_clothes_pvis(body_mesh, ['Shirt', 'VestFluff', 'Clothes', 'Fingernails'])
    elif character == 'Robin':
        import rjg.build_scripts.robin_clothes as rc
        reload(rc)
        rc.robin_clothes(body_mesh, extras)
        
        if pvis_toggle:
            mc.parent('hair_M', 'RIG')
            mc.parent('hair_root_jnt', 'head_M_JNT')
            #mc.parent('hair_export_root_jn', 'SKEL')
            mc.parentConstraint('head_M_01_CTRL', 'bang_01_ofst', mo=True)
            mc.parentConstraint('head_M_01_CTRL', 'bun_01_ofst', mo=True)
            
            rUtil.create_pxWrap('bun_guides', 'bun_clump')#_export')
            rUtil.create_pxWrap('left_bang_guides', 'left_bang_clump')#_export')
        else:
            mc.delete('HairCurves')
            mc.delete('hair_root_jnt')
        
        mc.select('LowerTeeth', 'UpperTeeth', 'Tongue')
        mel.eval('hyperShade -assign Robin_Skin1;')
        
        mc.select(clear=True)
        
        rUtil.create_pxPin(0, 132.481, -11.065, 'Clothes.vtx[54013]', 'pick_pin')
        
        mc.group('pick_pin', n='PROP')
        mc.parent('PROP', 'ROOT')
        #mc.parent('pick_pin', 'Robin_EXTRAS')
        mc.parent('pick', 'pick_pin')
        mc.hide('pinInput')
        
        
        
        


    for s in mc.ls(type='skinCluster'):
        try:
            rWeightNgIO.init_skc(s)
        except Exception as e:
            print(e)

    ##### PROJECT FACE
    if face:
        reload(rFile)
        face = rFile.import_hierarchy(groups + f'/dungeons/anim/Rigs/{character}Face.mb')
        import rjg.post.faceProject as rFaceProj
        reload(rFaceProj)
        rFaceProj.project(body=body_mesh, char='ROOT', f_model='FaceAtOrigin', f_rig='face_M', extras=f'{character}_Extras', f_extras='F_EXTRAS', f_skel='faceRoot_JNT')#, tY=1.103)
        mc.delete(face)
        
        
    rFinal.final(utX=90, utY=0, DutZ=15, utScale=3, polish=False)

    ##### IMPORT POSE INTERPOLATORS
    if pp:
        import rjg.libs.util as rUtil
        rUtil.import_poseInterpolator(pp)
        
    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    
    for item in mc.ls('*_MT1'):
        mc.rename(item, item[:-1])
        
    if not character == 'DungeonMonster':
        create_groom_bust(body_mesh)
        
    import rjg.post.textures as rTex
    reload(rTex)
    rTex.set_textures(character)
        
    mc.BakeAllNonDefHistory()
    mc.bakePartialHistory(all=True)    
    
    mc.select(clear=True)
    print(f"\n{character} rig build complete.")
    
    ### TEMP ###
    mc.hide('Eyelashes')
    #mc.setAttr('skinCluster2.envelope', 0)
    # for dim in 'XYZ':
    #     mc.disconnectAttr('neck_M_tip_JNT_parentConstraint1.constraintRotate' + dim, 'neck_M_tip_JNT.rotate' + dim)
    ###########
    

    #rCtrlIO.write_ctrls("/groups/dungeons/character/Rigging/Rigs/Rayden/Controls", force=True, name='rayden_control_curves')

    # rc.write_clothes()
    # rWeightIO.write_skin("/groups/dungeons/character/Rigging/Rigs/Rayden/Skin/Clothes/v1", name='clothing_weights', force=True)
    # rWeightIO.read_skin("/groups/dungeons/character/Rigging/Rigs/Rayden/Skin/Clothes/v1", weights_file='clothing_weights')




def create_groom_bust(model):
    mc.select(f'{model}.f[0:2041]',
              f'{model}.f[5887:5903]',
              f'{model}.f[5920]', 
              f'{model}.f[5981:5982]', 
              f'{model}.f[6042]', 
              f'{model}.f[6099]', 
              f'{model}.f[6762]', 
              f'{model}.f[7086:9274]', 
              f'{model}.f[13120:13136]', 
              f'{model}.f[13153]', 
              f'{model}.f[13214:13215]', 
              f'{model}.f[13275]', 
              f'{model}.f[13332]', 
              f'{model}.f[13995]', 
              f'{model}.f[14319:14649]', 
              f'{model}.f[14722:14953]')
              
    mc.componentTag(create=True, ntn='GroomBust')
    # mc.polyColorPerVertex(r=1, g=1, b=1, a=1)
    # mc.polyColorSet(rename=True, colorSet='colorSet1', newColorSet='GroomBust')
              









