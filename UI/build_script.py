import maya.cmds as mc
from importlib import reload

import rjg.build.buildPart as rBuild
import rjg.post.finalize as rFinal

def build(info):
    mp = info['model_path']
    gp = info['guide_path']
    
    mc.file(new=True, f=True)

    ### BUILD SCRIPT
    
    root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
    mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)
    
    hip = rBuild.build_module(module_type='hip', side='M', part='hip', guide_list=['Hips'], ctrl_scale=50, hip_shape='circle')
    chest = rBuild.build_module(module_type='chest', side='M', part='chest', guide_list=['Spine2'], ctrl_scale=70, chest_shape='circle')
    spine = rBuild.build_module(module_type='spine', side='M', part='spine', guide_list=['Hips', 'Spine2'], ctrl_scale=15)
    neck = rBuild.build_module(module_type='neck', side='M', part='neck', guide_list=['Spine2', 'Head'], ctrl_scale=8)
    head = rBuild.build_module(module_type='head', side='M', part='head', guide_list=['Head'], ctrl_scale=50)
    
    
    for fs in ['Left', 'Right']:    
        arm = rBuild.build_module(module_type='biped_limb', side=fs[0], part='arm', guide_list=[fs + piece for piece in ['Arm', 'ForeArm', 'Hand']], offset_pv=30, ctrl_scale=15)
        clavicle = rBuild.build_module(module_type='clavicle', side=fs[0], part='clavicle', guide_list=[fs + piece for piece in ['Shoulder', 'Arm']], local_orient=True, ctrl_scale=9) 
        hand = rBuild.build_module(module_type='hand', side=fs[0], part='hand', guide_list=[fs + 'Hand'], ctrl_scale=8)
        
        leg = rBuild.build_module(module_type='biped_limb', side=fs[0], part='leg', guide_list=[fs + piece for piece in ['UpLeg', 'Leg', 'Foot']], offset_pv=60, ctrl_scale=10)
        foot = rBuild.build_module(module_type='foot', side=fs[0], part='foot', guide_list=[fs + piece for piece in ['Foot', 'ToeBase', 'Toe_End']], ctrl_scale=10, toe_piv=fs+'ToePiv', heel_piv=fs+'HeelPiv', in_piv=fs+'In', out_piv=fs+'Out')
        
        fingers = []
        for f in ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']:
            finger = rBuild.build_module(module_type='finger', side=fs[0], part='finger'+f, guide_list=[fs + 'Hand' + f + str(num+1) for num in range(4)], ctrl_scale=3)
            fingers.append(finger)
    
    
    rFinal.final()
    
    mc.delete('Hips')
    