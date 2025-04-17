try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as mc

def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class RibbonUtilsWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(RibbonUtilsWindow, self).__init__(parent)
        self.setWindowTitle("Steve's Ribbon Utils")
        self.setObjectName("ribbonUtilsWindow")
        self.setFixedSize(400, 250)

        # Create a layout for the window
        layout = QtWidgets.QVBoxLayout(self)
        title_label = QtWidgets.QLabel("Steve's Ribbon Utils")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)

        # Convert Edge to Curve Row
        convert_layout = QtWidgets.QHBoxLayout()
        convert_label = QtWidgets.QLabel("Convert Edge to Curve")
        convert_label.setAlignment(QtCore.Qt.AlignCenter)
        convert_layout.addWidget(convert_label)

        convert_button = QtWidgets.QPushButton("Convert")
        convert_button.clicked.connect(self.ConvertToCurve)
        convert_layout.addWidget(convert_button)
        layout.addLayout(convert_layout)

        # Loft Row
        loft_layout = QtWidgets.QHBoxLayout()
        loft_label = QtWidgets.QLabel("Loft")
        loft_label.setAlignment(QtCore.Qt.AlignCenter)
        loft_layout.addWidget(loft_label)

        loft_button = QtWidgets.QPushButton("Loft")
        loft_button.clicked.connect(self.Loft)
        loft_layout.addWidget(loft_button)
        layout.addLayout(loft_layout)

        # Reverse Loft Row
        reverse_loft_layout = QtWidgets.QHBoxLayout()
        reverse_loft_label = QtWidgets.QLabel("Reverse Loft")
        reverse_loft_label.setAlignment(QtCore.Qt.AlignCenter)
        reverse_loft_layout.addWidget(reverse_loft_label)

        reverse_loft_button = QtWidgets.QPushButton("Reverse")
        reverse_loft_button.clicked.connect(self.ReverseLoft)
        reverse_loft_layout.addWidget(reverse_loft_button)
        layout.addLayout(reverse_loft_layout)

         # Temp Skin Row
        temp_skin_layout = QtWidgets.QHBoxLayout()
        temp_skin_label = QtWidgets.QLabel("Temp Skin")
        temp_skin_label.setAlignment(QtCore.Qt.AlignCenter)
        temp_skin_layout.addWidget(temp_skin_label)

        temp_skin_button = QtWidgets.QPushButton("Build Temp Skin")
        temp_skin_button.clicked.connect(self.Build_TempSkin)
        temp_skin_layout.addWidget(temp_skin_button)
        layout.addLayout(temp_skin_layout)

        # Default UVpin Loft Row
        uvpin_label = QtWidgets.QLabel("Default UVpin Loft")
        layout.addWidget(uvpin_label)

        uvpin_layout = QtWidgets.QHBoxLayout()
        self.automatic_checkbox = QtWidgets.QCheckBox("Automatic")
        uvpin_layout.addWidget(self.automatic_checkbox)

        self.uvpin_input = QtWidgets.QLineEdit()
        self.uvpin_input.setPlaceholderText("Enter number")
        uvpin_layout.addWidget(self.uvpin_input)

        layout.addLayout(uvpin_layout)

        # Build Ribbon Row
        build_layout = QtWidgets.QHBoxLayout()
        build_label = QtWidgets.QLabel("Build Ribbon")
        build_label.setAlignment(QtCore.Qt.AlignCenter)
        build_layout.addWidget(build_label)

        build_button = QtWidgets.QPushButton("Build")
        build_button.clicked.connect(self.build_ribbon)
        build_layout.addWidget(build_button)
        layout.addLayout(build_layout)

        # Set the window flags to stay on top
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)

    def ConvertToCurve(self):
        try:
            mc.polyToCurve(form=2, degree=3, conformToSmoothMeshPreview=1)
            print("Converted selected edges to curves.")
        except:
            print("No edges selected.")

    def Loft(self):
        try:
            mc.loft(ch=1, u=1, c=0, ar=1, d=1, ss=1, rn=0, po=0, rsn=True)
            print("Loft operation performed.")
        except:
            print("No curves selected.")

    def ReverseLoft(self):
        try:
            mc.reverseSurface()
            print("Reverse loft operation performed.")
        except:
            print("No surface selected.")





    def Build_TempSkin(self):
        try:
            mc.nurbsToPoly(mnd=1, ch=1, f=3, pt=0, pc=200, chr=0.9, ft=0.01, mel=0.001, d=0.1, ut=1, un=3, vt=1, vn=3, uch=0, ucr=0, cht=0.2, es=0, ntr=0, mrt=0, uss=1)
            print("Temporary skin built successfully.")
        except:
            print("Failed to build temporary skin.")
    
