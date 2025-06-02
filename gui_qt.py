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

# 移除直接导入
# import Classifierpy as Classifier

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
        'welcome': 'Welcome to LumoSort!',
        'upload': 'Upload Images',
        'dark': 'Dark Mode',
        'light': 'Light Mode',
        'back': '← Back',
        'ready': 'Ready',
        'classifying': 'Classifying...',
        'completed': '{} categories loaded',
        'loading': 'Loading... {}/{} ETA: {}s',
        'home': 'Home',
        'tools': 'Tools',
        'classified': 'Classified',
        'loading_categories': 'Loading categories...',
        'no_images': 'No classified images',
        'no_images_desc': 'Please upload and classify images first.',
        'processing': 'Processing Images',
        'input_folder': 'Input Folder',
        'output_folder': 'Output Folder',
        'browse': 'Browse',
        'background_style': 'Background Style',
        'processing_log': 'Processing Log',
        'process_images': 'Process Images',
        'select_input': 'Select Input Folder',
        'select_output': 'Select Output Folder',
        'error': 'Error',
        'select_folders': 'Please select both input and output folders.',
        'bg_styles': [
            '1. Main Color Background',
            '2. Main Color Circle',
            '3. Blur Background',
            '4. White Background',
            '5. Custom Parameters'
        ]
    },
    'zh': {
        'welcome': '欢迎使用 LumoSort！',
        'upload': '上传图片',
        'dark': '夜间模式',
        'light': '日间模式',
        'back': '← 返回',
        'ready': '就绪',
        'classifying': '正在分类...',
        'completed': '已加载 {} 个类别',
        'loading': '加载中... {}/{} 剩余约 {} 秒',
        'home': '主页',
        'tools': '工具',
        'classified': '已分类',
        'loading_categories': '正在加载分类...',
        'no_images': '暂无分类图片',
        'no_images_desc': '请先上传并分类图片。',
        'processing': '图片处理',
        'input_folder': '输入文件夹',
        'output_folder': '输出文件夹',
        'browse': '浏览',
        'background_style': '背景样式',
        'processing_log': '处理日志',
        'process_images': '处理图片',
        'select_input': '选择输入文件夹',
        'select_output': '选择输出文件夹',
        'error': '错误',
        'select_folders': '请选择输入和输出文件夹。',
        'bg_styles': [
            '1. 主色调背景',
            '2. 主色调圆形背景',
            '3. 模糊背景',
            '4. 纯白背景',
            '5. 自定义参数'
        ]
    },
    'zh-tw': {
        'welcome': '歡迎使用 LumoSort！',
        'upload': '上傳圖片',
        'dark': '夜間模式',
        'light': '日間模式',
        'back': '← 返回',
        'ready': '就緒',
        'classifying': '正在分類...',
        'completed': '已載入 {} 個類別',
        'loading': '載入中... {}/{} 剩餘約 {} 秒',
        'home': '主頁',
        'tools': '工具',
        'classified': '已分類',
        'loading_categories': '正在載入分類...',
        'no_images': '暫無分類圖片',
        'no_images_desc': '請先上傳並分類圖片。',
        'processing': '圖片處理',
        'input_folder': '輸入資料夾',
        'output_folder': '輸出資料夾',
        'browse': '瀏覽',
        'background_style': '背景樣式',
        'processing_log': '處理日誌',
        'process_images': '處理圖片',
        'select_input': '選擇輸入資料夾',
        'select_output': '選擇輸出資料夾',
        'error': '錯誤',
        'select_folders': '請選擇輸入和輸出資料夾。',
        'bg_styles': [
            '1. 主色調背景',
            '2. 主色調圓形背景',
            '3. 模糊背景',
            '4. 純白背景',
            '5. 自定義參數'
        ]
    },
    'ja': {
        'welcome': 'LumoSort へようこそ！',
        'upload': '画像をアップロード',
        'dark': 'ダークモード',
        'light': 'ライトモード',
        'back': '← 戻る',
        'ready': '準備完了',
        'classifying': '分類中...',
        'completed': '{} カテゴリを読み込み済み',
        'loading': '読み込み中... {}/{} 残り約 {} 秒',
        'home': 'ホーム',
        'tools': 'ツール',
        'classified': '分類済み',
        'loading_categories': 'カテゴリを読み込み中...',
        'no_images': '分類された画像がありません',
        'no_images_desc': '画像をアップロードして分類してください。',
        'processing': '画像処理',
        'input_folder': '入力フォルダ',
        'output_folder': '出力フォルダ',
        'browse': '参照',
        'background_style': '背景スタイル',
        'processing_log': '処理ログ',
        'process_images': '画像を処理',
        'select_input': '入力フォルダを選択',
        'select_output': '出力フォルダを選択',
        'error': 'エラー',
        'select_folders': '入力フォルダと出力フォルダを選択してください。',
        'bg_styles': [
            '1. メインカラー背景',
            '2. メインカラー円形',
            '3. ぼかし背景',
            '4. 白背景',
            '5. カスタムパラメータ'
        ]
    },
    'fr': {
        'welcome': 'Bienvenue sur LumoSort !',
        'upload': 'Importer',
        'dark': 'Mode sombre',
        'light': 'Mode clair',
        'back': '← Retour',
        'ready': 'Prêt',
        'classifying': 'Classification en cours...',
        'completed': '{} catégories chargées',
        'loading': 'Chargement... {}/{} estimé {}s',
        'home': 'Accueil',
        'tools': 'Outils',
        'classified': 'Classées',
        'loading_categories': 'Chargement des catégories...',
        'no_images': 'Aucune image classée',
        'no_images_desc': 'Veuillez importer et classer des images.',
        'processing': 'Traitement des images',
        'input_folder': 'Dossier source',
        'output_folder': 'Dossier destination',
        'browse': 'Parcourir',
        'background_style': 'Style d\'arrière-plan',
        'processing_log': 'Journal de traitement',
        'process_images': 'Traiter les images',
        'select_input': 'Sélectionner le dossier source',
        'select_output': 'Sélectionner le dossier destination',
        'error': 'Erreur',
        'select_folders': 'Veuillez sélectionner les dossiers source et destination.',
        'bg_styles': [
            '1. Couleur principale',
            '2. Cercle couleur principale',
            '3. Arrière-plan flou',
            '4. Arrière-plan blanc',
            '5. Paramètres personnalisés'
        ]
    },
    'ko': {
        'welcome': 'LumoSort에 오신 것을 환영합니다!',
        'upload': '이미지 업로드',
        'dark': '다크 모드',
        'light': '라이트 모드',
        'back': '← 뒤로',
        'ready': '준비 완료',
        'classifying': '분류 중...',
        'completed': '{}개 카테고리 로드됨',
        'loading': '로드 중... {}/{} 남은 시간 {}초',
        'home': '홈',
        'tools': '도구',
        'classified': '분류됨',
        'loading_categories': '카테고리 로드 중...',
        'no_images': '분류된 이미지 없음',
        'no_images_desc': '이미지를 업로드하고 분류해 주세요.',
        'processing': '이미지 처리',
        'input_folder': '입력 폴더',
        'output_folder': '출력 폴더',
        'browse': '찾아보기',
        'background_style': '배경 스타일',
        'processing_log': '처리 로그',
        'process_images': '이미지 처리',
        'select_input': '입력 폴더 선택',
        'select_output': '출력 폴더 선택',
        'error': '오류',
        'select_folders': '입력 폴더와 출력 폴더를 선택해 주세요.',
        'bg_styles': [
            '1. 메인 컬러 배경',
            '2. 메인 컬러 원형',
            '3. 블러 배경',
            '4. 흰색 배경',
            '5. 사용자 정의 매개변수'
        ]
    },
    'ru': {
        'welcome': 'Добро пожаловать в LumoSort!',
        'upload': 'Загрузить изображения',
        'dark': 'Темная тема',
        'light': 'Светлая тема',
        'back': '← Назад',
        'ready': 'Готово',
        'classifying': 'Классификация...',
        'completed': 'Загружено категорий: {}',
        'loading': 'Загрузка... {}/{} осталось ~{} сек',
        'home': 'Главная',
        'tools': 'Инструменты',
        'classified': 'Классифицировано',
        'loading_categories': 'Загрузка категорий...',
        'no_images': 'Нет классифицированных изображений',
        'no_images_desc': 'Загрузите и классифицируйте изображения.',
        'processing': 'Обработка изображений',
        'input_folder': 'Исходная папка',
        'output_folder': 'Папка назначения',
        'browse': 'Обзор',
        'background_style': 'Стиль фона',
        'processing_log': 'Журнал обработки',
        'process_images': 'Обработать изображения',
        'select_input': 'Выберите исходную папку',
        'select_output': 'Выберите папку назначения',
        'error': 'Ошибка',
        'select_folders': 'Выберите исходную папку и папку назначения.',
        'bg_styles': [
            '1. Основной цвет фона',
            '2. Круг основного цвета',
            '3. Размытый фон',
            '4. Белый фон',
            '5. Пользовательские параметры'
        ]
    },
    'ar': {
        'welcome': 'مرحبًا بك في LumoSort!',
        'upload': 'تحميل الصور',
        'dark': 'الوضع الليلي',
        'light': 'الوضع النهاري',
        'back': '← رجوع',
        'ready': 'جاهز',
        'classifying': 'جارٍ التصنيف...',
        'completed': '{} فئة تم تحميلها',
        'loading': 'جارٍ التحميل... {}/{} المتبقي: {} ث',
        'home': 'الرئيسية',
        'tools': 'الأدوات',
        'classified': 'مصنفة',
        'loading_categories': 'جارٍ تحميل الفئات...',
        'no_images': 'لا توجد صور مصنفة',
        'no_images_desc': 'يرجى تحميل وتصنيف الصور أولاً.',
        'processing': 'معالجة الصور',
        'input_folder': 'مجلد الإدخال',
        'output_folder': 'مجلد الإخراج',
        'browse': 'تصفح',
        'background_style': 'نمط الخلفية',
        'processing_log': 'سجل المعالجة',
        'process_images': 'معالجة الصور',
        'select_input': 'اختر مجلد الإدخال',
        'select_output': 'اختر مجلد الإخراج',
        'error': 'خطأ',
        'select_folders': 'يرجى اختيار مجلدي الإدخال والإخراج.',
        'bg_styles': [
            '1. خلفية باللون الرئيسي',
            '2. دائرة باللون الرئيسي',
            '3. خلفية ضبابية',
            '4. خلفية بيضاء',
            '5. معلمات مخصصة'
        ]
    },
    'es': {
        'welcome': '¡Bienvenido a LumoSort!',
        'upload': 'Subir imágenes',
        'dark': 'Modo oscuro',
        'light': 'Modo claro',
        'back': '← Atrás',
        'ready': 'Listo',
        'classifying': 'Clasificando...',
        'completed': '{} categorías cargadas',
        'loading': 'Cargando... {}/{} ETA: {}s',
        'home': 'Inicio',
        'tools': 'Herramientas',
        'classified': 'Clasificadas',
        'loading_categories': 'Cargando categorías...',
        'no_images': 'No hay imágenes clasificadas',
        'no_images_desc': 'Por favor, sube y clasifica imágenes primero.',
        'processing': 'Procesando imágenes',
        'input_folder': 'Carpeta de entrada',
        'output_folder': 'Carpeta de salida',
        'browse': 'Examinar',
        'background_style': 'Estilo de fondo',
        'processing_log': 'Registro de procesamiento',
        'process_images': 'Procesar imágenes',
        'select_input': 'Seleccionar carpeta de entrada',
        'select_output': 'Seleccionar carpeta de salida',
        'error': 'Error',
        'select_folders': 'Por favor, selecciona las carpetas de entrada y salida.',
        'bg_styles': [
            '1. Fondo color principal',
            '2. Círculo color principal',
            '3. Fondo desenfocado',
            '4. Fondo blanco',
            '5. Parámetros personalizados'
        ]
    },
    'de': {
        'welcome': 'Willkommen bei LumoSort!',
        'upload': 'Bilder hochladen',
        'dark': 'Dunkelmodus',
        'light': 'Hellmodus',
        'back': '← Zurück',
        'ready': 'Bereit',
        'classifying': 'Klassifizierung...',
        'completed': '{} Kategorien geladen',
        'loading': 'Lädt... {}/{} verbleibend: {}s',
        'home': 'Start',
        'tools': 'Werkzeuge',
        'classified': 'Klassifiziert',
        'loading_categories': 'Lade Kategorien...',
        'no_images': 'Keine klassifizierten Bilder',
        'no_images_desc': 'Bitte laden Sie zuerst Bilder hoch und klassifizieren Sie sie.',
        'processing': 'Bildverarbeitung',
        'input_folder': 'Eingabeordner',
        'output_folder': 'Ausgabeordner',
        'browse': 'Durchsuchen',
        'background_style': 'Hintergrundstil',
        'processing_log': 'Verarbeitungsprotokoll',
        'process_images': 'Bilder verarbeiten',
        'select_input': 'Eingabeordner auswählen',
        'select_output': 'Ausgabeordner auswählen',
        'error': 'Fehler',
        'select_folders': 'Bitte wählen Sie Eingabe- und Ausgabeordner aus.',
        'bg_styles': [
            '1. Hauptfarbe Hintergrund',
            '2. Hauptfarbe Kreis',
            '3. Unscharfer Hintergrund',
            '4. Weißer Hintergrund',
            '5. Benutzerdefinierte Parameter'
        ]
    }
}

