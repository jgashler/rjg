import maya.cmds as mc
from importlib import reload
import json
import os

import rjg.libs.common as rCommon
reload(rCommon)

SHAPE_DIR = os.path.dirname(os.path.realpath(__file__)) + "\shapes"

'''
shapes to add to library

2D: 3-arrow, IK, FK, pentagon, hexagon
3D: 3-pyramid, tri-prism, cylinder?, 3D-circle, 3D-square, 
'''

class Draw:
    def __init__(self, curve=None) -> None:
        if curve:
            self.curve = rCommon.get_transform(curve)
        elif len(mc.ls(selection=True)):
            self.curve = rCommon.get_transform(mc.ls(selection=True)[0])
        else:
            self.curve = None

        self.color_dict = {'red' : [1, 0, 0],
                           'green' : [0, 1, 0],
                           'blue' : [0, 0, 1],
                           'yellow' : [1, 1, 0],
                           'magenta' : [1, 0, 1],
                           'cyan' : [0, 1, 1],
                           'black' : [0, 0, 0],
                           'white' : [1, 1, 1],
                           'grey25' : [.25, .25, .25],
                           'grey50' : [.5, .5, .5],
                           'grey75' : [.75, .75, .75],
                           'orange' : [1, .5, 0],
                           'light_blue' : [0, .5, 1],
                           'purple' : [.35, 0, .35],
                           'brown' : [.65, .16, .16]}



    '''
    create a curve from the library to be used as a control

    param name: name of created control
    param shape: shape to draw from library
    axis: axis along which to draw the control shape
    scale: size of control
    '''
    def create_curve(self, name=None, shape='circle', color=None, axis='y', scale=1):
        file_path = "{}/{}".format(SHAPE_DIR, shape)
        if os.path.isfile(file_path):
            json_file = open(file_path, 'r')
            json_data = json_file.read()
            curve_dict = json.loads(json_data)
        else:
            mc.error("Shape does not exist in library. You must write shape to library before creating.")

        if not name:
            name = shape + '1'
        for i, shp in enumerate(curve_dict):
            info = curve_dict[shp]
            point_info = []
            for point_list in info['cv_pose']:
                point = [p * scale for p in point_list]
                point_info.append(point)
            if i == 0:
                self.curve = mc.curve(point=point_info, degree=info['degree'], name=name)
                crv_shape = rCommon.get_shapes(self.curve)[0]
            else:
                child_crv = mc.curve(point=point_info, degree=info['degree'])
                crv_shape = rCommon.get_shapes(child_crv)[0]
                mc.parent(crv_shape, self.curve, shape=True, relative=True)
                mc.delete(child_crv)
            
            if info['form'] >= 1:
                mc.closeCurve(crv_shape, constructionHistory=False, preserveShape=0, replaceOriginal=True)

        curve_shapes = rCommon.get_shapes(self.curve)
        for i, shp in enumerate(curve_shapes):
            if i == 0:
                mc.rename(shp, self.curve + "Shape")
            else:
                mc.rename(shp, self.curve + "{}_{}".format(self.curve, i))

        if axis != 'y':
            self.set_axis(axis)

        if color:
            print("coloring " + color)
            self.color_curve(self.curve, color)

    def color_curve(self, curve, color):
        if isinstance(color, tuple) or isinstance(color, list):
            if len(color) == 3:
                mc.color(curve, rgb=color)
            else:
                mc.error('Color must be in 0-1 RGB format, i.e. [1, 0, 0].')

        elif isinstance(color, str):
            if color in self.color_dict:
                mc.color(curve, rgb=self.color_dict[color])
            else:
                mc.error("Color '" + color + "' not found in color_dict.")

        else:
            mc.error("Unable to change control color. Please enter 0-1 RGB value as list, or a string containing color name.")


    '''
    saves curve to shapes library

    param control: control/curve to be saved to library (can be selection)
    param name: name under which to save the curve in the library
    param force: if true, will guarantee to overwrite existing shape with same name, otherwise will not overwrite
    '''
    def write_curve(self, control=None, name=None, force=False):
        if control:
            self.curve = rCommon.get_transform(control)
        elif len(mc.ls(selection=True)):
            sel = mc.ls(selection=True)
            self.curve = rCommon.get_transform(sel[0])
        elif self.curve:
            pass
        else:
            mc.error("Please define or select a curve to write.")

        if not name:
            name = self.curve
        
        curve_data = self.get_curve_info(self.curve)

        json_path = "{}/{}".format(SHAPE_DIR, name)
        json_dump = json.dumps(curve_data, indent=4)

        if force or os.path.isfile(json_path) == False:
            json_file = open(json_path, "w")
            json_file.write(json_dump)
            json_file.close()
        else:
            mc.error("The shape you are trying to write already exists. Either change the intended name, delete the existing file, or use the force flag.")


    '''
    gets useful information about a curve to store and recreate later

    param curve: name of control/curve to be copied to dictionary

    returns: a dictionary with all curve data relevant to the selected control
    '''
    def get_curve_info(self, curve=None):
        if not curve:
            curve = self.curve

        self.curve_dict = {}
        for crv in rCommon.get_shapes(curve):
            min_value = mc.getAttr(crv + ".minValue")
            max_value = mc.getAttr(crv + ".maxValue")
            spans = mc.getAttr(crv + ".spans")
            degree = mc.getAttr(crv + ".degree")
            form = mc.getAttr(crv + ".form")
            cv_len = len(mc.ls(crv + '.cv[*]', flatten=True))
            cv_pose = self.get_cv_position(crv, cv_len)

            curve_info = {'min': min_value,
                          'max': max_value,
                          'spans': spans,
                          'degree': degree,
                          'form': form,
                          'cv_len': cv_len,
                          'cv_pose': cv_pose}
            self.curve_dict[crv] = curve_info

        return self.curve_dict


    '''
    creates and returns a list of world space points from all control vertices of a curve

    param curve: curve to retrieve cv positions from
    param cv_len: number of cv's on the curve

    returns: list of cv positions
    '''
    def get_cv_position(self, curve, cv_len):
        cv_pose = []
        for i in range(cv_len):
            cv_pos = mc.xform("{}.cv[{}]".format(curve, i), query=True, objectSpace=True, translation=True)
            cv_pose.append(cv_pos)
        return cv_pose

    '''
    used to combine curves under a single transform
    
    param curve: main control that other curves will be parented under
    param shapes: a list of other shapes to combine under param curve
    '''
    def combine_curves(self, curve=None, shapes=None):
        if not curve:
            curve = self.curve
        mc.makeIdentity(curve, apply=True)

        if not shapes:
            shapes = mc.ls(selection=True)
        
        all_shapes = []
        for shape in shapes:
            shape_list = rCommon.get_shapes(shape)
            if shape_list:
                all_shapes += shape_list

        for shape in all_shapes:
            transform = mc.listRelatives(shape, parent=True)
            mc.makeIdentity(transform, apply=True)
            if mc.listRelatives(shape, parent=True)[0] == self.curve:
                continue
            mc.parent(shape, curve, shape=True, relative=True)
            if not mc.listRelatives(transform, allDescendents=True):
                mc.delete(transform)

    '''
    orients a control curve after it has been created

    param axis: primary axis for the control
    '''
    def set_axis(self, axis='y'):
        axis_dict = {'x': [0, 0, -90],
                     '-x': [0, 0, 90],
                     'y': [0, 0, 0],
                     '-y': [0, 0, 180],
                     'z': [90, 0, 0],
                     '-z': [-90, 0, 0]
                    }
        
        mc.setAttr(self.curve + ".rotate", *axis_dict[axis])
        mc.refresh()
        mc.makeIdentity(self.curve, apply=True)