from __future__ import annotations

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets


from pipe.db import DB
from env_sg import DB_Config

import maya.cmds as mc
import os, platform, pathlib

import shared.util as su
from pipe.m.local import get_main_qt_window

rig_list = [
    "select rig",
    "Robin",
    "RobinFace",
    "Rayden",
    "RaydenFace",
    "DungeonMonster",
    "Jett",
    "Blitz",
    "Crossbow",
    "Cipher",
    "LootBag",
    "ManCannon",
    "Door",
    "test",
]


class RigPublishUI(QtWidgets.QDialog):
    def __init__(self, parent=get_main_qt_window()):
        super().__init__(parent)

        self._conn = DB.Get(DB_Config)

        self.setWindowTitle("Rig Publish")
        self.setMinimumWidth(200)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.rig_options = QtWidgets.QComboBox()
        self.rig_options.addItems(rig_list)

        self.anim_check = QtWidgets.QCheckBox("Update Anim Symlink")
        self.pvis_check = QtWidgets.QCheckBox("Update Previs Symlink")
        self.anim_check.setChecked(False)
        self.pvis_check.setChecked(False)

        self.publish_btn = QtWidgets.QPushButton("Publish")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        options_layout = QtWidgets.QFormLayout()
        options_layout.addWidget(self.rig_options)
        options_layout.addWidget(self.anim_check)
        options_layout.addWidget(self.pvis_check)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.publish_btn)
        buttons_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(options_layout)
        main_layout.addLayout(buttons_layout)

    def create_connections(self):
        self.publish_btn.clicked.connect(self.on_publish)
        self.cancel_btn.clicked.connect(self.on_cancel)

    def on_publish(self):
        asset = self._conn.get_asset_by_name("Rayden")
        su.get_production_path() / asset.path / "rig" / "rig.mb"
        file_name = self.rig_options.currentText()

        groups = 'G:' if platform.system() == 'Windows' else '/groups'

        if file_name == "select rig":
            mc.warning("Select a rig to publish.")
            return

        update_anim = self.anim_check.isChecked()
        update_pvis = self.pvis_check.isChecked()

        dir_path = su.get_rigging_path() / "Rigs" / file_name / "RigVersions"
        if file_name in ['Jett', 'Blitz', 'ManCannon']:
            dir_path = f'{groups}/skyguard/Anim/Rigging/{file_name}/RigVersions'
            dir_path = pathlib.Path(dir_path)

        # search directory for all versions and determine new version number
        ls_dir = dir_path.iterdir()
        latest_version = 0

        for item in ls_dir:
            try:
                version = int(str(item).split(".")[-2])
                if version > latest_version:
                    latest_version = version
            except Exception as e:
                print(f"exception '{e}' for: {item}")

        v_string = str(latest_version + 1).zfill(3)

        # save file to path
        full_name = dir_path / f"{file_name}.{v_string}.mb"
        mc.file(rename=full_name)
        saved = mc.file(s=True, f=True, typ="mayaBinary")

        print(f"File saved to '{saved}'")

        # create symlinks
        if file_name in ['Jett', 'Blitz', 'ManCannon'] and update_anim:
            game_link_dir_path = f'{groups}/skyguard/Anim/Rigs'
            temp_name = f"{game_link_dir_path}\\tmp"
            os.symlink(full_name, temp_name)
            os.rename(temp_name, f"{game_link_dir_path}/{file_name}.mb")

            print(
                f"Link to file created or updated at '{game_link_dir_path}/{file_name}.mb'\n"
            )        
        elif update_anim:
            anim_link_dir_path = su.get_anim_path() / "Rigs"
            temp_name = f"{anim_link_dir_path}\\tmp"
            os.symlink(full_name, temp_name)
            os.rename(temp_name, f"{anim_link_dir_path}/{file_name}.mb")

            print(
                f"Link to file created or updated at '{anim_link_dir_path}/{file_name}.mb'\n"
            )
        elif update_pvis:
            pvis_link_dir_path = su.get_previs_path() / "Rigs"
            temp_name = f"{pvis_link_dir_path}\\tmp"
            os.symlink(full_name, temp_name)
            os.rename(temp_name, f"{pvis_link_dir_path}/{file_name}.mb")

            print(
                f"Link to file created or updated at '{pvis_link_dir_path}/{file_name}.mb'\n"
            )
        self.close()

    def on_cancel(self):
        print("Cancelled Rig Publish")
        self.close()


rig_pub: RigPublishUI | None = None


def run():
    global rig_pub
    try:
        assert rig_pub is not None
        rig_pub.close()
        rig_pub.deleteLater()
    except AssertionError:
        pass

    rig_pub = RigPublishUI()
    rig_pub.show()


if __name__ == "__main__":
    try:
        assert rig_pub is not None
        rig_pub.close()
        rig_pub.deleteLater()
    except AssertionError:
        pass

    rig_pub = RigPublishUI()
    rig_pub.show()
