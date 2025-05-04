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
    QStackedWidget, QListWidget, QListWidgetItem, QComboBox, QCheckBox
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QPalette, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer

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
# TEXTS = {
#     'en': {
#         'welcome': 'Welcome to LumoSort!', 'upload': 'Upload Images', 'dark': 'Dark Mode', 'back': '← Back', 'ready': 'Ready', 'classifying': 'Classifying...', 'completed': '{} categories loaded', 'loading': 'Loading... {}/{} ETA: {}s'
#     },
#     'zh': {
#         'welcome': '欢迎使用 LumoSort！', 'upload': '上传图片', 'dark': '夜间模式', 'back': '← 返回', 'ready': '就绪', 'classifying': '正在分类...', 'completed': '已加载 {} 个类别', 'loading': '加载中... {}/{} 剩余约 {} 秒'
#     },
#     'zh-tw': {
#         'welcome': '歡迎使用 LumoSort！', 'upload': '上傳圖片', 'dark': '夜間模式', 'back': '← 返回', 'ready': '就緒', 'classifying': '正在分類...', 'completed': '已載入 {} 個類別', 'loading': '載入中... {}/{} 剩餘約 {} 秒'
#     },
#     'ja': {
#         'welcome': 'LumoSort へようこそ！', 'upload': '画像を選択', 'dark': 'ダークモード', 'back': '← 戻る', 'ready': '準備完了', 'classifying': '分類中...', 'completed': '{} カテゴリを読み込み済み', 'loading': '読み込み中... {}/{} 残り約 {} 秒'
#     },
#     'fr': {
#         'welcome': 'Bienvenue sur LumoSort !', 'upload': 'Importer des images', 'dark': 'Mode sombre', 'back': '← Retour', 'ready': 'Prêt', 'classifying': 'Classification en cours...', 'completed': '{} catégories chargées', 'loading': 'Chargement... {}/{} estimé {}s'
#     },
#     'ko': {
#         'welcome': 'LumoSort에 오신 것을 환영합니다!', 'upload': '이미지 업로드', 'dark': '다크 모드', 'back': '← 뒤로', 'ready': '준비 완료', 'classifying': '분류 중...', 'completed': '{}개 카테고리 로드됨', 'loading': '로드 중... {}/{} 남은 시간 {}초'
#     },
#     'ru': {
#         'welcome': 'Добро пожаловать в LumoSort!', 'upload': 'Загрузить изображения', 'dark': 'Темная тема', 'back': '← Назад', 'ready': 'Готово', 'classifying': 'Классификация...', 'completed': 'Загружено категорий: {}', 'loading': 'Загрузка... {}/{} осталось ~{} сек'
#     },
#     'ar': {
#         'welcome': 'مرحبًا بك في LumoSort!', 'upload': 'تحميل الصور', 'dark': 'الوضع الليلي', 'back': '← رجوع', 'ready': 'جاهز', 'classifying': 'جارٍ التصنيف...', 'completed': '{} فئة تم تحميلها', 'loading': 'جارٍ التحميل... {}/{} المتبقي: {} ث'
#     },
#     'es': {
#         'welcome': '¡Bienvenido a LumoSort!', 'upload': 'Subir imágenes', 'dark': 'Modo oscuro', 'back': '← Atrás', 'ready': 'Listo', 'classifying': 'Clasificando...', 'completed': '{} categorías cargadas', 'loading': 'Cargando... {}/{} ETA: {}s'
#     },
#     'de': {
#         'welcome': 'Willkommen bei LumoSort!', 'upload': 'Bilder hochladen', 'dark': 'Dunkelmodus', 'back': '← Zurück', 'ready': 'Bereit', 'classifying': 'Klassifizierung...', 'completed': '{} Kategorien geladen', 'loading': 'Lädt... {}/{} verbleibend: {}s'
#     }
# }

