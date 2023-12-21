from telegram import Update
from telegram.ext import CallbackContext


class HabitManager:

    def __init__(self, db):
        self.db = db

    async def add_habit(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        context.user_data[chat_id] = {'state': 'add_habit'}
        await update.message.reply_text('Please write the habit you want to track.')

    async def handle_add_habit(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        habit_description = update.message.text.strip()

        habit_id = self.db.save_habit(chat_id, habit_description)

        if habit_id:
            context.user_data[chat_id]['state'] = ''
            await update.message.reply_text(f"New Habit was added💪🏿!")

    async def show_habits(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id

        habits = self.db.get_habits(chat_id)

        if habits:

            action_habits = [habit for habit in habits if not habit.get('completed', False)]
            completed_habits = [habit for habit in habits if habit.get('completed', True)]

            if action_habits:
                action_habits_text = "\n".join([f"● {habit['description']}" for habit in action_habits])
                action_habits_message = "Action Habits🔥:\n__________________________\n" + action_habits_text
                await update.message.reply_text(action_habits_message)
            if completed_habits:
                completed_habits_text = "\n".join([f"● {habit['description']}" for habit in completed_habits])
                completed_habits_message = "Completed Habits✅:\n__________________________\n" + completed_habits_text
                await update.message.reply_text(completed_habits_message)
        else:
            await update.message.reply_text("You do not have any habits yet!")

    async def complete_habit(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id

        habits = self.db.get_habits(chat_id)

        action_habits = [habit for habit in habits if 'completed' not in habit or habit['completed'] is False]

        if action_habits:
            context.user_data[chat_id] = {'state': 'complete_habit'}
            habits_text = "\n".join([f"{habit['id']}. {habit['description']}" for habit in action_habits])
            await update.message.reply_text(f"Your habits to complete:\n{habits_text}\n\n__________________________\n"
                                            "Enter the ID of the habit you want to mark as completed.")
        else:
            await update.message.reply_text("You do not have any habits to complete!")

    async def handle_complete_habit(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        user_input = update.message.text.strip()

        try:
            habit_id = int(user_input)

            if self.db.habit_exists(chat_id, habit_id):
                completed = self.db.complete_habit(chat_id, habit_id)
                if completed:
                    context.user_data[chat_id]['state'] = ''
                    await update.message.reply_text(f"The habit No.{habit_id} has been marked as completed✅")
            else:
                context.user_data[chat_id] = {'state': 'complete_habit'}
                await update.message.reply_text("Invalid habit ID. Please choose a valid ID from the list👆🏿")
        except ValueError:
            context.user_data[chat_id] = {'state': 'complete_habit'}
            await update.message.reply_text("Invalid input. Please enter a valid habit ID numer.")

    async def delete_habit(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        habits = self.db.get_habits(chat_id)
        if habits:
            context.user_data[chat_id] = {'state': 'delete_habit'}
            habit_text = "\n".join([f"{habit['id']}. {habit['description']}" for habit in habits])
            await update.message.reply_text(f"Your habits:\n{habit_text}\n\n"
                                            "Enter the ID of the habit you want to delete.")
        else:
            await update.message.reply_text("You do not have any habits yet!")

    async def handle_delete_habit(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        user_input = update.message.text.strip()

        try:
            habit_id = int(user_input)

            if self.db.habit_exists(chat_id, habit_id):

                self.db.delete_habit(chat_id, habit_id)
                context.user_data[chat_id]['state'] = ''
                await update.message.reply_text(f"The task No.{habit_id} has been removed!")
            else:
                context.user_data[chat_id] = {'state': 'delete_habit'}
                await update.message.reply_text("Invalid habit ID. Please choose a valid ID from the list👆🏿")

        except ValueError:
            context.user_data[chat_id] = {'state': 'delete_habit'}
            await update.message.reply_text("Invalid input. Please enter a valid habit ID number.")
