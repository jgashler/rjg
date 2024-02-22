import maya.cmds as mc
from importlib import reload

import rjg.libs.attribute as rAttr
import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
import rjg.build.guide as rGuide
import rjg.libs.transform as rXform
reload(rAttr)
reload(rChain)
reload(rCtrl)
reload (rGuide)
reload(rXform)

class Spline:
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=1, joint_num=5, mid_ctrl=True, local_ctrl=False, stretchy=True, aim_vector=(0, 1, 0), up_vector=(0, 0, 1), world_up_vector=(0, 0, 1), fk_offset=False):
        self.side = side
        self.part = part
        self.base_name = self.part + '_' + self.side

        self.guide_list = guide_list
        self.ctrl_scale = ctrl_scale
        self.joint_num = joint_num
        self.mid_ctrl = mid_ctrl
        self.local_ctrl = local_ctrl
        self.stretchy = stretchy
        self.aim_vector = aim_vector
        self.up_vector = up_vector
        self.world_up_vector = world_up_vector
        self.fk_offset = fk_offset

        if self.guide_list:
            if not isinstance(self.guide_list, list):
                self.guide_list = [self.guide_list]

    def build_spline(self):
        self.build_spline_curve()
        self.build_spline_ctrls()
        self.build_spline_chain()
        self.build_spline_ikh()

    def build_spline_curve(self):
        point_list = []
        for guide in self.guide_list:
            pos = mc.xform(guide, q=True, ws=True, translation=True)
            point_list.append(pos)

        temp = mc.curve(editPoint=point_list, degree=1, name=self.base_name + "_temp")
        self.curve, bs = mc.fitBspline(temp, constructionHistory=True, tolerance=0.01, name=self.base_name + '_CRV')
        mc.delete(self.curve, constructionHistory=True)
        self.curve = mc.rebuildCurve(self.curve, replaceOriginal=True, rebuildType=0, endKnots=1, keepRange=0, keepControlPoints=False, keepEndPoints=False, keepTangents=False, spans=4, degree=3)[0]
        mc.delete(temp)

    def build_spline_ctrls(self):
        self.attr_util = rAttr.Attribute(add=False)

        self.curve_ctrls = []

        self.base_ctrl = rCtrl.Control(parent=None, shape='cube', side=None, suffix='CTRL', name=self.base_name + '_base', axis='y', group_type='main', rig_type='primary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale)
        self.attr_util.lock_and_hide(node=self.base_ctrl.ctrl, translate=False, rotate=False)
        self.curve_ctrls.append(self.base_ctrl.top)
        self.base_driver = self.base_ctrl.ctrl
        self.base_ctrl.tag_as_controller()

        self.tip_ctrl = rCtrl.Control(parent=None, shape='cube', side=None, suffix='CTRL', name=self.base_name + '_tip', axis='y', group_type='main', rig_type='primary', translate=self.guide_list[-1], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale)
        self.attr_util.lock_and_hide(node=self.tip_ctrl.ctrl, translate=False, rotate=False)
        self.curve_ctrls.append(self.tip_ctrl.top)
        self.tip_driver = self.tip_ctrl.ctrl
        self.tip_ctrl.tag_as_controller()

        if self.local_ctrl:
            self.base_local = rCtrl.Control(parent=self.base_ctrl.ctrl, shape='quad_arrow', side=None, suffix='CTRL', name=self.base_name + '_base_local', axis='y', group_type='main', rig_type='secondary', translate=self.guide_list[0], rotate=self.guide_list[0], ctrl_scale=self.ctrl_scale)
            self.attr_util.lock_and_hide(node=self.base_local.ctrl, translate=False, rotate=False)
            #self.curve_ctrls.append(self.tip_ctrl)
            self.base_driver = self.base_local.ctrl
            self.base_local.tag_as_controller()

            self.tip_local = rCtrl.Control(parent=self.tip_ctrl.ctrl, shape='quad_arrow', side=None, suffix='CTRL', name=self.base_name + '_tip_local', axis='y', group_type='main', rig_type='secondary', translate=self.guide_list[-1], rotate=self.guide_list[-1], ctrl_scale=self.ctrl_scale)
            self.attr_util.lock_and_hide(node=self.tip_local.ctrl, translate=False, rotate=False)
            #self.curve_ctrls.append(self.tip_ctrl)
            self.tip_driver = self.tip_local.ctrl
            self.tip_local.tag_as_controller()

        if self.mid_ctrl:
            pos = rXform.findPosOnCurve(self.curve, 0.5)

            self.mid_01_ctrl = rCtrl.Control(parent=None, shape='circle', side=None, suffix='CTRL', name=self.base_name + '_mid_01', axis='y', group_type='main', rig_type='primary', translate=pos, rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale * 12)
            self.attr_util.lock_and_hide(node=self.mid_01_ctrl.ctrl, translate=False, rotate=False)
            self.curve_ctrls.append(self.mid_01_ctrl.top)

            self.mid_02_ctrl = rCtrl.Control(parent=self.mid_01_ctrl.ctrl, shape='circle', side=None, suffix='CTRL', name=self.base_name + '_mid_02', axis='y', group_type='main', rig_type='primary', translate=pos, rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale * 10)
            self.attr_util.lock_and_hide(node=self.mid_02_ctrl.ctrl, translate=False, rotate=False)
            #self.curve_ctrls.append(self.mid_02_ctrl.top)
            
            # if self.local_ctrl:
            #     self.base_driver = self.base_local.ctrl
            self.mid_01_ctrl.tag_as_controller()
            self.mid_02_ctrl.tag_as_controller()

    def build_spline_chain(self, scale_attr=None):
        if not scale_attr:
            scale_attr = rAttr.Attribute(node=self.base_ctrl.ctrl, type='double', value=1, keyable=True, name='globalScale')

        self.spline_chain = rChain.Chain(side=self.side, suffix='driver_JNT', name=self.part)
        self.spline_chain.create_from_curve(joint_num=self.joint_num, curve=self.curve, aim_vector=self.aim_vector, up_vector=self.up_vector, world_up_vector=self.world_up_vector, stretch=self.stretchy)
        self.spline_joints = self.spline_chain.joints

        if self.local_ctrl:
            mc.matchTransform(self.base_local.top, self.spline_joints[0])
            mc.matchTransform(self.tip_local.top, self.spline_joints[-1])

        if self.stretchy:
            stretch = rAttr.Attribute(node=self.tip_ctrl.ctrl, type='double', value=1, min=0, max=1, keyable=True, name='stretch')

            self.loc_grp = mc.group(empty=True, name=self.base_name + '_driver_LOC_GRP')
            inc = 1 / (self.joint_num - 1)
            par = None

            for i, jnt in enumerate(self.spline_joints):
                pci = mc.createNode("pointOnCurveInfo", name=jnt.replace('JNT', 'PCI'))
                loc = mc.spaceLocator(name=jnt.replace('JNT', 'LOC'))[0]
                mc.setAttr(pci + '.parameter', i * inc)
                mc.connectAttr(self.curve + 'Shape.worldSpace[0]', pci + '.inputCurve')
                mc.connectAttr(pci + '.position', loc + '.translate')
                mc.setAttr(loc + '.inheritsTransform', 0)

                if par:
                    par_loc = mc.listRelatives(self.loc_grp)[-1]
                    rChain.stretch_segment(jnt=par, start=par_loc, end=loc, stretch_driver=stretch.attr, global_scale=scale_attr.attr)

                par = jnt
                mc.parent(loc, self.loc_grp)

        if self.fk_offset:
            ctrl_par = None
            grp_par = None

            self.fk_offset_list = []
            for joint in self.spline_joints:
                fk_name = joint.replace(self.side + '_', '')
                fk_name = fk_name.replace('driver_JNT', 'fk_offset')
                fk_ctrl = rCtrl.Control(parent=ctrl_par, shape='circle', side=self.side, suffix='CTRL', name=fk_name, axis='y', group_type='main', rig_type='fk', translate=(0, 0, 0), rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale)
                self.attr_util.lock_and_hide(node=fk_ctrl.ctrl, translate=False, rotate=False)
                self.fk_offset_list.append(fk_ctrl)
                mc.setAttr(fk_ctrl.top + '.translate', 0, 0, 0)
                mc.setAttr(fk_ctrl.top + '.rotate', 0, 0, 0)
                fk_ctrl.tag_as_controller()

                grp = mc.group(empty=True, name=joint.replace('driver_JNT', 'fk_offset_GRP'))
                pac = mc.parentConstraint(joint, grp, mo=False)[0]
                if grp_par:
                    mc.parent(grp, grp_par)
                else:
                    self.offset_grp = grp
                mc.connectAttr(pac + '.constraintTranslate', fk_ctrl.top + '.translate')
                mc.connectAttr(pac + '.constraintRotate', fk_ctrl.top + '.rotate')

                ctrl_par = fk_ctrl.ctrl
                grp_par = grp

    def build_spline_ikh(self):
        self.spline_ikh = mc.ikHandle(name=self.base_name + '_spline_IKH', startJoint=self.spline_joints[0], endEffector=self.spline_joints[-1], createCurve=False, curve=self.curve, solver='ikSplineSolver')[0]
                