"""
Скрипт для создания .exe файла с помощью PyInstaller
Запустите: python build_exe.py
"""
import os
import shutil
import subprocess
import sys

def build_exe():
    """Создание исполняемых файлов Helper.exe и updater.exe"""
    
    print("=" * 60)
    print("🔨 Начинаю сборку Helper.exe и updater.exe...")
    print("=" * 60)
    
    # Путь к текущей директории
    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, 'dist')
    build_dir = os.path.join(project_dir, 'build')
    
    # Очистка старых файлов
    print("\n📦 Очищаю старые файлы сборки...")
    for dir_path in [dist_dir, build_dir]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"   ✓ Удалена папка {dir_path}")
    
    # Создаем папки заново
    os.makedirs(dist_dir, exist_ok=True)
    
    success = True
    
    # Команда для PyInstaller - Helper.exe
    print("\n🔨 Создаю Helper.exe...")
    pyinstaller_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'Helper',
        '--add-data', f'{os.path.join(project_dir, "version.json")};.',
        '--distpath', dist_dir,
        '--workpath', build_dir,
        '--specpath', project_dir,
        os.path.join(project_dir, 'main.py'),
        '-y'
    ]
    
    # Добавляем иконку если она существует
    icon_path = os.path.join(project_dir, 'icon.ico')
    if os.path.exists(icon_path):
        pyinstaller_cmd.extend(['--icon', icon_path])
        print(f"   ✓ Добавлена иконка: {icon_path}")
    
    try:
        result = subprocess.run(pyinstaller_cmd, check=True)
        print("   ✓ Helper.exe создан успешно!")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Ошибка при создании Helper.exe: {e}")
        success = False
    
    # Команда для PyInstaller - updater.exe
    print("\n🔨 Создаю updater.exe...")
    updater_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--console',
        '--name', 'updater',
        '--distpath', dist_dir,
        '--workpath', build_dir,
        '--specpath', project_dir,
        os.path.join(project_dir, 'updater.py'),
        '-y'
    ]
    
    try:
        result = subprocess.run(updater_cmd, check=True)
        print("   ✓ updater.exe создан успешно!")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Ошибка при создании updater.exe: {e}")
        success = False
    
    if success:
        helper_exe = os.path.join(dist_dir, 'Helper.exe')
        updater_exe = os.path.join(dist_dir, 'updater.exe')
        
        if os.path.exists(helper_exe) and os.path.exists(updater_exe):
            print("\n" + "=" * 60)
            print("✅ УСПЕШНО! Все файлы созданы!")
            print("=" * 60)
            print(f"\n📂 Helper.exe: {helper_exe}")
            print(f"📊 Размер: {os.path.getsize(helper_exe) / (1024*1024):.2f} MB")
            print(f"\n📂 updater.exe: {updater_exe}")
            print(f"📊 Размер: {os.path.getsize(updater_exe) / (1024*1024):.2f} MB")
            print("\n💡 Скопируйте оба файла вместе для работы автообновления")
            
            return True
        else:
            print("\n❌ Ошибка: Файлы не найдены в папке dist")
            return False
    else:
        return False

if __name__ == '__main__':
    success = build_exe()
    sys.exit(0 if success else 1)
