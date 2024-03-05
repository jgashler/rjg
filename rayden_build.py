import maya.cmds as mc
from importlib import reload

import rjg.build.buildPart as rBuild
import rjg.post.finalize as rFinal
import rjg.build.prop as rProp
import rjg.libs.file as rFile
reload(rProp)
reload(rBuild)
reload(rFinal)
reload(rFile)

mp = '/groups/dungeons/character/Rigging/Rayden/ray_model.mb'
gp = '/groups/dungeons/character/Rigging/Rayden/ray_guides.mb'
pref = ''

mc.file(new=True, f=True)

### BUILD SCRIPT
root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
rFile.import_hierarchy('/groups/dungeons/character/Rigging/Rayden/ray_extras.mb', parent='MODEL')
mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)

hip = rBuild.build_module(module_type='hip', side='M', part='COG', guide_list=[pref+'Hips'], ctrl_scale=50, cog_shape='quad_arrow', waist_shape='circle')
chest = rBuild.build_module(module_type='chest', side='M', part='chest', guide_list=[pref+'Spine2'], ctrl_scale=70, chest_shape='circle')
spine = rBuild.build_module(module_type='spine', side='M', part='spine', guide_list=[pref+'Hips', pref+'Spine', pref+'Spine1', pref+'Spine2'], ctrl_scale=1, mid_ctrl=True)
neck = rBuild.build_module(module_type='neck', side='M', part='neck', guide_list=[pref+'Neck', pref+'Neck1', pref+'Head'], ctrl_scale=1, mid_ctrl=True)
head = rBuild.build_module(module_type='head', side='M', part='head', guide_list=[pref+'Head'], ctrl_scale=50)


for fs in ['Left', 'Right']:    
    arm = rBuild.build_module(module_type='biped_limb', side=fs[0], part='arm', guide_list=[pref + fs + piece for piece in ['Arm', 'ForeArm', 'Hand']], offset_pv=50, ctrl_scale=5)
    clavicle = rBuild.build_module(module_type='clavicle', side=fs[0], part='clavicle', guide_list=[pref + fs + piece for piece in ['Shoulder', 'Arm']], local_orient=False, ctrl_scale=9) 
    hand = rBuild.build_module(module_type='hand', side=fs[0], part='hand', guide_list=[pref + fs + 'Hand'], ctrl_scale=8)
    
    leg = rBuild.build_module(module_type='biped_limb', side=fs[0], part='leg', guide_list=[pref + fs + piece for piece in ['UpLeg', 'Leg', 'Foot']], offset_pv=50, ctrl_scale=8)
    foot = rBuild.build_module(module_type='foot', side=fs[0], part='foot', guide_list=[pref + fs + piece for piece in ['Foot', 'ToeBase', 'Toe_End']], ctrl_scale=10, toe_piv=pref + fs+'ToePiv', heel_piv=pref + fs+'HeelPiv', in_piv=pref + fs+'In', out_piv=pref + fs+'Out')
    
    fingers = []
    for f in ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']:
        #finger = rBuild.build_module(module_type='finger', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num+1) for num in range(4)], ctrl_scale=3)
        #finger = rBuild.build_module(module_type='biped_limb', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num+1) for num in range(4)], ctrl_scale=2.5, offset_pv=10, bendy=False, twisty=False, segments=False, gimbal=False, offset=False)
        finger = rBuild.build_module(module_type='meta_finger', side=fs[0], part='finger'+f, guide_list=[pref + fs + 'Hand' + f + str(num+1) for num in range(4)], ctrl_scale=2, hand=fs + 'Hand')
        fingers.append(finger)



#####

rFinal.final(utX=90, utY=0, DutZ=15, utScale=3)
mc.delete('Ray_Guides')

### DEFAULT SKIN

bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
geo = mc.ls('Ray_UBM')
for g in geo:
    mc.skinCluster(bind_joints, g, tsb=True, bindMethod=2)
    #mc.geomBind(bm=3, 

### SKIN/CURVE IO

import rjg.post.dataIO.weights as rWeightIO
import rjg.post.dataIO.controls as rCtrlIO
reload(rWeightIO)
reload(rCtrlIO)

rCtrlIO.read_ctrls("/groups/dungeons/character/Rigging/Robin/Controls", curve_file='robin_control_curves')
#rCtrlIO.write_ctrls("/groups/dungeons/character/Rigging/Rayden/Controls", force=True, name='robin_control_curves')

#rWeightIO.write_skin("/groups/dungeons/character/Rigging/Rayden/Skin", force=True, name='robin_skin_weights')
print("Reading skin weight files...")
#rWeightIO.read_skin("/groups/dungeons/character/Rigging/Rayden/Skin", weights_file='robin_skin_weights')
import rjg.rayden_clothes as rc
reload(rc)

mc.select(clear=True)
print("Rayden rig build complete.")