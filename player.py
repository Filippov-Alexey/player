import sys
import os
import json
import tkinter as tk
from tkinter import messagebox
import vlc

HISTORY_FILE = "history.json"
REWIND_FILE = "rewind.json"
class MediaPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Media Player")

        # Указываем путь к библиотеке VLC
        vlc_path = r"C:\Program Files\VideoLAN\VLC"
        os.add_dll_directory(vlc_path)

        # Создаем VLC плеер
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Создаем элемент управления для отображения видео
        self.video_frame = tk.Frame(master, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=True)
        self.player.set_hwnd(self.video_frame.winfo_id())  # Установка окна

        self.play_button = tk.Button(master, text="Play", command=self.play)
        self.play_button.pack(side=tk.BOTTOM)

        # Переменные для медиаплеера
        self.media_file = None
        self.resume_time = 0
        self.his={}

        self.load_history()

        # Запускаем таймер для проверки статуса воспроизведения
        self.check_playback()

        self.start_rewind_check()

        # Установка обработки клавиш
        self.master.bind("<Left>", self.rewind_key)
        self.master.bind("<Right>", self.forward)
        self.master.bind("<space>", self.toggle_pause)

    def play(self):
        if len(sys.argv) < 2:
            messagebox.showerror("Error", "Please provide a media file as an argument.")
            return

        self.media_file = sys.argv[1]
        media = self.instance.media_new(self.media_file)
        self.player.set_media(media)

        # Запускаем воспроизведение
        self.player.play()
        # Устанавливаем время воспроизведения, если есть
        if self.resume_time > 0:
            self.player.set_time(self.resume_time)

        # Запуск записи истории
        self.save_history()
        self.his=self.update_histor()

    def check_playback(self):
        if self.player.get_state() == vlc.State.Ended:
            self.master.quit()  # Завершение программы, если воспроизведение окончено
        else:
            self.master.after(1000, self.check_playback)  # Проверка состояния через 1 секунду

    def save_history(self):
        def update_history(file, time):
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r') as f:
                    history = json.load(f)
            else:
                history = {}

            # Обновляем или добавляем запись
            history[file] = time

            # Записываем обновленный history обратно в файл
            with open(HISTORY_FILE, 'w') as f:
                json.dump(history, f)

        # Запуск записи времени каждую секунду
        def record_time():
            if self.media_file:
                current_time = self.player.get_time()  # Получаем текущее время воспроизведения
                update_history(self.media_file, current_time)
            self.master.after(1000, record_time)  # Каждый 1 секунду

        record_time()  # Начинаем запись времени

    def load_history(self):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)

        self.media_file = sys.argv[1]
        if self.media_file in history:
            self.resume_time = history[self.media_file]
            
            # Устанавливаем время после воспроизведения
            self.player.set_time(self.resume_time)

    def rewind_key(self, event):
        current_time = self.player.get_time()
        new_time = max(current_time - 5000, 0)  # Не даем времени быть меньше 0
        self.player.set_time(new_time)

    def start_rewind_check(self):
        """Запускает проверку на возможность перемотки каждую секунду."""
        self.update_histor()  # Обновляем историю перед проверкой
        self.rewindv()  # Вызываем проверку перемотки
        self.master.after(1000, self.start_rewind_check)  # Запланируем следующий вызов через 1 секунду

    def update_histor(self):
        """Загружает данные из rewind.json."""
        if os.path.exists(REWIND_FILE):
            with open(REWIND_FILE, 'r') as f:
                self.his = json.load(f)  # Загружаем данные
        else:
            self.his = {}  # Пустой словарь, если файл не существует

    def rewindv(self):
        current_time = self.player.get_time()
        print(f"Текущее время: {current_time}")

        # Используем данные из self.his
        rewind_data = self.his  
        print("Данные перемотки:", rewind_data)

        file_rewind_info = rewind_data.get(self.media_file)
        print("Информация о перемотке:", file_rewind_info)
        
        if file_rewind_info:
            # Проверяем, есть ли диапазоны перемотки для текущего файла
            for (start, end) in file_rewind_info:
                print(f"Диапазон: {start}-{end}")

                # Если текущее время находится в диапазоне перемотки
                if start <= current_time <= end:
                    # Перематываем на начало диапазона
                    print(f"Перематываем на начало диапазона: {start}")
                    self.player.set_time(end)
                    return  # Выходим, так как перемотка завершена
                
    def forward(self, event):
        """Перемотка вперед на 5 секунд."""
        current_time = self.player.get_time()
        new_time = current_time + 5000
        self.player.set_time(new_time)

    def toggle_pause(self, event):
        """Пауза/воспроизведение при нажатии пробела."""
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

# Запуск основного приложения
if __name__ == "__main__":
    root = tk.Tk()
    player = MediaPlayer(root)
    root.attributes('-fullscreen',True)
    # root.geometry("640x480")

    if len(sys.argv) < 2:
        messagebox.showerror("Error", "Please provide a media file as an argument.")
    else:
        media_file = sys.argv[1]
        player.play()

    root.mainloop()
