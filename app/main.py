import argparse
from collections import defaultdict
from app.database.db import SessionLocal, init_db
from app.repositories.task import TaskRepository
from app.repositories.focus_session import FocusSessionRepository
from app.utils.timer import run_timer
from datetime import datetime
from app.utils.period_map import PERIOD_MAP


class Service:
    def __init__(self):
        self.session = SessionLocal

    def create_task(self, name):
        with self.session() as session:
            task = TaskRepository.create(session, name)
        return task

    def all_task(self):
        with self.session() as session:
            tasks = TaskRepository.get_all(session)
        return tasks

    def start_focus_in_task(self, task_id):
        with self.session() as session:
            focus_session = FocusSessionRepository.create(session, task_id, 0)
        return focus_session

    def finish_focus_in_task(self, focus_id, task_id, duration: int, end_time: datetime = datetime.now()):
        with self.session() as session:
            # Обновляем длительность сессии
            focus_session = FocusSessionRepository.update(session, focus_id, end_time=end_time, duration=duration)
            # Обновляем общее время в задаче
            TaskRepository.update(session, task_id, time=duration)
        return focus_session

    def total_time_in_task(self, task_id):
        with self.session() as session:
            total_time = FocusSessionRepository.get_total_duration_for_task(session, task_id)
        return total_time
    
    def get_stats_by(self, period: str, task_id: int | None):
        with self.session() as session:
            focus_sessions = FocusSessionRepository.get_stats_by(session, period, task_id)
            if not focus_sessions:
                return None
            result = defaultdict(int)
            for s in focus_sessions:
                task = TaskRepository.get(session, s.task_id)
                if task:
                    result[task.name] += s.duration
            return result

            
            


class App:
    def __init__(self) -> None:
        self.service = Service()

    def create_task(self, name):
        name = name.capitalize()
        task = self.service.create_task(name)
        if not task:
            return f"Задача: {name} уже существует"
        return f"Задача создана\nID: {task.id}\nName: {task.name}"

    def start_focus_in_task(self, task_id, duration: int = 0):
        # Проверяем, существует ли задача
        with self.service.session() as session:
            task = TaskRepository.get(session, task_id)
            if not task:
                return f"Ошибка: Задача с ID {task_id} не найдена"
            else:
                print(f"Задача: {task.name}\n")
            # Создаем сессию в базе данных
            focus_session = self.service.start_focus_in_task(task_id)

            # Запускаем таймер
            elapsed_time = run_timer(duration)
            print(elapsed_time)
            # Завершаем сессию с учетом прошедшего времени
            focus_session = self.service.finish_focus_in_task(focus_id=focus_session.id, task_id=task_id, end_time=datetime.now(), duration=elapsed_time)
            session.refresh(task)

        return f"Рабочая сессия завершена. Общее время в задаче: {round(task.time_spent/60)} минут"

    def get_all_tasks(self):
        tasks = self.service.all_task()
        if not tasks:
            print("Нет созданных задач")
            return
        print("Список задач:")
        for task in tasks:
            hours_spent = task.time_spent // 3600
            minutes_spent = (task.time_spent % 3600) // 60
            print(f"\nID: {task.id}\nНазвание: {task.name}\nОбщее время: {hours_spent} ч. {minutes_spent} мин.\n")

    def get_stats_by_period(self, period, task_id: int | None):
        name_time = self.service.get_stats_by(period, task_id)
        if not name_time:
            return 'За этот период нет рабочих сессий'
        for name, time in name_time.items():
            type = 'минут'
            if time > 60:
                time = round(time / 60)
                type = 'часов'
            print(f"Задача: {name}\nВремя: {time} {type}\n")
        
            
        



init_db()
def main():
    parser = argparse.ArgumentParser(description="Timer CLI приложение для управления задачами")
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Команда для создания задачи
    create_parser = subparsers.add_parser("create", help="Создать новую задачу")
    create_parser.add_argument("name", type=str, help="Название задачи")

    # Команда для просмотра всех задач
    list_parser = subparsers.add_parser("list", help="Показать все задачи")

    # Команда для запуска таймера
    start_parser = subparsers.add_parser("start", help="Запустить таймер для задачи")
    start_parser.add_argument("task_id", type=int, help="ID задачи")
    start_parser.add_argument("--duration", type=int, default=0, help="Длительность таймера в минутах (0 для бесконечного)")

    # Команды для просмотра статистики за неделю за месяц за все время
    stats_parser = subparsers.add_parser("stats", help='Получить статистику за неделю/месяц/год/сегодня')
    stats_parser.add_argument("period", type=str, help='выбор week/month/year/today')
    stats_parser.add_argument("--task", type=int, default=None, help='ID задачи')
    

    args = parser.parse_args()

    app = App()

    if args.command == "create":
        result = app.create_task(args.name)
        print(result)
    elif args.command == "list":
        app.get_all_tasks()
    elif args.command == "start":
        result = app.start_focus_in_task(args.task_id, args.duration)
        print(result)
    elif args.command == 'stats':
        result = app.get_stats_by_period(args.period, args.task)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