class ClassifyThread(QThread):
    finished = pyqtSignal(object)
    status_update = pyqtSignal(str)

    def __init__(self, paths):
        super().__init__()
        self.paths = paths

    def run(self):
        try:
            import Classifierpy
            self.status_update.emit("正在分类图片...")
            results = Classifierpy.classify_images_by_clip(self.paths, 'sorted', progress_callback=None)
            self.finished.emit(results)
        except Exception as e:
            self.finished.emit(e)

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
        self.current_lang = 'zh'  # 默认使用中文
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 设置大小策略
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 设置样式表
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
        input_group = QGroupBox()
        input_group.setObjectName("input_group")
        input_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        self.input_entry = QLineEdit()
        self.input_entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_entry.setPlaceholderText(TEXTS['zh']['select_input'])  # 默认中文，后续会更新
        input_browse = QPushButton()
        input_browse.setFixedWidth(60)
        input_browse.clicked.connect(self.choose_input_folder)
        input_layout.addWidget(self.input_entry)
        input_layout.addWidget(input_browse)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Output Folder
        output_group = QGroupBox()
        output_group.setObjectName("output_group")
        output_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        output_layout = QHBoxLayout()
        output_layout.setSpacing(10)
        self.output_entry = QLineEdit()
        self.output_entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.output_entry.setPlaceholderText(TEXTS['zh']['select_output'])  # 默认中文，后续会更新
        output_browse = QPushButton()
        output_browse.setFixedWidth(60)
        output_browse.clicked.connect(self.choose_output_folder)
        output_layout.addWidget(self.output_entry)
        output_layout.addWidget(output_browse)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Background Type
        bg_group = QGroupBox()
        bg_group.setObjectName("bg_group")
        bg_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        bg_layout = QVBoxLayout()
        self.bg_combo = QComboBox()
        self.bg_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.bg_combo.addItems(TEXTS['zh']['bg_styles'])  # 默认中文，后续会更新
        bg_layout.addWidget(self.bg_combo)
        bg_group.setLayout(bg_layout)
        layout.addWidget(bg_group)
        
        # Log Text
        log_group = QGroupBox()
        log_group.setObjectName("log_group")
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
        self.submit_btn = QPushButton()
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
        
        # 初始化文本
        self.update_texts('zh')  # 默认使用中文
            
        # 设置初始主题
        self.update_theme(QApplication.instance().palette().window().color().lightness() > 128)
            
    def update_texts(self, lang):
        """更新界面文本"""
        self.current_lang = lang  # 添加这行，保存当前语言
        t = TEXTS[lang]
        # 更新组标题
        for group in self.findChildren(QGroupBox):
            if group.objectName() == "input_group":
                group.setTitle(t['input_folder'])
            elif group.objectName() == "output_group":
                group.setTitle(t['output_folder'])
            elif group.objectName() == "bg_group":
                group.setTitle(t['background_style'])
            elif group.objectName() == "log_group":
                group.setTitle(t['processing_log'])
        
        # 更新输入框提示文本
        self.input_entry.setPlaceholderText(t['select_input'])
        self.output_entry.setPlaceholderText(t['select_output'])
        
        # 更新按钮文本
        for btn in self.findChildren(QPushButton):
            if btn == self.submit_btn:
                btn.setText(t['process_images'])
            else:
                btn.setText(t['browse'])
        
        # 更新背景样式选项
        current_index = self.bg_combo.currentIndex()
        self.bg_combo.clear()
        self.bg_combo.addItems(t['bg_styles'])
        self.bg_combo.setCurrentIndex(current_index)
            
    def choose_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, TEXTS[self.current_lang]['select_input'])
        if folder:
            self.input_entry.setText(folder)
            
    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, TEXTS[self.current_lang]['select_output'])
        if folder:
            self.output_entry.setText(folder)
            
    def process_images(self):
        """处理图片"""
        input_folder = self.input_entry.text()
        output_folder = self.output_entry.text()
        
        if not input_folder or not output_folder:
            QMessageBox.warning(self, TEXTS[self.current_lang]['error'], 
                              TEXTS[self.current_lang]['select_folders'])
            return
            
        # 禁用按钮，避免重复点击
        self.submit_btn.setEnabled(False)
        
        # 重置进度条
        self.progress_bar.setValue(0)
        self.progress_bar.setRange(0, 100)
        
        # 清空日志
        self.log_text.clear()
        
        # 创建处理线程
        self.processor = ImageProcessor(
            input_folder,
            output_folder,
            self.bg_combo.currentIndex() + 1  # 背景类型从1开始
        )
        
        # 连接信号
        self.processor.progress.connect(self.update_progress)
        self.processor.log.connect(self.update_log)
        self.processor.finished.connect(self.on_processing_finished)
        
        # 创建线程并启动
        self.process_thread = QThread()
        self.processor.moveToThread(self.process_thread)
        self.process_thread.started.connect(self.processor.run)
        self.process_thread.start()
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def update_log(self, text):
        """更新日志"""
        self.log_text.append(text)
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
    def on_processing_finished(self):
        """处理完成的回调"""
        # 停止线程
        self.process_thread.quit()
        self.process_thread.wait()
        
        # 重新启用按钮
        self.submit_btn.setEnabled(True)
        
        # 显示完成消息
        self.log_text.append("\n处理完成！")

    def update_theme(self, is_light):
        """更新主题样式"""
        self.setStyleSheet(self.light_style if is_light else self.dark_style)
        # 更新阴影颜色
        shadow_color = QColor(0, 0, 0, 25) if is_light else QColor(0, 0, 0, 40)
        for widget in self.findChildren(QGroupBox):
            if widget.graphicsEffect():
                widget.graphicsEffect().setColor(shadow_color)
        
        # 更新提交按钮样式
        if not is_light:
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
                    background-color: #666666;
                }
            """)
        else:
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
            import os
            
            # 检查输入文件夹是否存在
            if not os.path.exists(self.input_folder):
                raise FileNotFoundError(f"输入文件夹不存在: {self.input_folder}")
                
            # 检查输入文件夹是否包含图片
            image_files = [f for f in os.listdir(self.input_folder) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            if not image_files:
                raise ValueError(f"输入文件夹中没有找到图片文件: {self.input_folder}")
                
            # 检查输出文件夹是否可写
            if not os.path.exists(self.output_folder):
                try:
                    os.makedirs(self.output_folder)
                except Exception as e:
                    raise PermissionError(f"无法创建输出文件夹: {self.output_folder}\n错误: {str(e)}")
            elif not os.access(self.output_folder, os.W_OK):
                raise PermissionError(f"输出文件夹没有写入权限: {self.output_folder}")
                
            # 检查输入和输出路径是否相同
            if os.path.normpath(self.input_folder) == os.path.normpath(self.output_folder):
                raise ValueError("输入和输出文件夹不能相同")
                
            self.log.emit("开始处理图片...")
            self.log.emit(f"输入文件夹: {self.input_folder}")
            self.log.emit(f"输出文件夹: {self.output_folder}")
            self.log.emit(f"背景样式: {self.bg_type}")
            self.log.emit(f"找到 {len(image_files)} 个图片文件")
            self.log.emit("-------------------")
            
            # 创建进度回调
            def update_progress(value):
                self.progress.emit(value)
                
            # 创建日志回调
            def update_log(text):
                self.log.emit(text)
            
            # 处理图片
            process_images(
                self.input_folder, 
                self.output_folder,
                background=self.bg_type,
                progress_callback=update_progress,
                log_callback=update_log
            )
            
            self.log.emit("-------------------")
            self.log.emit("处理完成！")
            
        except FileNotFoundError as e:
            self.log.emit(f"错误: 文件未找到 - {str(e)}")
        except PermissionError as e:
            self.log.emit(f"错误: 权限不足 - {str(e)}")
        except ValueError as e:
            self.log.emit(f"错误: 参数无效 - {str(e)}")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log.emit(f"发生错误:\n{str(e)}\n\n详细信息:\n{error_details}")
        
        self.finished.emit()

class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(400, 300)  # 缩小加载窗口的大小
        self.setup_ui()

    def setup_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建内容容器
        content_widget = QWidget()
        content_widget.setStyleSheet("background: white; border-radius: 20px;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)  # 减小内边距
        content_layout.setSpacing(20)  # 减小间距
        
        # 加载图标
        icon_container = QWidget()
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "icon", "logo.ico")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(96, 96,  # 缩小图标大小
                                        Qt.AspectRatioMode.KeepAspectRatio, 
                                        Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
            icon_label.setFixedSize(96, 96)  # 缩小图标容器大小
        
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        # 为图标添加阴影效果
        icon_shadow = QGraphicsDropShadowEffect()
        icon_shadow.setBlurRadius(10)  # 减小阴影范围
        icon_shadow.setXOffset(0)
        icon_shadow.setYOffset(0)
        icon_shadow.setColor(QColor(0, 0, 0, 50))
        icon_label.setGraphicsEffect(icon_shadow)
        
        content_layout.addWidget(icon_container)

        # 加载文本
        self.loading_label = QLabel("正在初始化...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: #333333; font-size: 16px; margin: 10px; font-family: Microsoft YaHei")
        content_layout.addWidget(self.loading_label)

        # 进度条
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedSize(200, 4)  # 缩小进度条
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #E0E0E0;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background: #007AFF;
                border-radius: 2px;
            }
        """)
        progress_layout.addWidget(self.progress)
        content_layout.addWidget(progress_container)

        # 添加内容容器到主布局
        main_layout.addWidget(content_widget)

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)  # 减小阴影范围
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 40))
        content_widget.setGraphicsEffect(shadow)

    def center(self):
        """将窗口居中显示"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def update_theme(self, is_dark):
        """更新主题"""
        if is_dark:
            self.findChild(QWidget).setStyleSheet("background: #2D2D2D; border-radius: 20px;")
            self.loading_label.setStyleSheet("color: #FFFFFF; font-size: 16px; margin: 10px; font-family: Microsoft YaHei")
        else:
            self.findChild(QWidget).setStyleSheet("background: white; border-radius: 20px;")
            self.loading_label.setStyleSheet("color: #333333; font-size: 16px; margin: 10px; font-family: Microsoft YaHei")

class ModelLoadThread(QThread):
    finished = pyqtSignal(bool)  # True表示成功，False表示失败
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)  # 新增错误信号

    def run(self):
        try:
            self.status_update.emit("正在初始化...")
            import Classifierpy
            success = Classifierpy.initialize_model(self.status_update.emit)
            if not success:
                self.error_occurred.emit("模型初始化失败")
                self.finished.emit(False)
                return
            self.finished.emit(True)
        except Exception as e:
            import traceback
            error_msg = f"错误: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)  # 打印到控制台
            self.error_occurred.emit(error_msg)
            self.finished.emit(False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            # 创建加载界面
            self.loading_screen = LoadingScreen()
            self.loading_screen.center()
            self.loading_screen.show()

            # 启动模型加载线程
            self.load_thread = ModelLoadThread()
            self.load_thread.finished.connect(self.on_model_loaded)
            self.load_thread.status_update.connect(self.loading_screen.loading_label.setText)
            self.load_thread.error_occurred.connect(self.on_error)
            self.load_thread.start()

            # 延迟初始化主窗口
            self.init_started = False
            
            # 设置窗口大小和位置
            self.resize(960, 720)
            self.setMinimumSize(400, 300)
            
            # 居中显示窗口
            screen = QApplication.primaryScreen().geometry()
            size = self.geometry()
            self.move(
                (screen.width() - size.width()) // 2,
                (screen.height() - size.height()) // 2
            )
        except Exception as e:
            import traceback
            print(f"初始化错误: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(None, "错误", f"程序初始化失败: {str(e)}")
            sys.exit(1)

    def on_error(self, error_msg):
        """处理错误信息"""
        print(f"发生错误: {error_msg}")  # 打印到控制台
        # 确保错误消息框在主线程中显示
        QTimer.singleShot(0, lambda: QMessageBox.critical(self.loading_screen, "错误", error_msg))

    def on_model_loaded(self, success):
        try:
            if not self.init_started:
                self.init_started = True
                if success:
                    print("模型加载成功，开始初始化UI...")
                    self.setWindowTitle('LumoSort')
                    
                    self._window_icon = None
                    self._init_window_icon()

                    self.current_lang = 'en'
                    self.status_mode = 'ready'
                    self.categories = {}
                    self.current_images = []
                    self.current_index = 0
                    self._flash_on = True
                    self.pixel_font = "Courier New"
                    
                    print("开始设置UI组件...")
                    # 初始化UI组件
                    self.setup_basic_ui()
                    print("基础UI设置完成...")
                    
                    # 关闭加载界面并显示主窗口
                    self.loading_screen.close()
                    self.show()
                    print("主窗口显示完成...")
                else:
                    print("模型加载失败...")
                    QMessageBox.critical(self.loading_screen, "错误", "模型加载失败，请检查文件完整性。")
                    sys.exit(1)
        except Exception as e:
            import traceback
            error_msg = f"UI初始化错误: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            QMessageBox.critical(self.loading_screen, "错误", error_msg)
            sys.exit(1)

    def _init_window_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon", "logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def setup_basic_ui(self):
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

        # Home按钮
        self.home_btn = QPushButton()
        self.home_btn.setMinimumHeight(48)
        self.home_btn.setStyleSheet(self._upload_button_style(dark=False))
        self.home_btn.clicked.connect(self.on_home)
        
        # Home按钮的阴影
        home_shadow = QGraphicsDropShadowEffect(self.home_btn)
        home_shadow.setBlurRadius(15)
        home_shadow.setOffset(0, 3)
        home_shadow.setColor(QColor(0, 0, 0, 80))
        self.home_btn.setGraphicsEffect(home_shadow)

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
        self.tools_btn = QPushButton()
        self.tools_btn.setMinimumHeight(48)
        self.tools_btn.setStyleSheet(self._upload_button_style(dark=False))
        self.tools_btn.clicked.connect(self.on_tools)
        
        # Tools按钮的阴影
        tools_shadow = QGraphicsDropShadowEffect(self.tools_btn)
        tools_shadow.setBlurRadius(15)
        tools_shadow.setOffset(0, 3)
        tools_shadow.setColor(QColor(0, 0, 0, 80))
        self.tools_btn.setGraphicsEffect(tools_shadow)

        # 已分类按钮
        self.classified_btn = QPushButton()
        self.classified_btn.setMinimumHeight(48)
        self.classified_btn.setStyleSheet(self._upload_button_style(dark=False))
        self.classified_btn.clicked.connect(self.on_show_classified)
        
        # 已分类按钮的阴影
        classified_shadow = QGraphicsDropShadowEffect(self.classified_btn)
        classified_shadow.setBlurRadius(15)
        classified_shadow.setOffset(0, 3)
        classified_shadow.setColor(QColor(0, 0, 0, 80))
        self.classified_btn.setGraphicsEffect(classified_shadow)

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

        sb_layout.addWidget(self.home_btn)
        sb_layout.addWidget(self.upload_btn)
        sb_layout.addWidget(self.tools_btn)
        sb_layout.addWidget(self.classified_btn)
        sb_layout.addWidget(self.dark_chk)
        sb_layout.addWidget(self.lang_combo)
        sb_layout.addStretch()
        sb_layout.addWidget(self.progress)
        sb_layout.addLayout(status_layout)
        sidebar.setFixedWidth(200)

        # 创建主要内容区域的堆叠窗口
        self.main_stack = QStackedWidget()
        
        # 添加加载页面
        self.loading_page = QWidget()
        loading_layout = QVBoxLayout(self.loading_page)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 加载动画容器
        loading_container = QWidget()
        loading_container.setFixedSize(300, 200)
        loading_container.setStyleSheet("background-color: white; border-radius: 20px;")
        
        # 加载容器布局
        loading_container_layout = QVBoxLayout(loading_container)
        loading_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 加载进度条
        self.loading_progress = QProgressBar()
        self.loading_progress.setRange(0, 0)  # 设置为循环模式
        self.loading_progress.setFixedSize(200, 4)
        self.loading_progress.setTextVisible(False)
        self.loading_progress.setStyleSheet("QProgressBar {border: none; background: #E0E0E0; border-radius: 2px;} QProgressBar::chunk {background: #007AFF; border-radius: 2px;}")
        
        # 加载文本
        self.loading_label = QLabel("正在加载分类...")
        self.loading_label.setStyleSheet("color: #333333; font-size: 16px; margin-top: 15px;")
        
        loading_container_layout.addWidget(self.loading_progress)
        loading_container_layout.addWidget(self.loading_label)
        
        # 添加阴影效果
        container_shadow = QGraphicsDropShadowEffect()
        container_shadow.setBlurRadius(20)
        container_shadow.setXOffset(0)
        container_shadow.setYOffset(2)
        container_shadow.setColor(QColor(0, 0, 0, 40))
        loading_container.setGraphicsEffect(container_shadow)
        
        loading_layout.addWidget(loading_container)
        
        # 将加载页面添加到主堆叠窗口
        self.main_stack.addWidget(self.loading_page)
        
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
        self.cat_list.setSpacing(15)
        self.cat_list.setIconSize(QSize(159, 159))
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
        self.category_images_list.setSpacing(8)
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
        """更新所有界面文本"""
        t = TEXTS[self.current_lang]
        # 欢迎页面
        self.welcome_lbl.restart(t['welcome'])
        self.welcome_lbl.setText(t['welcome'])
        
        # 按钮文本
        self.upload_btn.setText(t['upload'])
        self.home_btn.setText(t['home'])
        self.tools_btn.setText(t['tools'])
        self.classified_btn.setText(t['classified'])
        self.dark_chk.setText(t['dark'] if not self.dark_chk.isChecked() else t['light'])
        
        # 返回按钮
        self.back_btn.setText(t['back'])
        self.back2_btn.setText(t['back'])
        self.back_to_categories_btn.setText(t['back'])

        # 工具页面
        if hasattr(self, 'tools_page'):
            self.tools_page.setWindowTitle(t['processing'])
            input_group = self.tools_page.findChild(QGroupBox, "input_group")
            if input_group:
                input_group.setTitle(t['input_folder'])
            output_group = self.tools_page.findChild(QGroupBox, "output_group")
            if output_group:
                output_group.setTitle(t['output_folder'])
            bg_group = self.tools_page.findChild(QGroupBox, "bg_group")
            if bg_group:
                bg_group.setTitle(t['background_style'])
            log_group = self.tools_page.findChild(QGroupBox, "log_group")
            if log_group:
                log_group.setTitle(t['processing_log'])
            
            # 更新按钮文本
            browse_buttons = self.tools_page.findChildren(QPushButton)
            for btn in browse_buttons:
                if btn.text() == "Browse":
                    btn.setText(t['browse'])
                elif btn.text() == "Process Images":
                    btn.setText(t['process_images'])
            
            # 更新下拉框选项
            bg_combo = self.tools_page.findChild(QComboBox)
            if bg_combo:
                current_index = bg_combo.currentIndex()
                bg_combo.clear()
                bg_combo.addItems(t['bg_styles'])
                bg_combo.setCurrentIndex(current_index)

        # 状态文本
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
        # 更新工具页面的文本
        if hasattr(self, 'tools_page'):
            self.tools_page.update_texts(self.current_lang)

    def toggle_theme(self, checked):
        app = QApplication.instance()
        pal = QPalette()
        t = TEXTS[self.current_lang]
        if checked:
            # 深色主题
            pal.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
            pal.setColor(QPalette.ColorRole.WindowText, QColor('white'))
            pal.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
            pal.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 50, 50))
            pal.setColor(QPalette.ColorRole.Text, QColor('white'))
            pal.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
            pal.setColor(QPalette.ColorRole.ButtonText, QColor('white'))
            self.upload_btn.setStyleSheet(self._upload_button_style(dark=True))
            self.dark_chk.setText(t['light'])
            self.tools_page.update_theme(False)
            # 更新加载页面的样式
            self.loading_page.findChild(QWidget).setStyleSheet("background-color: #2D2D2D; border-radius: 20px;")
            self.loading_label.setStyleSheet("color: #FFFFFF; font-size: 16px; margin-top: 15px;")
        else:
            # 浅色主题
            pal.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            pal.setColor(QPalette.ColorRole.WindowText, QColor('black'))
            pal.setColor(QPalette.ColorRole.Base, QColor('white'))
            pal.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
            pal.setColor(QPalette.ColorRole.Text, QColor('black'))
            pal.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            pal.setColor(QPalette.ColorRole.ButtonText, QColor('black'))
            self.upload_btn.setStyleSheet(self._upload_button_style(dark=False))
            self.dark_chk.setText(t['dark'])
            self.tools_page.update_theme(True)
            # 更新加载页面的样式
            self.loading_page.findChild(QWidget).setStyleSheet("background-color: white; border-radius: 20px;")
            self.loading_label.setStyleSheet("color: #333333; font-size: 16px; margin-top: 15px;")
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
            icon = self._make_circle(cover, 159)
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

    def on_show_classified(self):
        """显示已分类的图片"""
        # 首先显示加载页面
        self.main_stack.setCurrentWidget(self.loading_page)
        self.loading_label.setText(TEXTS[self.current_lang]['loading_categories'])
        
        # 使用QTimer延迟执行加载操作，让加载页面有时间显示
        QTimer.singleShot(100, self._load_classified_images)
    
    def _load_classified_images(self):
        """实际加载分类图片的操作"""
        if self._check_classified_images():
            # 如果有已分类的图片，加载并显示
            self.load_categories()
            self.main_stack.setCurrentWidget(self.classifier_widget)
            self.classifier_widget.setCurrentWidget(self.cat_page)
        else:
            # 如果没有已分类的图片，显示提示信息
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle(TEXTS[self.current_lang]['error'])
            msg.setText(TEXTS[self.current_lang]['no_images'])
            msg.setInformativeText(TEXTS[self.current_lang]['no_images_desc'])
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            # 返回主页
            self.main_stack.setCurrentWidget(self.classifier_widget)
            self.classifier_widget.setCurrentWidget(self.welcome_page)

    def setup_tools_page(self):
        """设置工具页面"""
        self.tools_page = ImageProcessingWidget()
        input_group = self.tools_page.findChild(QGroupBox, "input_group")
        if input_group:
            input_group.setObjectName("input_group")
        output_group = self.tools_page.findChild(QGroupBox, "output_group")
        if output_group:
            output_group.setObjectName("output_group")
        bg_group = self.tools_page.findChild(QGroupBox, "bg_group")
        if bg_group:
            bg_group.setObjectName("bg_group")
        log_group = self.tools_page.findChild(QGroupBox, "log_group")
        if log_group:
            log_group.setObjectName("log_group")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app._default_palette = app.palette()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())



