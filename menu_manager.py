from telegram.ext import CallbackContext
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup


class MenuManager:

    def __init__(self, note_manager, task_manager, habit_manager):
        self.note_manager = note_manager
        self.task_manager = task_manager
        self.habit_manager = habit_manager

    async def show_note_menu(self, update: Update, context: CallbackContext, text=" "):
        chat_id = update.message.chat_id
        menu_options = ["📝Add Note📝", "📖show Notes📖", "❌Delete Note❌"]
        menu_keyboard = [[KeyboardButton(option)] for option in menu_options]
        menu = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=menu)

    async def show_task_menu(self, update: Update, context: CallbackContext, text=" "):
        chat_id = update.message.chat_id
        menu_options = ["➕Add Task➕", "🔎show Tasks🔍", "✅Complete Task✅", "❌Delete Task❌"]
        menu_keyboard = [[KeyboardButton(option)] for option in menu_options]
        menu = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=menu)

    async def show_habit_menu(self, update: Update, context: CallbackContext, text=" "):
        chat_id = update.message.chat_id
        menu_options = ["➕Add Habit➕", "🔎show Habits🔍", "✅Complete Habit✅", "❌Delete Habit❌"]
        menu_keyboard = [[KeyboardButton(option)] for option in menu_options]
        menu = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=menu)

    async def handle_note_menu_command(self, command, update: Update, context: CallbackContext):
        if command == "add note":
            await self.note_manager.add_note(update, context)
        elif command == "show notes":
            await self.note_manager.show_notes(update, context)
        elif command == "delete note":
            await self.note_manager.delete_note(update, context)
        else:
            text = "Invalid option. Please choose from the note menu."
            await self.show_task_menu(update, context, text)

    async def handle_task_menu_command(self, command, update: Update, context: CallbackContext):
        if command == "add task":
            await self.task_manager.add_task(update, context)
        elif command == "show tasks":
            await self.task_manager.show_tasks(update, context)
        elif command == "complete task":
            await self.task_manager.complete_task(update, context)
        elif command == "delete task":
            await self.task_manager.delete_task(update, context)
        else:
            text = "Invalid option. Please choose from the task menu."
            await self.show_task_menu(update, context, text)

    async def handle_habit_menu_command(self, command, update: Update, context: CallbackContext):
        if command == "add habit":
            await self.habit_manager.add_habit(update, context)
        elif command == "show habits":
            await self.habit_manager.show_habits(update, context)
        elif command == "complete habit":
            await self.habit_manager.complete_habit(update, context)
        elif command == "delete habit":
            await self.habit_manager.delete_habit(update, context)
        else:
            text = "Invalid option. Please choose from the habit menu."
            await self.show_task_menu(update, context, text)
