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

class FloatBone(rModule.RigModule):
    def __init__(self, side='floatBone', part=None, guide_list=None, ctrl_scale=None, shape='cube', model_path=None, guide_path=None, par_ctrl=None, par_jnt=None):
        super().__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)

        self.par_ctrl = par_ctrl
        self.par_jnt = par_jnt

        self.shape = shape
        self.base_name = self.part + '_' + self.side
        #self.base_name = self.part

        self.create_module()

    def create_module(self):
        super().create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()


    def control_rig(self):
        self.floatBone_ctrl = rCtrl.Control(parent=self.control_grp, shape=self.shape, side=self.side, suffix='CTRL', name=self.base_name, axis='y', group_type='float', rig_type='float', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale)
        self.floatBone_ctrl.tag_as_controller()

    def output_rig(self):
        float_jnt_grp = mc.group(parent=self.module_grp, empty=True, name=self.base_name + '_JNT_GRP')
        mc.matchTransform(float_jnt_grp, self.floatBone_ctrl.ctrl)

        self.floatBone_jnt = mc.joint(float_jnt_grp, name=self.floatBone_ctrl.ctrl.replace('CTRL', 'JNT'))
        mc.parentConstraint(self.floatBone_ctrl.ctrl, self.floatBone_jnt, mo=True)

        # self.floatBone_jnt = mc.joint(name=self.floatBone_ctrl.ctrl.replace('CTRL', 'JNT'))
        # mc.parentConstraint(self.floatBone_ctrl.ctrl, self.floatBone_jnt, mo=False)

    def skeleton(self):
        floatBone_chain = rChain.Chain(transform_list=[self.floatBone_jnt], side=self.side, suffix='JNT', name=self.part)
        floatBone_chain.create_from_transforms(parent=self.skel, pad=False)
        self.bind_joints = floatBone_chain.joints
        self.tag_bind_joints(self.bind_joints)


    def add_plugs(self):
        rAttr.Attribute(node=self.part_grp, type='plug', value=[self.par_jnt], name='skeletonPlugs', children_name=[self.bind_joints[0]])
        rAttr.Attribute(node=self.part_grp, type='plug', value=[self.par_ctrl], name='pacRigPlugs', children_name=[self.base_name + '_CTRL_CNST_GRP'])