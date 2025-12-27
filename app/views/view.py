from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from datetime import datetime
from typing import List, Dict, Any


class View:
    def __init__(self):
        self.console = Console()

    def display_welcome(self):
        """Display welcome message"""
        welcome_text = Text("Focus Tracker CLI", style="bold blue")
        welcome_text.append("\n\nProfessional Time Management Tool", style="italic")
        self.console.print(Panel(welcome_text, expand=False))

    def display_task_created(self, task_id: int, task_name: str) -> None:
        """Display task creation confirmation"""
        success_text = Text(f"✅ Задача создана", style="bold green")
        table = Table(show_header=False, box=None)
        table.add_row("ID:", str(task_id))
        table.add_row("Название:", task_name)
        self.console.print(success_text)
        self.console.print(table)

    def display_task_exists(self, task_name: str) -> None:
        """Display message when task already exists"""
        warning_text = Text(f"⚠️  Задача: {task_name} уже существует", style="bold yellow")
        self.console.print(warning_text)

    def display_task_not_found(self, task_id: int) -> None:
        """Display message when task is not found"""
        error_text = Text(f"❌ Ошибка: Задача с ID {task_id} не найдена", style="bold red")
        self.console.print(error_text)

    def display_task_focus_start(self, task_name: str) -> None:
        """Display task focus start message"""
        info_text = Text(f"🎯 Задача: {task_name}", style="bold cyan")
        self.console.print(info_text)
        self.console.print(Text("Начинаем сессию фокусировки...", style="bold"))

    def display_timer_running(self, duration_minutes: int = 0) -> None:
        """Display timer running message"""
        if duration_minutes == 0:
            self.console.print(Text("⏱️  Бесконечный таймер запущен", style="bold yellow"))
        else:
            self.console.print(Text(f"⏱️  Таймер запущен на {duration_minutes} минут", style="bold yellow"))

    def display_timer_interrupted(self, elapsed_time_formatted: str) -> None:
        """Display timer interrupted message"""
        warning_text = Text(f"⏸️  Таймер прерван. Прошло времени: {elapsed_time_formatted}", style="bold yellow")
        self.console.print(warning_text)

    def display_timer_completed(self, elapsed_time_formatted: str, is_countdown: bool = True) -> None:
        """Display timer completed message"""
        if is_countdown:
            success_text = Text(f"✅ Таймер завершен. Время вышло!", style="bold green")
        else:
            success_text = Text(f"✅ Таймер завершен. Прошло времени: {elapsed_time_formatted}", style="bold green")
        self.console.print(success_text)

    def display_focus_session_completed(self, total_time_minutes: float) -> None:
        """Display focus session completion message"""
        success_text = Text(f"🎉 Рабочая сессия завершена.", style="bold green")
        info_text = Text(f"Общее время в задаче: {round(total_time_minutes)} минут", style="bold")
        self.console.print(success_text)
        self.console.print(info_text)

    def display_tasks_list(self, tasks: List[Any]) -> None:
        """Display list of all tasks in a table"""
        if not tasks:
            self.console.print(Text("❌ Нет созданных задач", style="bold red"))
            return

        self.console.print(Text("📋 Список задач:", style="bold underline"))

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Название", style="cyan", min_width=15)
        table.add_column("Общее время", style="green")

        for task in tasks:
            hours_spent = task.time_spent // 3600
            minutes_spent = (task.time_spent % 3600) // 60
            time_str = f"{hours_spent} ч. {minutes_spent} мин."
            table.add_row(str(task.id), task.name, time_str)

        self.console.print(table)

    def display_statistics(self, stats: Dict[str, int], period: str) -> None:
        """Display statistics for a given period"""
        if not stats:
            self.console.print(Text("📊 За этот период нет рабочих сессий", style="bold yellow"))
            return

        period_names = {
            'today': 'сегодня',
            'week': 'неделю',
            'month': 'месяц',
            'year': 'год'
        }
        
        period_name = period_names.get(period, period)
        title = Text(f"📈 Статистика за {period_name}:", style="bold underline")
        self.console.print(title)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Задача", style="cyan", min_width=15)
        table.add_column("Время", style="green")

        for name, time in stats.items():
            if time > 60:
                time_value = round(time / 60)
                unit = 'часов'
            else:
                time_value = time
                unit = 'минут'
            table.add_row(name, f"{time_value} {unit}")

        self.console.print(table)

    def display_error(self, message: str) -> None:
        """Display error message"""
        error_text = Text(f"❌ {message}", style="bold red")
        self.console.print(error_text)

    def display_info(self, message: str) -> None:
        """Display info message"""
        info_text = Text(f"ℹ️  {message}", style="bold blue")
        self.console.print(info_text)

    def display_warning(self, message: str) -> None:
        """Display warning message"""
        warning_text = Text(f"⚠️  {message}", style="bold yellow")
        self.console.print(warning_text)

    def get_user_input(self, prompt: str) -> str:
        """Get user input with styled prompt"""
        return Prompt.ask(f"[bold cyan]{prompt}[/bold cyan]")

    def display_beautiful_timer(self, duration_minutes: int = 0):
        """Display a beautiful timer interface with live updating"""
        from app.utils.timer import Timer
        import time
        from rich.live import Live

        timer = Timer(duration_minutes)
        timer.start_timer()

        try:
            with Live(console=self.console, refresh_per_second=1) as live:
                while timer.is_running and not timer.stop_event.is_set():
                    elapsed = timer.get_elapsed_time()

                    if duration_minutes == 0:  # Бесконечный таймер - показываем прошедшее время
                        time_text = f"ПРОШЛО ВРЕМЕНИ: {timer.format_time(elapsed)}"
                        title = "БЕСКОНЕЧНЫЙ ТАЙМЕР"
                    else:  # Таймер с обратным отсчетом - показываем оставшееся время
                        remaining = timer.get_remaining_time()
                        time_text = f"ОСТАЛОСЬ ВРЕМЕНИ: {timer.format_time(remaining)}"
                        title = f"ТАЙМЕР НА {duration_minutes} МИНУТ"

                    # Create large text for timer
                    timer_text = Text()
                    timer_text.append(f"\n{title}\n\n", style="bold yellow underline")
                    timer_text.append(f"{time_text}\n", style="bold white on blue")

                    panel = Panel(
                        Align.center(timer_text),
                        title="[bold green]Focus Timer[/bold green]",
                        border_style="bright_yellow",
                        expand=False,
                        padding=(2, 2)
                    )

                    live.update(panel)

                    # Check for interruption more frequently to catch Ctrl+C
                    for _ in range(10):  # Check 10 times per second
                        if timer.stop_event.is_set():
                            break
                        time.sleep(0.1)

                    if duration_minutes != 0 and elapsed >= timer.duration_seconds:
                        break

            # Stop timer and return elapsed time
            elapsed_time = timer.stop_timer()

            # Display completion message
            self.console.print(f"\n[bold green]Таймер завершен![/bold green]")
            if duration_minutes == 0:  # Бесконечный таймер
                self.console.print(f"[bold yellow]Прошло времени: {timer.format_time(elapsed_time)}[/bold yellow]")
            else:  # Таймер с обратным отсчетом
                if elapsed_time >= timer.duration_seconds:
                    self.console.print(f"[bold green]Время вышло![/bold green]")
                else:
                    self.console.print(f"[bold yellow]Прошло времени: {timer.format_time(elapsed_time)}[/bold yellow]")

            return elapsed_time

        except KeyboardInterrupt:
            elapsed_time = timer.stop_timer()
            self.console.print(f"\n[bold red]Таймер прерван.[/bold red]")
            self.console.print(f"[bold yellow]Прошло времени: {timer.format_time(elapsed_time)}[/bold yellow]")
            return elapsed_time