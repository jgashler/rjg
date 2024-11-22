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
import rjg.post.dataIO.controls as rCtrlIO
reload(rUtil)
reload(rProp)
reload(rBuild)
reload(rFinal)
reload(rFile)

import pipe.m.space_switch as spsw


def run(character, mp=None, gp=None, ep=None, cp=None, sp=None, pp=None, face=True, previs=False):
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
    
    not_previs = False if previs or character == 'DungeonMonster' else True
    bony = False if (character in ['Robin', 'Rayden', 'Jett', 'Blitz']) else True

    body_mesh = f'{character}_UBM'

    mc.file(new=True, f=True)

    ### BUILD SCRIPT
    root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
    if ep:
        extras = rFile.import_hierarchy(ep, parent='MODEL')[0]
    mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)
    
    if character == 'Skeleton':
        body_mesh = mc.listRelatives('skeleton_grp', children=True)
    elif character == 'DungeonMonster':
        body_mesh = mc.listRelatives('dungeonmonster_FINAL_GEO', children=True)

    hip = rBuild.build_module(module_type='hip', side='M', part='COG', guide_list=['Hips'], ctrl_scale=50, cog_shape='quad_arrow', waist_shape='circle')
    chest = rBuild.build_module(module_type='chest', side='M', part='chest', guide_list=['Spine2'], ctrl_scale=70, chest_shape='circle')
    spine = rBuild.build_module(module_type='spine', side='M', part='spine', guide_list=['Hips', 'Spine', 'Spine1', 'Spine2'], ctrl_scale=1, mid_ctrl=True)
    neck = rBuild.build_module(module_type='biped_limb', side='M', part='neck', guide_list=['Neck', 'Neck1', 'Head'], ctrl_scale=10, bendy=False, twisty=False, stretchy=False, segments=1, create_ik=False)
    head = rBuild.build_module(module_type='head', side='M', part='head', guide_list=['Head'], ctrl_scale=50)

    # dungeon monster tail and jaw
    if character == "DungeonMonster":
        tail = rBuild.build_module(module_type='tail', side='M', part='tail', guide_list=['Tail_' + str(t) for t in range(1, 8)], ctrl_scale=25, pad=2)
        jaw = rBuild.build_module(module_type='hinge', side='M', part='jaw', guide_list=['JawBase', 'JawTip'], ctrl_scale=40, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')

    # previs face rig
    if not not_previs and not bony and character != 'Jett' and character != 'Blitz':
        arbit_guides = mc.listRelatives('FaceGuides', children=True)
        for ag in arbit_guides:
            if ag in ['lipLower']:#, 'lipLeft', 'lipRight']:
                pj = 'jaw_M_JNT'
                pc = ['jaw_M_M_CTRL', 'head_M_01_CTRL']
            else:
                pj = 'head_M_JNT'
                pc = ['head_M_01_CTRL']            
            arb = rBuild.build_module(module_type='arbitrary', side='M', part=ag, guide_list=mc.getAttr(ag + '.translate'), ctrl_scale=1, par_jnt=pj, par_ctrl=pc)
        jaw = rBuild.build_module(module_type='hinge', side='M', part='jaw', guide_list=['JawBase', 'JawTip'], ctrl_scale=40, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')
        eyes = rBuild.build_module(module_type='look_eyes', side='M', part='lookEyes', guide_list=['eye_L', 'eye_R', 'look_L', 'look_R'], ctrl_scale=1, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')


    for fs in ['Left', 'Right']:    
        arm = rBuild.build_module(module_type='biped_limb', side=fs[0], part='arm', guide_list=[fs + piece for piece in ['Arm', 'ForeArm', 'Hand']], offset_pv=50, ctrl_scale=5, bendy=not_previs, twisty=not_previs, stretchy=not_previs, segments=4 if not_previs else 1)
        clavicle = rBuild.build_module(module_type='clavicle', side=fs[0], part='clavicle', guide_list=[fs + piece for piece in ['Shoulder', 'Arm']], local_orient=False, ctrl_scale=9) 
        hand = rBuild.build_module(module_type='hand', side=fs[0], part='hand', guide_list=[fs + 'Hand'], ctrl_scale=8)
        
        leg = rBuild.build_module(module_type='biped_limb', side=fs[0], part='leg', guide_list=[fs + piece for piece in ['UpLeg', 'Leg', 'Foot']], offset_pv=50, ctrl_scale=8, bendy=not_previs, twisty=not_previs, stretchy=not_previs, segments=4 if not_previs else 1)
        foot = rBuild.build_module(module_type='foot', side=fs[0], part='foot', guide_list=[fs + piece for piece in ['Foot', 'ToeBase', 'Toe_End']], ctrl_scale=10, toe_piv=fs+'ToePiv', heel_piv=fs+'HeelPiv', in_piv=fs+'In', out_piv=fs+'Out')
        
        fingers = []
            
        for f in ['Index', 'Middle', 'Ring', 'Pinky']:
            finger = rBuild.build_module(module_type='finger', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num) for num in range(4 if character == 'DungeonMonster' else 5)], ctrl_scale=1, fk_shape='lollipop')
            fingers.append(finger)
        thumb = rBuild.build_module(module_type='finger', side=fs[0], part='fingerThumb', guide_list=[fs + 'HandThumb' + str(num+1) for num in range(4)], ctrl_scale=1, fk_shape='lollipop')
        fingers.append(thumb)    
        
    mc.delete('Guides')
    
    if bony and pp:
        import rjg.build_scripts.dm_bone_dict as dm_bd
        import rjg.build_scripts.sk_bone_dict as sk_bd
        reload(dm_bd)
        reload(sk_bd)
        
        if character == 'DungeonMonster':
            bone_dict = dm_bd.BoneDict().bone_dict
        elif character == 'Skeleton':
            bone_dict = sk_bd.BoneDict().bone_dict
        
        bone_locs = rFile.import_hierarchy(pp)   
        bone_locs = mc.listRelatives('bone_locs', children=True)
        
        bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
        for j in bind_joints:
            mc.deleteAttr(j + '.bindJoint')
            
        float_bone_grp = mc.group(empty=True, name='floatBones_F')
        mc.parent(float_bone_grp, 'RIG')
        for b in bone_locs:
            bone_name = b[:-4]
            if bone_name in bone_dict:
                par_jnt = bone_dict[bone_name][0]
                par_ctrl = bone_dict[bone_name][1]
                if len(bone_dict[bone_name]) > 2:
                    print("TODO: handle extra cases")
            else:
                #print(f'    Bone {bone_name} not found in bone dictionary')
                par_jnt = 'root_M_JNT'
                par_ctrl = 'root_02_M_CTRL'
            floatBone = rBuild.build_module(module_type='float_bone', side='F', part=b[:-4], guide_list=[b], ctrl_scale=2, par_jnt=par_jnt, par_ctrl=par_ctrl)
            mc.parent(floatBone.part_grp, float_bone_grp)
            #mc.connectJoint(floatBone.floatBone_jnt, par_jnt, pm=True)
            mc.connectJoint(floatBone.bind_joints[0], par_jnt, pm=True)
            mc.parentConstraint(par_jnt, floatBone.floatBone_ctrl.top, mo=True)


            
        mc.delete('bone_locs')


    ### DEFAULT SKIN
    if not bony:
        bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
        geo = mc.ls(body_mesh)
        for g in geo:
            skc = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1, bindMethod=0)[0]
            mc.setAttr(skc + '.dqsSupportNonRigid', 1)
    else:
        geo = mc.ls(body_mesh)
        bone_skcs = []
        for g in geo:
            mc.select(g, g + '_F_JNT')
            skc = mc.skinCluster(g + '_F_JNT', g, tsb=True)
            bone_skcs.append(skc)
        try:
            merged = mc.polyUniteSkinned(geo, ch=1, mergeUVSets=1)
            mc.rename(merged[0], 'skeleton_geo')
            mc.rename(merged[1], 'skeleton_skc')
            mc.parent('skeleton_geo', 'MODEL')
        except Exception as e:
            mc.warning(e)


    ### SKIN/CURVE IO
    try:
        import ngSkinTools2; ngSkinTools2.workspace_control_main_window(); ngSkinTools2.open_ui()
    except Exception as e:
        print(e)


    # read skin data
    if sp:
        if not not_previs and character != 'Jett' and character != 'Blitz':
            sp = sp[:-5]
            sp += '_pvis.json'
        sp_div = sp.split('/')
        dir = '/'.join(sp_div[:-1])
        rWeightNgIO.read_skin(body_mesh, dir, sp_div[-1][:-5])


    #### RAYDEN SPECIFICS
    if character == 'Rayden':
        import rjg.build_scripts.rayden_clothes as rc
        reload(rc)
        if not_previs:
            rc.rayden_clothes(body_mesh, extras)
        else:
            try:
                rc.rayden_clothes_pvis(body_mesh, ['Shirt', 'VestFluff', 'Clothes', 'Fingernails', 'Eyeballs', 'Corneas', 'Tongue', 'LowerTeeth', 'UpperTeeth', 'RaydenHair'])
            except:
                rc.rayden_clothes_pvis(body_mesh, ['Clothes'])    
        try:
            rUtil.create_pxPin(0, 142.159, -12.095, 'Clothes.vtx[83073]', 'S_Crossbow:crossbow', ctrl=True, prop='S_Crossbow:crossbow_geo')
    
            mc.parent('S_Crossbow:crossbow_geo', 'S_Crossbow:crossbow')
            mc.hide('pinInput')
            mc.parent('S_Crossbow:ROOT', world=True)
            mc.select('chest_M_02_CTRL', 'arm_R_03_fk_CTRL', 'arm_L_03_fk_CTRL', 'crossbow_M_CTRL')
            spsw.run()
            mc.addAttr('crossbow_M_CTRL.spaceSwitch', e=True, enumName='world:back:right hand:left hand:')
            mc.setAttr('crossbow_M_CTRL.spaceSwitch', 1)
            mc.parent('crossbow_M_CTRL_space_switch_GRP', 'RIG')
            mc.parent('S_Crossbow:crossbow', 'S_Crossbow:MODEL')
            
        except:
            pass
        
        
    #### ROBIN SPECIFICS
    elif character == 'Robin':
        import rjg.build_scripts.robin_clothes as rc
        reload(rc)
        
        if not_previs:
            rc.robin_clothes(body_mesh, extras)
        else:
            rc.robin_clothes_pvis(body_mesh, ['Clothes', 'Hairtie', 'Earrings', 'Tongue', 'UpperTeeth', 'LowerTeeth', 'Eyes', 'Cornea', 'Eyebrows', 'static_hair', 'Fingernails'])
        
        mc.parent('hair_M', 'RIG')
        mc.parent('hair_root_jnt', 'head_M_JNT')
        mc.parentConstraint('head_M_01_CTRL', 'CoG_hair_root_ctrl_OFST', mo=True)
        #mc.parentConstraint('head_M_01_CTRL', 'bun_01_ofst', mo=True)
        
        mc.select('LowerTeeth', 'UpperTeeth', 'Tongue')
        mel.eval('hyperShade -assign Robin_Skin1;')
        
        mc.select(clear=True)
        
        rUtil.create_pxPin(0, 132.481, -11.065, 'Clothes.vtx[54013]', 'icepick', ctrl=True, prop='icepick_geo')
        
        mc.parent('icepick_geo', 'icepick')
        mc.hide('pinInput')
        mc.parent('icepick', 'MODEL')
        mc.select('chest_M_02_CTRL', 'arm_R_03_fk_CTRL', 'arm_L_03_fk_CTRL', 'icepick_M_CTRL')
        spsw.run()
        mc.addAttr('icepick_M_CTRL.spaceSwitch', e=True, enumName='world:back:right hand:left hand:')
        mc.setAttr('icepick_M_CTRL.spaceSwitch', 1)
        mc.parent('icepick_M_CTRL_space_switch_GRP', 'RIG')
        

    # initialize skin clusters as ngST layers
    if not bony:
        for s in mc.ls(type='skinCluster'):
            try:
                rWeightNgIO.init_skc(s)
            except Exception as e:
                print(e)
                
    if not_previs and not bony:
        try:
            mc.blendShape(n='breath_blendshapes', foc=True, ip=groups + f'/dungeons/character/Rigging/Rigs/{character}/Skin/breath_shapes.shp')
            mc.select('chest_M_01_CTRL')
            mc.addAttr(at='float', longName='chestBreath', min=0, max=1, k=True)
            mc.addAttr(at='float', longName='bellyBreath', min=0, max=1, k=True)

            mc.connectAttr('chest_M_01_CTRL.chestBreath', 'breath_blendshapes.chest_breath')
            mc.connectAttr('chest_M_01_CTRL.bellyBreath', 'breath_blendshapes.belly_breath')
        except Exception as e:
            print('no breath blendshapes connected:', e)


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
        
        mc.select('head_M_01_CTRL', 'Look_Control')
        spsw.run()
        mc.addAttr('Look_Control.spaceSwitch', e=True, enumName='world:head:')
        mc.setAttr('Look_Control.spaceSwitch', 1)
        mc.parent('Look_Control_space_switch_GRP', 'RIG')
        
        

        

        
    # delete anim curves
    mc.select(all=True)
    ac = mc.ls(selection=True, type='animCurve')
    mc.delete(ac)

    # finalize. create all connections/constraints
    if not bony:
        rFinal.final(utX=90, utY=0, DutZ=15, utScale=3, polish=False, character=character)
    else:
        rFinal.final(utX=90, utY=0, DutZ=15, utScale=3, polish=False)
    
    # set up control shapes
    if cp:
        cp_div = cp.split('/')
        dir = '/'.join(cp_div[:-1])
        rCtrlIO.read_ctrls(dir, curve_file=cp_div[-1][:-5])    
    
    # add prop to set
    if character == 'Robin':
        mc.sets('icepick', add='prop_SET')
    elif character == 'Rayden':
        mc.parent('S_Crossbow:crossbow', 'S_Crossbow:MODEL')
        mc.sets('S_Crossbow:MODEL', add='prop_SET')

    ##### IMPORT POSE INTERPOLATORS
    if pp and not_previs and not bony:
        import rjg.libs.util as rUtil
        rUtil.import_poseInterpolator(pp)
        
    if character == 'Rayden':
        mc.connectAttr('cbow_rev.outputX', 'S_Crossbow:crossbow.visibility')
        
    # clean up scene
    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    
    # create groom bust
    if not bony:
        create_groom_bust(body_mesh)
        
    # set up textures
    import rjg.post.textures as rTex
    reload(rTex)
    for item in mc.ls('*_MT1'):
        mc.rename(item, item[:-1])
    rTex.set_textures(character)
    
    if not not_previs and not bony:
        try:
            mc.blendShape(character + '_UBM', name = 'pvis_shapes', foc=True)
            mc.blendShape('pvis_shapes', e=True, ip=f'/groups/dungeons/character/Rigging/Rigs/{character}/Skin/pvis_shapes.shp')
            mc.connectAttr('look_L_CTRL.blink', 'pvis_shapes.blink_LShape')
            mc.connectAttr('look_R_CTRL.blink', 'pvis_shapes.blink_RShape')
        except:
            pass
        

            
    if not not_previs and not bony:
        try:
            for o in ['lipLeft_M_M_CTRL_SDK_GRP.', 'lipRight_M_M_CTRL_SDK_GRP.']:
                for a in ['translateY', 'rotateX']:
                    mc.setDrivenKeyframe(o, at=a, cd='jaw_M_M_CTRL.rotateX')
            mc.setAttr('jaw_M_M_CTRL.rotateX', 38)
            mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.translateY', -1.773)
            mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.rotateX', 21.592)
            mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.translateZ', -.56)
            mc.setAttr('lipRight_M_M_CTRL_SDK_GRP.translateY', -1.773)
            mc.setAttr('lipRight_M_M_CTRL_SDK_GRP.rotateX', 21.592)
            mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.translateZ', -.56)
            for o in ['lipLeft_M_M_CTRL_SDK_GRP.', 'lipRight_M_M_CTRL_SDK_GRP.']:
                for a in ['translateY', 'rotateX']:
                    mc.setDrivenKeyframe(o, at=a, cd='jaw_M_M_CTRL.rotateX')
            mc.setAttr('jaw_M_M_CTRL.rotateX', 0)
        except:
            pass
        
    try:
        mc.BakeAllNonDefHistory()
        mc.bakePartialHistory(all=True)    
    except Exception as e:
        mc.warning("Delete history error:", e)
    
    ### TEMP ###
    # try:
    #     if character == 'Rayden':
    #         mc.hide('Eyelashes')
    # except:
    #     pass
    try:
        mc.parent('Fingernails', body_mesh[:-4] + '_EXTRAS')
    except:
        pass
    try:
        mc.delete('locator1')
    except:
        pass
    try:
        lpc = mc.parentConstraint('head_M_01_CTRL', 'lipLeft_M_M_CTRL_CNST_GRP', mo=True)
        rpc = mc.parentConstraint('head_M_01_CTRL', 'lipRight_M_M_CTRL_CNST_GRP', mo=True)
        mc.setAttr(lpc[0] + '.interpType', 0)
        mc.setAttr(rpc[0] + '.interpType', 0)
    except Exception as e:
        print(e)
    try:
        mc.disconnectAttr('Robin_H_file.outColor', 'Robin_Hair.baseColor')
        mc.disconnectAttr('Robin_S_file.outColor', 'Robin_Silk.baseColor')
        mc.setAttr('Robin_Silk.baseColor', 0.124521, 0.0142565, 0.00418706, type='double3')
    except Exception as e:
        print(e)
        
    if character == 'DungeonMonster':
        mc.setAttr('switch_CTRL.armL_IKFK', 0)
        mc.setAttr('switch_CTRL.armR_IKFK', 0)
    try:
        orig = mc.select('*ShapeOrig1')
        orig = mc.ls(selection=True)
        clean_o, broken_o = [], []
        for o in orig:
            if '_' not in o:
                clean_o.append(o)

        for o1 in clean_o:
            if mc.objExists(o1[:-1]):
                broken_o.append(o1)
            
        for o in broken_o:
            conn = mc.listConnections(o, d=True)
            skc = conn[0]
            bs = conn[1]
            o_new = o[:-1]
            mc.connectAttr(o_new + '.outMesh', bs + '.originalGeometry[0]', f=True)
            mc.connectAttr(o_new + '.outMesh', skc + '.originalGeometry[0]', f=True)
            mc.connectAttr(o_new + '.worldMesh[0]', bs + '.input[0].inputGeometry', f=True)
            mc.delete(o)
    except Exception as e:
        print('shapeOrig1 error:',e)
        if character == 'Robin' and face:
            run(character, mp=mp, gp=gp, ep=ep, cp=cp, sp=sp, pp=pp, face=face, previs=previs)
            print("attempt etc.")
            return
    

    ############
        
    if not not_previs and not bony:
        try:
            try:
                mc.select('Eyes', 'Cornea', 'LowerTeeth', 'UpperTeeth', 'Tongue')
                mel.eval('doDetachSkin 3 { "1", "1", "1" };')
                mc.skinCluster('eyeBind_L_JNT', 'eyeBind_R_JNT', 'Cornea', mi=1, tsb=True)
                mc.skinCluster('eyeBind_L_JNT', 'eyeBind_R_JNT', 'Eyes', mi=1, tsb=True)
                mc.skinCluster('jaw_M_JNT', 'LowerTeeth', mi=1, tsb=True)
                mc.skinCluster('jaw_M_JNT', 'Tongue', mi=1, tsb=True)
                mc.skinCluster('head_M_JNT', 'UpperTeeth', mi=1, tsb=True)
            except Exception as e:
                mc.select('Eyeballs', 'Corneas', 'LowerTeeth', 'UpperTeeth', 'Tongue')
                mel.eval('doDetachSkin 3 { "1", "1", "1" };')
                mc.skinCluster('eyeBind_L_JNT', 'eyeBind_R_JNT', 'Corneas', mi=1, tsb=True)
                mc.skinCluster('eyeBind_L_JNT', 'eyeBind_R_JNT', 'Eyeballs', mi=1, tsb=True)
                mc.skinCluster('jaw_M_JNT', 'LowerTeeth', mi=1, tsb=True)
                mc.skinCluster('jaw_M_JNT', 'Tongue', mi=1, tsb=True)
                mc.skinCluster('head_M_JNT', 'UpperTeeth', mi=1, tsb=True)
            try:
                rUtil.pvis_blink('eyelid_L_JNT', 'look_L_CTRL', 40)
                rUtil.pvis_blink('eyelid_R_JNT', 'look_R_CTRL', 40)
            except Exception as e:
                print(e)
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
#rCtrlIO.write_ctrls("/groups/dungeons/character/Rigging/Rigs/DungeonMonster/Controls", force=True, name='dm_control_curves')


'''   
for o in ['lipLeft_M_M_CTRL_SDK_GRP.', 'lipRight_M_M_CTRL_SDK_GRP.']:
    for a in ['translateY', 'rotateX']:
        mc.setDrivenKeyframe(o, at=a, cd='jaw_M_M_CTRL.rotateX')
mc.setAttr('jaw_M_M_CTRL.rotateX', 38)
mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.translateY', -1.773)
mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.rotateX', 21.592)
mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.translateZ', -.56)
mc.setAttr('lipRight_M_M_CTRL_SDK_GRP.translateY', -1.773)
mc.setAttr('lipRight_M_M_CTRL_SDK_GRP.rotateX', 21.592)
mc.setAttr('lipLeft_M_M_CTRL_SDK_GRP.translateZ', -.56)
for o in ['lipLeft_M_M_CTRL_SDK_GRP.', 'lipRight_M_M_CTRL_SDK_GRP.']:
    for a in ['translateY', 'rotateX']:
        mc.setDrivenKeyframe(o, at=a, cd='jaw_M_M_CTRL.rotateX')
mc.setAttr('jaw_M_M_CTRL.rotateX', 0)
'''