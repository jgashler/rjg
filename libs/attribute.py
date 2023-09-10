import maya.cmds as mc
from importlib import reload

class Attribute:
    def __init__(self, add=True, type=None, node=None, name=None, value=None, lock=False, min=None, max=None, keyable=None):
        self.type = type
        self.node = node
        self.name = name
        self.value = value
        self.min = min
        self.max = max
        self.keyable = keyable
        self.lock = lock

        # not sure if python allows this
        self.hasMinValue = True if min else False
        self.hasMaxValue = True if max else False

        if self.name and self.node:
            self.attr = self.node + '.' + self.name
        
        if add:
            if not self.type:
                mc.error("Must define type when adding attributes.")
            self.add_attr()

    def add_attr(self):
        self.attr = self.node + '.' + self.name
        type_dict = {'string' : self.add_string,
                     'double' : self.add_double,
                     'bool' : self.add_bool}
        type_dict[self.type]()

    def add_string(self):
        mc.addAttr(self.node, longName=self.name, dataType='string')
        mc.setAttr(self.attr, self.value, type='string')

    def add_bool(self):
        mc.addAttr(self.node, attributeType='bool', defaultValue=self.value, keyable=self.keyable, longName=self.name)

    def add_double(self):
        mc.addAttr(self.node, attributeType='double', hasMinValue=self.hasMinValue, hasMaxValue=self.hasMaxValue, defaultValue=self.value, keyable=self.keyable, longName=self.name)