"""
Проверка структуры icon.ico
"""
from PIL import Image

# Открыть ico файл
with Image.open(r'C:\Code\Helper\icon.ico') as img:
    print(f"Основной размер: {img.size}")
    print(f"Формат: {img.format}")
    print(f"Всего изображений в файле: {img.n_frames}")
    
    # Проверить все размеры
    for i in range(img.n_frames):
        img.seek(i)
        print(f"  Размер {i+1}: {img.size}")
