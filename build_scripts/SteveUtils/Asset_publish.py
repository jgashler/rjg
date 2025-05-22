import maya.cmds as mc
import maya.mel as mel
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

try:
    from modelChecker.modelChecker_UI import UI as MCUI
except TypeError:
    # this external code throws errors when in headless mode
    MCUI = object

import sys, platform
from importlib import reload
from pipe.db import DB
from env_sg import DB_Config

# Define Publisher class first
class Publisher:
    def __init__(self, window_class):
        self._window = window_class()  # Simplified example

# Optional: a simple placeholder dialog for testing
class PublishAssetDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dummy Publish Dialog")

# Now define AssetPublisher
class AssetPublisher(Publisher):
    _override: bool

    def __init__(self) -> None:
        super().__init__(PublishAssetDialog)

    def _prepublish(self) -> bool:
        print("Running prepublish checks...")
        # Simulate a passed check
        self._override = True
        return True

groups = 'G:' if platform.system() == 'Windows' else '/groups'

'''
SUDO CODE
    User Experince 
        Just a button on the assets tab, where they open it there will be a drop down menu (hopefully synced with both shotgrids / add your own) On it they will be able to select the asset, then just hit publish
    We need to set up a UI synced with shotgrid or just managed by me where we can select an asset, then hit publish
    So at the publish button here is the order of operation
    1: Run Checks, need to check with Dallin, but i would like to run checks with the model checker for bad geo, history, transforms,  names, uvs, and materials. On the names, i will be looking for a group called f"{asset}_grp"
        Model Checher Checks
        Check Mat Sets
        Check Geo grp name

    2: once the checks are done, I will want to just save the f'asset_grp' as f'{asset}_publish' in bobo\character\Rigs\Assets_from_Enviroments




'''
def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)



def export_model(asset, production):
    # Construct the object name
    obj_name = f"{asset}_grp"

    # Check if the object exists in the scene
    mc.select(obj_name)
    #print(f"Selected object: {obj_name}")
    if production == 'Bobo':
        mc.file(f"{groups}/bobo/character/Rigs/Assets_from_Enviroments/{asset}_Model.mb", force=True, options="v=0;", type="mayaBinary", exportSelected=True)
    elif production == 'DraggonKisser':
        mc.file(f"{groups}/dragonkisser/character/Rigs/Assets_from_Enviroments/{asset}_Model.mb", force=True, options="v=0;", type="mayaBinary", exportSelected=True)
    elif production == 'Custom':
        mc.file(f"{groups}/bobo/character/Rigs/Custom_rigs_list/{asset}_Model.mb", force=True, options="v=0;", type="mayaBinary", exportSelected=True)
    

def check_grpname(asset):
    #Check if the model group exists
    obj_name = f"{asset}_grp"
    if mc.objExists(obj_name):
        #print(f'{obj_name} is found')
        return True
    else:
        print(f"Warning: Object '{obj_name}' not found in the scene, looking for pipename_grp")
        return False

def run_checks(asset):
    grpname_check = check_grpname(asset)
    # Run other checks as needed

    if grpname_check is True:
        mc.select(f'{asset}_grp')
        publisher = AssetPublisher()
        result = publisher._prepublish()

        if not result:
            print("Model check failed or was cancelled.")
            return False

        print("Model check passed or overridden.")
        return True

    else:
        print("Group name check failed.")
        return False



def get_production(selected_production, conn: DB):
    asset_list = conn.get_asset_name_list(sorted=True)
    production = selected_production
    #production = DropDown with Bobo, DragonKisser, custom
    if production == 'Bobo':
        gotten_list = asset_list  #this is where we get the list from shot grid
    elif production == 'DraggonKisser':
        gotten_list = ['Dragon', 'Chicken']  #this is where we get the list from shot grid
    elif production == 'Custom':
        try:
            custom_list_location = f"{groups}/bobo/character/Rigs/Custom_rigs_list/CustomRig_List.txt"
            with open(custom_list_location, 'r') as file:
                gotten_list = [line.strip() for line in file if line.strip()] 
            #gotten_list = []  #this is where we get a list from my files
        except Exception as e:
            print(f"Error reading file: {e}")
            return []
    print(production, gotten_list)
    return production, gotten_list

def publish(asset, production):
    if run_checks(asset) == True:
        export_model(asset, production)


Productions = ['Select Production', 'Bobo', 'DraggonKisser', 'Custom']

