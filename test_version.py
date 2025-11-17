"""
Диагностика чтения version.json из PyInstaller
"""
import sys
from pathlib import Path

print("=" * 60)
print("ДИАГНОСТИКА VERSION.JSON")
print("=" * 60)

print(f"\nsys.frozen: {getattr(sys, 'frozen', False)}")
print(f"sys.executable: {sys.executable}")

if hasattr(sys, '_MEIPASS'):
    print(f"sys._MEIPASS: {sys._MEIPASS}")
    meipass_path = Path(sys._MEIPASS)
    print(f"\nФайлы в _MEIPASS:")
    try:
        for f in meipass_path.iterdir():
            print(f"  - {f.name}")
    except:
        print("  Не удалось прочитать")
else:
    print("sys._MEIPASS: НЕТ")

# Проверяем разные варианты пути
paths_to_check = [
    Path(sys.executable).parent / "version.json",
    Path("version.json"),
]

if hasattr(sys, '_MEIPASS'):
    paths_to_check.insert(0, Path(sys._MEIPASS) / "version.json")

print(f"\n\nПроверяю пути к version.json:")
for p in paths_to_check:
    exists = p.exists()
    print(f"\n  {p}")
    print(f"  Существует: {exists}")
    if exists:
        try:
            import json
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"  Версия: {data.get('version')}")
        except Exception as e:
            print(f"  Ошибка чтения: {e}")

input("\n\nНажмите Enter для выхода...")
