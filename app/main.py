import argparse
from collections import defaultdict
from app.database.db import SessionLocal, init_db
from app.repositories.task import TaskRepository
from app.repositories.focus_session import FocusSessionRepository
from app.utils.timer import run_timer
from datetime import datetime
from app.utils.period_map import PERIOD_MAP
from app.views.view import View


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

    def delete_task(self, task_id):
        with self.session() as session:
            result = TaskRepository.delete(session, task_id)
        return result
    
    def delete_sessions_by_task(self, task_id):
        with self.session() as session:
            result = FocusSessionRepository.delete_by_task(session, task_id)
        return result



class App:
    def __init__(self) -> None:
        self.service = Service()
        self.view = View()

    def create_task(self, name):
        name = name.capitalize()
        task = self.service.create_task(name)
        if not task:
            self.view.display_task_exists(name)
        else:
            self.view.display_task_created(task.id, task.name)

    def start_focus_in_task(self, task_id, duration: int = 0):
        # Проверяем, существует ли задача
        with self.service.session() as session:
            from app.models.task import Task
            from sqlalchemy import select
            task = session.scalar(select(Task).where(Task.id == task_id))
            if not task:
                self.view.display_task_not_found(task_id)
                return
            else:
                self.view.display_task_focus_start(task.name)

        # Создаем сессию в базе данных
        focus_session = self.service.start_focus_in_task(task_id)

        # Запускаем красивый таймер через View
        elapsed_time = self.view.display_beautiful_timer(duration)

        # Завершаем сессию с учетом прошедшего времени
        focus_session = self.service.finish_focus_in_task(
            focus_id=focus_session.id,
            task_id=task_id,
            end_time=datetime.now(),
            duration=elapsed_time
        )

        # Refresh task to get updated time
        with self.service.session() as session:
            updated_task = session.scalar(select(Task).where(Task.id == task_id))

        self.view.display_focus_session_completed(updated_task.time_spent / 60)

    def get_all_tasks(self):
        tasks = self.service.all_task()
        self.view.display_tasks_list(tasks)

    def get_stats_by_period(self, period, task_id: int | None):
        name_time = self.service.get_stats_by(period, task_id)
        self.view.display_statistics(name_time, period)

    def delete_task_and_sessions(self, task_id: int):
        res = self.service.delete_sessions_by_task(task_id)
        res1 = self.service.delete_task(task_id)
        if res or res1:
            self.view.display_info(f"Задача {task_id} и все сессии удалены")


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
    
    # удалить задачу и все сессии с ней
    del_parser = subparsers.add_parser("del", help='Удалить задачу и все сессии связанные с ней')
    del_parser.add_argument("task_id", type=int, help="ID задачи")

    args = parser.parse_args()

    # Initialize database
    init_db()

    # Initialize the App with View layer
    app = App()

    if args.command == "create":
        app.create_task(args.name)
    elif args.command == "list":
        app.get_all_tasks()
    elif args.command == "start":
        app.start_focus_in_task(args.task_id, args.duration)
    elif args.command == 'stats':
        app.get_stats_by_period(args.period, args.task)
    elif args.command == 'del':
        app.delete_task_and_sessions(args.task_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

