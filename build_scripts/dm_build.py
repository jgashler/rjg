import maya.cmds as mc
import platform
from importlib import reload

groups = 'G:' if platform.system() == 'Windows' else '/groups'
mc.scriptEditorInfo(suppressWarnings=True,suppressInfo=True)

import rjg.build.buildPart as rBuild
import rjg.post.finalize as rFinal
import rjg.libs.file as rFile
reload(rBuild)
reload(rFinal)
reload(rFile)

mp = groups + '/dungeons/character/Rigging/Rigs/DungeonMonster/dm_model_combine.mb'
gp = groups + '/dungeons/character/Rigging/Rigs/DungeonMonster/dm_guides.mb'
bp = groups + '/dungeons/character/Rigging/Rigs/DungeonMonster/dm_bone_locs.mb'

body_mesh = 'DM_combine'

mc.file(new=True, f=True)

### BUILD SCRIPT
root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)

hip = rBuild.build_module(module_type='hip', side='M', part='COG', guide_list=['Hips'], ctrl_scale=50, cog_shape='quad_arrow', waist_shape='circle', ctrl_rotate=True)
chest = rBuild.build_module(module_type='chest', side='M', part='chest', guide_list=['Spine2'], ctrl_scale=200, chest_shape='quad_arrow', rotate_ctrl=True)
spine = rBuild.build_module(module_type='spine', side='M', part='spine', guide_list=['Hips', 'Spine', 'Spine1', 'Spine2'], ctrl_scale=4, mid_ctrl=True, ctrl_rotate=True)
neck = rBuild.build_module(module_type='spine', side='M', part='neck', guide_list=['Neck', 'Neck1', 'Head'], ctrl_scale=3, mid_ctrl=False, joint_num=3, ctrl_rotate=True)
head = rBuild.build_module(module_type='head', side='M', part='head', guide_list=['Head'], ctrl_scale=5)

tail = rBuild.build_module(module_type='tail', side='M', part='tail', guide_list=['Tail_' + str(t) for t in range(1, 15)], ctrl_scale=25, pad=2)
jaw = rBuild.build_module(module_type='hinge', side='M', part='jaw', guide_list=['JawBase', 'JawTip'], ctrl_scale=40, par_ctrl='head_M_01_CTRL', par_jnt='head_M_JNT')

for fs in ['Left', 'Right']:    
    arm = rBuild.build_module(module_type='biped_limb', side=fs[0], part='arm', guide_list=[fs + piece for piece in ['Arm', 'ForeArm', 'Hand']], offset_pv=50, ctrl_scale=35)
    clavicle = rBuild.build_module(module_type='clavicle', side=fs[0], part='clavicle', guide_list=[fs + piece for piece in ['Shoulder', 'Arm']], local_orient=False, ctrl_scale=20) 
    hand = rBuild.build_module(module_type='hand', side=fs[0], part='hand', guide_list=[fs + 'Hand'], ctrl_scale=20)
    
    leg = rBuild.build_module(module_type='biped_limb', side=fs[0], part='leg', guide_list=[fs + piece for piece in ['UpLeg', 'Leg', 'Foot']], offset_pv=50, ctrl_scale=35)
    foot = rBuild.build_module(module_type='foot', side=fs[0], part='foot', guide_list=[fs + piece for piece in ['Foot', 'ToeBase', 'Toe_End']], ctrl_scale=20, toe_piv=fs+'ToePiv', heel_piv=fs+'HeelPiv', in_piv=fs+'In', out_piv=fs+'Out')
    
    fingers = []
        
    for f in ['Index', 'Middle', 'Pinky']:
        finger = rBuild.build_module(module_type='finger', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num) for num in range(4)], ctrl_scale=10, fk_shape='lollipop')
        fingers.append(finger)
    thumb = rBuild.build_module(module_type='finger', side=fs[0], part='fingerThumb', guide_list=[fs + 'HandThumb' + str(num+1) for num in range(4)], ctrl_scale=10, fk_shape='lollipop')
    fingers.append(thumb)    
    
### BONE CONTROLS    
    
# bone_locs = rFile.import_hierarchy(bp)   
# bone_locs = mc.listRelatives('bone_locs', children=True)

# bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
# for j in bind_joints:
#     mc.deleteAttr(j + '.bindJoint')

# float_bone_grp = mc.group(empty=True, name='floatBones_F')
# mc.parent(float_bone_grp, 'RIG')
# for b in bone_locs:
#     floatBone = rBuild.build_module(module_type='float_bone', side='F', part=b[:-4], guide_list=[b], ctrl_scale=2, par_jnt='root_M_JNT', par_ctrl='root_02_M_CTRL')
#     mc.parent(floatBone.part_grp, float_bone_grp)
# mc.delete('bone_locs')

### FINALIZE
    
rFinal.final(utX=150, utY=0, DutZ=20, utScale=50, quad=True)
mc.delete('Hips')

### DEFAULT SKIN

bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
geo = mc.ls(body_mesh)
for g in geo:
   mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1, bindMethod=0)
    
import rjg.post.dataIO.ng_weights as rWeightNgIO
import rjg.post.dataIO.weights as rWeightIO
import rjg.post.dataIO.controls as rCtrlIO
reload(rWeightNgIO)
reload(rWeightIO)
reload(rCtrlIO)
    
rCtrlIO.read_ctrls(groups + "/dungeons/character/Rigging/Rigs/DungeonMonster/Controls", curve_file='dm_control_curves')
#rCtrlIO.write_ctrls("/groups/dungeons/character/Rigging/Rigs/DungeonMonster/Controls", force=True, name='dm_control_curves')