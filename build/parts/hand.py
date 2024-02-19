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


class Hand(rModule.RigModule):
    def __init__(self,
                 side=None,
                 part=None,
                 guide_list=None,
                 ctrl_scale=None,
                 local_orient=False,
                 model_path=None,
                 guide_path=None):
        super().__init__(side=side, part=part,
                                       guide_list=guide_list,
                                       ctrl_scale=ctrl_scale,
                                       model_path=model_path,
                                       guide_path=guide_path)
        
        self.base_name = self.part + '_' + self.side

        self.local_orient = local_orient

        self.create_module()

    def create_module(self):
        super().create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()

    def control_rig(self):
        self.hand_01 = rCtrl.Control(parent=self.control_grp, shape='cube', side=None, suffix='CTRL', name=self.base_name + '_01', axis='y', group_type='main', 
                                     rig_type='primary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale)
        self.hand_02 = rCtrl.Control(parent=self.hand_01.ctrl, shape='cube', side=None, suffix='CTRL', name=self.base_name + '_02', axis='y', group_type='main', 
                                     rig_type='secondary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale * 0.85)
        self.hand_local = rCtrl.Control(parent=self.hand_02.ctrl, shape='quad_arrow', side=None, suffix='CTRL', name=self.base_name + '_local', axis='y', group_type='main', 
                                     rig_type='secondary', translate=self.guide_list[0], rotate=self.guide_list[0], ctrl_scale=self.ctrl_scale)
        self.hand_fk = rCtrl.Control(parent=self.control_grp, shape='circle', side=None, suffix='CTRL', name=self.base_name + '_fk', axis='y', group_type='main', 
                                     rig_type='fk', translate=self.guide_list[0], rotate=self.guide_list[0], ctrl_scale=self.ctrl_scale)
        
        for c in [self.hand_01, self.hand_02, self.hand_local, self.hand_fk]:
            c.tag_as_controller()
        
    def output_rig(self):
        ik_jnt = mc.joint(self.hand_local.ctrl, name=self.hand_01.ctrl.replace("CTRL", "ik_JNT"))
        fk_jnt = mc.joint(self.hand_local.ctrl, name=self.hand_01.ctrl.replace("CTRL", "JNT"))

        mc.parentConstraint(self.hand_local.ctrl, ik_jnt, mo=True)
        mc.parentConstraint(self.hand_fk.ctrl, fk_jnt, mo=True)
        mc.connectAttr(self.hand_local.ctrl + '.scale', ik_jnt + '.scale')
        mc.connectAttr(self.hand_fk.ctrl + '.scale', fk_jnt + '.scale')

        self.blend_chain = rChain.Chain(transform_list=[ik_jnt], side=self.side, suffix='switch_JNT', name=self.part)
        self.blend_chain.create_blend_chain(switch_node=self.base_name, chain_a=[fk_jnt], chain_b=[ik_jnt], translate=False)
        mc.setAttr(self.blend_chain.joints[0] + '.jointOrient', 0, 0, 0)

        rev = mc.createNode("reverse", name=self.base_name + '_REV')
        mc.connectAttr(self.blend_chain.switch.attr, rev + '.inputX')
        mc.connectAttr(rev + '.outputX', self.hand_01.top + '.visibility')

        mc.group(ik_jnt, fk_jnt, self.blend_chain.joints[0], parent=self.module_grp, name=self.base_name + '_JNT_GRP')
        mc.matchTransform(self.base_name + '_JNT_GRP', self.guide_list[0])

    def skeleton(self):
        jnt = mc.joint(self.skel, name=self.base_name + '_JNT')
        mc.parentConstraint(self.blend_chain.joints[0], jnt, mo=False)
        mc.connectAttr(self.blend_chain.joints[0] + '.scale', jnt + '.scale')
        self.bind_joints = [jnt]
        self.tag_bind_joints(self.bind_joints)

    def add_plugs(self):
        rAttr.Attribute(node=self.part_grp, type='plug', value=['mc.ls("arm_' + self.side + '_??_JNT")[-1]'], name='skeletonPlugs', children_name=[self.bind_joints[0]])

        driver_list = ['arm_'+ self.side +'_03_switch_JNT', 'clavicle_'+ self.side +'_02_driver_JNT']
        driven_list = [self.base_name + '_fk_CTRL_CNST_GRP', self.base_name + '_JNT_GRP']
        rAttr.Attribute(node=self.part_grp, type='plug', value=driver_list, name='pacRigPlugs', children_name=driven_list)

        driver_list = ['arm_'+ self.side +'_03_switch_JNT']
        driven_list = [self.base_name + '_01_switch_JNT']
        rAttr.Attribute(node=self.part_grp, type='plug', value=driver_list, name='pocRigPlugs', children_name=driven_list)

        hide_list = ['hand_'+ self.side + '_fk_CTRL_CNST_GRP']
        rAttr.Attribute(node=self.part_grp, type='plug', value=[' '.join(hide_list)], name='hideRigPlugs', children_name=['hideNodes'])

        target_list = ['CHAR',
                       'global_M_CTRL',
                       'root_02_M_CTRL',
                       'COG_M_CTRL',
                       'chest_M_01_CTRL',
                       'clavicle_'+ self.side +'_CTRL', '2']
        name_list = ['world', 'global', 'root', 'hip', 'chest', 'clavicle', 'default_value']
        rAttr.Attribute(node=self.part_grp, type='plug', value=target_list, name=self.hand_01.ctrl +'_parent', children_name=name_list)

        switch_attr = self.side.lower() + 'ArmIKFK'
        switch_attr = 'arm' + self.side + '_IKFK'
        rAttr.Attribute(node=self.part_grp, type='plug', value=[switch_attr], name='switchRigPlugs', children_name=['ikFkSwitch'])