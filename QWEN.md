# Focus Tracker CLI Application

## Project Overview

This is a command-line interface (CLI) application designed for time management and focus tracking. The application allows users to create tasks, set timers for focused work sessions, and track statistics on time spent on different tasks. It implements a Pomodoro-style timer functionality where users can set work periods and track their productivity.

The application is built with Python and uses SQLAlchemy as an ORM with SQLite as the database backend. It provides a simple but effective way to manage tasks and track time spent on them, with support for viewing statistics over different time periods (daily, weekly, monthly, yearly).

## Architecture

The application follows a service-oriented architecture with the following main components:

- **Main Application (`app/main.py`)**: Contains the `App` and `Service` classes that implement the business logic and CLI interface
- **Models (`app/models/`)**: SQLAlchemy models for tasks and focus sessions
- **Repositories (`app/repositories/`)**: Data access layer with methods for CRUD operations
- **Database (`app/database/`)**: Database initialization and session management
- **Utilities (`app/utils/`)**: Helper functions including timer implementation and period mapping

### Key Models

- **Task**: Represents a work task with name, creation date, and total time spent
- **FocusSession**: Represents a focused work session with start/end times, duration, and associated task

### Key Features

1. **Task Management**: Create and list tasks
2. **Timer Functionality**: Start timers for tasks with optional duration limits
3. **Time Tracking**: Automatically track time spent on tasks
4. **Statistics**: View time spent on tasks over different periods (today, week, month, year)

## Building and Running

### Prerequisites

- Python 3.12 or higher
- Package manager: uv (recommended) or pip

### Setup

1. Install dependencies:
   ```bash
   uv sync  # If using uv
   # OR
   pip install -r requirements.txt  # If using pip with generated requirements
   ```

2. The application uses SQLite as its database, which is automatically created as `focus_tracker.db` in the project root.

### Commands

The application provides the following CLI commands:

#### Create a Task
```bash
python -m app.main create "task_name"
```
Creates a new task with the specified name.

#### List All Tasks
```bash
python -m app.main list
```
Displays all created tasks with their IDs and total time spent.

#### Start a Focus Session
```bash
python -m app.main start <task_id> [--duration MINUTES]
```
Starts a timer for the specified task. The `--duration` parameter is optional and sets a time limit in minutes (0 for infinite timer).

#### View Statistics
```bash
python -m app.main stats <period> [--task TASK_ID]
```
Shows statistics for time spent on tasks. Period can be:
- `today`: Statistics for the current day
- `week`: Statistics for the past 7 days
- `month`: Statistics for the past 30 days
- `year`: Statistics for the past 365 days

The optional `--task` parameter filters statistics for a specific task.

## Development Conventions

### Code Structure
- Business logic is separated from CLI interface in the `Service` class
- Data access is abstracted through repository patterns
- Models use SQLAlchemy ORM with proper relationships
- Timer functionality is implemented with threading for real-time display

### Database Schema
- Uses SQLite with automatic table creation on startup
- Two main tables: `tasks` and `focus_sessions`
- Foreign key relationship between focus sessions and tasks

### Timer Implementation
- Supports both infinite and countdown timers
- Real-time display of elapsed or remaining time
- Handles interruption with Ctrl+C
- Tracks duration in seconds for precision

## Dependencies

The project uses:
- `sqlalchemy>=2.0.45`: ORM for database operations
- `aiosqlite>=0.22.1`: Asynchronous SQLite support (though not currently used in an async context)
- Standard Python libraries for threading, datetime, and signal handling

## File Structure

```
project_python/
├── app/
│   ├── main.py              # Main application and CLI entry point
│   ├── database/
│   │   └── db.py           # Database initialization and session management
│   ├── models/
│   │   ├── base.py         # Base SQLAlchemy model
│   │   ├── task.py         # Task model
│   │   └── focus_session.py # Focus session model
│   ├── repositories/
│   │   ├── task.py         # Task data access layer
│   │   └── focus_session.py # Focus session data access layer
│   └── utils/
│       ├── timer.py        # Timer implementation
│       └── period_map.py   # Period mapping for statistics
├── focus_tracker.db        # SQLite database (generated)
├── pyproject.toml          # Project dependencies and metadata
├── uv.lock                 # Dependency lock file
└── README.md               # Project description
```