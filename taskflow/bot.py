import os
import django
from datetime import datetime, date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskflow.settings")
django.setup()

from tasks.models import Task, TelegramUser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters, ConversationHandler, CallbackQueryHandler
)
from asgiref.sync import sync_to_async

TOKEN = "8265486442:AAGovuD08MuP_AS5TiI3Y3a3LwORq_obwjA"

GREETING = 0
TITLE, PRIORITY, DEADLINE = range(1, 4)
SEARCH = 10


def get_main_keyboard():
    keyboard = [
        ['/list', '/add'],
        ['/done', '/delete'],
        ['/search', '/stats'],
        ['/today', '/overdue'],
        ['/help']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_priority_keyboard():
    keyboard = [['High', 'Medium', 'Low'], ['/cancel']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


async def get_user(update):
    tg_user = update.message.from_user
    user_obj, _ = await sync_to_async(TelegramUser.objects.get_or_create)(
        telegram_id=tg_user.id,
        defaults={'name': tg_user.first_name or '', 'username': tg_user.username or ''}
    )
    return user_obj


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в TODO+!\nКак мне к тебе обращаться?",
        reply_markup=ReplyKeyboardRemove()
    )
    return GREETING


async def save_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text
    tg_user = update.message.from_user
    await sync_to_async(TelegramUser.objects.get_or_create)(
        telegram_id=tg_user.id,
        defaults={'name': user_name, 'username': tg_user.username or ''}
    )
    context.user_data["user_name"] = user_name
    await update.message.reply_text(
        f"Приятно познакомиться, {user_name}!",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/list — все задачи\n"
        "/add — добавить задачу\n"
        "/done — отметить выполненной\n"
        "/delete — удалить задачу\n"
        "/search — поиск по задачам\n"
        "/stats — статистика\n"
        "/today — задачи на сегодня\n"
        "/overdue — просроченные задачи\n"
        "/cancel — отмена\n"
        "/start — начать заново",
        reply_markup=get_main_keyboard()
    )


async def task_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_obj = await get_user(update)
        tasks = await sync_to_async(list)(Task.objects.filter(user=user_obj).order_by('id'))
        if not tasks:
            await update.message.reply_text("Список задач пуст! Добавь первую задачу через /add.", reply_markup=get_main_keyboard())
            return
        text = "Твои задачи:\n\n"
        for t in tasks:
            status = "✓" if t.done else "○"
            deadline_str = t.deadline.strftime("%d.%m.%Y") if t.deadline else "нет"
            text += f"{t.id}. {status} [{t.priority}] {t.title} | {deadline_str}\n"
        await update.message.reply_text(text, reply_markup=get_main_keyboard())
    except Exception as e:
        await update.message.reply_text("Ошибка подключения к базе данных. Попробуй позже.")
        print(f"Ошибка task_list: {e}")

async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введи название задачи:", reply_markup=ReplyKeyboardRemove())
    return TITLE


async def add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Название не может быть пустым. Введи ещё раз:")
        return TITLE
    context.user_data["title"] = text
    await update.message.reply_text("Выбери приоритет:", reply_markup=get_priority_keyboard())
    return PRIORITY


async def add_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if text not in ["high", "medium", "low"]:
        await update.message.reply_text("Неверный приоритет. Выбери High, Medium или Low:", reply_markup=get_priority_keyboard())
        return PRIORITY
    context.user_data["priority"] = text
    await update.message.reply_text("Дедлайн? (ДД.ММ.ГГГГ, 'завтра' или skip):", reply_markup=ReplyKeyboardRemove())
    return DEADLINE


async def add_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    deadline = None
    if text != "skip":
        try:
            import dateparser
            parsed = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future', 'DATE_ORDER': 'DMY'})
            if parsed:
                deadline = parsed.date()
            else:
                await update.message.reply_text("Не понял дату. Попробуй ДД.ММ.ГГГГ или напиши skip:")
                return DEADLINE
        except Exception:
            await update.message.reply_text("Ошибка при обработке даты. Напиши skip или ДД.ММ.ГГГГ:")
            return DEADLINE

    try:
        user_obj = await get_user(update)
        await sync_to_async(Task.objects.create)(
            user=user_obj,
            title=context.user_data["title"],
            priority=context.user_data["priority"],
            deadline=deadline,
        )
        await update.message.reply_text(
            f"Задача '{context.user_data['title']}' добавлена!",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        await update.message.reply_text("Ошибка при сохранении задачи. Попробуй ещё раз.")
        print(f"Ошибка create: {e}")
    return ConversationHandler.END


async def show_action_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = "done" if "done" in update.message.text else "delete"
    user_obj = await get_user(update)
    tasks = await sync_to_async(list)(Task.objects.filter(user=user_obj).order_by('id'))
    if not tasks:
        await update.message.reply_text("Задач нет!", reply_markup=get_main_keyboard())
        return
    keyboard = []
    for t in tasks:
        status = "✓" if t.done else "○"
        keyboard.append([InlineKeyboardButton(f"{status} {t.title}", callback_data=f"{command}_{t.id}")])
    header = "Выбери задачу для отметки:" if command == "done" else "Выбери задачу для удаления:"
    await update.message.reply_text(header, reply_markup=InlineKeyboardMarkup(keyboard))



async def button_tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        action, task_id = query.data.split("_")
        task = await sync_to_async(Task.objects.get)(pk=int(task_id))
        if action == "done":
            task.done = not task.done
            await sync_to_async(task.save)()
            await query.edit_message_text(f"Статус '{task.title}': {'выполнена' if task.done else 'в работе'}.")
        elif action == "delete":
            title = task.title
            await sync_to_async(task.delete)()
            await query.edit_message_text(f"Задача '{title}' удалена.")
    except Task.DoesNotExist:
        await query.edit_message_text("Задача не найдена — возможно уже удалена.")
    except Exception as e:
        await query.edit_message_text("Произошла ошибка. Попробуй ещё раз.")
        print(f"Ошибка button_tap: {e}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_obj = await get_user(update)
    tasks = await sync_to_async(list)(Task.objects.filter(user=user_obj))
    total = len(tasks)
    done = sum(1 for t in tasks if t.done)
    pending = total - done
    high = sum(1 for t in tasks if t.priority == "high")
    medium = sum(1 for t in tasks if t.priority == "medium")
    low = sum(1 for t in tasks if t.priority == "low")
    await update.message.reply_text(
        f"Статистика:\n\n"
        f"Всего задач: {total}\n"
        f"Выполнено: {done}\n"
        f"В работе: {pending}\n\n"
        f"Высокий приоритет: {high}\n"
        f"Средний приоритет: {medium}\n"
        f"Низкий приоритет: {low}",
        reply_markup=get_main_keyboard()
    )


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_obj = await get_user(update)
    today_date = date.today()
    tasks = await sync_to_async(list)(Task.objects.filter(user=user_obj, deadline=today_date))
    if not tasks:
        await update.message.reply_text("На сегодня задач нет!", reply_markup=get_main_keyboard())
        return
    text = "Задачи на сегодня:\n\n"
    for t in tasks:
        status = "✓" if t.done else "○"
        text += f"{t.id}. {status} [{t.priority}] {t.title}\n"
    await update.message.reply_text(text, reply_markup=get_main_keyboard())


async def overdue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_obj = await get_user(update)
    today_date = date.today()
    tasks = await sync_to_async(list)(
        Task.objects.filter(user=user_obj, deadline__lt=today_date, done=False)
    )
    if not tasks:
        await update.message.reply_text("Просроченных задач нет!", reply_markup=get_main_keyboard())
        return
    text = "Просроченные задачи:\n\n"
    for t in tasks:
        text += f"{t.id}. [{t.priority}] {t.title} | {t.deadline.strftime('%d.%m.%Y')}\n"
    await update.message.reply_text(text, reply_markup=get_main_keyboard())


async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введи слово для поиска:", reply_markup=ReplyKeyboardRemove())
    return SEARCH


async def search_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Введи слово для поиска:")
        return SEARCH
    try:
        user_obj = await get_user(update)
        tasks = await sync_to_async(list)(Task.objects.filter(user=user_obj, title__icontains=text))
        if not tasks:
            await update.message.reply_text(f"По запросу '{text}' ничего не найдено.", reply_markup=get_main_keyboard())
        else:
            result = f"Результаты по '{text}':\n\n"
            for t in tasks:
                status = "✓" if t.done else "○"
                result += f"{t.id}. {status} [{t.priority}] {t.title}\n"
            await update.message.reply_text(result, reply_markup=get_main_keyboard())
    except Exception as e:
        await update.message.reply_text("Ошибка при поиске. Попробуй позже.")
        print(f"Ошибка search: {e}")
    return ConversationHandler.END


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if any(w in text for w in ["привет", "хай", "hello", "hi"]):
        name = context.user_data.get("user_name", "")
        await update.message.reply_text(f"Привет{' ' + name if name else ''}! Чем могу помочь?", reply_markup=get_main_keyboard())

    elif any(w in text for w in ["как дела", "как ты", "что нового"]):
        await update.message.reply_text("Всё отлично! Готов помогать с задачами.", reply_markup=get_main_keyboard())

    elif any(w in text for w in ["спасибо", "thanks", "thank you"]):
        await update.message.reply_text("Пожалуйста! Если нужна помощь — пиши.", reply_markup=get_main_keyboard())

    elif any(w in text for w in ["пока", "bye", "до свидания"]):
        await update.message.reply_text("Пока! Не забывай про задачи.", reply_markup=get_main_keyboard())

    elif any(w in text for w in ["помощь", "help", "что умеешь"]):
        await help_cmd(update, context)

    elif any(w in text for w in ["задач", "список", "list"]):
        await task_list(update, context)

    elif any(w in text for w in ["статистик", "stats", "сколько"]):
        await stats(update, context)

    elif any(w in text for w in ["сегодня", "today"]):
        await today(update, context)

    elif any(w in text for w in ["просроч", "overdue"]):
        await overdue(update, context)

    else:
        await update.message.reply_text(
            "Не понимаю. Попробуй написать 'помощь' или используй /help.",
            reply_markup=get_main_keyboard()
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.", reply_markup=get_main_keyboard())
    return ConversationHandler.END


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    start_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={GREETING: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_name)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    add_conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={
            TITLE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, add_title)],
            PRIORITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_priority)],
            DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_deadline)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    search_conv = ConversationHandler(
        entry_points=[CommandHandler("search", search_start)],
        states={SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_query)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(start_conv)
    app.add_handler(add_conv)
    app.add_handler(search_conv)
    app.add_handler(CommandHandler("list", task_list))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("overdue", overdue))
    app.add_handler(CommandHandler(["done", "delete"], show_action_buttons))
    app.add_handler(CallbackQueryHandler(button_tap))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    print("Bot is running...")
    app.run_polling()
