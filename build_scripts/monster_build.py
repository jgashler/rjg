import maya.cmds as mc
from importlib import reload

import rjg.build.buildPart as rBuild
import rjg.post.finalize as rFinal
import rjg.build.prop as rProp
reload(rProp)
reload(rBuild)
reload(rFinal)

mp = 'C:/Users/jgash/Documents/maya/projects/W24/monster_geo.mb'
gp = 'C:/Users/jgash/Documents/maya/projects/W24/monster_guides.mb'

mc.file(new=True, f=True)

### BUILD SCRIPT

root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)

hip = rBuild.build_module(module_type='hip', side='M', part='hip', guide_list=['Hips'], ctrl_scale=50, hip_shape='circle')
chest = rBuild.build_module(module_type='chest', side='M', part='chest', guide_list=['Spine2'], ctrl_scale=70, chest_shape='circle')
spine = rBuild.build_module(module_type='spine', side='M', part='spine', guide_list=['Hips', 'Spine', 'Spine1', 'Spine2'], ctrl_scale=1, mid_ctrl=True)
neck = rBuild.build_module(module_type='neck', side='M', part='neck', guide_list=['Spine2', 'Head'], ctrl_scale=1)
head = rBuild.build_module(module_type='head', side='M', part='head', guide_list=['Head'], ctrl_scale=50)


for fs in ['Left', 'Right']:    
    arm = rBuild.build_module(module_type='biped_limb', side=fs[0], part='arm', guide_list=[fs + piece for piece in ['Arm', 'ForeArm', 'Hand']], offset_pv=5, ctrl_scale=15, bendy=False)
    clavicle = rBuild.build_module(module_type='clavicle', side=fs[0], part='clavicle', guide_list=[fs + piece for piece in ['Shoulder', 'Arm']], local_orient=True, ctrl_scale=9) 
    #hand = rBuild.build_module(module_type='hand', side=fs[0], part='hand', guide_list=[fs + 'Hand'], ctrl_scale=8)
    
    leg = rBuild.build_module(module_type='biped_limb', side=fs[0], part='leg', guide_list=[fs + piece for piece in ['UpLeg', 'Leg', 'Foot']], offset_pv=5, ctrl_scale=10, bendy=False)
    #foot = rBuild.build_module(module_type='foot', side=fs[0], part='foot', guide_list=[fs + piece for piece in ['Foot', 'ToeBase', 'Toe_End']], ctrl_scale=10, toe_piv=fs+'ToePiv', heel_piv=fs+'HeelPiv', in_piv=fs+'In', out_piv=fs+'Out')
  

####

rFinal.final(utX=90, utY=0, DutZ=15, utScale=3)
#print(prop.ssl_grp)

mc.delete('Hips')

### DEFAULT SKIN
'''
bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
geo = mc.ls('Ch24')
for g in geo:
    mc.skinCluster(bind_joints, g, tsb=True, bindMethod=2)
    #mc.geomBind(bm=3, 

### SKIN/CURVE IO

import rjg.post.dataIO.weights as rWeightIO
import rjg.post.dataIO.controls as rCtrlIO
reload(rWeightIO)
reload(rCtrlIO)
'''
#rCtrlIO.write_ctrls("C:/Users/jgash/Desktop", force=True)
#rCtrlIO.read_ctrls("C:/Users/jgash/Desktop/")

#rWeightIO.write_skin("C:/Users/jgash/Desktop", force=True)
#rWeightIO.read_skin("C:/Users/jgash/Desktop/")
