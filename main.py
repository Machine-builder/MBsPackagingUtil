import datetime
import jstyleson
import os
import shutil
import sys
import pyperclip

from scripts import const, release_notes
from scripts import post_processing
from scripts import pack


def increment_version(version, release_type):
    if release_type == 0:
        return [version[0]+1, 0, 0]
    elif release_type == 1:
        return [version[0], version[1]+1, 0]
    elif release_type == 2:
        return [version[0], version[1], version[2]+1]
    elif release_type == 3:
        return [version[0], version[1], version[2]]


# omg the code above this comment sucks pls don't kill me

if __name__ == "__main__":
    from PyQt5 import QtGui, QtCore, QtWidgets, QtWebChannel, uic
    from PyQt5.QtCore import pyqtSignal, QUrl
    from PyQt5.QtWebEngineWidgets import QWebEngineView

    dir_file = os.path.dirname(__file__)
    dir_working = os.getcwd()

    class MDDocument(QtCore.QObject):
        textChanged = pyqtSignal(str)
        requestText = pyqtSignal()
        def __init__(self, parent=None):
            super().__init__(parent)
            self.text_content = ""
        def get_text(self):
            return self.text_content
        def set_text(self, text:str):
            self.text_content = text
            self.textChanged.emit(self.text_content)
        @QtCore.pyqtSlot()
        def request_text(self):
            self.requestText.emit()
        text = QtCore.pyqtProperty(str, fget=get_text, fset=set_text, notify=textChanged)

    class MainWindow(QtWidgets.QMainWindow):
        def __init__(self, config:object):
            super(MainWindow, self).__init__()
            uic.loadUi(os.path.join(dir_file, "resources/interface.ui"), self)

            self.config = config
            self.setup_menu_bar()

            self.input_release_type.currentIndexChanged.connect(self.input_release_type_changed)
            self.btn_package.clicked.connect(self.run_packaging_process)

            self.text_edit_release_headline.textChanged.connect(self.refresh_release_notes)
            self.text_edit_whats_new.textChanged.connect(self.refresh_release_notes)
            self.text_edit_fixes.textChanged.connect(self.refresh_release_notes)
            self.text_edit_other_notes.textChanged.connect(self.refresh_release_notes)

            self.release_type = 0
            self.release_notes_md_document = MDDocument(self)
            self.channel = QtWebChannel.QWebChannel()
            self.channel.registerObject("document", self.release_notes_md_document)
            self.webview.page().setWebChannel(self.channel)
            self.webview.setUrl(QUrl.fromLocalFile(os.path.join(dir_file, "./resources/index.html")))
            self.release_notes_md_document.requestText.connect(self.refresh_release_notes)

            self.release_datetime = datetime.datetime.now()

            self.menu_bar_packs_load(0)
        
        def setup_menu_bar(self):
            self.packs_load_functions = []
            menu_bar = self.menuBar
            menu_bar_configuration = menu_bar.addMenu("Configuration")
            menu_bar_packs = menu_bar_configuration.addMenu("Packs")
            for i, pack in enumerate(self.config["packs"]):
                packaged_name = pack["packaged_name"]
                action = menu_bar_packs.addAction(packaged_name)
                f = lambda _,i=i: self.menu_bar_packs_load(index=i)
                action.triggered.connect(f)
        
        def menu_bar_packs_load(self, index):
            self.selected_pack_index = index
            selected_pack = self.config["packs"][index]
            path_bp = selected_pack["path_bp"]
            path_rp = selected_pack["path_rp"]
            pack_bp = pack.Pack(path_bp)
            pack_rp = pack.Pack(path_rp)
            self.set_packs(pack_bp, pack_rp)
            self.label_title.setText("MACHINE_BUILDER's Packaging Utility - "+selected_pack["packaged_name"])

        def set_packs(self, pack_bp:pack.Pack, pack_rp:pack.Pack):
            self.pack_bp = pack_bp
            self.pack_rp = pack_rp
            self.reload_packs()
        
        def reload_packs(self):
            self.pack_version = self.pack_bp.get_pack_version()
            self.pack_version_next = self.pack_version.copy()
            self.refresh_pack_version()

        def refresh_pack_version(self):
            self.pack_version_next = increment_version(self.pack_version, self.release_type)
            pack_version_str = ".".join([str(x) for x in self.pack_version])
            pack_version_next_str = ".".join([str(x) for x in self.pack_version_next])
            self.line_version.setText(pack_version_str)
            self.line_version_next.setText(pack_version_next_str)
            self.refresh_release_notes()
        
        def refresh_release_notes(self):
            selected_pack = self.config["packs"][self.selected_pack_index]
            self.release_notes_md_text = release_notes.generate_release_notes(
                config=self.config,
                selected_pack=selected_pack,
                release_type=self.release_type,
                version_str=self.line_version_next.text(),
                release_datetime=self.release_datetime,
                text_release_headline=self.text_edit_release_headline.toPlainText(),
                text_whats_new=self.text_edit_whats_new.toPlainText(),
                text_fixes=self.text_edit_fixes.toPlainText(),
                text_other_notes=self.text_edit_other_notes.toPlainText())
            self.release_notes_md_document.set_text(self.release_notes_md_text)
        
        def input_release_type_changed(self):
            self.release_type = self.input_release_type.currentIndex()
            self.refresh_pack_version()
        
        def run_packaging_process(self):
            selected_pack = self.config["packs"][self.selected_pack_index]

            if self.release_type != 4:
                self.pack_bp.set_pack_version(self.pack_version_next)
                self.pack_bp.save_changes()
                self.pack_rp.set_pack_version(self.pack_version_next)
                self.pack_rp.save_changes()
                
            release_info = {
                "release_type": const.RELEASE_TYPE[self.release_type],
                "version": self.pack_version_next,
                "packaged_on": [
                    int(self.release_datetime.timestamp()),
                    self.release_datetime.ctime()
                ],
                "release_notes": self.release_notes_md_text
            }

            print("Packing...")

            version_str = self.line_version_next.text()
            release_path_pack = os.path.join(self.config["releases_path"], selected_pack["packaged_name"])
            if not os.path.exists(self.config["releases_path"]):
                os.mkdir(self.config["releases_path"])
            if not os.path.exists(release_path_pack):
                os.mkdir(release_path_pack)
            release_path = os.path.join(release_path_pack, version_str)
            
            try:
                os.mkdir(release_path)
            except:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Packaging Failure",
                    ("Could not create release folder. "
                        "This may be due to the release type "
                        "being set to repackage and the "
                        "version folder already in the "
                        "releases folder.")
                )
                return
            
            for output in selected_pack["outputs"]:
                pack.pack_bp_and_rp(
                    dir_file,
                    self.pack_bp, self.pack_rp,
                    os.path.join(release_path, selected_pack["packaged_name"]+output["packaged_suffix"]+"_"+version_str),
                    output.get("post_processing", {}))
                try:
                    jstyleson.dump(release_info, open(os.path.join(release_path, "info.json"), "w"), indent=4)
                except:
                    print("Failed to save release info.json")
            pyperclip.copy(self.release_notes_md_text)
            self.reload_packs()
            print("Complete")
            QtWidgets.QMessageBox.information(
                self,
                f"{version_str} Packaging Complete",
                ("The packaging process completed successfully. "
                    "To distribute this release, see the version "
                    "folder in the releases folder. Also note that "
                    "the changelog has been copied to clipboard, "
                    "and is also available in the release info.json file.")
            )

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    config_filepath = os.path.join(dir_file, "config.json")
    if os.path.exists(config_filepath):
        with open(config_filepath, encoding="utf-8") as config_file:
            config = jstyleson.load(config_file)
    else:
        # write config file and send a little message
        print("No config.json file found in project folder.")
        print("One has been created for you.")
        print("Please add your packs to config before re-running.")
        with open(config_filepath, "w") as config_file:
            jstyleson.dump(const.CONFIG_DEFAULT, config_file, indent=4, ensure_ascii=False)
        sys.exit(-1)
    
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    app.exec_()