# # Clear cache when opne 
# if os.path.exists("thumb_cache"):
#     try:
#         for f in os.listdir("thumb_cache"):
#             if f.endswith("_thumb.jpg"):
#                 os.remove(os.path.join("thumb_cache", f))
#     except Exception:
#         pass

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LumoSort')
        self.resize(1000, 700)
        icon_path = os.path.join(os.path.dirname(__file__), "icon", "icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.current_lang = 'en'
        self.status_mode = 'ready'
        self.categories = {}
        self.current_images = []
        self.current_index = 0
        self._flash_on = True
        self.pixel_font = "Courier New"
        #Sidebar
        sidebar = QWidget()
        sb_layout = QVBoxLayout(sidebar)
        # self.upload_btn = QPushButton()
        # self.upload_btn.clicked.connect(self.on_upload)

        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        #上传
        self.upload_btn = QPushButton()
        self.upload_btn.setText(TEXTS[self.current_lang]['upload'])
        self.upload_btn.setMinimumHeight(48)
        self.upload_btn.setStyleSheet(self._upload_button_style(dark=False))
        self.upload_btn.clicked.connect(self.on_upload)

        #按钮的阴影
        shadow = QGraphicsDropShadowEffect(self.upload_btn)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.upload_btn.setGraphicsEffect(shadow)


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

        # self.status_lbl = QLabel()
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
        sb_layout.addWidget(self.dark_chk)
        sb_layout.addWidget(self.lang_combo)
        sb_layout.addStretch()
        sb_layout.addWidget(self.progress)
        sb_layout.addLayout(status_layout)
        sidebar.setFixedWidth(200)

        # sb_layout.addWidget(self.upload_btn)
        # sb_layout.addWidget(self.dark_chk)
        # sb_layout.addWidget(self.lang_combo)
        # sb_layout.addStretch()
        # sb_layout.addWidget(self.progress)
        # sb_layout.addWidget(self.status_lbl)
        # sidebar.setFixedWidth(200)

        # Pages
        self.stack = QStackedWidget()

        self.welcome_page = QWidget()
        wp_layout = QVBoxLayout(self.welcome_page)
        wp_layout.addStretch()
        # self.welcome_lbl = QLabel()
        # self.welcome_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_lbl = TypingLabel(TEXTS[self.current_lang]['welcome'])
        self.welcome_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_lbl.setFont(QFont(self.pixel_font, 18))

        wp_layout.addWidget(self.welcome_lbl)
        wp_layout.addStretch()
        self.stack.addWidget(self.welcome_page)

        self.album_list = QListWidget()
        self.album_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.album_list.setIconSize(QSize(150, 150))
        self.album_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.album_list.setSpacing(20)
        self.album_list.itemClicked.connect(self.open_category)
        self.stack.addWidget(self.album_list)

        self.cat_page = QWidget()
        cp_layout = QVBoxLayout(self.cat_page)
        # self.back_btn = QPushButton()
        self.back_btn = QPushButton()
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #007AFF;
                border: none;
                padding: 10px 16px;
                font-size: 16px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(0, 122, 255, 0.1);
            }
        """)

        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.cat_title = QLabel()
        self.cat_title.setStyleSheet('font-weight:bold; font-size:16px;')
        cp_layout.addWidget(self.back_btn)
        cp_layout.addWidget(self.cat_title)
        self.cat_list = QListWidget()
        self.cat_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.cat_list.setWrapping(True)
        self.cat_list.setFlow(QListWidget.Flow.LeftToRight)
        # self.cat_list.setGridSize(QSize(120, 120))  # disabled for per-item sizeHint
        self.cat_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.cat_list.setUniformItemSizes(True)
        self.cat_list.setWordWrap(True)
        # self.cat_list.setIconSize(QSize(180, 180))  # disabled for per-item icon size
        self.cat_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.cat_list.setSpacing(9)
        self.cat_list.itemClicked.connect(self.open_preview)
        cp_layout.addWidget(self.cat_list)
        self.stack.addWidget(self.cat_page)

        self.pre_page = QWidget()
        pp_layout = QVBoxLayout(self.pre_page)
        # self.back2_btn = QPushButton()
        
        self.back2_btn = QPushButton()
        self.back2_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #007AFF;
                border: none;
                padding: 10px 16px;
                font-size: 16px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(0, 122, 255, 0.1);
            }
        """)
        self.back2_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back2_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))


        pp_layout.addWidget(self.back2_btn)
        self.pre_lbl = ScaledPreview()
        pp_layout.addWidget(self.pre_lbl)
        nav = QHBoxLayout()
        prev_btn = QPushButton('◀')
        next_btn = QPushButton('▶')
        prev_btn.clicked.connect(self.show_prev)
        next_btn.clicked.connect(self.show_next)
        nav.addWidget(prev_btn)
        nav.addStretch()
        nav.addWidget(next_btn)
        pp_layout.addLayout(nav)
        self.stack.addWidget(self.pre_page)

        main = QWidget()
        m_layout = QHBoxLayout(main)
        m_layout.addWidget(sidebar)
        m_layout.addWidget(self.stack, 1)
        self.setCentralWidget(main)

        self.cat_list.resizeEvent = self.adjust_grid_size

        self.update_texts()
        self.load_categories()
        if self.categories:
            self.status_mode = 'completed'
            # self.status_lbl.setText(TEXTS[self.current_lang]['completed'].format(len(self.categories)))
            self.set_status('completed', TEXTS[self.current_lang]['completed'].format(len(self.categories)))

            self.stack.setCurrentIndex(1)
        else:
            self.status_mode = 'ready'
            # self.status_lbl.setText(TEXTS[self.current_lang]['ready'])
            self.set_status('ready', TEXTS[self.current_lang]['ready'])
            self.stack.setCurrentIndex(0)

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

        if self.status_mode == 'ready':
            self.set_status('ready', t['ready'])
        elif self.status_mode == 'classifying':
            self.set_status('classifying', t['classifying'])
        elif self.status_mode == 'completed':
            self.set_status('completed', t['completed'].format(len(self.categories)))

        # if self.status_mode == 'ready':
        #     self.status_lbl.setText(t['ready'])
        # elif self.status_mode == 'classifying':
        #     self.status_lbl.setText(t['classifying'])
        # elif self.status_mode == 'completed':
        #     self.status_lbl.setText(t['completed'].format(len(self.categories)))
        # loading state is updated dynamically during processing

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
            self.upload_btn.setStyleSheet(self._upload_button_style(dark=True))#new
            self.dark_chk.setText(t['light'])
        else:
            pal = app._default_palette
            self.upload_btn.setStyleSheet(self._upload_button_style(dark=False))#new
            self.dark_chk.setText(t['dark'])
        app.setPalette(pal)

    def on_upload(self):
        files, _ = QFileDialog.getOpenFileNames(self, TEXTS[self.current_lang]['upload'], "", "Images (*.png *.jpg *.jpeg)")
        if not files:
            return
        self.status_mode = 'classifying'
        # self.status_lbl.setText(TEXTS[self.current_lang]['classifying'])
        self.set_status('classifying', TEXTS[self.current_lang]['classifying'])
        self.progress.show()
        self.progress.setRange(0, 0)
        self.thread = ClassifyThread(files)
        self.thread.finished.connect(self.on_classified)
        self.thread.start()

    def on_classified(self, result):
        self.progress.hide()
        if isinstance(result, Exception):
            self.status_lbl.setText(f"Error: {result}")
            return
        self.categories = result
        self.load_categories()
        self.status_mode = 'completed'
        # self.status_lbl.setText(TEXTS[self.current_lang]['completed'].format(len(self.categories)))
        self.set_status('completed', TEXTS[self.current_lang]['completed'].format(len(self.categories)))

        self.stack.setCurrentIndex(1)

    def load_categories(self):
        sd = 'sorted'
        self.categories.clear()
        self.album_list.clear()
        if not os.path.isdir(sd):
            return
        for sub in sorted(os.listdir(sd)):
            p = os.path.join(sd, sub)
            if not os.path.isdir(p):
                continue
            imgs = [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            if not imgs:
                continue
            cover = imgs[0]
            icon = self._make_circle(cover, 150)
            self.categories[sub] = imgs
            item = QListWidgetItem(QIcon(icon), sub)
            item.setData(Qt.ItemDataRole.UserRole, sub)
            self.album_list.addItem(item)

    def open_category(self, item):
        cat = item.data(Qt.ItemDataRole.UserRole)
        self.cat_title.setText(cat)
        self.cat_list.clear()
        self.current_images = self.categories.get(cat, [])
        self.stack.setCurrentIndex(2)

        def load_thumb(path):
            from PyQt6.QtGui import QImageReader
            cache_dir = os.path.join('thumb_cache')
            os.makedirs(cache_dir, exist_ok=True)
            mtime = os.path.getmtime(path)
            thumb_path = os.path.join(cache_dir, os.path.basename(path) + f'_{int(mtime)}_thumb.jpg')
            # clean older cache
            for f in os.listdir(cache_dir):
                if f.startswith(os.path.basename(path)) and f != os.path.basename(thumb_path):
                    try:
                        os.remove(os.path.join(cache_dir, f))
                    except:
                        pass
            if os.path.exists(thumb_path):
                pix = QPixmap(thumb_path)
                if not pix.isNull():
                    return pix, path
                else:
                    os.remove(thumb_path)

            reader = QImageReader(path)
            reader.setAutoTransform(True)
            # reader.setScaledSize(QSize(9999, 180)) 
            image = reader.read()
            if not image.isNull():
                scaled = image.scaledToHeight(180, Qt.TransformationMode.SmoothTransformation)
                scaled.save(thumb_path, 'JPG')
                return QPixmap.fromImage(scaled), path
            if not image.isNull():
                
                return None

        num_images = len(self.current_images)
        self.progress.show()
        self.progress.setRange(0, num_images)
        start_time = time.time()
        self.status_mode = 'loading'

        loaded_pixmaps = [None] * len(self.current_images)
        with concurrent.futures.ThreadPoolExecutor(max_workers=math.ceil(cpu_count() * 0.66)) as executor:
            futures = {executor.submit(load_thumb, path): path for path in self.current_images}
            future_to_index = {fut: idx for idx, fut in enumerate(futures)}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                idx = future_to_index[future]
                result = future.result()
                if result:
                    loaded_pixmaps[idx] = result
                self.progress.setValue(i + 1)
                elapsed = time.time() - start_time
                remaining = (elapsed / (i + 1)) * (num_images - i - 1)
                self.status_lbl.setText(TEXTS[self.current_lang]['loading'].format(i + 1, num_images, int(remaining)))

        view_width = self.cat_list.viewport().width()
        spacing = self.cat_list.spacing()
        min_cols = 3
        target_width = max(120, min((view_width - spacing * 2 * min_cols) // min_cols, 300))
        max_height = max([pix.height() for pix, _ in loaded_pixmaps]) if loaded_pixmaps else 100
        icon_size = QSize(target_width, max_height)
        # skip setting global icon size since we set per-item
        # skip setting global grid size since we set per-item

        for i, (pix, path) in enumerate(loaded_pixmaps):
            if pix is None:
                continue
            scaled = pix.scaledToHeight(180, Qt.TransformationMode.SmoothTransformation)
            self.cat_list.setIconSize(scaled.size())
            icon = QIcon(scaled)
            item = QListWidgetItem()
            item.setIcon(icon)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setToolTip(os.path.basename(path))
            item.setSizeHint(scaled.size())
            self.cat_list.addItem(item)

        self.progress.hide()
        self.status_mode = 'completed'
        self.set_status('completed', TEXTS[self.current_lang]['completed'].format(len(self.categories)))
        self.status_mode = 'completed'
        self.set_status('completed', TEXTS[self.current_lang]['completed'].format(len(self.categories)))


    def open_preview(self, item):
        idx = self.cat_list.row(item)
        self.current_index = idx
        self._update_preview()
        self.stack.setCurrentIndex(3)
        self.pre_lbl.setMinimumSize(0, 0)

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
        self.pre_lbl.setMinimumSize(1, 1)
        self.pre_lbl.setPixmap(pix)

    def adjust_grid_size(self, event):
        view_width = self.cat_list.viewport().width()
        spacing = self.cat_list.spacing()
        if self.cat_list.count() == 0:
            QListWidget.resizeEvent(self.cat_list, event)
            return

        item = self.cat_list.item(0)
        size = self.cat_list.iconSize()
        icon_width = size.width()
        icon_height = size.height()
        cols = max(1, view_width // (icon_width + spacing * 2))
        grid_width = view_width // cols - spacing
        self.cat_list.setGridSize(QSize(grid_width, icon_height + 30))
        QListWidget.resizeEvent(self.cat_list, event)

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app._default_palette = app.palette()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())






# # import os
# # import sys
# # import shutil
# # import concurrent.futures
# # import math
# # import time
# # from multiprocessing import cpu_count
# # from PyQt6.QtWidgets import (
# #     QSizePolicy,
# #     QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
# #     QPushButton, QLabel, QFileDialog, QProgressBar,
# #     QStackedWidget, QListWidget, QListWidgetItem, QComboBox, QCheckBox
# # )
# # from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QPalette
# # from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize

# # import Classifierpy as Classifier

# # class ScaledPreview(QLabel):
# #     def __init__(self):
# #         super().__init__()
# #         self.pix = None
# #         self.setAlignment(Qt.AlignmentFlag.AlignCenter)
# #         self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
# #         self.setStyleSheet("background-color: black;")

# #     def setPixmap(self, pixmap):
# #         self.pix = pixmap
# #         self.update()

# #     def paintEvent(self, event):
# #         super().paintEvent(event)
# #         if not self.pix:
# #             return
# #         painter = QPainter(self)
# #         painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
# #         painter.fillRect(self.rect(), self.palette().color(QPalette.ColorRole.Window))
# #         scaled = self.pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
# #         x = (self.width() - scaled.width()) // 2
# #         y = (self.height() - scaled.height()) // 2
# #         painter.drawPixmap(x, y, scaled)
# #         painter.end()
# # from labels import LABEL_DISPLAY

# # TEXTS = {
# #     'en': {
# #         'welcome': 'Welcome to LumoSort!', 'upload': 'Upload Images', 'dark': 'Dark Mode', 'back': '← Back', 'ready': 'Ready', 'classifying': 'Classifying...', 'completed': '{} categories loaded', 'loading': 'Loading... {}/{} ETA: {}s'
# #     },
# #     'zh': {
# #         'welcome': '欢迎使用 LumoSort！', 'upload': '上传图片', 'dark': '夜间模式', 'back': '← 返回', 'ready': '就绪', 'classifying': '正在分类...', 'completed': '已加载 {} 个类别', 'loading': '加载中... {}/{} 剩余约 {} 秒'
# #     },
# #     'zh-tw': {
# #         'welcome': '歡迎使用 LumoSort！', 'upload': '上傳圖片', 'dark': '夜間模式', 'back': '← 返回', 'ready': '就緒', 'classifying': '正在分類...', 'completed': '已載入 {} 個類別', 'loading': '載入中... {}/{} 剩餘約 {} 秒'
# #     },
# #     'ja': {
# #         'welcome': 'LumoSort へようこそ！', 'upload': '画像を選択', 'dark': 'ダークモード', 'back': '← 戻る', 'ready': '準備完了', 'classifying': '分類中...', 'completed': '{} カテゴリを読み込み済み', 'loading': '読み込み中... {}/{} 残り約 {} 秒'
# #     },
# #     'fr': {
# #         'welcome': 'Bienvenue sur LumoSort !', 'upload': 'Importer des images', 'dark': 'Mode sombre', 'back': '← Retour', 'ready': 'Prêt', 'classifying': 'Classification en cours...', 'completed': '{} catégories chargées', 'loading': 'Chargement... {}/{} estimé {}s'
# #     },
# #     'ko': {
# #         'welcome': 'LumoSort에 오신 것을 환영합니다!', 'upload': '이미지 업로드', 'dark': '다크 모드', 'back': '← 뒤로', 'ready': '준비 완료', 'classifying': '분류 중...', 'completed': '{}개 카테고리 로드됨', 'loading': '로드 중... {}/{} 남은 시간 {}초'
# #     },
# #     'ru': {
# #         'welcome': 'Добро пожаловать в LumoSort!', 'upload': 'Загрузить изображения', 'dark': 'Темная тема', 'back': '← Назад', 'ready': 'Готово', 'classifying': 'Классификация...', 'completed': 'Загружено категорий: {}', 'loading': 'Загрузка... {}/{} осталось ~{} сек'
# #     },
# #     'ar': {
# #         'welcome': 'مرحبًا بك في LumoSort!', 'upload': 'تحميل الصور', 'dark': 'الوضع الليلي', 'back': '← رجوع', 'ready': 'جاهز', 'classifying': 'جارٍ التصنيف...', 'completed': '{} فئة تم تحميلها', 'loading': 'جارٍ التحميل... {}/{} المتبقي: {} ث'
# #     },
# #     'es': {
# #         'welcome': '¡Bienvenido a LumoSort!', 'upload': 'Subir imágenes', 'dark': 'Modo oscuro', 'back': '← Atrás', 'ready': 'Listo', 'classifying': 'Clasificando...', 'completed': '{} categorías cargadas', 'loading': 'Cargando... {}/{} ETA: {}s'
# #     },
# #     'de': {
# #         'welcome': 'Willkommen bei LumoSort!', 'upload': 'Bilder hochladen', 'dark': 'Dunkelmodus', 'back': '← Zurück', 'ready': 'Bereit', 'classifying': 'Klassifizierung...', 'completed': '{} Kategorien geladen', 'loading': 'Lädt... {}/{} verbleibend: {}s'
# #     }
# # }

# # # # Clear outdated thumbnails on each launch
# # # if os.path.exists("thumb_cache"):
# # #     try:
# # #         for f in os.listdir("thumb_cache"):
# # #             if f.endswith("_thumb.jpg"):
# # #                 os.remove(os.path.join("thumb_cache", f))
# # #     except Exception:
# # #         pass

# # class ClassifyThread(QThread):
# #     finished = pyqtSignal(object)

# #     def __init__(self, paths):
# #         super().__init__()
# #         self.paths = paths

# #     def run(self):
# #         try:
# #             results = Classifier.classify_images_by_clip(self.paths, 'sorted')
# #         except Exception as e:
# #             results = e
# #         self.finished.emit(results)

# # class MainWindow(QMainWindow):
# #     def __init__(self):
# #         super().__init__()
# #         self.setWindowTitle('LumoSort')
# #         self.resize(1000, 700)

# #         self.current_lang = 'en'
# #         self.status_mode = 'ready'
# #         self.categories = {}
# #         self.current_images = []
# #         self.current_index = 0

# #         # Sidebar
# #         sidebar = QWidget()
# #         sb_layout = QVBoxLayout(sidebar)
# #         # self.upload_btn = QPushButton()
# #         # self.upload_btn.clicked.connect(self.on_upload)

# #         from PyQt6.QtWidgets import QGraphicsDropShadowEffect
# #         # 上传按钮
# #         self.upload_btn = QPushButton()
# #         self.upload_btn.setText(TEXTS[self.current_lang]['upload'])
# #         self.upload_btn.setMinimumHeight(48)
# #         self.upload_btn.setStyleSheet(self._upload_button_style(dark=False))
# #         self.upload_btn.clicked.connect(self.on_upload)

# #         # 添加阴影
# #         shadow = QGraphicsDropShadowEffect(self.upload_btn)
# #         shadow.setBlurRadius(15)
# #         shadow.setOffset(0, 3)
# #         shadow.setColor(QColor(0, 0, 0, 80))
# #         self.upload_btn.setGraphicsEffect(shadow)


# #         self.dark_chk = QCheckBox()
# #         self.dark_chk.toggled.connect(self.toggle_theme)
# #         self.lang_combo = QComboBox()
# #         self.lang_combo.addItems(['English', '简体中文', '繁體中文', '日本語', 'Français', '한국어', 'Русский', 'العربية', 'Español', 'Deutsch'])
# #         self.lang_combo.currentIndexChanged.connect(self.on_lang_change)
# #         self.progress = QProgressBar()
# #         self.progress.hide()
# #         self.status_lbl = QLabel()
# #         sb_layout.addWidget(self.upload_btn)
# #         sb_layout.addWidget(self.dark_chk)
# #         sb_layout.addWidget(self.lang_combo)
# #         sb_layout.addStretch()
# #         sb_layout.addWidget(self.progress)
# #         sb_layout.addWidget(self.status_lbl)
# #         sidebar.setFixedWidth(200)

# #         # Pages
# #         self.stack = QStackedWidget()

# #         self.welcome_page = QWidget()
# #         wp_layout = QVBoxLayout(self.welcome_page)
# #         wp_layout.addStretch()
# #         self.welcome_lbl = QLabel()
# #         self.welcome_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
# #         wp_layout.addWidget(self.welcome_lbl)
# #         wp_layout.addStretch()
# #         self.stack.addWidget(self.welcome_page)

# #         self.album_list = QListWidget()
# #         self.album_list.setViewMode(QListWidget.ViewMode.IconMode)
# #         self.album_list.setIconSize(QSize(150, 150))
# #         self.album_list.setResizeMode(QListWidget.ResizeMode.Adjust)
# #         self.album_list.setSpacing(20)
# #         self.album_list.itemClicked.connect(self.open_category)
# #         self.stack.addWidget(self.album_list)

# #         self.cat_page = QWidget()
# #         cp_layout = QVBoxLayout(self.cat_page)
# #         self.back_btn = QPushButton()
# #         self.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
# #         self.cat_title = QLabel()
# #         self.cat_title.setStyleSheet('font-weight:bold; font-size:16px;')
# #         cp_layout.addWidget(self.back_btn)
# #         cp_layout.addWidget(self.cat_title)
# #         self.cat_list = QListWidget()
# #         self.cat_list.setViewMode(QListWidget.ViewMode.IconMode)
# #         self.cat_list.setWrapping(True)
# #         self.cat_list.setFlow(QListWidget.Flow.LeftToRight)
# #         # self.cat_list.setGridSize(QSize(120, 120))  # disabled for per-item sizeHint
# #         self.cat_list.setResizeMode(QListWidget.ResizeMode.Adjust)
# #         self.cat_list.setUniformItemSizes(True)
# #         self.cat_list.setWordWrap(True)
# #         # self.cat_list.setIconSize(QSize(180, 180))  # disabled for per-item icon size
# #         self.cat_list.setResizeMode(QListWidget.ResizeMode.Adjust)
# #         self.cat_list.setSpacing(9)
# #         self.cat_list.itemClicked.connect(self.open_preview)
# #         cp_layout.addWidget(self.cat_list)
# #         self.stack.addWidget(self.cat_page)

# #         self.pre_page = QWidget()
# #         pp_layout = QVBoxLayout(self.pre_page)
# #         self.back2_btn = QPushButton()
# #         self.back2_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
# #         pp_layout.addWidget(self.back2_btn)
# #         self.pre_lbl = ScaledPreview()
# #         pp_layout.addWidget(self.pre_lbl)
# #         nav = QHBoxLayout()
# #         prev_btn = QPushButton('◀')
# #         next_btn = QPushButton('▶')
# #         prev_btn.clicked.connect(self.show_prev)
# #         next_btn.clicked.connect(self.show_next)
# #         nav.addWidget(prev_btn)
# #         nav.addStretch()
# #         nav.addWidget(next_btn)
# #         pp_layout.addLayout(nav)
# #         self.stack.addWidget(self.pre_page)

# #         main = QWidget()
# #         m_layout = QHBoxLayout(main)
# #         m_layout.addWidget(sidebar)
# #         m_layout.addWidget(self.stack, 1)
# #         self.setCentralWidget(main)

# #         self.cat_list.resizeEvent = self.adjust_grid_size

# #         self.update_texts()
# #         self.load_categories()
# #         if self.categories:
# #             self.status_mode = 'completed'
# #             self.status_lbl.setText(TEXTS[self.current_lang]['completed'].format(len(self.categories)))
# #             self.stack.setCurrentIndex(1)
# #         else:
# #             self.status_mode = 'ready'
# #             self.status_lbl.setText(TEXTS[self.current_lang]['ready'])
# #             self.stack.setCurrentIndex(0)

# #     def _upload_button_style(self, dark=False):
# #         if dark:
# #             bg = "#0A84FF"  # 深色模式下略微亮蓝色
# #             hover = "#339CFF"
# #             pressed = "#0060DF"
# #             text_color = "white"
# #         else:
# #             bg = "#007AFF"  # 浅色苹果蓝
# #             hover = "#339CFF"
# #             pressed = "#005BBB"
# #             text_color = "white"
# #         return f"""
# #             QPushButton {{
# #                 background-color: {bg};
# #                 color: {text_color};
# #                 border-radius: 12px;
# #                 padding: 10px 20px;
# #                 font-size: 16px;
# #                 font-weight: 500;
# #             }}
# #             QPushButton:hover {{
# #                 background-color: {hover};
# #             }}
# #             QPushButton:pressed {{
# #                 background-color: {pressed};
# #             }}
# #         """


# #     def update_texts(self):
# #         t = TEXTS[self.current_lang]
# #         self.welcome_lbl.setText(t['welcome'])
# #         self.upload_btn.setText(t['upload'])
# #         self.dark_chk.setText(t['dark'])
# #         self.back_btn.setText(t['back'])
# #         self.back2_btn.setText(t['back'])

# #         if self.status_mode == 'ready':
# #             self.status_lbl.setText(t['ready'])
# #         elif self.status_mode == 'classifying':
# #             self.status_lbl.setText(t['classifying'])
# #         elif self.status_mode == 'completed':
# #             self.status_lbl.setText(t['completed'].format(len(self.categories)))
# #         # loading state is updated dynamically during processing

# #     def on_lang_change(self, index):
# #         codes = ['en', 'zh', 'zh-tw', 'ja', 'fr', 'ko', 'ru', 'ar', 'es', 'de']
# #         self.current_lang = codes[index]
# #         self.update_texts()

# #     def toggle_theme(self, checked):
# #         app = QApplication.instance()
# #         pal = app.palette()
# #         if checked:
# #             pal.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
# #             pal.setColor(QPalette.ColorRole.WindowText, QColor('white'))
# #             self.upload_btn.setStyleSheet(self._upload_button_style(dark=True))#new
# #         else:
# #             pal = app._default_palette
# #             self.upload_btn.setStyleSheet(self._upload_button_style(dark=False))#new
# #         app.setPalette(pal)

# #     def on_upload(self):
# #         files, _ = QFileDialog.getOpenFileNames(self, TEXTS[self.current_lang]['upload'], "", "Images (*.png *.jpg *.jpeg)")
# #         if not files:
# #             return
# #         self.status_mode = 'classifying'
# #         self.status_lbl.setText(TEXTS[self.current_lang]['classifying'])
# #         self.progress.show()
# #         self.progress.setRange(0, 0)
# #         self.thread = ClassifyThread(files)
# #         self.thread.finished.connect(self.on_classified)
# #         self.thread.start()

# #     def on_classified(self, result):
# #         self.progress.hide()
# #         if isinstance(result, Exception):
# #             self.status_lbl.setText(f"Error: {result}")
# #             return
# #         self.categories = result
# #         self.load_categories()
# #         self.status_mode = 'completed'
# #         self.status_lbl.setText(TEXTS[self.current_lang]['completed'].format(len(self.categories)))
# #         self.stack.setCurrentIndex(1)

# #     def load_categories(self):
# #         sd = 'sorted'
# #         self.categories.clear()
# #         self.album_list.clear()
# #         if not os.path.isdir(sd):
# #             return
# #         for sub in sorted(os.listdir(sd)):
# #             p = os.path.join(sd, sub)
# #             if not os.path.isdir(p):
# #                 continue
# #             imgs = [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
# #             if not imgs:
# #                 continue
# #             cover = imgs[0]
# #             icon = self._make_circle(cover, 150)
# #             self.categories[sub] = imgs
# #             item = QListWidgetItem(QIcon(icon), sub)
# #             item.setData(Qt.ItemDataRole.UserRole, sub)
# #             self.album_list.addItem(item)

# #     def open_category(self, item):
# #         cat = item.data(Qt.ItemDataRole.UserRole)
# #         self.cat_title.setText(cat)
# #         self.cat_list.clear()
# #         self.current_images = self.categories.get(cat, [])
# #         self.stack.setCurrentIndex(2)

# #         def load_thumb(path):
# #             from PyQt6.QtGui import QImageReader
# #             cache_dir = os.path.join('thumb_cache')
# #             os.makedirs(cache_dir, exist_ok=True)
# #             mtime = os.path.getmtime(path)
# #             thumb_path = os.path.join(cache_dir, os.path.basename(path) + f'_{int(mtime)}_thumb.jpg')
# #             # clean older cache
# #             for f in os.listdir(cache_dir):
# #                 if f.startswith(os.path.basename(path)) and f != os.path.basename(thumb_path):
# #                     try:
# #                         os.remove(os.path.join(cache_dir, f))
# #                     except:
# #                         pass
# #             if os.path.exists(thumb_path):
# #                 pix = QPixmap(thumb_path)
# #                 if not pix.isNull():
# #                     return pix, path
# #                 else:
# #                     os.remove(thumb_path)  # remove corrupted cache and rebuild

# #             reader = QImageReader(path)
# #             reader.setAutoTransform(True)
# #             # reader.setScaledSize(QSize(9999, 180))  # removed to prevent distortion  # enforce max height 180px, width auto-computed  # Set width only, height auto-computed to preserve aspect
# #             image = reader.read()
# #             if not image.isNull():
# #                 scaled = image.scaledToHeight(180, Qt.TransformationMode.SmoothTransformation)
# #                 scaled.save(thumb_path, 'JPG')
# #                 return QPixmap.fromImage(scaled), path
# #             if not image.isNull():
                
# #                 return None

# #         num_images = len(self.current_images)
# #         self.progress.show()
# #         self.progress.setRange(0, num_images)
# #         start_time = time.time()
# #         self.status_mode = 'loading'

# #         loaded_pixmaps = [None] * len(self.current_images)
# #         with concurrent.futures.ThreadPoolExecutor(max_workers=math.ceil(cpu_count() * 0.66)) as executor:
# #             futures = {executor.submit(load_thumb, path): path for path in self.current_images}
# #             future_to_index = {fut: idx for idx, fut in enumerate(futures)}
# #             for i, future in enumerate(concurrent.futures.as_completed(futures)):
# #                 idx = future_to_index[future]
# #                 result = future.result()
# #                 if result:
# #                     loaded_pixmaps[idx] = result
# #                 self.progress.setValue(i + 1)
# #                 elapsed = time.time() - start_time
# #                 remaining = (elapsed / (i + 1)) * (num_images - i - 1)
# #                 self.status_lbl.setText(TEXTS[self.current_lang]['loading'].format(i + 1, num_images, int(remaining)))

# #         view_width = self.cat_list.viewport().width()
# #         spacing = self.cat_list.spacing()
# #         min_cols = 3
# #         target_width = max(120, min((view_width - spacing * 2 * min_cols) // min_cols, 300))
# #         max_height = max([pix.height() for pix, _ in loaded_pixmaps]) if loaded_pixmaps else 100
# #         icon_size = QSize(target_width, max_height)  # e.g., 4:3 ratio
# #         # skip setting global icon size since we set per-item
# #         # skip setting global grid size since we set per-item

# #         for i, (pix, path) in enumerate(loaded_pixmaps):
# #             if pix is None:
# #                 continue
# #             scaled = pix.scaledToHeight(180, Qt.TransformationMode.SmoothTransformation)
# #             self.cat_list.setIconSize(scaled.size())
# #             icon = QIcon(scaled)
# #             item = QListWidgetItem()
# #             item.setIcon(icon)
# #             item.setData(Qt.ItemDataRole.UserRole, path)
# #             item.setToolTip(os.path.basename(path))
# #             item.setSizeHint(scaled.size())
# #             self.cat_list.addItem(item)

# #         self.progress.hide()
# #         self.status_mode = 'completed'
# #         self.status_lbl.setText(TEXTS[self.current_lang]['completed'].format(len(self.categories)))
# #         self.status_mode = 'completed'
# #         self.status_lbl.setText(TEXTS[self.current_lang]['completed'].format(len(self.categories)))

# #     def open_preview(self, item):
# #         idx = self.cat_list.row(item)
# #         self.current_index = idx
# #         self._update_preview()
# #         self.stack.setCurrentIndex(3)
# #         self.pre_lbl.setMinimumSize(0, 0)  # allow window to shrink after preview

# #     def show_prev(self):
# #         if self.current_index > 0:
# #             self.current_index -= 1
# #             self._update_preview()

# #     def show_next(self):
# #         if self.current_index < len(self.current_images) - 1:
# #             self.current_index += 1
# #             self._update_preview()

# #     def _update_preview(self):
# #         img_path = self.current_images[self.current_index]
# #         pix = QPixmap(img_path)
# #         if pix.isNull():
# #             return
# #         self.pre_lbl.setMinimumSize(1, 1)
# #         self.pre_lbl.setPixmap(pix)

# #     def adjust_grid_size(self, event):
# #         view_width = self.cat_list.viewport().width()
# #         spacing = self.cat_list.spacing()
# #         if self.cat_list.count() == 0:
# #             QListWidget.resizeEvent(self.cat_list, event)
# #             return

# #         item = self.cat_list.item(0)
# #         size = self.cat_list.iconSize()
# #         icon_width = size.width()
# #         icon_height = size.height()
# #         cols = max(1, view_width // (icon_width + spacing * 2))
# #         grid_width = view_width // cols - spacing
# #         self.cat_list.setGridSize(QSize(grid_width, icon_height + 30))
# #         QListWidget.resizeEvent(self.cat_list, event)

# #     def _make_circle(self, path, size):
# #         pix = QPixmap(path)
# #         side = min(pix.width(), pix.height())
# #         x = (pix.width() - side) // 2
# #         y = (pix.height() - side) // 2
# #         pix = pix.copy(x, y, side, side)
# #         pix = pix.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
# #         out = QPixmap(size, size)
# #         out.fill(Qt.GlobalColor.transparent)
# #         p = QPainter(out)
# #         p.setRenderHint(QPainter.RenderHint.Antialiasing)
# #         p.setBrush(QBrush(pix))
# #         p.setPen(Qt.PenStyle.NoPen)
# #         p.drawEllipse(0, 0, size, size)
# #         p.end()
# #         return out

# # if __name__ == '__main__':
# #     app = QApplication(sys.argv)
# #     app._default_palette = app.palette()
# #     window = MainWindow()
# #     window.show()
# #     sys.exit(app.exec())

# import os
# import sys
# import shutil
# import concurrent.futures
# import math
# import time
# from multiprocessing import cpu_count
# from PyQt6.QtWidgets import (
#     QSizePolicy,
#     QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
#     QPushButton, QLabel, QFileDialog, QProgressBar,
#     QStackedWidget, QListWidget, QListWidgetItem, QComboBox, QCheckBox
# )
# from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QPalette
# from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
# from PyQt6.QtGui import QFont

# import Classifierpy as Classifier

# class ScaledPreview(QLabel):
#     def __init__(self):
#         super().__init__()
#         self.pix = None
#         self.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
#         self.setStyleSheet("background-color: black;")

#     def setPixmap(self, pixmap):
#         self.pix = pixmap
#         self.update()

#     def paintEvent(self, event):
#         super().paintEvent(event)
#         if not self.pix:
#             return
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
#         painter.fillRect(self.rect(), self.palette().color(QPalette.ColorRole.Window))
#         scaled = self.pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
#         x = (self.width() - scaled.width()) // 2
#         y = (self.height() - scaled.height()) // 2
#         painter.drawPixmap(x, y, scaled)
#         painter.end()
# from labels import LABEL_DISPLAY

# TEXTS = {
#     'en': {
#         'welcome': 'Welcome to LumoSort!', 'upload': 'Upload Images', 'dark': 'Dark Mode', 'back': '← Back', 'ready': 'Ready', 'classifying': 'Classifying...', 'completed': '{} categories loaded', 'loading': 'Loading... {}/{} ETA: {}s'
#     },
#     'zh': {
#         'welcome': '欢迎使用 LumoSort！', 'upload': '上传图片', 'dark': '夜间模式', 'back': '← 返回', 'ready': '就绪', 'classifying': '正在分类...', 'completed': '已加载 {} 个类别', 'loading': '加载中... {}/{} 剩余约 {} 秒'
#     },
#     'zh-tw': {
#         'welcome': '歡迎使用 LumoSort！', 'upload': '上傳圖片', 'dark': '夜間模式', 'back': '← 返回', 'ready': '就緒', 'classifying': '正在分類...', 'completed': '已載入 {} 個類別', 'loading': '載入中... {}/{} 剩餘約 {} 秒'
#     },
#     'ja': {
#         'welcome': 'LumoSort へようこそ！', 'upload': '画像を選択', 'dark': 'ダークモード', 'back': '← 戻る', 'ready': '準備完了', 'classifying': '分類中...', 'completed': '{} カテゴリを読み込み済み', 'loading': '読み込み中... {}/{} 残り約 {} 秒'
#     },
#     'fr': {
#         'welcome': 'Bienvenue sur LumoSort !', 'upload': 'Importer des images', 'dark': 'Mode sombre', 'back': '← Retour', 'ready': 'Prêt', 'classifying': 'Classification en cours...', 'completed': '{} catégories chargées', 'loading': 'Chargement... {}/{} estimé {}s'
#     },
#     'ko': {
#         'welcome': 'LumoSort에 오신 것을 환영합니다!', 'upload': '이미지 업로드', 'dark': '다크 모드', 'back': '← 뒤로', 'ready': '준비 완료', 'classifying': '분류 중...', 'completed': '{}개 카테고리 로드됨', 'loading': '로드 중... {}/{} 남은 시간 {}초'
#     },
#     'ru': {
#         'welcome': 'Добро пожаловать в LumoSort!', 'upload': 'Загрузить изображения', 'dark': 'Темная тема', 'back': '← Назад', 'ready': 'Готово', 'classifying': 'Классификация...', 'completed': 'Загружено категорий: {}', 'loading': 'Загрузка... {}/{} осталось ~{} сек'
#     },
#     'ar': {
#         'welcome': 'مرحبًا بك في LumoSort!', 'upload': 'تحميل الصور', 'dark': 'الوضع الليلي', 'back': '← رجوع', 'ready': 'جاهز', 'classifying': 'جارٍ التصنيف...', 'completed': '{} فئة تم تحميلها', 'loading': 'جارٍ التحميل... {}/{} المتبقي: {} ث'
#     },
#     'es': {
#         'welcome': '¡Bienvenido a LumoSort!', 'upload': 'Subir imágenes', 'dark': 'Modo oscuro', 'back': '← Atrás', 'ready': 'Listo', 'classifying': 'Clasificando...', 'completed': '{} categorías cargadas', 'loading': 'Cargando... {}/{} ETA: {}s'
#     },
#     'de': {
#         'welcome': 'Willkommen bei LumoSort!', 'upload': 'Bilder hochladen', 'dark': 'Dunkelmodus', 'back': '← Zurück', 'ready': 'Bereit', 'classifying': 'Klassifizierung...', 'completed': '{} Kategorien geladen', 'loading': 'Lädt... {}/{} verbleibend: {}s'
#     }
# }

# # # Clear outdated thumbnails on each launch
# # if os.path.exists("thumb_cache"):
# #     try:
# #         for f in os.listdir("thumb_cache"):
# #             if f.endswith("_thumb.jpg"):
# #                 os.remove(os.path.join("thumb_cache", f))
# #     except Exception:
# #         pass

# class ClassifyThread(QThread):
#     finished = pyqtSignal(object)

#     def __init__(self, paths):
#         super().__init__()
#         self.paths = paths

#     def run(self):
#         try:
#             results = Classifier.classify_images_by_clip(self.paths, 'sorted')
#         except Exception as e:
#             results = e
#         self.finished.emit(results)


# class TypingLabel(QLabel):
#     def __init__(self, text, interval=100):
#         super().__init__()
#         self.full_text = text
#         self.interval = interval
#         self.index = 0
#         self.cursor_visible = True
#         self.setText("")
#         self.timer = QTimer()
#         self.cursor_timer = QTimer()
#         self.timer.timeout.connect(self._next_char)
#         self.cursor_timer.timeout.connect(self._blink_cursor)
#         self.timer.start(self.interval)
#         self.cursor_timer.start(500)

#     def _next_char(self):
#         if self.index < len(self.full_text):
#             self.index += 1
#             self.update_text()
#         else:
#             self.timer.stop()

#     def _blink_cursor(self):
#         self.cursor_visible = not self.cursor_visible
#         self.update_text()

#     def update_text(self):
#         cursor = "|" if self.cursor_visible else " "
#         self.setText(self.full_text[:self.index] + cursor)

#     def restart(self, text=None):
#         if text:
#             self.full_text = text
#         self.index = 0
#         self.cursor_visible = True
#         self.timer.start(self.interval)
#         if not self.cursor_timer.isActive():
#             self.cursor_timer.start(500)

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle('LumoSort')
#         self.resize(1000, 700)

#         self.current_lang = 'en'
#         self.status_mode = 'ready'
#         self.categories = {}
#         self.current_images = []
#         self.current_index = 0
#         self._flash_on = True
#         self.pixel_font = "Courier New"
#         # Sidebar
#         sidebar = QWidget()
#         sb_layout = QVBoxLayout(sidebar)
#         # self.upload_btn = QPushButton()
#         # self.upload_btn.clicked.connect(self.on_upload)

#         from PyQt6.QtWidgets import QGraphicsDropShadowEffect
#         # 上传按钮
#         self.upload_btn = QPushButton()
#         self.upload_btn.setText(TEXTS[self.current_lang]['upload'])
#         self.upload_btn.setMinimumHeight(48)
#         self.upload_btn.setStyleSheet(self._upload_button_style(dark=False))
#         self.upload_btn.clicked.connect(self.on_upload)

#         # 添加阴影
#         shadow = QGraphicsDropShadowEffect(self.upload_btn)
#         shadow.setBlurRadius(15)
#         shadow.setOffset(0, 3)
#         shadow.setColor(QColor(0, 0, 0, 80))
#         self.upload_btn.setGraphicsEffect(shadow)


#         self.dark_chk = QCheckBox()
#         self.dark_chk.toggled.connect(self.toggle_theme)
#         self.lang_combo = QComboBox()
#         self.lang_combo.addItems(['English', '简体中文', '繁體中文', '日本語', 'Français', '한국어', 'Русский', 'العربية', 'Español', 'Deutsch'])
#         self.lang_combo.currentIndexChanged.connect(self.on_lang_change)
#         self.progress = QProgressBar()
#         self.progress.hide()

#         # self.status_lbl = QLabel()
#         status_layout = QHBoxLayout()
#         self.status_light = QLabel()
#         self.status_light.setFixedSize(12, 12)
#         self.status_light.setStyleSheet("border-radius: 6px; background-color: green;")
#         status_layout.addWidget(self.status_light)
#         status_layout.addSpacing(6)
#         self.status_lbl = QLabel()
#         status_layout.addWidget(self.status_lbl)
#         status_layout.addStretch()

#         sb_layout.addWidget(self.upload_btn)
#         sb_layout.addWidget(self.dark_chk)
#         sb_layout.addWidget(self.lang_combo)
#         sb_layout.addStretch()
#         sb_layout.addWidget(self.progress)
#         sb_layout.addLayout(status_layout)
#         sidebar.setFixedWidth(200)

#         # sb_layout.addWidget(self.upload_btn)
#         # sb_layout.addWidget(self.dark_chk)
#         # sb_layout.addWidget(self.lang_combo)
#         # sb_layout.addStretch()
#         # sb_layout.addWidget(self.progress)
#         # sb_layout.addWidget(self.status_lbl)
#         # sidebar.setFixedWidth(200)

#         # Pages
#         self.stack = QStackedWidget()

#         self.welcome_page = QWidget()
#         wp_layout = QVBoxLayout(self.welcome_page)
#         wp_layout.addStretch()
#         # self.welcome_lbl = QLabel()
#         # self.welcome_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.welcome_lbl = TypingLabel(TEXTS[self.current_lang]['welcome'])
#         self.welcome_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.welcome_lbl.setFont(QFont(self.pixel_font, 18))

#         wp_layout.addWidget(self.welcome_lbl)
#         wp_layout.addStretch()
#         self.stack.addWidget(self.welcome_page)

#         self.album_list = QListWidget()
#         self.album_list.setViewMode(QListWidget.ViewMode.IconMode)
#         self.album_list.setIconSize(QSize(150, 150))
#         self.album_list.setResizeMode(QListWidget.ResizeMode.Adjust)
#         self.album_list.setSpacing(20)
#         self.album_list.itemClicked.connect(self.open_category)
#         self.stack.addWidget(self.album_list)

#         self.cat_page = QWidget()
#         cp_layout = QVBoxLayout(self.cat_page)
#         # self.back_btn = QPushButton()
#         self.back_btn = QPushButton()
#         self.back_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: transparent;
#                 color: #007AFF;
#                 border: none;
#                 padding: 10px 16px;
#                 font-size: 16px;
#                 font-weight: 500;
#                 text-align: left;
#             }
#             QPushButton:hover {
#                 background-color: rgba(0, 122, 255, 0.1);
#             }
#         """)

#         self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
#         self.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
#         self.cat_title = QLabel()
#         self.cat_title.setStyleSheet('font-weight:bold; font-size:16px;')
#         cp_layout.addWidget(self.back_btn)
#         cp_layout.addWidget(self.cat_title)
#         self.cat_list = QListWidget()
#         self.cat_list.setViewMode(QListWidget.ViewMode.IconMode)
#         self.cat_list.setWrapping(True)
#         self.cat_list.setFlow(QListWidget.Flow.LeftToRight)
#         # self.cat_list.setGridSize(QSize(120, 120))  # disabled for per-item sizeHint
#         self.cat_list.setResizeMode(QListWidget.ResizeMode.Adjust)
#         self.cat_list.setUniformItemSizes(True)
#         self.cat_list.setWordWrap(True)
#         # self.cat_list.setIconSize(QSize(180, 180))  # disabled for per-item icon size
#         self.cat_list.setResizeMode(QListWidget.ResizeMode.Adjust)
#         self.cat_list.setSpacing(9)
#         self.cat_list.itemClicked.connect(self.open_preview)
#         cp_layout.addWidget(self.cat_list)
#         self.stack.addWidget(self.cat_page)

#         self.pre_page = QWidget()
#         pp_layout = QVBoxLayout(self.pre_page)
#         # self.back2_btn = QPushButton()
        
#         self.back2_btn = QPushButton()
#         self.back2_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: transparent;
#                 color: #007AFF;
#                 border: none;
#                 padding: 10px 16px;
#                 font-size: 16px;
#                 font-weight: 500;
#                 text-align: left;
#             }
#             QPushButton:hover {
#                 background-color: rgba(0, 122, 255, 0.1);
#             }
#         """)
#         self.back2_btn.setCursor(Qt.CursorShape.PointingHandCursor)
#         self.back2_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))


#         pp_layout.addWidget(self.back2_btn)
#         self.pre_lbl = ScaledPreview()
#         pp_layout.addWidget(self.pre_lbl)
#         nav = QHBoxLayout()
#         prev_btn = QPushButton('◀')
#         next_btn = QPushButton('▶')
#         prev_btn.clicked.connect(self.show_prev)
#         next_btn.clicked.connect(self.show_next)
#         nav.addWidget(prev_btn)
#         nav.addStretch()
#         nav.addWidget(next_btn)
#         pp_layout.addLayout(nav)
#         self.stack.addWidget(self.pre_page)

#         main = QWidget()
#         m_layout = QHBoxLayout(main)
#         m_layout.addWidget(sidebar)
#         m_layout.addWidget(self.stack, 1)
#         self.setCentralWidget(main)

#         self.cat_list.resizeEvent = self.adjust_grid_size

#         self.update_texts()
#         self.load_categories()
#         if self.categories:
#             self.status_mode = 'completed'
#             # self.status_lbl.setText(TEXTS[self.current_lang]['completed'].format(len(self.categories)))
#             self.set_status('completed', TEXTS[self.current_lang]['completed'].format(len(self.categories)))

#             self.stack.setCurrentIndex(1)
#         else:
#             self.status_mode = 'ready'
#             # self.status_lbl.setText(TEXTS[self.current_lang]['ready'])
#             self.set_status('ready', TEXTS[self.current_lang]['ready'])
#             self.stack.setCurrentIndex(0)

#     def _upload_button_style(self, dark=False):
#         if dark:
#             bg = "#0A84FF"  # 深色模式下略微亮蓝色
#             hover = "#339CFF"
#             pressed = "#0060DF"
#             text_color = "white"
#         else:
#             bg = "#007AFF"  # 浅色苹果蓝
#             hover = "#339CFF"
#             pressed = "#005BBB"
#             text_color = "white"
#         return f"""
#             QPushButton {{
#                 background-color: {bg};
#                 color: {text_color};
#                 border-radius: 12px;
#                 padding: 10px 20px;
#                 font-size: 16px;
#                 font-weight: 500;
#             }}
#             QPushButton:hover {{
#                 background-color: {hover};
#             }}
#             QPushButton:pressed {{
#                 background-color: {pressed};
#             }}
#         """


#     def set_status(self, mode, text):
#         self.status_mode = mode
#         self.status_lbl.setText(text)
#         if mode == 'ready':
#             self.status_light.setStyleSheet("border-radius: 6px; background-color: green;")
#             if hasattr(self, '_flash_timer'):
#                 self._flash_timer.stop()
#         elif mode == 'classifying':
#             self.status_light.setStyleSheet("border-radius: 6px; background-color: red;")
#             if not hasattr(self, '_flash_timer'):
#                 self._flash_timer = QTimer()
#                 self._flash_timer.timeout.connect(self._toggle_light_visibility)
#             self._flash_timer.start(500)
#         elif mode == 'completed':
#             if hasattr(self, '_flash_timer'):
#                 self._flash_timer.stop()
#             self.status_light.setStyleSheet("border-radius: 6px; background-color: green;")
#         else:
#             self.status_light.setStyleSheet("border-radius: 6px; background-color: orange;")
#             if hasattr(self, '_flash_timer'):
#                 self._flash_timer.stop()

#     def _toggle_light_visibility(self):
#         self._flash_on = not self._flash_on
#         color = "red" if self._flash_on else "#330000"
#         self.status_light.setStyleSheet(f"border-radius: 6px; background-color: {color};")

#     def update_texts(self):
#         t = TEXTS[self.current_lang]
#         self.welcome_lbl.restart(t['welcome'])
#         self.welcome_lbl.setText(t['welcome'])
#         self.upload_btn.setText(t['upload'])
#         self.dark_chk.setText(t['dark'])
#         self.back_btn.setText(t['back'])
#         self.back2_btn.setText(t['back'])

#         if self.status_mode == 'ready':
#             self.set_status('ready', t['ready'])
#         elif self.status_mode == 'classifying':
#             self.set_status('classifying', t['classifying'])
#         elif self.status_mode == 'completed':
#             self.set_status('completed', t['completed'].format(len(self.categories)))

#         # if self.status_mode == 'ready':
#         #     self.status_lbl.setText(t['ready'])
#         # elif self.status_mode == 'classifying':
#         #     self.status_lbl.setText(t['classifying'])
#         # elif self.status_mode == 'completed':
#         #     self.status_lbl.setText(t['completed'].format(len(self.categories)))
#         # loading state is updated dynamically during processing

#     def on_lang_change(self, index):
#         codes = ['en', 'zh', 'zh-tw', 'ja', 'fr', 'ko', 'ru', 'ar', 'es', 'de']
#         self.current_lang = codes[index]
#         self.update_texts()

#     def toggle_theme(self, checked):
#         app = QApplication.instance()
#         pal = app.palette()
#         if checked:
#             pal.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
#             pal.setColor(QPalette.ColorRole.WindowText, QColor('white'))
#             self.upload_btn.setStyleSheet(self._upload_button_style(dark=True))#new
#         else:
#             pal = app._default_palette
#             self.upload_btn.setStyleSheet(self._upload_button_style(dark=False))#new
#         app.setPalette(pal)

#     def on_upload(self):
#         files, _ = QFileDialog.getOpenFileNames(self, TEXTS[self.current_lang]['upload'], "", "Images (*.png *.jpg *.jpeg)")
#         if not files:
#             return
#         self.status_mode = 'classifying'
#         # self.status_lbl.setText(TEXTS[self.current_lang]['classifying'])
#         self.set_status('classifying', TEXTS[self.current_lang]['classifying'])
#         self.progress.show()
#         self.progress.setRange(0, 0)
#         self.thread = ClassifyThread(files)
#         self.thread.finished.connect(self.on_classified)
#         self.thread.start()

#     def on_classified(self, result):
#         self.progress.hide()
#         if isinstance(result, Exception):
#             self.status_lbl.setText(f"Error: {result}")
#             return
#         self.categories = result
#         self.load_categories()
#         self.status_mode = 'completed'
#         # self.status_lbl.setText(TEXTS[self.current_lang]['completed'].format(len(self.categories)))
#         self.set_status('completed', TEXTS[self.current_lang]['completed'].format(len(self.categories)))

#         self.stack.setCurrentIndex(1)

#     def load_categories(self):
#         sd = 'sorted'
#         self.categories.clear()
#         self.album_list.clear()
#         if not os.path.isdir(sd):
#             return
#         for sub in sorted(os.listdir(sd)):
#             p = os.path.join(sd, sub)
#             if not os.path.isdir(p):
#                 continue
#             imgs = [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
#             if not imgs:
#                 continue
#             cover = imgs[0]
#             icon = self._make_circle(cover, 150)
#             self.categories[sub] = imgs
#             item = QListWidgetItem(QIcon(icon), sub)
#             item.setData(Qt.ItemDataRole.UserRole, sub)
#             self.album_list.addItem(item)

#     def open_category(self, item):
#         cat = item.data(Qt.ItemDataRole.UserRole)
#         self.cat_title.setText(cat)
#         self.cat_list.clear()
#         self.current_images = self.categories.get(cat, [])
#         self.stack.setCurrentIndex(2)

#         def load_thumb(path):
#             from PyQt6.QtGui import QImageReader
#             cache_dir = os.path.join('thumb_cache')
#             os.makedirs(cache_dir, exist_ok=True)
#             mtime = os.path.getmtime(path)
#             thumb_path = os.path.join(cache_dir, os.path.basename(path) + f'_{int(mtime)}_thumb.jpg')
#             # clean older cache
#             for f in os.listdir(cache_dir):
#                 if f.startswith(os.path.basename(path)) and f != os.path.basename(thumb_path):
#                     try:
#                         os.remove(os.path.join(cache_dir, f))
#                     except:
#                         pass
#             if os.path.exists(thumb_path):
#                 pix = QPixmap(thumb_path)
#                 if not pix.isNull():
#                     return pix, path
#                 else:
#                     os.remove(thumb_path)  # remove corrupted cache and rebuild

#             reader = QImageReader(path)
#             reader.setAutoTransform(True)
#             # reader.setScaledSize(QSize(9999, 180))  # removed to prevent distortion  # enforce max height 180px, width auto-computed  # Set width only, height auto-computed to preserve aspect
#             image = reader.read()
#             if not image.isNull():
#                 scaled = image.scaledToHeight(180, Qt.TransformationMode.SmoothTransformation)
#                 scaled.save(thumb_path, 'JPG')
#                 return QPixmap.fromImage(scaled), path
#             if not image.isNull():
                
#                 return None

#         num_images = len(self.current_images)
#         self.progress.show()
#         self.progress.setRange(0, num_images)
#         start_time = time.time()
#         self.status_mode = 'loading'

#         loaded_pixmaps = [None] * len(self.current_images)
#         with concurrent.futures.ThreadPoolExecutor(max_workers=math.ceil(cpu_count() * 0.66)) as executor:
#             futures = {executor.submit(load_thumb, path): path for path in self.current_images}
#             future_to_index = {fut: idx for idx, fut in enumerate(futures)}
#             for i, future in enumerate(concurrent.futures.as_completed(futures)):
#                 idx = future_to_index[future]
#                 result = future.result()
#                 if result:
#                     loaded_pixmaps[idx] = result
#                 self.progress.setValue(i + 1)
#                 elapsed = time.time() - start_time
#                 remaining = (elapsed / (i + 1)) * (num_images - i - 1)
#                 self.status_lbl.setText(TEXTS[self.current_lang]['loading'].format(i + 1, num_images, int(remaining)))

#         view_width = self.cat_list.viewport().width()
#         spacing = self.cat_list.spacing()
#         min_cols = 3
#         target_width = max(120, min((view_width - spacing * 2 * min_cols) // min_cols, 300))
#         max_height = max([pix.height() for pix, _ in loaded_pixmaps]) if loaded_pixmaps else 100
#         icon_size = QSize(target_width, max_height)  # e.g., 4:3 ratio
#         # skip setting global icon size since we set per-item
#         # skip setting global grid size since we set per-item

#         for i, (pix, path) in enumerate(loaded_pixmaps):
#             if pix is None:
#                 continue
#             scaled = pix.scaledToHeight(180, Qt.TransformationMode.SmoothTransformation)
#             self.cat_list.setIconSize(scaled.size())
#             icon = QIcon(scaled)
#             item = QListWidgetItem()
#             item.setIcon(icon)
#             item.setData(Qt.ItemDataRole.UserRole, path)
#             item.setToolTip(os.path.basename(path))
#             item.setSizeHint(scaled.size())
#             self.cat_list.addItem(item)

#         self.progress.hide()
#         self.status_mode = 'completed'
#         self.set_status('completed', TEXTS[self.current_lang]['completed'].format(len(self.categories)))
#         self.status_mode = 'completed'
#         self.set_status('completed', TEXTS[self.current_lang]['completed'].format(len(self.categories)))


#     def open_preview(self, item):
#         idx = self.cat_list.row(item)
#         self.current_index = idx
#         self._update_preview()
#         self.stack.setCurrentIndex(3)
#         self.pre_lbl.setMinimumSize(0, 0)  # allow window to shrink after preview

#     def show_prev(self):
#         if self.current_index > 0:
#             self.current_index -= 1
#             self._update_preview()

#     def show_next(self):
#         if self.current_index < len(self.current_images) - 1:
#             self.current_index += 1
#             self._update_preview()

#     def _update_preview(self):
#         img_path = self.current_images[self.current_index]
#         pix = QPixmap(img_path)
#         if pix.isNull():
#             return
#         self.pre_lbl.setMinimumSize(1, 1)
#         self.pre_lbl.setPixmap(pix)

#     def adjust_grid_size(self, event):
#         view_width = self.cat_list.viewport().width()
#         spacing = self.cat_list.spacing()
#         if self.cat_list.count() == 0:
#             QListWidget.resizeEvent(self.cat_list, event)
#             return

#         item = self.cat_list.item(0)
#         size = self.cat_list.iconSize()
#         icon_width = size.width()
#         icon_height = size.height()
#         cols = max(1, view_width // (icon_width + spacing * 2))
#         grid_width = view_width // cols - spacing
#         self.cat_list.setGridSize(QSize(grid_width, icon_height + 30))
#         QListWidget.resizeEvent(self.cat_list, event)

#     def _make_circle(self, path, size):
#         pix = QPixmap(path)
#         side = min(pix.width(), pix.height())
#         x = (pix.width() - side) // 2
#         y = (pix.height() - side) // 2
#         pix = pix.copy(x, y, side, side)
#         pix = pix.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
#         out = QPixmap(size, size)
#         out.fill(Qt.GlobalColor.transparent)
#         p = QPainter(out)
#         p.setRenderHint(QPainter.RenderHint.Antialiasing)
#         p.setBrush(QBrush(pix))
#         p.setPen(Qt.PenStyle.NoPen)
#         p.drawEllipse(0, 0, size, size)
#         p.end()
#         return out

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     app._default_palette = app.palette()
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec())



