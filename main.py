import customtkinter as ctk
from models.template_manager import TemplateManager
from views.main_window import MainWindow

def main():
    """Основная функция приложения Хелпер"""
    # Настройка темы customtkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    # Создание корневого окна с нормальным управлением
    root = ctk.CTk()
    # Больше не скрываем окно из панели задач!
    
    # Инициализация менеджера шаблонов
    template_manager = TemplateManager()
    
    # Создание главного окна приложения с современным дизайном
    app = MainWindow(root, template_manager)
    
    # Запуск главного цикла
    root.mainloop()

if __name__ == "__main__":
    main()