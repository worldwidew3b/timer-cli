import time
import signal
import sys
import threading
from datetime import datetime


class Timer:
    def __init__(self, duration_minutes=0):
        """
        Инициализация таймера
        
        Args:
            duration_minutes (int): Длительность таймера в минутах (0 для бесконечного таймера)
        """
        self.duration_seconds = duration_minutes * 60 if duration_minutes > 0 else None
        self.start_time = None
        self.elapsed_time = 0
        self.is_running = False
        self.stop_event = threading.Event()
        self.timer_thread = None

    def start_timer(self):
        """Запуск таймера"""
        self.start_time = time.time()
        self.is_running = True
        self.stop_event.clear()
        
        if self.duration_seconds is None:  # Бесконечный таймер
            self.timer_thread = threading.Thread(target=self._run_infinite_timer)
        else:
            self.timer_thread = threading.Thread(target=self._run_countdown_timer)
        
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def _run_infinite_timer(self):
        """Запуск бесконечного таймера"""
        while not self.stop_event.is_set():
            self.elapsed_time = int(time.time() - self.start_time)
            time.sleep(1)
            if self.stop_event.is_set():
                break

    def _run_countdown_timer(self):
        """Запуск таймера с обратным отсчетом"""
        while not self.stop_event.is_set():
            self.elapsed_time = int(time.time() - self.start_time)
            if self.elapsed_time >= self.duration_seconds:
                break
            time.sleep(1)
            if self.stop_event.is_set():
                break

    def stop_timer(self):
        """Остановка таймера и возврат прошедшего времени в секундах"""
        self.stop_event.set()
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join()
        self.is_running = False
        if self.start_time:
            self.elapsed_time = int(time.time() - self.start_time)
        return self.elapsed_time

    def format_time(self, seconds):
        """Форматирование времени в формат ЧЧ:ММ:СС"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def get_elapsed_time(self):
        """Получение прошедшего времени в секундах"""
        if self.is_running and self.start_time:
            return int(time.time() - self.start_time)
        return self.elapsed_time

    def display_timer(self):
        """Отображение таймера в реальном времени"""
        while self.is_running and not self.stop_event.is_set():
            elapsed = self.get_elapsed_time()

            if self.duration_seconds is None:  # Бесконечный таймер - показываем прошедшее время
                print(f"\rПрошло времени: {self.format_time(elapsed)}", end="", flush=True)
            else:  # Таймер с обратным отсчетом - показываем оставшееся время
                remaining = max(0, self.duration_seconds - elapsed)
                print(f"\rОсталось времени: {self.format_time(remaining)}", end="", flush=True)

            time.sleep(1)


def run_timer(duration_minutes=0):
    """
    Запуск таймера с возможностью прерывания по Ctrl+C
    
    Args:
        duration_minutes (int): Длительность таймера в минутах (0 для бесконечного таймера)
    
    Returns:
        int: Прошедшее время в секундах
    """
    timer = Timer(duration_minutes)
    timer.start_timer()
    
    # Запускаем отображение таймера в отдельном потоке
    display_thread = threading.Thread(target=timer.display_timer)
    display_thread.daemon = True
    display_thread.start()
    
    # # Устанавливаем обработчик сигнала для корректного завершения по Ctrl+C
    # def signal_handler(sig, frame):
    #     print(f"\nТаймер прерван. Прошло времени: {timer.format_time(timer.get_elapsed_time())}")
    #     elapsed_time = timer.stop_timer()

    # signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Ждем завершения таймера или прерывания
        if duration_minutes == 0:  # Бесконечный таймер
            while timer.is_running and not timer.stop_event.is_set():
                time.sleep(1)
        else:  # Таймер с обратным отсчетом
            while timer.is_running and not timer.stop_event.is_set():
                if timer.get_elapsed_time() >= timer.duration_seconds:
                    break
                time.sleep(1)

        # Останавливаем таймер и возвращаем прошедшее время
        elapsed_time = timer.stop_timer()

        if duration_minutes == 0:  # Бесконечный таймер
            print(f"\nТаймер завершен. Прошло времени: {timer.format_time(elapsed_time)}")
        else:  # Таймер с обратным отсчетом
            if timer.get_elapsed_time() >= timer.duration_seconds:
                print(f"\nТаймер завершен. Время вышло!")
            else:
                print(f"\nТаймер завершен. Прошло времени: {timer.format_time(elapsed_time)}")

        return elapsed_time

    except KeyboardInterrupt:
        elapsed_time = timer.stop_timer()
        # print(f"\nТаймер прерван. Прошло времени: {timer.format_time(timer.get_elapsed_time())}")
        print(f"\nТаймер прерван. Прошло времени: {timer.format_time(elapsed_time)}")
        return elapsed_time