import maya.cmds as mc
from importlib import reload

import rjg.build.buildPart as rBuild
import rjg.post.finalize as rFinal
reload(rBuild)
reload(rFinal)

mp = 'C:/Users/jgash/Documents/maya/projects/F23/ninja_model.mb'
gp = 'C:/Users/jgash/Documents/maya/projects/F23/ninja_guides.mb'

mc.file(new=True, f=True)

### BUILD SCRIPT

root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)

for fs in ['Left', 'Right']:
    #arm = rBuild.build_module(module_type='biped_limb', side=fs[0], part='arm', guide_list=[fs + piece for piece in ['Arm', 'ForeArm', 'Hand']], offset_pv=5, ctrl_scale=15)
    #hand = rBuild.build_module(module_type='hand', side=fs[0], part='hand', guide_list=[fs + 'Hand'], ctrl_scale=8)
    fingers = []
    for f in ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']:
        #finger = rBuild.build_module(module_type='finger', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num+1) for num in range(4)], ctrl_scale=3)
        finger = rBuild.build_module(module_type='meta_finger', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num+1) for num in range(4)], ctrl_scale=2, hand=fs + 'Hand')
        fingers.append(finger)

#rFinal.final(utX=90, utY=0, DutZ=15, utScale=3)

mc.delete('Hips')

### DEFAULT SKIN

bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
geo = mc.ls('Ch24')
for g in geo:
    mc.skinCluster(bind_joints, g, tsb=True, bindMethod=0)
    #mc.geomBind(bm=3, 






