import maya.cmds as mc

try:
    from PySide6 import QtWidgets, QtCore
    from PySide6.QtWidgets import QDialog
except ImportError:
    from PySide2 import QtWidgets, QtCore
    from PySide2.QtWidgets import QDialog

import maya.OpenMayaUI as omui
try:
    from shiboken6 import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance

def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def flip_arm():
    clav = 'LeftShoulder'
    if mc.objExists('RightShoulder'):
        mc.delete('RightShoulder')
    mc.select(clav)
    mc.mirrorJoint(mirrorYZ=True, mirrorBehavior=True, searchReplace=('Left', 'Right'))

def flip_legs():
    hip = 'LeftUpLeg'
    parent = mc.listRelatives('LeftFoot', parent=True)
    if parent and parent[0] == 'LeftLeg':
        print("LeftFoot is directly parented to LeftLeg")
        mc.parent("LeftFoot", 'Hips')
    if mc.objExists('RightUpLeg'):
        mc.delete('RightUpLeg')
        
    mc.select(hip)
    mc.mirrorJoint(mirrorYZ=True, mirrorBehavior=True, searchReplace=('Left', 'Right'))

def flip_feet():
    foot = 'LeftFoot'
    if mc.objExists('RightFoot'):
        mc.delete('RightFoot')
    mc.select(foot)
    mc.mirrorJoint(mirrorYZ=True, mirrorBehavior=False, searchReplace=('Left', 'Right'))
    rename_map = {
            'LeftHeelPiv1': 'RightHeelPiv',
            'LeftIn1': 'RightIn',
            'LeftOut1': 'RightOut',
            'LeftToePiv1': 'RightToePiv'
        }

    for old_name, new_name in rename_map.items():
        if mc.objExists(old_name):
            mc.rename(old_name, new_name)


def flip_ue():
    Bigjoints = ['Leftcalf_correctiveRoot', 'Leftlowerarm_correctiveRoot', 'Leftthigh_correctiveRoot', 'Leftupperarm_correctiveRoot']
    subFolders = ['Hands', 'Face']

    for left in Bigjoints:
        right = left.replace('Left', 'Right', 1)  # only replace the first "Left"
        if mc.objExists(right):
            mc.delete(right)
        mc.select(left)
        mc.mirrorJoint(mirrorYZ=True, mirrorBehavior=True, searchReplace=('Left', 'Right'))
    
    for grp in subFolders:
        lefts = []
        all_objects = mc.listRelatives(grp, allDescendents=True, fullPath=False) or []
        for obj in all_objects:
            if obj.startswith('Left'):
                lefts.append(obj)
        for left in lefts:
            right = left.replace('Left', 'Right', 1)  # only replace the first "Left"
            if mc.objExists(right):
                mc.delete(right)
            mc.select(left)
            mc.mirrorJoint(mirrorYZ=True, mirrorBehavior=True, searchReplace=('Left', 'Right'))

class GuideMirrorUi(QtWidgets.QDialog):

    def __init__(self, parent=get_maya_main_window()):
        super(GuideMirrorUi, self).__init__(parent)

        self.setWindowTitle("Mirror Guides Left to Right")
        self.setMinimumWidth(300)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.build_ui()

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Mirror Guides Left to Right")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Checkbox list
        self.arm_checkbox = self.add_checkbox_row(layout, "Arms")
        self.leg_checkbox = self.add_checkbox_row(layout, "Legs")
        self.feet_checkbox = self.add_checkbox_row(layout, "Feet")
        self.ue_checkbox = self.add_checkbox_row(layout, "UE")

        # Mirror button
        self.publish_button = QtWidgets.QPushButton("Mirror")
        self.publish_button.clicked.connect(self.mirror_selected_guides)
        layout.addWidget(self.publish_button)

    def add_checkbox_row(self, parent_layout, label_text):
        layout = QtWidgets.QHBoxLayout()
        checkbox = QtWidgets.QCheckBox()
        label = QtWidgets.QLabel(label_text)
        layout.addWidget(checkbox)
        layout.addWidget(label)
        parent_layout.addLayout(layout)
        return checkbox

    def mirror_selected_guides(self):
        if self.arm_checkbox.isChecked():
            print("Mirroring arms...")
            flip_arm()
        if self.leg_checkbox.isChecked():
            print("Mirroring legs...")
            flip_legs()
        if self.feet_checkbox.isChecked():
            print("Mirroring feet...")
            flip_feet()
        if self.ue_checkbox.isChecked():
            print("Mirroring UE...")
            flip_ue()

# Run the window
def launch_ui():
    # Avoid duplicate windows
    try:
        for widget in QtWidgets.QApplication.allWidgets():
            if isinstance(widget, GuideMirrorUi):
                widget.close()
    except:
        pass

    ui = GuideMirrorUi()
    ui.show()


launch_ui()
                