class ModelChecker(MCUI):
    @classmethod
    def get(cls):
        if not cls.qmwInstance or (type(cls.qmwInstance) is not cls):
            cls.qmwInstance = cls()
        return cls.qmwInstance

    def configure(self) -> None:
        self.uncheckAll()
        commands = [
            "crossBorder",
            "hardEdges",
            "lamina",
            "missingUVs",
            "ngons",
            "noneManifoldEdges",
            "onBorder",
            # "selfPenetratingUVs",
            "zeroAreaFaces",
            "zeroLengthEdges",
            "duplicatedNames",
            "namespaces",
            "unfrozenTransforms",
            #"shaders",
            "history",
            "emptyGroups",



        ]
        for cmd in commands:
            self.commandCheckBox[cmd].setChecked(True)

    def check_selected(self) -> bool:
        self.configure()
        self.sanityCheck(["Selection"], True)
        self.createReport("Selection")

        # loop and show UI if anything had an error
        diagnostics = self.contexts["Selection"]["diagnostics"]
        for error in self.commandsList.keys():
            if (error in diagnostics) and len(self.parseErrors(diagnostics[error])):
                self.show_UI()
                return False

        return True

class AssetPublisher(Publisher):
    _override: bool

    def __init__(self) -> None:
        super().__init__(PublishAssetDialog)

    def _prepublish(self) -> bool:
        checker = ModelChecker.get()
        self._override = False
        if not checker.check_selected():
            checker_fail_dialog = MessageDialogCustomButtons(
                self._window,
                "Error. This asset did not pass the model checker. Please "
                "ensure your model meets the requirements set by the model "
                "checker.",
                "Cannot export: Model Checker",
                has_cancel_button=True,
                ok_name="Override",
                cancel_name="Ok",
            )
            self._override = bool(checker_fail_dialog.exec_())
            if not self._override:
                cursor = QTextCursor(checker.reportOutputUI.textCursor())
                cursor.setPosition(0)
                cursor.insertHtml(
                    "<h1>Asset not exported. Please resolve model checks.</h1>"
                )
                return False
        return True

class RiggedModelPublishUI(QtWidgets.QDialog):
    conn_: DB
    
    def __init__(self, parent=get_maya_main_window()):
        super(RiggedModelPublishUI, self).__init__(parent)
        self.setWindowTitle("Rigged Model Publish")
        self.setMinimumWidth(300)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        self.conn_ = DB.Get(DB_Config)

        self.build_ui()
        self.make_connections()
        


    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Title row
        title = QtWidgets.QLabel("Rigged Model Publish")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Production label
        production_label = QtWidgets.QLabel("Production")
        layout.addWidget(production_label)

        # Production dropdown
        self.production_dropdown = QtWidgets.QComboBox()
        self.production_dropdown.addItems(Productions)
        layout.addWidget(self.production_dropdown)

        # Asset label
        asset_label = QtWidgets.QLabel("Asset")
        layout.addWidget(asset_label)

        # Asset dropdown
        self.asset_dropdown = QtWidgets.QComboBox()
        layout.addWidget(self.asset_dropdown)

        # Buttons row
        button_layout = QtWidgets.QHBoxLayout()
        self.check_button = QtWidgets.QPushButton("Check")
        self.publish_button = QtWidgets.QPushButton("Publish")
        button_layout.addWidget(self.check_button)
        button_layout.addWidget(self.publish_button)
        layout.addLayout(button_layout)

    def make_connections(self):
        self.production_dropdown.currentTextChanged.connect(self.update_assets)
        self.check_button.clicked.connect(self.handle_check)
        self.publish_button.clicked.connect(self.handle_publish)

    def update_assets(self, selected_production):
        self.asset_dropdown.clear()
        production_name, gotten_list = get_production(selected_production, self.conn_)
        self.asset_dropdown.addItems(gotten_list)

    def handle_check(self):
        asset = self.asset_dropdown.currentText()
        if asset:
            run_checks(asset)

    def handle_publish(self):
        asset = self.asset_dropdown.currentText()
        production = self.production_dropdown.currentText()
        if asset and production:
            publish(asset, production)

# Run the window
def launch_ui():
    # Avoid duplicate windows
    try:
        for widget in QtWidgets.QApplication.allWidgets():
            if isinstance(widget, RiggedModelPublishUI):
                widget.close()
    except:
        pass

    ui = RiggedModelPublishUI()
    ui.show()


launch_ui()
    



#Test
'''
get_production()
check_grpname('MailBox')
export_model('MailBox', 'Bobo')
'''


