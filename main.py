import sys
import os
import traceback
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from gui_qt import MainWindow

def excepthook(exc_type, exc_value, exc_tb):
    """全局异常处理器"""
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("ERROR:")
    print(tb)
    QMessageBox.critical(None, "Error", f"发生未处理的错误:\n{str(exc_value)}\n\n详细信息已打印到控制台。")
    sys.exit(1)

if __name__ == "__main__":
    # 设置全局异常处理器
    sys.excepthook = excepthook
    
    try:
        # 在创建QApplication之前设置环境变量来启用高DPI缩放
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        os.environ["QT_SCALE_FACTOR"] = "1"
        
        app = QApplication(sys.argv)
        
        # 设置应用图标
        icon_path = os.path.join(os.path.dirname(__file__), "icon", "logo.ico")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            app.setWindowIcon(app_icon)
        
        # 创建主窗口（加载界面会在MainWindow中创建）
        window = MainWindow()
        sys.exit(app.exec())
    except Exception as e:
        print(f"程序启动错误: {str(e)}")
        print(traceback.format_exc())
        QMessageBox.critical(None, "Error", f"程序启动失败:\n{str(e)}")
        sys.exit(1)
