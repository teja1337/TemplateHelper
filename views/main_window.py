import customtkinter as ctk
from typing import TYPE_CHECKING
import threading
import time
import json
from pathlib import Path
import sys

if TYPE_CHECKING:
    from models.template_manager import TemplateManager

from views.template_widgets import CategoryHeader, TemplateWidget
from utils.clipboard import copy_to_clipboard
from utils.updater import AppUpdater

# Стандартизированные размеры шрифтов для консистентности
FONT_TITLE = ("Segoe UI", 14, "bold")  # Заголовок окна
FONT_BUTTON_EMOJI = ("Segoe UI", 13)  # Кнопки с эмодзи
FONT_BUTTON = ("Segoe UI", 12)  # Обычные кнопки
FONT_LABEL = ("Segoe UI", 11)  # Подписи
FONT_SMALL = ("Segoe UI", 10)  # Маленький текст

class MainWindow:
    """Главное окно приложения Хелпер с современным дизайном"""
    
    def __init__(self, root: ctk.CTk, template_manager: 'TemplateManager'):
        self.root = root
        self.template_manager = template_manager
        self.is_always_on_top = False  # Флаг для режима "всегда поверх"
        
        self.setup_window()
        self.setup_ui()
        self.update_templates_display()
        
        # Проверка обновлений при запуске
        self.check_updates_on_startup()
    
    @staticmethod
    def get_app_version():
        """Получить версию приложения из version.json"""
        try:
            # Определяем путь к version.json
            if getattr(sys, 'frozen', False):
                # Если запущен как .exe
                version_path = Path(sys.executable).parent / "version.json"
            else:
                # Если запущен как скрипт
                version_path = Path(__file__).parent.parent / "version.json"
            
            if version_path.exists():
                with open(version_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', '0.0.1')
        except Exception as e:
            print(f"Ошибка при получении версии: {e}")
        
        return "0.0.1"
    
    def setup_context_menu_for_widget(self, widget: ctk.CTkBaseClass) -> None:
        """Добавить горячие клавиши для текстового виджета"""
        # Добавляем горячие клавиши
        def make_copy_handler():
            def copy_handler(event=None):
                try:
                    if isinstance(widget, ctk.CTkTextbox):
                        text = widget.tag_ranges("sel")
                        if text:
                            text_content = widget.get(text[0], text[1])
                            self.root.clipboard_clear()
                            self.root.clipboard_append(text_content)
                            self.root.update()
                    return "break"
                except Exception:
                    return "break"
            return copy_handler
        
        def make_paste_handler():
            def paste_handler(event=None):
                try:
                    text = self.root.clipboard_get()
                    if isinstance(widget, ctk.CTkTextbox):
                        widget.insert(ctk.END, text)
                    return "break"
                except Exception:
                    return "break"
            return paste_handler
        
        def make_cut_handler():
            def cut_handler(event=None):
                try:
                    if isinstance(widget, ctk.CTkTextbox):
                        text = widget.tag_ranges("sel")
                        if text:
                            text_content = widget.get(text[0], text[1])
                            widget.delete(text[0], text[1])
                            self.root.clipboard_clear()
                            self.root.clipboard_append(text_content)
                            self.root.update()
                    return "break"
                except Exception:
                    return "break"
            return cut_handler
        
        def make_select_all_handler():
            def select_all_handler(event=None):
                if isinstance(widget, ctk.CTkTextbox):
                    widget.tag_add("sel", "1.0", ctk.END)
                elif isinstance(widget, ctk.CTkEntry):
                    widget.select_range(0, ctk.END)
                return "break"
            return select_all_handler
        
        # Горячие клавиши
        widget.bind('<Control-c>', make_copy_handler())
        widget.bind('<Control-v>', make_paste_handler())
        widget.bind('<Control-x>', make_cut_handler())
        widget.bind('<Control-a>', make_select_all_handler())
    
    def setup_window(self) -> None:
        """Настройка главного окна с современным дизайном"""
        self.root.title("Хелпер - оператор чата")
        
        # Начальный размер окна - 1000x800 (средний размер)
        window_width = 1000
        window_height = 800
        
        # Получаем размеры экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Центрируем окно
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Устанавливаем геометрию
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Устанавливаем минимальный размер окна
        self.root.minsize(800, 600)
        
        # Добавляем тень для окна без рамок (Windows 10/11)
        try:
            self.root.after(100, lambda: self.root.wm_attributes("-topmost", False))
        except Exception:
            pass
    
    def setup_ui(self) -> None:
        """Создание современного пользовательского интерфейса"""
        # Создание кастомной заголовочной панели (для окна без рамок)
        self.create_custom_titlebar()
        
        # Основной фрейм с отступом сверху
        main_frame = ctk.CTkFrame(self.root, fg_color="#1a1a1a")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=0, pady=(10, 0))
        
        # Заголовок с категориями
        self.category_header = CategoryHeader(
            parent=main_frame,
            categories=self.template_manager.get_categories(),
            category_types=self.template_manager.get_category_types(),
            on_category_select=self.on_category_selected,
            on_category_type_select=self.on_category_type_selected,
            on_add_category=self.add_category,
            on_edit_category=self.edit_category,
            on_add_template=self.add_template
        )
        
        # Область отображения шаблонов
        self.templates_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a")
        self.templates_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        # Статус-бар в правом нижнем углу
        self.setup_status_bar(main_frame)
        
        # Принудительно обновляем отображение для первой категории
        self.root.after(100, self.on_category_selected)
    
    def setup_status_bar(self, parent):
        """Настройка статус-бара"""
        status_frame = ctk.CTkFrame(parent, fg_color="#2b2b2b", height=40)
        status_frame.pack(fill=ctk.X, side=ctk.BOTTOM)
        status_frame.pack_propagate(False)
        
        # Левая часть статус-бара
        self.status_left = ctk.CTkLabel(
            status_frame, 
            text="Готов к работе", 
            text_color="#a0a0a0",
            font=("Segoe UI", 10)
        )
        self.status_left.pack(side=ctk.LEFT, padx=10, pady=10)
        
        # Правая часть статус-бара (для временных уведомлений)
        self.status_right = ctk.CTkLabel(
            status_frame, 
            text="", 
            text_color="#90EE90",
            font=("Segoe UI", 10)
        )
        self.status_right.pack(side=ctk.RIGHT, padx=10, pady=10)
    
    def show_status_message(self, message: str, duration: int = 2000):
        """Показать временное сообщение в статус-баре"""
        self.status_right.configure(text=message, text_color="#90EE90")
        
        # Запускаем таймер для скрытия сообщения
        def clear_message():
            time.sleep(duration / 1000)
            self.status_right.configure(text="")
        
        threading.Thread(target=clear_message, daemon=True).start()
    
    def create_custom_dialog(self, title: str, width: int, height: int) -> ctk.CTkToplevel:
        """Создает диалоговое окно с кастомным заголовком без рамок"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.overrideredirect(True)
        dialog.geometry(f"{width}x{height}")
        
        # Если главное окно закреплено, то закрепляем и диалог
        if self.is_always_on_top:
            dialog.wm_attributes("-topmost", True)
        
        # Центрирование диалога
        dialog.update_idletasks()
        x = (self.root.winfo_x() + (self.root.winfo_width() // 2)) - (width // 2)
        y = (self.root.winfo_y() + (self.root.winfo_height() // 2)) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Контейнер с обводкой для всего диалога
        border_frame = ctk.CTkFrame(
            dialog,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#1e1e1e",
            corner_radius=0
        )
        border_frame.pack(fill=ctk.BOTH, expand=True)
        
        # Создаем кастомный заголовок для диалога
        dialog_titlebar = ctk.CTkFrame(
            border_frame,
            fg_color="#1e1e1e",
            corner_radius=0,
            height=35
        )
        dialog_titlebar.pack(side=ctk.TOP, fill=ctk.X)
        dialog_titlebar.pack_propagate(False)
        
        # Название диалога
        dialog_title_label = ctk.CTkLabel(
            dialog_titlebar,
            text=title,
            font=("Segoe UI", 12, "bold"),
            text_color="#e0e0e0"
        )
        dialog_title_label.pack(side=ctk.LEFT, padx=12, pady=0)
        
        # Кнопка закрытия диалога
        dialog_close_button = ctk.CTkButton(
            dialog_titlebar,
            text="✕",
            font=("Arial", 14, "bold"),
            width=35,
            height=35,
            fg_color="transparent",
            hover_color="#e81123",
            text_color="#e0e0e0",
            command=dialog.destroy,
            corner_radius=0,
            border_width=0
        )
        dialog_close_button.pack(side=ctk.RIGHT)
        
        # Функциональность перемещения диалога
        dialog_drag_data = {"x": 0, "y": 0}
        
        def start_dialog_move(event):
            dialog_drag_data["x"] = event.x_root - dialog.winfo_x()
            dialog_drag_data["y"] = event.y_root - dialog.winfo_y()
        
        def do_dialog_move(event):
            x = event.x_root - dialog_drag_data["x"]
            y = event.y_root - dialog_drag_data["y"]
            dialog.geometry(f"+{x}+{y}")
        
        dialog_titlebar.bind("<Button-1>", start_dialog_move)
        dialog_titlebar.bind("<B1-Motion>", do_dialog_move)
        dialog_title_label.bind("<Button-1>", start_dialog_move)
        dialog_title_label.bind("<B1-Motion>", do_dialog_move)
        
        # Сохраняем ссылку на border_frame для добавления контента
        dialog.content_frame = border_frame
        
        return dialog
    
    def create_custom_titlebar(self) -> None:
        """Создает кастомную заголовочную панель с кнопкой закрытия и возможностью перемещения"""
        # Фрейм для заголовка
        titlebar = ctk.CTkFrame(
            self.root,
            fg_color="#1e1e1e",
            corner_radius=0,
            height=40,
            border_width=0
        )
        titlebar.pack(side=ctk.TOP, fill=ctk.X, padx=0, pady=0)
        titlebar.pack_propagate(False)
        
        # Иконка и название приложения слева
        title_label = ctk.CTkLabel(
            titlebar,
            text="💬 HelperTemplates",
            font=FONT_TITLE,
            text_color="#e0e0e0"
        )
        title_label.pack(side=ctk.LEFT, padx=15, pady=0)
        
        # Авторство и версия справа (перед кнопками) - вертикальный стек
        info_frame = ctk.CTkFrame(titlebar, fg_color="transparent")
        info_frame.pack(side=ctk.RIGHT, padx=15, pady=0)
        
        author_label = ctk.CTkLabel(
            info_frame,
            text="Created by Nostro",
            font=("Segoe UI", 11),
            text_color="#808080"
        )
        author_label.pack(side=ctk.TOP, pady=0)
        
        version_label = ctk.CTkLabel(
            info_frame,
            text=f"v{self.get_app_version()}",
            font=("Segoe UI", 10),
            text_color="#808080"
        )
        version_label.pack(side=ctk.TOP, pady=0)
        
        # Кнопки управления окном справа
        buttons_frame = ctk.CTkFrame(titlebar, fg_color="transparent")
        buttons_frame.pack(side=ctk.RIGHT, padx=0, pady=0)
        
        # Кнопка блокировки (всегда поверх)
        self.pin_button = ctk.CTkButton(
            buttons_frame,
            text="📌",
            font=FONT_BUTTON_EMOJI,
            width=45,
            height=40,
            fg_color="transparent",
            hover_color="#404040",
            text_color="#808080",
            command=self.toggle_always_on_top,
            corner_radius=0,
            border_width=0
        )
        self.pin_button.pack(side=ctk.LEFT, padx=0)
        
        # Кнопка сворачивания
        minimize_button = ctk.CTkButton(
            buttons_frame,
            text="─",
            font=FONT_BUTTON_EMOJI,
            width=45,
            height=40,
            fg_color="transparent",
            hover_color="#404040",
            text_color="#e0e0e0",
            command=self.minimize_window,
            corner_radius=0,
            border_width=0
        )
        minimize_button.pack(side=ctk.LEFT, padx=0)
        
        # Кнопка закрытия
        close_button = ctk.CTkButton(
            buttons_frame,
            text="✕",
            font=FONT_BUTTON_EMOJI,
            width=45,
            height=40,
            fg_color="transparent",
            hover_color="#e81123",
            text_color="#e0e0e0",
            command=self.root.quit,
            corner_radius=0,
            border_width=0
        )
        close_button.pack(side=ctk.LEFT, padx=0)
        
        # Функциональность перемещения окна
        self.drag_data = {"x": 0, "y": 0}
        titlebar.bind("<Button-1>", self.start_move)
        titlebar.bind("<B1-Motion>", self.do_move)
        title_label.bind("<Button-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.do_move)
    
    def start_move(self, event):
        """Начинает перемещение окна"""
        self.drag_data["x"] = event.x_root - self.root.winfo_x()
        self.drag_data["y"] = event.y_root - self.root.winfo_y()
    
    def do_move(self, event):
        """Перемещает окно при перетаскивании заголовка"""
        x = event.x_root - self.drag_data["x"]
        y = event.y_root - self.drag_data["y"]
        self.root.geometry(f"+{x}+{y}")
    
    def minimize_window(self):
        """Сворачивает окно - для frameless окон используем withdraw и восстанавливаем через панель задач"""
        # Для окна без рамок iconify() не работает, поэтому используем withdraw()
        # и возвращаем рамки временно
        self.root.overrideredirect(False)
        self.root.iconify()
        # После восстановления вернем frameless режим
        self.root.bind('<Map>', self._on_window_restore)
    
    def _on_window_restore(self, event=None):
        """Восстанавливает frameless режим после разворачивания"""
        self.root.unbind('<Map>')
        self.root.overrideredirect(True)
    
    def toggle_always_on_top(self) -> None:
        """Включает/отключает режим 'всегда поверх всех окон'"""
        self.is_always_on_top = not self.is_always_on_top
        self.root.wm_attributes("-topmost", self.is_always_on_top)
        
        # Обновляем цвет кнопки как индикатор статуса
        if self.is_always_on_top:
            self.pin_button.configure(text_color="#4CAF50")  # Зелёный - активно
        else:
            self.pin_button.configure(text_color="#808080")  # Серый - неактивно
    
    def on_category_selected(self, event=None) -> None:
        """Обработчик выбора категории"""
        self.update_templates_display()
        
        # Обновляем левую часть статус-бара
        current_category = self.category_header.get_selected_category()
        if current_category:
            templates_count = len(self.template_manager.get_templates(current_category))
            self.status_left.configure(text=f"Категория: {current_category} | Шаблонов: {templates_count}")
    
    def on_category_type_selected(self, category_type: str) -> None:
        """Обработчик выбора типа категорий"""
        self.template_manager.set_category_type(category_type)
        # Обновляем список категорий
        categories = self.template_manager.get_categories()
        self.category_header.update_categories(categories)
        # Обновляем отображение шаблонов
        if categories:
            self.on_category_selected()
        else:
            # Если категорий нет, очищаем область шаблонов
            self.update_templates_display()
    
    def add_category(self) -> None:
        """Добавление новой категории с современным диалогом"""
        category_name = self.show_modern_dialog(
            "Новая категория", 
            "Введите название категории:"
        )
        if category_name:
            if self.template_manager.add_category(category_name):
                self.category_header.update_categories(self.template_manager.get_categories())
                self.category_header.set_selected_category(category_name)
                self.update_templates_display()
                self.show_status_message("✓ Категория добавлена")
            else:
                self.show_status_message("✗ Ошибка добавления категории")
    
    def edit_category(self) -> None:
        """Редактирование текущей категории с опциями переименования и удаления"""
        current_category = self.category_header.get_selected_category()
        if not current_category:
            self.show_status_message("⚠ Сначала выберите категорию")
            return
        
        # Создаем кастомный диалог
        dialog = self.create_custom_dialog("Редактирование категории", 450, 235)
        
        # Основной фрейм
        main_frame = ctk.CTkFrame(dialog.content_frame, fg_color="#1a1a1a")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Категория: {current_category}",
            font=("Segoe UI", 16, "bold"),
            text_color="white"
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Поле для переименования
        ctk.CTkLabel(main_frame, text="Новое название:", text_color="white").pack(anchor="w", pady=(10, 3))
        
        name_entry = ctk.CTkTextbox(
            main_frame,
            height=2,
            font=("Segoe UI Emoji", 12),
            text_color="white",
            fg_color="#2b2b2b",
            border_color="#404040",
            border_width=1
        )
        name_entry.pack(fill=ctk.X, pady=(0, 20))
        name_entry.insert("1.0", current_category)
        name_entry.focus()
        self.setup_context_menu_for_widget(name_entry)
        
        # Кнопки действий
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill=ctk.X, pady=(10, 0))
        
        def on_rename():
            new_name = name_entry.get("1.0", ctk.END).strip()
            if not new_name:
                self.show_status_message("✗ Введите название")
                return
            
            if new_name == current_category:
                dialog.destroy()
                return
            
            if self.template_manager.rename_category(current_category, new_name):
                self.category_header.update_categories(self.template_manager.get_categories())
                self.category_header.set_selected_category(new_name)
                self.update_templates_display()
                self.show_status_message("✓ Категория переименована")
                dialog.destroy()
            else:
                self.show_status_message("✗ Ошибка переименования")
        
        def on_delete():
            dialog.destroy()
            # Подтверждение удаления
            confirm_dialog = self.create_custom_dialog("Подтверждение", 400, 195)
            
            confirm_frame = ctk.CTkFrame(confirm_dialog.content_frame, fg_color="#1a1a1a")
            confirm_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
            
            ctk.CTkLabel(
                confirm_frame,
                text=f"Удалить категорию '{current_category}'?\nВсе шаблоны будут удалены.",
                text_color="white",
                font=("Segoe UI", 12)
            ).pack(pady=20)
            
            btn_confirm_frame = ctk.CTkFrame(confirm_frame, fg_color="transparent")
            btn_confirm_frame.pack(pady=10)
            
            def confirm_delete():
                if self.template_manager.delete_category(current_category):
                    categories = self.template_manager.get_categories()
                    self.category_header.update_categories(categories)
                    
                    if categories:
                        self.category_header.set_selected_category(categories[0])
                    
                    self.update_templates_display()
                    self.show_status_message("✓ Категория удалена")
                    confirm_dialog.destroy()
                else:
                    self.show_status_message("✗ Ошибка удаления")
                    confirm_dialog.destroy()
            
            ctk.CTkButton(btn_confirm_frame, text="Да", command=confirm_delete, width=100).pack(side=ctk.LEFT, padx=5)
            ctk.CTkButton(btn_confirm_frame, text="Нет", command=confirm_dialog.destroy, width=100).pack(side=ctk.LEFT, padx=5)
        
        def on_cancel():
            dialog.destroy()
        
        # Кнопка переименования
        ctk.CTkButton(
            btn_frame,
            text="🔤 Переименовать",
            command=on_rename,
            width=150,
            font=FONT_BUTTON_EMOJI
        ).pack(side=ctk.LEFT, padx=5)
        
        # Кнопка удаления
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Удалить",
            command=on_delete,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            width=150,
            font=("Segoe UI Emoji", 12)
        ).pack(side=ctk.LEFT, padx=5)
        
        # Кнопка отмены
        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=on_cancel,
            width=100
        ).pack(side=ctk.LEFT, padx=5)
        
        # Обработка горячих клавиш
        dialog.bind('<Return>', lambda e: on_rename())
        dialog.bind('<Escape>', lambda e: on_cancel())
    
    def add_template(self) -> None:
        """Добавление нового шаблона в текущую категорию"""
        current_category = self.category_header.get_selected_category()
        if not current_category:
            self.show_status_message("⚠ Сначала выберите категорию")
            return
        
        # Создаем кастомный диалог для добавления шаблона
        dialog = self.create_custom_dialog("Добавить новый шаблон", 750, 700)
        
        # Основной фрейм диалога
        main_frame = ctk.CTkFrame(dialog.content_frame, fg_color="#1a1a1a")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Добавить шаблон в категорию '{current_category}'",
            font=("Segoe UI", 14, "bold"),
            text_color="white"
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Поле для названия шаблона
        ctk.CTkLabel(main_frame, text="Название шаблона:", text_color="white").pack(anchor="w", pady=(10, 3))
        
        title_var = ctk.StringVar()
        title_entry = ctk.CTkTextbox(
            main_frame,
            height=2,
            font=("Segoe UI Emoji", 12),
            text_color="white",
            fg_color="#2b2b2b",
            border_color="#404040",
            border_width=1
        )
        title_entry.pack(fill=ctk.X, pady=(0, 15))
        title_entry.focus()
        self.setup_context_menu_for_widget(title_entry)
        
        # Поле для текста шаблона
        ctk.CTkLabel(main_frame, text="Текст шаблона:", text_color="white").pack(anchor="w", pady=(10, 3))
        
        text_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        text_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 15))
        
        # Текстовое поле для содержимого шаблона
        text_widget = ctk.CTkTextbox(
            text_frame,
            height=18,
            width=70,
            font=("Segoe UI", 12)
        )
        text_widget.pack(fill=ctk.BOTH, expand=True)
        self.setup_context_menu_for_widget(text_widget)
        
        # Кнопки действий
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill=ctk.X, pady=(10, 0), anchor="e")
        
        def on_save():
            template_title = title_entry.get("1.0", ctk.END).strip()
            template_text = text_widget.get("1.0", ctk.END).strip()
            
            if not template_title:
                self.show_status_message("✗ Введите название")
                return
            
            if not template_text:
                self.show_status_message("✗ Введите текст")
                return
            
            if self.template_manager.add_template(current_category, template_title, template_text):
                self.show_status_message("✓ Шаблон добавлен")
                self.update_templates_display()
                dialog.destroy()
            else:
                self.show_status_message("✗ Ошибка добавления")
        
        def on_cancel():
            dialog.destroy()
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Сохранить",
            command=on_save,
            width=150,
            font=("Segoe UI Emoji", 12)
        ).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=on_cancel,
            width=100
        ).pack(side=ctk.LEFT, padx=5)
        
        # Обработка горячих клавиш
        dialog.bind('<Escape>', lambda e: on_cancel())
    
    def show_modern_dialog(self, title: str, prompt: str, initial_value: str = "") -> str:
        """Современный диалог ввода"""
        dialog = self.create_custom_dialog(title, 400, 215)
        
        # Содержимое диалога
        main_frame = ctk.CTkFrame(dialog.content_frame, fg_color="#1a1a1a")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(main_frame, text=prompt, text_color="white").pack(pady=15)
        
        # Используем Textbox вместо Entry для поддержки эмодзи
        text_widget = ctk.CTkTextbox(
            main_frame, 
            height=2,
            font=("Segoe UI Emoji", 12),
            text_color="white",
            fg_color="#2b2b2b",
            border_color="#404040",
            border_width=1
        )
        text_widget.pack(fill=ctk.X, pady=5)
        text_widget.insert("1.0", initial_value)
        text_widget.focus()
        self.setup_context_menu_for_widget(text_widget)
        
        result = []
        
        def on_ok():
            result.append(text_widget.get("1.0", ctk.END).strip())
            dialog.destroy()
        
        def on_cancel():
            result.append(None)
            dialog.destroy()
        
        # Кнопки
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        ctk.CTkButton(btn_frame, text="OK", command=on_ok, width=100).pack(side=ctk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="Отмена", command=on_cancel, width=100).pack(side=ctk.LEFT, padx=5)
        
        # Обработка Enter и Escape
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        self.root.wait_window(dialog)
        return result[0] if result else None
    
    def update_templates_display(self) -> None:
        """Обновление отображения шаблонов с современным дизайном"""
        # Очистка текущего отображения
        for widget in self.templates_frame.winfo_children():
            widget.destroy()
        
        current_category = self.category_header.get_selected_category()
        if not current_category:
            # Плейсхолдер при отсутствии выбранной категории
            placeholder = ctk.CTkLabel(
                self.templates_frame, 
                text="👆 Выберите категорию для просмотра шаблонов", 
                text_color="#a0a0a0",
                font=("Segoe UI", 14)
            )
            placeholder.pack(expand=True, pady=100)
            return
        
        templates = self.template_manager.get_templates(current_category)
        
        if not templates:
            # Плейсхолдер для пустой категории
            empty_label = ctk.CTkLabel(
                self.templates_frame, 
                text="📝 В этой категории пока нет шаблонов", 
                text_color="#a0a0a0",
                font=("Segoe UI", 12)
            )
            empty_label.pack(expand=True, pady=100)
            return
        
        # Создание современной прокручиваемой области
        self.create_modern_scrollable_frame(templates)
    
    def create_modern_scrollable_frame(self, templates: list) -> None:
        """Создание современной прокручиваемой области для шаблонов"""
        # Основной контейнер
        container = ctk.CTkFrame(self.templates_frame, fg_color="transparent")
        container.pack(fill=ctk.BOTH, expand=True)
        
        # Canvas и скроллбар
        canvas = ctk.CTkCanvas(
            container, 
            bg="#1a1a1a",
            highlightthickness=0
        )
        
        scrollbar = ctk.CTkScrollbar(
            container, 
            orientation="vertical", 
            command=canvas.yview
        )
        
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="#1a1a1a")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Получаем доступную ширину
        available_width = self.templates_frame.winfo_width()
        if available_width <= 1:
            available_width = 900  # Значение по умолчанию
        
        canvas_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=available_width - 20)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Автоматическое изменение ширины контента
        def configure_canvas(event):
            canvas.itemconfig(canvas_id, width=event.width - 20)
        
        canvas.bind("<Configure>", configure_canvas)
        
        # Функция для скролла мышью по всей области
        def on_mousewheel(event):
            """Обработка скролла мышью по всему canvas"""
            # Определяем направление скролла
            if event.num == 5 or event.delta < 0:
                canvas.yview_scroll(3, "units")
            elif event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-3, "units")
        
        # Привязываем скролл к canvas и всем его дочерним элементам
        canvas.bind("<MouseWheel>", on_mousewheel)
        canvas.bind("<Button-4>", on_mousewheel)
        canvas.bind("<Button-5>", on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        scrollable_frame.bind("<Button-4>", on_mousewheel)
        scrollable_frame.bind("<Button-5>", on_mousewheel)
        
        # Отображение каждого шаблона
        for index, template in enumerate(templates):
            TemplateWidget(
                parent=scrollable_frame,
                template=template,
                template_index=index,
                copy_callback=self.copy_template_text,
                edit_callback=self.edit_template
            )
        
        # Упаковка элементов
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        scrollbar.pack(side="right", fill="y")
    
    def copy_template_text(self, text: str) -> None:
        """Копирование текста шаблона в буфер обмена"""
        if copy_to_clipboard(self.root, text):
            self.show_status_message("✓ Текст скопирован")
        else:
            self.show_status_message("✗ Ошибка копирования")
    
    def edit_template(self, template_index: int) -> None:
        """Редактирование выбранного шаблона"""
        current_category = self.category_header.get_selected_category()
        if not current_category:
            self.show_status_message("⚠ Сначала выберите категорию")
            return
        
        templates = self.template_manager.get_templates(current_category)
        if not templates or template_index >= len(templates) or template_index < 0:
            self.show_status_message("⚠ Ошибка: шаблон не найден")
            return
        
        template = templates[template_index]
        
        # Создаем кастомный диалог для редактирования шаблона
        dialog = self.create_custom_dialog("Редактировать шаблон", 750, 700)
        
        # Основной фрейм диалога
        main_frame = ctk.CTkFrame(dialog.content_frame, fg_color="#1a1a1a")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Редактировать шаблон в категории '{current_category}'",
            font=("Segoe UI", 14, "bold"),
            text_color="white"
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Поле для названия шаблона
        ctk.CTkLabel(main_frame, text="Название шаблона:", text_color="white").pack(anchor="w", pady=(10, 3))
        
        title_entry = ctk.CTkTextbox(
            main_frame,
            height=2,
            font=("Segoe UI Emoji", 12),
            text_color="white",
            fg_color="#2b2b2b",
            border_color="#404040",
            border_width=1
        )
        title_entry.pack(fill=ctk.X, pady=(0, 15))
        title_entry.insert("1.0", template['title'])
        self.setup_context_menu_for_widget(title_entry)
        
        # Поле для текста шаблона
        ctk.CTkLabel(main_frame, text="Текст шаблона:", text_color="white").pack(anchor="w", pady=(10, 3))
        
        text_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        text_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 15))
        
        # Текстовое поле для содержимого шаблона
        text_widget = ctk.CTkTextbox(
            text_frame,
            height=18,
            width=70,
            font=("Segoe UI", 12)
        )
        text_widget.insert("1.0", template['text'])
        text_widget.pack(fill=ctk.BOTH, expand=True)
        self.setup_context_menu_for_widget(text_widget)
        
        # Кнопки действий
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill=ctk.X, pady=(10, 0), anchor="e")
        
        def on_save():
            template_title = title_entry.get("1.0", ctk.END).strip()
            template_text = text_widget.get("1.0", ctk.END).strip()
            
            if not template_title:
                self.show_status_message("✗ Введите название")
                return
            
            if not template_text:
                self.show_status_message("✗ Введите текст")
                return
            
            if self.template_manager.edit_template(current_category, template_index, template_title, template_text):
                self.show_status_message("✓ Шаблон обновлен")
                self.update_templates_display()
                dialog.destroy()
            else:
                self.show_status_message("✗ Ошибка сохранения")
        
        def on_delete():
            dialog.destroy()
            # Подтверждение удаления
            confirm_dialog = self.create_custom_dialog("Подтверждение", 350, 175)
            
            confirm_frame = ctk.CTkFrame(confirm_dialog.content_frame, fg_color="#1a1a1a")
            confirm_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
            
            ctk.CTkLabel(
                confirm_frame,
                text="Удалить этот шаблон?",
                text_color="white",
                font=("Segoe UI", 12)
            ).pack(pady=20)
            
            btn_confirm_frame = ctk.CTkFrame(confirm_frame, fg_color="transparent")
            btn_confirm_frame.pack(pady=10)
            
            def confirm_delete():
                if self.template_manager.delete_template(current_category, template_index):
                    self.show_status_message("✓ Шаблон удален")
                    self.update_templates_display()
                    confirm_dialog.destroy()
                else:
                    self.show_status_message("✗ Ошибка удаления")
                    confirm_dialog.destroy()
            
            ctk.CTkButton(btn_confirm_frame, text="Да", command=confirm_delete, width=100).pack(side=ctk.LEFT, padx=5)
            ctk.CTkButton(btn_confirm_frame, text="Нет", command=confirm_dialog.destroy, width=100).pack(side=ctk.LEFT, padx=5)
        
        def on_cancel():
            dialog.destroy()
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Сохранить",
            command=on_save,
            width=150,
            font=("Segoe UI Emoji", 12)
        ).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Удалить",
            command=on_delete,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            width=150,
            font=("Segoe UI Emoji", 12)
        ).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=on_cancel,
            width=100
        ).pack(side=ctk.LEFT, padx=5)
    
    def check_updates_on_startup(self):
        """Проверить обновления в отдельном потоке"""
        thread = threading.Thread(target=self._check_updates_background, daemon=True)
        thread.start()
    
    def _check_updates_background(self):
        """Проверить обновления в фоновом потоке"""
        try:
            has_update, remote_version, download_url = AppUpdater.check_for_updates()
            
            if has_update:
                # Вызываем диалог в главном потоке
                self.root.after(0, lambda: self.show_update_dialog(remote_version, download_url))
        except Exception as e:
            print(f"Ошибка при проверке обновлений: {e}")
    
    def show_update_dialog(self, remote_version, download_url):
        """Показать диалог об обновлении"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Доступно обновление")
        dialog.geometry("450x250")
        dialog.resizable(False, False)
        
        # Центрируем диалог
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Устанавливаем поверх всех окон
        dialog.attributes("-topmost", True)
        dialog.lift()
        dialog.focus_force()
        
        # Заголовок
        title_label = ctk.CTkLabel(
            dialog,
            text="🎉 Доступно обновление!",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Информация о версии
        info_label = ctk.CTkLabel(
            dialog,
            text=f"Новая версия: {remote_version}\n\nОбновить приложение сейчас?",
            font=("Segoe UI", 13)
        )
        info_label.pack(pady=10)
        
        # Прогресс бар (изначально скрыт)
        progress_label = ctk.CTkLabel(
            dialog,
            text="Загрузка обновления...",
            font=("Segoe UI", 11)
        )
        
        progress_bar = ctk.CTkProgressBar(dialog, width=350)
        progress_bar.set(0)
        
        def update_now():
            # Скрываем кнопки, показываем прогресс
            btn_frame.pack_forget()
            progress_label.pack(pady=5)
            progress_bar.pack(pady=10)
            
            # Запускаем загрузку в отдельном потоке
            thread = threading.Thread(
                target=self._download_and_install,
                args=(download_url, progress_bar, dialog),
                daemon=True
            )
            thread.start()
        
        def skip():
            dialog.destroy()
        
        # Кнопки
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        update_btn = ctk.CTkButton(
            btn_frame,
            text="✅ Обновить",
            command=update_now,
            width=150,
            height=35,
            font=("Segoe UI", 12, "bold"),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        update_btn.pack(side="left", padx=10)
        
        skip_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Пропустить",
            command=skip,
            width=150,
            height=35,
            font=("Segoe UI", 12),
            fg_color="#757575",
            hover_color="#616161"
        )
        skip_btn.pack(side="left", padx=10)
    
    def _download_and_install(self, download_url, progress_bar, dialog):
        """Скачать и установить обновление"""
        def update_progress(value):
            # Обновляем прогресс в главном потоке
            self.root.after(0, lambda: progress_bar.set(value / 100))
        
        # Скачиваем обновление
        success, update_path = AppUpdater.download_update(download_url, update_progress)
        
        if success:
            # Закрываем диалог
            self.root.after(0, dialog.destroy)
            # Устанавливаем обновление
            self.root.after(100, lambda: AppUpdater.install_update(self.root))
        else:
            # Показываем ошибку
            self.root.after(0, lambda: self._show_update_error(dialog))
    
    def _show_update_error(self, parent_dialog):
        """Показать ошибку обновления"""
        parent_dialog.destroy()
        
        error_dialog = ctk.CTkToplevel(self.root)
        error_dialog.title("Ошибка обновления")
        error_dialog.geometry("400x150")
        error_dialog.attributes("-topmost", True)
        
        label = ctk.CTkLabel(
            error_dialog,
            text="❌ Не удалось загрузить обновление\n\nПопробуйте позже",
            font=("Segoe UI", 13)
        )
        label.pack(pady=30)
        
        ok_btn = ctk.CTkButton(
            error_dialog,
            text="OK",
            command=error_dialog.destroy,
            width=100
        )
        ok_btn.pack(pady=10)
        
        # Обработка горячих клавиш
        dialog.bind('<Escape>', lambda e: on_cancel())
