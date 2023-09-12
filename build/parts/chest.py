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

class Chest(rModule.RigModule):
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=None, chest_shape='chest', model_path=None, guide_path=None):
        super().__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)

        self.chest_shape = chest_shape
        self.create_module()

    def create_module(self):
        super().create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        #self.add_plugs()

    def control_rig(self):
        self.chest_01 = rCtrl.Control(parent=self.control_grp, shape=self.chest_shape, side=self.side, suffix='CTRL', name=self.part + '_01', axis='y', group_type='main', rig_type='primary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale*0.4)

        self.chest_02 = rCtrl.Control(parent=self.chest_01.ctrl, shape=self.chest_shape, side=self.side, suffix='CTRL', name=self.part + '_02', axis='y', group_type='main', rig_type='secondary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale*0.35)

    def output_rig(self):
        chest_jnt_grp = mc.group(parent=self.module_grp, empty=True, name=self.base_name + "_JNT_GRP")
        mc.matchTransform(chest_jnt_grp, self.chest_02.ctrl)

        self.chest_jnt = mc.joint(chest_jnt_grp, name=self.chest_02.ctrl.replace("CTRL", "JNT"))
        mc.parentConstraint(self.chest_02.ctrl, self.chest_jnt, mo=True)

    def skeleton(self):
        chest_chain = rChain.Chain(transform_list=[self.chest_jnt], side=self.side, suffix='JNT', name=self.part)
        chest_chain.create_from_transforms(parent=self.skel, pad=False)
        self.bind_joints = chest_chain.joints

        self.tag_bind_joints(self.bind_joints)

        
