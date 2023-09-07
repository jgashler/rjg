import maya.cmds as mc
from importlib import reload
import ast

import rjg.libs.control.draw as rDraw
import rjg.libs.group as rGroup
import rjg.libs.common as rCommon
import rjg.libs.attribute as rAttr
import rjg.libs.transform as rXform
reload(rDraw)
reload(rGroup)
reload(rCommon)
reload(rAttr)
reload(rXform)

class Control(rDraw.Draw, rGroup.Group):
    def __init__(self, ctrl=None, parent=None, shape='circle', side='M', suffix='CTRL', name='default', axis='y', 
                 group_type='main', rig_type='primary', ctrl_scale=1, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1)):
        self.group_dict = {
                           "main": ["CNST", "MOCAP", "SDK", "OFF"],
                           "offset": ["CNST", "OFF"]
                          }
        self.parent = parent
        self.translate = translate
        self.rotate = rotate
        self.scale = scale

        self.ctrl = ctrl
        if not self.ctrl:
            self.shape = shape
            self.side = side
            self.suffix = suffix
            self.name = name
            self.axis = axis
            self.group_type = group_type
            self.rig_type = rig_type
            self.ctrl_scale = ctrl_scale
            if side:
                self.ctrl_name = "{}_{}_{}".format(name, side, suffix)
            else:
                self.ctrl_name = "{}_{}".format(name, suffix)

            self.create()

        else:
            self.get_control()

    def create(self):
        self.create_curve(name=self.ctrl_name, shape=self.shape, axis=self.axis, scale=self.ctrl_scale)
        self.ctrl = self.curve

        if isinstance(self.group_type, str):
            self.group_by_list(nodes=self.ctrl, pad_name_list=self.group_dict[self.group_type], name=self.ctrl_name)

        elif isinstance(self.group_type, list):
            self.group_by_list(nodes=self.ctrl, pad_name_list=self.group_type, name=self.ctrl_name)

        elif isinstance(self.group_type, int):
            self.group_by_int(nodes=self.ctrl, group_num=self.group_type, name=self.ctrl_name)

        else:
            self.group_list=None
            self.top = self.ctrl_name
            self.bot = self.ctrl_name
            mc.warning(self.ctrl_name + " has no padding.")

        rXform.match_pose(node=self.top, translate=self.translate, rotate=self.rotate, scale=self.scale)

        if self.parent:
            mc.parent(self.top, self.parent)
        self.tag_control()


    def get_control(self):
        tag_dict = mc.getAttr(self.ctrl + ".ctrlDict")
        self.control_dict = ast.literal_eval(tag_dict)
        self.curve = self.ctrl
        self.shape = self.control_dict['shape']
        self.side = self.control_dict['side']
        self.suffix = self.control_dict['suffix']
        self.name = self.control_dict['name']
        self.axis = self.control_dict['axis']
        self.group_list = self.control_dict['rig_groups']
        self.rig_type = self.control_dict['rig_type']
        self.ctrl_scale = self.control_dict['ctrl_scale']

        if self.side:
            self.ctrl_name = '{}_{}_{}'.format(self.name, self.side, self.suffix)
        else:
            self.ctrl_name = '{}_{}'.format(self.name, self.suffix)

        if self.group_list:
            self.top = self.group_list[-1]
            self.bot = self.group_list[0]


    def tag_control(self):
        self.control_dict = {
                             "shape" : self.shape,
                             "side" : self.side,
                             "suffix" : self.suffix,
                             "name" : self.name,
                             "axis" : self.axis,
                             "rig_groups" : self.group_list,
                             "rig_type" : self.rig_type,
                             "ctrl_scale" : self.ctrl_scale
                            }
        tag_string = str(self.control_dict)

        rAttr.Attribute(type='string', node=self.ctrl, name='ctrlDict', value=tag_string, lock=True)            