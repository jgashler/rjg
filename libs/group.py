import maya.cmds as mc
from importlib import reload

class Group:

    '''
    takes a list of nodes and adds them to a group with padding

    param nodes: the list of nodes to be grouped
    param pad_name_list: a list of pad names, one hierarchy layer will be created for each one
    param name: name of group
    '''
    def group_by_list(self, nodes, pad_name_list, name=None):
        self.group_list = []
        nodes = self.get_node_list(nodes)

        for node in nodes:
            if not name:
                name = node

            for group_name in pad_name_list[::-1]:
                grp = mc.group(empty=True, name=name + '_' + group_name + "_GRP")
                if group_name != pad_name_list[-1]:
                    mc.parent(self.top, grp)
                else:
                    self.bot = grp

                self.top = grp
                self.group_list.append(grp)
            mc.parent(node, self.bot)
    

    '''
    does the same thing as group_by_list(), but uses numbers as pad names

    param group_num: number of hierarchy layers to add
    '''
    def group_by_int(self, nodes, group_num, name=None):
        self.group_list = []
        nodes = self.get_node_list(nodes)
        num_len = len(str(group_num)) + 1
        for node in nodes:
            if not name:
                name = node

            for i in range(group_num):
                grp = mc.group(empty=True, name=name + "_" + str(i+1).zfill(num_len) + "_OFF_GRP")
                
                if i < 1:
                    self.bot = grp
                else:
                    mc.parent(self.top, grp)
                self.top = grp
                self.group_list.append(grp)

            mc.parent(node, self.bot)    

    '''
    ensures that nodes are a list
    '''
    def get_node_list(self, nodes):
        if isinstance(nodes, list):
            return nodes
        else:
            nodes = [nodes]
            return nodes