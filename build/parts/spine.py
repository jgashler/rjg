import maya.cmds as mc
from importlib import reload

import rjg.build.rigModule as rModule
import rjg.build.chain as rChain
import rjg.build.spline as rSpline
import rjg.libs.control.ctrl as rCtrl
import rjg.libs.attribute as rAttr

reload(rModule)
reload(rChain)
reload(rSpline)
reload(rCtrl)
reload(rAttr)

class Spine(rModule.RigModule, rSpline.Spline):
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=None, joint_num=5, mid_ctrl=True,
                 local_ctrl=False, stretchy=True, aim_vector=(0, 1, 0), up_vector=(0, 0, 1), world_up_vector=(0, 0, 1), 
                 fk_offset=False, model_path=None, guide_path=None):
        super().__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale,
                                    model_path=model_path, guide_path=guide_path)
        
        self.__dict__.update(locals())

        self.base_name = self.part + '_' + self.side
        self.pad = len(str(self.joint_num)) + 1

        self.create_module()

    def create_module(self):
        super().create_module()

        self.build_spline_curve()
        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()

    def control_rig(self):
        # create and parent controls
        self.build_spline_ctrls()

        # build fk controls
        fk_chain = rChain.Chain(side=self.side, suffix='ctrl_JNT', name=self.part)
        fk_chain.create_from_curve(joint_num=4, curve=self.curve, stretch=None)

        self.fk_ctrl_list = []
        par = None
        for i, jnt in enumerate(fk_chain.joints[:-1]):
            name_list = [self.part, str(i + 1).zfill(2), 'FK']
            ctrl_name = '_'.join(name_list)
            if i == 0:
                shape = 'square'
            else:
                shape = 'square'
            fk_ctrl = rCtrl.Control(parent=par, shape=shape, side=self.side, suffix='CTRL',
                                     name=ctrl_name, axis='y', group_type='main', rig_type='fk', 
                                     translate=jnt, rotate=jnt, ctrl_scale=self.ctrl_scale)
            self.attr_util.lock_and_hide(node=fk_ctrl.ctrl, translate=False, rotate=False)
            par = fk_ctrl.ctrl
            self.fk_ctrl_list.append(fk_ctrl)

        # clean up and organize
        mc.delete(fk_chain.joints[0])
        mc.parent(self.curve_ctrls, self.fk_ctrl_list[0].top, self.control_grp)

    def output_rig(self):
        # build spline joints
        self.build_spline_chain(scale_attr=self.global_scale)

        # build joints to bind the curve to
        c_jnt_grp = mc.group(empty=True, parent=self.module_grp, name=self.base_name + '_curve_bind_JNT_GRP')
        base_jnt = mc.joint(c_jnt_grp, name=self.base_ctrl.ctrl.replace('CTRL', 'JNT'))
        tip_jnt = mc.joint(c_jnt_grp, name=self.tip_ctrl.ctrl.replace('CTRL', 'JNT'))

        mc.matchTransform(base_jnt, self.spline_joints[0])
        mc.matchTransform(tip_jnt, self.spline_joints[-1])
        mc.parentConstraint(self.base_driver, base_jnt, maintainOffset=True)
        mc.parentConstraint(self.tip_driver, tip_jnt, maintainOffset=True)
        mc.parentConstraint(self.fk_ctrl_list[-1].ctrl, self.tip_ctrl.top, maintainOffset=True)

        if self.mid_ctrl:
            blend = rAttr.Attribute(node=self.mid_01_ctrl.ctrl, type='double', value=1, min=0, max=1, keyable=True, name='blendBetween')
            mid_jnt = mc.joint(c_jnt_grp, name=self.mid_01_ctrl.ctrl.replace('CTRL', 'JNT'))
            mc.parentConstraint(self.mid_02_ctrl.ctrl, mid_jnt, maintainOffset=False)

            # blend locator between start and end
            mid_loc = mc.spaceLocator(name=mid_jnt.replace('JNT', 'LOC'))[0]
            mc.matchTransform(mid_loc, mid_jnt)
            mc.pointConstraint(base_jnt, tip_jnt, mid_loc, maintainOffset=True)
            aim = mc.aimConstraint(tip_jnt, mid_loc, aimVector=(0, 1, 0), upVector=(0, 0, 1), worldUpType='vector',
                                     worldUpVector=(0, 0, 1), maintainOffset=True)[0]
            b_vp = mc.createNode('vectorProduct', name=base_jnt.replace('JNT', 'VP'))
            t_vp = mc.createNode('vectorProduct', name=tip_jnt.replace('JNT', 'VP'))
            pma = mc.createNode('plusMinusAverage', name=mid_jnt.replace('JNT', 'PMA'))
            rev = mc.createNode('reverse', name=mid_jnt.replace('JNT', 'REV'))
            mc.connectAttr(base_jnt + '.worldMatrix', b_vp + '.matrix')
            mc.connectAttr(tip_jnt + '.worldMatrix', t_vp + '.matrix')
            mc.connectAttr(b_vp + '.output', pma + '.input3D[0]')
            mc.connectAttr(t_vp + '.output', pma + '.input3D[1]')
            mc.connectAttr(pma + '.output3D', aim + '.worldUpVector')
            mc.setAttr(b_vp + '.input1Z', 1)
            mc.setAttr(t_vp + '.input1Z', 1)
            mc.setAttr(b_vp + '.operation', 3)
            mc.setAttr(t_vp + '.operation', 3)
            mc.setAttr(pma + '.operation', 3)

            pac = mc.parentConstraint(self.fk_ctrl_list[1].ctrl, mid_loc, self.mid_01_ctrl.top, maintainOffset=True)[0]
            wal = mc.parentConstraint(pac, query=True, weightAliasList=True)
            mc.connectAttr(blend.attr, rev + '.inputX')
            mc.connectAttr(rev + '.outputX', pac + '.' + wal[0])
            mc.connectAttr(blend.attr, pac + '.' + wal[1])

            mc.parent(mid_loc, self.loc_grp)
            mc.parent(self.loc_grp, self.module_grp)

        # bind curve to control joint
        bind_list = mc.listRelatives(c_jnt_grp) + [self.curve]
        mc.skinCluster(bind_list, toSelectedBones=True, name=self.curve.replace('CRV', 'SKC'))

        # build spline ik handle
        self.build_spline_ikh()
        ikh_grp = mc.group(self.spline_ikh, self.curve, parent=self.module_grp, name=self.base_name + '_spline_IKH_GRP')
        mc.setAttr(ikh_grp + '.inheritsTransform', 0)
        mc.group(self.spline_joints[0], parent=self.module_grp, name=self.base_name + '_driver_JNT_GRP')

        # setup advanced twist
        mc.setAttr(self.spline_ikh + '.dTwistControlEnable', 1)
        mc.setAttr(self.spline_ikh + '.dWorldUpType', 4)
        mc.setAttr(self.spline_ikh + '.dForwardAxis', 2)
        mc.setAttr(self.spline_ikh + '.dWorldUpAxis', 3)
        mc.setAttr(self.spline_ikh + '.dTwistControlEnable', 1)
        mc.setAttr(self.spline_ikh + '.dWorldUpVector', 0, 0, 1)
        mc.setAttr(self.spline_ikh + '.dWorldUpVectorEnd', 0, 0, 1)
        mc.connectAttr(base_jnt + '.worldMatrix[0]', self.spline_ikh + '.dWorldUpMatrix')
        mc.connectAttr(tip_jnt + '.worldMatrix[0]', self.spline_ikh + '.dWorldUpMatrixEnd')

    def skeleton(self):
        spine_chain = rChain.Chain(transform_list=self.spline_joints, side=self.side, suffix='JNT', name=self.part)
        spine_chain.create_from_transforms(parent=self.skel)
        self.bind_joints = spine_chain.joints

        self.tag_bind_joints(self.bind_joints[:-1])

    def add_plugs(self):
        # add skeleton plugs
        rAttr.Attribute(node=self.part_grp, type='plug',
                         value=['hip_M_JNT'], name='skeletonPlugs',
                         children_name=[self.bind_joints[0]])

        # add parentConstraint rig plugs
        driver_list = ['waist_M_CTRL',
                       'COG_M_CTRL',
                       'chest_M_02_CTRL']
        driven_list = [self.base_name + '_base_CTRL_CNST_GRP',
                       self.base_name[:-2] + '_01_FK_M_CTRL_CNST_GRP',
                       self.base_name + '_tip_CTRL_CNST_GRP']
        rAttr.Attribute(node=self.part_grp, type='plug',
                         value=driver_list, name='pacRigPlugs',
                         children_name=driven_list)

        # add hide rig plugs
        hide_list = [self.base_name + '_base_CTRL_CNST_GRP',
                     self.base_name + '_tip_CTRL_CNST_GRP']
        rAttr.Attribute(node=self.part_grp, type='plug',
                         value=[' '.join(hide_list)], name='hideRigPlugs',
                         children_name=['hideNodes'])