### Micheal's UV PIN Ribbon Code

    def generate_ribbon(
        self,
        nurbs_surface_name: str, 
        number_of_joints: int,
        cyclic: bool = False,
        swap_uv: bool = False,
        local_space: bool = False, 
        control_joints: bool = False, 
        number_of_controls: int = None,
        half_controls: bool = False
        ):
        ribbon_length: float = 2
        surface_shape = cmds.listRelatives(nurbs_surface_name, shapes=True)[0]
        if cmds.nodeType(surface_shape) == "nurbsSurface":
            if swap_uv:
                ribbon_length = cmds.getAttr(str(surface_shape)+".minMaxRangeV")[0][1]
                ribbon_width = cmds.getAttr(str(surface_shape)+".minMaxRangeU")[0][1]
            else:
                ribbon_length = cmds.getAttr(str(surface_shape)+".minMaxRangeU")[0][1]
                ribbon_width = cmds.getAttr(str(surface_shape)+".minMaxRangeV")[0][1]
            if not number_of_controls:
                number_of_controls = int(ribbon_length)
                if half_controls:
                    number_of_controls = int(number_of_controls/2)

            ribbon_object: str = cmds.duplicate(nurbs_surface_name, name=nurbs_surface_name+"_ribbon")[0]
            ribbon_group = cmds.group(ribbon_object, name=ribbon_object+"_GRP")

            if control_joints:
                
                if cyclic:
                    for i in range(number_of_controls):
                        control_spacing: float = (ribbon_length/(number_of_controls))
                        u: float = (control_spacing*i)
                        v: float = ribbon_width/2
                        if swap_uv:
                            position = cmds.pointOnSurface(ribbon_object, position=True, parameterU=v, parameterV=u)
                            print(u,v)
                        else:
                            position = cmds.pointOnSurface(ribbon_object, position=True, parameterU=u, parameterV=v)
                            print(u,v)
                        cmds.select(ribbon_group, replace=True)
                        joint_name = cmds.joint(position=position, radius=1, name=str(ribbon_object)+str(i+1)+"_ControlJoint")
                else:
                    for i in range(number_of_controls + 1):
                        control_spacing: float = (ribbon_length/(number_of_controls))
                        u: float = (control_spacing*i)
                        v: float = ribbon_width/2
                        if swap_uv:
                            position = cmds.pointOnSurface(ribbon_object, position=True, parameterU=v, parameterV=u)
                        else:
                            position = cmds.pointOnSurface(ribbon_object, position=True, parameterU=u, parameterV=v)
                        cmds.select(ribbon_group, replace=True)
                        joint_name = cmds.joint(position=position, radius=1, name=str(ribbon_object)+str(i+1)+"_ControlJoint")

            if cyclic:
                for i in range(number_of_joints):
                    cmds.select(ribbon_group, replace=True)
                    u: float = ((i/(number_of_joints))*ribbon_length)
                    v: float = ribbon_width/2
                    if swap_uv:
                        position = cmds.pointOnSurface(ribbon_object, position=True, parameterU=v, parameterV=u)
                    else:
                        position = cmds.pointOnSurface(ribbon_object, position=True, parameterU=u, parameterV=v)
                    joint_name = cmds.joint(position=position, radius=0.5, name=str(ribbon_object)+"_point"+str(i+1)+"_DEF")
                    cmds.select(ribbon_object+".uv"+"["+str((i/(number_of_joints-2))*2)+"]"+"[0.5]", replace=True)
                    cmds.select(joint_name, add=True)
                    cmds.UVPin()
                    if not local_space:
                        cmds.setAttr(joint_name+".inheritsTransform", 0)
            else:
                for i in range(number_of_joints):
                    cmds.select(ribbon_group, replace=True)
                    u: float = ((i/(number_of_joints-1))*ribbon_length)
                    v: float = ribbon_width/2
                    if swap_uv:
                        position = cmds.pointOnSurface(ribbon_object, position=True, parameterU=v, parameterV=u)
                    else:
                        position = cmds.pointOnSurface(ribbon_object, position=True, parameterU=u, parameterV=v)
                    joint_name = cmds.joint(position=position, radius=0.5, name=str(ribbon_object)+"_point"+str(i+1)+"_DEF")
                    if swap_uv:
                        cmds.select(ribbon_object+".uv"+"["+str(v)+"]"+"["+str(u)+"]", replace=True)
                    else:
                        cmds.select(ribbon_object+".uv"+"["+str(u)+"]"+"["+str(v)+"]", replace=True)
                    cmds.select(joint_name, add=True)
                    cmds.UVPin()
                    if not local_space:
                        cmds.setAttr(joint_name+".inheritsTransform", 0)





    def build_ribbon(self):
        # Get the value from the checkbox and text input
        auto = self.automatic_checkbox.isChecked()
        pin_num = int(self.uvpin_input.text()) if self.uvpin_input.text().isdigit() else 0  # Default to 0 if invalid input

        # Initialize pin_count
        pin_count = pin_num

        if auto:
            # Count the number of CVs on the selected NURBS surface
            selected_objects = mc.ls(selection=True)
            for obj in selected_objects:
                try:
                    # Get the CVs
                    cvs = mc.getAttr(f"{obj}.cv[*][*]")  # This will retrieve all CVs of the NURBS surface
                    cv_count = len(cvs) // 2  # Each CV has X, Y, and Z coordinates
                    print(f"{obj} has {cv_count} control vertices (CVs).")
                    pin_count = cv_count - 2 # Set pin_count based on the CV count
                except:
                    print(f"{obj} is not a NURBS surface.")

        print(pin_count)
        selected_objects = mc.ls(selection=True)
        for obj in selected_objects:
            # Ensure to call the function without conflicting arguments
            self.generate_ribbon(obj, pin_count)








def show_ribbon_utils():
    print("Attempting to show the Ribbon Utils Window...")
    main_window = get_maya_main_window()
    ribbon_utils_window = RibbonUtilsWindow(parent=main_window)
    ribbon_utils_window.setGeometry(1000, 1000, 400, 250)
    ribbon_utils_window.show()
    print("Window should be displayed now.")

# Check if the window is already open, if so, delete it
if mc.window("ribbonUtilsWindow", exists=True):
    mc.deleteUI("ribbonUtilsWindow")

show_ribbon_utils()
