import maya.cmds as mc
from importlib import reload

class Group:
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

    def get_node_list(self, nodes):
        if isinstance(nodes, list):
            return nodes
        else:
            nodes = [nodes]
            return nodes