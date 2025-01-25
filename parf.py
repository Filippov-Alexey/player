import subprocess
import sys
import os
import json
import time
from icecream import ic
ic.configureOutput(includeContext=True)
folder_path = sys.argv[1]

full_paths = []

# Обход всех файлов в заданной папке
for root, dirs, files in os.walk(folder_path):
    for file in files:
        full_path = os.path.normpath(os.path.join(root, file))  # Нормализация пути
        full_paths.append(full_path)

file1=[]
if os.path.exists('historyf.json'):
    with open('historyf.json', 'r', encoding='utf-8') as f:
        h = json.load(f)  # Предположим, что h - это словарь с файлом как ключами
    ic(full_paths, h)

    # Проходим по всем полным путям
    for file in full_paths:
        # Проверяем, есть ли файл в h
        if file in h:
            status = h[file]
            if status == 0:
                ic(file, "Status is 0. Performing action...")
                # Здесь можно запустить ваш плеер
                p = subprocess.Popen(['python', 'player.py', file, '0'])
                p.wait()
        else:
            # Если файла нет в h, добавляем его в список file1
            if file not in file1:
                file1.append(file)
                ic(file, "Not in history. Adding to file1.")
                # Здесь можно также запустить ваш плеер, если это нужно
                p = subprocess.Popen(['python', 'player.py', file, '0'])
                p.wait()
else:
    for name in full_paths:
        p=subprocess.Popen(['python','player.py',name,'0'])
        p.wait()
        print(name)
        time.sleep(1)