import maya.cmds as mc
import json, os
from importlib import reload

import rjg.UI.build_script as rBuildScript
reload(rBuildScript)

def launch_build_ui(title):
    window_id = 'build_id'
    if mc.window(window_id, exists=True):
        mc.deleteUI(window_id)
        
    mc.window(window_id, title=title, sizeable=False, resizeToFitChildren=True)
    
    mc.rowColumnLayout(numberOfColumns=4, columnWidth=[(1, 75), (2, 100), (3, 600), (3, 60)], columnOffset=[(1, 'right', 3)])
    
    mc.text(label='Model')
    mc.separator(h=10, style='none')
    model_path = mc.textField()
    mc.button(label='Search', command=lambda _:mc.textField(model_path, e=True, text=(mc.fileDialog2(fm=1, dialogStyle=2)[0])))

    mc.text(label='Guides')
    mc.separator(h=10, style='none')
    guide_path = mc.textField()
    mc.button(label='Search', command=lambda _:mc.textField(guide_path, e=True, text=(mc.fileDialog2(fm=1, dialogStyle=2)[0])))

    sr = mc.radioCollection()
    mc.text(label='Skin Weights')
    skin_d = mc.radioButton(label='Default', select=True, onCommand=lambda _:sd_on(), offCommand=lambda _:sd_off())
    skin_path = mc.textField(enable=False)
    skin_search = mc.button(label='Search', enable=False, command=lambda _:mc.textField(skin_path, e=True, text=(mc.fileDialog2(fm=1, dialogStyle=2)[0])))
    mc.separator(h=10, style='none')
    skin_r = mc.radioButton(label='Read')
    mc.separator(h=10, style='none')
    mc.separator(h=10, style='none')
    mc.separator(h=10, style='none')
    skin_w = mc.radioButton(label='Write')
    mc.separator(h=10, style='none')
    mc.separator(h=10, style='none')
    def sd_on():
        mc.button(skin_search, e=True, enable=False)
        mc.textField(skin_path, e=True, enable=False)
    def sd_off():
        mc.button(skin_search, e=True, enable=True)
        mc.textField(skin_path, e=True, enable=True)
    
    cr = mc.radioCollection()
    mc.text(label='Curve Shapes')
    curve_d = mc.radioButton(label='Default', select=True, onCommand=lambda _:cd_on(), offCommand=lambda _:cd_off())
    curve_path = mc.textField(enable=False)
    curve_search = mc.button(label='Search', enable=False, command=lambda _:mc.textField(curve_path, e=True, text=(mc.fileDialog2(fm=1, dialogStyle=2)[0])))
    mc.separator(h=10, style='none')
    curve_r = mc.radioButton(label='Read')
    mc.separator(h=10, style='none')
    mc.separator(h=10, style='none')
    mc.separator(h=10, style='none')
    curve_w = mc.radioButton(label='Write')
    mc.separator(h=10, style='none')
    mc.separator(h=10, style='none')
    def cd_on():
        mc.button(curve_search, e=True, enable=False)
        mc.textField(curve_path, e=True, enable=False)
    def cd_off():
        mc.button(curve_search, e=True, enable=True)
        mc.textField(curve_path, e=True, enable=True)

    mc.separator(h=10, style='none')
    mc.separator(h=10, style='none')
    mc.separator(h=10, style='none')
    mc.separator(h=10, style='none')

    mc.separator(h=10, style='none')
    mc.separator(h=10, style='none')
    mc.button(label='Build', command=lambda _:build(model_path, guide_path, [skin_d, skin_r, skin_w], skin_path, [curve_d, curve_r, curve_w], curve_path))
    mc.button(label='Close', command=lambda _:mc.deleteUI(window_id))
    
    mc.showWindow()
    
def build(model_path, guide_path, skin_flags, skin_path, curve_flags, curve_path):
    model_path = mc.textField(model_path, q=True, tx=True)
    guide_path = mc.textField(guide_path, q=True, tx=True)
    skin_path = mc.textField(skin_path, q=True, tx=True)
    curve_path = mc.textField(curve_path, q=True, tx=True)
    skin_d = True if mc.radioButton(skin_flags[0], q=True, select=True) else False
    skin_r = True if mc.radioButton(skin_flags[1], q=True, select=True) else False
    skin_w = True if mc.radioButton(skin_flags[2], q=True, select=True) else False
    curve_d = True if mc.radioButton(curve_flags[0], q=True, select=True) else False
    curve_r = True if mc.radioButton(curve_flags[1], q=True, select=True) else False
    curve_w = True if mc.radioButton(curve_flags[2], q=True, select=True) else False
    
    if model_path == '' or guide_path == '':
        mc.error('Please specify both model and guide paths.')
    if (skin_r or skin_w) and skin_path == '':
        mc.error('Please specify skin path or use default skin')
    if (curve_r or curve_w) and curve_path == '':
        mc.error('Please specify curve path or use default curves')
    
    info_dict = {}
    info_dict['model_path'] = model_path
    info_dict['guide_path'] = guide_path
    info_dict['skin'] = [skin_d, skin_r, skin_w]
    info_dict['skin_path'] = skin_path
    info_dict['curve'] = [curve_d, curve_r, curve_w]
    info_dict['curve_path'] = curve_path
    
    
    dump = json.dumps(info_dict, indent=4)
    
    # save inputs to json for next time window is opened
    '''
    model_path_div = model_path.split('/')
    path = model_path_div[:-1]
    file = model_path_div[-1].split('.')[0] + '_UIinfo.json'
    path.append(file)
    path = '/'.join(path)
    
    file = open(path, 'w')
    file.write(dump)
    file.close()
    '''
    
    rBuildScript.build(info_dict)


launch_build_ui('rjg')