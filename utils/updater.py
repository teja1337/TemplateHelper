"""
Модуль для автоматического обновления приложения
"""
import requests
import json
import subprocess
import os
import sys
from pathlib import Path
import urllib3

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Пытаемся импортировать версию из Python модуля
try:
    from version import VERSION as HARDCODED_VERSION
except ImportError:
    HARDCODED_VERSION = None

class AppUpdater:
    """Класс для автоматического обновления приложения"""
    
    VERSION_FILE = "version.json"
    REPO_OWNER = "teja1337"
    REPO_NAME = "HelperTemplates"
    
    @staticmethod
    def get_local_version():
        """Получить локальную версию"""
        # Сначала пытаемся использовать встроенную версию из version.py
        if HARDCODED_VERSION:
            print(f"[DEBUG] Используем встроенную версию: {HARDCODED_VERSION}")
            return HARDCODED_VERSION
        
        # Fallback - читаем из version.json
        try:
            if getattr(sys, 'frozen', False):
                # PyInstaller создаёт временную папку _MEIPASS
                if hasattr(sys, '_MEIPASS'):
                    # Ищем в временной папке PyInstaller
                    version_path = Path(sys._MEIPASS) / AppUpdater.VERSION_FILE
                else:
                    # Fallback - рядом с .exe
                    version_path = Path(sys.executable).parent / AppUpdater.VERSION_FILE
            else:
                version_path = Path(__file__).parent.parent / AppUpdater.VERSION_FILE
            
            print(f"[DEBUG] Читаю version.json из: {version_path}")
            with open(version_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                version = data.get('version', '0.0.0')
                print(f"[DEBUG] Прочитана версия: {version}")
                return version
        except Exception as e:
            print(f"[ERROR] Ошибка при чтении локальной версии: {e}")
            print(f"[DEBUG] Искал в: {version_path if 'version_path' in locals() else 'unknown'}")
            return '0.0.0'
    
    @staticmethod
    def get_remote_version():
        """Получить версию с GitHub API (последний релиз)"""
        try:
            url = f"https://api.github.com/repos/{AppUpdater.REPO_OWNER}/{AppUpdater.REPO_NAME}/releases/latest"
            response = requests.get(url, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            
            # Извлекаем версию из тега (v1.0.0 → 1.0.0)
            tag = data.get('tag_name', 'v0.0.0').lstrip('v')
            
            # Ищем Helper.exe в assets
            download_url = None
            for asset in data.get('assets', []):
                if asset['name'] == 'Helper.exe':
                    download_url = asset['browser_download_url']
                    break
            
            if not download_url:
                print("Helper.exe не найден в релизе!")
                return None, None
            
            return tag, download_url
        except Exception as e:
            print(f"Ошибка при получении версии с GitHub: {e}")
            return None, None
    
    @staticmethod
    def compare_versions(local, remote):
        """Сравнить версии (1.0.0 > 0.9.0)"""
        try:
            local_parts = [int(x) for x in local.split('.')]
            remote_parts = [int(x) for x in remote.split('.')]
            return remote_parts > local_parts
        except:
            return False
    
    @staticmethod
    def download_update(download_url, progress_callback=None):
        """Скачать обновление"""
        try:
            print(f"[DEBUG] Начинаю загрузку: {download_url}")
            
            # Определяем путь для сохранения
            if getattr(sys, 'frozen', False):
                save_path = Path(sys.executable).parent / "Helper_update.exe"
            else:
                save_path = Path("Helper_update.exe")
            
            print(f"[DEBUG] Сохраняю в: {save_path}")
            
            response = requests.get(download_url, stream=True, timeout=30, verify=False)
            response.raise_for_status()
            
            print(f"[DEBUG] Ответ получен: {response.status_code}")
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            print(f"[DEBUG] Размер файла: {total_size / (1024*1024):.2f} MB")
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size and progress_callback:
                            progress = (downloaded / total_size * 100)
                            progress_callback(progress)
            
            print(f"[DEBUG] Загрузка завершена: {save_path}")
            return True, str(save_path)
        except Exception as e:
            print(f"[ERROR] Ошибка при скачивании: {e}")
            import traceback
            traceback.print_exc()
            return False, None
    
    @staticmethod
    def check_for_updates():
        """Проверить наличие обновлений"""
        local_version = AppUpdater.get_local_version()
        remote_version, download_url = AppUpdater.get_remote_version()
        
        if remote_version and AppUpdater.compare_versions(local_version, remote_version):
            return True, remote_version, download_url
        
        return False, local_version, None
    
    @staticmethod
    def install_update(root_window):
        """Установить обновление через updater.exe"""
        try:
            # Закрываем главное окно
            root_window.quit()
            root_window.destroy()
            
            # Определяем путь к updater.exe
            if getattr(sys, 'frozen', False):
                updater_path = Path(sys.executable).parent / "updater.exe"
            else:
                updater_path = Path("dist") / "updater.exe"
            
            # Запускаем updater.exe
            if updater_path.exists():
                subprocess.Popen([str(updater_path)])
            else:
                print("updater.exe не найден!")
            
            sys.exit()
        except Exception as e:
            print(f"Ошибка при установке обновления: {e}")
