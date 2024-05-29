import maya.cmds as mc
import platform
from importlib import reload

groups = 'G:' if platform.system() == 'Windows' else '/groups'
mc.scriptEditorInfo(suppressWarnings=True,suppressInfo=True)

import rjg.build.buildPart as rBuild
import rjg.post.finalize as rFinal
import rjg.build.prop as rProp
import rjg.libs.file as rFile
reload(rProp)
reload(rBuild)
reload(rFinal)
reload(rFile)

mp = groups + '/dungeons/character/Rigging/Rigs/Robin/robin_model.mb'
gp = groups + '/dungeons/character/Rigging/Rigs/Robin/robin_guides.mb'
ep = groups + '/dungeons/character/Rigging/Rigs/Robin/robin_extras.mb'

body_mesh = 'Robin_UBM'

mc.file(new=True, f=True)

### BUILD SCRIPT
root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
extras = rFile.import_hierarchy(ep, parent='MODEL')[0]
mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)

hip = rBuild.build_module(module_type='hip', side='M', part='COG', guide_list=['Hips'], ctrl_scale=50, cog_shape='quad_arrow', waist_shape='circle')
chest = rBuild.build_module(module_type='chest', side='M', part='chest', guide_list=['Spine2'], ctrl_scale=70, chest_shape='circle')
spine = rBuild.build_module(module_type='spine', side='M', part='spine', guide_list=['Hips', 'Spine', 'Spine1', 'Spine2'], ctrl_scale=1, mid_ctrl=True)
neck = rBuild.build_module(module_type='spine', side='M', part='neck', guide_list=['Neck', 'Neck1', 'Head'], ctrl_scale=1, mid_ctrl=False, joint_num=3)
head = rBuild.build_module(module_type='head', side='M', part='head', guide_list=['Head'], ctrl_scale=50)


for fs in ['Left', 'Right']:    
    arm = rBuild.build_module(module_type='biped_limb', side=fs[0], part='arm', guide_list=[fs + piece for piece in ['Arm', 'ForeArm', 'Hand']], offset_pv=50, ctrl_scale=5)
    clavicle = rBuild.build_module(module_type='clavicle', side=fs[0], part='clavicle', guide_list=[fs + piece for piece in ['Shoulder', 'Arm']], local_orient=False, ctrl_scale=9) 
    hand = rBuild.build_module(module_type='hand', side=fs[0], part='hand', guide_list=[fs + 'Hand'], ctrl_scale=8)
    
    leg = rBuild.build_module(module_type='biped_limb', side=fs[0], part='leg', guide_list=[fs + piece for piece in ['UpLeg', 'Leg', 'Foot']], offset_pv=50, ctrl_scale=8)
    foot = rBuild.build_module(module_type='foot', side=fs[0], part='foot', guide_list=[fs + piece for piece in ['Foot', 'ToeBase', 'Toe_End']], ctrl_scale=10, toe_piv=fs+'ToePiv', heel_piv=fs+'HeelPiv', in_piv=fs+'In', out_piv=fs+'Out')
    
    fingers = []
        
    for f in ['Index', 'Middle', 'Ring', 'Pinky']:
        finger = rBuild.build_module(module_type='finger', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num) for num in range(5)], ctrl_scale=1, fk_shape='lollipop')
        fingers.append(finger)
    thumb = rBuild.build_module(module_type='finger', side=fs[0], part='fingerThumb', guide_list=[fs + 'HandThumb' + str(num+1) for num in range(4)], ctrl_scale=1, fk_shape='lollipop')
    fingers.append(thumb)    
    

rFinal.final(utX=90, utY=0, DutZ=15, utScale=3, polish=False)
mc.delete('Hips')

### DEFAULT SKIN

bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
geo = mc.ls(body_mesh)
for g in geo:
    mc.skinCluster(bind_joints, g, tsb=True, bindMethod=0)

### SKIN/CURVE IO

import rjg.post.dataIO.ng_weights as rWeightNgIO
import rjg.post.dataIO.weights as rWeightIO
import rjg.post.dataIO.controls as rCtrlIO
reload(rWeightNgIO)
reload(rWeightIO)
reload(rCtrlIO)

print("Reading skin weight files...")

rCtrlIO.read_ctrls(groups + "/dungeons/character/Rigging/Rigs/Robin/Controls", curve_file='robin_control_curves')
rWeightNgIO.read_skin(body_mesh, groups + '/dungeons/character/Rigging/Rigs/Rayden/Skin', 'rayden_skinning_file') 

mc.copySkinWeights(ss='skinCluster1', ds='skinCluster1', mm='YZ', sa='closestPoint', ia='closestJoint') # necessary??

import rjg.build_scripts.robin_clothes as rc
reload(rc)
rc.robin_clothes(body_mesh, extras)

##### PROJECT FACE

face = rFile.import_hierarchy(groups + '/dungeons/anim/Rigs/RobinFace.mb')
import rjg.post.faceProject as rFaceProj
reload(rFaceProj)
rFaceProj.project(body=body_mesh, char='CHAR', f_model='FaceAtOrigin', f_rig='face_M', extras='Robin_EXTRAS', f_extras='F_EXTRAS', f_skel='faceRoot_JNT')
mc.delete(face)

mc.select(clear=True)
print("Robin rig build complete.")

#rCtrlIO.write_ctrls("/groups/dungeons/character/Rigging/Rigs/Robin/Controls", force=True, name='robin_control_curves')
# Don't use this. Use export skin weights from ngskintools. rWeightIO.write_skin("/groups/dungeons/character/Rigging/Rigs/Rayden/Skin", force=True, name='rayden_skin_weights')



















