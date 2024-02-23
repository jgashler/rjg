import maya.cmds as mc
from importlib import reload

import rjg.build.rigModule as rModule
import rjg.libs.attribute as rAttr
import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
import rjg.build.ik as rIk
import rjg.build.fk as rFk
reload(rAttr)
reload(rModule)
reload(rChain)
reload(rCtrl)
reload(rIk)
reload(rFk)



class Foot(rModule.RigModule):
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=None, local_orient=False, model_path=None, guide_path=None, in_piv=None, out_piv=None, heel_piv=None, toe_piv=None):
        super(Foot, self).__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)
        self.__dict__.update(locals())

        if not self.toe_piv:
            self.toe_piv = self.guide_list[-1]
            
        self.create_module()

    def create_module(self):
        super().create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()

    def control_rig(self):
        attr_util = rAttr.Attribute(add=False)

        self.main_ctrl = rCtrl.Control(parent=self.control_grp, shape='cube', side=self.side, suffix='CTRL', name=self.base_name + '_01', axis='y', group_type='main', rig_type='primary', translate=self.guide_list[0], ctrl_scale=self.ctrl_scale)
        self.second_ctrl = rCtrl.Control(parent=self.main_ctrl.ctrl, shape='cube', side=self.side, suffix='CTRL', name=self.base_name + '_02', axis='y', group_type='main', rig_type='secondary', translate=self.guide_list[0], ctrl_scale=self.ctrl_scale * 0.85)
        self.toe_piv = rCtrl.Control(parent=self.second_ctrl.ctrl, shape='cube', side=self.side, suffix='CTRL', name=self.base_name + '_toe_piv', axis='y', group_type='main', rig_type='pivot', translate=self.toe_piv, rotate=self.guide_list[-1], ctrl_scale=self.ctrl_scale * 0.2)
        self.heel_piv = rCtrl.Control(parent=self.toe_piv.ctrl, shape='cube', side=self.side, suffix='CTRL', name=self.base_name + '_heel_piv', axis='y', group_type='main', rig_type='pivot', translate=self.heel_piv, ctrl_scale=self.ctrl_scale * 0.2)
        self.in_piv = rCtrl.Control(parent=self.heel_piv.ctrl, shape='cube', side=self.side, suffix='CTRL', name=self.base_name + '_in_piv', axis='y', group_type='main', rig_type='pivot', translate=self.in_piv, ctrl_scale=self.ctrl_scale * 0.2)
        self.out_piv = rCtrl.Control(parent=self.in_piv.ctrl, shape='cube', side=self.side, suffix='CTRL', name=self.base_name + '_out_piv', axis='y', group_type='main', rig_type='pivot', translate=self.out_piv, ctrl_scale=self.ctrl_scale * 0.2)
        self.ball_ctrl = rCtrl.Control(parent=self.out_piv.ctrl, shape='locator_3D', side=self.side, suffix='CTRL', name=self.base_name + '_ball', axis='y', group_type='main', rig_type='secondary', translate=self.guide_list[1], rotate=self.guide_list[1], ctrl_scale=self.ctrl_scale * 1.45)
        self.ankle_ctrl = rCtrl.Control(parent=self.ball_ctrl.ctrl, shape='locator_3D', side=self.side, suffix='CTRL', name=self.base_name + '_ankle', axis='y', group_type='main', rig_type='secondary', translate=self.guide_list[0], rotate=self.guide_list[0], ctrl_scale=self.ctrl_scale)
        self.toe_ctrl = rCtrl.Control(parent=self.out_piv.ctrl, shape='locator_3D', side=self.side, suffix='CTRL', name=self.base_name + '_toe', axis='y', group_type='main', rig_type='secondary', translate=self.guide_list[1], rotate=self.guide_list[1], ctrl_scale=self.ctrl_scale)
        ts_list = [self.ball_ctrl, self.toe_ctrl, self.toe_piv, self.heel_piv, self.in_piv, self.out_piv]
        for c in ts_list:
            attr_util.lock_and_hide(node=c.ctrl, rotate=False)

        s_list = [self.main_ctrl, self.second_ctrl]
        for s in s_list:
            attr_util.lock_and_hide(node=s.ctrl, translate=False, rotate=False)
            s.tag_as_controller()

    def output_rig(self):
        sc = rIk.Ik(side=self.side, part=self.part, guide_list=[self.guide_list[0], self.guide_list[1]], solver='ikSCsolver')
        sc.build_ik_chain()
        sc.build_ikh(constrain=False)
        mc.setAttr(sc.ik_joints[-1] + '.jointOrient', 0, 0, 0)

        toe_chain = rChain.Chain(transform_list=[self.guide_list[1], self.guide_list[2]], side=self.side, suffix='toe_JNT', name=self.part)
        toe_chain.create_from_transforms(parent=self.module_grp, static=True)

        sc_grp = mc.group(empty=True, parent=self.module_grp, name=sc.ikh + '_GRP')
        mc.matchTransform(sc_grp, sc.ik_joints[-1])
        mc.parent(sc.ik_joints[0], sc.ikh, sc_grp)

        mc.aimConstraint(self.ankle_ctrl.ctrl, sc_grp, aimVector=(0, -1, 0), upVector=(0, 0, 1), worldUpType='objectRotation', worldUpObject=self.ankle_ctrl.ctrl, worldUpVector=(0, 0, 1), mo=True)
        mc.pointConstraint(self.ball_ctrl.ctrl, sc_grp, mo=True)
        mc.parentConstraint(self.toe_ctrl.ctrl, toe_chain.joints[0], mo=True)

        fk = rFk.Fk(side=self.side, part=self.part, guide_list=self.guide_list, gimbal=False, offset=False, pad='auto', ctrl_scale=self.ctrl_scale, fk_shape='circle')
        fk.build_fk()
        mc.parent(fk.fk_joints[0], self.module_grp)
        mc.parent(fk.fk_ctrls[0].top, self.control_grp)

        ik_chain = rChain.Chain(transform_list=[sc.ik_joints[0], toe_chain.joints[0], toe_chain.joints[1]], side=self.side, suffix='ik_JNT', name=self.part)
        ik_chain.create_from_transforms(parent=self.module_grp)

        self.blend_chain = rChain.Chain(transform_list=fk.fk_joints, side=self.side, suffix='switch_JNT', name=self.part)
        self.blend_chain.create_blend_chain(switch_node=self.base_name, chain_a=fk.fk_joints, chain_b=ik_chain.joints)
        mc.parent(self.blend_chain.joints[0], self.module_grp)

        self.add_foot_attrs()

        rev = mc.createNode('reverse', name=self.base_name + '_REV')
        mc.connectAttr(self.blend_chain.switch.attr, rev + '.inputX')
        mc.connectAttr(rev + '.outputX', self.main_ctrl.top + '.visibility')
        mc.connectAttr(self.blend_chain.switch.attr, fk.fk_ctrls[0].top + '.visibility')


    def add_foot_attrs(self):
        rAttr.Attribute(node=self.main_ctrl.ctrl, type='separator', name='________')

        roll = rAttr.Attribute(node=self.main_ctrl.ctrl, type='double', value=0, keyable=True, name='roll')
        roll_max = rAttr.Attribute(node=self.main_ctrl.ctrl, type='double', value=30, min=0, keyable=True, name='rollMax')
        toe_roll = rAttr.Attribute(node=self.main_ctrl.ctrl, type='double', value=0, keyable=True, name='toeRoll')
        heel_roll = rAttr.Attribute(node=self.main_ctrl.ctrl, type='double', value=0, keyable=True, name='heelRoll')
        bank = rAttr.Attribute(node=self.main_ctrl.ctrl, type='double', value=0, keyable=True, name='bank')

        roll_cnd = mc.createNode('condition', name=self.base_name + '_roll_CND')
        roll_pma = mc.createNode('plusMinusAverage', name=self.base_name + '_roll_PMA')
        ball_mdl = mc.createNode('multDoubleLinear', name=self.base_name + '_roll_MDL')
        toe_mdl = mc.createNode('multDoubleLinear', name=self.base_name + '_toe_MDL')
        toe_adl = mc.createNode('addDoubleLinear', name=self.base_name + '_toe_ADL')
        bank_cnd = mc.createNode('condition', name=self.base_name + '_bank_CND')
        
        roll_cnd2 = mc.createNode('condition', name=self.base_name + '_roll2_CND')
        roll_mdl2 = mc.createNode('multDoubleLinear', name=self.base_name + '_roll2_MDL')

        mc.setAttr(ball_mdl + '.input2', -1)
        mc.setAttr(toe_mdl + '.input2', -1)
        mc.setAttr(roll_cnd + '.operation', 4)
        mc.setAttr(roll_pma + '.operation', 2)
        mc.setAttr(bank_cnd + '.operation', 2)
        mc.setAttr(bank_cnd + '.colorIfFalseG', 0)

        mc.setAttr(roll_cnd2 + '.operation', 4)
        mc.setAttr(roll_mdl2 + '.input2', -1)

        # roll
        mc.connectAttr(roll.attr, roll_cnd + '.firstTerm')
        mc.connectAttr(roll.attr, roll_cnd + '.colorIfTrueR')
        mc.connectAttr(roll.attr, roll_pma + '.input1D[0]')
        mc.connectAttr(roll_max.attr, roll_cnd + '.secondTerm')
        mc.connectAttr(roll_max.attr, roll_cnd + '.colorIfFalseR')
        mc.connectAttr(roll_max.attr, roll_pma + '.input1D[1]')
        mc.connectAttr(roll_pma + '.output1D', roll_cnd + '.colorIfFalseG')
        mc.connectAttr(roll_cnd + '.outColorR', ball_mdl + '.input1')
        mc.connectAttr(roll_cnd + '.outColorG', toe_adl + '.input1')
        mc.connectAttr(toe_roll.attr, toe_adl + '.input2')
        mc.connectAttr(toe_adl + '.output', toe_mdl + '.input1')

        mc.connectAttr(roll.attr, roll_cnd2 + '.firstTerm')
        mc.connectAttr(roll.attr, roll_cnd2 + '.colorIfTrueR')
        mc.connectAttr(roll_cnd2 + '.outColorR', roll_mdl2 + '.input1')
        mc.connectAttr(roll_mdl2 + '.output', self.toe_ctrl.group_list[1] + '.rotateX')

        # bank
        mc.connectAttr(bank.attr, bank_cnd + '.firstTerm')
        mc.connectAttr(bank.attr, bank_cnd + '.colorIfFalseR')
        mc.connectAttr(bank.attr, bank_cnd + '.colorIfTrueG')

        # drive
        mc.connectAttr(ball_mdl + '.output', self.ball_ctrl.group_list[1] + '.rotateX')
        mc.connectAttr(toe_mdl + '.output', self.toe_piv.group_list[1] + '.rotateX')
        mc.connectAttr(heel_roll.attr, self.heel_piv.group_list[1] + '.rotateX')

        if self.side == 'L':
            mc.connectAttr(bank_cnd + '.outColorR', self.out_piv.group_list[1] + '.rotateZ')
            mc.connectAttr(bank_cnd + '.outColorG', self.in_piv.group_list[1] + '.rotateZ')
        else:
            mc.setAttr(bank_cnd + '.operation', 4)
            in_mdl = mc.createNode('multDoubleLinear', name=self.base_name + '_bank_in_MDL')
            out_mdl = mc.createNode('multDoubleLinear', name=self.base_name + '_bank_out_MDL')
            mc.setAttr(in_mdl + '.input2', -1)
            mc.setAttr(out_mdl + '.input2', -1)
            mc.connectAttr(bank_cnd + '.outColorG', in_mdl + '.input1')
            mc.connectAttr(bank_cnd + '.outColorR', out_mdl + '.input1')
            mc.connectAttr(in_mdl + '.output', self.out_piv.group_list[1] + '.rotateZ')
            mc.connectAttr(out_mdl + '.output', self.in_piv.group_list[1] + '.rotateZ')

    def skeleton(self):
        foot_chain = rChain.Chain(transform_list=self.blend_chain.joints, side=self.side, suffix='JNT', name=self.part)
        foot_chain.create_from_transforms(parent=self.skel)

        self.bind_joints = foot_chain.joints
        self.tag_bind_joints(self.bind_joints[:-1])

    def add_plugs(self):
        rAttr.Attribute(node=self.part_grp, type='plug', value=['mc.ls("leg_' + self.side + '_??_JNT")[-1]'], name='skeletonPlugs', children_name=[self.bind_joints[0]])

        driver_list = ['leg_' + self.side + '_03_switch_JNT','root_02_M_CTRL']
        driven_list = [self.base_name + '_01_switch_JNT', self.base_name + '_01_CTRL_CNST_GRP']
        rAttr.Attribute(node=self.part_grp, type='plug', value=driver_list, name='pocRigPlugs', children_name=driven_list)

        driver_list = ['leg_' + self.side + '_02_fk_CTRL']
        driven_list = [self.base_name + '_01_fk_CTRL_CNST_GRP']
        rAttr.Attribute(node=self.part_grp, type='plug', value=driver_list, name='pacRigPlugs', children_name=driven_list)

        # driver_list = ['root_02_M_CTRL']
        # driven_list = [self.base_name + '_IK_MAIN_CTRL_CNST_GRP']
        # rAttr.Attribute(node=self.part_grp, type='plug', value=driver_list, name='pocRigPlugs', children_name=driven_list)

        delete_list = [self.base_name + '_01_translate_BCN']
        rAttr.Attribute(node=self.part_grp, type='plug', value=[' '.join(delete_list)], name='deleteRigPlugs', children_name=['deleteNodes'])

        target_list = ['CHAR',
                       'global_M_CTRL',
                       'root_02_M_CTRL',
                       'COG_M_CTRL',
                       'leg_'+ self.side +'_IK_BASE_CTRL',
                       '2']
        name_list = ['world', 'global', 'root', 'hip', 'leg', 'default_value']
        rAttr.Attribute(node=self.part_grp, type='plug', value=target_list, name=self.main_ctrl.ctrl + '_parent', children_name=name_list)

        switch_attr = 'leg' + self.side + '_IKFK'
        rAttr.Attribute(node=self.part_grp, type='plug', value=[switch_attr], name='switchRigPlugs', children_name=['ikFkSwitch'])
