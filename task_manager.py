from telegram import Update
from telegram.ext import CallbackContext


class TaskManager:
    def __init__(self, db):
        self.db = db

    async def add_task(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        context.user_data[chat_id] = {'state': 'add_task'}
        await update.message.reply_text('Please write the task you want to add.')

    async def handle_add_task(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        task_description = update.message.text.strip()

        task_id = self.db.save_task(chat_id, task_description)
        await update.message.reply_text(f"Task №:{task_id} was added!")

    async def show_tasks(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        tasks = self.db.get_tasks(chat_id)

        if not tasks:
            await update.message.reply_text("You do not have any tasks yet!")
            return

        action_tasks = [task for task in tasks if not task.get('completed', False)]
        completed_tasks = [task for task in tasks if task.get('completed', False)]

        if action_tasks:
            action_tasks_text = "\n".join([f"{task['id']}. {task['description']}" for task in action_tasks])
            action_tasks_message = "Action tasks🔥:\n__________________________\n" + action_tasks_text
            await update.message.reply_text(action_tasks_message)

        if completed_tasks:
            completed_tasks_text = "\n".join([f"{task['id']}. {task['description']}" for task in completed_tasks])
            completed_tasks_message = "Completed tasks✅:\n__________________________\n" + completed_tasks_text
            await update.message.reply_text(completed_tasks_message)

    async def complete_task(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        tasks = self.db.get_tasks(chat_id)

        if not tasks:
            await update.message.reply_text("You do not have any tasks yet!")
            return

        action_tasks = [task for task in tasks if not task.get('completed', False)]
        action_tasks_text = "\n".join([f"{task['id']}. {task['description']}" for task in action_tasks])

        if action_tasks:
            context.user_data[chat_id] = {'state': 'complete_task'}
            await update.message.reply_text(f"Your tasks:\n{action_tasks_text}\n\n__________________________\n"
                                            "Enter the ID of the task you want to mark as completed.")
        else:
            await update.message.reply_text("You do not have any tasks to complete try adding tasks")

    async def handle_complete_task(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        task_id = update.message.text.strip()

        try:
            task_id = int(task_id)

            if self.db.task_exists(chat_id, task_id):

                self.db.complete_task(chat_id, task_id)
                context.user_data[chat_id]['state'] = ''
                await update.message.reply_text(f"The task №:{task_id} "
                                                f"has been marked as completed✅")
            else:
                context.user_data[chat_id] = {'state': 'complete_task'}
                await update.message.reply_text("Invalid task ID. Please choose a valid ID from the list👆🏿")
        except ValueError:
            context.user_data[chat_id] = {'state': 'complete_task'}
            await update.message.reply_text("Invalid input. Please enter a valid task ID number.")

    async def delete_task(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id

        tasks = self.db.get_tasks(chat_id)
        if tasks:
            tasks_text = "\n".join([f"{task['id']}. {task['description']}" for task in tasks])
            context.user_data[chat_id] = {'state': 'delete_task'}
            await update.message.reply_text(f"Your tasks:\n{tasks_text}\n\n"
                                            "Enter the ID of the task you want to delete.")
        else:
            await update.message.reply_text("You do not have any tasks yet")

    async def handle_delete_task(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        task_id = update.message.text.strip()

        try:
            task_id = int(task_id)
            if self.db.task_exists(chat_id, task_id):
                self.db.delete_task(chat_id, task_id)
                await update.message.reply_text(f"The task №:{task_id} has been removed.")
            else:
                context.user_data[chat_id] = {'state': 'delete_task'}
                await update.message.reply_text("Please choose a valid ID from the list👆🏿")
        except ValueError:
            context.user_data[chat_id] = {'state': 'delete_task'}
            await update.message.reply_text("Invalid input. Please enter a valid task ID number.")
