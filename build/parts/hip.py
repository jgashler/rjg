import maya.cmds as mc
from importlib import reload

import rjg.build.rigModule as rModule
import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
import rjg.libs.attribute as rAttr
reload(rModule)
reload(rChain)
reload(rCtrl)
reload(rAttr)

class Hip(rModule.RigModule):
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=None, offset_hip=-0.1, hip_shape='hip', model_path=None, guide_path=None):
        super().__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)
        self.base_name = self.part + '_' + self.side
        self.offset_hip = offset_hip
        self.hip_shape = hip_shape
        self.create_module()

    def create_module(self):
        super().create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()

    def control_rig(self):
        self.hip_01 = rCtrl.Control(parent=self.control_grp, shape=self.hip_shape, side=None, suffix='CTRL', name=self.base_name + '_01', axis='y', group_type='main', rig_type='primary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale*0.4)
        self.hip_02 = rCtrl.Control(parent=self.hip_01.ctrl, shape=self.hip_shape, side=None, suffix='CTRL', name=self.base_name + '_02', axis='y', group_type='main', rig_type='secondary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale*0.35)
        self.hip_01.tag_as_controller()
        self.hip_02.tag_as_controller()

    def output_rig(self):
        hip_jnt_grp = mc.group(parent=self.module_grp, empty=True, name=self.base_name + "_JNT_GRP")
        mc.matchTransform(hip_jnt_grp, self.hip_02.ctrl)

        self.hip_jnt = mc.joint(hip_jnt_grp, name=self.hip_02.ctrl.replace("CTRL", "JNT"))
        mc.parentConstraint(self.hip_02.ctrl, self.hip_jnt, mo=True)

    def skeleton(self):
        hip_chain = rChain.Chain(transform_list=[self.hip_jnt], side=self.side, suffix='JNT', name=self.part)
        hip_chain.create_from_transforms(parent=self.skel, pad=False)
        self.bind_joints = hip_chain.joints

        mc.setAttr(hip_chain.constraints[0] + '.target[0].targetOffsetTranslateY', self.offset_hip)
        self.tag_bind_joints(self.bind_joints)

    def add_plugs(self):
        rAttr.Attribute(node=self.part_grp, type='plug', value=['root_M_JNT'], name='skeletonPlugs', children_name=[self.bind_joints[0]])

        target_list = ['CHAR', 'global_M_JNT', 'root_02_M_CTRL', '2']
        name_list = ['world', 'global', 'root', 'default_value']

        rAttr.Attribute(node=self.part_grp, type='plug', value=target_list, name=self.hip_01.ctrl + "_parent", children_name=name_list)

    def add_plugs(self):
        rAttr.Attribute(node=self.part_grp, type='plug', value=['root_M_JNT'], name='skeletonPlugs', children_name=[self.bind_joints[0]])
        
        target_list = ['CHAR',
                       'global_M_CTRL',
                       'root_02_M_CTRL',
                       '2']
        name_list = ['world', 'global', 'root', 'default_value']
        rAttr.Attribute(node=self.part_grp, type='plug', value=target_list, name=self.hip_01.ctrl +'_parent', children_name=name_list)

        driver_list = ['root_02_M_CTRL']
        driven_list = [self.hip_01.ctrl]
        rAttr.Attribute(node=self.part_grp, type='plug', value=driver_list, name='pacRigPlugs', children_name=driven_list)