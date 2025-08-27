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
                 group_type='main', rig_type='primary', ctrl_scale=1, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1),
                 color_rgb=None):
        self.group_dict = {
                           "main": ["CNST", "SDK", "OFF"],
                           "offset": ["CNST", "OFF"],
                           "float": ['CNST', 'OFF']
                          }
        self.parent = parent
        self.translate = translate
        self.rotate = rotate
        self.scale = scale
        self.fail = False
        self.color_rgb = color_rgb

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
            try:
                self.get_control()
            except:
                self.fail = True  # for imported parts (props), this trigger will let finalize.py know how to handle things
    '''
    creates a control, adds padding, and sets SRT position, tags control with information
    '''
    def create(self):
        self.create_curve(name=self.ctrl_name, shape=self.shape, axis=self.axis, scale=self.ctrl_scale)
        self.ctrl = self.curve

        if self.color_rgb:
            shapes = mc.listRelatives(self.ctrl, shapes=True, fullPath=True) or []
            for shape in shapes:
                mc.setAttr(shape + ".overrideEnabled", 1)
                mc.setAttr(shape + ".overrideRGBColors", 1)
                mc.setAttr(shape + ".overrideColorRGB", *self.color_rgb)

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
        mc.setAttr(self.ctrl_name + '.v', keyable=False, cb=True)

        mc.setAttr(self.ctrl_name + '.rotateOrder', k=True)

        if self.parent:
            mc.parent(self.top, self.parent)
        self.tag_control()

    '''
    from a control's ctrlDict attribute, regenerate Control object for use in other functions
    '''
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

        self.color_rgb = self.control_dict.get('color_rgb', None)

        if self.side:
            self.ctrl_name = '{}_{}_{}'.format(self.name, self.side, self.suffix)
        else:
            self.ctrl_name = '{}_{}'.format(self.name, self.suffix)

        if self.group_list:
            self.top = self.group_list[-1]
            self.bot = self.group_list[0]

    '''
    adds a tag attribute to the control based on its object attributes. allows it to be turned back into a Control object
    '''
    def tag_control(self):
        self.control_dict = {
                             "shape" : self.shape,
                             "side" : self.side,
                             "suffix" : self.suffix,
                             "name" : self.name,
                             "axis" : self.axis,
                             "rig_groups" : self.group_list,
                             "rig_type" : self.rig_type,
                             "ctrl_scale" : self.ctrl_scale,
                             "color_rgb": self.color_rgb
                            }
        tag_string = str(self.control_dict)

        try:
            rAttr.Attribute(type='string', node=self.ctrl, name='ctrlDict', value=tag_string, lock=True)    
        except:
            rAttr.Attribute(type='string', node=self.ctrl, name='ctrlDict', value='ctrlDict', lock=True)  

    #TODO figure out how to set, query pickwalk targets    
    def tag_as_controller(self, new=True, parent=None, query=False):
        # return info on controller
        if query:
            q_dict = {}
            q_dict['controller'] = mc.getAttr(self.ctrl.message)
            if q_dict['controller']:
                q_dict['parent'] = mc.getAttr(q_dict['controller'] + '.parent')

            return q_dict

        # create new tag
        if new:
            ctrl_tag = mc.createNode('controller', name=self.ctrl + '_TAG')
            mc.connectAttr(self.ctrl + '.message', ctrl_tag + '.controllerObject')

        # get existing tag (for adding a parent)
        else:
            ctrl_tag = mc.getAttr(self.ctrl + '.message')
            if not ctrl_tag:
                mc.error("Tag does not exist")

        # set parent
        if parent:
            mc.connectAttr(parent.ctrl + '.message', ctrl_tag + '.parent')
            
def tag_as_controller(ctrl):
    ctrl_tag = mc.createNode('controller', name=ctrl + '_TAG')
    mc.connectAttr(ctrl + '.message', ctrl_tag + '.controllerObject')
    return ctrl_tag