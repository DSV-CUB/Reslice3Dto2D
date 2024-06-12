#!/bin/sh
cd -- "$(dirname "$0")"
python3 -c "from sourcecode import gui_main; gui_main.QtWidgets.QApplication.setAttribute(gui_main.QtCore.Qt.AA_EnableHighDpiScaling, True); global gui_run; app = gui_main.QtWidgets.QApplication(gui_main.sys.argv); gui_run = gui_main.GUI(); gui_run.show(); gui_main.sys.exit(app.exec_())"