import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext

from urllib.parse import quote_plus
import arrow
import asyncio
from datetime import datetime

from task_manager import TaskManager
from note_manager import NoteManager
from menu_manager import MenuManager
from habit_manager import HabitManager
from quote_manager import QuoteManager
from report_manager import ReportManager
from journal_manager import JournalManager
from database_manager import DatabaseManager


async def start(update: Update, context: CallbackContext) -> None:
    """Send an initial message when the user starts the bot."""
    user_name = update.message.from_user.first_name
    chat_id = update.message.chat_id

    await update.message.reply_text(f"Hi {user_name}! 👋\n"
                                    "Welcome to the Journaling bot!\n"
                                    "I can help you with daily Journaling✨\n\n"
                                    "Try:\n"
                                    "- /task_manager to work with tasks✅\n"
                                    "- /note_manager to write your notes📝\n"
                                    "- /habit_manager to track habits🎯\n"
                                    "- /state to set your current location and activities🌍\n")
    await asyncio.sleep(3)
    await update.message.reply_text("After you can try: /end_day to complete your day😌\n"
                                    "And to receive Your Daily Journal✨\n"
                                    "Similar to this one👇🏿!")
    await asyncio.sleep(2)
    sample_pdf = os.path.join(script_directory, 'utilities/Sample Journal.pdf')
    await context.bot.send_document(chat_id=chat_id, document=open(sample_pdf, 'rb'))

    video_file = os.path.join(script_directory, 'utilities/Bot Tutorial.mp4')
    await context.bot.send_video(chat_id=chat_id, video=open(video_file, 'rb'))

    quote_manager.get_quote(chat_id)
    # Saving user for daily-quote sending
    database_manager.save_user(chat_id, user_name)


async def note_command(update: Update, context: CallbackContext):
    text = "Choose an option from the menu:"
    await menu_manager.show_note_menu(update, context, text)


async def task_command(update: Update, context: CallbackContext):
    text = "Choose an option from the menu:"
    await menu_manager.show_task_menu(update, context, text)


async def habit_command(update: Update, context: CallbackContext):
    text = "Choose an option from the menu:"
    await menu_manager.show_habit_menu(update, context, text)


