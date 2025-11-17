import json
import os
from typing import List, Dict, Optional

class TemplateManager:
    """Класс для управления шаблонами и категориями"""
    
    def __init__(self):
        # Получаем путь к директории данных пользователя (AppData)
        self.app_data_dir = os.path.join(os.getenv('APPDATA'), 'Helper')
        
        # Создаём директорию если её нет
        os.makedirs(self.app_data_dir, exist_ok=True)
        
        self.current_category_type = "Клиенты"
        self.files = {
            "Клиенты": os.path.join(self.app_data_dir, "templates_clients.json"),
            "Коллеги": os.path.join(self.app_data_dir, "templates_colleagues.json")
        }
        self.categories: Dict[str, List[Dict]] = {}
        self.load_templates()
    
    def get_current_filename(self) -> str:
        """Получить имя файла для текущего типа категорий"""
        return self.files[self.current_category_type]
    
    def load_templates(self) -> None:
        """Загрузка шаблонов из файла текущего типа"""
        filename = self.get_current_filename()
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.categories = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._create_default_templates()
        else:
            self._create_default_templates()
    
    def _create_default_templates(self) -> None:
        """Создание демо-шаблонов при первом запуске"""
        if self.current_category_type == "Клиенты":
            self.categories = {
                "Приветствие": [
                    {"title": "Стандартное приветствие", "text": "Здравствуйте! Чем могу помочь?"}
                ],
                "Прощание": [
                    {"title": "Стандартное прощание", "text": "Всего доброго! Обращайтесь еще!"}
                ]
            }
        else:  # Коллеги
            self.categories = {
                "Общение": [
                    {"title": "Привет", "text": "Привет! Как дела?"}
                ]
            }
        self.save_templates()
    
    def save_templates(self) -> None:
        """Сохранение шаблонов в файл текущего типа"""
        try:
            filename = self.get_current_filename()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise Exception(f"Ошибка сохранения файла: {e}")
    
    def set_category_type(self, category_type: str) -> None:
        """Установить текущий тип категорий и загрузить его шаблоны"""
        if category_type in self.files:
            self.current_category_type = category_type
            self.load_templates()
    
    def get_category_types(self) -> List[str]:
        """Получить список типов категорий"""
        return list(self.files.keys())
    
    def get_categories(self) -> List[str]:
        """Получить список категорий"""
        return list(self.categories.keys())
    
    def add_category(self, category_name: str) -> bool:
        """Добавить новую категорию"""
        if category_name and category_name not in self.categories:
            self.categories[category_name] = []
            self.save_templates()
            return True
        return False
    
    def rename_category(self, old_name: str, new_name: str) -> bool:
        """Переименовать категорию"""
        if old_name in self.categories and new_name and new_name not in self.categories:
            self.categories[new_name] = self.categories.pop(old_name)
            self.save_templates()
            return True
        return False
    
    def delete_category(self, category_name: str) -> bool:
        """Удалить категорию"""
        if category_name in self.categories:
            del self.categories[category_name]
            self.save_templates()
            return True
        return False
    
    def get_templates(self, category: str) -> List[Dict]:
        """Получить шаблоны для категории"""
        return self.categories.get(category, [])
    
    def add_template(self, category: str, title: str, text: str) -> bool:
        """Добавить шаблон в категорию"""
        if category in self.categories:
            self.categories[category].append({"title": title, "text": text})
            self.save_templates()
            return True
        return False
    
    def edit_template(self, category: str, index: int, new_title: str, new_text: str) -> bool:
        """Редактировать шаблон"""
        if category in self.categories and 0 <= index < len(self.categories[category]):
            self.categories[category][index] = {"title": new_title, "text": new_text}
            self.save_templates()
            return True
        return False
    
    def delete_template(self, category: str, index: int) -> bool:
        """Удалить шаблон из категории"""
        if category in self.categories and 0 <= index < len(self.categories[category]):
            self.categories[category].pop(index)
            self.save_templates()
            return True
        return False