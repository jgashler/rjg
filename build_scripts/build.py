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




def run(character, mp, gp, ep, cp=None, sp=None, pp=None, face=True, previs=False):
    import rjg.build_scripts
    reload(rjg.build_scripts)
    
    import rjg.post.dataIO.ng_weights as rWeightNgIO
    import rjg.post.dataIO.weights as rWeightIO
    import rjg.post.dataIO.controls as rCtrlIO
    import rjg.libs.util as rUtil
    reload(rUtil)
    reload(rWeightNgIO)
    reload(rWeightIO)
    reload(rCtrlIO)
    
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
    neck = rBuild.build_module(module_type='biped_limb', side='M', part='neck', guide_list=['Neck', 'Neck1', 'Head'], ctrl_scale=10, bendy=False, twisty=False, stretchy=False, segments=1, create_ik=False)
    head = rBuild.build_module(module_type='head', side='M', part='head', guide_list=['Head'], ctrl_scale=50)

    # dungeon monster tail and jaw
    if character == "DungeonMonster":
        tail = rBuild.build_module(module_type='tail', side='M', part='tail', guide_list=['Tail_' + str(t) for t in range(1, 15)], ctrl_scale=25, pad=2)
        jaw = rBuild.build_module(module_type='hinge', side='M', part='jaw', guide_list=['JawBase', 'JawTip'], ctrl_scale=40, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')

    # previs face rig
    if not pvis_toggle:
        arbit_guides = mc.listRelatives('FaceGuides', children=True)
        for ag in arbit_guides:
            if ag in ['lipLower', 'lipLeft', 'lipRight']:
                pj = 'jaw_M_JNT'
                pc = ['jaw_M_M_CTRL', 'head_M_01_CTRL']
            else:
                pj = 'head_M_JNT'
                pc = ['head_M_01_CTRL']            
            arb = rBuild.build_module(module_type='arbitrary', side='M', part=ag, guide_list=mc.getAttr(ag + '.translate'), ctrl_scale=1, par_jnt=pj, par_ctrl=pc)
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
        
    mc.delete('Guides')

    ### DEFAULT SKIN

    bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
    geo = mc.ls(body_mesh)
    for g in geo:
        skc = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1, bindMethod=0)[0]
        mc.setAttr(skc + '.dqsSupportNonRigid', 1)


    ### SKIN/CURVE IO
    try:
        import ngSkinTools2; ngSkinTools2.workspace_control_main_window(); ngSkinTools2.open_ui()
    except Exception as e:
        print(e)


    # read skin data
    if sp:
        if not pvis_toggle:
            sp = sp[:-5]
            sp += '_pvis.json'
        sp_div = sp.split('/')
        dir = '/'.join(sp_div[:-1])
        rWeightNgIO.read_skin(body_mesh, dir, sp_div[-1][:-5])


    #### RAYDEN SPECIFICS
    if character == 'Rayden':
        import rjg.build_scripts.rayden_clothes as rc
        reload(rc)
        if pvis_toggle:
            rc.rayden_clothes(body_mesh, extras)
        else:
            rc.rayden_clothes_pvis(body_mesh, ['Shirt', 'VestFluff', 'Clothes', 'Fingernails', 'Eyeballs', 'Corneas', 'Tongue', 'LowerTeeth', 'UpperTeeth', 'RaydenHair'])
        
        rUtil.create_pxPin(0, 142.159, -12.095, 'Clothes.vtx[83073]', 'crossbow', ctrl=True, prop='crossbow_geo')
        
        mc.parent('crossbow_geo', 'crossbow')
        mc.hide('pinInput')
        mc.parent('crossbow', 'MODEL')
        
        
    #### ROBIN SPECIFICS
    elif character == 'Robin':
        import rjg.build_scripts.robin_clothes as rc
        reload(rc)
        
        if pvis_toggle:
            rc.robin_clothes(body_mesh, extras)
        else:
            rc.robin_clothes_pvis(body_mesh, ['Clothes', 'Hairtie', 'Earrings', 'Tongue', 'UpperTeeth', 'LowerTeeth', 'Eyes', 'Cornea', 'Eyebrows', 'static_hair', 'Fingernails'])
        
        mc.parent('hair_M', 'RIG')
        mc.parent('hair_root_jnt', 'head_M_JNT')
        mc.parentConstraint('head_M_01_CTRL', 'bang_01_ofst', mo=True)
        mc.parentConstraint('head_M_01_CTRL', 'bun_01_ofst', mo=True)
        
        mc.select('LowerTeeth', 'UpperTeeth', 'Tongue')
        mel.eval('hyperShade -assign Robin_Skin1;')
        
        mc.select(clear=True)
        
        rUtil.create_pxPin(0, 132.481, -11.065, 'Clothes.vtx[54013]', 'icepick', ctrl=True, prop='icepick_geo')
        
        mc.parent('icepick_geo', 'icepick')
        mc.hide('pinInput')
        mc.parent('icepick', 'MODEL')
        

    # initialize skin clusters as ngST layers
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
        
        mc.joint(n='root_root_JNT')
        mc.parent('root_root_JNT', 'SKEL')
        mc.parent('root_M_JNT', 'faceRoot_JNT', 'root_root_JNT')
        
    # set up control shapes
    if cp:
        cp_div = cp.split('/')
        dir = '/'.join(cp_div[:-1])
        rCtrlIO.read_ctrls(dir, curve_file=cp_div[-1][:-5])    
        
    # delete anim curves
    mc.select(all=True)
    ac = mc.ls(selection=True, type='animCurve')
    mc.delete(ac)

    # finalize. create all connections/constraints
    rFinal.final(utX=90, utY=0, DutZ=15, utScale=3, polish=False)
    
    # add prop to set
    if character == 'Robin':
        mc.sets('icepick', add='prop_SET')
    elif character == 'Rayden':
        mc.sets('crossbow', add='prop_SET')

    ##### IMPORT POSE INTERPOLATORS
    if pp and pvis_toggle:
        import rjg.libs.util as rUtil
        rUtil.import_poseInterpolator(pp)
        
    # clean up scene
    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    
    # create groom bust
    if not character == 'DungeonMonster':
        create_groom_bust(body_mesh)
        
    # set up textures
    import rjg.post.textures as rTex
    reload(rTex)
    for item in mc.ls('*_MT1'):
        mc.rename(item, item[:-1])
    rTex.set_textures(character)
        
    mc.BakeAllNonDefHistory()
    mc.bakePartialHistory(all=True)    
    
    
    ### TEMP ###
    mc.hide('Eyelashes')
    try:
        mc.parent('Fingernails', body_mesh[:-4] + '_EXTRAS')
    except:
        pass
    try:
        mc.delete('locator1')
    except:
        pass
    try:
        mc.parentConstraint('head_M_01_CTRL', 'lipLeft_M_M_CTRL_CNST_GRP', mo=True)
        mc.parentConstraint('head_M_01_CTRL', 'lipRight_M_M_CTRL_CNST_GRP', mo=True)
    except:
        pass
    ######
    
    mc.select(clear=True)
    print(f"\n{character} rig build complete.")



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

            

    #rCtrlIO.write_ctrls("/groups/dungeons/character/Rigging/Rigs/Rayden/Controls", force=True, name='rayden_control_curves')
    #rCtrlIO.write_ctrls("/groups/dungeons/character/Rigging/Rigs/Robin/Controls", force=True, name='robin_control_curves')

    # rc.write_clothes()
    # rWeightIO.write_skin("/groups/dungeons/character/Rigging/Rigs/Rayden/Skin/Clothes/v1", name='clothing_weights', force=True)
    # rWeightIO.read_skin("/groups/dungeons/character/Rigging/Rigs/Rayden/Skin/Clothes/v1", weights_file='clothing_weights')


