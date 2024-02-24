import maya.cmds as mc
import json, os
from importlib import reload

import rjg.libs.control.ctrl as rCtrl
reload(rCtrl)

def write_ctrls(directory, name='control_curves', force=False):
    curve_data = {}
    for c_dict in mc.ls('*.ctrlDict'):
        ctrl_name = c_dict.split('.')[0]
        ctrl = rCtrl.Control(ctrl=ctrl_name)
        info = ctrl.get_curve_info()
        curve_data[ctrl_name] = info

    path = '{}/{}.json'.format(directory, name)
    dump = json.dumps(curve_data, indent=4)

    if force or os.path.isfile(path) == False:
        file = open(path, 'w')
        file.write(dump)
        file.close()
    else:
        mc.error('The curve data you are trying to save already exist in the specified directory at {}. Please choose a different directory or set the force flag to True.'.format(path))
    
def read_ctrls(directory, curve_file='control_curves'):
    path = directory + '/' + curve_file + '.json'
    if os.path.isfile(path):
        file = open(path, 'r')
        curve_data = json.loads(file.read())
    else:
        mc.error('Curves file {} does not exist.'.format(path))

    for info in curve_data.values():
        for shape in info:
            if mc.objExists(shape):
                for i, pos in enumerate(info[shape]['cv_pose']):
                    mc.xform('{}.cv[{}]'.format(shape, i), objectSpace=True, translation=pos)
