import maya.cmds as mc
from importlib import reload

import rjg.build.rigModule as rModule
import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
reload(rModule)
reload(rChain)
reload(rCtrl)

class Root(rModule.RigModule):
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=None, model_path=None, guide_path=None, global_shape='gear_2D', root_shape='circle'):
        super(Root, self).__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)

        if self.guide_list:
            self.root_pose = guide_list[0]
        else:
            self.root_pose = (0, 0, 0)

        self.global_shape = global_shape
        self.root_shape = root_shape

        self.create_module()

    def create_module(self):
        super(Root, self).create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()

    def control_rig(self):
        if self.root_pose == (0, 0, 0):
            group_type = None
        else:
            group_type = 1

        self.global_control = rCtrl.Control(parent=self.control_grp, shape=self.global_shape, side=self.side, suffix='CTRL', name='global', axis='y', group_type=group_type, rig_type='global', translate=self.root_pose, rotate=self.root_pose, ctrl_scale=self.ctrl_scale)

        self.root_01 = rCtrl.Control(parent=self.global_control.ctrl, shape=self.root_shape, side=self.side, suffix='CTRL', name='root_01', axis='y', group_type='main', rig_type='root_01', translate=self.root_pose, rotate=self.root_pose, ctrl_scale=self.ctrl_scale * 0.5)

        self.root_02 = rCtrl.Control(parent=self.root_01.ctrl, shape=self.root_shape, side=self.side, suffix='CTRL', name='root_02', axis='y', group_type='main', rig_type='root_02', translate=self.root_pose, rotate=self.root_pose, ctrl_scale=self.ctrl_scale * 0.4)


    def output_rig(self):
        root_jnt_grp = mc.group(parent=self.module_grp, empty=True, name=self.base_name + '_JNT_GRP')
        mc.matchTransform(root_jnt_grp, self.root_02.ctrl)
        self.root_joint = mc.joint(root_jnt_grp, name=self.root_02.ctrl.replace('CTRL', 'JNT'))

        mc.parentConstraint(self.root_02.ctrl, self.root_joint, mo=True)
        mc.scaleConstraint(self.root_02.ctrl, self.root_joint, mo=True)


    def skeleton(self):
        bind_joints = []
        root_chain = rChain.Chain(transform_list=[self.root_joint], side=self.side, suffix='JNT', name=self.part)
        root_chain.create_from_transforms(parent=self.skel, pad=False)