# TODO+ — Smart Task Manager

## Description

TODO+ is a task management system that allows users to create, organize, and track their tasks. The project includes a web application built with Django and a Telegram bot for managing tasks directly from Telegram.

---

## Technologies

- **Python 3.14**
- **Django 6.0** — web framework
- **python-telegram-bot** — Telegram bot library
- **dateparser** — natural language date parsing
- **requests** — weather API integration

---

## Installation

1. Clone or download the project

2. Create and activate virtual environment:
```
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```
pip install django python-telegram-bot requests dateparser
```

4. Go to project folder:
```
cd taskflow
```

5. Apply migrations:
```
python manage.py migrate
```

---

## Running

### Web application

```
cd taskflow
python manage.py runserver
```

Open in browser: `http://127.0.0.1:8000`

### Telegram bot

Open a second terminal and run:

```
cd taskflow
python bot.py
```

---

## Telegram Bot Commands

| Command | Description |
|---------|-------------|
| /start | Start the bot, enter your name |
| /list | Show all your tasks |
| /add | Add a new task |
| /done | Mark a task as done |
| /delete | Delete a task |
| /search | Search tasks by keyword |
| /stats | Show task statistics |
| /today | Show tasks due today |
| /overdue | Show overdue tasks |
| /help | Show all commands |
| /cancel | Cancel current action |

---

## Bot Usage Examples

**Adding a task:**
```
User: /add
Bot: Enter task title:
User: Buy groceries
Bot: Choose priority:
User: High
Bot: Deadline? (DD.MM.YYYY, 'tomorrow' or skip):
User: tomorrow
Bot: Task 'Buy groceries' added!
```

**Viewing tasks:**
```
User: /list
Bot:
1. ○ [high] Buy groceries | 19.05.2026
2. ✓ [medium] Read Python book | нет
```

**Statistics:**
```
User: /stats
Bot:
Total tasks: 5
Done: 2
In progress: 3

High priority: 2
Medium priority: 2
Low priority: 1
```

**Natural language:**
```
User: привет
Bot: Привет! Чем могу помочь?

User: список
Bot: (shows task list)

User: спасибо
Bot: Пожалуйста! Если нужна помощь — пиши.
``


## Project Structure

```
PyCharmMiscProject/
    taskflow/
        taskflow/
            settings.py
            urls.py
        tasks/
            models.py
            views.py
            templates/
                tasks/
                    list.html
                    add.html
                    login.html
                    register.html
        bot.py
        manage.py
    script.py      ← Stage 1: console application
    tasks.json
```
