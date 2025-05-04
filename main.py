import sys
import os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from gui_qt import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app._default_palette = app.palette()
    icon_path = os.path.join(os.path.dirname(__file__), "icon", "icon.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