async def set_state(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.user_data[chat_id] = {'state': 'set_state'}
    await update.message.reply_text(f"Define your current location and activities🌍!"
                                    f"\n\nFor example:\n"
                                    f"Russia, Orenburg, Learning IT, Online University Classes")


async def message_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user_input = update.message.text.strip().lower()[1:-1]

    note_commands = ["add note", "show notes", "delete note"]
    if user_input in note_commands:
        await menu_manager.handle_note_menu_command(user_input, update, context)
        return

    task_commands = ["add task", "show tasks", "complete task", "delete task"]
    if user_input in task_commands:
        await menu_manager.handle_task_menu_command(user_input, update, context)
        return

    habit_commands = ["add habit", "show habits", "complete habit", "delete habit"]
    if user_input in habit_commands:
        await menu_manager.handle_habit_menu_command(user_input, update, context)
        return

    if context.user_data.get(chat_id) and context.user_data[chat_id]['state'] == 'add_note':
        await note_manager.handle_add_note(update, context)
        return
    elif context.user_data.get(chat_id) and context.user_data[chat_id]['state'] == 'delete_note':
        await note_manager.handle_delete_note(update, context)
        return

    elif context.user_data.get(chat_id) and context.user_data[chat_id]['state'] == 'add_task':
        await task_manager.handle_add_task(update, context)
        return
    elif context.user_data.get(chat_id) and context.user_data[chat_id]['state'] == 'complete_task':
        await task_manager.handle_complete_task(update, context)
        return
    elif context.user_data.get(chat_id) and context.user_data[chat_id]['state'] == 'delete_task':
        await task_manager.handle_delete_task(update, context)
        return

    elif context.user_data.get(chat_id) and context.user_data[chat_id]['state'] == 'add_habit':
        await habit_manager.handle_add_habit(update, context)
        return
    elif context.user_data.get(chat_id) and context.user_data[chat_id]['state'] == 'complete_habit':
        await habit_manager.handle_complete_habit(update, context)
        return
    elif context.user_data.get(chat_id) and context.user_data[chat_id]['state'] == 'delete_habit':
        await habit_manager.handle_delete_habit(update, context)
        return
    elif context.user_data.get(chat_id) and context.user_data[chat_id]['state'] == 'day_rating':
        await journal_manager.handle_add_rating(update, context)
        return
    elif context.user_data.get(chat_id) and context.user_data[chat_id]['state'] == 'set_state':
        await journal_manager.add_state(update, context)
        return
    else:
        await update.message.reply_text(f"Do not type yet!\n"
                                        f"First choose an option from menu")
        return


async def end_day(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    await update.message.reply_text("It's the end of the day!\nLet's sum up✍️...")

    await asyncio.sleep(2)

    keyboard = [
        [
            InlineKeyboardButton("😎", callback_data="😎"),  # Excited
            InlineKeyboardButton("😊", callback_data="😊"),  # Content
            InlineKeyboardButton("😐", callback_data="😐"),  # Neutral
        ],
        [
            InlineKeyboardButton("😡", callback_data="😡"),  # Angry
            InlineKeyboardButton("😞", callback_data="😞"),  # Sad
            InlineKeyboardButton("🤕", callback_data="🤕"),  # Sick
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('How do you feel today?', reply_markup=reply_markup)

    habits = database_manager.get_habits(chat_id)

    if habits:
        for habit in habits:
            if 'completed' not in habit or not habit['completed']:
                await asyncio.sleep(4)
                keyboard = [
                    [
                        InlineKeyboardButton("Yes", callback_data=str(habit['id'])),
                        InlineKeyboardButton("No", callback_data="no")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(f'Have you attended or done {habit["description"]}?',
                                                reply_markup=reply_markup)

    await asyncio.sleep(3)
    context.user_data[chat_id] = {'state': 'day_rating'}
    await update.message.reply_text('How do you rate your day from 1 to 10?')


async def callback_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    callback_data = query.data

    if callback_data in ["😎", "😊", "😐", "😡", "😞", "🤕"]:
        if callback_data == "😎":
            mood_score = 10
        elif callback_data == "😊":
            mood_score = 7
        elif callback_data == "😐":
            mood_score = 5
        elif callback_data == "😞":
            mood_score = 3
        elif callback_data == "🤕":
            mood_score = 2
        else:
            mood_score = 0
        database_manager.save_mood(chat_id, callback_data, mood_score)
        return
    elif callback_data == "no":
        await query.answer("No worries, tomorrow is a new opportunity. You got this💪🏿")
        return
    try:
        habit_id = int(callback_data)

        if database_manager.habit_exists(chat_id, habit_id):
            database_manager.complete_habit(chat_id, habit_id)
            await query.answer(f"The habit completed✅")
    except ValueError:
        await habit_manager.complete_habit(update, context)


async def send_quote(context: CallbackContext):
    users = database_manager.get_all_users()

    if users:
        print('Sending Quotes...')
        for user in users:
            try:
                quote = quote_manager.get_quote(user['chat_id'])
                await context.bot.send_message(chat_id=user['chat_id'], text="Today's quote🫰🏿:")
                await context.bot.send_message(chat_id=user['chat_id'], text=quote)

            except telegram.error.Forbidden as e:
                print(f"Could not send quote to chat_id {user['chat_id']}. Forbidden: {e}")
            except Exception as e:
                print(f"An error occurred while sending quotes to {user['chat_id']}: {e}")


async def send_reminder(context: CallbackContext):
    users = database_manager.get_all_users()

    if users:
        print('Sending Reminders...')
        for user in users:
            try:
                await context.bot.send_message(chat_id=user['chat_id'],
                                               text="🌟 Reminder:\n"
                                               "⏳ Only 30 minutes left to wrap up your day's activities!\n\n"
                                               "After use /end_day to receive your Journal of the day! ✨")

            except telegram.error.Forbidden as e:
                print(f"Could not send reminder to chat_id {user['chat_id']}. Forbidden: {e}")
            except Exception as e:
                print(f"An error occurred while sending reminder to {user['chat_id']}: {e}")


async def send_report(context: CallbackContext):
    if datetime.now().weekday() == 4:
        users = database_manager.get_all_users()

        if users:
            print('Sending Reports...')
            for user in users:
                try:
                    await context.bot.send_message(chat_id=user['chat_id'], text="Hi, it's Friday! 🌞\n"
                                                                                 "Here is your Weekly Report:")

                    mood_report = report_manager.generate_mood_report(user['chat_id'])
                    if mood_report:
                        await asyncio.sleep(1)
                        await context.bot.send_message(chat_id=user['chat_id'], text=mood_report)
                    tasks_report = report_manager.generate_tasks_report(user['chat_id'])
                    if tasks_report:
                        await asyncio.sleep(1)
                        await context.bot.send_message(chat_id=user['chat_id'], text=tasks_report)
                    habits_report = report_manager.generate_habits_report(user['chat_id'])
                    if habits_report:
                        await asyncio.sleep(1)
                        await context.bot.send_message(chat_id=user['chat_id'], text=habits_report)
                    satisfaction_report = report_manager.generate_satisfaction_report(user['chat_id'])
                    if satisfaction_report:
                        await asyncio.sleep(1)
                        await context.bot.send_message(chat_id=user['chat_id'],
                                                       text="Now based on Your Own Daily Ratings we have🤩...")
                        await asyncio.sleep(1)
                        await context.bot.send_message(chat_id=user['chat_id'], text=satisfaction_report)
                    else:
                        await context.bot.send_message(chat_id=user['chat_id'],
                                                       text="You do not have enough data 😞")
                        await asyncio.sleep(1)
                        await context.bot.send_message(chat_id=user['chat_id'],
                                                       text="Please try using the bot more often\n"
                                                            "To get weekly reports on your weekly:\n"
                                                            "● Mood levels 😊\n"
                                                            "● Tasks 📋\n"
                                                            "● Habits 🌱\n\n"
                                                            "Try /start to get started! 🤠")

                except telegram.error.Forbidden as e:
                    print(f"Could not send message to chat_id {user['chat_id']}. Forbidden: {e}")
                except Exception as e:
                    print(f"An error occurred while sending messages to {user['chat_id']}: {e}")
    else:
        print("It's not Friday. No reports will be sent today.")

def main():
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('note_manager', note_command))
    app.add_handler(CommandHandler('task_manager', task_command))
    app.add_handler(CommandHandler('habit_manager', habit_command))
    app.add_handler(CommandHandler('end_day', end_day))
    app.add_handler(CommandHandler('state', set_state))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("Current time in Berlin:", berlin.format('YYYY-MM-DD HH:mm:ss'))
    job_queue = app.job_queue
    job_queue.run_daily(send_quote, time=quote_time, days=(0, 1, 2, 3, 4, 5, 6))
    job_queue.run_daily(send_reminder, time=reminder_time, days=(0, 1, 2, 3, 4, 5, 6))
    job_queue.run_repeating(send_report, interval=86400)

    print('Polling...')
    app.run_polling()


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    DB_URL = os.getenv("DB_URL")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")

    connection_string = f"mongodb+srv://{username}:{password}@cluster0.vn5v3ng.mongodb.net/?retryWrites=true&w=majority"

    database_manager = DatabaseManager(connection_string)
    habit_manager = HabitManager(database_manager)
    task_manager = TaskManager(database_manager)
    note_manager = NoteManager(database_manager)
    quote_manager = QuoteManager(database_manager)
    report_manager = ReportManager(database_manager)
    journal_manager = JournalManager(database_manager)
    menu_manager = MenuManager(note_manager, task_manager, habit_manager)

    script_directory = os.path.dirname(os.path.realpath(__file__))

    berlin = arrow.get(datetime.now(), 'local').to('Europe/Berlin')
    quote_time = berlin.replace(hour=17, minute=23, second=00, microsecond=0)
    reminder_time = berlin.replace(hour=17, minute=23, second=00, microsecond=0)

    main()
