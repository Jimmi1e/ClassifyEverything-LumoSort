import os
import sys
import concurrent.futures
import math
import time
from multiprocessing import cpu_count
from PyQt6.QtWidgets import (
    QSizePolicy,
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QProgressBar,
    QStackedWidget, QListWidget, QListWidgetItem, QComboBox, QCheckBox,
    QFrame, QGraphicsDropShadowEffect, QGroupBox, QLineEdit, QTextEdit, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QPalette, QFont, QWindow
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QObject

import Classifierpy as Classifier

class ScaledPreview(QLabel):
    def __init__(self):
        super().__init__()
        self.pix = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: black;")

    def setPixmap(self, pixmap):
        self.pix = pixmap
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.pix:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.fillRect(self.rect(), self.palette().color(QPalette.ColorRole.Window))
        scaled = self.pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        painter.end()
from labels import LABEL_DISPLAY
TEXTS = {
    'en': {
        'welcome': 'Welcome to LumoSort!', 'upload': 'Upload Images', 'dark': 'Dark Mode', 'light': 'Light Mode', 'back': '← Back', 'ready': 'Ready', 'classifying': 'Classifying...', 'completed': '{} categories loaded', 'loading': 'Loading... {}/{} ETA: {}s'
    },
    'zh': {
        'welcome': '欢迎使用 LumoSort！', 'upload': '上传图片', 'dark': '夜间模式', 'light': '日间模式', 'back': '← 返回', 'ready': '就绪', 'classifying': '正在分类...', 'completed': '已加载 {} 个类别', 'loading': '加载中... {}/{} 剩余约 {} 秒'
    },
    'zh-tw': {
        'welcome': '歡迎使用 LumoSort！', 'upload': '上傳圖片', 'dark': '夜間模式', 'light': '日間模式', 'back': '← 返回', 'ready': '就緒', 'classifying': '正在分類...', 'completed': '已載入 {} 個類別', 'loading': '載入中... {}/{} 剩餘約 {} 秒'
    },
    'ja': {
        'welcome': 'LumoSort へようこそ！', 'upload': '画像を選択', 'dark': 'ダークモード', 'light': 'ライトモード', 'back': '← 戻る', 'ready': '準備完了', 'classifying': '分類中...', 'completed': '{} カテゴリを読み込み済み', 'loading': '読み込み中... {}/{} 残り約 {} 秒'
    },
    'fr': {
        'welcome': 'Bienvenue sur LumoSort !', 'upload': 'Importer des images', 'dark': 'Mode sombre', 'light': 'Mode clair', 'back': '← Retour', 'ready': 'Prêt', 'classifying': 'Classification en cours...', 'completed': '{} catégories chargées', 'loading': 'Chargement... {}/{} estimé {}s'
    },
    'ko': {
        'welcome': 'LumoSort에 오신 것을 환영합니다!', 'upload': '이미지 업로드', 'dark': '다크 모드', 'light': '라이트 모드', 'back': '← 뒤로', 'ready': '준비 완료', 'classifying': '분류 중...', 'completed': '{}개 카테고리 로드됨', 'loading': '로드 중... {}/{} 남은 시간 {}초'
    },
    'ru': {
        'welcome': 'Добро пожаловать в LumoSort!', 'upload': 'Загрузить изображения', 'dark': 'Темная тема', 'light': 'Светлая тема', 'back': '← Назад', 'ready': 'Готово', 'classifying': 'Классификация...', 'completed': 'Загружено категорий: {}', 'loading': 'Загрузка... {}/{} осталось ~{} сек'
    },
    'ar': {
        'welcome': 'مرحبًا بك في LumoSort!', 'upload': 'تحميل الصور', 'dark': 'الوضع الليلي', 'light': 'الوضع النهاري', 'back': '← رجوع', 'ready': 'جاهز', 'classifying': 'جارٍ التصنيف...', 'completed': '{} فئة تم تحميلها', 'loading': 'جارٍ التحميل... {}/{} المتبقي: {} ث'
    },
    'es': {
        'welcome': '¡Bienvenido a LumoSort!', 'upload': 'Subir imágenes', 'dark': 'Modo oscuro', 'light': 'Modo claro', 'back': '← Atrás', 'ready': 'Listo', 'classifying': 'Clasificando...', 'completed': '{} categorías cargadas', 'loading': 'Cargando... {}/{} ETA: {}s'
    },
    'de': {
        'welcome': 'Willkommen bei LumoSort!', 'upload': 'Bilder hochladen', 'dark': 'Dunkelmodus', 'light': 'Hellmodus', 'back': '← Zurück', 'ready': 'Bereit', 'classifying': 'Klassifizierung...', 'completed': '{} Kategorien geladen', 'loading': 'Lädt... {}/{} verbleibend: {}s'
    }
}

class ClassifyThread(QThread):
    finished = pyqtSignal(object)

    def __init__(self, paths):
        super().__init__()
        self.paths = paths

    def run(self):
        try:
            results = Classifier.classify_images_by_clip(self.paths, 'sorted')
        except Exception as e:
            results = e
        self.finished.emit(results)


class TypingLabel(QLabel):
    def __init__(self, text, interval=100):
        super().__init__()
        self.full_text = text
        self.interval = interval
        self.index = 0
        self.cursor_visible = True
        self.setText("")
        self.timer = QTimer()
        self.cursor_timer = QTimer()
        self.timer.timeout.connect(self._next_char)
        self.cursor_timer.timeout.connect(self._blink_cursor)
        self.timer.start(self.interval)
        self.cursor_timer.start(500)

    def _next_char(self):
        if self.index < len(self.full_text):
            self.index += 1
            self.update_text()
        else:
            self.timer.stop()

    def _blink_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.update_text()

    def update_text(self):
        cursor = "|" if self.cursor_visible else " "
        self.setText(self.full_text[:self.index] + cursor)

    def restart(self, text=None):
        if text:
            self.full_text = text
        self.index = 0
        self.cursor_visible = True
        self.timer.start(self.interval)
        if not self.cursor_timer.isActive():
            self.cursor_timer.start(500)

class ImageProcessingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 设置大小策略
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 整体样式
        self.light_style = """
            QWidget {
                background-color: #f5f5f7;
                color: #1d1d1f;
            }
            QGroupBox {
                font-weight: 500;
                border: none;
                border-radius: 10px;
                background-color: white;
                margin-top: 24px;
                padding: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                color: #1d1d1f;
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #d2d2d7;
                border-radius: 6px;
                padding: 8px;
                background: white;
                selection-background-color: #0071e3;
            }
            QLineEdit:focus {
                border-color: #0071e3;
            }
            QPushButton {
                background-color: #f5f5f7;
                border: 1px solid #d2d2d7;
                border-radius: 6px;
                padding: 8px 16px;
                color: #1d1d1f;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e8e8ed;
            }
            QPushButton:pressed {
                background-color: #dcdce0;
            }
            QComboBox {
                border: 1px solid #d2d2d7;
                border-radius: 6px;
                padding: 8px;
                background: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QTextEdit {
                border: 1px solid #d2d2d7;
                border-radius: 10px;
                padding: 10px;
                background: white;
                selection-background-color: #0071e3;
            }
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #f5f5f7;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0071e3;
                border-radius: 6px;
            }
        """
        
        self.dark_style = """
            QWidget {
                background-color: #1d1d1f;
                color: #f5f5f7;
            }
            QGroupBox {
                font-weight: 500;
                border: none;
                border-radius: 10px;
                background-color: #2d2d2f;
                margin-top: 24px;
                padding: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                color: #f5f5f7;
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #424245;
                border-radius: 6px;
                padding: 8px;
                background: #2d2d2f;
                color: #f5f5f7;
                selection-background-color: #0071e3;
            }
            QLineEdit:focus {
                border-color: #0071e3;
            }
            QPushButton {
                background-color: #2d2d2f;
                border: 1px solid #424245;
                border-radius: 6px;
                padding: 8px 16px;
                color: #f5f5f7;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3d3d3f;
            }
            QPushButton:pressed {
                background-color: #4d4d4f;
            }
            QComboBox {
                border: 1px solid #424245;
                border-radius: 6px;
                padding: 8px;
                background: #2d2d2f;
                color: #f5f5f7;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow_dark.png);
                width: 12px;
                height: 12px;
            }
            QTextEdit {
                border: 1px solid #424245;
                border-radius: 10px;
                padding: 10px;
                background: #2d2d2f;
                color: #f5f5f7;
                selection-background-color: #0071e3;
            }
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #2d2d2f;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0071e3;
                border-radius: 6px;
            }
        """
        
        # Input Folder
        input_group = QGroupBox("输入文件夹")
        input_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        self.input_entry = QLineEdit()
        self.input_entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_entry.setPlaceholderText("选择包含图片的文件夹...")
        input_browse = QPushButton("浏览")
        input_browse.setFixedWidth(60)
        input_browse.clicked.connect(self.choose_input_folder)
        input_layout.addWidget(self.input_entry)
        input_layout.addWidget(input_browse)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Output Folder
        output_group = QGroupBox("输出文件夹")
        output_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        output_layout = QHBoxLayout()
        output_layout.setSpacing(10)
        self.output_entry = QLineEdit()
        self.output_entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.output_entry.setPlaceholderText("选择保存处理后图片的文件夹...")
        output_browse = QPushButton("浏览")
        output_browse.setFixedWidth(60)
        output_browse.clicked.connect(self.choose_output_folder)
        output_layout.addWidget(self.output_entry)
        output_layout.addWidget(output_browse)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Background Type
        bg_group = QGroupBox("背景样式")
        bg_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        bg_layout = QVBoxLayout()
        self.bg_combo = QComboBox()
        self.bg_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.bg_combo.addItems([
            "1. 主色调背景",
            "2. 主色调圆形背景",
            "3. 模糊背景",
            "4. 纯白背景",
            "5. 自定义参数"
        ])
        bg_layout.addWidget(self.bg_combo)
        bg_group.setLayout(bg_layout)
        layout.addWidget(bg_group)
        
        # Log Text
        log_group = QGroupBox("处理日志")
        log_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(100)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Progress Bar
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)
        
        # Submit Button
        self.submit_btn = QPushButton("处理图片")
        self.submit_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
            QPushButton:pressed {
                background-color: #006edb;
            }
            QPushButton:disabled {
                background-color: #999999;
            }
        """)
        self.submit_btn.clicked.connect(self.process_images)
        layout.addWidget(self.submit_btn)
        
        # 添加阴影效果
        for widget in self.findChildren(QGroupBox):
            shadow = QGraphicsDropShadowEffect(widget)
            shadow.setBlurRadius(20)
            shadow.setXOffset(0)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 25))
            widget.setGraphicsEffect(shadow)
            
        # 设置初始主题
        self.update_theme(QApplication.instance().palette().window().color().lightness() > 128)
        
    def update_theme(self, is_light):
        """更新主题样式"""
        self.setStyleSheet(self.light_style if is_light else self.dark_style)
        # 更新阴影颜色
        shadow_color = QColor(0, 0, 0, 25) if is_light else QColor(0, 0, 0, 40)
        for widget in self.findChildren(QGroupBox):
            if widget.graphicsEffect():
                widget.graphicsEffect().setColor(shadow_color)
        
    def choose_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_entry.setText(folder)
            
    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_entry.setText(folder)
            
    def process_images(self):
        input_folder = self.input_entry.text()
        output_folder = self.output_entry.text()
        
        if not input_folder or not output_folder:
            QMessageBox.warning(self, "Error", "Please select both input and output folders.")
            return
            
        # Get background type (extract number from combo box text)
        bg_type = self.bg_combo.currentText().split('.')[0]
        
        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.submit_btn.setEnabled(False)
        
        # Create a QThread for processing
        self.thread = QThread()
        self.worker = ImageProcessor(input_folder, output_folder, bg_type)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.update_log)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(lambda: self.submit_btn.setEnabled(True))
        
        # Start processing
        self.thread.start()
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def update_log(self, text):
        self.log_text.append(text)

class ImageProcessor(QObject):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, input_folder, output_folder, bg_type):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.bg_type = bg_type
        
    def run(self):
        try:
            from Add_Background import process_images
            
            # Create a progress callback
            def update_progress(value):
                self.progress.emit(value)
                
            # Create a log callback
            def update_log(text):
                self.log.emit(text)
            
            # Process images
            process_images(
                self.input_folder, 
                self.output_folder,
                background=self.bg_type,
                progress_callback=update_progress,
                log_callback=update_log
            )
            
        except Exception as e:
            self.log.emit(f"Error: {str(e)}")
        
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LumoSort')
        self.resize(800, 600)
        self.setMinimumSize(400, 300)
        icon_path = os.path.join(os.path.dirname(__file__), "icon", "logo.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.current_lang = 'en'
        self.status_mode = 'ready'
        self.categories = {}
        self.current_images = []
        self.current_index = 0
        self._flash_on = True
        self.pixel_font = "Courier New"
        
        # 检查是否有已分类的图片
        self.has_classified_images = self._check_classified_images()
        
        # 创建主窗口布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Sidebar
        sidebar = QWidget()
        sb_layout = QVBoxLayout(sidebar)

        # 上传按钮
        self.upload_btn = QPushButton()
        self.upload_btn.setText(TEXTS[self.current_lang]['upload'])
        self.upload_btn.setMinimumHeight(48)
        self.upload_btn.setStyleSheet(self._upload_button_style(dark=False))
        self.upload_btn.clicked.connect(self.on_upload)

        # 按钮的阴影
        shadow = QGraphicsDropShadowEffect(self.upload_btn)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.upload_btn.setGraphicsEffect(shadow)

        # Tools按钮
        self.tools_btn = QPushButton("Tools")
        self.tools_btn.setMinimumHeight(48)
        self.tools_btn.setStyleSheet(self._upload_button_style(dark=False))
        self.tools_btn.clicked.connect(self.on_tools)
        
        # Tools按钮的阴影
        tools_shadow = QGraphicsDropShadowEffect(self.tools_btn)
        tools_shadow.setBlurRadius(15)
        tools_shadow.setOffset(0, 3)
        tools_shadow.setColor(QColor(0, 0, 0, 80))
        self.tools_btn.setGraphicsEffect(tools_shadow)

        # 返回主页按钮
        self.home_btn = QPushButton("Home")
        self.home_btn.setMinimumHeight(48)
        self.home_btn.setStyleSheet(self._upload_button_style(dark=False))
        self.home_btn.clicked.connect(self.on_home)
        
        # Home按钮的阴影
        home_shadow = QGraphicsDropShadowEffect(self.home_btn)
        home_shadow.setBlurRadius(15)
        home_shadow.setOffset(0, 3)
        home_shadow.setColor(QColor(0, 0, 0, 80))
        self.home_btn.setGraphicsEffect(home_shadow)

        self.dark_chk = QCheckBox()
        self.dark_chk.toggled.connect(self.toggle_theme)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['English', '简体中文', '繁體中文', '日本語', 'Français', '한국어', 'Русский', 'العربية', 'Español', 'Deutsch'])
        self.lang_combo.currentIndexChanged.connect(self.on_lang_change)
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 10px;
                background-color: #f0f0f0;
                height: 20px;
                text-align: center;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #007AFF;
                border-radius: 10px;
            }
        """)
        self.progress.hide()

        status_layout = QHBoxLayout()
        self.status_light = QLabel()
        self.status_light.setFixedSize(12, 12)
        self.status_light.setStyleSheet("border-radius: 6px; background-color: green;")
        status_layout.addWidget(self.status_light)
        status_layout.addSpacing(6)
        self.status_lbl = QLabel()
        status_layout.addWidget(self.status_lbl)
        status_layout.addStretch()

        sb_layout.addWidget(self.upload_btn)
        sb_layout.addWidget(self.tools_btn)
        sb_layout.addWidget(self.home_btn)
        sb_layout.addWidget(self.dark_chk)
        sb_layout.addWidget(self.lang_combo)
        sb_layout.addStretch()
        sb_layout.addWidget(self.progress)
        sb_layout.addLayout(status_layout)
        sidebar.setFixedWidth(200)

        # 创建主要内容区域的堆叠窗口
        self.main_stack = QStackedWidget()
        
        # 分类功能页面
        self.classifier_widget = QStackedWidget()
        
        # Welcome page
        self.welcome_page = QWidget()
        wp_layout = QVBoxLayout(self.welcome_page)
        wp_layout.addStretch()
        self.welcome_lbl = TypingLabel(TEXTS[self.current_lang]['welcome'])
        self.welcome_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont(self.pixel_font, 24)
        self.welcome_lbl.setFont(font)
        wp_layout.addWidget(self.welcome_lbl)
        wp_layout.addStretch()
        self.classifier_widget.addWidget(self.welcome_page)
        
        # Category page
        self.cat_page = QWidget()
        cp_layout = QVBoxLayout(self.cat_page)
        self.back_btn = QPushButton()
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #666;
                font-size: 14px;
                text-align: left;
                padding: 8px;
            }
            QPushButton:hover {
                color: #000;
            }
        """)
        self.back_btn.clicked.connect(lambda: self.classifier_widget.setCurrentWidget(self.welcome_page))
        cp_layout.addWidget(self.back_btn)
        
        self.cat_list = QListWidget()
        self.cat_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.cat_list.setWrapping(True)
        self.cat_list.setFlow(QListWidget.Flow.LeftToRight)
        self.cat_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.cat_list.setUniformItemSizes(True)
        self.cat_list.setWordWrap(True)
        self.cat_list.setSpacing(20)
        self.cat_list.setIconSize(QSize(199, 199))
        self.cat_list.itemClicked.connect(self.open_preview)
        cp_layout.addWidget(self.cat_list)
        self.classifier_widget.addWidget(self.cat_page)
        
        # Preview page
        self.pre_page = QWidget()
        pp_layout = QVBoxLayout(self.pre_page)
        self.back2_btn = QPushButton()
        self.back2_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #666;
                font-size: 14px;
                text-align: left;
                padding: 8px;
            }
            QPushButton:hover {
                color: #000;
            }
        """)
        self.back2_btn.clicked.connect(lambda: self.classifier_widget.setCurrentWidget(self.cat_page))
        pp_layout.addWidget(self.back2_btn)
        
        self.preview = ScaledPreview()
        pp_layout.addWidget(self.preview)
        
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("←")
        self.prev_btn.clicked.connect(self.show_prev)
        self.next_btn = QPushButton("→")
        self.next_btn.clicked.connect(self.show_next)
        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()
        pp_layout.addLayout(nav_layout)
        self.classifier_widget.addWidget(self.pre_page)

        # Category preview page (显示某个类别的所有图片)
        self.category_preview_page = QWidget()
        category_preview_layout = QVBoxLayout(self.category_preview_page)
        
        # 返回按钮
        self.back_to_categories_btn = QPushButton()
        self.back_to_categories_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #666;
                font-size: 14px;
                text-align: left;
                padding: 8px;
            }
            QPushButton:hover {
                color: #000;
            }
        """)
        self.back_to_categories_btn.clicked.connect(lambda: self.classifier_widget.setCurrentWidget(self.cat_page))
        category_preview_layout.addWidget(self.back_to_categories_btn)
        
        # 类别名称标签
        self.category_name_label = QLabel()
        self.category_name_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        category_preview_layout.addWidget(self.category_name_label)
        
        # 图片网格
        self.category_images_list = QListWidget()
        self.category_images_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.category_images_list.setWrapping(True)
        self.category_images_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.category_images_list.setUniformItemSizes(True)
        self.category_images_list.setIconSize(QSize(150, 150))
        self.category_images_list.setSpacing(10)
        self.category_images_list.itemClicked.connect(self.show_full_preview)
        category_preview_layout.addWidget(self.category_images_list)
        
        self.classifier_widget.addWidget(self.category_preview_page)

        # Tools页面（图片处理工具）
        self.tools_page = ImageProcessingWidget()

        # 将两个主要页面添加到主堆叠窗口
        self.main_stack.addWidget(self.classifier_widget)
        self.main_stack.addWidget(self.tools_page)
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.main_stack)
        
        self.update_texts()
        self.show_appropriate_page()  # 显示适当的页面

    def _check_classified_images(self):
        """检查是否有已分类的图片"""
        if os.path.exists('sorted') and os.path.isdir('sorted'):
            for sub in os.listdir('sorted'):
                p = os.path.join('sorted', sub)
                if os.path.isdir(p):
                    # 检查文件夹中是否有图片
                    for f in os.listdir(p):
                        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                            return True
        return False

    def on_tools(self):
        """切换到工具页面"""
        self.main_stack.setCurrentWidget(self.tools_page)

    def on_home(self):
        """返回主页（分类器页面）"""
        self.main_stack.setCurrentWidget(self.classifier_widget)

    def on_upload(self):
        """处理上传操作"""
        self.main_stack.setCurrentWidget(self.classifier_widget)  # 确保在分类器页面
        files, _ = QFileDialog.getOpenFileNames(self, TEXTS[self.current_lang]['upload'], "", "Images (*.png *.jpg *.jpeg)")
        if not files:
            return
        self.status_mode = 'classifying'
        self.set_status('classifying', TEXTS[self.current_lang]['classifying'])
        self.progress.show()
        self.progress.setRange(0, 0)
        self.thread = ClassifyThread(files)
        self.thread.finished.connect(self.on_classified)
        self.thread.start()

    def _upload_button_style(self, dark=False):
        if dark:
            bg = "#0A84FF" #瞎调的色儿
            hover = "#339CFF"
            pressed = "#0060DF"
            text_color = "white"
        else:
            bg = "#007AFF"
            hover = "#339CFF"
            pressed = "#005BBB"
            text_color = "white"
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {pressed};
            }}
        """

    def set_status(self, mode, text):
        self.status_mode = mode
        self.status_lbl.setText(text)
        if mode == 'ready':
            self.status_light.setStyleSheet("border-radius: 6px; background-color: green;")
            if hasattr(self, '_flash_timer'):
                self._flash_timer.stop()
        elif mode == 'classifying':
            self.status_light.setStyleSheet("border-radius: 6px; background-color: red;")
            if not hasattr(self, '_flash_timer'):
                self._flash_timer = QTimer()
                self._flash_timer.timeout.connect(self._toggle_light_visibility)
            self._flash_timer.start(500)
        elif mode == 'completed':
            if hasattr(self, '_flash_timer'):
                self._flash_timer.stop()
            self.status_light.setStyleSheet("border-radius: 6px; background-color: green;")
        else:
            self.status_light.setStyleSheet("border-radius: 6px; background-color: orange;")
            if hasattr(self, '_flash_timer'):
                self._flash_timer.stop()

    def _toggle_light_visibility(self):
        self._flash_on = not self._flash_on
        color = "red" if self._flash_on else "#330000"
        self.status_light.setStyleSheet(f"border-radius: 6px; background-color: {color};")

    def update_texts(self):
        t = TEXTS[self.current_lang]
        self.welcome_lbl.restart(t['welcome'])
        self.welcome_lbl.setText(t['welcome'])
        self.upload_btn.setText(t['upload'])
        self.dark_chk.setText(t['dark'])
        self.back_btn.setText(t['back'])
        self.back2_btn.setText(t['back'])
        self.back_to_categories_btn.setText(t['back'])

        if self.status_mode == 'ready':
            self.set_status('ready', t['ready'])
        elif self.status_mode == 'classifying':
            self.set_status('classifying', t['classifying'])
        elif self.status_mode == 'completed':
            self.set_status('completed', t['completed'].format(len(self.categories)))

    def on_lang_change(self, index):
        codes = ['en', 'zh', 'zh-tw', 'ja', 'fr', 'ko', 'ru', 'ar', 'es', 'de']
        self.current_lang = codes[index]
        self.update_texts()

    def toggle_theme(self, checked):
        app = QApplication.instance()
        pal = app.palette()
        t = TEXTS[self.current_lang]
        if checked:
            pal.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
            pal.setColor(QPalette.ColorRole.WindowText, QColor('white'))
            self.upload_btn.setStyleSheet(self._upload_button_style(dark=True))
            self.dark_chk.setText(t['light'])
            # 更新Tools页面主题
            self.tools_page.update_theme(False)
        else:
            pal = app._default_palette
            self.upload_btn.setStyleSheet(self._upload_button_style(dark=False))
            self.dark_chk.setText(t['dark'])
            # 更新Tools页面主题
            self.tools_page.update_theme(True)
        app.setPalette(pal)

    def on_classified(self, result):
        self.progress.hide()
        if isinstance(result, Exception):
            self.status_lbl.setText(f"Error: {result}")
            return
        self.categories = result
        self.load_categories()
        self.status_mode = 'completed'
        self.set_status('completed', TEXTS[self.current_lang]['completed'].format(len(self.categories)))
        self.has_classified_images = True
        self.classifier_widget.setCurrentWidget(self.cat_page)

    def load_categories(self):
        sd = 'sorted'
        self.categories.clear()
        self.cat_list.clear()
        if not os.path.isdir(sd):
            self.has_classified_images = False
            self.show_appropriate_page()
            return
            
        has_any_images = False
        for sub in sorted(os.listdir(sd)):
            p = os.path.join(sd, sub)
            if not os.path.isdir(p):
                continue
            imgs = [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            if not imgs:
                continue
            has_any_images = True
            cover = imgs[0]
            icon = self._make_circle(cover, 199)
            self.categories[sub] = imgs
            item = QListWidgetItem(QIcon(icon), sub)
            item.setData(Qt.ItemDataRole.UserRole, sub)
            self.cat_list.addItem(item)
            
        if not has_any_images:
            self.has_classified_images = False
            self.show_appropriate_page()

    def _make_circle(self, path, size):
        pix = QPixmap(path)
        side = min(pix.width(), pix.height())
        x = (pix.width() - side) // 2
        y = (pix.height() - side) // 2
        pix = pix.copy(x, y, side, side)
        pix = pix.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        out = QPixmap(size, size)
        out.fill(Qt.GlobalColor.transparent)
        p = QPainter(out)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(pix))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, size, size)
        p.end()
        return out

    def open_preview(self, item):
        cat = item.data(Qt.ItemDataRole.UserRole)
        self.current_images = self.categories[cat]
        self.category_name_label.setText(cat)
        self.category_images_list.clear()
        
        for img_path in self.current_images:
            pix = QPixmap(img_path)
            if not pix.isNull():
                scaled_pix = pix.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                item = QListWidgetItem(QIcon(scaled_pix), "")
                item.setData(Qt.ItemDataRole.UserRole, img_path)
                self.category_images_list.addItem(item)
        
        self.classifier_widget.setCurrentWidget(self.category_preview_page)

    def show_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self._update_preview()

    def show_next(self):
        if self.current_index < len(self.current_images) - 1:
            self.current_index += 1
            self._update_preview()

    def _update_preview(self):
        img_path = self.current_images[self.current_index]
        pix = QPixmap(img_path)
        if pix.isNull():
            return
        self.preview.setPixmap(pix)

    def show_full_preview(self, item):
        img_path = item.data(Qt.ItemDataRole.UserRole)
        pix = QPixmap(img_path)
        if not pix.isNull():
            self.preview.setPixmap(pix)
            self.classifier_widget.setCurrentWidget(self.pre_page)

    def show_appropriate_page(self):
        """根据是否有分类图片显示适当的页面"""
        if self.has_classified_images:
            self.load_categories()
            self.classifier_widget.setCurrentWidget(self.cat_page)
        else:
            self.classifier_widget.setCurrentWidget(self.welcome_page)
        self.main_stack.setCurrentWidget(self.classifier_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app._default_palette = app.palette()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())



