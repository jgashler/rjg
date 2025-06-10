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

import pathlib

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


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

# --- Production Options ---
Productions = ['Select Production', 'Bobo', 'DraggonKisser', 'Custom']

# --- Dummy DB connection class (replace with your real one) ---

# --- Function to get production asset list ---
def get_production(selected_production, conn: DB):
    asset_list = conn.get_asset_name_list(sorted=True)
    production = selected_production
    if production == 'Bobo':
        gotten_list = asset_list
    elif production == 'DraggonKisser':
        gotten_list = ['Dragon', 'Chicken']
    elif production == 'Custom':
        try:
            custom_list_location = f"{groups}/bobo/character/Rigs/Custom_rigs_list/CustomRig_List.txt"
            with open(custom_list_location, 'r') as file:
                gotten_list = [line.strip() for line in file if line.strip()]
        except Exception as e:
            print(f"Error reading file: {e}")
            return []
    else:
        gotten_list = []
    print(production, gotten_list)
    return production, gotten_list

# --- UI Class ---


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

        # Production label + dropdown
        layout.addWidget(QtWidgets.QLabel("Production"))
        self.production_dropdown = QtWidgets.QComboBox()
        self.production_dropdown.addItems(Productions)
        layout.addWidget(self.production_dropdown)

        # Asset label + dropdown
        layout.addWidget(QtWidgets.QLabel("Asset"))
        self.asset_dropdown = QtWidgets.QComboBox()
        layout.addWidget(self.asset_dropdown)

        # Checkbox row with label next to it
        checkbox_layout = QtWidgets.QHBoxLayout()
        self.export_checkbox = QtWidgets.QCheckBox()
        checkbox_label = QtWidgets.QLabel("Update Anim Symlink")

        checkbox_layout.addWidget(self.export_checkbox)
        checkbox_layout.addWidget(checkbox_label)
        checkbox_layout.addStretch()  # Push them to the left

        layout.addLayout(checkbox_layout)

        # Publish button (single)
        self.publish_button = QtWidgets.QPushButton("Publish")
        layout.addWidget(self.publish_button)


    def make_connections(self):
        self.production_dropdown.currentTextChanged.connect(self.update_assets)
        self.publish_button.clicked.connect(self.handle_publish)

    def update_assets(self, selected_production):
        self.asset_dropdown.clear()
        production_name, gotten_list = get_production(selected_production, self.conn_)
        self.asset_dropdown.addItems(gotten_list)

    def handle_publish(self):
        asset = self.asset_dropdown.currentText()
        production = self.production_dropdown.currentText()
        update_anim = self.export_checkbox.isChecked()
        if production == 'Bobo':
            production_path = 'bobo'
        elif production == 'Custom':
            production_path = 'bobo'
        else:
            production_path = production
    
        if not asset or production == "Select Production":
            mc.warning("Please select both a production and asset before publishing.")
            return

        rig = asset  # assuming rig name is same as asset dropdown
        version_dir = pathlib.Path(f"{groups}/{ production_path}/anim/Rigging/{rig}/RigVersions")
        symlink_dir = pathlib.Path(f"{groups}/{ production_path}/anim/Rigs")

        # Create version directory if it doesn't exist
        version_dir.mkdir(parents=True, exist_ok=True)

        # Determine latest version
        latest_version = 0
        for item in version_dir.glob(f"{rig}.*.mb"):
            try:
                version = int(item.stem.split('.')[-1])
                if version > latest_version:
                    latest_version = version
            except Exception as e:
                print(f"Skipping {item}: {e}")

        v_string = str(latest_version + 1).zfill(3)
        full_name = version_dir / f"{rig}.{v_string}.mb"

        # Save rig file
        mc.file(rename=str(full_name))
        saved = mc.file(save=True, force=True, type="mayaBinary")
        print(f"File saved to: {saved}")

        # Create or update symlink
        if update_anim:
            symlink_dir.mkdir(parents=True, exist_ok=True)
            tmp_link = symlink_dir / "tmp"
            final_link = symlink_dir / f"{rig}.mb"

            try:
                if tmp_link.exists():
                    tmp_link.unlink()
                os.symlink(full_name, tmp_link)
                if final_link.exists():
                    final_link.unlink()
                tmp_link.rename(final_link)
                print(f"Symlink created/updated at: {final_link}")
            except Exception as e:
                print(f"Failed to create symlink: {e}")



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