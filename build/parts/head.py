import maya.cmds as mc
from importlib import reload

import rjg.build.rigModule as rModule
import rjg.libs.attribute as rAttr
import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
reload(rAttr)
reload(rModule)
reload(rChain)
reload(rCtrl)

class Head(rModule.RigModule):
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=None, model_path=None, guide_path=None, head_shape='circle'):
        super().__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)

        self.side = side
        self.part = part
        self.base_name = self.part + '_' + self.side

        self.guide_list = guide_list
        self.ctrl_scale = ctrl_scale
        self.model_path = model_path
        self.guide_list = guide_list

        self.head_shape = head_shape

        self.create_module()

    def create_module(self):
        super().create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()

    def control_rig(self):
        self.head_01 = rCtrl.Control(parent=self.control_grp, shape=self.head_shape, side=None, suffix='CTRL', name=self.base_name + '_01', axis='y', group_type='main', rig_type='primary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale*0.4)
        self.head_02 = rCtrl.Control(parent=self.head_01.ctrl, shape=self.head_shape, side=None, suffix='CTRL', name=self.base_name + '_02', axis='y', group_type='main', rig_type='secondary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale*0.3)
        self.head_01.tag_as_controller()
        self.head_02.tag_as_controller(parent=self.head_01)

    def output_rig(self):
        head_jnt_grp = mc.group(parent=self.module_grp, empty=True, name=self.base_name + '_JNT_GRP')
        mc.matchTransform(head_jnt_grp, self.head_02.ctrl)

        self.head_jnt = mc.joint(head_jnt_grp, name=self.head_02.ctrl.replace('CTRL', 'JNT'))
        #mc.parentConstraint(self.head_02.ctrl, self.head_jnt, mo=True)
        mc.pointConstraint(self.head_02.ctrl, self.head_jnt, maintainOffset=True)
        mc.orientConstraint(self.head_02.ctrl, self.head_jnt, maintainOffset=True)
        mc.scaleConstraint(self.head_02.ctrl, self.head_jnt, maintainOffset=True)

    def skeleton(self):
        head_chain = rChain.Chain(transform_list=[self.head_jnt], side=self.side, suffix='JNT', name=self.part)
        head_chain.create_from_transforms(parent=self.skel, pad=False)
        self.bind_joints = head_chain.joints
        self.tag_bind_joints(self.bind_joints)


    def add_plugs(self):
        rAttr.Attribute(node=self.part_grp, type='plug', value=['mc.ls("neck_' + self.side + '_??_JNT")[-1]'], name='skeletonPlugs', children_name=[self.bind_joints[0]])

        target_list = ['CHAR', 
                       'global_M_CTRL',
                       'root_02_M_CTRL',
                       'COG_M_CTRL',
                       'chest_M_01_CTRL',
                       'chest_M_02_CTRL',
                       'neck_M_base_CTRL',
                       '6']
        name_list = ['world', 'global', 'root', 'cog', 'chest_01', 'chest_02', 'neck', 'default_value']
        point_names = ['point' + name.title() for name in name_list]
        orient_names = ['orient' + name.title() for name in name_list]
        rAttr.Attribute(node=self.part_grp, type='plug', value=target_list, name=self.head_01.ctrl +'_point', children_name=point_names)
        rAttr.Attribute(node=self.part_grp, type='plug', value=target_list, name=self.head_01.ctrl +'_orient', children_name=orient_names)

        delete_list = [self.base_name + '_02_JNT_pointConstraint1']
        rAttr.Attribute(node=self.part_grp, type='plug', value=[' '.join(delete_list)], name='deleteRigPlugs', children_name=['deleteNodes'])

        rAttr.Attribute(node=self.part_grp, type='plug', value=[self.head_01.ctrl], name='transferAttributes', children_name=['neck_M_tip_CTRL'])

        rAttr.Attribute(node=self.part_grp, type='plug', value=['mc.ls("neck_M_??_driver_JNT", "neck_M_??_fk_offset_CTRL")[-1]'], name='pocRigPlugs', children_name=[self.head_jnt])