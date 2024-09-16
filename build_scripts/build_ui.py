from PySide2 import QtWidgets, QtCore, QtGui

import maya.cmds as mc
import platform
from typing import Optional
from importlib import reload

from pipe.m.local import get_main_qt_window

import rjg.build_scripts.build as build
reload(build)


class RigBuildUI(QtWidgets.QDialog):
    def __init__(self, parent=get_main_qt_window()):
        super().__init__(parent)
        
        self.setWindowTitle("Rig Build")
        self.setMinimumWidth(550)

        groups = 'G:' if platform.system() == 'Windows' else '/groups'
        
        self.default_dict = {
            "Rayden" : {
                "gp" : f"{groups}/dungeons/character/Rigging/Rigs/Rayden/rayden_guides.mb",
                "mp" : f"{groups}/dungeons/character/Rigging/Rigs/Rayden/rayden_model.mb",
                "ep" : f"{groups}/dungeons/character/Rigging/Rigs/Rayden/rayden_extras.mb",
                "cp" : f"{groups}/dungeons/character/Rigging/Rigs/Rayden/Controls/rayden_control_curves.json",
                "sp" : f"{groups}/dungeons/character/Rigging/Rigs/Rayden/Skin/rayden_skinning_file.json",
                "pp" : f"{groups}/dungeons/character/Rigging/Rigs/Rayden/Skin/ray_new_interp.pose",
                "im" : f"{groups}/dungeons/pipeline/pipeline/software/maya/scripts/rjg/build_scripts/ui_images/CursedRay128.jpg",
            },
            "Robin" : {
                "mp" : f"{groups}/dungeons/character/Rigging/Rigs/Robin/robin_model.mb",
                "gp" : f"{groups}/dungeons/character/Rigging/Rigs/Robin/robin_guides.mb",
                "ep" : f"{groups}/dungeons/character/Rigging/Rigs/Robin/robin_extras.mb",
                "cp" : f"{groups}/dungeons/character/Rigging/Rigs/Robin/Controls/robin_control_curves.json",
                "sp" : f"{groups}/dungeons/character/Rigging/Rigs/Robin/Skin/robin_skinning_file.json",
                "pp" : f"{groups}/dungeons/character/Rigging/Rigs/Robin/Skin/robin_new_interp.pose",
                "im" : f"{groups}/dungeons/pipeline/pipeline/software/maya/scripts/rjg/build_scripts/ui_images/Robin128.jpg",
            },
            "DungeonMonster" : {
                "mp" : f"{groups}/dungeons/character/Rigging/Rigs/DungeonMonster/dm_model_combine.mb",
                "gp" : f"{groups}/dungeons/character/Rigging/Rigs/DungeonMonster/dm_guides.mb",
                "ep" : None,
                "cp" : f"{groups}/dungeons/character/Rigging/Rigs/DungeonMonster/Controls/dm_control_curves.json",
                "sp" : None,
                "pp" : None,
                "im" : f"{groups}/dungeons/pipeline/pipeline/software/maya/scripts/rjg/build_scripts/ui_images/DMSkull128.jpg",
            },
        }
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.update_fields()
        
    def create_widgets(self):
        self.char_options = QtWidgets.QComboBox()
        self.char_options.addItems(['Rayden', 'Robin', 'DungeonMonster'])
        self.char_options.setFixedWidth(100)
        
        self.model_label = QtWidgets.QLabel('Model:')
        self.model_label.setFixedWidth(45)
        self.model_input = QtWidgets.QLineEdit()
        self.model_input.setPlaceholderText('Path to model')
        self.model_search = QtWidgets.QPushButton('search')
        #self.model_search.setFixedHeight(17)
        
        self.guides_label = QtWidgets.QLabel('Guides:')
        self.guides_label.setFixedWidth(45)
        self.guides_input = QtWidgets.QLineEdit()
        self.guides_input.setPlaceholderText('Path to guides')
        self.guides_search = QtWidgets.QPushButton('search')
        #self.guides_search.setFixedHeight(17)
        
        self.extras_label = QtWidgets.QLabel('Extras:')
        self.extras_label.setFixedWidth(45)
        self.extras_input = QtWidgets.QLineEdit()
        self.extras_input.setPlaceholderText('Path to extras')
        self.extras_search = QtWidgets.QPushButton('search')
        #self.extras_search.setFixedHeight(17)
        
        self.curve_label = QtWidgets.QLabel('Controls:')
        self.curve_label.setFixedWidth(45)
        self.curve_input = QtWidgets.QLineEdit()
        self.curve_input.setPlaceholderText('Path to curve data')
        self.curve_search = QtWidgets.QPushButton('search')
        #self.curve_search.setFixedHeight(17)
        
        self.skin_label = QtWidgets.QLabel('Skin:')
        self.skin_label.setFixedWidth(45)
        self.skin_input = QtWidgets.QLineEdit()
        self.skin_input.setPlaceholderText('Path to skin data')
        self.skin_search = QtWidgets.QPushButton('search')
        #self.skin_search.setFixedHeight(17)
        
        self.pose_label = QtWidgets.QLabel('Poses:')
        self.pose_label.setFixedWidth(45)
        self.pose_input = QtWidgets.QLineEdit()
        self.pose_input.setPlaceholderText('Path to pose data')
        self.pose_search = QtWidgets.QPushButton('search')
        #self.pose_search.setFixedHeight(17)
        
        self.build_btn = QtWidgets.QPushButton("Build")
        self.build_btn.setDefault(True)
        self.close_btn = QtWidgets.QPushButton("Close")
        
        self.face_check = QtWidgets.QCheckBox("Build face")
        self.pvis_check = QtWidgets.QCheckBox("Build previs rig")
        
        self.pixframe = QtWidgets.QLabel()
        self.pixmap = QtGui.QPixmap()
        self.pixframe.setPixmap(self.pixmap)
        self.pixframe.setFixedHeight(128)
        self.pixframe.setFixedWidth(128)
        
        
        
    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.pixframe)
        top_layout.addWidget(self.char_options, alignment=(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom))
        
        model_layout = QtWidgets.QHBoxLayout()
        model_layout.addWidget(self.model_label)
        model_layout.addWidget(self.model_input)
        model_layout.addWidget(self.model_search)
        
        guides_layout = QtWidgets.QHBoxLayout()
        guides_layout.addWidget(self.guides_label)
        guides_layout.addWidget(self.guides_input)
        guides_layout.addWidget(self.guides_search)
        
        extras_layout = QtWidgets.QHBoxLayout()
        extras_layout.addWidget(self.extras_label)
        extras_layout.addWidget(self.extras_input)
        extras_layout.addWidget(self.extras_search)
        
        curve_layout = QtWidgets.QHBoxLayout()
        curve_layout.addWidget(self.curve_label)
        curve_layout.addWidget(self.curve_input)
        curve_layout.addWidget(self.curve_search)
        
        skin_layout = QtWidgets.QHBoxLayout()
        skin_layout.addWidget(self.skin_label)
        skin_layout.addWidget(self.skin_input)
        skin_layout.addWidget(self.skin_search)
        
        pose_layout = QtWidgets.QHBoxLayout()
        pose_layout.addWidget(self.pose_label)
        pose_layout.addWidget(self.pose_input)
        pose_layout.addWidget(self.pose_search)
        
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(self.build_btn)
        buttons_layout.addWidget(self.close_btn)
        
        checks_layout = QtWidgets.QVBoxLayout()
        checks_layout.addWidget(self.face_check)
        checks_layout.addWidget(self.pvis_check)
        
        main_layout.addLayout(top_layout)
        main_layout.addLayout(model_layout)
        main_layout.addLayout(guides_layout)
        main_layout.addLayout(extras_layout)
        main_layout.addLayout(curve_layout)
        main_layout.addLayout(skin_layout)
        main_layout.addLayout(pose_layout)
        main_layout.addLayout(checks_layout)
        main_layout.addLayout(buttons_layout)
        
    def create_connections(self):
        self.char_options.currentTextChanged.connect(self.update_fields)
        
        self.model_search.clicked.connect(lambda: self.on_search(self.model_input, 'Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)'))
        self.guides_search.clicked.connect(lambda: self.on_search(self.guides_input, 'Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)'))
        self.extras_search.clicked.connect(lambda: self.on_search(self.extras_input, 'Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)'))
        self.skin_search.clicked.connect(lambda: self.on_search(self.skin_input, 'JSON files (*.json);;All Files (*.*)'))
        self.curve_search.clicked.connect(lambda: self.on_search(self.curve_input, 'JSON files (*.json);;All Files (*.*)'))
        self.pose_search.clicked.connect(lambda: self.on_search(self.pose_input, 'Pose files (*.pose);;All Files (*.*)'))
        
        self.build_btn.clicked.connect(self.on_build)
        self.close_btn.clicked.connect(self.on_cancel)
        
    def on_search(self, text_field, filter):
        f = mc.fileDialog2(fm=1, ff=filter)
        try:
            text_field.setText(str(f[0]))
        except:
            pass # here if file dialog closed w/o file selected
        
    def on_cancel(self):
        self.close()
        
    def update_fields(self):
        curr_char = self.char_options.currentText()
        defaults = self.default_dict[curr_char]
        
        self.pixmap.load(defaults['im'])
        self.pixframe.setPixmap(self.pixmap)
        
        self.model_input.setText(defaults['mp'])
        self.guides_input.setText(defaults['gp'])
        self.extras_input.setText(defaults['ep'])
        self.curve_input.setText(defaults['cp'])
        self.skin_input.setText(defaults['sp'])
        self.pose_input.setText(defaults['pp'])
        
    def on_build(self):
        character = self.char_options.currentText()
        mp = self.model_input.text()
        gp = self.guides_input.text()
        ep = self.extras_input.text()
        cp = self.curve_input.text()
        sp = self.skin_input.text()
        pp = self.pose_input.text()
        face = self.face_check.isChecked()
        previs = self.pvis_check.isChecked()
        
        for v in [mp, gp, ep, cp, sp, pp]:
            if v == "":
                v = None
        
        self.close()
        build.run(character=character, mp=mp, gp=gp, ep=ep, cp=cp, sp=sp, pp=pp, face=face, previs=previs)
        
        
        
rig_build: Optional[RigBuildUI] = None        
        
def run():
    global rig_build
    try:
        assert rig_build is not None
        rig_build.close()
        rig_build.deleteLater()
    except AssertionError:
        pass

    rig_build = RigBuildUI()
    rig_build.show()
    

    
if __name__ == '__main__':
    run()