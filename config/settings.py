"""
Настройки приложения: пути, URL, версии
"""
import os
from pathlib import Path

# ==================== ОСНОВНОЕ ====================
APP_NAME = "Template Helper"
APP_TITLE_PANEL = "Work In Progress"  # Название панели для будущих фич
APP_AUTHOR = "Created by Nostro"

# ==================== GITHUB ====================
class GITHUB:
    """Настройки GitHub репозитория"""
    OWNER = "teja1337"
    REPO_NAME = "HelperTemplates"
    
    @staticmethod
    def get_api_url():
        """Получить URL GitHub API для последнего релиза"""
        return f"https://api.github.com/repos/{GITHUB.OWNER}/{GITHUB.REPO_NAME}/releases/latest"
    
    @staticmethod
    def get_release_url(version: str):
        """Получить URL для скачивания релиза"""
        return f"https://github.com/{GITHUB.OWNER}/{GITHUB.REPO_NAME}/releases/download/v{version}/Helper.exe"


# ==================== ПУТИ ====================
class PATHS:
    """Пути к файлам и директориям"""
    # Директория данных пользователя
    APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), 'Helper')
    
    # Файлы шаблонов
    TEMPLATES_CLIENTS = os.path.join(APP_DATA_DIR, "templates_clients.json")
    TEMPLATES_COLLEAGUES = os.path.join(APP_DATA_DIR, "templates_colleagues.json")
    
    # Системные файлы
    VERSION_FILE = "version.json"
    ICON_FILE = "icon.ico"
    UPDATER_EXE = "updater.exe"
    UPDATE_FILE = "Helper_update.exe"
    
    @staticmethod
    def get_version_path():
        """Получить путь к version.json в зависимости от режима запуска"""
        import sys
        
        if getattr(sys, 'frozen', False):
            # PyInstaller
            if hasattr(sys, '_MEIPASS'):
                return Path(sys._MEIPASS) / PATHS.VERSION_FILE
            else:
                return Path(sys.executable).parent / PATHS.VERSION_FILE
        else:
            # Запуск как скрипт
            return Path(__file__).parent.parent / PATHS.VERSION_FILE
    
    @staticmethod
    def get_icon_paths():
        """Получить возможные пути к иконке"""
        import sys
        
        icon_paths = []
        
        if getattr(sys, 'frozen', False):
            # Запуск как скомпилированное приложение
            exe_dir = Path(sys.executable).parent
            
            # 1. В папке вместе с .exe (обычно Program Files\Helper)
            icon_paths.append(exe_dir / PATHS.ICON_FILE)
            
            # 2. В распакованных файлах PyInstaller (если есть _MEIPASS)
            if hasattr(sys, '_MEIPASS'):
                icon_paths.append(Path(sys._MEIPASS) / PATHS.ICON_FILE)
        else:
            # Запуск как скрипт (development)
            icon_paths.append(Path(__file__).parent.parent / PATHS.ICON_FILE)
        
        # Вернуть только существующие пути
        return [p for p in icon_paths if p.exists()]
    
    @staticmethod
    def get_updater_path():
        """Получить путь к updater.exe"""
        import sys
        
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent / PATHS.UPDATER_EXE
        else:
            return Path("dist") / PATHS.UPDATER_EXE


# ==================== КАТЕГОРИИ ====================
class CATEGORIES:
    """Типы категорий шаблонов"""
    CLIENTS = "Клиенты"
    COLLEAGUES = "Коллеги"
    
    @staticmethod
    def get_all():
        """Получить список всех типов категорий"""
        return [CATEGORIES.CLIENTS, CATEGORIES.COLLEAGUES]
    
    @staticmethod
    def get_file_path(category_type: str):
        """Получить путь к файлу для типа категории"""
        if category_type == CATEGORIES.CLIENTS:
            return PATHS.TEMPLATES_CLIENTS
        elif category_type == CATEGORIES.COLLEAGUES:
            return PATHS.TEMPLATES_COLLEAGUES
        return None


# ==================== СООБЩЕНИЯ ====================
class MESSAGES:
    """Текстовые сообщения приложения"""
    # Статус-бар
    STATUS_READY = "Готов к работе"
    STATUS_COPIED = "✓ Текст скопирован"
    STATUS_ERROR_COPY = "✗ Ошибка копирования"
    STATUS_CATEGORY_ADDED = "✓ Категория добавлена"
    STATUS_CATEGORY_ERROR = "✗ Ошибка добавления категории"
    STATUS_SELECT_CATEGORY = "⚠ Сначала выберите категорию"
    STATUS_CATEGORY_RENAMED = "✓ Категория переименована"
    STATUS_ERROR_RENAME = "✗ Ошибка переименования"
    STATUS_CATEGORY_DELETED = "✓ Категория удалена"
    STATUS_ERROR_DELETE = "✗ Ошибка удаления"
    STATUS_TEMPLATE_ADDED = "✓ Шаблон добавлен"
    STATUS_TEMPLATE_ERROR = "✗ Ошибка добавления"
    STATUS_TEMPLATE_UPDATED = "✓ Шаблон обновлен"
    STATUS_TEMPLATE_DELETED = "✓ Шаблон удален"
    STATUS_ERROR_SAVE = "✗ Ошибка сохранения"
    STATUS_ENTER_TITLE = "✗ Введите название"
    STATUS_ENTER_TEXT = "✗ Введите текст"
    
    # Плейсхолдеры
    PLACEHOLDER_SELECT = "👆 Выберите категорию для просмотра шаблонов"
    PLACEHOLDER_EMPTY = "📝 В этой категории пока нет шаблонов"
    
    # Диалоги
    DIALOG_DELETE_CATEGORY = "Удалить категорию '{}'?\nВсе шаблоны будут удалены."
    DIALOG_DELETE_TEMPLATE = "Удалить этот шаблон?"
    
    # Обновления
    UPDATE_AVAILABLE = "🎉 Доступно обновление!"
    UPDATE_NEW_VERSION = "Новая версия: {}\n\nОбновить приложение сейчас?"
    UPDATE_DOWNLOADING = "Загрузка обновления..."
    UPDATE_ERROR = "❌ Не удалось загрузить обновление\n\nПопробуйте позже"


# ==================== ЭМОДЗИ ====================
class EMOJI:
    """Эмодзи для интерфейса"""
    LOCK = "🔒"
    COPY = "📋"
    EDIT = "✏️"
    ADD = "➕"
    DELETE = "🗑️"
    SAVE = "💾"
    CLOSE = "✕"
    CHECK = "✅"
    CROSS = "❌"
    PARTY = "🎉"
