import maya.cmds as mc
from importlib import reload

class Attribute:
    def __init__(self, add=True, type=None, node=None, name=None, value=None, lock=False):
        self.type = type
        self.node = node
        self.name = name
        self.value = value
        self.lock = lock

        if self.name and self.node:
            self.attr = self.node + '.' + self.name
        
        if add:
            if not self.type:
                mc.error("Must define type when adding attributes.")
            self.add_attr()

    def add_attr(self):
        self.attr = self.node + '.' + self.name
        type_dict = {'string' : self.add_string}
        type_dict[self.type]()

    def add_string(self):
        mc.addAttr(self.node, longName=self.name, dataType='string')
        mc.setAttr(self.attr, self.value, type='string')