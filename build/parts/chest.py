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
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=None, chest_shape='chest', model_path=None, guide_path=None, parent=None):
        super().__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)

        self.chest_shape = chest_shape
        self.base_name = self.part + '_' + self.side
        self.parent = parent

        if not self.parent:             # allow parenting to other controls
            parent = self.control_grp

        self.create_module()

    def create_module(self):
        super().create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()


    def control_rig(self):
        self.chest_01 = rCtrl.Control(parent=self.parent, shape=self.chest_shape, side=None, suffix='CTRL', name=self.base_name + '_01', axis='y', group_type='main', rig_type='primary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale*0.4)

        self.chest_02 = rCtrl.Control(parent=self.chest_01.ctrl, shape=self.chest_shape, side=None, suffix='CTRL', name=self.base_name + '_02', axis='y', group_type='main', rig_type='secondary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale*0.35)

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

    def add_plugs(self):
        # skeleton plugs
        rAttr.Attribute(node=self.part_grp, type='plug', value=['mc.ls("spine_M_??_JNT")[-1]'], name='skeletonPlugs', children_name=[self.bind_joints[0]])

        delete_list = ['chest_M_02_JNT_parentConstraint1', 'spine_M_tip_CTRL_CNST_GRP_parentConstraint1']
        rAttr.Attribute(node=self.part_grp, type='plug', value=[' '.join(delete_list)], name='deleteRigPlugs', children_name=['deleteNodes'])

        rAttr.Attribute(node=self.part_grp, type='plug', value=['mc.ls("spine_M_??_driver_JNT")[-1]'], name='pocRigPlugs', children_name=[self.chest_jnt + '_point'])
        rAttr.Attribute(node=self.part_grp, type='plug', value=[self.chest_02.ctrl], name='orcRigPlugs', children_name=[self.chest_jnt + '_orient'])

        target_list = ['CHAR',
                       'global_M_CTRL',
                       'root_02_M_CTRL',
                       'spine_M_03_FK_CTRL',
                       '3']
        name_list = ['world', 'global', 'root', 'spine', 'default_value']
        point_names = ['point' + name.title() for name in name_list]
        orient_names = ['orient' + name.title() for name in name_list]

        rAttr.Attribute(node=self.part_grp, type='plug', value=target_list, name=self.chest_01.ctrl + '_point', children_name=point_names)
        rAttr.Attribute(node=self.part_grp, type='plug', value=target_list, name=self.chest_01.ctrl + '_orient', children_name=orient_names)

        rAttr.Attribute(node=self.part_grp, type='plug', value=[self.chest_01.ctrl], name='transferAttributes', children_name=['spine_M_tip_CTRL'])


