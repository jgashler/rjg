
import maya.cmds as mc
from importlib import reload

import rjg.build.buildPart as rBuild
import rjg.post.finalize as rFinal
import rjg.build.prop as rProp
reload(rProp)
reload(rBuild)
reload(rFinal)

mp = '/groups/dungeons/character/Rigging/robin_model.mb'
gp = '/groups/dungeons/character/Rigging/robin_guides.mb'
pref = ''

mc.file(new=True, f=True)

### BUILD SCRIPT

root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)

hip = rBuild.build_module(module_type='hip', side='M', part='hip', guide_list=[pref+'Hips'], ctrl_scale=50, hip_shape='circle')
chest = rBuild.build_module(module_type='chest', side='M', part='chest', guide_list=[pref+'Spine2'], ctrl_scale=70, chest_shape='circle')
spine = rBuild.build_module(module_type='spine', side='M', part='spine', guide_list=[pref+'Hips', pref+'Spine', pref+'Spine1', pref+'Spine2'], ctrl_scale=1, mid_ctrl=True)
neck = rBuild.build_module(module_type='neck', side='M', part='neck', guide_list=[pref+'Spine2', pref+'Head'], ctrl_scale=1)
head = rBuild.build_module(module_type='head', side='M', part='head', guide_list=[pref+'Head'], ctrl_scale=50)


for fs in ['Left', 'Right']:    
    arm = rBuild.build_module(module_type='biped_limb', side=fs[0], part='arm', guide_list=[pref + fs + piece for piece in ['Arm', 'ForeArm', 'Hand']], offset_pv=5, ctrl_scale=15)
    clavicle = rBuild.build_module(module_type='clavicle', side=fs[0], part='clavicle', guide_list=[pref + fs + piece for piece in ['Shoulder', 'Arm']], local_orient=True, ctrl_scale=9) 
    hand = rBuild.build_module(module_type='hand', side=fs[0], part='hand', guide_list=[pref + fs + 'Hand'], ctrl_scale=8)
    
    leg = rBuild.build_module(module_type='biped_limb', side=fs[0], part='leg', guide_list=[pref + fs + piece for piece in ['UpLeg', 'Leg', 'Foot']], offset_pv=5, ctrl_scale=10)
    foot = rBuild.build_module(module_type='foot', side=fs[0], part='foot', guide_list=[pref + fs + piece for piece in ['Foot', 'ToeBase', 'Toe_End']], ctrl_scale=10, toe_piv=pref + fs+'ToePiv', heel_piv=pref + fs+'HeelPiv', in_piv=pref + fs+'In', out_piv=pref + fs+'Out')
    
    fingers = []
    for f in ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']:
        #finger = rBuild.build_module(module_type='finger', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num+1) for num in range(4)], ctrl_scale=3)
        #finger = rBuild.build_module(module_type='biped_limb', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num+1) for num in range(4)], ctrl_scale=2.5, offset_pv=10, bendy=False, twisty=False, segments=False, gimbal=False, offset=False)
        finger = rBuild.build_module(module_type='meta_finger', side=fs[0], part='finger'+f, guide_list=[pref + fs + 'Hand' + f + str(num+1) for num in range(4)], ctrl_scale=2, hand=fs + 'Hand')
        fingers.append(finger)

####
'''
target_list = ['CHAR', 'global_M_CTRL', 'root_02_M_CTRL','chest_M_01_CTRL', 'arm_L_03_fk_CTRL', 'arm_R_03_fk_CTRL', '3']
target_names = ['world', 'global', 'root', 'chest', 'leftHand', 'rightHand', 'default_value']

fp = 'C:/Users/jgash/Documents/maya/projects/F23/ninja_prop.mb'

prop = rProp.Prop(name='staff', prop_filepath=fp, target_names=target_names, target_list=target_list, char_ctrl='root_M', prop_ctrl='prop_CTRL')

mc.parent(prop.ssl_grp, 'RIG')
mc.parent(prop.prop, prop.ssl_grp)
'''

#####
rFinal.final(utX=90, utY=0, DutZ=15, utScale=3)
#print(prop.ssl_grp)

mc.delete('Hips')

### DEFAULT SKIN

bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
geo = mc.ls('Robin_Retopologized')
for g in geo:
    mc.skinCluster(bind_joints, g, tsb=True, bindMethod=2)
    #mc.geomBind(bm=3, 

### SKIN/CURVE IO

import rjg.post.dataIO.weights as rWeightIO
import rjg.post.dataIO.controls as rCtrlIO
reload(rWeightIO)
reload(rCtrlIO)

#rCtrlIO.write_ctrls("C:/Users/jgash/Desktop", force=True)
#rCtrlIO.read_ctrls("C:/Users/jgash/Desktop/")

#rWeightIO.write_skin("C:/Users/jgash/Desktop", force=True)
#rWeightIO.read_skin("C:/Users/jgash/Desktop/")