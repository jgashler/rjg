import maya.cmds as mc
from importlib import reload

import rjg.build.rigBase as rBase
import rjg.libs.attribute as rAttr
import rjg.libs.common as rCommon

reload(rBase)
reload(rAttr)
reload(rCommon)

'''
Base class for all buildable parts. Adds to base hierarchy the part hierarchy for modules and controls.
'''
class RigModule(rBase.RigBase):
    def __init__(self, side='M', part='default', guide_list=None, ctrl_scale=None, model_path=None, guide_path=None):
        print("Building " +part)
        super().__init__(model_path=model_path, guide_path=guide_path)

        self.side = side
        self.part = part
        self.guide_list = guide_list
        self.ctrl_scale = ctrl_scale

        if not self.side:
            self.side = 'M'
        if not self.part:
            self.part = 'default'

        self.base_name = '{}_{}'.format(self.part, self.side)

        if self.guide_list:
            if not isinstance(self.guide_list, list):
                guide_list = [guide_list]

    def create_module(self):
        super().create_module()
        self.part_hierarchy()

        # set ctrl_scale to model's bounding box as default
        if not self.ctrl_scale:
            bb = rCommon.get_bounding_box(self.model)
            if abs(bb[0]) > abs(bb[1]):
                scale_factor = abs(bb[0])
            else:
                scale_factor = abs(bb[1])
            self.ctrl_scale=scale_factor

    # creates individual part's hierarchy as a subset of the RIG group created by rigBase
    def part_hierarchy(self):
        self.part_grp = self.rig_group(name=self.base_name, parent=self.rig)                        # part group
        self.module_grp = self.rig_group(name=self.base_name + "_MODULE", parent=self.part_grp)     # module group to contain rig systems
        self.control_grp = self.rig_group(name=self.base_name + "_CONTROL", parent=self.part_grp)   # control group to contain any control curves

        # global scale attribute added to root
        if self.part != 'root':
            try:
                self.global_scale = rAttr.Attribute(node=self.part_grp, type='double', value=1, keyable=True, name='globalScale')
            except Exception as e:
                mc.warning('GlobalScale:', e)
        
    # tag joints to be used for skinning
    def tag_bind_joints(self, joints):
        if not isinstance(joints, list):
            joints = [joints]

        for joint in joints:
            rAttr.Attribute(node=joint, type='bool', value=True, keyable=False, name='bindJoint')
